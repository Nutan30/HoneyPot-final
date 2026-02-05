# thresholds.py

SCAM_THRESHOLD = 60
LIKELY_SCAM_THRESHOLD = 40
MAX_RISK_SCORE = 100

# 🔐 LLM TOGGLE (DEFAULT = OFF)
ENABLE_LLM_FALLBACK = False

# Only invoke LLM if risk is in this band
LLM_LOWER_BOUND = 40
LLM_UPPER_BOUND = 70
