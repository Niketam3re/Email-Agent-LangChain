"""
Pattern Detection Evaluator
Evaluates if the agent correctly identifies communication patterns
"""

from typing import Dict, Any


def pattern_detection_evaluator(run, example) -> Dict[str, Any]:
    """
    Evaluate if agent correctly identifies communication patterns

    Checks:
    - Confidence calibration
    - Tone detection
    - Formality detection
    - Response requirement detection

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    confidence = run.outputs.get("confidence", 0.5)
    category_predicted = run.outputs.get("category", "").lower()
    category_expected = example.outputs.get("expected_category", "").lower()

    tone_predicted = run.outputs.get("tone", "").lower()
    tone_expected = example.outputs.get("expected_tone", "").lower()

    formality_predicted = run.outputs.get("formality", "").lower()
    formality_expected = example.outputs.get("expected_formality", "").lower()

    # Calculate individual pattern detection scores
    category_correct = category_predicted == category_expected
    tone_correct = _tones_match(tone_predicted, tone_expected)
    formality_correct = formality_predicted == formality_expected

    patterns_detected = sum([category_correct, tone_correct, formality_correct])
    total_patterns = 3

    detection_score = patterns_detected / total_patterns

    # Evaluate confidence calibration
    confidence_appropriate = _evaluate_confidence(confidence, category_correct)

    # Overall score (weighted)
    overall_score = (detection_score * 0.7 + confidence_appropriate * 0.3)

    # Generate feedback
    feedback_lines = []
    feedback_lines.append(f"Pattern Detection: {patterns_detected}/{total_patterns}")

    if category_correct:
        feedback_lines.append("  ✅ Category pattern recognized")
    else:
        feedback_lines.append(f"  ❌ Category pattern missed (expected: {category_expected})")

    if tone_correct:
        feedback_lines.append("  ✅ Tone pattern recognized")
    else:
        feedback_lines.append(f"  ❌ Tone pattern missed (expected: {tone_expected})")

    if formality_correct:
        feedback_lines.append("  ✅ Formality pattern recognized")
    else:
        feedback_lines.append(f"  ❌ Formality pattern missed (expected: {formality_expected})")

    if confidence_appropriate > 0.7:
        feedback_lines.append(f"  ✅ Confidence well-calibrated ({confidence:.2f})")
    else:
        feedback_lines.append(f"  ⚠️  Confidence calibration issue ({confidence:.2f})")

    comment = "\n".join(feedback_lines)

    return {
        "key": "pattern_detection",
        "score": overall_score,
        "comment": comment
    }


def confidence_calibration_evaluator(run, example) -> Dict[str, Any]:
    """
    Evaluate if agent's confidence is well-calibrated

    Well-calibrated confidence means:
    - High confidence when correct
    - Low confidence when incorrect
    - Not overconfident

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    confidence = run.outputs.get("confidence", 0.5)
    category_predicted = run.outputs.get("category", "").lower()
    category_expected = example.outputs.get("expected_category", "").lower()

    category_correct = category_predicted == category_expected

    # Define calibration thresholds
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.6
    LOW_CONFIDENCE = 0.4

    # Evaluate calibration
    if confidence >= HIGH_CONFIDENCE and category_correct:
        # Perfect: High confidence + correct
        return {
            "key": "confidence_calibration",
            "score": 1.0,
            "comment": f"✅ Well-calibrated: High confidence ({confidence:.2f}) and correct prediction"
        }

    elif confidence >= HIGH_CONFIDENCE and not category_correct:
        # Bad: Overconfident
        return {
            "key": "confidence_calibration",
            "score": 0.0,
            "comment": f"❌ Overconfident: High confidence ({confidence:.2f}) but incorrect prediction"
        }

    elif confidence < MEDIUM_CONFIDENCE and not category_correct:
        # Good: Low confidence + incorrect (agent knew it was uncertain)
        return {
            "key": "confidence_calibration",
            "score": 0.8,
            "comment": f"✅ Well-calibrated: Low confidence ({confidence:.2f}) and incorrect - agent properly uncertain"
        }

    elif confidence < MEDIUM_CONFIDENCE and category_correct:
        # Suboptimal: Under-confident
        return {
            "key": "confidence_calibration",
            "score": 0.6,
            "comment": f"⚠️  Under-confident: Low confidence ({confidence:.2f}) but prediction was correct"
        }

    elif MEDIUM_CONFIDENCE <= confidence < HIGH_CONFIDENCE:
        # Acceptable: Medium confidence (reasonable in most cases)
        if category_correct:
            return {
                "key": "confidence_calibration",
                "score": 0.8,
                "comment": f"✅ Reasonable: Medium confidence ({confidence:.2f}) and correct"
            }
        else:
            return {
                "key": "confidence_calibration",
                "score": 0.5,
                "comment": f"⚠️  Medium confidence ({confidence:.2f}) but incorrect"
            }

    # Default
    return {
        "key": "confidence_calibration",
        "score": 0.5,
        "comment": f"⚠️  Confidence: {confidence:.2f}, Correct: {category_correct}"
    }


def consistency_evaluator(run, example) -> Dict[str, Any]:
    """
    Evaluate if agent's outputs are internally consistent

    Checks:
    - Category and tone consistency (e.g., Work should be professional)
    - Category and formality consistency
    - Tone and formality consistency

    Args:
        run: The run object with agent outputs
        example: The example from dataset with expected outputs

    Returns:
        Dictionary with score and feedback
    """
    category = run.outputs.get("category", "").lower()
    tone = run.outputs.get("tone", "").lower()
    formality = run.outputs.get("formality", "").lower()

    # Define expected consistencies
    consistency_rules = {
        "work": {
            "expected_tone": ["professional", "formal"],
            "expected_formality": ["high", "medium"]
        },
        "hockey": {
            "expected_tone": ["casual", "friendly"],
            "expected_formality": ["low", "medium"]
        },
        "personal": {
            "expected_tone": ["casual", "friendly", "warm"],
            "expected_formality": ["low", "medium"]
        },
        "finance": {
            "expected_tone": ["formal", "professional"],
            "expected_formality": ["high"]
        },
        "shopping": {
            "expected_tone": ["friendly", "casual"],
            "expected_formality": ["medium", "low"]
        },
        "organizational": {
            "expected_tone": ["formal", "professional"],
            "expected_formality": ["high"]
        }
    }

    # Get parent category
    parent_category = category.split(">")[0].strip() if ">" in category else category

    # Check consistency
    if parent_category in consistency_rules:
        rules = consistency_rules[parent_category]

        tone_consistent = any(expected in tone for expected in rules["expected_tone"])
        formality_consistent = formality in rules["expected_formality"]

        if tone_consistent and formality_consistent:
            return {
                "key": "internal_consistency",
                "score": 1.0,
                "comment": f"✅ Internally consistent: {parent_category} → {tone}/{formality}"
            }
        elif tone_consistent or formality_consistent:
            return {
                "key": "internal_consistency",
                "score": 0.5,
                "comment": f"⚠️  Partially consistent: {parent_category} → {tone}/{formality}"
            }
        else:
            return {
                "key": "internal_consistency",
                "score": 0.0,
                "comment": f"❌ Inconsistent: {parent_category} should not have {tone}/{formality}"
            }

    # Unknown category
    return {
        "key": "internal_consistency",
        "score": 0.5,
        "comment": f"⚠️  Cannot evaluate consistency for category: {parent_category}"
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _tones_match(predicted: str, expected: str) -> bool:
    """Check if tones match, accounting for synonyms"""
    if predicted == expected:
        return True

    tone_synonyms = {
        "formal": ["formal", "professional", "polished"],
        "casual": ["casual", "informal", "relaxed"],
        "friendly": ["friendly", "warm", "welcoming"],
        "urgent": ["urgent", "pressing", "important"]
    }

    for group in tone_synonyms.values():
        if predicted in group and expected in group:
            return True

    return False


def _evaluate_confidence(confidence: float, correct: bool) -> float:
    """Evaluate confidence appropriateness (0.0 to 1.0)"""
    if confidence >= 0.8 and correct:
        return 1.0  # Perfect
    elif confidence >= 0.8 and not correct:
        return 0.0  # Overconfident
    elif confidence < 0.6 and not correct:
        return 0.8  # Appropriately uncertain
    elif confidence < 0.6 and correct:
        return 0.6  # Under-confident
    else:
        return 0.7  # Medium confidence is generally acceptable
