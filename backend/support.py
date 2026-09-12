"""Login-free reporting with separate receipt capabilities and explicit context consent."""
import hashlib
import hmac
import threading
from datetime import timedelta
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import delete, select

from backend import aid
from backend.auth import read_token
from backend import database
from backend.database import now

router = APIRouter(prefix='/api/support', tags=['Anonymous support'])
REPORT_LOCK = threading.RLock()
CONTEXTS = Literal['secrets', 'uncomfortable', 'bullying', 'talk', 'unfamiliar-person']

def cleanup_reports(db):
    expired = select(database.Report.id).where(database.Report.created_at < now() - timedelta(days=7))
    db.execute(delete(database.AidRoute).where(database.AidRoute.report_id.in_(expired)))
    db.execute(delete(database.Report).where(database.Report.id.in_(expired)))
    db.commit()

def private_response(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'

class ContextIn(BaseModel):
    context_token: str = Field(min_length=1, max_length=2048)

class ContextOut(BaseModel):
    linked_alert_id: str
    pattern_type: str
    risk_level: Literal['Low', 'Medium', 'High']
    suggested_context: CONTEXTS

class RouteOut(BaseModel):
    aid_channel_name: str
    status: Literal['simulated_received']
    routed_at: str

class ReceiptOut(BaseModel):
    id: str
    status: str
    urgency_level: Literal['Low', 'Medium', 'High']
    locality: str = 'South Delhi'
    created_at: str
    expires_at: str
    context_shared: bool
    simulated: Literal[True] = True
    human_contacted: Literal[False] = False
    aid_route: RouteOut | None

def detection_context(db, token):
    claims = read_token(token, 'youth-context')
    alert = db.get(database.Alert, claims['sub'])
    if not alert:
        raise HTTPException(410, 'This suggestion has expired. You can continue without it.')
    context = 'bullying' if alert.pattern_type == 'bullying-harassment' else 'unfamiliar-person'
    if alert.pattern_type == 'grooming-isolation-request':
        context = 'secrets'
    return {'linked_alert_id': alert.id, 'pattern_type': alert.pattern_type,
            'risk_level': alert.risk_level, 'suggested_context': context}

@router.post('/context', response_model=ContextOut)
def get_context(payload: ContextIn, response: Response):
    private_response(response)
    with database.SessionLocal() as db:
        return detection_context(db, payload.context_token)

class ReportIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    anonymous_token: str = Field(pattern=r'^[a-f0-9]{64}$')
    selected_context: CONTEXTS = 'talk'
    report_text: str = Field(default='', max_length=1500)
    urgency_level: Literal['Low', 'Medium', 'High'] = 'Medium'
    locality: str = Field(default='South Delhi', max_length=60)
    linked_alert_id: str | None = Field(default=None, max_length=36)
    context_token: str | None = Field(default=None, max_length=2048)
    share_detection_context: bool = False

    @field_validator('report_text')
    @classmethod
    def trim(cls, value):
        return value.strip()

def route_report(db, report):
    if db.scalar(select(database.AidRoute).where(database.AidRoute.report_id == report.id)):
        return
    payload = aid.AidPayload(report_id=report.id, selected_context=report.selected_context,
                             report_text=report.report_text, urgency_level=report.urgency_level,
                             detection_context=report.detection_context)
    try:
        receipt = aid.aid_provider.route(payload, idempotency_key=report.id)
    except Exception:
        # Preserve submission and allow a receipt-authorized retry; never claim delivery.
        return
    db.add(database.AidRoute(id=str(uuid4()), report_id=report.id, aid_channel_name=receipt.channel_name,
                    status=receipt.status))
    report.status = 'routed'
    db.commit()

def receipt_out(db, report):
    route = db.scalar(select(database.AidRoute).where(database.AidRoute.report_id == report.id))
    return {'id': report.id, 'status': report.status, 'urgency_level': report.urgency_level,
            'locality': getattr(report, 'locality', 'South Delhi') or 'South Delhi',
            'created_at': report.created_at.isoformat() + 'Z',
            'expires_at': (report.created_at + timedelta(days=7)).isoformat() + 'Z',
            'context_shared': report.detection_context is not None,
            'simulated': True, 'human_contacted': False,
            'aid_route': None if not route else {'aid_channel_name': route.aid_channel_name,
            'status': route.status, 'routed_at': route.routed_at.isoformat() + 'Z'}}

@router.post('/reports', status_code=201, response_model=ReceiptOut)
def submit_report(payload: ReportIn, response: Response):
    private_response(response)
    digest = hashlib.sha256(payload.anonymous_token.encode()).hexdigest()
    with REPORT_LOCK, database.SessionLocal() as db:
        cleanup_reports(db)
        existing = db.scalar(select(database.Report).where(database.Report.anonymous_token == digest))
        if existing:
            return receipt_out(db, existing)  # Same receipt secret = idempotent retry.
        context = None
        if payload.share_detection_context:
            if not payload.context_token or not payload.linked_alert_id:
                raise HTTPException(422, 'Choose a valid suggestion or continue without sharing it.')
            context = detection_context(db, payload.context_token)
            if context['linked_alert_id'] != payload.linked_alert_id:
                raise HTTPException(422, 'The selected suggestion does not match this alert.')
        elif payload.linked_alert_id or payload.context_token:
            raise HTTPException(422, 'Detection context requires your explicit choice to share it.')
        report = database.Report(id=str(uuid4()), anonymous_token=digest,
                        linked_alert_id=context['linked_alert_id'] if context else None,
                        selected_context=payload.selected_context, report_text=payload.report_text,
                        urgency_level=payload.urgency_level, locality=payload.locality,
                        detection_context=(
                            {'pattern_type': context['pattern_type'], 'risk_level': context['risk_level']}
                            if context else None))
        db.add(report)
        db.commit()
        route_report(db, report)
        return receipt_out(db, report)

def owned_report(db, report_id, authorization):
    token = (authorization or '').removeprefix('Bearer ')
    report = db.get(database.Report, report_id)
    digest = hashlib.sha256(token.encode()).hexdigest()
    if not report or not hmac.compare_digest(report.anonymous_token, digest):
        raise HTTPException(404, 'This receipt was not found, has expired, or its private code is incorrect.')
    return report

@router.get('/reports/{report_id}', response_model=ReceiptOut)
def report_status(report_id: str, response: Response, authorization: str | None = Header(default=None)):
    private_response(response)
    with REPORT_LOCK, database.SessionLocal() as db:
        cleanup_reports(db)
        return receipt_out(db, owned_report(db, report_id, authorization))

@router.post('/reports/{report_id}/retry', response_model=ReceiptOut)
def retry_route(report_id: str, response: Response, authorization: str | None = Header(default=None)):
    private_response(response)
    with REPORT_LOCK, database.SessionLocal() as db:
        cleanup_reports(db)
        report = owned_report(db, report_id, authorization)
        route_report(db, report)
        return receipt_out(db, report)
