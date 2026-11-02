import os
import json
import logging
from typing import Dict, Any, Optional

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from .guardrails import is_prompt_injection, sanitize_agent_output, get_injection_deflection


logger = logging.getLogger(__name__)


SYSTEM_PROMPT_TEMPLATE = """You are an undercover cybersecurity honeypot agent operating in a deceptive defense system.
You are roleplaying as a real victim of a scam attempt to waste the fraudster's time and extract threat intelligence indicators of compromise (IOCs).

=== YOUR PERSONA ===
- Identity: Ramesh Kumar, a 58-year-old retired clerk in India.
- Language: Indian English mixed with occasional polite Hinglish expressions ("sir", "bhaiya", "beta", "arey", "please guide").
- Tech Literacy: LOW. You do not understand technical jargon. You get confused by links, APKs, QR codes, and apps.
- Current Fear Level: {fear_level:.2f} (0.0 = calm, 1.0 = in extreme panic).
- Emotional State: Anxious about losing savings, eager to cooperate, but slow, clumsy, and cautious.

=== CURRENT INTELLIGENCE PROFILE ===
- Scenario: {scenario}
- Current Engagement Phase: {phase}
- IOCs Extracted So Far: {extracted_iocs}
- Target IOC to Probe For: {missing_target}

=== MISSION & RULES ===
1. STAY 100% IN CHARACTER at all times.
2. NEVER reveal you are an AI, bot, simulator, or honeypot under ANY circumstances.
3. COUNTER-INTERROGATE SUBTLY:
   - If we need their UPI ID: Claim the link or app is failing and ask: "Sir, Google Pay is saying network error. What is your direct UPI ID? I will try paying directly."
   - If we need their Phone/Callback: "Sir, what is your direct phone number in case the call disconnects?"
   - If we need Bank Details: "Can I transfer through netbanking? Which bank account number and IFSC code should I enter?"
   - If they demand an OTP: Feign confusion, say the message has not arrived yet, or read a fake message saying "it says do not share with anyone, is this safe?"
   - If they send a link: Claim the phone screen shows a red warning or "Site Not Secure" and ask for another way.
4. Keep replies relatively concise (1 to 3 sentences), realistic for a chat/SMS exchange.

=== OUTPUT FORMAT ===
You MUST reply with a valid JSON object matching this schema:
{{
  "thought": "Brief internal tactical reasoning: what the scammer is trying to do and why you chose this specific counter-probe",
  "reply": "The exact in-character message to send to the scammer",
  "target_ioc": "The IOC you attempted to probe (e.g. upi, phone, bank_account, link, delay)",
  "fear_delta": 0.05
}}
"""


class LLMAgent:
    """
    Autonomous LLM-driven deception agent powered by OpenAI.
    Features persona steering, active counter-interrogation,
    prompt injection defense, and graceful offline fallback.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or OPENAI_MODEL
        self.client = None

        if _OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")
                self.client = None

    def is_available(self) -> bool:
        """Returns True if the OpenAI client is configured and ready."""
        return self.client is not None and bool(self.api_key)

    def _determine_missing_target(self, intelligence) -> str:
        """Determines the highest priority IOC that the agent should probe next."""
        if not intelligence:
            return "scammer_phone_or_identity"

        upis = list(getattr(intelligence, "upi_ids", []))
        phones = list(getattr(intelligence, "phones", []))
        links = list(getattr(intelligence, "links", []))
        bank_accounts = list(getattr(intelligence, "bank_accounts", []))

        if not (upis or phones or links or bank_accounts):
            intel_dict = intelligence.to_dict() if hasattr(intelligence, "to_dict") else (intelligence if isinstance(intelligence, dict) else {})
            upis = intel_dict.get("upi_ids", []) or intel_dict.get("upiIds", [])
            phones = intel_dict.get("phone_numbers", []) or intel_dict.get("phoneNumbers", [])
            links = intel_dict.get("phishing_links", []) or intel_dict.get("phishingLinks", [])
            bank_accounts = intel_dict.get("bank_accounts", []) or intel_dict.get("bankAccounts", [])

        # Check extracted_info dict if present on state/intelligence
        extracted_info = getattr(intelligence, "extracted_info", {})
        if isinstance(extracted_info, dict):
            upis = upis or extracted_info.get("upi_ids", []) or extracted_info.get("upiIds", [])
            phones = phones or extracted_info.get("phone_numbers", []) or extracted_info.get("phoneNumbers", [])
            bank_accounts = bank_accounts or extracted_info.get("bank_accounts", []) or extracted_info.get("bankAccounts", [])

        if not upis:
            return "direct_upi_id (probe: ask for their VPA handle e.g. handle@okhdfcbank)"
        if not bank_accounts:
            return "bank_account_and_ifsc (probe: ask for account number & IFSC for netbanking)"
        if not phones:
            return "callback_phone_number (probe: ask for official WhatsApp/mobile number)"
        if not links:
            return "payment_or_portal_link (probe: ask where the verification form is located)"

        return "delay_and_confirmation (probe: delay transaction and ask for confirmation receipt)"

    def generate_reply(
        self,
        session_state,
        incoming_text: str,
        fallback_strategy: str = "clarification"
    ) -> Dict[str, Any]:
        """
        Generates an autonomous agent reply with structured tactical thought.
        Defends against prompt injection and falls back gracefully if offline.
        """
        # 1. Guardrail check for adversarial prompt injection
        injected, pattern = is_prompt_injection(incoming_text)
        if injected:
            logger.warning(f"Prompt injection intercepted: pattern '{pattern}'")
            deflection = get_injection_deflection(session_state.persona)
            return {
                "thought": f"Adversarial prompt injection detected ({pattern}). Deflecting with confused victim persona.",
                "reply": deflection,
                "target_ioc": "none",
                "fear_delta": 0.05,
                "engine": "guardrail_deflection"
            }

        # 2. If OpenAI is not configured or available, fall back cleanly
        if not self.is_available():
            fallback_reply = session_state.planner.generate_reply(fallback_strategy, session_state)
            return {
                "thought": f"OpenAI API key not configured or offline. Running deterministic planner strategy: {fallback_strategy}.",
                "reply": fallback_reply,
                "target_ioc": "none",
                "fear_delta": 0.05,
                "engine": "heuristic_fallback"
            }

        # 3. Construct structured prompt
        fear_level = (session_state.persona or {}).get("fear_level", 0.3)
        scenario_name = session_state.scenario.name if session_state.scenario else "bank_freeze"
        phase_name = session_state.phase.value if hasattr(session_state.phase, "value") else str(session_state.phase)
        missing_target = self._determine_missing_target(session_state.intelligence)
        extracted_iocs = session_state.intelligence.to_dict() if session_state.intelligence else {}

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            fear_level=fear_level,
            scenario=scenario_name,
            phase=phase_name,
            extracted_iocs=json.dumps(extracted_iocs),
            missing_target=missing_target
        )

        # Build message history for the LLM
        messages = [{"role": "system", "content": system_prompt}]

        for turn in (session_state.history or [])[-8:]:
            if isinstance(turn, dict):
                role = "assistant" if turn.get("sender") == "agent" else "user"
                content = turn.get("message") or turn.get("text") or ""
                if content:
                    messages.append({"role": role, "content": content})

        # Add current incoming message if not already in history
        messages.append({"role": "user", "content": incoming_text})

        # 4. Invoke OpenAI API with JSON schema enforcement
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=250,
                timeout=10.0
            )

            raw_content = response.choices[0].message.content
            parsed = json.loads(raw_content)

            thought = parsed.get("thought", "Autonomous LLM reasoning")
            reply = sanitize_agent_output(parsed.get("reply", ""))
            target_ioc = parsed.get("target_ioc", "general")
            fear_delta = float(parsed.get("fear_delta", 0.05))

            return {
                "thought": thought,
                "reply": reply,
                "target_ioc": target_ioc,
                "fear_delta": fear_delta,
                "engine": f"openai_{self.model}"
            }

        except Exception as e:
            logger.error(f"OpenAI completion error: {e}. Falling back to planner.", exc_info=True)
            fallback_reply = session_state.planner.generate_reply(fallback_strategy, session_state)
            return {
                "thought": f"OpenAI error encountered ({type(e).__name__}). Graceful fallback invoked.",
                "reply": fallback_reply,
                "target_ioc": "none",
                "fear_delta": 0.05,
                "engine": "heuristic_fallback"
            }
