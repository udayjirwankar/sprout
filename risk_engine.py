def determine_risk(prediction, confidence):
    """
    Convert the model's classification output into a
    prototype wellbeing signal.

    IMPORTANT:
    These are prototype thresholds, not clinical thresholds.
    """

    # High-risk signal is only generated when the model strongly
    # predicts the Suicidal class.
    if prediction == "Suicidal" and confidence >= 0.70:
        return {
            "risk_level": "HIGH",
            "signal_summary": "Potential high-risk distress signal detected"
        }

    # Elevated signal for strong distress-related predictions.
    if prediction in ["Suicidal", "Depression", "Anxiety"] and confidence >= 0.60:
        return {
            "risk_level": "ELEVATED",
            "signal_summary": "Potential distress signal detected"
        }

    # Otherwise, no escalation signal.
    return {
        "risk_level": "LOW",
        "signal_summary": "No significant escalation signal detected"
    }