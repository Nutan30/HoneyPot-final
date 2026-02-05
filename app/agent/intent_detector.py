def detect_intent(text: str) -> str:
    text = text.lower()

    if any(k in text for k in ["otp", "one-time password", "verify otp"]):
        return "OTP_SCAM"

    if any(k in text for k in ["account blocked", "account suspended", "wallet blocked"]):
        return "BANK_THREAT"

    if any(k in text for k in ["urgent", "act now", "immediate action", "last warning"]):
        return "URGENCY_PRESSURE"

    if any(k in text for k in ["amazon", "flipkart", "sbi", "hdfc", "icici"]):
        return "BRAND_IMPERSONATION"

    if any(k in text for k in ["won", "cashback", "reward", "lottery"]):
        return "REWARD_SCAM"

    if any(k in text for k in ["delivery", "package", "customs", "shipment"]):
        return "DELIVERY_SCAM"

    if any(k in text for k in ["fir", "arrest", "court notice", "legal action"]):
        return "LEGAL_THREAT"

    return "GENERIC_SCAM"
