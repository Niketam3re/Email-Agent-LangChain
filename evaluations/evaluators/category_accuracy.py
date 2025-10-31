"""
Category Accuracy Evaluator
Evaluates if the agent correctly categorizes emails
"""

from typing import Dict, Any


def category_accuracy_evaluator(run, example) -> Dict[str, Any]:
    """
    Evaluate if predicted category matches expected category

    Scoring:
    - 1.0: Exact match
    - 0.5: Partial match (parent category correct)
    - 0.0: No match

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    predicted = run.outputs.get("category", "Unknown").lower().strip()
    expected = example.outputs.get("expected_category", "").lower().strip()

    # Handle case where agent returns hierarchical category
    predicted_parts = predicted.split(">")
    expected_parts = expected.split(">")

    predicted_parent = predicted_parts[0].strip() if predicted_parts else predicted
    expected_parent = expected_parts[0].strip() if expected_parts else expected

    # Exact match
    if predicted == expected:
        return {
            "key": "category_accuracy",
            "score": 1.0,
            "comment": f"✅ Perfect match: '{expected}'"
        }

    # Parent category match
    if predicted_parent == expected_parent:
        return {
            "key": "category_accuracy",
            "score": 0.7,
            "comment": f"⚠️  Parent category correct\nExpected: '{expected}'\nGot: '{predicted}'"
        }

    # Fuzzy match (one contains the other)
    if expected in predicted or predicted in expected:
        return {
            "key": "category_accuracy",
            "score": 0.5,
            "comment": f"⚠️  Partial match\nExpected: '{expected}'\nGot: '{predicted}'"
        }

    # No match
    return {
        "key": "category_accuracy",
        "score": 0.0,
        "comment": f"❌ Incorrect category\nExpected: '{expected}'\nGot: '{predicted}'"
    }


def hierarchical_category_evaluator(run, example) -> Dict[str, Any]:
    """
    Evaluate hierarchical category structure separately
    Checks if subcategory is appropriate even if parent is wrong

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    predicted = run.outputs.get("category", "Unknown").lower().strip()
    expected = example.outputs.get("expected_category", "").lower().strip()

    predicted_parts = predicted.split(">")
    expected_parts = expected.split(">")

    # Both are hierarchical
    if len(predicted_parts) > 1 and len(expected_parts) > 1:
        predicted_parent = predicted_parts[0].strip()
        predicted_child = predicted_parts[1].strip()
        expected_parent = expected_parts[0].strip()
        expected_child = expected_parts[1].strip()

        if predicted_parent == expected_parent and predicted_child == expected_child:
            return {
                "key": "hierarchical_accuracy",
                "score": 1.0,
                "comment": "✅ Perfect hierarchical match"
            }
        elif predicted_parent == expected_parent:
            return {
                "key": "hierarchical_accuracy",
                "score": 0.7,
                "comment": f"⚠️  Parent correct, subcategory wrong\nExpected child: '{expected_child}'\nGot: '{predicted_child}'"
            }
        elif predicted_child == expected_child:
            return {
                "key": "hierarchical_accuracy",
                "score": 0.5,
                "comment": f"⚠️  Subcategory correct, parent wrong\nExpected parent: '{expected_parent}'\nGot: '{predicted_parent}'"
            }

    # Expected hierarchical but got flat
    if len(expected_parts) > 1 and len(predicted_parts) == 1:
        return {
            "key": "hierarchical_accuracy",
            "score": 0.3,
            "comment": f"⚠️  Expected hierarchical category, got flat\nExpected: '{expected}'\nGot: '{predicted}'"
        }

    # Both flat
    if len(predicted_parts) == 1 and len(expected_parts) == 1:
        if predicted == expected:
            return {
                "key": "hierarchical_accuracy",
                "score": 1.0,
                "comment": "✅ Correct flat category"
            }

    return {
        "key": "hierarchical_accuracy",
        "score": 0.0,
        "comment": f"❌ Category structure mismatch\nExpected: '{expected}'\nGot: '{predicted}'"
    }
