import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List


# Standard MITRE ATT&CK Matrix Techniques for Social Engineering & Financial Scams
MITRE_TECHNIQUES = {
    "spearphishing_link": {
        "id": "T1566.002",
        "name": "Phishing: Spearphishing Link",
        "description": "Adversary sends targeted deceptive links via chat or SMS to lure victim into credential harvesting or malware download."
    },
    "phishing_information": {
        "id": "T1598",
        "name": "Phishing for Information",
        "description": "Adversary elicits sensitive financial details, OTPs, or identity documentation through conversational deception."
    },
    "impersonation": {
        "id": "T1656",
        "name": "Impersonation",
        "description": "Adversary impersonates trusted authorities, law enforcement officers (CBI/police), or bank officials to gain compliance."
    },
    "user_execution": {
        "id": "T1204.001",
        "name": "User Execution: Malicious Link",
        "description": "Adversary relies on the user executing an action such as clicking on an external payment link or malicious APK."
    }
}


def _generate_stix_id(type_name: str) -> str:
    return f"{type_name}--{uuid.uuid4()}"


def _format_timestamp(dt: Any = None) -> str:
    if isinstance(dt, datetime):
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def export_session_to_stix(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms session intelligence and captured IOCs into an OASIS STIX 2.1 JSON bundle.
    Includes MITRE ATT&CK attack patterns, indicators, threat actor, and relationships.
    """
    session_id = session.get("sessionId", "unknown_session")
    intel = session.get("extractedIntelligence", {})

    # Handle nested extractedIntelligence if wrapped
    if "extractedIntelligence" in intel and isinstance(intel["extractedIntelligence"], dict):
        intel = intel["extractedIntelligence"]

    now_iso = _format_timestamp()
    bundle_id = _generate_stix_id("bundle")

    objects: List[Dict[str, Any]] = []

    # 1. Identity SDO (The Honeypot System)
    identity_id = _generate_stix_id("identity")
    identity_obj = {
        "type": "identity",
        "spec_version": "2.1",
        "id": identity_id,
        "created": now_iso,
        "modified": now_iso,
        "name": "Autonomous Agentic AI Honeypot Defense",
        "description": "Automated cyber deception system capturing social engineering tactics and financial mule indicators.",
        "identity_class": "system"
    }
    objects.append(identity_obj)

    # 2. Threat Actor SDO (The Scammer)
    threat_actor_id = _generate_stix_id("threat-actor")
    scam_type = session.get("scamClassification") or "Financial Social Engineering"
    notes = session.get("agentNotes") or "Scammer engaged via automated honeypot victim persona."

    threat_actor_obj = {
        "type": "threat-actor",
        "spec_version": "2.1",
        "id": threat_actor_id,
        "created": now_iso,
        "modified": now_iso,
        "name": f"Adversary-{session_id[:10]}",
        "threat_actor_types": ["crime-syndicate", "financial-crime"],
        "description": f"Scam Classification: {scam_type}. {notes}",
        "confidence": int((session.get("confidence") or 0.8) * 100),
        "created_by_ref": identity_id
    }
    objects.append(threat_actor_obj)

    # 3. MITRE ATT&CK Attack Patterns
    attack_pattern_ids = []
    # Determine applicable techniques based on session features
    active_tactics = ["phishing_information", "impersonation"]
    if intel.get("phishingLinks"):
        active_tactics.extend(["spearphishing_link", "user_execution"])

    for tactic_key in active_tactics:
        meta = MITRE_TECHNIQUES[tactic_key]
        ap_id = _generate_stix_id("attack-pattern")
        ap_obj = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": ap_id,
            "created": now_iso,
            "modified": now_iso,
            "name": meta["name"],
            "description": meta["description"],
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": meta["id"],
                    "url": f"https://attack.mitre.org/techniques/{meta['id'].replace('.', '/')}/"
                }
            ],
            "created_by_ref": identity_id
        }
        objects.append(ap_obj)
        attack_pattern_ids.append(ap_id)

        # Relationship: Threat Actor -> uses -> Attack Pattern
        objects.append({
            "type": "relationship",
            "spec_version": "2.1",
            "id": _generate_stix_id("relationship"),
            "created": now_iso,
            "modified": now_iso,
            "relationship_type": "uses",
            "source_ref": threat_actor_id,
            "target_ref": ap_id,
            "created_by_ref": identity_id
        })

    # 4. Indicators (STIX patterns for captured IOCs)
    indicator_ids = []

    # Phones
    for phone in intel.get("phoneNumbers", []):
        ind_id = _generate_stix_id("indicator")
        ind_obj = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": ind_id,
            "created": now_iso,
            "modified": now_iso,
            "name": f"Scammer Phone: {phone}",
            "pattern": f"[telephone-number:value = '{phone}']",
            "pattern_type": "stix",
            "valid_from": now_iso,
            "indicator_types": ["malicious-activity"],
            "created_by_ref": identity_id
        }
        objects.append(ind_obj)
        indicator_ids.append(ind_id)

    # UPI IDs
    for upi in intel.get("upiIds", []):
        ind_id = _generate_stix_id("indicator")
        ind_obj = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": ind_id,
            "created": now_iso,
            "modified": now_iso,
            "name": f"Mule UPI VPA: {upi}",
            "pattern": f"[user-account:account_login = '{upi}']",
            "pattern_type": "stix",
            "valid_from": now_iso,
            "indicator_types": ["malicious-activity"],
            "created_by_ref": identity_id
        }
        objects.append(ind_obj)
        indicator_ids.append(ind_id)

    # Phishing Links
    for link in intel.get("phishingLinks", []):
        ind_id = _generate_stix_id("indicator")
        ind_obj = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": ind_id,
            "created": now_iso,
            "modified": now_iso,
            "name": f"Phishing URL: {link}",
            "pattern": f"[url:value = '{link}']",
            "pattern_type": "stix",
            "valid_from": now_iso,
            "indicator_types": ["malicious-activity"],
            "created_by_ref": identity_id
        }
        objects.append(ind_obj)
        indicator_ids.append(ind_id)

    # Bank Accounts
    for acc in intel.get("bankAccounts", []):
        ind_id = _generate_stix_id("indicator")
        ind_obj = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": ind_id,
            "created": now_iso,
            "modified": now_iso,
            "name": f"Mule Bank Account: {acc}",
            "pattern": f"[financial-account:account_number = '{acc}']",
            "pattern_type": "stix",
            "valid_from": now_iso,
            "indicator_types": ["malicious-activity"],
            "created_by_ref": identity_id
        }
        objects.append(ind_obj)
        indicator_ids.append(ind_id)

    # Crypto Addresses
    for crypto in intel.get("cryptoAddresses", []):
        addr = crypto.get("address") if isinstance(crypto, dict) else str(crypto)
        net = crypto.get("network", "Crypto") if isinstance(crypto, dict) else "Crypto"
        ind_id = _generate_stix_id("indicator")
        ind_obj = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": ind_id,
            "created": now_iso,
            "modified": now_iso,
            "name": f"Ransom/Scam Crypto Wallet ({net}): {addr}",
            "pattern": f"[crypto-wallet:address = '{addr}']",
            "pattern_type": "stix",
            "valid_from": now_iso,
            "indicator_types": ["malicious-activity"],
            "created_by_ref": identity_id
        }
        objects.append(ind_obj)
        indicator_ids.append(ind_id)

    # Relationships: Threat Actor -> indicates -> Indicators
    for ind_id in indicator_ids:
        objects.append({
            "type": "relationship",
            "spec_version": "2.1",
            "id": _generate_stix_id("relationship"),
            "created": now_iso,
            "modified": now_iso,
            "relationship_type": "indicates",
            "source_ref": ind_id,
            "target_ref": threat_actor_id,
            "created_by_ref": identity_id
        })

    return {
        "type": "bundle",
        "id": bundle_id,
        "spec_version": "2.1",
        "objects": objects
    }
