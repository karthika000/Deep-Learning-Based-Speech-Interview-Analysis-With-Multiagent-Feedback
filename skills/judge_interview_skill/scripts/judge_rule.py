def interpret_score(score: float | None) -> str:
    if score is None:
        return "not available"

    if score >= 0.75:
        return "strong"
    if score >= 0.55:
        return "good"
    if score >= 0.40:
        return "moderate"
    return "needs improvement"


def summarize_judge_scores(predictions: dict) -> dict:
    return {
        "speaking_skills": interpret_score(predictions.get("speaking_skills")),
        "confidence_score": interpret_score(predictions.get("confidence_score")),
        "interview_score": interpret_score(predictions.get("interview_score")),
        "overall_performance": interpret_score(predictions.get("overall_performance")),
        "answer_score": interpret_score(predictions.get("answer_score")),
    }