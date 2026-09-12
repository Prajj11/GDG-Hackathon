"""Digital Guardrails — app.main compatibility entry point.
Allows running with `uvicorn app.main:app` or importing from `app.main`.
Attaches alias routes for full backward and cross-specification compatibility.
"""
from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy import select
from backend.main import app, serialize
from backend.database import SessionLocal, Alert, Report, AidRoute, Conversation
from app.schemas import (
    MessageIngestRequest, MessageIngestResponse,
    AlertSummary, AlertDetail, DashboardSummary,
    ReportSubmitRequest, ReportSubmitResponse, ReportStatusResponse
)
from app.ml_engine import analyze_message, load_model, RiskLevel, PatternType

# 1. Alias: GET /health
@app.get("/health", tags=["System"])
def root_health():
    return {"status": "ok"}

# 2. Alias: POST /api/alerts/{alert_id}/review
@app.post("/api/alerts/{alert_id}/review", tags=["Guardian Alerts"])
def mark_alert_reviewed_alias(alert_id: str):
    with SessionLocal() as db:
        alert = db.get(Alert, alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        alert.reviewed = True
        db.commit()
        return {"id": alert_id, "status": "reviewed"}

# 3. Alias: POST /api/reports (Youth Support anonymous submission)
@app.post("/api/reports", response_model=ReportSubmitResponse, tags=["Youth Support"])
def submit_report_alias(payload: ReportSubmitRequest):
    with SessionLocal() as db:
        import uuid
        report_id = str(uuid.uuid4())
        anon_token = str(uuid.uuid4())
        report = Report(
            id=report_id,
            anonymous_token=anon_token,
            selected_context=payload.starting_prompt or "general",
            report_text=payload.report_text or "",
            urgency_level=payload.urgency_level or "standard",
            status="submitted"
        )
        db.add(report)
        db.flush()
        
        aid_channel = None
        if payload.urgency_level in ["immediate_danger", "High"] or payload.report_text:
            route_id = str(uuid.uuid4())
            route = AidRoute(
                id=route_id,
                report_id=report_id,
                aid_channel_name="Simulated CHILDLINE Endpoint",
                status="routed"
            )
            db.add(route)
            report.status = "routed"
            aid_channel = route.aid_channel_name

        db.commit()

        message = (
            "You're not alone. Your message has been shared with a support "
            "contact — you don't need to share anything else if you're not ready."
            if aid_channel else
            "Thank you for reaching out. You can check back anytime with your "
            "reference code below."
        )

        return ReportSubmitResponse(
            anonymous_token=anon_token,
            status=report.status,
            aid_channel_name=aid_channel,
            message=message
        )

# 4. Alias: GET /api/reports/{anonymous_token}/status
@app.get("/api/reports/{anonymous_token}/status", response_model=ReportStatusResponse, tags=["Youth Support"])
def report_status_alias(anonymous_token: str):
    with SessionLocal() as db:
        report = db.scalar(select(Report).where(Report.anonymous_token == anonymous_token))
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        aid_channel = None
        if report.status == "routed":
            route = db.scalar(select(AidRoute).where(AidRoute.report_id == report.id))
            if route:
                aid_channel = route.aid_channel_name

        return ReportStatusResponse(status=report.status, aid_channel_name=aid_channel)

__all__ = ['app', 'load_model', 'analyze_message']
