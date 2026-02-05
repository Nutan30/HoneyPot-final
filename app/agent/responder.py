def generate_reply(session: dict, latest_message: str) -> str:
    msg = latest_message.lower()
    confidence = session["confidence"]
    turn = session["totalMessages"]

    if not session["agentActive"]:
        return "Okay, thanks for the update."

    # Early probing
    if turn <= 2:
        if "bank" in msg:
            return "Which bank are you referring to?"
        return "Why are you asking me to verify this?"

    # Mid extraction
    if 0.6 <= confidence < 0.85:
        if "otp" in msg:
            return "I didn’t receive any OTP. Can you resend?"
        return "Is there any official message or reference number?"

    # High confidence bait
    if confidence >= 0.85:
        return "I already verified once. What else is pending?"

    return "Please explain again."
