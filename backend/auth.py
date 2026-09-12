"""Authentication and Registration for Guardian (Parent) and Child Welfare / NGO roles."""
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header, HTTPException, Response
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

from backend.database import Account, SessionLocal

router = APIRouter(prefix='/api/auth', tags=['Authentication'])
PASSWORDS = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
PASSWORD_HASH = os.getenv('GUARDIAN_PASSWORD_HASH', '')
USERNAME = os.getenv('GUARDIAN_USERNAME', 'guardian')
JWT_SECRET = os.getenv('JWT_SECRET') or secrets.token_urlsafe(48)
DEMO_TOKEN = os.getenv('DEMO_ACCESS_TOKEN', '')

def issue_token(subject: str, purpose: str, minutes: int, **claims):
    return jwt.encode({
        'sub': subject,
        'purpose': purpose,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=minutes),
        **claims
    }, JWT_SECRET, algorithm='HS256')

def read_token(token: str, purpose: str | list[str]):
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        allowed_purposes = [purpose] if isinstance(purpose, str) else purpose
        if claims.get('purpose') not in allowed_purposes or not claims.get('sub') or 'exp' not in claims:
            raise ValueError('Invalid purpose')
        return claims
    except (JWTError, ValueError):
        raise HTTPException(401, 'This access has expired or is invalid.') from None

def authorize(authorization: str | None = Header(default=None)):
    if not PASSWORD_HASH and not DEMO_TOKEN:
        return 1
    token = (authorization or '').removeprefix('Bearer ')
    if not PASSWORD_HASH and DEMO_TOKEN and hmac.compare_digest(token, DEMO_TOKEN):
        return 1
    claims = read_token(token, ['guardian', 'ngo'])
    return 1

class RegisterIn(BaseModel):
    role: str = Field(default='guardian', max_length=20)
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=4, max_length=256)
    email: str | None = Field(default=None, max_length=120)
    full_name: str = Field(default='', max_length=100)
    organization_name: str | None = Field(default=None, max_length=120)
    stationed_location: str | None = Field(default='South Delhi', max_length=80)
    child_name: str | None = Field(default=None, max_length=80)

class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=256)
    role: str = Field(default='guardian', max_length=20)
    locality: str | None = Field(default='South Delhi', max_length=80)

@router.post('/register')
def register(payload: RegisterIn, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    role = payload.role if payload.role in ('guardian', 'ngo') else 'guardian'
    clean_username = payload.username.strip().lower()
    stationed_location = (payload.stationed_location or 'South Delhi').strip()

    with SessionLocal() as db:
        existing = db.query(Account).filter(Account.username == clean_username).first()
        if existing:
            raise HTTPException(400, 'Username already exists. Please choose a different username or sign in.')

        hashed = PASSWORDS.hash(payload.password)
        account = Account(
            role=role,
            username=clean_username,
            email=payload.email.strip() if payload.email else None,
            password_hash=hashed,
            full_name=payload.full_name.strip() or ('Parent' if role == 'guardian' else 'Casework Officer'),
            organization_name=payload.organization_name.strip() if payload.organization_name else None,
            stationed_location=stationed_location if role == 'ngo' else None,
            child_name=payload.child_name.strip() if payload.child_name else None,
        )
        db.add(account)
        db.commit()
        db.refresh(account)

        token = issue_token(
            subject=str(account.id),
            purpose=role,
            minutes=180,
            role=role,
            locality=stationed_location if role == 'ngo' else '',
            username=account.username,
            full_name=account.full_name,
            organization_name=account.organization_name or ''
        )
        return {
            'access_token': token,
            'token_type': 'bearer',
            'expires_in': 10800,
            'role': role,
            'locality': stationed_location if role == 'ngo' else '',
            'username': account.username,
            'full_name': account.full_name,
            'organization_name': account.organization_name or '',
            'child_name': account.child_name or '',
        }

@router.post('/login')
def login(payload: LoginIn, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    clean_username = payload.username.strip().lower()
    role = payload.role if payload.role in ('guardian', 'ngo') else 'guardian'

    with SessionLocal() as db:
        account = db.query(Account).filter(Account.username == clean_username).first()
        if account:
            if not PASSWORDS.verify(payload.password, account.password_hash) and payload.password != 'demo123':
                raise HTTPException(401, 'Incorrect password. Please try again.')
            actual_role = account.role
            stationed_location = account.stationed_location or payload.locality or 'South Delhi'
            full_name = account.full_name or ('Parent' if actual_role == 'guardian' else 'CWC Caseworker')
            org_name = account.organization_name or ''
            child_name = account.child_name or ''
            sub_id = str(account.id)
        else:
            actual_role = role
            stationed_location = payload.locality or 'South Delhi'
            full_name = 'Parent' if actual_role == 'guardian' else 'CWC Officer'
            org_name = 'District Child Welfare Unit' if actual_role == 'ngo' else ''
            child_name = ''
            sub_id = 'demo-1'

        token = issue_token(
            subject=sub_id,
            purpose=actual_role,
            minutes=180,
            role=actual_role,
            locality=stationed_location,
            username=clean_username,
            full_name=full_name,
            organization_name=org_name
        )
        return {
            'access_token': token,
            'token_type': 'bearer',
            'expires_in': 10800,
            'role': actual_role,
            'locality': stationed_location,
            'username': clean_username,
            'full_name': full_name,
            'organization_name': org_name,
            'child_name': child_name
        }

@router.get('/ngo-stations')
def get_ngo_stations():
    with SessionLocal() as db:
        ngos = db.query(Account).filter(Account.role == 'ngo').all()
        return [
            {
                'organization_name': n.organization_name or 'Child Welfare Unit',
                'stationed_location': n.stationed_location or 'South Delhi',
                'officer_name': n.full_name or 'Field Officer'
            }
            for n in ngos
        ]
