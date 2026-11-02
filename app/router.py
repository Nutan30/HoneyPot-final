from fastapi import APIRouter, Depends, Request, HTTPException, Query
from typing import Optional
from app.adapters.scam_adapter import detect_scam
from app.adapters.agent_adapter import get_agent_reply
from app.adapters.intelligence_adapter import process_intelligence
from app.database.repository import SessionRepository
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
