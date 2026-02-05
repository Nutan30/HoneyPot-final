# test_detector.py

from detector import detect_scam

tests = [
    {
        "text": "Your bank account will be blocked today. Verify immediately.",
        "history": [],
        "metadata": {"channel": "SMS"}
    },
    {
        "text": "OTP for your login is 123456",
        "history": [],
        "metadata": {"channel": "SMS"}
    },
    {
        "text": "Share your UPI ID to avoid suspension",
        "history": [
            {"text": "Urgent! Your account is under review"},
            {"text": "This is the last warning"}
        ],
        "metadata": {"channel": "SMS"}
    }
]

for t in tests:
    print("\nMessage:", t["text"])
    print(detect_scam(t["text"], t["history"], t["metadata"]))
