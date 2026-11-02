import random
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List


def verify_luhn(card_number: str) -> bool:
    """
    Verifies if a credit card number passes the Luhn (Mod 10) algorithm.
    """
    clean = "".join(filter(str.isdigit, str(card_number)))
    if not clean or len(clean) < 2:
        return False

    digits = [int(d) for d in clean]
    checksum = 0
    reverse_digits = digits[::-1]

    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += (doubled - 9) if doubled > 9 else doubled
        else:
            checksum += digit

    return checksum % 10 == 0


def _generate_luhn_card_number(prefix: str, length: int = 16) -> str:
    """
    Generates a synthetically valid card number with the given prefix and total length.
    Computes the final check digit to strictly satisfy the Luhn algorithm.
    """
    # Generate length - 1 digits
    needed_random = length - len(prefix) - 1
    random_part = "".join(str(random.randint(0, 9)) for _ in range(needed_random))
    base = prefix + random_part

    # Calculate Luhn check digit
    digits = [int(d) for d in base]
    checksum = 0
    # In base (which lacks the last digit), when appended with check digit,
    # the check digit is at index 0 in reversed list (i % 2 == 0),
    # so base[-1] will be at index 1 in reversed list (doubled).
    for i, digit in enumerate(digits[::-1]):
        if i % 2 == 0:
            doubled = digit * 2
            checksum += (doubled - 9) if doubled > 9 else doubled
        else:
            checksum += digit

    check_digit = (10 - (checksum % 10)) % 10
    return base + str(check_digit)


class HoneyTokenRegistry:
    """
    Registry for managing and tracking deceptive honey-tokens (cards, UPIs, canary URLs).
    Synchronizes with SQLite database when available while maintaining in-memory cache.
    """
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(
        cls,
        token_id: str,
        token_type: str,
        decoy_value: str,
        session_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        record = {
            "tokenId": token_id,
            "sessionId": session_id,
            "tokenType": token_type,
            "decoyValue": decoy_value,
            "tripped": False,
            "trippedAt": None,
            "clientIp": None,
            "userAgent": None,
            "extraData": extra_data or {},
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        cls._cache[token_id] = record

        # Persist to SQLite if DB is available
        try:
            from app.database.connection import SessionLocal
            from app.database.models import CanaryTokenModel
            with SessionLocal() as db:
                db_token = CanaryTokenModel(
                    token_id=token_id,
                    session_id=session_id,
                    token_type=token_type,
                    decoy_value=decoy_value,
                    extra_data=extra_data or {}
                )
                db.add(db_token)
                db.commit()
        except Exception:
            pass

        return record

    @classmethod
    def get(cls, token_id: str) -> Optional[Dict[str, Any]]:
        if token_id in cls._cache:
            return cls._cache[token_id]

        try:
            from app.database.connection import SessionLocal
            from app.database.models import CanaryTokenModel
            with SessionLocal() as db:
                db_token = db.query(CanaryTokenModel).filter(CanaryTokenModel.token_id == token_id).first()
                if db_token:
                    record = db_token.to_dict()
                    cls._cache[token_id] = record
                    return record
        except Exception:
            pass

        return None

    @classmethod
    def trip_token(
        cls,
        token_id: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Marks a canary token as tripped (scammer interacted with it).
        Logs scammer IP, User-Agent, and timestamp.
        """
        record = cls.get(token_id)
        if not record:
            return None

        now_str = datetime.now(timezone.utc).isoformat()
        record["tripped"] = True
        record["trippedAt"] = now_str
        record["clientIp"] = client_ip
        record["userAgent"] = user_agent
        if extra_data:
            record["extraData"].update(extra_data)

        cls._cache[token_id] = record

        try:
            from app.database.connection import SessionLocal
            from app.database.models import CanaryTokenModel
            with SessionLocal() as db:
                db_token = db.query(CanaryTokenModel).filter(CanaryTokenModel.token_id == token_id).first()
                if db_token:
                    db_token.tripped = True
                    db_token.tripped_at = datetime.now(timezone.utc)
                    db_token.client_ip = client_ip
                    db_token.user_agent = user_agent
                    curr_extra = db_token.extra_data or {}
                    if extra_data:
                        curr_extra.update(extra_data)
                    db_token.extra_data = curr_extra
                    db.commit()
        except Exception:
            pass

        return record

    @classmethod
    def list_tokens(cls, session_id: Optional[str] = None, tripped_only: bool = False) -> List[Dict[str, Any]]:
        tokens = list(cls._cache.values())
        if session_id:
            tokens = [t for t in tokens if t.get("sessionId") == session_id]
        if tripped_only:
            tokens = [t for t in tokens if t.get("tripped")]
        return tokens


def generate_canary_card(
    issuer: str = "visa",
    session_id: Optional[str] = None,
    cardholder_name: str = "RAMESH KUMAR"
) -> Dict[str, Any]:
    """
    Generates a realistic canary credit/debit card with valid Luhn checksum.
    Uses standard test BIN prefixes.
    """
    prefixes = {
        "visa": "400000",
        "mastercard": "510000",
        "rupay": "604000"
    }
    issuer_clean = issuer.lower()
    prefix = prefixes.get(issuer_clean, "400000")

    card_number = _generate_luhn_card_number(prefix, 16)
    token_id = f"canary_card_{uuid.uuid4().hex[:10]}"

    expiry_month = f"{random.randint(1, 12):02d}"
    expiry_year = f"{random.randint(28, 32)}"
    cvv = f"{random.randint(100, 999)}"

    card_data = {
        "cardNumber": card_number,
        "issuer": issuer.upper(),
        "expiry": f"{expiry_month}/{expiry_year}",
        "cvv": cvv,
        "cardholderName": cardholder_name,
        "isValidLuhn": verify_luhn(card_number)
    }

    HoneyTokenRegistry.register(
        token_id=token_id,
        token_type="card",
        decoy_value=card_number,
        session_id=session_id,
        extra_data=card_data
    )

    return {
        "tokenId": token_id,
        **card_data
    }


def generate_decoy_upi(
    session_id: Optional[str] = None,
    bank: str = "okaxis",
    persona_name: str = "ramesh.kumar"
) -> Dict[str, Any]:
    """
    Generates a realistic decoy UPI VPA for counter-interrogation deception.
    """
    suffix = bank.lower().strip("@")
    tag = uuid.uuid4().hex[:6]
    clean_name = persona_name.lower().replace(" ", ".")
    vpa = f"{clean_name}.{tag}@{suffix}"
    token_id = f"canary_upi_{uuid.uuid4().hex[:10]}"

    HoneyTokenRegistry.register(
        token_id=token_id,
        token_type="upi",
        decoy_value=vpa,
        session_id=session_id,
        extra_data={"vpa": vpa, "bank": suffix}
    )

    return {
        "tokenId": token_id,
        "vpa": vpa,
        "bank": suffix
    }


def generate_canary_url(
    session_id: Optional[str] = None,
    base_url: str = "http://localhost:8000"
) -> Dict[str, Any]:
    """
    Generates a unique canary tracking URL that traps the scammer upon HTTP request.
    """
    token_id = f"ct_{uuid.uuid4().hex[:12]}"
    clean_base = base_url.rstrip("/")
    canary_url = f"{clean_base}/canary/{token_id}"

    HoneyTokenRegistry.register(
        token_id=token_id,
        token_type="url",
        decoy_value=canary_url,
        session_id=session_id,
        extra_data={"url": canary_url}
    )

    return {
        "tokenId": token_id,
        "url": canary_url
    }
