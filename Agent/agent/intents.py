import re

INTENT_KEYWORDS = {
    "otp_request": ["otp", "one time", "code", "kode", "password", "pasword"],
    "upi_request": ["upi", "google pay", "phonepe", "paytm", "gpay", "bhim", "paise", "paisa", "rupaye", "rupya"],
    "authority_claim": ["bank", "axis", "hdfc", "sbi", "icici", "rbi", "employee", "officer", "police", "government", "income tax", "customs", "cbi", "sarkar", "adhikari", "afsar", "from bank", "axis bank", "hdfc bank", "sbi bank"],
    "urgency_threat": ["blocked", "freeze", "urgent", "final", "immediately", "today", "arrest", "legal action", "band", "block", "jaldi", "turant", "abhi", "aaj", "pakad", "giraftar", "flagged", "suspicious", "activity", "verify"],
    "send_link": ["link", "click", "update", "download", "install", "app", "click karo", "dabao", "press karo"],
    "channel_shift": ["call", "whatsapp", "telegram", "video call", "phone karo", "call karo", "whatsapp pe"],
    "reward_claim": ["reward", "cashback", "won", "lottery", "prize", "congratulations", "selected", "jeet", "jeeta", "inaam", "badhai", "mubarak"],
    "money_request": ["send money", "need money", "rs", "rupees", "help me", "paise bhejo", "paise bhej", "paisa chahiye", "madad", "help", "money send", "paisa send"],
    "medical_emergency": ["emergency", "medical", "accident", "hospital", "emergency hai", "hospital mein", "doctor", "operation", "treatment"],
    "friend_scam": ["friend", "college", "school", "know each other", "remember me", "classmate", "dost", "yaar", "bhai"],
    "job_offer": ["job", "work from home", "earn money", "part time", "data entry", "typing work", "income", "kaam", "naukri", "ghar se kaam", "paisa kamao", "typing ka kaam"],
    "investment_scam": ["investment", "trading", "profit", "returns", "stock", "crypto", "bitcoin", "double money", "nivesh", "fayda", "munafa", "share", "trading karo", "paisa double"],
    "tech_support": ["computer", "virus", "malware", "microsoft", "windows", "technical support", "infected", "laptop", "mobile", "phone", "kharab", "problem", "virus aaya"],
    "romance_scam": ["love", "marry", "relationship", "lonely", "beautiful", "handsome", "meet you", "pyaar", "mohabbat", "shaadi", "milna", "sundar", "khubsurat"],
    "fake_delivery": ["delivery", "courier", "package", "parcel", "shipping", "customs duty", "fedex", "dhl", "saman", "packet", "delivery boy", "courier boy"]
}

def detect_intent(text: str) -> str:
    """Score-based intent detection with word boundaries"""
    text_lower = text.lower()
    intent_scores = {}
    
    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # Use word boundaries to avoid substring matches
            if re.search(rf'\b{re.escape(keyword)}\b', text_lower):
                score += 1
        
        if score > 0:
            intent_scores[intent] = score
    
    if not intent_scores:
        return "unknown"
    
    # Return intent with highest score
    return max(intent_scores, key=intent_scores.get)
