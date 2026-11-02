import os
import json
import logging
from app.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)


def ai_extract_insights(messages: list) -> dict:
    """
    Extracts deep threat intelligence insights using OpenAI LLM analysis,
    including scam typology, attacker intent, persuasion tactics, and actor persona.
    Falls back to heuristic analysis when offline.
    """
    if not messages:
        return {
            "scam_type": "UNKNOWN",
            "intent": [],
            "tactics": [],
            "confidence": 0.0,
            "threat_actor_persona": "None"
        }

    combined_text = "\n".join(str(m) for m in messages[-10:])
    api_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

    # Live OpenAI Analysis
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            prompt = f"""You are a Cyber Threat Intelligence (CTI) analyst examining deceptive communications.
Analyze this honeypot conversation between a scammer and victim:

\"\"\"
{combined_text}
\"\"\"

Produce structured cyber intelligence as a valid JSON object matching this schema:
{{
  "scam_type": "One of: BANK_KYC_FRAUD, UPI_PHISHING, ELECTRICITY_BILL_SCAM, JOB_OFFER_SCAM, LOTTERY_FRAUD, TECH_SUPPORT_SCAM, MEDICAL_EMERGENCY_SCAM, UNKNOWN",
  "intent": ["list", "of", "attacker", "intents", "e.g.", "steal_otp", "collect_vpa_payment", "harvest_credentials"],
  "tactics": ["list", "of", "tactics", "e.g.", "urgency", "fear", "authority_impersonation", "social_proof"],
  "confidence": float between 0.0 and 1.0,
  "threat_actor_persona": "Who the scammer claims to be, e.g. SBI Security Officer or Electricity Board Official"
}}
"""
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=7.0
            )

            result = json.loads(response.choices[0].message.content)
            return {
                "scam_type": str(result.get("scam_type", "UNKNOWN")),
                "intent": list(result.get("intent", [])),
                "tactics": list(result.get("tactics", [])),
                "confidence": float(result.get("confidence", 0.85)),
                "threat_actor_persona": str(result.get("threat_actor_persona", "Impersonator"))
            }

        except Exception as e:
            logger.warning(f"OpenAI CTI extraction fallback triggered: {e}")

    # Heuristic Fallback Analysis
    text = combined_text.lower()
    scam_type = "UNKNOWN"
    intent = []
    tactics = []

    if "otp" in text or "pin" in text:
        scam_type = "OTP_SCAM"
        intent.append("steal_otp")

    if any(k in text for k in ["upi", "gpay", "phonepe", "paytm", "vpa"]):
        scam_type = "UPI_PHISHING"
        intent.append("collect_vpa_payment")

    if any(k in text for k in ["blocked", "suspend", "freeze", "kyc"]) and any(k in text for k in ["bank", "account", "rbi", "sbi"]):
        if scam_type == "UNKNOWN":
            scam_type = "BANK_KYC_FRAUD"
        intent.append("account_takeover")

    if "blocked" in text or "suspend" in text or "freeze" in text:
        tactics.append("fear")

    if "immediately" in text or "urgent" in text or "today" in text or "now" in text:
        tactics.append("urgency")

    if "rbi" in text or "bank" in text or "sbi" in text or "police" in text:
        tactics.append("authority_impersonation")

    if "electricity" in text or "power" in text:
        scam_type = "ELECTRICITY_BILL_SCAM"

    return {
        "scam_type": scam_type,
        "intent": list(set(intent)),
        "tactics": list(set(tactics)),
        "confidence": 0.6 if scam_type != "UNKNOWN" else 0.2,
        "threat_actor_persona": "Alleged Authority / Official" if "authority_impersonation" in tactics else "Unknown"
    }
