# text_signals.py

TEXT_SIGNAL_RISK = {
    "urgency": (["urgent", "immediately", "today", "now", "last warning"], 15),
    "threat": (["blocked", "suspended", "terminated", "closed"], 20),
    "authority": (["bank", "rbi", "customer care", "support"], 10),
    "financial_action": (["verify", "update", "confirm"], 15),
    "credential_request": (["otp", "upi", "pin", "password"], 30),
    "link": (["http", "https", "bit.ly", "tinyurl"], 25),
}

KNOWN_SCRIPTS = [
    "account will be blocked",
    "verify immediately",
    "avoid suspension",
    "kyc update required",
    "service will stop today"
]


def analyze_text(text: str):
    text = text.lower()
    risk = 0
    signals = []

    for signal, (keywords, score) in TEXT_SIGNAL_RISK.items():
        if any(k in text for k in keywords):
            risk += score
            signals.append(signal)

    for script in KNOWN_SCRIPTS:
        if script in text:
            risk += 20
            signals.append("known_scam_script")
            break

    # Structural patterns
    if text.isupper():
        risk += 10
        signals.append("all_caps")

    if len(text.split()) < 8:
        risk += 5
        signals.append("short_command")

    return risk, signals
