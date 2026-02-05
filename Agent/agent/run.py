import json
import time
import random
from agent.state import ConversationState
from agent.api import process_message

state_store = {}

def handle_input(input_json):
    session_id = input_json["session_id"]
    message = input_json["message"]

    if session_id not in state_store:
        state_store[session_id] = ConversationState(session_id)

    state = state_store[session_id]

    # Simulate human typing delay
    typing_delay = 1 + (len(message) * 0.1) + random.uniform(0.5, 2.0)
    print(f"[Typing for {typing_delay:.1f} seconds...]")
    time.sleep(min(typing_delay, 3.0))

    # Use new API
    result = process_message(state, message)
    
    # Handle multiple messages with delays
    reply = result["reply"]
    if "\n" in reply:
        messages = reply.split("\n")
        for i, msg in enumerate(messages):
            if i > 0:
                follow_up_delay = random.uniform(1.0, 3.0)
                print(f"[Typing follow-up for {follow_up_delay:.1f} seconds...]")
                time.sleep(follow_up_delay)
            print(f"Agent: {msg}")
        
        # Show intelligence if engagement complete
        if result["engagement_complete"]:
            print(f"\n=== INTELLIGENCE GATHERED ===")
            intel = result["intelligence"]
            for key, value in intel.items():
                if value:
                    print(f"{key}: {value}")
            print(f"Notes: {result['notes']}")
            print("=== ENGAGEMENT COMPLETE ===")
        
        return " | ".join(messages)
    else:
        if result["engagement_complete"]:
            print(f"\n=== INTELLIGENCE GATHERED ===")
            intel = result["intelligence"]
            for key, value in intel.items():
                if value:
                    print(f"{key}: {value}")
            print(f"Notes: {result['notes']}")
            print("=== ENGAGEMENT COMPLETE ===")
        
        return reply

if __name__ == "__main__":
    print("Agent started. Enter messages directly for testing.\n")
    session_id = "test_session"
    
    while True:
        message = input("Message: ").strip()
        if not message:
            print("Please enter a message.\n")
            continue
        
        # Create test input data
        data = {"session_id": session_id, "message": message}
        result = handle_input(data)
        
        # Only print if it's a single message (multiple messages already printed)
        if " | " not in result:
            print("Agent:", result)
