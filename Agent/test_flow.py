#!/usr/bin/env python3

from agent.state import ConversationState
from agent.api import process_message

def test_bank_scam_flow():
    """Test the correct human-like flow for bank scam"""
    session_id = "test_flow"
    state = ConversationState(session_id)
    
    # Test conversation following the correct pattern
    test_messages = [
        "hi",
        "Rahul from Axis bank", 
        "I am from axis bank",
        "your account is flagged",
        "suspicious activity",
        "verify details",
        "send on this link http://fake-site.in",
        "UPI",
        "axishelp@upi"
    ]
    
    print("=== Testing Bank Scam Flow ===\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Scammer: {message}")
        
        result = process_message(state, message)
        reply = result["reply"]
        
        print(f"Agent: {reply}")
        print(f"Phase: {state.phase.value}")
        print(f"Intelligence: {result['intelligence']}")
        print("-" * 50)
        
        if result["engagement_complete"]:
            print("ENGAGEMENT COMPLETE!")
            break
    
    print(f"\nFinal Intelligence Gathered:")
    for key, value in result["intelligence"].items():
        if value:
            print(f"  {key}: {value}")
    print(f"Notes: {result['notes']}")

if __name__ == "__main__":
    test_bank_scam_flow()