"""
Evaluate Email AI Agent using LangSmith
Runs agent against dataset and calculates metrics
"""

import os
import sys
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate

# Add parent directory to path to import agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# LangSmith configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "email-ai-agent")
DATASET_NAME = "email-agent-evaluation-v1"


# ============================================================================
# AGENT TARGET FUNCTION
# ============================================================================

async def classify_and_analyze_email_async(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run agent to classify email and analyze patterns
    This is the async version that will be wrapped

    Args:
        inputs: Dictionary with email_id, from, subject, body, date, has_attachments

    Returns:
        Dictionary with agent's outputs: category, tone, formality, confidence
    """
    # Import here to avoid circular imports
    from agent import create_email_agent
    from langchain_core.messages import HumanMessage

    # Create agent
    agent = await create_email_agent()

    # Construct prompt for categorization
    email_prompt = f"""
    Please classify this email and analyze its characteristics:

    From: {inputs['from']}
    Subject: {inputs['subject']}
    Body:
    {inputs['body']}

    Please provide:
    1. The category this email belongs to (use existing categories if available, or suggest a new one)
    2. The tone (formal, professional, casual, friendly, warm, urgent)
    3. The formality level (high, medium, low)
    4. Your confidence in this classification (0.0 to 1.0)
    5. Whether this email requires a response (yes/no)

    Format your response as:
    Category: [category > subcategory]
    Tone: [tone]
    Formality: [formality]
    Confidence: [0.0-1.0]
    Requires Response: [yes/no]
    Reasoning: [brief explanation]
    """

    # Invoke agent
    try:
        result = agent.invoke({
            "messages": [HumanMessage(content=email_prompt)]
        })

        # Extract response
        response = result["messages"][-1].content

        # Parse response (simple parsing - in production would use structured output)
        parsed = _parse_classification_response(response)

        return parsed

    except Exception as e:
        print(f"Error processing email {inputs.get('email_id')}: {e}")
        return {
            "category": "Error",
            "tone": "unknown",
            "formality": "unknown",
            "confidence": 0.0,
            "requires_response": False,
            "error": str(e)
        }


def classify_and_analyze_email(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for the async agent function
    LangSmith evaluate() requires sync functions

    Args:
        inputs: Dictionary with email data

    Returns:
        Dictionary with classification results
    """
    return asyncio.run(classify_and_analyze_email_async(inputs))


def _parse_classification_response(response: str) -> Dict[str, Any]:
    """
    Parse agent's text response into structured output

    Args:
        response: Agent's text response

    Returns:
        Structured dictionary
    """
    lines = response.split("\n")
    parsed = {
        "category": "Unknown",
        "tone": "unknown",
        "formality": "unknown",
        "confidence": 0.5,
        "requires_response": False,
        "raw_response": response
    }

    for line in lines:
        line = line.strip()
        if line.startswith("Category:"):
            parsed["category"] = line.split(":", 1)[1].strip()
        elif line.startswith("Tone:"):
            parsed["tone"] = line.split(":", 1)[1].strip().lower()
        elif line.startswith("Formality:"):
            parsed["formality"] = line.split(":", 1)[1].strip().lower()
        elif line.startswith("Confidence:"):
            try:
                conf_str = line.split(":", 1)[1].strip()
                parsed["confidence"] = float(conf_str)
            except:
                parsed["confidence"] = 0.5
        elif line.startswith("Requires Response:"):
            response_needed = line.split(":", 1)[1].strip().lower()
            parsed["requires_response"] = response_needed in ["yes", "true"]

    return parsed


# ============================================================================
# CUSTOM EVALUATORS
# ============================================================================

def category_accuracy_evaluator(run, example) -> dict:
    """
    Evaluate if predicted category matches expected category

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    predicted = run.outputs.get("category", "").lower().strip()
    expected = example.outputs.get("expected_category", "").lower().strip()

    # Exact match
    if predicted == expected:
        return {
            "key": "category_accuracy",
            "score": 1.0,
            "comment": f"✅ Correct: {expected}"
        }

    # Partial match (e.g., got parent category right but not subcategory)
    if expected in predicted or predicted in expected:
        return {
            "key": "category_accuracy",
            "score": 0.5,
            "comment": f"⚠️  Partial match\nExpected: {expected}\nGot: {predicted}"
        }

    # No match
    return {
        "key": "category_accuracy",
        "score": 0.0,
        "comment": f"❌ Incorrect\nExpected: {expected}\nGot: {predicted}"
    }


def tone_match_evaluator(run, example) -> dict:
    """
    Evaluate if predicted tone matches expected tone

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    predicted = run.outputs.get("tone", "").lower().strip()
    expected = example.outputs.get("expected_tone", "").lower().strip()

    # Define tone synonyms
    tone_groups = {
        "formal": ["formal", "professional"],
        "casual": ["casual", "informal"],
        "friendly": ["friendly", "warm", "casual"],
        "urgent": ["urgent", "pressing", "important"]
    }

    # Check if tones are in same group
    predicted_group = next((k for k, v in tone_groups.items() if predicted in v), predicted)
    expected_group = next((k for k, v in tone_groups.items() if expected in v), expected)

    if predicted == expected or predicted_group == expected_group:
        return {
            "key": "tone_match",
            "score": 1.0,
            "comment": f"✅ Correct tone: {expected}"
        }
    else:
        return {
            "key": "tone_match",
            "score": 0.0,
            "comment": f"❌ Tone mismatch\nExpected: {expected}\nGot: {predicted}"
        }


def formality_match_evaluator(run, example) -> dict:
    """
    Evaluate if predicted formality matches expected formality

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    predicted = run.outputs.get("formality", "").lower().strip()
    expected = example.outputs.get("expected_formality", "").lower().strip()

    if predicted == expected:
        return {
            "key": "formality_match",
            "score": 1.0,
            "comment": f"✅ Correct formality: {expected}"
        }
    else:
        # Partial credit if off by one level (high/medium/low)
        formality_levels = ["low", "medium", "high"]
        try:
            pred_idx = formality_levels.index(predicted)
            exp_idx = formality_levels.index(expected)
            distance = abs(pred_idx - exp_idx)

            if distance == 1:
                return {
                    "key": "formality_match",
                    "score": 0.5,
                    "comment": f"⚠️  Close\nExpected: {expected}\nGot: {predicted}"
                }
        except:
            pass

        return {
            "key": "formality_match",
            "score": 0.0,
            "comment": f"❌ Formality mismatch\nExpected: {expected}\nGot: {predicted}"
        }


def confidence_threshold_evaluator(run, example) -> dict:
    """
    Evaluate if agent's confidence is appropriate
    High confidence should correlate with correct predictions

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    confidence = run.outputs.get("confidence", 0.5)
    category_correct = run.outputs.get("category", "").lower() == example.outputs.get("expected_category", "").lower()

    # High confidence + correct = good
    if confidence >= 0.8 and category_correct:
        return {
            "key": "confidence_calibration",
            "score": 1.0,
            "comment": f"✅ High confidence ({confidence:.2f}) and correct"
        }

    # Low confidence + incorrect = acceptable
    if confidence < 0.6 and not category_correct:
        return {
            "key": "confidence_calibration",
            "score": 0.75,
            "comment": f"⚠️  Low confidence ({confidence:.2f}) but incorrect - at least agent knew it was uncertain"
        }

    # High confidence + incorrect = bad
    if confidence >= 0.8 and not category_correct:
        return {
            "key": "confidence_calibration",
            "score": 0.0,
            "comment": f"❌ Overconfident ({confidence:.2f}) but incorrect"
        }

    # Medium confidence
    return {
        "key": "confidence_calibration",
        "score": 0.5,
        "comment": f"⚠️  Medium confidence ({confidence:.2f})"
    }


# ============================================================================
# EVALUATION RUNNER
# ============================================================================

def run_evaluation(dataset_name: str = DATASET_NAME, max_concurrency: int = 5):
    """
    Run evaluation on the dataset

    Args:
        dataset_name: Name of the dataset in LangSmith
        max_concurrency: Maximum number of concurrent evaluations
    """
    print("=" * 80)
    print("Email AI Agent Evaluation")
    print("=" * 80)

    # Check API key
    if not LANGSMITH_API_KEY:
        print("\n❌ ERROR: LANGSMITH_API_KEY not found in environment")
        return

    client = Client(api_key=LANGSMITH_API_KEY)

    # Verify dataset exists
    print(f"\n🔍 Checking dataset '{dataset_name}'...")
    try:
        datasets = list(client.list_datasets())
        dataset = next((ds for ds in datasets if ds.name == dataset_name), None)

        if not dataset:
            print(f"❌ Dataset '{dataset_name}' not found")
            print("\n💡 Create dataset first:")
            print("   python evaluations/create_dataset.py")
            return

        examples = list(client.list_examples(dataset_id=dataset.id))
        print(f"✅ Found dataset with {len(examples)} examples")

    except Exception as e:
        print(f"❌ Error accessing dataset: {e}")
        return

    # Run evaluation
    print(f"\n🚀 Starting evaluation...")
    print(f"   Max concurrency: {max_concurrency}")
    print(f"   This may take several minutes...\n")

    try:
        results = evaluate(
            classify_and_analyze_email,
            data=dataset_name,
            evaluators=[
                category_accuracy_evaluator,
                tone_match_evaluator,
                formality_match_evaluator,
                confidence_threshold_evaluator
            ],
            experiment_prefix="email-agent",
            max_concurrency=max_concurrency,
            client=client
        )

        print("\n✅ Evaluation complete!")
        print("\n📊 Results Summary:")
        print("=" * 80)

        # Show aggregate results
        if hasattr(results, 'aggregate'):
            for key, value in results.aggregate.items():
                print(f"   {key}: {value}")

        print("\n🔗 View full results in LangSmith:")
        print("   https://smith.langchain.com/")
        print(f"   Project: {LANGSMITH_PROJECT}")

    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main function"""
    print("Starting evaluation...\n")

    # Run evaluation
    run_evaluation(
        dataset_name=DATASET_NAME,
        max_concurrency=5  # Adjust based on your rate limits
    )

    print("\n" + "=" * 80)
    print("🎉 Evaluation complete!")
    print("=" * 80)
    print("\n💡 Next steps:")
    print("   1. View results in LangSmith UI")
    print("   2. Analyze failed cases")
    print("   3. Update system prompt based on insights")
    print("   4. Re-run evaluation to compare improvements")


if __name__ == "__main__":
    main()
