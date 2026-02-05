# behavior.py

def analyze_behavior(history: list):
    risk = 0
    signals = []

    if not history:
        return risk, signals

    urgency_count = sum(
        "urgent" in h["text"].lower()
        for h in history
    )

    if urgency_count >= 2:
        risk += 10
        signals.append("repeated_urgency")

    escalation_terms = ["last warning", "final notice", "legal action"]
    if any(
        term in h["text"].lower()
        for h in history
        for term in escalation_terms
    ):
        risk += 15
        signals.append("escalation_language")

    return risk, signals
