"""Digital Guardrails — app.schemas compatibility facade.
Pydantic data schemas for API requests and responses.
"""
from typing import Optional, List, Any
from pydantic import BaseModel, Field

class MessageIngestRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    child_label: str = "Child 1"
    source_platform: str = "demo"
    language_hint: Optional[str] = None
    conversation_id: Optional[str] = None

class MessageIngestResponse(BaseModel):
    conversation_id: Any
    risk_score: float
    risk_level: str
    pattern_type: str
    alert_created: bool = False
    alert_id: Optional[Any] = None
    explanation: Optional[str] = None
    model: Optional[str] = None
    confidence: Optional[float] = None

class AlertSummary(BaseModel):
    id: Any
    conversation_id: Any
    risk_score: float
    risk_level: str
    pattern_type: str
    flagged_snippet: str
    explanation: str
    status: str = "unreviewed"
    created_at: Optional[str] = None

class AlertDetail(AlertSummary):
    model: Optional[str] = None
    confidence: Optional[float] = None
    child_label: Optional[str] = None
    source_platform: Optional[str] = None
    language: Optional[str] = None

class DashboardSummary(BaseModel):
    total_alerts: int
    low_count: int = 0
    medium_count: int = 0
    high_count: int = 0
    unreviewed: Optional[int] = 0
    reviewed: Optional[int] = 0
    messages_analyzed: Optional[int] = 0
    conversations: Optional[int] = 0

class ReportSubmitRequest(BaseModel):
    starting_prompt: Optional[str] = None
    report_text: Optional[str] = ""
    urgency_level: str = "standard"

class ReportSubmitResponse(BaseModel):
    anonymous_token: str
    status: str
    aid_channel_name: Optional[str] = None
    message: str

class ReportStatusResponse(BaseModel):
    status: str
    aid_channel_name: Optional[str] = None
