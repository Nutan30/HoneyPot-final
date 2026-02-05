from .phases import Phase
from .memory import ReplyMemory
import random

class ConversationState:
    def __init__(self, session_id):
        self.session_id = session_id
        self.phase = Phase.HOOK
        self.turns = 0
        self.memory = ReplyMemory()
        self.history = []
        self.intent_history = []
        self.extracted_info = {}
        self.last_question_type = None  # Track repetition
        self.curiosity_level = 0        # Gradual escalation
        # Will be set by API
        self.scenario = None
        self.intelligence = None
        self.planner = None
        self.persona = None

    def add_intent(self, intent):
        self.intent_history.append(intent)
        if len(self.intent_history) > 10:  # Keep last 10
            self.intent_history.pop(0)

    def update_phase(self, detected_intent):
        """Real state machine based on intent + pressure"""
        recent_intents = self.intent_history[-3:] if len(self.intent_history) >= 3 else self.intent_history
        pressure_intents = ["urgency_threat", "authority_claim", "money_request"]
        
        if self.phase == Phase.HOOK:
            # First threat or payment request → PROBE
            if detected_intent in pressure_intents or detected_intent in ["otp_request", "upi_request"]:
                self.phase = Phase.CLARIFICATION
        
        elif self.phase == Phase.CLARIFICATION:
            # Payment request or link appears → EXTRACT
            if detected_intent in ["upi_request", "send_link", "money_request"]:
                self.phase = Phase.PROBING
        
        elif self.phase == Phase.PROBING:
            # Repeated pressure → DELAY
            pressure_count = sum(1 for intent in recent_intents if intent in pressure_intents)
            if pressure_count >= 2:
                self.phase = Phase.DELAY
        
        elif self.phase == Phase.DELAY:
            # Enough data or continued pressure → EXIT
            pressure_count = sum(1 for intent in recent_intents if intent in pressure_intents)
            if self.intelligence and (self.intelligence.has_valuable_data() or pressure_count >= 2):
                self.phase = Phase.EXIT
    
    def is_complete(self):
        """Check if engagement should end"""
        if not self.intelligence:
            return False
            
        # Has valuable intelligence
        if self.intelligence.has_valuable_data() and self.turns > 6:
            return True
            
        # Too many turns
        if self.turns > 12:
            return True
            
        # In EXIT phase for too long
        if self.phase == Phase.EXIT and self.turns > 8:
            return True
            
        return False
