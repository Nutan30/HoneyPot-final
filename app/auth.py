import secrets
from fastapi import Header, HTTPException
from app.config import API_KEY


def verify_api_key(x_api_key: str = Header(...)):
    """
    Validate the API key using constant-time comparison
    to prevent timing side-channel attacks.
    """
    if not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="Unauthorized")
