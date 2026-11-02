import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import API_KEY
from app.session_manager import validate_session_id
from app.database.connection import init_db, SessionLocal
from app.database.models import SessionModel, MessageModel, ExtractedIOCModel
from scam_detection.text_signals import analyze_text
from intelligence.extraction.regex_extractor import extract_upi_ids


@pytest.fixture(scope="module")
def client():
    init_db()
    return TestClient(app)


def test_path_traversal_validation():
    """Verify that path traversal and dangerous characters in session IDs are rejected."""
    dangerous_ids = [
        "../../etc/passwd",
        "../sessions/secret",
        "sub/folder",
        "test\\path",
        "test.session",
        "session;DROP TABLE",
        "a",  # too short (< 4 chars)
        "a" * 65,  # too long (> 64 chars)
        "invalid!@#$"
    ]
    for bad_id in dangerous_ids:
        with pytest.raises(ValueError):
            validate_session_id(bad_id)

    # Valid session IDs should pass
    valid_ids = ["test_session_1", "valid-id-1234", "session_abc-DEF_99"]
    for good_id in valid_ids:
        assert validate_session_id(good_id) == good_id


def test_auth_protection(client):
    """Verify timing-safe authentication and protected debug endpoint."""
    # 1. Missing API key should return 422 or 401
    resp = client.post("/message", json={})
    assert resp.status_code in [401, 422]

    # 2. Invalid API key returns 401
    resp = client.post(
        "/message",
        json={"sessionId": "test-sec-01", "message": {"text": "hello", "sender": "user"}},
        headers={"x-api-key": "WRONG_KEY_HERE"}
    )
    assert resp.status_code == 401

    # 3. Debug endpoint requires authentication
    resp = client.get("/debug/intelligence/test-sec-01")
    assert resp.status_code in [401, 422]

    resp = client.get(
        "/debug/intelligence/test-sec-01",
        headers={"x-api-key": "WRONG_KEY"}
    )
    assert resp.status_code == 401


def test_uppercase_signal_bug_fixed():
    """Verify that ALL-CAPS panic text is properly identified after bug fix."""
    text = "URGENT ACTION REQUIRED IMMEDIATELY YOUR ACCOUNT IS BLOCKED"
    risk, signals = analyze_text(text)
    # Must identify urgency, threat, and all_caps
    assert "all_caps" in signals
    assert "urgency" in signals
    assert "threat" in signals
    assert risk > 30


def test_upi_regex_false_positives_fixed():
    """Verify that normal email addresses are not incorrectly extracted as UPI VPAs."""
    sample_text = [
        "Please send payment to fraudster@okhdfcbank or recovery@paytm immediately.",
        "For official queries email support@google.com and billing@amazon.com."
    ]
    extracted = extract_upi_ids(sample_text)

    # Valid UPIs should be extracted
    assert "fraudster@okhdfcbank" in extracted
    assert "recovery@paytm" in extracted

    # Standard emails should NOT be extracted
    assert "support@google.com" not in extracted
    assert "billing@amazon.com" not in extracted


def test_e2e_message_and_sqlite_persistence(client):
    """End-to-end test verifying scam detection, agent response, and SQLite persistence."""
    session_id = "test_e2e_session_99"

    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "URGENT: Your account will be blocked. Verify immediately or payment service will stop today. Send OTP to verify@oksbi"
        }
    }

    response = client.post(
        "/message",
        json=payload,
        headers={"x-api-key": API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["reply"]) > 0

    # Verify SQLite database was updated
    with SessionLocal() as db:
        session_row = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        assert session_row is not None
        assert session_row.scam_detected is True
        assert session_row.agent_active is True
        assert session_row.total_messages >= 1

        # Check messages table
        messages = db.query(MessageModel).filter(MessageModel.session_id == session_id).all()
        assert len(messages) >= 2  # scammer message + agent reply

        # Check extracted IOCs table
        iocs = db.query(ExtractedIOCModel).filter(ExtractedIOCModel.session_id == session_id).all()
        ioc_values = [ioc.value for ioc in iocs]
        assert "verify@oksbi" in ioc_values


def test_monitoring_endpoints(client):
    """Test dashboard monitoring endpoints /api/sessions and /api/stats."""
    # Stats endpoint
    stats_resp = client.get("/api/stats", headers={"x-api-key": API_KEY})
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert "totalSessions" in stats
    assert "scamsDetected" in stats
    assert "totalMessages" in stats
    assert "uniqueUPIs" in stats
    assert stats["totalSessions"] >= 1

    # Sessions list endpoint
    sessions_resp = client.get("/api/sessions", headers={"x-api-key": API_KEY})
    assert sessions_resp.status_code == 200
    sessions_list = sessions_resp.json()
    assert isinstance(sessions_list, list)
    assert any(s["sessionId"] == "test_e2e_session_99" for s in sessions_list)
