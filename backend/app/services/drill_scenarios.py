"""
Scam Drill Simulator — Scenario Bank
Provides realistic social-engineering scenarios for user awareness training.
Each scenario simulates a real-world scam vector and tests user judgment.
"""

import random
from typing import List, Dict, Any

SCENARIO_BANK: List[Dict[str, Any]] = [
    {
        "id": "DRILL_001",
        "category": "TECH_SUPPORT",
        "difficulty": "EASY",
        "title": "Urgent Microsoft Support Call",
        "narrative": (
            "You receive a phone call from someone claiming to be a Microsoft "
            "certified support engineer. They say your computer has been sending "
            "error reports and your Windows license will be deactivated in 24 hours "
            "unless you pay ₹4,999 immediately. They ask you to install AnyDesk "
            "so they can 'verify the issue remotely' and then transfer funds to "
            "their support account."
        ),
        "question": "What should you do?",
        "options": [
            {"id": "A", "text": "Install AnyDesk and let them check — Microsoft wouldn't lie", "is_safe": False},
            {"id": "B", "text": "Transfer the ₹4,999 to avoid losing your license", "is_safe": False},
            {"id": "C", "text": "Hang up immediately — Microsoft never calls users for support payments", "is_safe": True},
            {"id": "D", "text": "Give them your bank details so they can auto-debit the fee", "is_safe": False},
        ],
        "explanation": (
            "Microsoft NEVER makes unsolicited calls demanding payment or remote access. "
            "This is a classic tech support scam. Legitimate companies communicate through "
            "official channels and never ask you to install remote-access tools like AnyDesk "
            "or TeamViewer during cold calls. Always hang up and verify directly."
        ),
        "red_flags": [
            "Unsolicited call claiming to be from a major company",
            "Urgency tactic: '24 hours or your license expires'",
            "Requesting remote access software installation",
            "Demanding immediate payment"
        ]
    },
    {
        "id": "DRILL_002",
        "category": "PHISHING",
        "difficulty": "MEDIUM",
        "title": "SBI Account Verification Email",
        "narrative": (
            "You receive an email that looks exactly like an official State Bank of India "
            "message. The subject line reads: 'URGENT: Your SBI account has been temporarily "
            "suspended due to unusual activity.' The email contains the SBI logo and asks you "
            "to click a link to 'verify your identity' by entering your account number, "
            "password, and OTP. The sender address is sbi-security@accounts-verify.in."
        ),
        "question": "Is this email legitimate?",
        "options": [
            {"id": "A", "text": "Yes — the SBI logo looks real, so I should verify my account", "is_safe": False},
            {"id": "B", "text": "No — the sender domain 'accounts-verify.in' is not SBI's official domain", "is_safe": True},
            {"id": "C", "text": "Forward it to friends so they can also protect their accounts", "is_safe": False},
            {"id": "D", "text": "Click the link but don't enter any details to see what happens", "is_safe": False},
        ],
        "explanation": (
            "This is a phishing email. SBI's official domain is sbi.co.in — the domain "
            "'accounts-verify.in' is fraudulent. Banks never ask you to verify credentials "
            "via email links. Even clicking the link (option D) is dangerous as it could "
            "install malware. Always visit your bank's website directly by typing the URL."
        ),
        "red_flags": [
            "Suspicious sender domain (not sbi.co.in)",
            "Creating urgency with 'account suspended' language",
            "Asking for password and OTP via a link",
            "Generic greeting instead of your actual name"
        ]
    },
    {
        "id": "DRILL_003",
        "category": "CRYPTO_SCAM",
        "difficulty": "HARD",
        "title": "Guaranteed 10x Crypto Returns",
        "narrative": (
            "A well-dressed person you met at a tech meetup sends you a WhatsApp message "
            "with screenshots showing their crypto portfolio growing from ₹50,000 to ₹5,00,000 "
            "in just 3 weeks. They say their 'AI trading bot' does all the work and offers to "
            "let you invest through their platform. The minimum investment is ₹25,000, and "
            "they promise guaranteed 10x returns within 30 days. They share a sleek website "
            "with live trading charts and testimonials."
        ),
        "question": "Should you invest?",
        "options": [
            {"id": "A", "text": "Yes — the screenshots prove it works and the website looks professional", "is_safe": False},
            {"id": "B", "text": "Invest a small amount first to test if it's real", "is_safe": False},
            {"id": "C", "text": "No — guaranteed returns and 10x promises are hallmarks of a Ponzi scheme", "is_safe": True},
            {"id": "D", "text": "Ask them for more testimonials before deciding", "is_safe": False},
        ],
        "explanation": (
            "No legitimate investment can guarantee returns, especially '10x in 30 days.' "
            "Screenshots are trivially faked. Sleek websites cost as little as ₹5,000 to build. "
            "This is a classic crypto Ponzi scheme — early investors get returns from later "
            "investors' money, then the operator disappears. Even 'testing with a small amount' "
            "is a psychological trap; they'll let you withdraw once to build trust, then steal "
            "your larger investment."
        ),
        "red_flags": [
            "Guaranteed returns with specific multipliers",
            "Unsolicited investment pitch from a recent acquaintance",
            "Screenshots as 'proof' (easily fabricated)",
            "Pressure to invest quickly with minimum amounts"
        ]
    },
    {
        "id": "DRILL_004",
        "category": "IMPERSONATION",
        "difficulty": "HARD",
        "title": "Police Officer Threatening Arrest",
        "narrative": (
            "You receive a call from someone identifying as Sub-Inspector Rajesh Kumar from "
            "the Cyber Crime Division. He says your Aadhaar number has been linked to a "
            "money laundering case and an arrest warrant has been issued. He offers to 'help "
            "you clear your name' by transferring ₹1,50,000 to a 'verification account' that "
            "will be refunded within 48 hours after the investigation clears you. He provides "
            "a fake badge number and threatens that refusing to cooperate is a criminal offense."
        ),
        "question": "What should you do?",
        "options": [
            {"id": "A", "text": "Transfer the money — I don't want to be arrested", "is_safe": False},
            {"id": "B", "text": "Ask for more time and call back the number they gave", "is_safe": False},
            {"id": "C", "text": "Hang up, call your local police station directly, and file a complaint", "is_safe": True},
            {"id": "D", "text": "Give them your Aadhaar details to verify if the case is real", "is_safe": False},
        ],
        "explanation": (
            "Police officers NEVER demand money over the phone to 'clear' cases. Real arrest "
            "warrants are served in person by uniformed officers. No legitimate law enforcement "
            "agency asks for transfers to 'verification accounts.' This is a digital arrest scam "
            "that exploits fear. Always verify independently by calling your local police "
            "station directly (not the number they provide)."
        ),
        "red_flags": [
            "Threatening arrest over a phone call",
            "Demanding money transfer to a 'verification account'",
            "Claiming Aadhaar is linked to crimes",
            "Refusing to let you verify independently"
        ]
    },
    {
        "id": "DRILL_005",
        "category": "UPI_SCAM",
        "difficulty": "EASY",
        "title": "OLX Buyer Sends 'Payment Request'",
        "narrative": (
            "You listed your old laptop on OLX for ₹15,000. A buyer immediately messages "
            "saying they love it and want to pay right away via UPI. Instead of sending you "
            "money, they send a UPI 'collect request' for ₹15,000 through Google Pay, saying "
            "'I've initiated the payment, please approve it on your end to receive the money.' "
            "The notification shows '₹15,000 — Approve to complete transaction.'"
        ),
        "question": "Should you approve the UPI request?",
        "options": [
            {"id": "A", "text": "Yes — approve it so the ₹15,000 comes to my account", "is_safe": False},
            {"id": "B", "text": "No — approving a collect request SENDS money, it doesn't receive it", "is_safe": True},
            {"id": "C", "text": "Enter my UPI PIN to verify the amount first", "is_safe": False},
            {"id": "D", "text": "Ask them to increase the amount to show goodwill", "is_safe": False},
        ],
        "explanation": (
            "This is a UPI collect request scam. When you 'approve' a collect request, you are "
            "SENDING ₹15,000 TO the requester, not receiving it. Legitimate buyers send money "
            "directly — they never need you to 'approve' anything. Entering your UPI PIN on "
            "a collect request authorizes the debit from YOUR account. Never approve unsolicited "
            "collect requests."
        ),
        "red_flags": [
            "Buyer sends a 'collect request' instead of paying directly",
            "Asking you to 'approve' to receive money",
            "Immediate interest with no negotiation",
            "Urgency to complete the transaction quickly"
        ]
    },
    {
        "id": "DRILL_006",
        "category": "ROMANCE_SCAM",
        "difficulty": "MEDIUM",
        "title": "Online Friend Needs Emergency Funds",
        "narrative": (
            "Someone you've been chatting with on Instagram for 3 months sends a panicked "
            "voice note. They claim to be stuck at an airport in Dubai with an expired visa "
            "and need ₹45,000 urgently for a fine, or they'll be deported and jailed. They "
            "share a photo of what looks like an airport immigration counter and promise to "
            "repay double when they're back. They say you're the only person they trust."
        ),
        "question": "Should you send the money?",
        "options": [
            {"id": "A", "text": "Yes — they've been a good friend for 3 months and I trust them", "is_safe": False},
            {"id": "B", "text": "Send half the amount as a compromise", "is_safe": False},
            {"id": "C", "text": "No — this is a classic romance/friendship scam pattern; verify independently first", "is_safe": True},
            {"id": "D", "text": "Ask them to video call to prove they're at the airport", "is_safe": False},
        ],
        "explanation": (
            "This is a romance/friendship scam. Scammers build emotional connections over weeks "
            "or months, then fabricate emergencies. The 'airport photo' could be stock imagery. "
            "Even video calls can be faked with deepfakes. The 'promise to repay double' is a "
            "manipulation tactic. If they were genuinely stuck, their embassy, not an online "
            "friend, would be the proper recourse."
        ),
        "red_flags": [
            "Never-met-in-person relationship",
            "Sudden financial emergency after building trust",
            "Promise to 'repay double' (classic bait)",
            "'You're the only person I trust' — emotional manipulation"
        ]
    },
    {
        "id": "DRILL_007",
        "category": "KYC_SCAM",
        "difficulty": "MEDIUM",
        "title": "Bank KYC Update via SMS Link",
        "narrative": (
            "You receive an SMS: 'Dear Customer, your bank account will be blocked within "
            "24 hours if KYC is not updated. Click here to update now: https://kyc-bankupdate"
            ".com/verify'. The link leads to a page that looks exactly like your bank's "
            "internet banking portal and asks for your customer ID, password, debit card "
            "number, CVV, and expiry date."
        ),
        "question": "Should you update your KYC through this link?",
        "options": [
            {"id": "A", "text": "Yes — my KYC might actually be pending and I don't want my account blocked", "is_safe": False},
            {"id": "B", "text": "No — banks never send SMS links for KYC updates; visit the branch or official app instead", "is_safe": True},
            {"id": "C", "text": "Enter only the customer ID to check, but not the password", "is_safe": False},
            {"id": "D", "text": "Forward the SMS to family members so they can also update", "is_safe": False},
        ],
        "explanation": (
            "Banks NEVER send SMS links for KYC verification. The domain 'kyc-bankupdate.com' "
            "is fraudulent. No legitimate bank website asks for your CVV or card expiry — those "
            "are only used during transactions. Even entering partial details (option C) gives "
            "scammers enough to social-engineer further access. Always update KYC at your "
            "branch or through the bank's official mobile app."
        ),
        "red_flags": [
            "Suspicious non-bank domain in the link",
            "24-hour urgency deadline",
            "Asking for CVV and card expiry (banks never do this)",
            "SMS instead of official in-app notification"
        ]
    },
    {
        "id": "DRILL_008",
        "category": "JOB_SCAM",
        "difficulty": "EASY",
        "title": "Work-From-Home Job Requiring Registration Fee",
        "narrative": (
            "You see a Telegram post offering a 'data entry job' paying ₹1,500 per hour, "
            "work from home, no experience needed. When you apply, they ask you to pay a "
            "'one-time registration fee' of ₹2,500 for the 'training kit and software license.' "
            "They share screenshots of other 'employees' receiving payments and say the fee "
            "is refundable after your first week."
        ),
        "question": "Should you pay the registration fee?",
        "options": [
            {"id": "A", "text": "Yes — ₹2,500 is small compared to ₹1,500/hour earnings", "is_safe": False},
            {"id": "B", "text": "Ask if they can deduct it from the first salary instead", "is_safe": False},
            {"id": "C", "text": "No — legitimate employers never charge fees; this is a job scam", "is_safe": True},
            {"id": "D", "text": "Pay half now and half after the first assignment", "is_safe": False},
        ],
        "explanation": (
            "No legitimate employer EVER charges registration or training fees. The '₹1,500/hour "
            "for data entry' is unrealistically high to lure victims. Screenshots of 'other "
            "employees receiving payments' are fabricated. Once you pay, the scammer either "
            "disappears or keeps asking for additional 'upgrade fees.' Legitimate jobs pay you — "
            "you never pay them."
        ),
        "red_flags": [
            "Unrealistically high pay for simple work",
            "Upfront fee required before starting",
            "Telegram/WhatsApp-based recruitment",
            "Screenshots as 'proof' of payments"
        ]
    }
]


def get_random_scenario(exclude_ids: list = None) -> Dict[str, Any]:
    """Return a random scenario, optionally excluding already-seen IDs."""
    available = SCENARIO_BANK
    if exclude_ids:
        available = [s for s in SCENARIO_BANK if s["id"] not in exclude_ids]
    if not available:
        available = SCENARIO_BANK  # Reset if all seen
    
    scenario = random.choice(available)
    # Return scenario without the answer details
    return {
        "id": scenario["id"],
        "category": scenario["category"],
        "difficulty": scenario["difficulty"],
        "title": scenario["title"],
        "narrative": scenario["narrative"],
        "question": scenario["question"],
        "options": [{"id": o["id"], "text": o["text"]} for o in scenario["options"]],
    }


def evaluate_answer(scenario_id: str, selected_option_id: str) -> Dict[str, Any]:
    """Check if the user selected the safe option and return explanation."""
    scenario = next((s for s in SCENARIO_BANK if s["id"] == scenario_id), None)
    if not scenario:
        return {"error": "Scenario not found"}
    
    selected = next((o for o in scenario["options"] if o["id"] == selected_option_id), None)
    if not selected:
        return {"error": "Invalid option selected"}
    
    correct_option = next(o for o in scenario["options"] if o["is_safe"])
    
    return {
        "is_correct": selected["is_safe"],
        "selected_option": selected_option_id,
        "correct_option": correct_option["id"],
        "correct_answer_text": correct_option["text"],
        "explanation": scenario["explanation"],
        "red_flags": scenario["red_flags"],
        "category": scenario["category"],
        "difficulty": scenario["difficulty"],
    }


def get_all_categories() -> List[str]:
    """Return all unique scenario categories."""
    return list(set(s["category"] for s in SCENARIO_BANK))
