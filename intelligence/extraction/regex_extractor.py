import re
from typing import List, Set

# Known Indian UPI Payment Service Provider (PSP) handles
VALID_UPI_SUFFIXES = {
    "okhdfcbank", "okaxis", "oksbi", "okicici",
    "ybl", "paytm", "upi", "apl", "axl",
    "ibl", "sbi", "pnb", "boi", "cnrb",
    "cbin", "unionbank", "indianbank", "kotak",
    "idbi", "rbl", "federal", "indus", "icici",
    "axisbank", "hdfcbank", "freecharge", "airtel",
    "jio", "waaxis", "wahdfcbank", "wasbi",
    "abfspay", "ikwik", "jupiteraxis", "slice",
    "barodampay", "allbank", "syndicate", "dbs"
}

# Regex Patterns
_PHONE_PATTERN = re.compile(r"(?:\+91[\s-]?)?(?:0)?[6-9]\d{4}[\s-]?\d{5}\b")
_UPI_PATTERN = re.compile(r"\b[\w.-]+@[\w.-]+\b")
_URL_PATTERN = re.compile(r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?|https?://\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?(?:/[^\s]*)?|\b(?:bit\.ly|tinyurl\.com|t\.co|is\.gd|cutt\.ly)/[a-zA-Z0-9_+-]+", re.IGNORECASE)
_IFSC_PATTERN = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")
_BANK_ACC_PATTERN = re.compile(r"(?:a/c|acct|account|acc(?:\.|\s+no\.?)?)\s*(?:no\.?|num(?:ber)?)?\s*[:\-]?\s*(\d{9,18})\b", re.IGNORECASE)
_GENERIC_ACC_PATTERN = re.compile(r"\b\d{11,16}\b")

# Crypto Address Patterns
_BTC_PATTERN = re.compile(r"\b(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})\b")
_ETH_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
_TRON_PATTERN = re.compile(r"\bT[a-zA-HJ-NP-Z1-9]{33}\b")


def extract_phone_numbers(messages: List[str]) -> List[str]:
    """
    Extracts Indian mobile numbers with optional country code (+91 / 0) and spacing.
    Returns cleaned 10-digit phone strings.
    """
    phones: Set[str] = set()

    for msg in messages:
        if not isinstance(msg, str):
            continue
        matches = _PHONE_PATTERN.findall(msg)
        for match in matches:
            # Strip +91, 0, whitespace, hyphens
            digits = re.sub(r"\D", "", match)
            if digits.startswith("91") and len(digits) == 12:
                digits = digits[2:]
            elif digits.startswith("0") and len(digits) == 11:
                digits = digits[1:]

            if len(digits) == 10 and digits[0] in "6789":
                phones.add(digits)

    return sorted(list(phones))


def extract_upi_ids(messages: List[str]) -> List[str]:
    """
    Extracts UPI Virtual Payment Addresses (VPAs).
    Validates suffix against authorized Indian PSP handles to eliminate standard email false positives.
    """
    upi_ids: Set[str] = set()

    for msg in messages:
        if not isinstance(msg, str):
            continue
        matches = _UPI_PATTERN.findall(msg)
        for match in matches:
            parts = match.split("@")
            if len(parts) == 2:
                suffix = parts[1].lower()
                if suffix in VALID_UPI_SUFFIXES:
                    upi_ids.add(match.lower())

    return sorted(list(upi_ids))


def extract_phishing_links(messages: List[str]) -> List[str]:
    """
    Extracts URLs, shortened links, and IP-based links used in phishing lures.
    """
    links: Set[str] = set()

    for msg in messages:
        if not isinstance(msg, str):
            continue
        matches = _URL_PATTERN.findall(msg)
        for match in matches:
            link = match.strip(".,;:)'\"")
            if not link.startswith("http"):
                link = f"https://{link}"
            links.add(link)

    return sorted(list(links))


def extract_ifsc_codes(messages: List[str]) -> List[str]:
    """
    Extracts Indian Financial System Code (IFSC) identifiers (e.g., SBIN0001234, HDFC0000456).
    """
    ifscs: Set[str] = set()

    for msg in messages:
        if not isinstance(msg, str):
            continue
        matches = _IFSC_PATTERN.findall(msg.upper())
        for match in matches:
            ifscs.add(match)

    return sorted(list(ifscs))


def extract_bank_accounts(messages: List[str]) -> List[str]:
    """
    Extracts bank account numbers with contextual proximity checks (a/c, account no).
    """
    accounts: Set[str] = set()

    for msg in messages:
        if not isinstance(msg, str):
            continue
        # Contextual matches
        context_matches = _BANK_ACC_PATTERN.findall(msg)
        for match in context_matches:
            if len(match) >= 9 and len(match) <= 18:
                accounts.add(match)

        # Standalone account numbers (11-16 digits)
        standalone = _GENERIC_ACC_PATTERN.findall(msg)
        for match in standalone:
            # Avoid picking up 10-digit phones or timestamps
            if len(match) in (11, 12, 14, 15, 16):
                accounts.add(match)

    return sorted(list(accounts))


def extract_crypto_addresses(messages: List[str]) -> List[dict]:
    """
    Extracts cryptocurrency addresses (Bitcoin, Ethereum/ERC-20, Tron/USDT).
    """
    crypto: List[dict] = []
    seen = set()

    for msg in messages:
        if not isinstance(msg, str):
            continue

        for btc in _BTC_PATTERN.findall(msg):
            if btc not in seen:
                crypto.append({"network": "Bitcoin", "address": btc})
                seen.add(btc)

        for eth in _ETH_PATTERN.findall(msg):
            if eth not in seen:
                crypto.append({"network": "Ethereum", "address": eth})
                seen.add(eth)

        for trx in _TRON_PATTERN.findall(msg):
            if trx not in seen:
                crypto.append({"network": "Tron", "address": trx})
                seen.add(trx)

    return crypto
