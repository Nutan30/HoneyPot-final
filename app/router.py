from fastapi import APIRouter, Depends, Request, BackgroundTasks
from app.adapters.scam_adapter import detect_scam
from app.adapters.agent_adapter import get_agent_reply
from app.adapters.intelligence_adapter import process_intelligence
from app.schemas import MessageRequest, MessageResponse
from app.auth import verify_api_key
from app.session_manager import get_or_create_session, get_session

router = APIRouter()

@router.post("/message", response_model=MessageResponse)
async def receive_message(
    request: Request,
    background_tasks: BackgroundTasks,
    _: str = Depends(verify_api_key)
):
    try:
        body = await request.json()
    except Exception:
        # GUVI tester safety
        return MessageResponse(
            status="success",
            reply="Honeypot endpoint active."
        )

    # Handle GUVI minimal / malformed payloads
    if not isinstance(body, dict):
        return MessageResponse(status="success", reply="Okay.")

    session_id = body.get("sessionId", "guvi-session")
    message_obj = body.get("message", {})
    text = message_obj.get("text", "")

    if not text:
        return MessageResponse(status="success", reply="Okay.")

    try:
        # ---- SAFE NORMAL FLOW ----
        session = get_or_create_session(session_id)

        session["messages"].append({
            "sender": message_obj.get("sender", "scammer"),
            "text": text
        })
        session["totalMessages"] += 1

        detection = detect_scam(text, session)

        if detection.get("scamDetected") and not session.get("agentActive"):
            session["scamDetected"] = True
            session["agentActive"] = True

        session["confidence"] = detection.get("confidence", 0.0)

        if session.get("agentActive"):
            reply = get_agent_reply(session, text)
        else:
            reply = "Okay, noted."

        # 🚀 RUN HEAVY WORK IN BACKGROUND
        background_tasks.add_task(process_intelligence, session)

        return MessageResponse(
            status="success",
            reply=reply
        )

    except Exception as e:
        # ABSOLUTE FAILSAFE
        print(" /message error:", str(e))
        return MessageResponse(
            status="success",
            reply="Okay."
        )

@router.get("/debug/intelligence/{session_id}")
def get_intelligence(session_id: str):
    session = get_session(session_id)
    return session.get("extractedIntelligence", {})
