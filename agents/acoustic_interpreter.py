def interpret_score(score):
    if score is None:
        return "not available"
    if score >= 0.75:
        return "strong"
    if score >= 0.55:
        return "good"
    if score >= 0.40:
        return "moderate"
    return "needs improvement"


def interpret_acoustic_features(acoustic_features):
    """
    Converts raw acoustic numbers into simple human-readable evidence.
    The agent still does not listen to audio. It only uses these interpreted points.
    """

    evidence = []

    speaking_rate = acoustic_features.get("speaking_rate_wpm")
    pause_ratio = acoustic_features.get("pause_ratio")
    long_pause_count = acoustic_features.get("long_pause_count")
    pitch_variation = acoustic_features.get("pitch_variation")
    mean_energy = acoustic_features.get("mean_energy")

    if speaking_rate is not None:
        if speaking_rate < 100:
            evidence.append(
                f"Speaking rate is {speaking_rate:.0f} WPM, which is slow and may reduce delivery energy."
            )
        elif speaking_rate <= 170:
            evidence.append(
                f"Speaking rate is {speaking_rate:.0f} WPM, which is within a normal conversational range."
            )
        else:
            evidence.append(
                f"Speaking rate is {speaking_rate:.0f} WPM, which is fast and may sound rushed."
            )

    if pause_ratio is not None:
        if pause_ratio < 0.15:
            evidence.append(
                f"Pause ratio is {pause_ratio:.2f}, which suggests smooth delivery."
            )
        elif pause_ratio <= 0.30:
            evidence.append(
                f"Pause ratio is {pause_ratio:.2f}, which suggests moderate pauses."
            )
        else:
            evidence.append(
                f"Pause ratio is {pause_ratio:.2f}, which suggests noticeable hesitation."
            )

    if long_pause_count is not None:
        if long_pause_count == 0:
            evidence.append("No long pauses were detected.")
        elif long_pause_count <= 2:
            evidence.append(
                f"{long_pause_count} long pause(s) were detected, suggesting minor hesitation."
            )
        else:
            evidence.append(
                f"{long_pause_count} long pauses were detected, suggesting possible planning gaps."
            )

    if pitch_variation is not None:
        if pitch_variation < 15:
            evidence.append(
                f"Pitch variation is {pitch_variation:.1f}, which may indicate flat delivery."
            )
        elif pitch_variation <= 45:
            evidence.append(
                f"Pitch variation is {pitch_variation:.1f}, which suggests moderate expressiveness."
            )
        else:
            evidence.append(
                f"Pitch variation is {pitch_variation:.1f}, which suggests high vocal variation."
            )

    if mean_energy is not None:
        if mean_energy < 0.015:
            evidence.append(
                f"Mean energy is {mean_energy:.3f}, which may indicate low delivery energy."
            )
        elif mean_energy <= 0.060:
            evidence.append(
                f"Mean energy is {mean_energy:.3f}, which suggests acceptable delivery energy."
            )
        else:
            evidence.append(
                f"Mean energy is {mean_energy:.3f}, which suggests high delivery energy."
            )

    return evidence


def build_interpreted_evidence(model_output):
    predictions = model_output.get("predictions", {})
    acoustic_features = model_output.get("acoustic_features", {})

    score_evidence = {
        "speaking_skills": interpret_score(predictions.get("speaking_skills")),
        "confidence_score": interpret_score(predictions.get("confidence_score")),
        "interview_score": interpret_score(predictions.get("interview_score")),
        "overall_performance": interpret_score(predictions.get("overall_performance")),
        "answer_score": interpret_score(predictions.get("answer_score")),
    }

    acoustic_evidence = interpret_acoustic_features(acoustic_features)

    return {
        "score_evidence": score_evidence,
        "acoustic_evidence": acoustic_evidence
    }