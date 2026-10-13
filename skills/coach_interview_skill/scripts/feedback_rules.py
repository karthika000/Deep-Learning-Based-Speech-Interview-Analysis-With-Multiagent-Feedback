def build_next_practice_task(predictions: dict, acoustic_features: dict) -> str:
    confidence = predictions.get("confidence_score")
    pause_ratio = acoustic_features.get("pause_ratio")
    wpm = acoustic_features.get("speaking_rate_wpm")

    if pause_ratio is not None and pause_ratio > 0.30:
        return (
            "Practice answering the same question in 60 seconds while reducing long pauses. "
            "Prepare three key points before speaking."
        )

    if wpm is not None and wpm > 170:
        return (
            "Practice the answer again at a slower pace. Aim for a speaking rate between "
            "120 and 160 words per minute."
        )

    if confidence is not None and confidence < 0.55:
        return (
            "Practice the opening 20 seconds of the answer until it feels smooth and structured. "
            "Focus on a clear first sentence."
        )

    return (
        "Practice the same answer using the STAR method: Situation, Task, Action, and Result."
    )