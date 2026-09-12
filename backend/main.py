import hmac
import os
import threading
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Literal
from uuid import uuid4
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, delete, func
from backend.database import Base, engine, SessionLocal, User, Conversation, Alert, Report, DatasetRecord, Account, ensure_schema, now
from backend.ml.detector import analyze_message, get_detector, minimal_snippet, risk_level
from backend.auth import router as auth_router, authorize as jwt_authorize, authorize_ngo, issue_token, PASSWORD_HASH
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
    ensure_schema(engine)
    with SessionLocal() as db:
        user = db.get(User, 1)
        if not user:
            db.add(User(id=1, snippets_enabled=True))
            db.commit()
        if os.getenv('SEED_DEMO_REPORTS') == 'true' and os.getenv('DG_HOSTED') != 'true' and db.scalar(select(func.count()).select_from(Report)) == 0:
            import hashlib, secrets
            seed_reports = [
                Report(
                    id='rep-dl-101',
                    anonymous_token=hashlib.sha256(secrets.token_hex(32).encode()).hexdigest(),
                    selected_context='bullying',
                    report_text='Classmates in my tuition center created a fake account and are posting abusive messages and threatening to leak edited pictures.',
                    urgency_level='High',
                    locality='South Delhi',
                    status='under_review',
                    assigned_worker='Ms. S. Sharma (Child Protection Officer)',
                    caseworker_notes='Initial risk assessment completed. School nodal authority contacted.',
                    detection_context={'pattern_type': 'bullying-harassment', 'risk_level': 'High'}
                ),
                Report(
                    id='rep-dl-102',
                    anonymous_token=hashlib.sha256(secrets.token_hex(32).encode()).hexdigest(),
                    selected_context='unfamiliar-person',
                    report_text='A stranger in a gaming channel keeps asking for my home address and school timing, promising gaming credits.',
                    urgency_level='Medium',
                    locality='South Delhi',
                    status='submitted',
                    assigned_worker=None,
                    detection_context={'pattern_type': 'grooming-isolation-request', 'risk_level': 'Medium'}
                ),
                Report(
                    id='rep-mb-201',
                    anonymous_token=hashlib.sha256(secrets.token_hex(32).encode()).hexdigest(),
                    selected_context='secrets',
                    report_text='Someone said they would share my private voice notes if I tell my parents.',
                    urgency_level='High',
                    locality='Mumbai Suburban',
                    status='dispatched',
                    assigned_worker='Inspector R. Kulkarni (SJPU)',
                    caseworker_notes='Field visit scheduled with CWC counsellor.',
                    detection_context={'pattern_type': 'grooming-isolation-request', 'risk_level': 'High'}
                )
            ]
            db.add_all(seed_reports)
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
            snippet = minimal_snippet(snippet_text) if (user and user.snippets_enabled) else ''
            db.add(Alert(id=alert_id, conversation_id=conversation.id, risk_score=result['risk_score'], risk_level=result['risk_level'], pattern_type=pattern, flagged_snippet=snippet, explanation=result['explanation'], model=result['model'], confidence=result['confidence']))
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

@app.get('/api/dataset/stats')
def dataset_stats():
    with SessionLocal() as db:
        total = db.scalar(select(func.count(DatasetRecord.id))) or 0
        origins = dict(db.execute(select(DatasetRecord.origin, func.count(DatasetRecord.id)).group_by(DatasetRecord.origin)).all())
        languages = dict(db.execute(select(DatasetRecord.language, func.count(DatasetRecord.id)).group_by(DatasetRecord.language)).all())
        patterns = dict(db.execute(select(DatasetRecord.pattern_label, func.count(DatasetRecord.id)).group_by(DatasetRecord.pattern_label)).all())
        return {
            'total_records': total,
            'origins': origins,
            'languages': languages,
            'patterns': patterns,
            'excel_path': 'backend/ml/dataset.xlsx'
        }

@app.get('/api/dataset/records')
def dataset_records(language: str | None = None, pattern: str | None = None, origin: str | None = None, limit: int = 50, offset: int = 0):
    with SessionLocal() as db:
        stmt = select(DatasetRecord)
        if language:
            stmt = stmt.where(DatasetRecord.language == language)
        if pattern:
            stmt = stmt.where(DatasetRecord.pattern_label == pattern)
        if origin:
            stmt = stmt.where(DatasetRecord.origin == origin)
        total = db.scalar(select(func.count()).select_from(stmt.subquery()))
        stmt = stmt.offset(offset).limit(min(limit, 100))
        records = db.scalars(stmt).all()
        return {
            'total': total,
            'limit': limit,
            'offset': offset,
            'records': [{
                'id': r.id,
                'origin': r.origin,
                'source_dataset': r.source_dataset,
                'language': r.language,
                'script': r.script,
                'pattern_label': r.pattern_label,
                'risk_level': r.risk_level,
                'target_text': r.target_text,
                'window_text': r.window_text,
                'rationale': r.rationale,
                'turns_count': len(r.turns or [])
            } for r in records]
        }

class NgoReportUpdate(BaseModel):
    status: Literal['submitted', 'under_review', 'dispatched', 'resolved'] | None = None
    assigned_worker: str | None = None
    caseworker_notes: str | None = None

@app.get('/api/ngo/reports', tags=['Child Welfare NGO Casework'])
def get_ngo_reports(locality: str | None = None, status: str | None = None, assigned_area: str = Depends(authorize_ngo)):
    with SessionLocal() as db:
        query = select(Report).where(Report.locality == assigned_area).order_by(Report.created_at.desc())
        if locality and locality != 'All Localities':
            query = query.where(Report.locality == locality)
        if status and status != 'all':
            query = query.where(Report.status == status)
        reports = db.scalars(query).all()
        return [{
            'id': r.id,
            'locality': r.locality or 'South Delhi',
            'selected_context': r.selected_context,
            'report_text': r.report_text,
            'urgency_level': r.urgency_level,
            'status': r.status,
            'assigned_worker': r.assigned_worker,
            'caseworker_notes': r.caseworker_notes,
            'detection_context': r.detection_context,
            'created_at': r.created_at.isoformat() + 'Z' if r.created_at else None
        } for r in reports]

@app.patch('/api/ngo/reports/{report_id}', tags=['Child Welfare NGO Casework'])
def update_ngo_report(report_id: str, payload: NgoReportUpdate, assigned_area: str = Depends(authorize_ngo)):
    with LOCK, SessionLocal() as db:
        report = db.get(Report, report_id)
        if not report or report.locality != assigned_area:
            raise HTTPException(404, 'Report not found')
        if payload.status:
            report.status = payload.status
        if payload.assigned_worker is not None:
            report.assigned_worker = payload.assigned_worker
        if payload.caseworker_notes is not None:
            report.caseworker_notes = payload.caseworker_notes
        db.commit()
        return {
            'id': report.id,
            'status': report.status,
            'assigned_worker': report.assigned_worker,
            'caseworker_notes': report.caseworker_notes
        }

@app.get('/api/ngo/localities', tags=['Child Welfare NGO Casework'])
def get_ngo_localities():
    base = ['South Delhi', 'North Delhi', 'Mumbai Suburban', 'Bengaluru Urban', 'Kolkata Central']
    with SessionLocal() as db:
        registered = [
            loc for (loc,) in db.query(Account.stationed_location).filter(
                Account.stationed_location != None,
                Account.stationed_location != ''
            ).distinct().all()
        ]
        combined = list(dict.fromkeys(base + registered))
        return ['All Localities'] + combined + ['Other']

# Antideploy runs the project as one container. Serve the built SPA from the
# same origin while keeping all /api routes registered above it.
if os.path.isdir('/app/dist'):
    from starlette.exceptions import HTTPException as StarletteHTTPException

    class FrontendFiles(StaticFiles):
        async def get_response(self, path, scope):
            try:
                return await super().get_response(path, scope)
            except StarletteHTTPException as exc:
                if exc.status_code == 404 and not path.startswith(('api/', 'assets/')) and '.' not in path.rsplit('/', 1)[-1]:
                    return await super().get_response('index.html', scope)
                raise

    app.mount('/', FrontendFiles(directory='/app/dist', html=True), name='frontend')

