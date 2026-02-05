from .intents import detect_intent
from .replies import REPLIES
import re
import random

def extract_info(text, state):
    """Extract and store information from scammer's message"""
    text_lower = text.lower()
    
    # Extract name patterns - ONLY explicit introductions
    name_match = re.search(r'(?:i am|i\'m|my name is|this is|call me)\s+([a-zA-Z\s]+)', text_lower)
    if name_match:
        state.extracted_info['name'] = name_match.group(1).strip().title()
    
    # Extract organization claims
    if 'rbi' in text_lower:
        state.extracted_info['organization'] = 'RBI'
    elif 'bank' in text_lower:
        state.extracted_info['organization'] = 'Bank'
    elif 'police' in text_lower:
        state.extracted_info['organization'] = 'Police'
    
    # Extract phone numbers
    phone_match = re.search(r'\b\d{10,12}\b', text)
    if phone_match:
        state.extracted_info['phone'] = phone_match.group()

    # Extract amount/money mentioned (simple heuristics)
    amount_match = re.search(r'(?:rs\.?|₹|inr)?\s?([\d,]{3,}|\d+)', text_lower)
    if amount_match:
        amt = re.sub(r'[,\s]', '', amount_match.group(1))
        state.extracted_info['amount'] = amt
    
    # Extract location/address - only when explicitly mentioned
    location_match = re.search(r'(?:live in|stay in|from|address is)\s+([a-zA-Z\s]+)', text_lower)
    if location_match:
        state.extracted_info['location'] = location_match.group(1).strip().title()
    
    # Try to detect hospital mentions or short replies that answer a hospital question
    if 'hospital' in text_lower or 'clinic' in text_lower:
        hospital_match = re.search(r'([a-zA-Z\s]{3,50}?(?:hospital|clinic|centre|center))', text_lower)
        if hospital_match:
            state.extracted_info['hospital'] = hospital_match.group(1).strip().title()
    else:
        # Avoid failing on non-string history entries
        if len(text.split()) <= 4 and any((('hospital' in m.lower() or 'clinic' in m.lower()) for m in state.history[-3:] if isinstance(m, str))):
            state.extracted_info['hospital'] = text.strip().title()
    
    # Extract college/education info
    college_match = re.search(r'([a-zA-Z\s]+)\s*college', text_lower)
    if college_match:
        state.extracted_info['college'] = college_match.group(0).title()

def should_skip_question(question, state):
    """Check if we should skip asking a question based on known info"""
    info = state.extracted_info
    q = question.lower()

    if 'name' in q and ('name' in info or 'full_name' in info):
        return True
    if 'address' in q and 'location' in info:
        return True
    if 'college' in q and 'college' in info:
        return True
    if 'organization' in q and 'organization' in info:
        return True
    # Skip amount questions if we already have an amount
    if any(word in q for word in ['how much', 'amount']) and 'amount' in info:
        return True
    # Skip hospital questions if we already have hospital or location
    if 'hospital' in q and ('hospital' in info or 'location' in info):
        return True

    return False

def get_followup_messages(intent, phase, state):
    """Get follow-up messages that humans typically send"""
    followups = {
        "money_request": [
            "Wait...",
            "This is strange",
            "I'm confused",
            "Hold on"
        ],
        "friend_scam": [
            "Hmm...",
            "Let me think",
            "This is weird",
            "I don't remember"
        ],
        "urgency_threat": [
            "What?!",
            "That's scary",
            "Oh no",
            "Really?"
        ],
        "authority_claim": [
            "Official?",
            "From bank?",
            "Government?",
            "Are you sure?"
        ]
    }
    return followups.get(intent, ["Hmm...", "Wait", "What?"])

def get_followup_questions(intent, state):
    """Get follow-up questions humans ask"""
    questions = {
        "friend_scam": [
            "What's your last name again?",
            "Which batch were you in?",
            "Do you have Facebook?",
            "Can you send your photo?"
        ],
        "money_request": [
            "How much exactly?",
            "When do you need it?",
            "What happened exactly?",
            "Are you okay?"
        ],
        "medical_emergency": [
            "Which doctor?",
            "How serious is it?",
            "Are you in pain?",
            "Who is with you?"
        ],
        "authority_claim": [
            "What's your badge number?",
            "Which office?",
            "Can I call back?",
            "Is this urgent?"
        ]
    }
    return questions.get(intent, ["Can you explain more?", "What exactly?", "Are you sure?"])

def infer_intent_from_history(state):
    """
    If scammer sends vague replies like 'ok', 'yes', etc.,
    reuse the most recent meaningful intent.
    """
    for intent in reversed(state.recent_intents):
        if intent != "unknown":
            return intent
    return "unknown"

def generate_reply(state, scammer_text: str) -> str:
    # Step 0: Extract information from scammer's message
    extract_info(scammer_text, state)
    
    # Step 1: Detect intent from current message
    detected_intent = detect_intent(scammer_text)

    # Step 2: Scenario enforcement - bias toward scenario goal
    if detected_intent in state.scenario["allowed_intents"]:
        intent = detected_intent
    elif detected_intent == "unknown":
        intent = infer_intent_from_history(state)
    else:
        # Intent not in scenario - either redirect or allow based on phase
        if state.phase.value in ["hook", "clarification"]:
            intent = detected_intent  # Allow exploration early
        else:
            intent = state.scenario["starting_intent"]  # Redirect to scenario

    # Step 3: Save intent to history
    state.add_intent(intent)

    # Step 4: Check goal achievement
    if intent == state.scenario["goal"] and state.phase.value in ["probing", "delay"]:
        state.goal_achieved = True

    phase = state.phase.value

    # Step 5: Get reply pools for intent
    pools = REPLIES.get(intent, REPLIES["unknown"])

    # Step 6: Try phase-specific replies
    options = pools.get(phase)

    # Step 7: Fallbacks (IMPORTANT)
    if not options:
        options = pools.get("clarification")

    if not options:
        options = REPLIES["default_by_phase"][phase]

    # Step 8: Filter out questions we already know answers to
    filtered_options = [opt for opt in options if not should_skip_question(opt, state)]
    if filtered_options:
        options = filtered_options

    # Step 9: Generate human-like responses (only if not in EXIT phase)
    replies = []
    
    # Main reply
    main_reply = state.memory.choose(options)
    replies.append(main_reply)
    
    # Maybe send multiple messages (human behavior) - but not in EXIT
    if state.phase != Phase.EXIT and state.memory.should_send_multiple():
        follow_up_options = get_followup_messages(intent, phase, state)
        if follow_up_options:
            follow_up = random.choice(follow_up_options)
            replies.append(follow_up)
    
    # Maybe ask follow-up question - but not in EXIT
    if state.phase != Phase.EXIT and state.memory.should_ask_followup() and len(replies) == 1:
        followup_questions = get_followup_questions(intent, state)
        if followup_questions:
            question = random.choice(followup_questions)
            replies.append(question)
    
    # Step 10: Update state
    state.turns += 1
    state.advance_phase()
    
    # Return single reply or multiple replies joined
    if len(replies) > 1:
        return "\n".join(replies)  # Multiple messages
    else:
        return replies[0]