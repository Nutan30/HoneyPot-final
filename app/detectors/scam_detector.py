def detect_scam(text: str, session: dict):
    text = text.lower()

    score = 0.0
    matched = []

    # 🔴 HIGH RISK (Immediate scam indicators)
    high_risk = {
        "otp", "one-time password", "share otp", "verify otp",
        "pin", "cvv", "password", "login details",
        "authentication failed", "reset password",
        "unauthorized access", "account compromised"
    }

    # 🟠 MEDIUM RISK (Social engineering)
    medium_risk = {
        "urgent", "immediate action", "act now", "last warning",
        "final notice", "within 24 hours", "expires today",
        "respond immediately", "time-sensitive",
        "account blocked", "account suspended", "wallet blocked",
        "kyc update", "bank verification"
    }

    # 🟡 IMPERSONATION / BRAND ABUSE
    brand_impersonation = {
        "sbi", "hdfc", "icici", "paytm", "phonepe",
        "amazon", "flipkart", "google security",
        "microsoft support", "uidai", "pan blocked",
        "income tax department", "trai"
    }

    # 🔵 LINK / CTA BAIT
    action_bait = {
        "click here", "verify now", "update now",
        "login here", "tap to confirm", "secure link",
        "bit.ly", "tinyurl"
    }

    # 🟢 REWARD / LURE
    reward_lure = {
        "congratulations", "you have won", "lucky winner",
        "lottery winner", "prize money", "free gift",
        "cashback offer", "reward points", "exclusive deal"
    }

    # --- Scoring logic ---
    for word in high_risk:
        if word in text:
            score += 0.5
            matched.append(word)

    for word in medium_risk:
        if word in text:
            score += 0.3
            matched.append(word)

    for word in brand_impersonation:
        if word in text:
            score += 0.2
            matched.append(word)

    for word in action_bait:
        if word in text:
            score += 0.2
            matched.append(word)

    for word in reward_lure:
        if word in text:
            score += 0.2
            matched.append(word)


    escalation = min(0.1 * session["totalMessages"], 0.4)
    score += escalation

    score = min(score, 1.0)

    return {
        "scamDetected": score >= 0.6,
        "confidence": round(score, 2),
        "signals": matched
    }
