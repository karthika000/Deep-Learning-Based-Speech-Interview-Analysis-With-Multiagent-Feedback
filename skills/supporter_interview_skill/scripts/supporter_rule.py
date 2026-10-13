def detect_strengths(acoustic_features: dict, predictions: dict, transcript: str) -> list[str]:
    strengths = []

    speaking = predictions.get("speaking_skills")
    confidence = predictions.get("confidence_score")
    interview = predictions.get("interview_score")
    wpm = acoustic_features.get("speaking_rate_wpm")
    pause_ratio = acoustic_features.get("pause_ratio")

    if speaking is not None and speaking >= 0.55:
        strengths.append("Predicted speaking skills are in the good range.")

    if confidence is not None and confidence >= 0.55:
        strengths.append("Predicted confidence score is in the good range.")
    elif confidence is not None and confidence >= 0.40:
        strengths.append("Predicted confidence score is moderate and can be improved with practice.")

    if interview is not None and interview >= 0.55:
        strengths.append("Predicted interview score indicates useful interview delivery.")

    if wpm is not None and 100 <= wpm <= 170:
        strengths.append("Speaking rate is within a normal conversational range.")

    if pause_ratio is not None and pause_ratio <= 0.30:
        strengths.append("Pause ratio is acceptable and does not indicate severe disfluency.")

    if transcript and len(transcript.split()) > 25:
        strengths.append("Transcript contains enough content for meaningful feedback.")

    return strengths