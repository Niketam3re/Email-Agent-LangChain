"""
Create LangSmith Dataset from Sample Emails
Uploads generated sample emails to LangSmith for evaluation
"""

import json
import os
from typing import List, Dict, Any
from langsmith import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LangSmith configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "email-ai-agent")

# Dataset configuration
DATASET_NAME = "email-agent-evaluation-v1"
DATASET_DESCRIPTION = """
Email AI Agent Evaluation Dataset

This dataset contains 300 realistic sample emails across multiple categories:
- Work (120 emails): Project Alpha, Project Beta, Meetings
- Hockey (60 emails): Team A, Team B
- Personal (50 emails): Family, Friends
- Finance (30 emails)
- Shopping (30 emails)
- Organizational (30 emails)
- Travel (20 emails)

Each email includes:
- Inputs: email_id, from, subject, body, date, has_attachments
- Expected outputs: category, tone, formality, response_length, requires_response

Use this dataset to evaluate:
1. Categorization accuracy
2. Pattern detection
3. Draft response quality
4. Tone and formality matching
"""


def load_sample_emails(filepath: str = "sample_emails_dataset.json") -> List[Dict[str, Any]]:
    """
    Load sample emails from JSON file

    Args:
        filepath: Path to the JSON file with sample emails

    Returns:
        List of email dictionaries
    """
    # Try different possible paths
    possible_paths = [
        filepath,
        f"evaluations/{filepath}",
        f"../{filepath}"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)

    raise FileNotFoundError(
        f"Could not find {filepath}. Please run sample_emails_for_langsmith.py first."
    )


def create_langsmith_dataset(
    emails: List[Dict[str, Any]],
    dataset_name: str = DATASET_NAME,
    description: str = DATASET_DESCRIPTION
) -> None:
    """
    Create or update LangSmith dataset with sample emails

    Args:
        emails: List of email dictionaries with inputs/outputs
        dataset_name: Name of the dataset in LangSmith
        description: Description of the dataset
    """
    # Initialize LangSmith client
    client = Client(api_key=LANGSMITH_API_KEY)

    print(f"\n🔍 Checking if dataset '{dataset_name}' exists...")

    # Check if dataset already exists
    try:
        existing_datasets = list(client.list_datasets())
        dataset_exists = any(ds.name == dataset_name for ds in existing_datasets)

        if dataset_exists:
            print(f"⚠️  Dataset '{dataset_name}' already exists")
            response = input("Do you want to delete and recreate it? (y/n): ")

            if response.lower() == "y":
                print(f"🗑️  Deleting existing dataset...")
                # Get dataset ID
                dataset_id = next(ds.id for ds in existing_datasets if ds.name == dataset_name)
                client.delete_dataset(dataset_id=dataset_id)
                print(f"✅ Deleted existing dataset")
            else:
                print("❌ Aborted. Dataset not updated.")
                return
    except Exception as e:
        print(f"⚠️  Could not check existing datasets: {e}")

    # Create new dataset
    print(f"\n📦 Creating dataset '{dataset_name}'...")

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description=description
    )

    print(f"✅ Created dataset with ID: {dataset.id}")

    # Upload examples
    print(f"\n📤 Uploading {len(emails)} examples...")

    for i, email in enumerate(emails, 1):
        try:
            client.create_example(
                dataset_id=dataset.id,
                inputs=email["inputs"],
                outputs=email["outputs"]
            )

            if i % 50 == 0:
                print(f"   Uploaded {i}/{len(emails)} examples...")

        except Exception as e:
            print(f"   ⚠️  Error uploading example {i}: {e}")
            continue

    print(f"\n✅ Successfully uploaded {len(emails)} examples to LangSmith!")
    print(f"\n🔗 View dataset at: https://smith.langchain.com/datasets")
    print(f"   Dataset name: {dataset_name}")
    print(f"   Dataset ID: {dataset.id}")


def verify_dataset(dataset_name: str = DATASET_NAME) -> None:
    """
    Verify dataset was created successfully and show statistics

    Args:
        dataset_name: Name of the dataset to verify
    """
    client = Client(api_key=LANGSMITH_API_KEY)

    print(f"\n🔍 Verifying dataset '{dataset_name}'...")

    try:
        # List datasets
        datasets = list(client.list_datasets())
        dataset = next((ds for ds in datasets if ds.name == dataset_name), None)

        if not dataset:
            print(f"❌ Dataset '{dataset_name}' not found")
            return

        print(f"✅ Dataset found: {dataset.name}")
        print(f"   ID: {dataset.id}")
        print(f"   Description: {dataset.description[:100]}...")

        # Get examples
        examples = list(client.list_examples(dataset_id=dataset.id))
        print(f"   Examples: {len(examples)}")

        # Show category distribution
        print(f"\n📊 Category Distribution:")
        category_counts = {}
        for example in examples:
            cat = example.outputs["expected_category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        for cat, count in sorted(category_counts.items()):
            print(f"   {cat}: {count}")

        # Show sample example
        if examples:
            sample = examples[0]
            print(f"\n📧 Sample Example:")
            print(f"   Email ID: {sample.inputs['email_id']}")
            print(f"   From: {sample.inputs['from']}")
            print(f"   Subject: {sample.inputs['subject']}")
            print(f"   Expected Category: {sample.outputs['expected_category']}")
            print(f"   Expected Tone: {sample.outputs['expected_tone']}")

    except Exception as e:
        print(f"❌ Error verifying dataset: {e}")


def main():
    """Main function to create dataset"""
    print("=" * 80)
    print("LangSmith Dataset Creation - Email AI Agent")
    print("=" * 80)

    # Check API key
    if not LANGSMITH_API_KEY:
        print("\n❌ ERROR: LANGSMITH_API_KEY not found in environment")
        print("   Please set it in your .env file:")
        print("   LANGSMITH_API_KEY=lsv2_pt_xxxxx")
        return

    # Load sample emails
    print("\n📧 Loading sample emails...")
    try:
        emails = load_sample_emails()
        print(f"✅ Loaded {len(emails)} sample emails")
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Please run this first:")
        print("   python evaluations/sample_emails_for_langsmith.py")
        return

    # Create dataset
    create_langsmith_dataset(emails)

    # Verify dataset
    verify_dataset()

    print("\n" + "=" * 80)
    print("🎉 Dataset creation complete!")
    print("=" * 80)
    print("\n💡 Next steps:")
    print("   1. View dataset at: https://smith.langchain.com/datasets")
    print("   2. Run evaluation: python evaluations/evaluate_agent.py")
    print("   3. Analyze results in LangSmith UI")


if __name__ == "__main__":
    main()
