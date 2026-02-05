# detector.py

from scam_detection.text_signals import analyze_text
from scam_detection.behavior import analyze_behavior
from scam_detection.thresholds import (
    SCAM_THRESHOLD,
    MAX_RISK_SCORE,
    ENABLE_LLM_FALLBACK,
    LLM_LOWER_BOUND,
    LLM_UPPER_BOUND
)
from scam_detection.schemas import scam_response
from scam_detection.llm_fallback import llm_classify


def detect_scam(message_text: str, conversation_history=None, metadata=None):
    if conversation_history is None:
        conversation_history = []
    if metadata is None:
        metadata = {}

    total_risk = 0
    signals = []

    # 1️⃣ Text + structural signals
    text_risk, text_signals = analyze_text(message_text)
    total_risk += text_risk
    signals.extend(text_signals)

    # 2️⃣ Behavior signals
    behavior_risk, behavior_signals = analyze_behavior(conversation_history)
    total_risk += behavior_risk
    signals.extend(behavior_signals)

    # 3️⃣ Channel-based boost
    if metadata.get("channel") == "SMS":
        total_risk += 10
        signals.append("sms_channel")

    # Cap risk
    total_risk = min(total_risk, MAX_RISK_SCORE)

    # 4️⃣ OPTIONAL LLM FALLBACK
    if (
        ENABLE_LLM_FALLBACK
        and LLM_LOWER_BOUND <= total_risk <= LLM_UPPER_BOUND
    ):
        llm_result = llm_classify(message_text)

        # LLM confirms scam → boost risk
        if llm_result["scamDetected"]:
            total_risk = min(total_risk + 20, MAX_RISK_SCORE)
            signals.append("llm_confirmed_scam")

    scam_detected = total_risk >= SCAM_THRESHOLD
    confidence = total_risk / MAX_RISK_SCORE

    return scam_response(
        scam_detected=scam_detected,
        risk_score=total_risk,
        confidence=confidence,
        signals=signals
    )
