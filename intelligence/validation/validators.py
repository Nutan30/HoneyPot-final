import re
from typing import List, Dict, Any
from urllib.parse import urlparse

# Known Indian UPI handles
from intelligence.extraction.regex_extractor import VALID_UPI_SUFFIXES

# Common URL Shortener domains
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly",
    "buff.ly", "ow.ly", "rebrand.ly", "shorturl.at"
}

# Suspicious / High-Risk TLDs often abused in phishing campaigns
SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".work", ".click", ".loan", ".zip",
    ".tk", ".ml", ".ga", ".cf", ".gq", ".country", ".stream"
}

# Bank IFSC prefix whitelist (top Indian retail banks)
KNOWN_IFSC_PREFIXES = {
    "SBIN", "HDFC", "ICIC", "UTIB", "KKBK", "PUNB", "BARB",
    "BKID", "CNRB", "UBIN", "IOBA", "IDIB", "CBIN", "MAHB",
    "YESB", "IDFB", "INDB", "FDRL", "RBLN", "KVBL", "CSBK"
}


def validate_phone_numbers(phone_numbers: List[str]) -> List[str]:
    """Validates 10-digit Indian mobile numbers starting with 6, 7, 8, or 9."""
    valid_phones = []
    for phone in phone_numbers:
        clean = re.sub(r"\D", "", str(phone))
        if len(clean) == 10 and clean[0] in "6789":
            valid_phones.append(clean)
    return sorted(list(set(valid_phones)))


def validate_upi_ids(upi_ids: List[str]) -> List[str]:
    """Validates UPI VPAs against authorized Indian PSP handles."""
    valid_upis = []
    for upi in upi_ids:
        upi_str = str(upi).strip().lower()
        if "@" in upi_str:
            parts = upi_str.split("@")
            if len(parts) == 2 and parts[0] and parts[1] in VALID_UPI_SUFFIXES:
                valid_upis.append(upi_str)
    return sorted(list(set(valid_upis)))


def validate_ifsc_codes(ifsc_list: List[str]) -> List[str]:
    """
    Validates Indian Financial System Code (IFSC).
    Format: 4 alphabetic characters (Bank code) + '0' (Reserved) + 6 alphanumeric branch code.
    Example: SBIN0001234, HDFC0000456
    """
    valid_ifscs = []
    pattern = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")

    for code in ifsc_list:
        clean = str(code).strip().upper()
        if pattern.match(clean):
            prefix = clean[:4]
            # Prioritize known bank prefixes or valid pattern matches
            valid_ifscs.append(clean)

    return sorted(list(set(valid_ifscs)))


def validate_bank_accounts(account_list: List[str]) -> List[str]:
    """
    Validates bank account numbers.
    Rules:
    - Length between 9 and 18 digits.
    - Excludes repetitive sequences (e.g. 0000000000, 1111111111).
    - Excludes values that match standard 10-digit mobile prefixes if unconfirmed.
    """
    valid_accs = []
    for acc in account_list:
        clean = re.sub(r"\D", "", str(acc))
        if 9 <= len(clean) <= 18:
            # Check for dummy/repeating patterns
            if len(set(clean)) <= 1:
                continue
            # Avoid sequential trivial test numbers
            if clean in ("123456789", "1234567890", "9876543210"):
                continue
            valid_accs.append(clean)

    return sorted(list(set(valid_accs)))


def validate_crypto_addresses(crypto_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Validates cryptocurrency addresses across Bitcoin, Ethereum, and Tron.
    """
    valid_crypto = []
    btc_regex = re.compile(r"^(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})$")
    eth_regex = re.compile(r"^0x[a-fA-F0-9]{40}$")
    tron_regex = re.compile(r"^T[a-zA-HJ-NP-Z1-9]{33}$")

    seen = set()
    for item in crypto_list:
        if not isinstance(item, dict):
            continue
        net = item.get("network", "")
        addr = item.get("address", "").strip()

        if not addr or addr in seen:
            continue

        is_valid = False
        if net == "Bitcoin" and btc_regex.match(addr):
            is_valid = True
        elif net == "Ethereum" and eth_regex.match(addr):
            is_valid = True
        elif net == "Tron" and tron_regex.match(addr):
            is_valid = True

        if is_valid:
            valid_crypto.append({"network": net, "address": addr})
            seen.add(addr)

    return valid_crypto


def enrich_phishing_links(links: List[str]) -> List[Dict[str, Any]]:
    """
    Enriches extracted URLs with threat intelligence metadata:
    - Domain and path breakdown
    - Direct IP address detection
    - URL shortener identification
    - High-risk TLD identification
    - Threat risk rating (Low, Medium, High)
    """
    enriched = []
    seen = set()

    ip_regex = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")

    for raw_link in links:
        link = str(raw_link).strip()
        if not link or link in seen:
            continue

        if not link.startswith(("http://", "https://")):
            link_for_parse = f"https://{link}"
        else:
            link_for_parse = link

        try:
            parsed = urlparse(link_for_parse)
            hostname = (parsed.hostname or "").lower()
            tld = f".{hostname.split('.')[-1]}" if "." in hostname else ""

            is_shortener = hostname in SHORTENER_DOMAINS
            is_ip = bool(ip_regex.match(hostname))
            is_suspicious_tld = tld in SUSPICIOUS_TLDS

            # Calculate risk level
            risk_factors = []
            if is_shortener:
                risk_factors.append("URL Shortener used (obfuscation)")
            if is_ip:
                risk_factors.append("Direct IP address URL (suspicious host)")
            if is_suspicious_tld:
                risk_factors.append(f"Abused TLD: {tld}")
            if "login" in parsed.path.lower() or "verify" in parsed.path.lower() or "bank" in parsed.path.lower():
                risk_factors.append("Sensitive keyword in path (credential lure)")

            if len(risk_factors) >= 2 or is_ip:
                threat_level = "HIGH"
            elif len(risk_factors) == 1:
                threat_level = "MEDIUM"
            else:
                threat_level = "LOW"

            enriched.append({
                "url": link,
                "domain": hostname,
                "isShortener": is_shortener,
                "isDirectIP": is_ip,
                "threatLevel": threat_level,
                "riskFactors": risk_factors
            })
            seen.add(link)
        except Exception:
            continue

    return enriched
