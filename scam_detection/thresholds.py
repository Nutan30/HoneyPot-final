# thresholds.py
import os

SCAM_THRESHOLD = 60
LIKELY_SCAM_THRESHOLD = 40
MAX_RISK_SCORE = 100

# 🔐 LLM TOGGLE: Enable automatically if configured or requested via env
ENABLE_LLM_FALLBACK = os.getenv("ENABLE_LLM_FALLBACK", "true").lower() in ("true", "1", "yes")

# Only invoke LLM if risk is in this ambiguous band
LLM_LOWER_BOUND = 35
LLM_UPPER_BOUND = 75
