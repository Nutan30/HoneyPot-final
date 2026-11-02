from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from typing import Optional, List
from app.adapters.scam_adapter import detect_scam
from app.adapters.agent_adapter import get_agent_reply
from app.adapters.intelligence_adapter import process_intelligence
from app.database.repository import SessionRepository
from intelligence.stix.exporter import export_session_to_stix
from intelligence.deception.honey_tokens import HoneyTokenRegistry
from .schemas import MessageRequest, MessageResponse
from .auth import verify_api_key
from .session_manager import (
    get_or_create_session,
    get_session,
    sync_session_to_db,
    save_message_to_file
)


router = APIRouter()

@router.post("/message", response_model=MessageResponse)
async def receive_message(
    request: Request,
    _: str = Depends(verify_api_key)
):
    # Try reading JSON body
    try:
        body = await request.json()
    except Exception:
        # Empty body fallback (e.g., health check probes)
        return MessageResponse(
            status="success",
            reply="Honeypot endpoint active."
        )

    # If body is empty or missing required fields
    if not body or "message" not in body or "sessionId" not in body:
        return MessageResponse(
            status="success",
            reply="Honeypot endpoint active."
        )

    # ---- NORMAL FLOW STARTS HERE ----

    try:
        data = MessageRequest(**body)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid request body: {str(e)}")

    try:
        session = get_or_create_session(data.sessionId)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Record incoming message in memory, SQLite, and file log
    msg_dict = data.message.model_dump()
    session["messages"].append(msg_dict)
    session["totalMessages"] += 1

    sender_name = getattr(data.message, "sender", "scammer") or "scammer"
    save_message_to_file(data.sessionId, sender_name, data.message.text)

    # Run scam detection
    detection = detect_scam(data.message.text, session)

    if detection["scamDetected"] and not session["agentActive"]:
        session["scamDetected"] = True
        session["agentActive"] = True

    session["confidence"] = detection["confidence"]

    # Generate reply
    if not session["agentActive"]:
        reply = "Okay, noted."
    else:
        reply = get_agent_reply(session, data.message.text)

    # Record agent reply in SQLite and file log
    save_message_to_file(data.sessionId, "agent", reply)

    # Process intelligence pipeline
    process_intelligence(session)

    # Persist updated session state to SQLite database
    sync_session_to_db(session)

    return MessageResponse(
        status="success",
        reply=reply
    )


@router.get("/debug/intelligence/{session_id}")
def get_intelligence(
    session_id: str,
    _: str = Depends(verify_api_key)
):
    """Debug endpoint to inspect extracted intelligence. Requires API key authentication."""
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.get("extractedIntelligence", {})


@router.get("/api/sessions")
def list_sessions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    scam_only: bool = Query(False),
    _: str = Depends(verify_api_key)
):
    """List sessions with pagination and scam filter for monitoring dashboard."""
    return SessionRepository.list_sessions(limit=limit, offset=offset, scam_only=scam_only)


@router.get("/api/stats")
def get_stats(
    _: str = Depends(verify_api_key)
):
    """Retrieve aggregate honeypot statistics for monitoring dashboard."""
    return SessionRepository.get_stats()


@router.get("/api/stix/{session_id}")
def get_session_stix(
    session_id: str,
    _: str = Depends(verify_api_key)
):
    """Generates an OASIS STIX 2.1 Threat Intelligence bundle for the session."""
    session = get_session(session_id) or SessionRepository.get_session_dict(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return export_session_to_stix(session)


@router.get("/api/iocs")
def list_extracted_iocs(
    ioc_type: Optional[str] = Query(None, description="Filter by IOC type (upi, phone, link, bank_account, ifsc, crypto)"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: str = Depends(verify_api_key)
):
    """Retrieve filterable extracted IOCs across sessions for threat intelligence consumers."""
    return SessionRepository.list_iocs(
        ioc_type=ioc_type,
        session_id=session_id,
        limit=limit,
        offset=offset
    )


@router.get("/canary/{token_id}")
def trap_canary_token(
    token_id: str,
    request: Request
):
    """
    Public deception endpoint for tracking scammer interactions.
    Captures visitor IP, User-Agent, and timestamp, returning a deceptive response.
    """
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (request.client.host if request.client else "unknown")
    user_agent = request.headers.get("user-agent", "unknown")

    record = HoneyTokenRegistry.trip_token(
        token_id=token_id,
        client_ip=client_ip,
        user_agent=user_agent
    )

    if not record:
        raise HTTPException(status_code=404, detail="Token expired or invalid")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Payment Portal - Session Expired</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #1e293b; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
        .card {{ background: white; padding: 2.5rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); max-width: 440px; text-align: center; border: 1px solid #e2e8f0; }}
        .icon {{ font-size: 3rem; margin-bottom: 1rem; color: #eab308; }}
        h1 {{ font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; }}
        p {{ color: #64748b; font-size: 0.925rem; line-height: 1.5; }}
        .badge {{ background: #f1f5f9; padding: 0.35rem 0.75rem; border-radius: 6px; font-family: monospace; font-size: 0.8rem; color: #475569; display: inline-block; margin-top: 1rem; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">⚠️</div>
        <h1>Verification Session Expired</h1>
        <p>This single-use payment verification token has expired or has already been authenticated.</p>
        <p>Please contact your bank representative to initiate a new secure request.</p>
        <div class="badge">Reference: {token_id}</div>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html_content, status_code=200)
