from pathlib import Path

import librosa
import numpy as np
import pandas as pd

from config import (
    PROJECT_ROOT,
    SAMPLE_RATE,
    TRAIN_CSV,
    VAL_CSV,
    TEST_CSV,
    ACOUSTIC_FEATURES_CSV,
)


ACOUSTIC_COLUMNS = [
    "duration_sec",
    "energy_mean",
    "energy_std",
    "energy_max",
    "pause_ratio",
    "voiced_ratio",
    "pitch_mean",
    "pitch_std",
    "pitch_min",
    "pitch_max",
    "speaking_rate",
    "split",
    "audio_path",
    "id",
    "user_no",
]


def safe_mean(values):
    if values is None or len(values) == 0:
        return 0.0
    return float(np.nanmean(values))


def safe_std(values):
    if values is None or len(values) == 0:
        return 0.0
    return float(np.nanstd(values))


def resolve_audio_path(audio_path_value):
    if pd.isna(audio_path_value):
        return None

    audio_path_value = str(audio_path_value).strip()

    if audio_path_value == "":
        return None

    audio_path = Path(audio_path_value)

    if audio_path.is_absolute():
        return audio_path

    return PROJECT_ROOT / audio_path


def extract_features_from_audio(audio_path, transcript=None):
    y, sr = librosa.load(str(audio_path), sr=SAMPLE_RATE, mono=True)

    duration = librosa.get_duration(y=y, sr=sr)

    if duration <= 0:
        duration = 1e-6

    # Energy features
    rms = librosa.feature.rms(y=y)[0]

    energy_mean = safe_mean(rms)
    energy_std = safe_std(rms)
    energy_max = float(np.max(rms)) if len(rms) > 0 else 0.0

    # Silence / pause features
    non_silent_intervals = librosa.effects.split(y, top_db=30)

    voiced_duration = 0.0

    for start, end in non_silent_intervals:
        voiced_duration += (end - start) / sr

    silence_duration = max(duration - voiced_duration, 0.0)

    pause_ratio = silence_duration / duration
    voiced_ratio = voiced_duration / duration

    # Pitch features
    try:
        f0, voiced_flag, voiced_prob = librosa.pyin(
            y,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sr,
        )

        valid_pitch = f0[~np.isnan(f0)]

    except Exception:
        valid_pitch = np.array([])

    pitch_mean = safe_mean(valid_pitch)
    pitch_std = safe_std(valid_pitch)
    pitch_min = float(np.min(valid_pitch)) if len(valid_pitch) > 0 else 0.0
    pitch_max = float(np.max(valid_pitch)) if len(valid_pitch) > 0 else 0.0

    # Speaking rate
    if transcript is not None and isinstance(transcript, str) and transcript.strip() != "":
        word_count = len(transcript.split())
        speaking_rate = (word_count / duration) * 60.0
    else:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
        speaking_rate = (len(onsets) / duration) * 60.0

    return {
        "duration_sec": float(duration),
        "energy_mean": energy_mean,
        "energy_std": energy_std,
        "energy_max": energy_max,
        "pause_ratio": float(pause_ratio),
        "voiced_ratio": float(voiced_ratio),
        "pitch_mean": pitch_mean,
        "pitch_std": pitch_std,
        "pitch_min": pitch_min,
        "pitch_max": pitch_max,
        "speaking_rate": float(speaking_rate),
    }


def load_already_processed_paths():
    if not ACOUSTIC_FEATURES_CSV.exists():
        return set()

    existing_df = pd.read_csv(ACOUSTIC_FEATURES_CSV)

    if "audio_path" not in existing_df.columns:
        return set()

    processed_paths = set(existing_df["audio_path"].dropna().astype(str).tolist())

    print(f"Found existing acoustic feature file: {ACOUSTIC_FEATURES_CSV}")
    print(f"Already processed files: {len(processed_paths)}")

    return processed_paths


def append_features_to_csv(feature_rows):
    if not feature_rows:
        return

    ACOUSTIC_FEATURES_CSV.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(feature_rows)

    file_exists = ACOUSTIC_FEATURES_CSV.exists()

    df.to_csv(
        ACOUSTIC_FEATURES_CSV,
        mode="a",
        header=not file_exists,
        index=False,
    )


def process_split(split_csv_path, split_name, processed_paths, save_every=50):
    df = pd.read_csv(split_csv_path)

    print(f"\nProcessing {split_name} split")
    print(f"CSV: {split_csv_path}")
    print(f"Rows: {len(df)}")

    batch_rows = []
    processed_count = 0
    skipped_count = 0
    failed_count = 0

    for index, row in df.iterrows():
        audio_path_csv = str(row["audio_path"]).strip()

        if audio_path_csv in processed_paths:
            skipped_count += 1
            continue

        audio_path = resolve_audio_path(audio_path_csv)

        if audio_path is None or not audio_path.exists():
            print(f"Skipping missing audio: {audio_path_csv}")
            failed_count += 1
            continue

        transcript = row["transcript"] if "transcript" in row else None

        try:
            features = extract_features_from_audio(audio_path, transcript=transcript)

        except Exception as error:
            print(f"Failed to process {audio_path}: {error}")
            failed_count += 1
            continue

        features["split"] = split_name
        features["audio_path"] = audio_path_csv
        features["id"] = row["id"] if "id" in row else None
        features["user_no"] = row["user_no"] if "user_no" in row else None

        batch_rows.append(features)
        processed_paths.add(audio_path_csv)
        processed_count += 1

        if processed_count % save_every == 0:
            append_features_to_csv(batch_rows)
            batch_rows = []
            print(f"Saved progress: {processed_count} new files processed in {split_name}")

    # Save remaining rows
    append_features_to_csv(batch_rows)

    print(f"\nFinished {split_name} split")
    print(f"New processed: {processed_count}")
    print(f"Skipped already processed: {skipped_count}")
    print(f"Failed/missing: {failed_count}")


def main():
    print("Starting acoustic feature extraction...")

    processed_paths = load_already_processed_paths()

    process_split(TRAIN_CSV, "train", processed_paths)
    process_split(VAL_CSV, "val", processed_paths)
    process_split(TEST_CSV, "test", processed_paths)

    print("\nAcoustic feature extraction completed.")
    print(f"Saved to: {ACOUSTIC_FEATURES_CSV}")

    if ACOUSTIC_FEATURES_CSV.exists():
        final_df = pd.read_csv(ACOUSTIC_FEATURES_CSV)
        print(f"Total rows in acoustic feature file: {len(final_df)}")

        print("\nRows by split:")
        print(final_df["split"].value_counts())


if __name__ == "__main__":
    main()