"""
Response Quality Evaluator
Evaluates the quality of generated draft responses
"""

from typing import Dict, Any


def response_quality_evaluator(run, example) -> Dict[str, Any]:
    """
    Evaluate overall quality of draft response
    Checks tone, formality, and appropriateness

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    # Get outputs
    predicted_tone = run.outputs.get("tone", "").lower().strip()
    expected_tone = example.outputs.get("expected_tone", "").lower().strip()

    predicted_formality = run.outputs.get("formality", "").lower().strip()
    expected_formality = example.outputs.get("expected_formality", "").lower().strip()

    predicted_requires_response = run.outputs.get("requires_response", False)
    expected_requires_response = example.outputs.get("requires_response", False)

    # Calculate individual scores
    tone_score = _calculate_tone_score(predicted_tone, expected_tone)
    formality_score = _calculate_formality_score(predicted_formality, expected_formality)
    response_needed_score = 1.0 if predicted_requires_response == expected_requires_response else 0.0

    # Overall score (weighted average)
    overall_score = (tone_score * 0.4 + formality_score * 0.4 + response_needed_score * 0.2)

    # Generate feedback
    feedback_parts = []

    if tone_score == 1.0:
        feedback_parts.append(f"✅ Tone correct: {expected_tone}")
    else:
        feedback_parts.append(f"❌ Tone mismatch: expected '{expected_tone}', got '{predicted_tone}'")

    if formality_score == 1.0:
        feedback_parts.append(f"✅ Formality correct: {expected_formality}")
    else:
        feedback_parts.append(f"❌ Formality mismatch: expected '{expected_formality}', got '{predicted_formality}'")

    if response_needed_score == 1.0:
        feedback_parts.append(f"✅ Response requirement correct")
    else:
        feedback_parts.append(f"❌ Response requirement wrong: expected {expected_requires_response}, got {predicted_requires_response}")

    comment = "\n".join(feedback_parts)
    comment += f"\n\nOverall Score: {overall_score:.2f}/1.00"

    return {
        "key": "response_quality",
        "score": overall_score,
        "comment": comment
    }


def _calculate_tone_score(predicted: str, expected: str) -> float:
    """Calculate tone match score"""
    # Define tone groups with synonyms
    tone_groups = {
        "formal": ["formal", "professional", "polished"],
        "casual": ["casual", "informal", "relaxed"],
        "friendly": ["friendly", "warm", "welcoming"],
        "urgent": ["urgent", "pressing", "important", "critical"]
    }

    # Get groups
    predicted_group = next((k for k, v in tone_groups.items() if predicted in v), predicted)
    expected_group = next((k for k, v in tone_groups.items() if expected in v), expected)

    # Exact match or same group
    if predicted == expected or predicted_group == expected_group:
        return 1.0

    # Related tones (e.g., formal and professional)
    related_pairs = [
        ("formal", "casual"),
        ("friendly", "warm"),
        ("urgent", "important")
    ]

    for pair in related_pairs:
        if (predicted in pair and expected in pair):
            return 0.7

    return 0.0


def _calculate_formality_score(predicted: str, expected: str) -> float:
    """Calculate formality match score"""
    formality_levels = ["low", "medium", "high"]

    if predicted == expected:
        return 1.0

    # Partial credit if off by one level
    try:
        pred_idx = formality_levels.index(predicted)
        exp_idx = formality_levels.index(expected)
        distance = abs(pred_idx - exp_idx)

        if distance == 1:
            return 0.5
        elif distance == 2:
            return 0.0
    except ValueError:
        pass

    return 0.0


def draft_appropriateness_evaluator(run, example) -> Dict[str, Any]:
    """
    Evaluate if response is appropriate for the email type

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    category = example.outputs.get("expected_category", "").lower()
    tone = run.outputs.get("tone", "").lower()
    formality = run.outputs.get("formality", "").lower()

    # Define appropriate tone/formality combinations for categories
    appropriateness_rules = {
        "work": {
            "acceptable_tones": ["professional", "formal", "polite"],
            "acceptable_formality": ["high", "medium"],
            "min_formality": "medium"
        },
        "hockey": {
            "acceptable_tones": ["casual", "friendly", "warm"],
            "acceptable_formality": ["low", "medium"],
            "max_formality": "medium"
        },
        "personal": {
            "acceptable_tones": ["casual", "friendly", "warm"],
            "acceptable_formality": ["low", "medium"],
            "max_formality": "medium"
        },
        "finance": {
            "acceptable_tones": ["formal", "professional"],
            "acceptable_formality": ["high"],
            "min_formality": "high"
        },
        "organizational": {
            "acceptable_tones": ["formal", "professional"],
            "acceptable_formality": ["high"],
            "min_formality": "high"
        }
    }

    # Get parent category
    parent_category = category.split(">")[0].strip() if ">" in category else category

    # Check appropriateness
    if parent_category in appropriateness_rules:
        rules = appropriateness_rules[parent_category]

        # Check tone
        tone_appropriate = any(acceptable in tone for acceptable in rules["acceptable_tones"])

        # Check formality
        formality_appropriate = formality in rules["acceptable_formality"]

        if tone_appropriate and formality_appropriate:
            return {
                "key": "draft_appropriateness",
                "score": 1.0,
                "comment": f"✅ Appropriate tone ({tone}) and formality ({formality}) for {parent_category} emails"
            }
        elif tone_appropriate or formality_appropriate:
            return {
                "key": "draft_appropriateness",
                "score": 0.5,
                "comment": f"⚠️  Partially appropriate for {parent_category}\nTone: {tone}, Formality: {formality}"
            }
        else:
            return {
                "key": "draft_appropriateness",
                "score": 0.0,
                "comment": f"❌ Inappropriate tone/formality for {parent_category}\nGot: {tone}/{formality}\nExpected: {rules['acceptable_tones']}/{rules['acceptable_formality']}"
            }

    # Unknown category - can't evaluate
    return {
        "key": "draft_appropriateness",
        "score": 0.5,
        "comment": f"⚠️  Unable to evaluate appropriateness for category: {parent_category}"
    }
