import os
import re
from typing import Dict, Any, Optional
from app.database.repository import SessionRepository

sessions: Dict[str, Dict[str, Any]] = {}

# Strict session ID validation: alphanumeric, hyphens, underscores only (4-64 chars)
SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{4,64}$')


def validate_session_id(session_id: str) -> str:
    """
    Validate and sanitize session ID to prevent path traversal attacks.
    Rejects IDs containing directory separators, dots, or other dangerous characters.
    """
    if not session_id or not SESSION_ID_PATTERN.match(session_id):
        raise ValueError(
            f"Invalid session ID: '{session_id}'. "
            "Must be 4-64 characters, alphanumeric/hyphens/underscores only."
        )
    return session_id


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve session from cache or SQLite database."""
    validate_session_id(session_id)
    if session_id in sessions:
        return sessions[session_id]

    data = SessionRepository.get_session_dict(session_id)
    if data:
        sessions[session_id] = data
        return sessions[session_id]
    return None


def get_or_create_session(session_id: str) -> Dict[str, Any]:
    """Retrieve or initialize a unified session in SQLite and memory."""
    validate_session_id(session_id)

    if session_id not in sessions:
        sessions[session_id] = SessionRepository.get_or_create_dict(session_id)

    return sessions[session_id]


def sync_session_to_db(session: Dict[str, Any]) -> None:
    """Persist session changes from memory to SQLite."""
    session_id = session.get("sessionId")
    if not session_id:
        return

    SessionRepository.update_detection(
        session_id=session_id,
        scam_detected=session.get("scamDetected", False),
        confidence=session.get("confidence", 0.0),
        agent_active=session.get("agentActive", False)
    )

    intel = session.get("extractedIntelligence", {})
    if intel:
        SessionRepository.update_intelligence(
            session_id=session_id,
            extracted_intelligence=intel.get("extractedIntelligence", intel),
            agent_notes=session.get("agentNotes", intel.get("agentNotes")),
            scam_classification=session.get("scamClassification", intel.get("scamClassification")),
            scam_detected=session.get("scamDetected", False)
        )


def save_message_to_file(session_id: str, role: str, content: str) -> None:
    """Save message to SQLite and maintain file log for backward compatibility."""
    validate_session_id(session_id)

    # 1. Save to SQLite database
    SessionRepository.add_message(session_id, sender=role, text=content)

    # 2. Maintain raw text file log with path-containment protection
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "intelligence", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    file_path = os.path.join(raw_dir, f"{session_id}.txt")
    resolved = os.path.realpath(file_path)
    if not resolved.startswith(os.path.realpath(raw_dir)):
        raise ValueError(f"Path traversal detected for session ID: '{session_id}'")

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{role}: {content}\n")
