import hmac
import os
import threading
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Literal
from uuid import uuid4
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, delete
from backend.database import Base, engine, SessionLocal, User, Conversation, Alert, now
from backend.ml.detector import analyze_message, get_detector, minimal_snippet, risk_level
from backend.auth import router as auth_router, authorize as jwt_authorize, issue_token, PASSWORD_HASH
from backend.support import router as support_router, cleanup_reports

LOCK = threading.RLock()
TOKEN = os.getenv('DEMO_ACCESS_TOKEN', '')

def authorize(authorization: str | None = Header(default=None)):
    if PASSWORD_HASH:
        return jwt_authorize(authorization)
    if TOKEN and not hmac.compare_digest(authorization or '', f'Bearer {TOKEN}'):
        raise HTTPException(401, 'Enter the demo access token in Settings.')

def cleanup(db):
    user = db.get(User, 1)
    cutoff = now() - timedelta(days=user.retention_days)
    db.execute(delete(Alert).where(Alert.created_at < cutoff))
    db.execute(delete(Conversation).where(Conversation.updated_at < cutoff, ~Conversation.id.in_(select(Alert.conversation_id))))
    db.commit()

@asynccontextmanager
async def lifespan(app):
    if os.getenv('DG_HOSTED') == 'true' and not PASSWORD_HASH and len(TOKEN) < 24:
        raise RuntimeError('Hosted demos require a DEMO_ACCESS_TOKEN of at least 24 characters.')
    if os.getenv('DG_HOSTED') == 'true' and PASSWORD_HASH and len(os.getenv('JWT_SECRET', '')) < 32:
        raise RuntimeError('Hosted guardian login requires a JWT_SECRET of at least 32 characters.')
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.get(User, 1):
            db.add(User(id=1))
            db.commit()
        cleanup(db)
        cleanup_reports(db)
    get_detector()
    yield

app = FastAPI(title='Digital Guardrails + Support Ecosystems', version='2.0.0', lifespan=lifespan)
app.include_router(auth_router)
app.include_router(support_router)
app.add_middleware(CORSMiddleware, allow_origins=os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(','), allow_methods=['GET', 'POST', 'PATCH'], allow_headers=['Content-Type', 'Authorization'])

class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    conversation_id: str = Field(min_length=1, max_length=64, pattern=r'^[a-zA-Z0-9_-]+$')
    child_label: Literal['Child 1', 'Child 2'] = 'Child 1'
    source_platform: Literal['Gaming chat', 'Social chat', 'Study group', 'Demo'] = 'Demo'
    language: Literal['English', 'Hindi', 'Malayalam', 'Hinglish', 'Manglish'] = 'Hinglish'
    @field_validator('text')
    @classmethod
    def strip_text(cls, value):
        if not value.strip():
            raise ValueError('Enter a message to analyze.')
        if len(value.splitlines()) > 8:
            raise ValueError('Use at most 8 lines per message window.')
        return value.strip()

class ReviewIn(BaseModel):
    reviewed: bool
class SettingsIn(BaseModel):
    retention_days: Literal[1, 7, 30]
    snippets_enabled: bool

class AnalysisOut(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: Literal['Low', 'Medium', 'High']
    pattern_type: str
    confidence: float
    explanation: str
    model: str
    model_kind: str
    alert_id: str | None
    conversation_id: str
    message_count: int
    escalated: bool
    support_context_token: str | None = None

def serialize(alert, conversation):
    return {key: getattr(alert, key) for key in ['id', 'conversation_id', 'risk_score', 'risk_level', 'pattern_type', 'flagged_snippet', 'explanation', 'model', 'confidence', 'reviewed']} | {'created_at': alert.created_at.isoformat()+'Z', 'child_label': conversation.child_label, 'source_platform': conversation.source_platform, 'language': conversation.language}

@app.get('/api/health')
def health():
    detector = get_detector()
    return {'status': 'ok', 'model': detector.name, 'model_kind': detector.kind, 'fallback_reason': detector.reason, 'synthetic_demo': True, 'access_protected': bool(TOKEN or PASSWORD_HASH), 'guardian_login_enabled': bool(PASSWORD_HASH), 'aid_mode': 'simulated'}

@app.post('/api/messages/ingest', response_model=AnalysisOut, dependencies=[Depends(authorize)])
def ingest(payload: MessageIn):
    with LOCK, SessionLocal() as db:
        cleanup(db)
        conversation = db.get(Conversation, payload.conversation_id)
        if conversation and (conversation.child_label != payload.child_label or conversation.source_platform != payload.source_platform):
            raise HTTPException(409, 'This conversation belongs to another child or source. Start a new conversation.')
        if not conversation:
            conversation = Conversation(id=payload.conversation_id, user_id=1, child_label=payload.child_label, source_platform=payload.source_platform, language=payload.language, signals=[], message_count=0)
            db.add(conversation)
        # Transient text only. Pick the line with the strongest model signal for the excerpt.
        lines = [line.strip() for line in payload.text.splitlines() if line.strip()]
        analyzed = [(line, analyze_message(line)) for line in lines]
        snippet_text, result = max(analyzed, key=lambda item: item[1]['risk_score'])
        cutoff = (now() - timedelta(hours=24)).isoformat()
        history = [item for item in conversation.signals if item['at'] > cutoff][-11:]
        previous = [item['pattern'] for item in history]
        pattern = result['pattern_type']
        escalated = False
        if pattern == 'grooming-isolation-request' and 'grooming-trust-building' in previous:
            result['risk_score'] = max(80, result['risk_score'])
            result['explanation'] += ' Earlier messages showed trust-building, followed now by secrecy. This change increases concern.'
            escalated = True
        if pattern == 'bullying-harassment' and previous.count(pattern) >= 1:
            result['risk_score'] = min(95, result['risk_score'] + 18)
            result['explanation'] += ' A similar harassment signal was detected earlier in this conversation within 24 hours.'
            escalated = True
        result['risk_level'] = risk_level(result['risk_score'])
        conversation.signals = (history + [{'pattern': pattern, 'at': now().isoformat()}])[-12:]
        conversation.message_count += 1
        conversation.language = payload.language
        conversation.updated_at = now()
        alert_id = None
        if pattern != 'neutral':
            alert_id = str(uuid4())
            user = db.get(User, 1)
            db.add(Alert(id=alert_id, conversation_id=conversation.id, risk_score=result['risk_score'], risk_level=result['risk_level'], pattern_type=pattern, flagged_snippet=minimal_snippet(snippet_text) if user.snippets_enabled else '', explanation=result['explanation'], model=result['model'], confidence=result['confidence']))
        db.commit()
        return result | {'alert_id': alert_id, 'conversation_id': conversation.id, 'message_count': conversation.message_count, 'escalated': escalated,
                         'support_context_token': issue_token(alert_id, 'youth-context', 30) if alert_id else None}

@app.get('/api/alerts', dependencies=[Depends(authorize)])
def alerts():
    with LOCK, SessionLocal() as db:
        cleanup(db)
        return [serialize(a, c) for a, c in db.execute(select(Alert, Conversation).join(Conversation).order_by(Alert.risk_score.desc(), Alert.created_at.desc()))]

@app.get('/api/alerts/{alert_id}', dependencies=[Depends(authorize)])
def alert_detail(alert_id: str):
    with LOCK, SessionLocal() as db:
        cleanup(db)
        alert = db.get(Alert, alert_id)
        if not alert:
            raise HTTPException(404, 'This alert was not found or its retention period ended.')
        return serialize(alert, db.get(Conversation, alert.conversation_id))

@app.patch('/api/alerts/{alert_id}', dependencies=[Depends(authorize)])
def review(alert_id: str, payload: ReviewIn):
    with LOCK, SessionLocal() as db:
        cleanup(db)
        alert = db.get(Alert, alert_id)
        if not alert:
            raise HTTPException(404, 'Alert not found.')
        alert.reviewed = payload.reviewed
        db.commit()
        return serialize(alert, db.get(Conversation, alert.conversation_id))

@app.get('/api/dashboard/summary', dependencies=[Depends(authorize)])
def summary():
    with LOCK, SessionLocal() as db:
        cleanup(db)
        rows = list(db.scalars(select(Alert)))
        conversations = list(db.scalars(select(Conversation)))
        days = [(now() - timedelta(days=i)).date() for i in reversed(range(7))]
        trends = [{'date': day.isoformat(), **{level: sum(a.created_at.date() == day and a.risk_level == level for a in rows) for level in ['High', 'Medium', 'Low']}} for day in days]
        return {'total_alerts': len(rows), 'unreviewed': sum(not a.reviewed for a in rows), 'high_risk': sum(a.risk_level == 'High' and not a.reviewed for a in rows), 'reviewed': sum(a.reviewed for a in rows), 'messages_analyzed': sum(c.message_count for c in conversations), 'conversations': len(conversations), 'trends': trends}

@app.get('/api/settings', dependencies=[Depends(authorize)])
def settings():
    with SessionLocal() as db:
        user = db.get(User, 1)
        return {'retention_days': user.retention_days, 'snippets_enabled': user.snippets_enabled}

@app.patch('/api/settings', dependencies=[Depends(authorize)])
def save_settings(payload: SettingsIn):
    with LOCK, SessionLocal() as db:
        user = db.get(User, 1)
        user.retention_days = payload.retention_days
        user.snippets_enabled = payload.snippets_enabled
        if not payload.snippets_enabled:
            for alert in db.scalars(select(Alert)):
                alert.flagged_snippet = ''
        db.commit()
        cleanup(db)
        return payload
