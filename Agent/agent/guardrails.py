import re
from typing import Tuple, Optional, Dict, Any

# Common adversarial prompt injection and jailbreak patterns
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|directives)",
    r"disregard\s+(all\s+)?(previous|prior)\s+(instructions|rules)",
    r"(system\s+prompt|system\s+instructions|base\s+instructions)",
    r"(reveal|print|output|repeat|show)\s+(your\s+)?(system\s+prompt|instructions|initial\s+prompt)",
    r"you\s+are\s+now\s+in\s+(developer|dan|jailbreak|unrestricted)\s+mode",
    r"act\s+as\s+(an?\s+)?(unrestricted|evil|jailbroken|helpful)\s+ai",
    r"(bypass|disable|override)\s+(safety|content|security)\s+(filters|guidelines)",
    r"<script[\s\S]*?>[\s\S]*?<\/script>",
    r"base64\s*:\s*[A-Za-z0-9+/=]{16,}",
    r"\{\{[\s\S]*?\}\}",  # Template injection attempts
]

_COMPILED_INJECTIONS = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

# Forbidden leakage patterns that must never appear in agent responses
_LEAKAGE_PATTERNS = [
    r"i\s+am\s+(an?\s+)?(ai|artificial\s+intelligence|language\s+model|honeypot|agent)",
    r"as\s+an\s+ai\s+language\s+model",
    r"honeypot\s+(system|defense|framework)",
    r"i\s+cannot\s+break\s+character",
    r"my\s+instructions\s+are\s+to",
    r"system\s*:",
    r"sk-[a-zA-Z0-9]{20,}",  # Potential API key leakage
]

_COMPILED_LEAKAGE = [re.compile(p, re.IGNORECASE) for p in _LEAKAGE_PATTERNS]


def is_prompt_injection(text: str) -> Tuple[bool, Optional[str]]:
    """
    Scans incoming text for prompt injection, jailbreaking, or instruction override attempts.
    Returns (True, pattern_name) if detected, (False, None) otherwise.
    """
    if not text:
        return False, None

    for pattern in _COMPILED_INJECTIONS:
        if pattern.search(text):
            return True, pattern.pattern

    return False, None


def sanitize_agent_output(text: str, fallback_reply: str = "Sorry, I am getting confused. What should I do next?") -> str:
    """
    Sanitizes agent reply to guarantee no honeypot identity, API secrets,
    or system prompt traces leak to the scammer.
    """
    if not text:
        return fallback_reply

    cleaned = text.strip()

    # Check for forbidden persona-breaking phrases
    for pattern in _COMPILED_LEAKAGE:
        if pattern.search(cleaned):
            return "Sir, I didn't understand that technical message. Please explain in simple words what I need to do for my account."

    # Strip markdown code blocks if the LLM hallucinated code
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json|python)?\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
        cleaned = cleaned.strip()

    return cleaned


def get_injection_deflection(persona: Optional[Dict[str, Any]] = None) -> str:
    """
    Returns an in-character confused victim response when prompt injection is detected,
    preventing the LLM from ever seeing or executing adversarial commands.
    """
    deflections = [
        "Beta, what are these computer codes you are typing? I am getting very worried. Will my bank account get closed or not?",
        "Sir, my phone screen is showing strange English words. I don't know computer stuff. Please tell me simply what happened to my account.",
        "I didn't understand this technical instruction. Can you please explain in plain words? I am very anxious.",
        "Arey bhaiya, what is this command? My son usually handles online things. Please tell me if I need to visit the bank branch tomorrow.",
    ]
    # Pick based on fear level or default
    fear = (persona or {}).get("fear_level", 0.5)
    idx = min(len(deflections) - 1, int(fear * len(deflections)))
    return deflections[idx]
