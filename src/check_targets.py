from pathlib import Path

import pandas as pd


POSSIBLE_TARGET_KEYWORDS = [
    "score",
    "skill",
    "confidence",
    "performance",
    "personality",
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "neuroticism",
    "facial",
    "answer",
    "interview",
]


def main():
    metadata_path = Path("data/processed/metadata_audio.csv")

    if not metadata_path.exists():
        raise FileNotFoundError(
            "data/processed/metadata_audio.csv not found. Run src/extract_audio.py first."
        )

    df = pd.read_csv(metadata_path)

    print("All columns:\n")
    for col in df.columns:
        print("-", col)

    print("\nPossible target columns:\n")
    for col in df.columns:
        lower_col = col.lower()
        if any(keyword in lower_col for keyword in POSSIBLE_TARGET_KEYWORDS):
            print("-", col)

    print("\nRecommended audio-only target candidates:")
    for candidate in [
        "speaking_skills",
        "confidence_score",
        "answer_score",
        "interview_score",
        "overall_performance",
    ]:
        matches = [col for col in df.columns if col.lower() == candidate.lower()]
        if matches:
            print("-", matches[0])


if __name__ == "__main__":
    main()