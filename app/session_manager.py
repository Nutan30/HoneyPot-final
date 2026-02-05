import os
sessions = {}

def get_session(session_id: str):
    return sessions.get(session_id)

def get_or_create_session(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = {
            "sessionId": session_id,
            "messages": [],
            "totalMessages": 0,
            "scamDetected": False,
            "confidence": 0.0,
            "agentActive": False,
            "agentActive": False,
            "callbackSent": False,
            "extractedIntelligence": {}
        }
    return sessions[session_id]

def save_message_to_file(session_id: str, role: str, content: str):
    raw_dir = "intelligence/data/raw"
    os.makedirs(raw_dir, exist_ok=True)

    file_path = os.path.join(raw_dir, f"{session_id}.txt")

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{role}: {content}\n")

