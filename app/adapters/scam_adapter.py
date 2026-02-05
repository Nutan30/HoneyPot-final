from scam_detection.detector import detect_scam as core_detect_scam

def detect_scam(text: str, session: dict) -> dict:
    result = core_detect_scam(
        text,
        session.get("messages", []),
        session.get("metadata", {})
    )

    return {
        "scamDetected": bool(result.get("scamDetected", False)),
        "confidence": float(result.get("confidence", 0.0)),
        "signals": result.get("signals", [])
    }
