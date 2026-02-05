REPLIES = {
    "otp_request": {
        "hook": [
            "Who is asking for OTP?",
            "I don't know you, who is this?",
            "Why do you need my OTP?",
            "Who are you texting?",
            "What is this regarding?"
        ],
        "clarification": [
            "OTP comes by message right?",
            "Which number will it come from?",
            "I didn’t get anything yet.",
            "Is it SMS or call?",
            "Network is weak here."
        ],
        "probing": [
            "Which department is sending OTP?",
            "OTP from bank number?",
            "Can you send verification link?",
            "Any reference number?",
            "Who am I speaking with?"
        ],
        "delay": [
            "Phone is not with me right now.",
            "Battery is low.",
            "App is hanging.",
            "I’ll check in few minutes.",
            "Network issue here."
        ],
        "exit": [
            "I’ll go to bank branch.",
            "I’ll ask my son once.",
            "I’ll check later.",
            "Busy right now.",
            "I don’t want mistake."
        ]
    },

    "upi_request": {
        "clarification": [
            "UPI is same as Google Pay?",
            "Which app is this for?",
            "I don’t remember my UPI ID.",
            "Why UPI needed?",
            "Is this for refund?"
        ],
        "probing": [
            "Tell your UPI ID.",
            "Is it personal or business?",
            "Which bank UPI?",
            "Send details please.",
            "Any reference number?"
        ],
        "delay": [
            "App loading slow.",
            "UPI limit exceeded.",
            "Network issue.",
            "Trying again.",
            "Phone heating."
        ],
        "exit": [
            "I’ll check with bank.",
            "I’ll do later.",
            "Let me ask family.",
            "I’ll visit branch.",
            "Not possible now."
        ]
    },

    "money_request": {
        "hook": [
            "Who is this?",
            "I don't know you.",
            "How did you get my number?",
            "Why are you asking me for money?",
            "Who are you calling?",
            "Kaun ho tum?",
            "Paise kyun maang rahe ho?"
        ],
        "clarification": [
            "How do I know you?",
            "Why should I send you money?",
            "What is your relation to me?",
            "I don't send money to strangers.",
            "Can you prove who you are?",
            "Tumhe kaise jaanta hun?",
            "Kya rishta hai mera tumse?"
        ],
        "probing": [
            "Which hospital exactly?",
            "What is the doctor's name?",
            "Can I speak to the doctor?",
            "Send me hospital contact number.",
            "What is your full name and address?",
            "Which college did we go to?",
            "What was our teacher's name?",
            "When did we meet last time?"
        ],
        "delay": [
            "I need to verify this first.",
            "Let me call the hospital directly.",
            "I don't have money right now.",
            "I need to check with family.",
            "This sounds suspicious."
        ],
        "exit": [
            "I don't send money to unknown people.",
            "This is a scam.",
            "I'm calling the police.",
            "Stop calling me.",
            "I'm hanging up now."
        ]
    },

    "medical_emergency": {
        "hook": [
            "Who is this?",
            "I don't know you.",
            "How did you get my number?",
            "What emergency?",
            "Which hospital?"
        ],
        "clarification": [
            "What happened exactly?",
            "How do I know you?",
            "Why are you calling me?",
            "What is your relation to me?",
            "Is this real?"
        ],
        "probing": [
            "Which hospital exactly?",
            "What is the doctor's name?",
            "Can I speak to the doctor?",
            "Send me hospital contact number.",
            "What is your full name and address?"
        ],
        "delay": [
            "I need to verify this first.",
            "Let me call the hospital directly.",
            "I don't have money right now.",
            "I need to check with family.",
            "This sounds suspicious."
        ],
        "exit": [
            "I don't send money to unknown people.",
            "This is a scam.",
            "I'm calling the police.",
            "Stop calling me.",
            "I'm hanging up now."
        ]
    },

    "friend_scam": {
        "hook": [
            "Who is this?",
            "I don't recognize this number.",
            "Sorry, who am I texting with?",
            "Do I know you?",
            "How did you get my number?"
        ],
        "clarification": [
            "How do I know you?",
            "Where did we meet?",
            "What's your full name again?",
            "I'm trying to remember you.",
            "Can you remind me how we know each other?"
        ],
        "probing": [
            "Which college exactly?",
            "What year did we study together?",
            "What was our professor's name?",
            "Which department were you in?",
            "What's your father's name?",
            "Where do you live now?",
            "What's your current job?",
            "Can you send me your address?",
            "What's your email ID?",
            "Send me your photo so I can remember."
        ],
        "delay": [
            "Let me think where I know you from.",
            "I'm trying to remember our college days.",
            "My memory is a bit weak these days.",
            "Can you give me more details?",
            "I need to check my old photos first."
        ],
        "exit": [
            "I don't think we studied together.",
            "This doesn't sound right.",
            "Real friends don't ask for money like this.",
            "I'm going to verify this with college.",
            "This seems like a scam."
        ]
    },

    "urgency_threat": {
        "hook": [
            "Who is this?",
            "Who are you?",
            "How did you get my number?",
            "What are you talking about?",
            "I don't understand, who is calling?"
        ],
        "clarification": [
            "What do you mean blocked?",
            "Why would it be blocked?",
            "Who told you this?",
            "I don't understand the urgency.",
            "Can you explain more?"
        ],
        "probing": [
            "Which department are you from?",
            "What is your employee ID?",
            "Can you give me reference number?",
            "How do I verify this?",
            "Send me official email."
        ],
        "delay": [
            "I need to check with bank first.",
            "Let me call bank directly.",
            "I'll visit branch tomorrow.",
            "Can we do this later?",
            "I'm busy right now."
        ],
        "exit": [
            "I'll handle this at bank.",
            "I don't trust phone calls.",
            "I'll ask my son to help.",
            "This sounds suspicious.",
            "I'm hanging up now."
        ]
    },

    "authority_claim": {
        "hook": [
            "Who is this?",
            "I didn't call anyone.",
            "How did you get my number?",
            "What is this about?",
            "Who are you calling?"
        ],
        "clarification": [
            "Which bank are you from?",
            "What is your name?",
            "Can you prove you're from bank?",
            "I didn't call any bank.",
            "How did you get my number?"
        ],
        "probing": [
            "What is your employee ID?",
            "Which branch are you calling from?",
            "Can you transfer me to manager?",
            "Send me official email first.",
            "What is the bank's main number?"
        ]
    },

    "job_offer": {
        "hook": [
            "Who is this?",
            "I didn't apply for any job.",
            "How did you get my number?",
            "What company are you from?",
            "I'm not looking for work."
        ],
        "clarification": [
            "What kind of work is this?",
            "How much do you pay?",
            "Is this a real company?",
            "Why are you calling me?",
            "What are the job details?"
        ],
        "probing": [
            "What is your company address?",
            "Can I visit your office?",
            "Send me official email.",
            "What is your registration number?",
            "Who is your HR manager?"
        ],
        "delay": [
            "I need to think about it.",
            "Let me discuss with family.",
            "I'm busy with current job.",
            "Can you call me next week?",
            "I need to check online reviews."
        ],
        "exit": [
            "This sounds like a scam.",
            "I'm not interested anymore.",
            "I'll find job through proper channels.",
            "Stop calling me.",
            "I'm reporting this number."
        ]
    },

    "investment_scam": {
        "hook": [
            "Who are you?",
            "I don't invest with strangers.",
            "How did you get my number?",
            "What is this about?",
            "I'm not interested."
        ],
        "clarification": [
            "How can you guarantee returns?",
            "What is the risk involved?",
            "Is this legal?",
            "Show me your license.",
            "This sounds too good to be true."
        ],
        "probing": [
            "What is your SEBI registration?",
            "Send me company documents.",
            "Can I meet you in person?",
            "What is your office address?",
            "Give me client references."
        ],
        "delay": [
            "I need to consult my financial advisor.",
            "Let me research your company first.",
            "I don't have money right now.",
            "I need to discuss with my CA.",
            "Can you give me some time?"
        ],
        "exit": [
            "This is definitely a scam.",
            "I'm not investing anything.",
            "I'll report you to SEBI.",
            "Stop harassing me.",
            "I'm blocking this number."
        ]
    },

    "tech_support": {
        "hook": [
            "Who is calling?",
            "I didn't call for support.",
            "How do you know about my computer?",
            "What company are you from?",
            "I don't need help."
        ],
        "clarification": [
            "How do you know my computer has virus?",
            "Which antivirus detected this?",
            "I don't see any problem.",
            "Can you prove you're from Microsoft?",
            "My computer is working fine."
        ],
        "probing": [
            "What is your employee ID?",
            "Which Microsoft office are you from?",
            "Can you transfer me to your manager?",
            "Send me official Microsoft email.",
            "What is the exact error code?"
        ],
        "delay": [
            "My son handles the computer.",
            "Let me call Microsoft directly.",
            "I need to check with IT person.",
            "Computer is not with me now.",
            "I'll call back later."
        ],
        "exit": [
            "This is a scam call.",
            "Microsoft doesn't call like this.",
            "I'm hanging up now.",
            "Stop calling me.",
            "I'll report this to cyber crime."
        ]
    },

    "fake_delivery": {
        "hook": [
            "I didn't order anything.",
            "Who is this?",
            "What delivery are you talking about?",
            "I'm not expecting any package.",
            "Wrong number maybe?"
        ],
        "clarification": [
            "What did I order?",
            "When did I place this order?",
            "From which website?",
            "Show me the order details.",
            "I don't remember ordering this."
        ],
        "probing": [
            "What is the tracking number?",
            "Which courier company are you from?",
            "Can I speak to your supervisor?",
            "Send me delivery receipt.",
            "What is your office address?"
        ],
        "delay": [
            "I'm not at home right now.",
            "Can you deliver tomorrow?",
            "Let me check my orders first.",
            "I need to verify this.",
            "Call me in the evening."
        ],
        "exit": [
            "This is a fake delivery scam.",
            "I'm not paying anything.",
            "Stop calling me.",
            "I'll complain to courier company.",
            "This is harassment."
        ]
    },

    "romance_scam": {
        "hook": [
            "Who is this?",
            "I don't know you.",
            "How did you get my number?",
            "Wrong number.",
            "I'm not interested."
        ],
        "clarification": [
            "Where did we meet?",
            "How do you know me?",
            "What is your real name?",
            "This is very strange.",
            "I don't remember you."
        ],
        "probing": [
            "Can we meet in person?",
            "Send me your photo.",
            "What is your address?",
            "Which city are you from?",
            "Can we video call?"
        ],
        "delay": [
            "I need time to think.",
            "This is moving too fast.",
            "I'm not ready for relationship.",
            "Let me know you better first.",
            "I'm busy with work."
        ],
        "exit": [
            "This is a romance scam.",
            "I'm not sending any money.",
            "Stop contacting me.",
            "I'll block your number.",
            "This is harassment."
        ]
    },

    "reward_claim": {
        "hook": [
            "I didn't participate in any lottery.",
            "Who is this?",
            "How did I win?",
            "I don't remember entering.",
            "What are you talking about?"
        ],
        "clarification": [
            "Which lottery is this?",
            "When did I participate?",
            "How much did I win?",
            "Is this real?",
            "What do I need to do?"
        ],
        "probing": [
            "What is your company registration?",
            "Can I visit your office?",
            "Send me official documents.",
            "What is the lottery license number?",
            "Who is your manager?"
        ],
        "delay": [
            "I need to verify this first.",
            "Let me check online.",
            "I'll ask my lawyer.",
            "This seems suspicious.",
            "Can you call me tomorrow?"
        ],
        "exit": [
            "This is a lottery scam.",
            "I'm not paying any fees.",
            "Real lotteries don't work like this.",
            "Stop calling me.",
            "I'll report this fraud."
        ]
    },

    "send_link": {
        "hook": [
            "What link?",
            "I didn't request anything.",
            "Who are you?",
            "Why should I click?",
            "I don't trust links."
        ],
        "clarification": [
            "What is this link for?",
            "Is this safe to click?",
            "Why do I need to update?",
            "Which app is this?",
            "I don't understand."
        ],
        "probing": [
            "Can you explain without link?",
            "Is there another way?",
            "What happens if I don't click?",
            "Can I do this at bank branch?",
            "Send me official email instead."
        ],
        "delay": [
            "I don't click unknown links.",
            "Let me ask someone tech-savvy.",
            "I'll do this later.",
            "My phone is not working properly.",
            "I'm scared of viruses."
        ],
        "exit": [
            "I never click suspicious links.",
            "This is a phishing attempt.",
            "I'll handle this at bank.",
            "Stop sending me links.",
            "I'm reporting this."
        ]
    },

    "channel_shift": {
        "hook": [
            "Why WhatsApp?",
            "I prefer phone calls.",
            "Is this official?",
            "I don't use WhatsApp for banking.",
            "This seems odd."
        ],
        "clarification": [
            "Why can't we continue on phone?",
            "Is WhatsApp secure for this?",
            "Do banks use WhatsApp?",
            "I'm not comfortable with this.",
            "Can we do this officially?"
        ],
        "probing": [
            "What is your official WhatsApp number?",
            "Can you send official documents first?",
            "Is this your company policy?",
            "Can I verify this with bank?",
            "Why this sudden change?"
        ],
        "delay": [
            "I don't have WhatsApp.",
            "My phone doesn't support it.",
            "Let me install it first.",
            "I need to learn how to use it.",
            "Can we do this tomorrow?"
        ],
        "exit": [
            "I only deal through official channels.",
            "This is not professional.",
            "I'll visit bank branch instead.",
            "This seems like a scam.",
            "I'm not comfortable with this."
        ]
    },

    "unknown": {
        "clarification": [
            "I’m not sure what you mean.",
            "Can you explain again?",
            "What is this regarding?",
            "I didn’t understand.",
            "Say again please."
        ]
    },

    "default_by_phase": {
        "hook": [
            "Hello, who is this?",
            "Yes, what happened?",
            "I'm listening.",
            "Kaun ho?",
            "Haan, kya baat hai?"
        ],
        "clarification": [
            "Can you explain again?",
            "I didn't understand.",
            "What do you mean?",
            "Samjha nahi, phir se bolo.",
            "Kya matlab hai?"
        ],
        "probing": [
            "Tell me more details.",
            "What exactly do you need?",
            "Can you be more specific?",
            "Aur detail mein batao.",
            "Exactly kya chahiye?"
        ],
        "delay": [
            "Let me think about it.",
            "I need some time.",
            "Can we do this later?",
            "Sochne do thoda.",
            "Baad mein kar sakte hain?"
        ],
        "exit": [
            "I'll handle this myself.",
            "I need to go now.",
            "Let me call you back.",
            "Main khud dekh lunga.",
            "Phone rakhta hun."
        ]
    }
}