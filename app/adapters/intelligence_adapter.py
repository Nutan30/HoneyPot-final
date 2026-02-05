# app/adapters/intelligence_adapter.py

from intelligence.main import run_intelligence
import requests

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"


def process_intelligence(session: dict):
    """
    Adapter for Teammate-4 intelligence system.
    Runs intelligence on LIVE session data.
    """

    try:
        run_intelligence(session)
    except Exception as e:
        print("⚠️ Intelligence error:", e)

    # 🚨 SEND CALLBACK ONLY WHEN READY
    if (
        session.get("scamDetected")
        and session.get("agentActive")
        and session.get("totalMessages", 0) >= 5
        and not session.get("callbackSent")
    ):
        send_guvi_callback(session)


def send_guvi_callback(session: dict):
    payload = {
        "sessionId": session["sessionId"],
        "scamDetected": session.get("scamDetected", False),
        "totalMessagesExchanged": session.get("totalMessages", 0),
        "extractedIntelligence": session.get(
            "extractedIntelligence",
            {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            }
        ),
        "agentNotes": "Scammer used urgency and verification tactics"
    }

    try:
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            timeout=5
        )
        print("GUVI CALLBACK STATUS:", response.status_code)
        session["callbackSent"] = True
    except Exception as e:
        print("GUVI CALLBACK FAILED:", str(e))
