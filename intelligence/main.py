import os
import yaml
import logging

from intelligence.extraction.regex_extractor import (
    extract_phone_numbers,
    extract_upi_ids,
    extract_phishing_links
)
from intelligence.validation.validators import (
    validate_phone_numbers,
    validate_upi_ids
)
from intelligence.storage.json_storage import save_to_json
from intelligence.extraction.llm_extractor import ai_extract_insights
from intelligence.extraction.scam_classifier import classify_scam
from intelligence.extraction.keyword_extractor import extract_suspicious_keywords


# ---------------- CONFIG & LOGGING ---------------- #

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, "configs", "config.yaml")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def setup_logging():
    logging.basicConfig(
        filename=os.path.join(LOG_DIR, "system.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


# ---------------- MAIN RUNTIME FUNCTION ---------------- #

def run_intelligence(session: dict):
    print("🔥 run_intelligence CALLED for session:", session.get("sessionId"))

    """
    Runs intelligence extraction on a LIVE session.
    Called from /message endpoint.
    """

    setup_logging()

    session_id = session.get("sessionId")
    messages = session.get("messages", [])
    # ✅ Convert message dicts → plain text strings
    texts = []

    for msg in messages:
        if isinstance(msg, dict) and "text" in msg:
            texts.append(msg["text"])
        elif isinstance(msg, str):
            texts.append(msg)

    if not session_id or not messages:
        logging.warning("No session data available for intelligence")
        return

    logging.info(f"Processing intelligence for session {session_id}")

    # ---- Extraction ---- #
    raw_phones = extract_phone_numbers(texts)
    raw_upis = extract_upi_ids(texts)
    links = extract_phishing_links(texts)
    suspicious_keywords = extract_suspicious_keywords(texts)
    phones = validate_phone_numbers(raw_phones)
    upis = validate_upi_ids(raw_upis)
    ai_insights = ai_extract_insights(texts)
    scam_label = classify_scam(texts, ai_insights)



    # ---- Final Intelligence Object ---- #
    intelligence_payload = {
        "sessionId": session_id,
        "scamDetected": bool(scam_label),
        "totalMessagesExchanged": len(messages),
        "extractedIntelligence": {
            "bankAccounts": [],
            "upiIds": upis,
            "phishingLinks": links,
            "phoneNumbers": phones,
            "suspiciousKeywords": suspicious_keywords
        },
        "agentNotes": "Urgency tactics and payment redirection observed"
    }

    # ---- Persist ---- #
    output_file = f"{session_id}.json"
    save_to_json(
        filename=f"{session_id}.json",
        data=intelligence_payload

    )


    # ---- Attach to session (for callback use) ---- #
    session["extractedIntelligence"] = intelligence_payload

    logging.info(f"Saved intelligence for session {session_id}")
