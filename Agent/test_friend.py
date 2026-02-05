#!/usr/bin/env python3

from agent.state import ConversationState
from agent.api import process_message

def test_friend_scam():
    """Test friend scam flow"""
    session_id = "friend_test"
    state = ConversationState(session_id)
    
    test_messages = [
        "i want 10000 urgently",
        "rahul your college friend",
        "rahul", 
        "we were in same college"
    ]
    
    print("=== Testing Friend Scam Flow ===\n")
    
    for message in test_messages:
        print(f"Scammer: {message}")
        
        result = process_message(state, message)
        reply = result["reply"]
        
        print(f"Agent: {reply}")
        print(f"Phase: {state.phase.value}")
        print(f"Recent intents: {state.intent_history[-3:]}")
        print("-" * 50)

if __name__ == "__main__":
    test_friend_scam()