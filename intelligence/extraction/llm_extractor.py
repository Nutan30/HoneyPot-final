def ai_extract_insights(messages):
    """
    AI-style extraction using simple rules (LLM placeholder)
    Later this can be replaced with real LLM API
    """

    text = " ".join(messages).lower()

    scam_type = "UNKNOWN"
    intent = []
    tactics = []

    if "otp" in text:
        scam_type = "OTP_SCAM"
        intent.append("steal_otp")

    if "upi" in text:
        scam_type = "UPI_FRAUD"
        intent.append("collect_money")

    if "blocked" in text or "suspend" in text:
        tactics.append("fear")

    if "immediately" in text or "urgent" in text:
        tactics.append("urgency")

    if "rbi" in text or "bank" in text:
        tactics.append("authority_impersonation")

    return {
        "scam_type": scam_type,
        "intent": list(set(intent)),
        "tactics": list(set(tactics))
    }
