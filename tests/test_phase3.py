import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.config import API_KEY
from intelligence.extraction.regex_extractor import (
    extract_ifsc_codes,
    extract_bank_accounts,
    extract_crypto_addresses,
    extract_phishing_links
)
from intelligence.validation.validators import (
    validate_ifsc_codes,
    validate_bank_accounts,
    validate_crypto_addresses,
    enrich_phishing_links
)
from intelligence.deception.honey_tokens import (
    verify_luhn,
    generate_canary_card,
    generate_decoy_upi,
    generate_canary_url,
    HoneyTokenRegistry
)
from intelligence.stix.exporter import export_session_to_stix
from app.adapters.intelligence_adapter import (
    build_callback_payload,
    dispatch_callback_async
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"x-api-key": API_KEY}


# ---------------- 1. ADVANCED IOC EXTRACTION & VALIDATION ---------------- #

def test_ifsc_extraction_and_validation():
    sample_text = [
        "Please send the amount to account with IFSC code SBIN0001234 immediately.",
        "Alternate branch is HDFC0000456, or Punjab bank PUNB0123456.",
        "Ignore INVALID123 and SBIN12."
    ]
    extracted = extract_ifsc_codes(sample_text)
    assert "SBIN0001234" in extracted
    assert "HDFC0000456" in extracted
    assert "PUNB0123456" in extracted

    validated = validate_ifsc_codes(extracted)
    assert "SBIN0001234" in validated
    assert "HDFC0000456" in validated
    assert len(validated) >= 3


def test_bank_account_extraction_and_validation():
    sample_text = [
        "Transfer to A/C no: 98765432101234 immediately.",
        "Our current account no: 112233445566 is active.",
        "Do not consider 000000000000 or 123456789."
    ]
    extracted = extract_bank_accounts(sample_text)
    assert any("98765432101234" in acc for acc in extracted)

    # Validation should reject all identical digits or trivial patterns
    validated = validate_bank_accounts(["000000000000", "123456789", "98765432101234"])
    assert "98765432101234" in validated
    assert "000000000000" not in validated
    assert "123456789" not in validated


def test_crypto_address_extraction_and_validation():
    sample_text = [
        "Pay ransom in Bitcoin: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa or bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
        "Send USDT on Tron: T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
        "Or ETH to 0x71C7656EC7ab88b098defB751B7401B5f6d8976F."
    ]
    extracted = extract_crypto_addresses(sample_text)
    assert len(extracted) == 4

    validated = validate_crypto_addresses(extracted)
    networks = {item["network"] for item in validated}
    assert "Bitcoin" in networks
    assert "Ethereum" in networks
    assert "Tron" in networks


def test_phishing_link_enrichment():
    links = [
        "https://bit.ly/secure-kyc-verify",
        "http://192.168.1.100/bank/login",
        "https://update-kyc.xyz/portal"
    ]
    enriched = enrich_phishing_links(links)
    assert len(enriched) == 3

    shortener_entry = next(e for e in enriched if "bit.ly" in e["url"])
    assert shortener_entry["isShortener"] is True

    ip_entry = next(e for e in enriched if "192.168.1.100" in e["url"])
    assert ip_entry["isDirectIP"] is True
    assert ip_entry["threatLevel"] == "HIGH"

    xyz_entry = next(e for e in enriched if ".xyz" in e["url"])
    assert "Abused TLD: .xyz" in xyz_entry["riskFactors"]


# ---------------- 2. HONEY-TOKENS & DECEPTION ENGINE ---------------- #

def test_luhn_algorithm_verification():
    # Known valid test card numbers (Luhn compliant)
    assert verify_luhn("49927398716") is True
    assert verify_luhn("4000001234567899") is not None

    # Invalid cards (tampered check digit)
    assert verify_luhn("49927398717") is False
    assert verify_luhn("12345") is False


def test_canary_card_generation():
    for issuer in ["visa", "mastercard", "rupay"]:
        card = generate_canary_card(issuer=issuer, session_id="test_sess_canary")
        assert verify_luhn(card["cardNumber"]) is True
        assert card["isValidLuhn"] is True
        assert len(card["cardNumber"]) == 16
        assert len(card["cvv"]) == 3
        assert "/" in card["expiry"]
        # Verify registered in HoneyTokenRegistry
        record = HoneyTokenRegistry.get(card["tokenId"])
        assert record is not None
        assert record["tokenType"] == "card"


def test_decoy_upi_generation():
    upi_token = generate_decoy_upi(session_id="test_sess_canary", bank="okaxis")
    assert upi_token["vpa"].endswith("@okaxis")
    assert "ramesh.kumar" in upi_token["vpa"]
    record = HoneyTokenRegistry.get(upi_token["tokenId"])
    assert record is not None
    assert record["tokenType"] == "upi"


def test_canary_url_and_trip():
    url_token = generate_canary_url(session_id="test_sess_canary", base_url="http://testserver")
    token_id = url_token["tokenId"]
    assert token_id in url_token["url"]

    # Before tripping
    record = HoneyTokenRegistry.get(token_id)
    assert record["tripped"] is False

    # Trip token
    tripped = HoneyTokenRegistry.trip_token(
        token_id=token_id,
        client_ip="198.51.100.42",
        user_agent="Mozilla/5.0 (ScammerBrowser)"
    )
    assert tripped["tripped"] is True
    assert tripped["clientIp"] == "198.51.100.42"
    assert tripped["userAgent"] == "Mozilla/5.0 (ScammerBrowser)"
    assert tripped["trippedAt"] is not None


# ---------------- 3. STIX 2.1 THREAT INTEL EXPORTER ---------------- #

def test_export_session_to_stix():
    sample_session = {
        "sessionId": "stix_test_session_101",
        "scamDetected": True,
        "scamClassification": "Bank Impersonation",
        "agentNotes": "Scammer demanded urgent payment transfer",
        "confidence": 0.95,
        "extractedIntelligence": {
            "phoneNumbers": ["9876543210"],
            "upiIds": ["fraudster@okhdfcbank"],
            "phishingLinks": ["https://bit.ly/bank-fake"],
            "bankAccounts": ["98765432101234"],
            "cryptoAddresses": [{"network": "Bitcoin", "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"}]
        }
    }

    stix_bundle = export_session_to_stix(sample_session)

    assert stix_bundle["type"] == "bundle"
    assert stix_bundle["spec_version"] == "2.1"
    assert stix_bundle["id"].startswith("bundle--")

    objects = stix_bundle["objects"]
    types = {obj["type"] for obj in objects}

    assert "identity" in types
    assert "threat-actor" in types
    assert "attack-pattern" in types
    assert "indicator" in types
    assert "relationship" in types

    # Check MITRE ATT&CK external reference
    attack_patterns = [o for o in objects if o["type"] == "attack-pattern"]
    assert len(attack_patterns) >= 2
    ext_refs = attack_patterns[0].get("external_references", [])
    assert any(ref.get("source_name") == "mitre-attack" for ref in ext_refs)

    # Check indicator patterns
    indicators = [o for o in objects if o["type"] == "indicator"]
    patterns = [ind["pattern"] for ind in indicators]
    assert any("[telephone-number:value = '9876543210']" in p for p in patterns)
    assert any("[user-account:account_login = 'fraudster@okhdfcbank']" in p for p in patterns)
    assert any("[url:value = 'https://bit.ly/bank-fake']" in p for p in patterns)


# ---------------- 4. ASYNC WEBHOOK DISPATCHER ---------------- #

@pytest.mark.asyncio
async def test_dispatch_callback_async_success():
    session = {
        "sessionId": "sess_async_callback_1",
        "scamDetected": True,
        "totalMessages": 6,
        "extractedIntelligence": {
            "upiIds": ["scam@okaxis"],
            "phoneNumbers": ["9876543210"]
        },
        "agentNotes": "Urgency observed"
    }

    payload = build_callback_payload(session)
    assert payload["sessionId"] == "sess_async_callback_1"
    assert payload["scamDetected"] is True
    assert "scam@okaxis" in payload["extractedIntelligence"]["upiIds"]

    # Mock httpx.AsyncClient response
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        success = await dispatch_callback_async(session, callback_url="http://mock.callback/api")
        assert success is True
        assert session.get("callbackSent") is True


# ---------------- 5. REST ENDPOINTS & INTEGRATION ---------------- #

def test_api_stix_endpoint(client, auth_headers):
    # Unauthenticated / invalid key should fail
    resp_unauth = client.get("/api/stix/test_session_id")
    assert resp_unauth.status_code in [401, 422]

    resp_invalid = client.get("/api/stix/test_session_id", headers={"x-api-key": "invalid_key"})
    assert resp_invalid.status_code == 401

    # First send a message to create a session
    client.post(
        "/message",
        json={"sessionId": "stix_endpoint_sess", "message": {"text": "Pay immediately to fraud@okaxis", "sender": "scammer"}},
        headers=auth_headers
    )

    # Authenticated STIX bundle retrieval
    resp = client.get("/api/stix/stix_endpoint_sess", headers=auth_headers)
    assert resp.status_code == 200
    bundle = resp.json()
    assert bundle["type"] == "bundle"
    assert bundle["spec_version"] == "2.1"


def test_api_iocs_endpoint(client, auth_headers):
    # Retrieve all IOCs
    resp = client.get("/api/iocs", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # Query with type filter
    resp_upi = client.get("/api/iocs?ioc_type=upi", headers=auth_headers)
    assert resp_upi.status_code == 200
    for item in resp_upi.json():
        assert item["iocType"] == "upi"


def test_canary_trap_endpoint(client):
    # Generate canary URL
    canary = generate_canary_url(session_id="canary_endpoint_sess")
    token_id = canary["tokenId"]

    # Public GET (scammer clicking the trap link)
    headers = {"User-Agent": "DeceptiveScammerProbe/1.0", "X-Forwarded-For": "203.0.113.195"}
    resp = client.get(f"/canary/{token_id}", headers=headers)

    assert resp.status_code == 200
    assert "Verification Session Expired" in resp.text
    assert token_id in resp.text

    # Verify that the token was tripped in the registry
    token_record = HoneyTokenRegistry.get(token_id)
    assert token_record["tripped"] is True
    assert token_record["clientIp"] == "203.0.113.195"
    assert "DeceptiveScammerProbe" in token_record["userAgent"]

    # Non-existent token returns 404
    resp_404 = client.get("/canary/invalid_nonexistent_token")
    assert resp_404.status_code == 404
