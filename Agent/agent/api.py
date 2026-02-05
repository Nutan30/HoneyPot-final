from .state import ConversationState
from .scenarios import SCENARIOS
from .intelligence import IntelligenceProfile
from .planner import AgentPlanner
import random
import time

def process_message(session_state, incoming_text):
    """
    Main API function - processes scammer message and returns structured response
    """
    # Initialize if new session
    if session_state.scenario is None:
        # Don't lock scenario immediately - wait for evidence
        session_state.scenario = None  # Will be set based on evidence
        session_state.intelligence = IntelligenceProfile()
        session_state.planner = AgentPlanner()
        session_state.persona = {
            "language": "English",
            "tone": "middle-class cautious", 
            "tech_skill": "low",
            "fear_level": 0.3,
            "phase": session_state.phase.value
        }
    
    # Extract intelligence ONLY through intelligence.py
    session_state.intelligence.extract(incoming_text)
    
    # Store conversation history (structured)
    session_state.history.append({
        "timestamp": time.time(),
        "sender": "scammer", 
        "message": incoming_text
    })
    
    # Detect intent with scoring
    intent = session_state.planner.detect_intent(incoming_text)
    session_state.add_intent(intent)
    
    # Lock scenario based on evidence (not assumptions)
    if session_state.scenario is None:
        session_state.scenario = session_state.planner.select_scenario_from_evidence(incoming_text, intent)
    
    # Update persona with current phase
    session_state.persona["phase"] = session_state.phase.value
    
    # Update phase based on intent + pressure
    session_state.update_phase(intent)
    
    # Choose strategy based on scenario + state
    strategy = session_state.planner.choose_strategy(session_state)
    
    # Generate reply using strategy + state (so we can avoid repeating questions)
    reply = session_state.planner.generate_reply(strategy, session_state)

    # Store agent reply
    session_state.history.append({
        "timestamp": time.time(),
        "sender": "agent",
        "message": reply
    })
    
    # Check if engagement complete
    engagement_complete = session_state.is_complete()
    
    # Save session to JSON
    save_session_json(session_state)
    
    # Increase fear level gradually
    session_state.persona["fear_level"] = min(1.0, session_state.persona["fear_level"] + 0.05)
    
    # Increment turns
    session_state.turns += 1
    
    return {
        "reply": reply,
        "engagement_complete": engagement_complete,
        "intelligence": session_state.intelligence.to_dict(),
        "notes": session_state.intelligence.get_notes()
    }
def save_session_json(state):
    """Save session data to JSON file"""
    import json
    import os
    import time
    
    # Create conversations directory if it doesn't exist
    os.makedirs("conversations", exist_ok=True)
    
    session_data = {
        "session_id": state.session_id,
        "scenario": state.scenario.name if state.scenario else None,
        "phase": state.phase.value,
        "turns": state.turns,
        "conversation_history": state.history,
        "intelligence_gathered": state.intelligence.to_dict(),
        "extracted_info": state.extracted_info,
        "persona": state.persona,
        "notes": state.intelligence.get_notes(),
        "timestamp": time.time()
    }
    
    filename = f"conversations/{state.session_id}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
        
# ---- APP ENTRY POINT ----

_AGENT_SESSIONS = {}

def agent_handle_message(session_id: str, message: str) -> dict:
    """
    Entry point for FastAPI app
    """

    if session_id not in _AGENT_SESSIONS:
        _AGENT_SESSIONS[session_id] = ConversationState(session_id)

    session_state = _AGENT_SESSIONS[session_id]

    return process_message(session_state, message)
