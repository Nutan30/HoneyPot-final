SCENARIOS = [

# ───────────── BANK / FINANCE ─────────────
{
    "id": 1,
    "name": "account_freeze_kyc",
    "starting_intent": "urgency_threat",
    "allowed_intents": ["authority_claim", "otp_request", "send_link"],
    "goal": "otp"
},
{
    "id": 2,
    "name": "debit_card_blocked",
    "starting_intent": "urgency_threat",
    "allowed_intents": ["otp_request", "authority_claim"],
    "goal": "otp"
},
{
    "id": 3,
    "name": "suspicious_login",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request", "urgency_threat"],
    "goal": "otp"
},
{
    "id": 4,
    "name": "salary_account_verification",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 5,
    "name": "atm_card_expiry",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 6,
    "name": "net_banking_disabled",
    "starting_intent": "urgency_threat",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 7,
    "name": "auto_debit_failed",
    "starting_intent": "authority_claim",
    "allowed_intents": ["upi_request"],
    "goal": "upi"
},
{
    "id": 8,
    "name": "loan_emi_bounce",
    "starting_intent": "urgency_threat",
    "allowed_intents": ["upi_request"],
    "goal": "upi"
},
{
    "id": 9,
    "name": "account_dormant",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 10,
    "name": "international_txn",
    "starting_intent": "urgency_threat",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 11,
    "name": "pan_mismatch",
    "starting_intent": "authority_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},
{
    "id": 12,
    "name": "joint_account_verification",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 13,
    "name": "mobile_update_bank",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 14,
    "name": "credit_limit_exceeded",
    "starting_intent": "urgency_threat",
    "allowed_intents": ["upi_request"],
    "goal": "upi"
},
{
    "id": 15,
    "name": "account_upgrade",
    "starting_intent": "authority_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},

# ───────────── OTP FRAUD ─────────────
{
    "id": 16,
    "name": "otp_verification",
    "starting_intent": "otp_request",
    "allowed_intents": ["urgency_threat"],
    "goal": "otp"
},
{
    "id": 17,
    "name": "otp_refund",
    "starting_intent": "otp_request",
    "allowed_intents": ["authority_claim"],
    "goal": "otp"
},
{
    "id": 18,
    "name": "otp_kyc",
    "starting_intent": "otp_request",
    "allowed_intents": ["send_link"],
    "goal": "otp"
},
{
    "id": 19,
    "name": "otp_upi_reactivation",
    "starting_intent": "otp_request",
    "allowed_intents": ["upi_request"],
    "goal": "otp"
},
{
    "id": 20,
    "name": "otp_card_unblock",
    "starting_intent": "otp_request",
    "allowed_intents": ["urgency_threat"],
    "goal": "otp"
},
{
    "id": 21,
    "name": "otp_cancel_txn",
    "starting_intent": "otp_request",
    "allowed_intents": ["urgency_threat"],
    "goal": "otp"
},
{
    "id": 22,
    "name": "otp_resend_loop",
    "starting_intent": "otp_request",
    "allowed_intents": ["urgency_threat"],
    "goal": "otp"
},

# ───────────── UPI FRAUD ─────────────
{
    "id": 23,
    "name": "upi_reversal",
    "starting_intent": "upi_request",
    "allowed_intents": ["urgency_threat"],
    "goal": "upi"
},
{
    "id": 24,
    "name": "wrong_upi_transfer",
    "starting_intent": "upi_request",
    "allowed_intents": ["urgency_threat"],
    "goal": "upi"
},
{
    "id": 25,
    "name": "pending_merchant_payment",
    "starting_intent": "upi_request",
    "allowed_intents": ["urgency_threat"],
    "goal": "upi"
},
{
    "id": 26,
    "name": "refund_collect",
    "starting_intent": "upi_request",
    "allowed_intents": ["send_link"],
    "goal": "upi"
},
{
    "id": 27,
    "name": "qr_code_refund",
    "starting_intent": "upi_request",
    "allowed_intents": ["send_link"],
    "goal": "upi"
},
{
    "id": 28,
    "name": "upi_limit_unlock",
    "starting_intent": "upi_request",
    "allowed_intents": ["otp_request"],
    "goal": "upi"
},
{
    "id": 29,
    "name": "failed_upi_retry",
    "starting_intent": "upi_request",
    "allowed_intents": ["urgency_threat"],
    "goal": "upi"
},
{
    "id": 30,
    "name": "business_payment",
    "starting_intent": "upi_request",
    "allowed_intents": ["authority_claim"],
    "goal": "upi"
},

# ───────────── REWARD / OFFER ─────────────
{
    "id": 31,
    "name": "cashback_reward",
    "starting_intent": "reward_claim",
    "allowed_intents": ["upi_request"],
    "goal": "upi"
},
{
    "id": 32,
    "name": "lottery_win",
    "starting_intent": "reward_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},
{
    "id": 33,
    "name": "festival_bonus",
    "starting_intent": "reward_claim",
    "allowed_intents": ["upi_request"],
    "goal": "upi"
},
{
    "id": 34,
    "name": "credit_card_rewards",
    "starting_intent": "reward_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 35,
    "name": "govt_subsidy",
    "starting_intent": "reward_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},
{
    "id": 36,
    "name": "telecom_offer",
    "starting_intent": "reward_claim",
    "allowed_intents": ["upi_request"],
    "goal": "upi"
},

# ───────────── TELECOM ─────────────
{
    "id": 37,
    "name": "sim_verification",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 38,
    "name": "sim_block_warning",
    "starting_intent": "urgency_threat",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 39,
    "name": "number_porting",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 40,
    "name": "telecom_kyc",
    "starting_intent": "authority_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},
{
    "id": 41,
    "name": "incoming_suspension",
    "starting_intent": "urgency_threat",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},

# ───────────── GOVERNMENT ─────────────
{
    "id": 42,
    "name": "rbi_compliance",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 43,
    "name": "income_tax_refund",
    "starting_intent": "reward_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},
{
    "id": 44,
    "name": "gst_refund",
    "starting_intent": "reward_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},
{
    "id": 45,
    "name": "pension_verification",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 46,
    "name": "aadhaar_update",
    "starting_intent": "authority_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},
{
    "id": 47,
    "name": "voter_id_link",
    "starting_intent": "authority_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},

# ───────────── E-COMMERCE ─────────────
{
    "id": 48,
    "name": "delivery_hold",
    "starting_intent": "authority_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},
{
    "id": 49,
    "name": "address_confirmation",
    "starting_intent": "authority_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},
{
    "id": 50,
    "name": "cod_payment",
    "starting_intent": "upi_request",
    "allowed_intents": ["urgency_threat"],
    "goal": "upi"
},
{
    "id": 51,
    "name": "order_refund",
    "starting_intent": "reward_claim",
    "allowed_intents": ["send_link"],
    "goal": "link"
},
{
    "id": 52,
    "name": "account_lock",
    "starting_intent": "urgency_threat",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},

# ───────────── MIXED / ADVANCED ─────────────
{
    "id": 53,
    "name": "bank_telecom_combo",
    "starting_intent": "urgency_threat",
    "allowed_intents": ["authority_claim", "otp_request"],
    "goal": "otp"
},
{
    "id": 54,
    "name": "reward_then_otp",
    "starting_intent": "reward_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 55,
    "name": "authority_escalation",
    "starting_intent": "authority_claim",
    "allowed_intents": ["urgency_threat"],
    "goal": "otp"
},
{
    "id": 56,
    "name": "friendly_to_threat",
    "starting_intent": "authority_claim",
    "allowed_intents": ["urgency_threat"],
    "goal": "otp"
},
{
    "id": 57,
    "name": "fake_customer_care",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 58,
    "name": "whatsapp_support",
    "starting_intent": "channel_shift",
    "allowed_intents": ["otp_request"],
    "goal": "otp"
},
{
    "id": 59,
    "name": "call_only_pressure",
    "starting_intent": "channel_shift",
    "allowed_intents": ["urgency_threat"],
    "goal": "otp"
},
{
    "id": 60,
    "name": "slow_burn_multiday",
    "starting_intent": "authority_claim",
    "allowed_intents": ["otp_request", "send_link"],
    "goal": "otp"
}

]
