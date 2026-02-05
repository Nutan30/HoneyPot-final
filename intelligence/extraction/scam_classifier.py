def classify_scam(messages, ai_insights):
    text = " ".join(messages).lower()

    # Rule-based checks (high accuracy)
    if "otp" in text:
        return "OTP_SCAM"

    if "upi" in text or "send money" in text:
        return "UPI_FRAUD"

    if "bank" in text or "rbi" in text or "account blocked" in text:
        return "FAKE_BANK"

    # Fallback to AI understanding
    if ai_insights["scam_type"] != "UNKNOWN":
        return ai_insights["scam_type"]

    return "UNKNOWN"
