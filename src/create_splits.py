from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]

METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "metadata_audio.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "splits"


def validate_audio_paths(df):
    """
    Keep only rows where audio_path exists on disk.
    audio_path is expected to be relative to project root, for example:
    data/processed/audio_wav/vid_0004.wav
    """

    valid_rows = []
    missing_paths = []

    for _, row in df.iterrows():
        audio_path = row.get("audio_path")

        if pd.isna(audio_path) or str(audio_path).strip() == "":
            valid_rows.append(False)
            missing_paths.append("empty audio_path")
            continue

        full_audio_path = PROJECT_ROOT / str(audio_path)

        if full_audio_path.exists():
            valid_rows.append(True)
        else:
            valid_rows.append(False)
            missing_paths.append(str(audio_path))

    cleaned_df = df[valid_rows].copy()

    print(f"Rows before audio validation: {len(df)}")
    print(f"Rows after audio validation:  {len(cleaned_df)}")
    print(f"Rows removed:                 {len(df) - len(cleaned_df)}")

    if missing_paths:
        print("\nFirst missing audio paths:")
        for path in missing_paths[:10]:
            print(f"  - {path}")

    return cleaned_df


def check_user_leakage(train_df, val_df, test_df):
    train_users = set(train_df["user_no"].dropna().unique())
    val_users = set(val_df["user_no"].dropna().unique())
    test_users = set(test_df["user_no"].dropna().unique())

    train_val_overlap = train_users.intersection(val_users)
    train_test_overlap = train_users.intersection(test_users)
    val_test_overlap = val_users.intersection(test_users)

    if train_val_overlap or train_test_overlap or val_test_overlap:
        raise ValueError(
            "User leakage detected between splits. "
            "The same user appears in more than one split."
        )

    print("\nUser leakage check passed.")
    print("No user appears in more than one split.")


def main():
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"{METADATA_PATH} not found. Run src/extract_audio.py first, "
            "then run src/fix_metadata_audio_paths.py."
        )

    df = pd.read_csv(METADATA_PATH)

    required_columns = [
        "user_no",
        "audio_path",
        "speaking_skills",
        "confidence_score",
        "interview_score",
        "overall_performance",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise KeyError(
            f"Missing required columns: {missing_columns}\n"
            f"Available columns: {list(df.columns)}"
        )

    df = validate_audio_paths(df)

    users = df["user_no"].dropna().unique()

    if len(users) < 3:
        raise ValueError(
            "Not enough unique users to create train/val/test splits."
        )

    train_users, temp_users = train_test_split(
        users,
        test_size=0.30,
        random_state=42,
    )

    val_users, test_users = train_test_split(
        temp_users,
        test_size=0.50,
        random_state=42,
    )

    train_df = df[df["user_no"].isin(train_users)].copy()
    val_df = df[df["user_no"].isin(val_users)].copy()
    test_df = df[df["user_no"].isin(test_users)].copy()

    check_user_leakage(train_df, val_df, test_df)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(OUTPUT_DIR / "train.csv", index=False)
    val_df.to_csv(OUTPUT_DIR / "val.csv", index=False)
    test_df.to_csv(OUTPUT_DIR / "test.csv", index=False)

    print("\nUser-independent splits created.")
    print(f"Train: {len(train_df)} samples from {len(train_users)} users")
    print(f"Val:   {len(val_df)} samples from {len(val_users)} users")
    print(f"Test:  {len(test_df)} samples from {len(test_users)} users")
    print(f"Saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()