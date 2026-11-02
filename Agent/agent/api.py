from .state import ConversationState
from .scenarios import SCENARIOS
from .intelligence import IntelligenceProfile
from .planner import AgentPlanner
from .llm_agent import LLMAgent
import re
import random
import time

# Strict session ID validation pattern (mirrors app/session_manager.py)
_SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{4,64}$')


def _validate_session_id(session_id: str) -> str:
    """Validate session ID to prevent path traversal in conversation file writes."""
    if not session_id or not _SESSION_ID_PATTERN.match(session_id):
        raise ValueError(f"Invalid session ID: '{session_id}'")
    return session_id


def process_message(session_state, incoming_text):
    """
    Main API function - processes scammer message and returns structured autonomous agent response
    with tactical counter-interrogation and persona steering.
    """
    # Initialize components ONCE on first call
    if session_state.intelligence is None:
        session_state.intelligence = IntelligenceProfile()
    if session_state.planner is None:
        session_state.planner = AgentPlanner()
    if getattr(session_state, "llm_agent", None) is None:
        session_state.llm_agent = LLMAgent()
    if session_state.persona is None:
        session_state.persona = {
            "name": "Ramesh Kumar",
            "age": 58,
            "language": "English / Hinglish",
            "tone": "middle-class cautious",
            "tech_skill": "low",
            "fear_level": 0.3,
            "phase": session_state.phase.value,
            "last_thought": "",
            "target_ioc": "",
            "engine": "autonomous_agent"
        }

    # Extract intelligence through intelligence profile
    session_state.intelligence.extract(incoming_text)

    # Store incoming scammer message
    session_state.history.append({
        "timestamp": time.time(),
        "sender": "scammer",
        "message": incoming_text
    })

    # Detect intent with scoring
    intent = session_state.planner.detect_intent(incoming_text)
    session_state.add_intent(intent)

    # Lock scenario based on evidence (only attempt once per turn)
    if session_state.scenario is None:
        session_state.scenario = session_state.planner.select_scenario_from_evidence(incoming_text, intent)

    # Update phase based on intent + pressure
    session_state.update_phase(intent)
    session_state.persona["phase"] = session_state.phase.value

    # Determine baseline strategy for fallback/guidance
    strategy = session_state.planner.choose_strategy(session_state)

    # Generate autonomous agent reply with persona steering, counter-interrogation, & guardrails
    llm_output = session_state.llm_agent.generate_reply(
        session_state=session_state,
        incoming_text=incoming_text,
        fallback_strategy=strategy
    )
    reply = llm_output["reply"]
    thought = llm_output.get("thought", "")
    target_ioc = llm_output.get("target_ioc", "")
    fear_delta = float(llm_output.get("fear_delta", 0.05))

    # Update persona with LLM metrics and thoughts
    session_state.persona["last_thought"] = thought
    session_state.persona["target_ioc"] = target_ioc
    session_state.persona["engine"] = llm_output.get("engine", "autonomous_agent")
    session_state.persona["fear_level"] = min(1.0, max(0.1, session_state.persona["fear_level"] + fear_delta))

    # Store agent reply in history with internal reasoning
    session_state.history.append({
        "timestamp": time.time(),
        "sender": "agent",
        "message": reply,
        "thought": thought,
        "target_ioc": target_ioc
    })

    # Check if engagement complete
    engagement_complete = session_state.is_complete()

    # Save session to JSON
    save_session_json(session_state)

    # Increment turns
    session_state.turns += 1

    # Sync to centralized SQLite repository if available
    try:
        from app.database.repository import SessionRepository
        SessionRepository.update_agent_state(
            session_id=session_state.session_id,
            scenario=session_state.scenario.name if session_state.scenario else None,
            phase=session_state.phase.value if session_state.phase else None,
            turns=session_state.turns,
            fear_level=session_state.persona.get("fear_level"),
            persona=session_state.persona
        )
    except Exception:
        pass

    return {
        "reply": reply,
        "thought": thought,
        "target_ioc": target_ioc,
        "engagement_complete": engagement_complete,
        "intelligence": session_state.intelligence.to_dict(),
        "notes": session_state.intelligence.get_notes(),
        "persona": session_state.persona
    }


def save_session_json(state):
    """Save session data to JSON file with path traversal protection."""
    import json
    import os

    # Validate session ID before constructing file path
    _validate_session_id(state.session_id)

    # Create conversations directory if it doesn't exist
    conversations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "conversations")
    os.makedirs(conversations_dir, exist_ok=True)

    session_data = {
        "session_id": state.session_id,
        "scenario": state.scenario.name if state.scenario else None,
        "phase": state.phase.value,
        "turns": state.turns,
        "conversation_history": state.history,
        "intelligence_gathered": state.intelligence.to_dict(),
        "extracted_info": state.extracted_info,
        "persona": state.persona,
        "last_thought": state.persona.get("last_thought", ""),
        "target_ioc": state.persona.get("target_ioc", ""),
        "engine": state.persona.get("engine", "autonomous_agent"),
        "notes": state.intelligence.get_notes(),
        "timestamp": time.time()
    }

    filename = os.path.join(conversations_dir, f"{state.session_id}.json")

    # Double-check resolved path stays within conversations directory
    resolved = os.path.realpath(filename)
    if not resolved.startswith(os.path.realpath(conversations_dir)):
        raise ValueError(f"Path traversal detected for session: '{state.session_id}'")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)


# ---- APP ENTRY POINT ----

_AGENT_SESSIONS = {}

def agent_handle_message(session_id: str, message: str) -> dict:
    """
    Entry point for FastAPI app.
    Validates session ID before processing.
    """
    _validate_session_id(session_id)

    if session_id not in _AGENT_SESSIONS:
        _AGENT_SESSIONS[session_id] = ConversationState(session_id)

    session_state = _AGENT_SESSIONS[session_id]

    return process_message(session_state, message)
