"""
Import Your Own Emails to LangSmith Dataset
Template script for importing your anonymized emails for evaluation
"""

import json
import os
import csv
from typing import List, Dict, Any
from datetime import datetime
from langsmith import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LangSmith configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
DATASET_NAME = "email-agent-my-emails-v1"


# ============================================================================
# IMPORT FROM DIFFERENT FORMATS
# ============================================================================

def import_from_json(filepath: str) -> List[Dict[str, Any]]:
    """
    Import emails from JSON file

    Expected format:
    [
        {
            "from": "sender@example.com",
            "subject": "Email subject",
            "body": "Email body text...",
            "date": "2024-01-15 10:30:00",
            "expected_category": "Work > Project Alpha",
            "expected_tone": "professional",
            "expected_formality": "high"
        },
        ...
    ]

    Args:
        filepath: Path to JSON file

    Returns:
        List of email dictionaries formatted for LangSmith
    """
    with open(filepath, "r") as f:
        raw_emails = json.load(f)

    formatted_emails = []
    for i, email in enumerate(raw_emails, 1):
        formatted_emails.append({
            "inputs": {
                "email_id": f"my_email_{i:04d}",
                "from": email.get("from", "unknown@example.com"),
                "subject": email.get("subject", "No subject"),
                "body": email.get("body", ""),
                "date": email.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "has_attachments": email.get("has_attachments", False)
            },
            "outputs": {
                "expected_category": email.get("expected_category", "Unknown"),
                "expected_tone": email.get("expected_tone", "neutral"),
                "expected_formality": email.get("expected_formality", "medium"),
                "expected_response_length": email.get("expected_response_length", "medium"),
                "requires_response": email.get("requires_response", True)
            }
        })

    return formatted_emails


def import_from_csv(filepath: str) -> List[Dict[str, Any]]:
    """
    Import emails from CSV file

    Expected columns:
    from, subject, body, date, expected_category, expected_tone, expected_formality

    Args:
        filepath: Path to CSV file

    Returns:
        List of email dictionaries formatted for LangSmith
    """
    formatted_emails = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):
            formatted_emails.append({
                "inputs": {
                    "email_id": f"my_email_{i:04d}",
                    "from": row.get("from", "unknown@example.com"),
                    "subject": row.get("subject", "No subject"),
                    "body": row.get("body", ""),
                    "date": row.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "has_attachments": row.get("has_attachments", "false").lower() == "true"
                },
                "outputs": {
                    "expected_category": row.get("expected_category", "Unknown"),
                    "expected_tone": row.get("expected_tone", "neutral"),
                    "expected_formality": row.get("expected_formality", "medium"),
                    "expected_response_length": row.get("expected_response_length", "medium"),
                    "requires_response": row.get("requires_response", "true").lower() == "true"
                }
            })

    return formatted_emails


def import_from_python_list(emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Import emails from Python list

    Use this if you want to define your emails directly in Python

    Args:
        emails: List of email dictionaries

    Returns:
        List of email dictionaries formatted for LangSmith
    """
    formatted_emails = []

    for i, email in enumerate(emails, 1):
        formatted_emails.append({
            "inputs": {
                "email_id": email.get("email_id", f"my_email_{i:04d}"),
                "from": email.get("from", "unknown@example.com"),
                "subject": email.get("subject", "No subject"),
                "body": email.get("body", ""),
                "date": email.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "has_attachments": email.get("has_attachments", False)
            },
            "outputs": {
                "expected_category": email.get("expected_category", "Unknown"),
                "expected_tone": email.get("expected_tone", "neutral"),
                "expected_formality": email.get("expected_formality", "medium"),
                "expected_response_length": email.get("expected_response_length", "medium"),
                "requires_response": email.get("requires_response", True)
            }
        })

    return formatted_emails


# ============================================================================
# ANONYMIZATION HELPERS
# ============================================================================

def anonymize_email(email: Dict[str, Any]) -> Dict[str, Any]:
    """
    Anonymize sensitive information in an email

    Replaces:
    - Email addresses with generic ones
    - Names with generic placeholders
    - Phone numbers with xxx-xxx-xxxx
    - Account numbers with xxxx

    Args:
        email: Email dictionary

    Returns:
        Anonymized email dictionary
    """
    import re

    # Anonymize sender
    if "from" in email:
        email["from"] = _anonymize_email_address(email["from"])

    # Anonymize body
    if "body" in email:
        body = email["body"]

        # Replace email addresses
        body = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email@example.com', body)

        # Replace phone numbers
        body = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'xxx-xxx-xxxx', body)

        # Replace account numbers (sequences of 8+ digits)
        body = re.sub(r'\b\d{8,}\b', 'xxxxxxxxxxxx', body)

        # Replace dollar amounts over $1000 with rounded amounts
        body = re.sub(r'\$\d{4,}(?:\.\d{2})?', '$X,XXX', body)

        email["body"] = body

    return email


def _anonymize_email_address(email: str) -> str:
    """Anonymize an email address while preserving domain type"""
    if "@" not in email:
        return "user@example.com"

    local, domain = email.split("@", 1)

    # Preserve common domain types
    if "gmail" in domain:
        return "user@gmail.com"
    elif "company" in domain or "corp" in domain or "work" in domain:
        return "user@company.com"
    elif "yahoo" in domain:
        return "user@yahoo.com"
    elif "outlook" in domain or "hotmail" in domain:
        return "user@outlook.com"
    else:
        return "user@example.com"


# ============================================================================
# UPLOAD TO LANGSMITH
# ============================================================================

def upload_to_langsmith(
    emails: List[Dict[str, Any]],
    dataset_name: str = DATASET_NAME,
    description: str = "Custom email dataset from user's inbox"
) -> None:
    """
    Upload emails to LangSmith dataset

    Args:
        emails: List of formatted email dictionaries
        dataset_name: Name for the dataset in LangSmith
        description: Description for the dataset
    """
    client = Client(api_key=LANGSMITH_API_KEY)

    print(f"\n📦 Creating dataset '{dataset_name}'...")

    # Check if dataset exists
    try:
        existing_datasets = list(client.list_datasets())
        dataset_exists = any(ds.name == dataset_name for ds in existing_datasets)

        if dataset_exists:
            print(f"⚠️  Dataset '{dataset_name}' already exists")
            response = input("Delete and recreate? (y/n): ")

            if response.lower() == "y":
                dataset_id = next(ds.id for ds in existing_datasets if ds.name == dataset_name)
                client.delete_dataset(dataset_id=dataset_id)
                print(f"✅ Deleted existing dataset")
            else:
                print("❌ Aborted")
                return
    except Exception as e:
        print(f"⚠️  Could not check existing datasets: {e}")

    # Create dataset
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description=description
    )

    print(f"✅ Created dataset: {dataset.id}")

    # Upload examples
    print(f"\n📤 Uploading {len(emails)} emails...")

    for i, email in enumerate(emails, 1):
        try:
            client.create_example(
                dataset_id=dataset.id,
                inputs=email["inputs"],
                outputs=email["outputs"]
            )

            if i % 10 == 0:
                print(f"   Uploaded {i}/{len(emails)}...")

        except Exception as e:
            print(f"   ⚠️  Error uploading email {i}: {e}")

    print(f"\n✅ Upload complete!")
    print(f"🔗 View at: https://smith.langchain.com/datasets")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_usage():
    """
    Example of how to use this script

    CUSTOMIZE THIS FUNCTION with your own emails
    """
    # Option 1: Define emails directly in Python
    my_emails = [
        {
            "from": "boss@company.com",
            "subject": "Q1 Review Meeting",
            "body": "Hi,\n\nLet's schedule our Q1 review for next week. Please come prepared with your metrics.\n\nThanks,\nBoss",
            "date": "2024-01-15 09:00:00",
            "expected_category": "Work > Meetings",
            "expected_tone": "professional",
            "expected_formality": "high"
        },
        {
            "from": "friend@gmail.com",
            "subject": "Coffee this weekend?",
            "body": "Hey! Want to grab coffee Saturday morning? Haven't seen you in forever!\n\nCheers,\nFriend",
            "date": "2024-01-16 14:30:00",
            "expected_category": "Personal > Friends",
            "expected_tone": "casual",
            "expected_formality": "low"
        },
        # Add more emails here...
    ]

    # Format emails
    formatted_emails = import_from_python_list(my_emails)

    # Anonymize if needed
    formatted_emails = [anonymize_email(email) for email in formatted_emails]

    # Upload to LangSmith
    upload_to_langsmith(
        formatted_emails,
        dataset_name="my-custom-email-dataset",
        description="My personal email examples for testing"
    )


def main():
    """Main function"""
    print("=" * 80)
    print("Import Your Emails to LangSmith")
    print("=" * 80)

    # Check API key
    if not LANGSMITH_API_KEY:
        print("\n❌ ERROR: LANGSMITH_API_KEY not found")
        print("   Set it in your .env file")
        return

    print("\n🎯 Choose import method:")
    print("1. From JSON file")
    print("2. From CSV file")
    print("3. From Python list (customize example_usage function)")
    print("4. Exit")

    choice = input("\nSelect (1-4): ").strip()

    if choice == "1":
        filepath = input("JSON file path: ").strip()
        if os.path.exists(filepath):
            emails = import_from_json(filepath)
            print(f"\n✅ Loaded {len(emails)} emails from JSON")

            # Ask about anonymization
            anonymize = input("Anonymize sensitive data? (y/n): ").strip().lower() == "y"
            if anonymize:
                emails = [anonymize_email(email) for email in emails]
                print("✅ Anonymized emails")

            upload_to_langsmith(emails)
        else:
            print(f"❌ File not found: {filepath}")

    elif choice == "2":
        filepath = input("CSV file path: ").strip()
        if os.path.exists(filepath):
            emails = import_from_csv(filepath)
            print(f"\n✅ Loaded {len(emails)} emails from CSV")

            # Ask about anonymization
            anonymize = input("Anonymize sensitive data? (y/n): ").strip().lower() == "y"
            if anonymize:
                emails = [anonymize_email(email) for email in emails]
                print("✅ Anonymized emails")

            upload_to_langsmith(emails)
        else:
            print(f"❌ File not found: {filepath}")

    elif choice == "3":
        print("\n💡 Customize the example_usage() function with your emails")
        print("   Then run this script again or call example_usage() directly")

    else:
        print("Goodbye!")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
