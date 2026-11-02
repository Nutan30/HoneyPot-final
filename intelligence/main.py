import os
import yaml
import logging

from intelligence.extraction.regex_extractor import (
    extract_phone_numbers,
    extract_upi_ids,
    extract_phishing_links,
    extract_ifsc_codes,
    extract_bank_accounts,
    extract_crypto_addresses
)
from intelligence.validation.validators import (
    validate_phone_numbers,
    validate_upi_ids,
    validate_ifsc_codes,
    validate_bank_accounts,
    validate_crypto_addresses,
    enrich_phishing_links
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


def _generate_agent_notes(ai_insights, suspicious_keywords, links, upis, phones, accounts=None, ifscs=None, crypto=None):
    """Generate dynamic agent notes based on actual extraction results."""
    notes = []

    tactics = ai_insights.get("tactics", [])
    if "urgency" in tactics:
        notes.append("Urgency tactics detected")
    if "fear" in tactics:
        notes.append("Fear-based pressure observed")
    if "authority_impersonation" in tactics:
        notes.append("Authority impersonation attempted")

    scam_type = ai_insights.get("scam_type", "UNKNOWN")
    if scam_type != "UNKNOWN":
        notes.append(f"Scam type: {scam_type}")

    if links:
        notes.append(f"Phishing links found: {len(links)}")
    if upis:
        notes.append(f"UPI IDs extracted: {len(upis)}")
    if phones:
        notes.append(f"Phone numbers captured: {len(phones)}")
    if accounts:
        notes.append(f"Bank accounts captured: {len(accounts)}")
    if ifscs:
        notes.append(f"IFSC codes found: {len(ifscs)}")
    if crypto:
        notes.append(f"Crypto wallets identified: {len(crypto)}")
    if suspicious_keywords:
        notes.append(f"Suspicious keywords: {', '.join(suspicious_keywords[:5])}")

    return " | ".join(notes) if notes else "Monitoring in progress"


# ---------------- MAIN RUNTIME FUNCTION ---------------- #

def run_intelligence(session: dict):
    """
    Runs intelligence extraction on a LIVE session.
    Called from /message endpoint.
    """

    setup_logging()

    session_id = session.get("sessionId")
    messages = session.get("messages", [])
    # Convert message dicts → plain text strings
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
    raw_links = extract_phishing_links(texts)
    raw_ifscs = extract_ifsc_codes(texts)
    raw_accounts = extract_bank_accounts(texts)
    raw_crypto = extract_crypto_addresses(texts)
    suspicious_keywords = extract_suspicious_keywords(texts)

    # ---- Validation & Enrichment ---- #
    phones = validate_phone_numbers(raw_phones)
    upis = validate_upi_ids(raw_upis)
    ifscs = validate_ifsc_codes(raw_ifscs)
    bank_accounts = validate_bank_accounts(raw_accounts)
    crypto = validate_crypto_addresses(raw_crypto)
    enriched_links = enrich_phishing_links(raw_links)

    ai_insights = ai_extract_insights(texts)
    scam_label = classify_scam(texts, ai_insights)

    # Explicitly check for real scam labels
    scam_detected = bool(scam_label and scam_label != "UNKNOWN")

    # Generate dynamic notes from actual analysis
    agent_notes = _generate_agent_notes(
        ai_insights, suspicious_keywords, raw_links, upis, phones,
        accounts=bank_accounts, ifscs=ifscs, crypto=crypto
    )

    # ---- Final Intelligence Object ---- #
    intelligence_payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": len(messages),
        "extractedIntelligence": {
            "bankAccounts": bank_accounts,
            "upiIds": upis,
            "phishingLinks": raw_links,
            "phoneNumbers": phones,
            "ifscCodes": ifscs,
            "cryptoAddresses": crypto,
            "enrichedLinks": enriched_links,
            "suspiciousKeywords": suspicious_keywords
        },
        "agentNotes": agent_notes,
        "scamClassification": scam_label,
        "aiInsights": ai_insights
    }

    # ---- Persist ---- #
    save_to_json(
        filename=f"{session_id}.json",
        data=intelligence_payload
    )

    # Persist to unified SQLite repository
    try:
        from app.database.repository import SessionRepository
        SessionRepository.update_intelligence(
            session_id=session_id,
            extracted_intelligence=intelligence_payload["extractedIntelligence"],
            agent_notes=agent_notes,
            scam_classification=scam_label,
            scam_detected=scam_detected
        )
    except Exception as e:
        logging.warning(f"Could not persist to SQLite: {e}")

    # ---- Merge into session (preserve agent-side intelligence, don't overwrite) ---- #
    existing_intel = session.get("extractedIntelligence", {})
    if isinstance(existing_intel, dict) and "extractedIntelligence" not in existing_intel:
        # Session has flat intelligence from agent — wrap and merge
        merged = intelligence_payload
    else:
        # Merge: keep agent-collected data, overlay with pipeline results
        merged = intelligence_payload
        if isinstance(existing_intel, dict):
            # Preserve any agent-side fields not in our pipeline output
            for key, value in existing_intel.items():
                if key not in merged and value:
                    merged[key] = value

    session["extractedIntelligence"] = merged

    logging.info(f"Saved intelligence for session {session_id}")
