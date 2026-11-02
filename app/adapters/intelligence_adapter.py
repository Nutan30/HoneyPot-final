import asyncio
import logging
from typing import Dict, Any, Optional
import httpx

from intelligence.main import run_intelligence
from app.config import GUVI_CALLBACK_URL
from app.database.repository import SessionRepository

logger = logging.getLogger(__name__)


def build_callback_payload(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs the standardized callback payload for GUVI evaluation endpoint.
    Extracts dynamic agent notes and all captured IOCs.
    """
    raw_intel = session.get("extractedIntelligence", {})
    if isinstance(raw_intel, dict) and "extractedIntelligence" in raw_intel:
        raw_intel = raw_intel["extractedIntelligence"]

    extracted = {
        "bankAccounts": raw_intel.get("bankAccounts", []) if isinstance(raw_intel, dict) else [],
        "upiIds": raw_intel.get("upiIds", []) if isinstance(raw_intel, dict) else [],
        "phishingLinks": raw_intel.get("phishingLinks", []) if isinstance(raw_intel, dict) else [],
        "phoneNumbers": raw_intel.get("phoneNumbers", []) if isinstance(raw_intel, dict) else [],
        "suspiciousKeywords": raw_intel.get("suspiciousKeywords", []) if isinstance(raw_intel, dict) else []
    }

    agent_notes = (
        session.get("agentNotes")
        or (raw_intel.get("agentNotes") if isinstance(raw_intel, dict) else None)
        or "Scammer engaged via automated honeypot victim persona. Urgency and verification tactics observed."
    )

    return {
        "sessionId": session.get("sessionId"),
        "scamDetected": bool(session.get("scamDetected", False)),
        "totalMessagesExchanged": int(session.get("totalMessages", 0)),
        "extractedIntelligence": extracted,
        "agentNotes": agent_notes
    }


async def dispatch_callback_async(
    session: Dict[str, Any],
    callback_url: Optional[str] = None,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> bool:
    """
    Dispatches session intelligence to the callback endpoint asynchronously with exponential backoff.
    """
    url = callback_url or GUVI_CALLBACK_URL
    session_id = session.get("sessionId", "unknown")
    payload = build_callback_payload(session)

    logger.info(f"Initiating async callback dispatch for session {session_id} to {url}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.post(url, json=payload)
                if 200 <= response.status_code < 300:
                    logger.info(f"Callback SUCCESS for session {session_id} (HTTP {response.status_code})")
                    session["callbackSent"] = True
                    try:
                        SessionRepository.set_callback_sent(session_id, True)
                    except Exception as e:
                        logger.warning(f"Failed to record callback status in DB: {e}")
                    return True
                else:
                    logger.warning(
                        f"Callback attempt {attempt}/{max_retries} received HTTP {response.status_code} for {session_id}"
                    )
            except Exception as e:
                logger.warning(f"Callback attempt {attempt}/{max_retries} failed for {session_id}: {e}")

            if attempt < max_retries:
                delay = base_delay * (2 ** (attempt - 1))
                await asyncio.sleep(delay)

    logger.error(f"Callback exhausted all {max_retries} retries for session {session_id}")
    return False


def send_guvi_callback(session: Dict[str, Any]) -> bool:
    """
    Synchronous fallback wrapper for dispatching the callback.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(dispatch_callback_async(session))
            return True
        else:
            return loop.run_until_complete(dispatch_callback_async(session))
    except RuntimeError:
        # No running event loop
        return asyncio.run(dispatch_callback_async(session))


def process_intelligence(session: Dict[str, Any]):
    """
    Adapter for intelligence processing.
    Runs extraction pipeline on LIVE session data and dispatches async callback when threshold met.
    """
    try:
        run_intelligence(session)
    except Exception as e:
        logger.error(f"Intelligence processing error for session {session.get('sessionId')}: {e}")

    # Send callback only when criteria are met
    should_send = (
        session.get("scamDetected")
        and session.get("agentActive")
        and session.get("totalMessages", 0) >= 5
        and not session.get("callbackSent")
    )

    if should_send:
        send_guvi_callback(session)
