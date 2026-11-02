import json
import os

def save_conversation(state):
    os.makedirs("conversations", exist_ok=True)
    path = f"conversations/{state.session_id}.json"

    with open(path, "w") as f:
        json.dump(state.history, f, indent=2)
