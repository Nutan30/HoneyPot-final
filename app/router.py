from fastapi import APIRouter, Depends, Request
from app.adapters.scam_adapter import detect_scam
from app.adapters.agent_adapter import get_agent_reply
from app.adapters.intelligence_adapter import process_intelligence
from .schemas import MessageRequest, MessageResponse
from .auth import verify_api_key
from .session_manager import get_or_create_session, get_session, save_message_to_file


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
        # GUVI tester case (empty body)
        return MessageResponse(
            status="success",
            reply="Honeypot endpoint active."
        )

    # If body is empty or missing required fields (GUVI tester)
    if not body or "message" not in body or "sessionId" not in body:
        return MessageResponse(
            status="success",
            reply="Honeypot endpoint active."
        )

    # ---- NORMAL FLOW STARTS HERE ----

    data = MessageRequest(**body)

    session = get_or_create_session(data.sessionId)

    session["messages"].append(data.message.dict())
    session["totalMessages"] += 1

    detection = detect_scam(data.message.text, session)

    if detection["scamDetected"] and not session["agentActive"]:
        session["scamDetected"] = True
        session["agentActive"] = True

    session["confidence"] = detection["confidence"]

    if not session["agentActive"]:
        reply = "Okay, noted."
    else:
        reply = get_agent_reply(session, data.message.text)

    process_intelligence(session)

    return MessageResponse(
        status="success",
        reply=reply
    )

@router.get("/debug/intelligence/{session_id}")
def get_intelligence(session_id: str):
    session = get_session(session_id)
    return session.get("extractedIntelligence", {})
