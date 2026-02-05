#!/usr/bin/env python3

from agent.planner import AgentPlanner

def test_intent_detection():
    """Test intent detection for bank scam messages"""
    planner = AgentPlanner()
    
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
    
    print("=== Intent Detection Test ===\n")
    
    for message in test_messages:
        intent = planner.detect_intent(message)
        print(f"Message: '{message}' -> Intent: {intent}")

if __name__ == "__main__":
    test_intent_detection()