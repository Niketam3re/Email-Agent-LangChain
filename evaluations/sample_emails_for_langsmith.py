"""
Sample Email Generator for LangSmith Dataset
Generates realistic mock emails covering various categories for evaluation
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


# ============================================================================
# EMAIL TEMPLATES BY CATEGORY
# ============================================================================

WORK_EMAILS = {
    "Project Alpha": [
        {
            "subjects": [
                "Project Alpha Status Update",
                "Alpha Milestone Review",
                "Q{q} Alpha Planning",
                "Alpha Team Sync - {date}",
                "Re: Alpha Deliverables"
            ],
            "senders": ["john.smith@company.com", "sarah.jones@company.com", "mike.chen@company.com"],
            "bodies": [
                "Hi team,\n\nCan you provide a status update on Project Alpha? We need to review progress before the quarterly planning meeting.\n\nSpecifically:\n- Current milestone completion\n- Any blockers\n- Projected completion date\n\nThanks,\n{sender_name}",
                "Hello,\n\nI wanted to touch base regarding the Alpha project timeline. Are we still on track for the end of month delivery?\n\nLet me know if there are any concerns.\n\nBest regards,\n{sender_name}",
                "Team,\n\nGreat progress on Alpha this week! A few items need attention:\n\n1. Code review for feature X\n2. Testing environment setup\n3. Documentation updates\n\nPlease update the tracker by EOD.\n\n{sender_name}"
            ],
            "tone": "professional",
            "formality": "high",
            "expected_response_length": "medium"
        }
    ],
    "Project Beta": [
        {
            "subjects": [
                "Beta Launch Timeline",
                "Beta Bug Report - Priority",
                "Re: Beta Testing Feedback",
                "Beta Deployment Plan",
                "Quick Beta Question"
            ],
            "senders": ["emily.davis@company.com", "robert.wilson@company.com", "lisa.brown@company.com"],
            "bodies": [
                "Hi,\n\nWe found a critical bug in Beta during testing. Can you take a look?\n\nSteps to reproduce:\n1. ...\n2. ...\n\nIt's blocking our launch. Please prioritize.\n\nThanks,\n{sender_name}",
                "Hello team,\n\nBeta testing is going well overall. Some feedback from users:\n\n- Feature Y is confusing\n- Performance is great\n- UI needs polish\n\nLet's discuss in tomorrow's standup.\n\n{sender_name}",
                "Quick question about Beta - what's the status of the API integration?\n\nNeed to update stakeholders by end of day.\n\nThanks!\n{sender_name}"
            ],
            "tone": "professional",
            "formality": "medium",
            "expected_response_length": "brief"
        }
    ],
    "Meetings": [
        {
            "subjects": [
                "Meeting Invitation: Team Sync",
                "Calendar: Weekly Standup",
                "Reschedule Request - 1:1",
                "Meeting Notes - {date}",
                "Can we meet this week?"
            ],
            "senders": ["calendar@company.com", "admin@company.com", "boss@company.com"],
            "bodies": [
                "Hi,\n\nLet's schedule our weekly 1:1. When works for you this week?\n\nI have openings:\n- Tuesday 2pm\n- Wednesday 10am\n- Thursday 3pm\n\nLet me know!\n\n{sender_name}",
                "Team,\n\nWeekly standup is tomorrow at 9am. Please come prepared with:\n\n- What you completed\n- What you're working on\n- Any blockers\n\nSee you then!\n{sender_name}",
                "Need to reschedule our meeting today - something came up. Can we do tomorrow same time?\n\nSorry for the inconvenience!\n\n{sender_name}"
            ],
            "tone": "professional",
            "formality": "medium",
            "expected_response_length": "brief"
        }
    ]
}

HOCKEY_EMAILS = {
    "Team A": [
        {
            "subjects": [
                "Practice this Tuesday",
                "Game Schedule Update",
                "Team A Jersey Orders",
                "Re: Playoff roster",
                "Who's in for Sunday?"
            ],
            "senders": ["coach@team-a.com", "captain@team-a.com", "john@team-a.com"],
            "bodies": [
                "Hey team!\n\nPractice is on Tuesday at 7pm. Please confirm if you're coming.\n\nWe'll be working on power plays.\n\nSee you on the ice!\n{sender_name}",
                "Hi everyone,\n\nJust got the updated game schedule. We play Saturday at 8pm instead of 7pm.\n\nDon't be late!\n\nCheers,\n{sender_name}",
                "Quick question - are you available for Sunday's game? Need to confirm the roster.\n\nLet me know ASAP!\n\n{sender_name}"
            ],
            "tone": "casual",
            "formality": "low",
            "expected_response_length": "brief"
        }
    ],
    "Team B": [
        {
            "subjects": [
                "Team B - Tournament Registration",
                "Fundraiser This Weekend",
                "New Player Introduction",
                "Equipment Check",
                "Parking Info for Game"
            ],
            "senders": ["manager@team-b.com", "treasurer@team-b.com", "dave@team-b.com"],
            "bodies": [
                "Hey guys,\n\nWe're doing a fundraiser this weekend at the arena. Can you help out for an hour or two?\n\nShifts available:\n- Saturday 10am-12pm\n- Saturday 2pm-4pm\n- Sunday 1pm-3pm\n\nThanks!\n{sender_name}",
                "Hi all,\n\nPlease bring your equipment for inspection next practice. League requires it.\n\nDon't forget!\n\n{sender_name}",
                "FYI - parking is limited for tomorrow's game. Arrive early or carpool.\n\nSee you there!\n{sender_name}"
            ],
            "tone": "casual",
            "formality": "low",
            "expected_response_length": "brief"
        }
    ]
}

PERSONAL_EMAILS = {
    "Family": [
        {
            "subjects": [
                "Thanksgiving Plans",
                "Mom's Birthday",
                "Re: Family Reunion",
                "Photos from last weekend",
                "Checking in"
            ],
            "senders": ["mom@family.com", "dad@family.com", "sister@family.com", "brother@family.com"],
            "bodies": [
                "Hi sweetie,\n\nWhat are your plans for Thanksgiving? We'd love to have you over. Let me know if you can make it!\n\nLove,\nMom",
                "Hey!\n\nSaw the photos from your vacation - looks amazing! How was the trip?\n\nWe should catch up soon.\n\nLove,\n{sender_name}",
                "Hi,\n\nJust checking in to see how you're doing. It's been a while since we talked!\n\nCall me when you get a chance.\n\n{sender_name}"
            ],
            "tone": "warm",
            "formality": "low",
            "expected_response_length": "medium"
        }
    ],
    "Friends": [
        {
            "subjects": [
                "Drinks this Friday?",
                "Re: Weekend plans",
                "Check out this article",
                "Birthday party invitation",
                "Long time no see!"
            ],
            "senders": ["alex@gmail.com", "jamie@gmail.com", "chris@gmail.com", "taylor@gmail.com"],
            "bodies": [
                "Hey!\n\nWant to grab drinks Friday night? Haven't seen you in forever!\n\nLet me know if you're free.\n\nCheers,\n{sender_name}",
                "Dude,\n\nI'm having a birthday party next Saturday. You better be there!\n\nDetails:\n- My place\n- 7pm\n- Bring snacks\n\nSee you then!\n{sender_name}",
                "Yo,\n\nCheck out this article I found - thought you'd find it interesting.\n\n[link]\n\nLet me know what you think!\n\n{sender_name}"
            ],
            "tone": "casual",
            "formality": "low",
            "expected_response_length": "brief"
        }
    ]
}

FINANCE_EMAILS = [
    {
        "subjects": [
            "Your monthly statement is ready",
            "Payment due reminder",
            "Investment update - {month}",
            "Credit card transaction alert",
            "Account activity summary"
        ],
        "senders": ["noreply@bank.com", "statements@creditcard.com", "alerts@investment.com"],
        "bodies": [
            "Your monthly statement for account ending in 1234 is now available.\n\nLogin to view: [link]\n\nIf you have questions, contact support.\n\n{sender_name}",
            "This is a reminder that your payment of $250.00 is due on {date}.\n\nPlease ensure sufficient funds in your account.\n\nThank you,\n{sender_name}",
            "Your portfolio performance for {month}:\n\n- Total value: $XX,XXX\n- Monthly change: +2.3%\n- YTD return: +8.1%\n\nView details: [link]\n\n{sender_name}"
        ],
        "tone": "formal",
        "formality": "high",
        "expected_response_length": "none"
    }
]

SHOPPING_EMAILS = [
    {
        "subjects": [
            "Your order has shipped!",
            "Order confirmation - #{order_num}",
            "20% off sale this weekend",
            "Product back in stock",
            "Your package is out for delivery"
        ],
        "senders": ["orders@amazon.com", "shipping@store.com", "deals@shop.com"],
        "bodies": [
            "Good news! Your order #{order_num} has shipped.\n\nTracking number: {tracking}\nExpected delivery: {date}\n\nTrack your package: [link]\n\nThanks for shopping with us!\n{sender_name}",
            "Thank you for your order!\n\nOrder #{order_num}\nTotal: $XX.XX\n\nYou'll receive a shipping notification soon.\n\n{sender_name}",
            "Flash sale! 20% off everything this weekend only.\n\nUse code: SAVE20\n\nShop now: [link]\n\nHappy shopping!\n{sender_name}"
        ],
        "tone": "friendly",
        "formality": "medium",
        "expected_response_length": "none"
    }
]

ORGANIZATIONAL_EMAILS = [
    {
        "subjects": [
            "Important: Policy Update",
            "Company-wide announcement",
            "Benefits enrollment reminder",
            "Office closure notice",
            "New employee onboarding"
        ],
        "senders": ["hr@company.com", "ceo@company.com", "admin@company.com"],
        "bodies": [
            "Dear team,\n\nWe're updating our remote work policy effective {date}.\n\nKey changes:\n- ...\n- ...\n\nFull details attached. Please review and acknowledge by {date}.\n\nThanks,\nHR Team",
            "Team,\n\nI'm excited to announce that we're opening a new office in Seattle!\n\nThis expansion represents significant growth for our company.\n\nMore details to come.\n\nBest,\n{sender_name}",
            "Reminder: Benefits enrollment closes {date}.\n\nPlease complete your elections in the portal.\n\nQuestions? Contact HR.\n\n{sender_name}"
        ],
        "tone": "formal",
        "formality": "high",
        "expected_response_length": "acknowledgment"
    }
]

TRAVEL_EMAILS = [
    {
        "subjects": [
            "Flight confirmation - {destination}",
            "Hotel reservation confirmed",
            "Check-in reminder",
            "Travel itinerary for {date}",
            "Booking modification confirmation"
        ],
        "senders": ["noreply@airline.com", "reservations@hotel.com", "bookings@travel.com"],
        "bodies": [
            "Your flight is confirmed!\n\nFlight: AA1234\nFrom: NYC to LAX\nDate: {date}\nTime: 8:00 AM\n\nConfirmation: ABC123\n\nCheck in online: [link]\n\nHave a great trip!\n{sender_name}",
            "Thank you for choosing our hotel.\n\nReservation details:\n- Check-in: {date}\n- Check-out: {date}\n- Room type: King Suite\n\nLooking forward to hosting you!\n\n{sender_name}",
            "Reminder: Check in for your flight tomorrow opens in 24 hours.\n\nCheck in early for best seat selection!\n\n[link]\n\n{sender_name}"
        ],
        "tone": "professional",
        "formality": "medium",
        "expected_response_length": "none"
    }
]


# ============================================================================
# EMAIL GENERATION
# ============================================================================

def generate_emails(target_count: int = 300) -> List[Dict[str, Any]]:
    """
    Generate diverse sample emails for evaluation

    Args:
        target_count: Target number of emails to generate (default 300)

    Returns:
        List of email dictionaries with inputs and expected outputs
    """
    emails = []
    email_id_counter = 1

    # Distribution (total ~300)
    distribution = {
        "Work": {"Project Alpha": 40, "Project Beta": 40, "Meetings": 40},  # 120
        "Hockey": {"Team A": 30, "Team B": 30},  # 60
        "Personal": {"Family": 25, "Friends": 25},  # 50
        "Finance": 30,
        "Shopping": 30,
        "Organizational": 30,
        "Travel": 20
    }

    # Generate Work emails
    for subcategory, count in distribution["Work"].items():
        for _ in range(count):
            emails.append(_generate_work_email(email_id_counter, "Work", subcategory))
            email_id_counter += 1

    # Generate Hockey emails
    for subcategory, count in distribution["Hockey"].items():
        for _ in range(count):
            emails.append(_generate_hockey_email(email_id_counter, "Hockey", subcategory))
            email_id_counter += 1

    # Generate Personal emails
    for subcategory, count in distribution["Personal"].items():
        for _ in range(count):
            emails.append(_generate_personal_email(email_id_counter, "Personal", subcategory))
            email_id_counter += 1

    # Generate other categories
    for category in ["Finance", "Shopping", "Organizational", "Travel"]:
        count = distribution[category]
        for _ in range(count):
            emails.append(_generate_other_email(email_id_counter, category))
            email_id_counter += 1

    # Shuffle to mix categories
    random.shuffle(emails)

    return emails[:target_count]


def _generate_work_email(email_id: int, category: str, subcategory: str) -> Dict[str, Any]:
    """Generate a work-related email"""
    template = random.choice(WORK_EMAILS[subcategory])
    subject = random.choice(template["subjects"])
    sender = random.choice(template["senders"])
    body = random.choice(template["bodies"])

    # Format placeholders
    subject = subject.format(
        q=random.randint(1, 4),
        date=_random_date_str()
    )
    sender_name = sender.split("@")[0].replace(".", " ").title()
    body = body.format(sender_name=sender_name)

    return {
        "inputs": {
            "email_id": f"email_{email_id:04d}",
            "from": sender,
            "subject": subject,
            "body": body,
            "date": _random_date(),
            "has_attachments": random.choice([True, False]) if "report" in subject.lower() else False
        },
        "outputs": {
            "expected_category": f"{category} > {subcategory}",
            "expected_tone": template["tone"],
            "expected_formality": template["formality"],
            "expected_response_length": template["expected_response_length"],
            "requires_response": True
        }
    }


def _generate_hockey_email(email_id: int, category: str, subcategory: str) -> Dict[str, Any]:
    """Generate a hockey-related email"""
    template = random.choice(HOCKEY_EMAILS[subcategory])
    subject = random.choice(template["subjects"])
    sender = random.choice(template["senders"])
    body = random.choice(template["bodies"])

    sender_name = sender.split("@")[0].title()
    body = body.format(sender_name=sender_name)

    return {
        "inputs": {
            "email_id": f"email_{email_id:04d}",
            "from": sender,
            "subject": subject,
            "body": body,
            "date": _random_date(),
            "has_attachments": False
        },
        "outputs": {
            "expected_category": f"{category} > {subcategory}",
            "expected_tone": template["tone"],
            "expected_formality": template["formality"],
            "expected_response_length": template["expected_response_length"],
            "requires_response": True
        }
    }


def _generate_personal_email(email_id: int, category: str, subcategory: str) -> Dict[str, Any]:
    """Generate a personal email"""
    template = random.choice(PERSONAL_EMAILS[subcategory])
    subject = random.choice(template["subjects"])
    sender = random.choice(template["senders"])
    body = random.choice(template["bodies"])

    sender_name = sender.split("@")[0].title()
    body = body.format(sender_name=sender_name)

    return {
        "inputs": {
            "email_id": f"email_{email_id:04d}",
            "from": sender,
            "subject": subject,
            "body": body,
            "date": _random_date(),
            "has_attachments": random.choice([True, False]) if "photo" in subject.lower() else False
        },
        "outputs": {
            "expected_category": f"{category} > {subcategory}",
            "expected_tone": template["tone"],
            "expected_formality": template["formality"],
            "expected_response_length": template["expected_response_length"],
            "requires_response": True
        }
    }


def _generate_other_email(email_id: int, category: str) -> Dict[str, Any]:
    """Generate finance, shopping, organizational, or travel email"""
    if category == "Finance":
        templates = FINANCE_EMAILS
    elif category == "Shopping":
        templates = SHOPPING_EMAILS
    elif category == "Organizational":
        templates = ORGANIZATIONAL_EMAILS
    elif category == "Travel":
        templates = TRAVEL_EMAILS

    template = random.choice(templates)
    subject = random.choice(template["subjects"])
    sender = random.choice(template["senders"])
    body = random.choice(template["bodies"])

    # Format placeholders
    subject = subject.format(
        month=random.choice(["January", "February", "March"]),
        order_num=random.randint(1000, 9999),
        destination=random.choice(["NYC", "LAX", "SFO", "ORD"])
    )
    body = body.format(
        sender_name=sender.split("@")[0].title(),
        date=_random_date_str(),
        month=random.choice(["January", "February", "March"]),
        order_num=random.randint(1000, 9999),
        tracking=f"1Z999AA10123456784"
    )

    return {
        "inputs": {
            "email_id": f"email_{email_id:04d}",
            "from": sender,
            "subject": subject,
            "body": body,
            "date": _random_date(),
            "has_attachments": "statement" in subject.lower() or "itinerary" in subject.lower()
        },
        "outputs": {
            "expected_category": category,
            "expected_tone": template["tone"],
            "expected_formality": template["formality"],
            "expected_response_length": template["expected_response_length"],
            "requires_response": category == "Organizational"
        }
    }


def _random_date() -> str:
    """Generate a random date in the past 6 months"""
    days_ago = random.randint(0, 180)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d %H:%M:%S")


def _random_date_str() -> str:
    """Generate a random date string"""
    days_ahead = random.randint(1, 30)
    date = datetime.now() + timedelta(days=days_ahead)
    return date.strftime("%B %d")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Generating Sample Emails for LangSmith Dataset")
    print("=" * 80)

    # Generate emails
    print("\n📧 Generating 300 sample emails...")
    emails = generate_emails(target_count=300)

    # Save to JSON
    output_file = "sample_emails_dataset.json"
    with open(output_file, "w") as f:
        json.dump(emails, f, indent=2)

    print(f"\n✅ Generated {len(emails)} emails")
    print(f"📁 Saved to: {output_file}")

    # Print statistics
    print("\n📊 Category Distribution:")
    category_counts = {}
    for email in emails:
        cat = email["outputs"]["expected_category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    for cat, count in sorted(category_counts.items()):
        print(f"   {cat}: {count} emails")

    print("\n💡 Next steps:")
    print("   1. Review the generated emails in sample_emails_dataset.json")
    print("   2. Run: python evaluations/create_dataset.py to upload to LangSmith")
    print("   3. Run: python evaluations/evaluate_agent.py to evaluate your agent")
