def extract_suspicious_keywords(messages):
    keywords = [
        "urgent",
        "verify now",
        "account blocked",
        "immediately",
        "suspend"
    ]

    text = " ".join(messages).lower()
    found = []

    for k in keywords:
        if k in text:
            found.append(k)

    return found
