# Adapter for Teammate-2 Agent
from Agent.agent.api import process_message
from Agent.agent.state import ConversationState

# in-memory agent sessions
AGENT_SESSIONS = {}

def get_agent_reply(session: dict, latest_message: str) -> str:
    session_id = session["sessionId"]

    # create agent state once per session
    if session_id not in AGENT_SESSIONS:
        AGENT_SESSIONS[session_id] = ConversationState(
            session_id=session_id
        )

    agent_state = AGENT_SESSIONS[session_id]

    # 🚨 FAST CALL ONLY — no loops, no sleeps
    result = process_message(
        session_state=agent_state,
        incoming_text=latest_message
    )

    return result.get("reply", "Okay.")
