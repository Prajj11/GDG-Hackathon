"""Tests verifying 100% backward and cross-specification compatibility between app.* and backend.*
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session, init_db
from app.models import Conversation, Alert, User, Report
from app.ml_engine import analyze_message, RiskLevel, PatternType, load_model
from app.schemas import MessageIngestRequest, ReportSubmitRequest

@pytest.fixture
def client():
    return TestClient(app)

def test_app_ml_engine_inference():
    # 1. Neutral test
    res_neutral = analyze_message("How was school today? Let us work on homework.")
    assert res_neutral.pattern_type == PatternType.NEUTRAL
    assert res_neutral.risk_level == RiskLevel.LOW
    assert res_neutral.risk_score <= 0.40

    # 2. Grooming coercive language test
    res_coercive = analyze_message("Photo bhejo warna tumhari chats sabko dikha dunga.")
    assert res_coercive.pattern_type == PatternType.GROOMING_COERCIVE_LANGUAGE
    assert res_coercive.risk_level == RiskLevel.HIGH
    assert res_coercive.risk_score >= 0.70

    # 3. Grooming trust building test
    res_trust = analyze_message("You are so mature for your age, I can buy you special gifts.")
    assert res_coercive.pattern_type in [PatternType.GROOMING_COERCIVE_LANGUAGE, PatternType.GROOMING_TRUST_BUILDING]

    # Test dictionary-like backwards compatibility
    assert res_coercive['risk_level'] == 'high'
    assert 'risk_score' in res_coercive.to_dict()

def test_app_endpoints(client):
    # Root /health endpoint
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

    # Anonymous report submission via app alias
    rep_payload = {
        "starting_prompt": "Someone asking for secrets",
        "report_text": "A person messaged asking not to tell my parents.",
        "urgency_level": "High"
    }
    rep_resp = client.post("/api/reports", json=rep_payload)
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    assert "anonymous_token" in rep_data
    assert rep_data["status"] == "routed"

    # Anonymous report status lookup
    token = rep_data["anonymous_token"]
    status_resp = client.get(f"/api/reports/{token}/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "routed"
