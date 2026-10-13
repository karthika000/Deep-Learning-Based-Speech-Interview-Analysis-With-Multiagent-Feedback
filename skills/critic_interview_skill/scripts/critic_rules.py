def detect_delivery_risks(acoustic_features: dict, predictions: dict) -> list[str]:
    risks = []

    confidence = predictions.get("confidence_score")
    speaking = predictions.get("speaking_skills")
    pause_ratio = acoustic_features.get("pause_ratio")
    long_pauses = acoustic_features.get("long_pause_count")
    wpm = acoustic_features.get("speaking_rate_wpm")

    if confidence is not None and confidence < 0.55:
        risks.append("Predicted confidence score is below the good range.")

    if speaking is not None and speaking < 0.55:
        risks.append("Predicted speaking skills score is below the good range.")

    if pause_ratio is not None and pause_ratio > 0.30:
        risks.append("Pause ratio is high and may indicate hesitation.")

    if long_pauses is not None and long_pauses >= 3:
        risks.append("Several long pauses were detected.")

    if wpm is not None and wpm > 170:
        risks.append("Speaking rate is fast and may sound rushed.")

    if wpm is not None and wpm < 100:
        risks.append("Speaking rate is slow and may reduce energy.")

    return risks