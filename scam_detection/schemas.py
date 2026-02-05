# schemas.py

def scam_response(
    scam_detected: bool,
    risk_score: int,
    confidence: float,
    signals: list
):
    return {
        "scamDetected": scam_detected,
        "riskScore": risk_score,
        "confidence": round(confidence, 2),
        "signals": list(set(signals))
    }
