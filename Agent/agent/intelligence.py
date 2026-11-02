import re
from collections import Counter
import time

class IntelligenceProfile:
    def __init__(self):
        self.upi_ids = set()
        self.phones = set()
        self.links = set()
        self.bank_accounts = set()
        self.suspicious_keywords = Counter()
        self.sources = {}  # value -> timestamp
        self.extracted_info = {}  # Store names, locations, etc.
        
    def extract(self, text):
        """Extract intelligence from scammer message"""
        timestamp = time.time()
        
        # Extract names from explicit introductions ONLY - require 2+ words
        name_match = re.search(r'(?:i am|i\'m|my name is|this is|call me)\s+([a-zA-Z\s]+)', text, re.IGNORECASE)
        if name_match:
            clean_name = name_match.group(1).strip().title()
            if len(clean_name.split()) >= 2:  # Require 2+ words to avoid "Apollo" as name
                self.extracted_info['name'] = clean_name
                self.sources[clean_name] = timestamp
        
        # Extract amounts (₹, rs, numbers with lakh/crore)
        amount_matches = re.findall(
            r'(?:rs\.?|₹)?\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+\s?(?:lakh|lakhs|crore)',
            text.lower()
        )
        if amount_matches:
            self.extracted_info["amount"] = amount_matches[0]
            self.sources[amount_matches[0]] = timestamp
        
        # Extract relationship claims
        relationship_patterns = [
            r'(?:i am your|i\'m your)\s+(friend|brother|cousin|classmate|colleague)',
            r'(?:we are|we\'re)\s+(friends|classmates|colleagues)',
            r'(?:from|remember)\s+(college|school|work|office)',
            r'(?:we met at|we studied at)\s+([a-zA-Z\s]+)'
        ]
        for pattern in relationship_patterns:
            match = re.search(pattern, text.lower())
            if match:
                self.extracted_info['relationship'] = match.group(1)
                self.sources[match.group(1)] = timestamp
        
        # Hospital/organization names (simple single/double word responses)
        if len(text.split()) <= 2 and text[0].isupper() and not any(word in text.lower() for word in ['yes', 'no', 'ok', 'hello']):
            self.extracted_info.setdefault("hospital", text.title())
            self.sources[text.title()] = timestamp
        
        # UPI ID patterns
        upi_patterns = [
            r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\b',  # email-like UPI
            r'\b\d{10}@[a-zA-Z]+\b',  # phone@provider
        ]
        for pattern in upi_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                self.upi_ids.add(match.lower())
                self.sources[match.lower()] = timestamp
        
        # Phone numbers
        phone_matches = re.findall(r'\b(?:\+91[-\s]?)?\d{10}\b', text)
        for phone in phone_matches:
            clean_phone = re.sub(r'[-\s+]', '', phone)
            if len(clean_phone) >= 10:
                self.phones.add(clean_phone)
                self.sources[clean_phone] = timestamp
        
        # URLs and links
        url_matches = re.findall(r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*', text)
        for url in url_matches:
            self.links.add(url)
            self.sources[url] = timestamp
        
        # Bank account patterns (IFSC + account)
        ifsc_matches = re.findall(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', text.upper())
        account_matches = re.findall(r'\b\d{9,18}\b', text)
        
        for ifsc in ifsc_matches:
            self.bank_accounts.add(f"IFSC:{ifsc}")
            self.sources[f"IFSC:{ifsc}"] = timestamp
            
        for account in account_matches:
            if len(account) >= 9:  # Valid account length
                self.bank_accounts.add(f"ACC:{account}")
                self.sources[f"ACC:{account}"] = timestamp
        
        # Suspicious keywords
        suspicious_words = [
            'urgent', 'immediately', 'blocked', 'freeze', 'arrest', 'legal action',
            'rbi', 'police', 'government', 'officer', 'employee', 'department',
            'otp', 'password', 'pin', 'cvv', 'expire', 'verify', 'update',
            'click', 'link', 'download', 'install', 'remote', 'access'
        ]
        
        text_lower = text.lower()
        for word in suspicious_words:
            if re.search(rf'\b{re.escape(word)}\b', text_lower):
                self.suspicious_keywords[word] += 1
    
    def has_valuable_data(self):
        """Check if we've collected valuable intelligence"""
        return (len(self.upi_ids) > 0 or 
                len(self.phones) > 0 or 
                len(self.links) > 0 or 
                len(self.bank_accounts) > 0)
    
    def to_dict(self):
        """Convert to clean output format"""
        return {
            "upiIds": list(self.upi_ids),
            "phoneNumbers": list(self.phones),
            "phishingLinks": list(self.links),
            "bankAccounts": list(self.bank_accounts),
            "suspiciousKeywords": dict(self.suspicious_keywords.most_common(10))
        }
    
    def get_notes(self):
        """Generate analysis notes"""
        notes = []
        
        if self.suspicious_keywords.get('urgent', 0) > 2:
            notes.append("High urgency pressure")
        
        if any(word in self.suspicious_keywords for word in ['rbi', 'police', 'government']):
            notes.append("Authority impersonation")
            
        if any(word in self.suspicious_keywords for word in ['otp', 'password', 'pin']):
            notes.append("Credential harvesting attempt")
            
        if self.links:
            notes.append("Phishing links detected")
            
        if self.upi_ids or self.bank_accounts:
            notes.append("Payment fraud attempt")
        
        return " + ".join(notes) if notes else "Social engineering attempt"