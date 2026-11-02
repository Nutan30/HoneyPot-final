# llm_fallback.py

import os
import json
import logging
from app.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)


def llm_classify(message: str) -> dict:
    """
    LLM-based scam classification using OpenAI with graceful heuristic fallback.
    Returns: {"scamDetected": bool, "confidence": float, "reason": str}
    """
    api_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

    # If OpenAI is configured, try live LLM classification
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            prompt = f"""You are a senior cybersecurity fraud detection expert.
Analyze the following incoming message and determine whether it represents a cyber fraud attempt (phishing, UPI scam, KYC threat, electricity cut, fake job, lottery, or extortion).

Message:
"{message}"

Return ONLY valid JSON matching this schema:
{{
  "scamDetected": true or false,
  "confidence": float between 0.0 and 1.0,
  "reason": "concise technical explanation"
}}
"""
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=6.0
            )

            result = json.loads(response.choices[0].message.content)
            return {
                "scamDetected": bool(result.get("scamDetected", False)),
                "confidence": float(result.get("confidence", 0.5)),
                "reason": str(result.get("reason", "Analyzed by OpenAI fraud model"))
            }

        except Exception as e:
            logger.warning(f"OpenAI scam classification fallback triggered due to: {e}")

    # Heuristic fallback if OpenAI is unavailable or offline
    lowered = message.lower()
    scam_keywords = ["upi", "account", "blocked", "verify", "kyc", "otp", "pin", "suspended", "urgent"]
    hits = [k for k in scam_keywords if k in lowered]

    if len(hits) >= 2:
        return {
            "scamDetected": True,
            "confidence": min(0.95, 0.5 + 0.15 * len(hits)),
            "reason": f"Heuristic detection: matched risk signals {hits}"
        }

    return {
        "scamDetected": False,
        "confidence": 0.2,
        "reason": "No strong scam indicators detected"
    }
