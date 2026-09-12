"""Optional single-guardian JWT login; youth routes never use guardian auth."""
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header, HTTPException, Response
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

router = APIRouter(prefix='/api/auth', tags=['Guardian authentication'])
PASSWORDS = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
PASSWORD_HASH = os.getenv('GUARDIAN_PASSWORD_HASH', '')
USERNAME = os.getenv('GUARDIAN_USERNAME', 'guardian')
# Local capability links expire on restart unless a key is explicitly configured.
JWT_SECRET = os.getenv('JWT_SECRET') or secrets.token_urlsafe(48)
DEMO_TOKEN = os.getenv('DEMO_ACCESS_TOKEN', '')

def issue_token(subject: str, purpose: str, minutes: int, **claims):
    return jwt.encode({'sub': subject, 'purpose': purpose,
                       'exp': datetime.now(timezone.utc) + timedelta(minutes=minutes),
                       **claims}, JWT_SECRET, algorithm='HS256')

def read_token(token: str, purpose: str):
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        if claims.get('purpose') != purpose or not claims.get('sub') or 'exp' not in claims:
            raise ValueError('Invalid purpose')
        return claims
    except (JWTError, ValueError):
        raise HTTPException(401, 'This access has expired or is invalid.') from None

def authorize(authorization: str | None = Header(default=None)):
    if not PASSWORD_HASH and not DEMO_TOKEN:
        return 1  # Explicit loopback demo mode.
    token = (authorization or '').removeprefix('Bearer ')
    if not PASSWORD_HASH and DEMO_TOKEN and hmac.compare_digest(token, DEMO_TOKEN):
        return 1
    claims = read_token(token, 'guardian')
    if claims['sub'] != '1':
        raise HTTPException(401, 'Please sign in as the guardian.')
    return 1

class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=256)

@router.post('/login')
def login(payload: LoginIn, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    if not PASSWORD_HASH:
        raise HTTPException(409, 'Guardian login is not configured. This is a local demo workspace.')
    valid_password = PASSWORDS.verify(payload.password, PASSWORD_HASH)
    if not hmac.compare_digest(payload.username.encode(), USERNAME.encode()) or not valid_password:
        raise HTTPException(401, 'Username or password was not recognized.')
    return {'access_token': issue_token('1', 'guardian', 60), 'token_type': 'bearer', 'expires_in': 3600}
