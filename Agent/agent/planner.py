from .scenarios import SCENARIOS
import re
import random
from .phases import Phase
from .engine import should_skip_question
from .intents import detect_intent

class AgentPlanner:
    def __init__(self):
        self.intent_keywords = {
            "otp_request": ["otp", "one time", "code", "password", "verification"],
            "upi_request": ["upi", "google pay", "phonepe", "paytm", "gpay"],
            "authority_claim": ["bank", "rbi", "police", "government", "officer"],
            "urgency_threat": ["urgent", "immediately", "blocked", "freeze", "arrest"],
            "send_link": ["link", "click", "update", "download", "install"],
            "money_request": ["send money", "need money", "emergency", "help"],
            "medical_emergency": ["hospital", "doctor", "accident", "emergency"],
            "friend_scam": ["friend", "college", "remember me", "classmate"],
            "job_offer": ["job", "work from home", "earn money", "opportunity"],
            "investment_scam": ["investment", "trading", "profit", "returns"],
            "tech_support": ["computer", "virus", "microsoft", "technical support"],
            "fake_delivery": ["delivery", "package", "courier", "customs"],
            "romance_scam": ["love", "relationship", "marry", "beautiful"],
            "reward_claim": ["lottery", "winner", "prize", "congratulations"]
        }
        
        self.strategies = {
            "feign_confusion": [
                "I don't understand what you're talking about.",
                "This is confusing. Can you explain?",
                "I'm not sure what this means.",
                "What are you asking me to do?"
            ],
            "request_alternate_payment": [
                "I don't have UPI. Is there another way?",
                "Can I pay through bank transfer instead?",
                "What other payment options do you have?",
                "I'm not comfortable with online payments."
            ],
            "delay_payment": [
                "I need to check with my family first.",
                "Can we do this tomorrow?",
                "I don't have money right now.",
                "Let me think about it."
            ],
            "challenge_softly": [
                "How do I know this is real?",
                "Can you prove you're from the bank?",
                "This seems suspicious to me.",
                "Why are you asking for this?"
            ],
            "comply_partially": [
                "I can only send half the amount.",
                "Let me send ₹500 first to test.",
                "I'll try but my limit is low.",
                "Can I send it in parts?"
            ],
            "escalate_worry": [
                "This is making me nervous.",
                "I'm scared something will go wrong.",
                "What if this is a mistake?",
                "I don't want to get in trouble."
            ]
        }
    
    def detect_intent(self, text):
        """Use centralized intent detection"""
        return detect_intent(text)
    
    def choose_strategy(self, state):
        """Choose strategy based on scenario + phase - HUMAN-LIKE FLOW"""
        phase = state.phase
        intel = state.intelligence
        recent_intents = state.intent_history[-3:] if len(state.intent_history) >= 3 else state.intent_history
        
        # Check for authority claims (bank, police, hospital, etc.) OR friend claims
        has_authority = any(intent in recent_intents for intent in ['authority_claim', 'medical_emergency'])
        has_friend_claim = any(intent in recent_intents for intent in ['friend_scam'])
        has_identity_claim = "name" in intel.extracted_info or has_authority or has_friend_claim
        
        # Use persona to influence strategy
        fear_level = state.persona.get("fear_level", 0.3)
        
        # HUMAN-LIKE FLOW: Accept premise → probe cause → escalate to extraction
        
        # First contact - who is this?
        if phase == Phase.HOOK and not has_identity_claim:
            return "feign_confusion"  # "Who is this?"
        
        # Identity claimed - accept and ask about the problem
        elif has_identity_claim and phase in [Phase.HOOK, Phase.CLARIFICATION]:
            # If we just got an authority claim, accept it
            if recent_intents and recent_intents[-1] == 'authority_claim':
                return "accept_premise"   # "What's this about?" / "What's wrong?"
            # If we got a friend claim, accept it
            elif recent_intents and recent_intents[-1] == 'friend_scam':
                return "accept_premise"   # "What's this about?" / "What's wrong?"
            else:
                return "clarification"    # Continue clarifying
        
        # Problem stated - probe details
        elif phase == Phase.CLARIFICATION:
            urgency_count = sum(1 for intent in recent_intents if intent == "urgency_threat")
            if urgency_count >= 2:
                return "escalate_worry"  # "Oh... that sounds serious. What do I need to do?"
            elif "urgency_threat" in recent_intents:
                return "probe_cause"     # "Flagged for what exactly?"
            elif "medical_emergency" in recent_intents:
                return "probe_cause"     # "What happened exactly?"
            else:
                return "clarification"   # General clarification
        
        # Details given - escalate toward solution/payment
        elif phase == Phase.PROBING:
            if fear_level > 0.6:
                return "escalate_worry"  # "That sounds serious. What do I need to do?"
            else:
                return "probe_solution"  # "How do I fix this?"
        
        # Solution offered - probe payment method
        elif phase == Phase.DELAY:
            if "send_link" in recent_intents:
                return "probe_alternative" # "Is there another way, like UPI?"
            elif "upi_request" in recent_intents:
                return "comply_partially"  # "Which UPI ID?"
            else:
                return "delay_payment"     # "Let me think about it"
        
        # Default fallback
        else:
            return "feign_confusion"
    
    def _has_scenario_evidence(self, state):
        """Check if we have evidence for current scenario"""
        recent_text = " ".join(
            msg.get("message", "") for msg in state.history[-3:] if isinstance(msg, dict)
        )
        
        scenario_keywords = {
            "bank_freeze": ["bank", "account", "upi", "kyc", "rbi", "debit"],
            "medical_emergency": ["hospital", "doctor", "accident", "emergency"],
            "job_offer": ["job", "work", "company", "salary"],
            "tech_support": ["computer", "virus", "microsoft", "windows"]
        }
        
        if state.scenario and state.scenario.name in scenario_keywords:
            keywords = scenario_keywords[state.scenario.name]
            return any(keyword in recent_text.lower() for keyword in keywords)
        
        return False
    
    def generate_reply(self, strategy, state):
        """Generate human-like reply with acknowledgment, hedging, and soft probing"""
        persona = state.persona
        fear_level = persona.get("fear_level", 0.3)
        
        # Acknowledgment phrases
        acknowledgments = ["Okay...", "I see...", "Alright...", "Oh...", "Right..."]
        
        # Hedging language based on fear
        hedges = ["I think", "maybe", "I'm not sure but", "this is confusing", "I don't know"]
        
        # Human-like response strategies following correct flow
        soft_strategies = {
            "feign_confusion": [
                "Hi... who is this?",
                "Hello, who am I talking to?",
                "Sorry, who is calling?"
            ],
            "accept_premise": [
                "Okay... what's this about?",
                "Alright... what happened?",
                "I see... what's wrong?",
                "Right... what's the problem?"
            ],
            "probe_cause": [
                "Flagged for what exactly?",
                "What kind of suspicious activity?",
                "What exactly happened?",
                "Blocked for what reason?"
            ],
            "escalate_worry": [
                "Oh... that sounds serious. What do I need to do?",
                "That's concerning... how do I fix this?",
                "This is worrying... what should I do?"
            ],
            "probe_solution": [
                "How am I supposed to verify—on a call or some link?",
                "What's the process to fix this?",
                "How do I resolve this issue?"
            ],
            "probe_alternative": [
                "I see... that page is asking for a lot. Is there another way, like UPI or branch visit?",
                "This link looks complicated... can I do UPI instead?",
                "Is there a simpler way to do this?"
            ],
            "comply_partially": [
                "Okay... which UPI ID should I send it to?",
                "Alright... give me a minute, I'm opening my app.",
                "Right... what's your UPI ID?"
            ],
            "clarification": [
                "Can you explain that again?",
                "I didn't understand completely.",
                "What do you mean exactly?"
            ],
            "delay_payment": [
                "Let me think about this first.",
                "I need to check with my family.",
                "Can we do this later?"
            ]
        }
        
        base_replies = soft_strategies.get(strategy, soft_strategies["feign_confusion"])
        
        # Use state's memory to choose (avoids repeating recent replies)
        reply = state.memory.choose(base_replies)
        
        # Add hedging based on fear (higher fear = more hedging)
        if fear_level > 0.6 and random.random() < 0.4:
            hedge = random.choice(hedges)
            reply = f"{hedge}, {reply.lower()}"
        
        # Add uncertainty for high fear
        if fear_level > 0.8:
            uncertainty = [" I'm really worried about this.", " I don't know what to do.", " This is making me nervous."]
            reply += random.choice(uncertainty)
        
        return reply
    
    def select_scenario_from_evidence(self, text, intent):
        """Select scenario based on evidence - lock early for consistent flow"""
        text_lower = text.lower()
        
        # Lock scenario early based on authority claims or context
        if any(word in text_lower for word in ["bank", "axis", "hdfc", "sbi", "account", "rbi", "blocked", "kyc"]):
            return next(s for s in SCENARIOS if s.name == "bank_freeze")
        elif any(word in text_lower for word in ["hospital", "doctor", "accident", "emergency", "medical"]):
            return next(s for s in SCENARIOS if s.name == "medical_emergency")
        elif any(word in text_lower for word in ["job", "work", "company", "salary", "interview"]):
            return next(s for s in SCENARIOS if s.name == "job_advance_fee")
        elif any(word in text_lower for word in ["computer", "virus", "microsoft", "windows", "technical"]):
            return next(s for s in SCENARIOS if s.name == "tech_support_scam")
        elif any(word in text_lower for word in ["delivery", "package", "courier", "customs"]):
            return next(s for s in SCENARIOS if s.name == "delivery_customs")
        elif any(word in text_lower for word in ["lottery", "winner", "prize", "congratulations"]):
            return next(s for s in SCENARIOS if s.name == "lottery_winner")
        elif any(word in text_lower for word in ["investment", "trading", "profit", "returns"]):
            return next(s for s in SCENARIOS if s.name == "investment_fraud")
        else:
            # Default to bank_freeze for authority claims
            if intent == "authority_claim":
                return next(s for s in SCENARIOS if s.name == "bank_freeze")
            return None