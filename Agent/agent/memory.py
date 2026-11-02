import random
import time

class ReplyMemory:
    def __init__(self):
        self.last_replies = []
        self.last_response_time = time.time()
        self.message_count = 0

    def choose(self, options):
        valid = [o for o in options if o not in self.last_replies]
        if not valid:
            valid = options
        reply = random.choice(valid)
        self.last_replies.append(reply)
        if len(self.last_replies) > 2:
            self.last_replies.pop(0)
        return reply
    
    def should_send_multiple(self):
        """Decide if we should send multiple messages"""
        return random.random() < 0.3  # 30% chance
    
    def should_ask_followup(self):
        """Decide if we should ask a follow-up question"""
        return random.random() < 0.4  # 40% chance
    
    def get_typing_delay(self, message_length):
        """Calculate realistic typing delay based on message length"""
        base_delay = 1 + (message_length * 0.1)  # Base typing speed
        thinking_delay = random.uniform(0.5, 2.0)  # Thinking time
        return base_delay + thinking_delay
