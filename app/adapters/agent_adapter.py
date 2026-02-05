from Agent.agent.api import agent_handle_message

def get_agent_reply(session: dict, latest_message: str) -> str:
    result = agent_handle_message(
        session_id=session["sessionId"],
        message=latest_message
    )

    # Attach intelligence snapshot to session
    session["extractedIntelligence"] = result.get("intelligence", {})

    return result["reply"]
