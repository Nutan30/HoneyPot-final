#!/usr/bin/env python3

from agent.state import ConversationState
from agent.api import process_message

def test_urgency_escalation():
    """Test urgency escalation like your transcript"""
    session_id = "urgency_test"
    state = ConversationState(session_id)
    
    # Test conversation with multiple urgency threats
    test_messages = [
        "hi",
        "aayush from axis bank", 
        "your account will be freeze in 30 minutes",
        "we found your account suspious",
        "we found a illigel activity from your account",
        "we found scam activity from your account",
        "i already told you all thing"
    ]
    
    print("=== Testing Urgency Escalation ===\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Scammer: {message}")
        
        result = process_message(state, message)
        reply = result["reply"]
        
        print(f"Agent: {reply}")
        print(f"Phase: {state.phase.value}")
        print(f"Recent intents: {state.intent_history[-3:]}")
        print("-" * 50)
        
        if result["engagement_complete"]:
            print("ENGAGEMENT COMPLETE!")
            break

if __name__ == "__main__":
    test_urgency_escalation()