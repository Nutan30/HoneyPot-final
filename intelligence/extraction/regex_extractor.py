import re


def extract_phone_numbers(messages):
    phone_pattern = r"\b[6-9]\d{9}\b"
    phones = set()

    for msg in messages:
        matches = re.findall(phone_pattern, msg)
        phones.update(matches)

    return list(phones)


def extract_upi_ids(messages):
    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    upi_ids = set()

    for msg in messages:
        matches = re.findall(upi_pattern, msg)
        upi_ids.update(matches)

    return list(upi_ids)

def extract_phishing_links(messages):
    import re
    link_pattern = r"https?://[^\s]+"
    links = set()

    for msg in messages:
        matches = re.findall(link_pattern, msg)
        links.update(matches)

    return list(links)

