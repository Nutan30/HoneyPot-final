# llm_fallback.py

import os
import json

def llm_classify(message: str):
    """
    Optional LLM-based scam classifier.
    Must return: scamDetected, confidence, reason
    """

    # ---- MOCK FALLBACK (SAFE DEFAULT) ----
    if not os.getenv("OPENAI_API_KEY"):
        lowered = message.lower()
        if "upi" in lowered or "account" in lowered or "verify" in lowered:
            return {
                "scamDetected": True,
                "confidence": 0.85,
                "reason": "Financial credential request with urgency"
            }
        return {
            "scamDetected": False,
            "confidence": 0.2,
            "reason": "No strong scam indicators"
        }

    # ---- REAL LLM (ONLY IF KEY EXISTS) ----
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
You are a fraud detection system.

Classify the message as scam or not_scam.

Message:
\"{message}\"

Return ONLY valid JSON:
{{
  "scamDetected": true/false,
  "confidence": number between 0 and 1,
  "reason": "short explanation"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return json.loads(response.choices[0].message.content)
