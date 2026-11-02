import re

# Known UPI PSP suffixes in India
VALID_UPI_SUFFIXES = {
    "okhdfcbank", "okaxis", "oksbi", "okicici",
    "ybl", "paytm", "upi", "apl", "axl",
    "ibl", "sbi", "pnb", "boi", "cnrb",
    "cbin", "unionbank", "indianbank", "kotak",
    "idbi", "rbl", "federal", "indus", "icici",
    "axisbank", "hdfcbank", "freecharge", "airtel",
    "jio", "waaxis", "wahdfcbank", "wasbi",
    "abfspay", "ikwik", "jupiteraxis", "slice",
}


def extract_phone_numbers(messages):
    # Indian mobile numbers: 10 digits starting with 6-9
    phone_pattern = r"\b[6-9]\d{9}\b"
    phones = set()

    for msg in messages:
        matches = re.findall(phone_pattern, msg)
        phones.update(matches)

    return list(phones)


def extract_upi_ids(messages):
    """
    Extract UPI Virtual Payment Addresses (VPAs).
    Validates against known PSP suffixes to avoid matching regular email addresses.
    """
    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    upi_ids = set()

    for msg in messages:
        matches = re.findall(upi_pattern, msg)
        for match in matches:
            parts = match.split("@")
            if len(parts) == 2:
                suffix = parts[1].lower()
                # Only accept known UPI payment service provider handles
                if suffix in VALID_UPI_SUFFIXES:
                    upi_ids.add(match.lower())

    return list(upi_ids)


def extract_phishing_links(messages):
    link_pattern = r"https?://[^\s]+"
    links = set()

    for msg in messages:
        matches = re.findall(link_pattern, msg)
        links.update(matches)

    return list(links)
