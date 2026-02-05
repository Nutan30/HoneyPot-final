class Scenario:
    def __init__(self, name, primary_goal, secondary_goals, tactics, allowed_intents):
        self.name = name
        self.primary_goal = primary_goal
        self.secondary_goals = secondary_goals
        self.tactics = tactics
        self.allowed_intents = allowed_intents

SCENARIOS = [
    Scenario(
        name="bank_freeze",
        primary_goal="upi",
        secondary_goals=["phone", "link"],
        tactics=["urgency", "authority"],
        allowed_intents=["urgency_threat", "authority_claim", "upi_request", "send_link"]
    ),
    Scenario(
        name="otp_harvest",
        primary_goal="otp",
        secondary_goals=["phone", "bank_details"],
        tactics=["authority", "verification"],
        allowed_intents=["authority_claim", "otp_request", "urgency_threat"]
    ),
    Scenario(
        name="medical_emergency",
        primary_goal="money_transfer",
        secondary_goals=["upi", "bank_account"],
        tactics=["urgency", "emotional"],
        allowed_intents=["medical_emergency", "money_request", "friend_scam"]
    ),
    Scenario(
        name="job_advance_fee",
        primary_goal="money_transfer",
        secondary_goals=["bank_details", "documents"],
        tactics=["opportunity", "urgency"],
        allowed_intents=["job_offer", "money_request", "send_link"]
    ),
    Scenario(
        name="investment_fraud",
        primary_goal="money_transfer",
        secondary_goals=["bank_details", "documents"],
        tactics=["greed", "authority"],
        allowed_intents=["investment_scam", "money_request", "send_link"]
    ),
    Scenario(
        name="tech_support_scam",
        primary_goal="link",
        secondary_goals=["remote_access", "payment"],
        tactics=["fear", "authority"],
        allowed_intents=["tech_support", "send_link", "money_request"]
    ),
    Scenario(
        name="delivery_customs",
        primary_goal="money_transfer",
        secondary_goals=["link", "bank_details"],
        tactics=["urgency", "authority"],
        allowed_intents=["fake_delivery", "money_request", "send_link"]
    ),
    Scenario(
        name="lottery_winner",
        primary_goal="money_transfer",
        secondary_goals=["bank_details", "documents"],
        tactics=["greed", "urgency"],
        allowed_intents=["reward_claim", "money_request", "send_link"]
    )
]