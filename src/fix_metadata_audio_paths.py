from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

METADATA_CSV = PROJECT_ROOT / "data" / "processed" / "metadata_audio.csv"
AUDIO_DIR = PROJECT_ROOT / "data" / "processed" / "audio_wav"

RELATIVE_AUDIO_DIR = Path("data/processed/audio_wav")


def build_audio_path_from_row(row):
    """
    Creates the expected audio_path using the file/video name.

    Example:
    videos/vid_0004.mp4
    becomes:
    data/processed/audio_wav/vid_0004.wav
    """

    possible_columns = ["audio_path", "file_name", "video_path"]

    for column in possible_columns:
        if column in row and pd.notna(row[column]):
            value = str(row[column]).strip()

            if value:
                stem = Path(value).stem
                return RELATIVE_AUDIO_DIR / f"{stem}.wav"

    return None


def main():
    if not METADATA_CSV.exists():
        raise FileNotFoundError(f"Metadata CSV not found: {METADATA_CSV}")

    if not AUDIO_DIR.exists():
        raise FileNotFoundError(f"Audio folder not found: {AUDIO_DIR}")

    df = pd.read_csv(METADATA_CSV)

    if "audio_path" not in df.columns:
        df["audio_path"] = ""

    fixed_audio_paths = []
    valid_rows = []
    missing_files = []

    for _, row in df.iterrows():
        relative_audio_path = build_audio_path_from_row(row)

        if relative_audio_path is None:
            fixed_audio_paths.append("")
            valid_rows.append(False)
            missing_files.append("Could not derive audio path")
            continue

        absolute_audio_path = PROJECT_ROOT / relative_audio_path

        fixed_audio_paths.append(relative_audio_path.as_posix())

        if absolute_audio_path.exists():
            valid_rows.append(True)
        else:
            valid_rows.append(False)
            missing_files.append(relative_audio_path.as_posix())

    df["audio_path"] = fixed_audio_paths

    before_count = len(df)

    # Keep only rows where the corresponding WAV file exists
    df = df[valid_rows].copy()

    after_count = len(df)

    df.to_csv(METADATA_CSV, index=False)

    print("metadata_audio.csv cleaned successfully.")
    print(f"Original rows: {before_count}")
    print(f"Rows with existing audio files: {after_count}")
    print(f"Removed rows: {before_count - after_count}")
    print(f"Updated file: {METADATA_CSV}")

    if missing_files:
        print("\nFirst missing audio files:")
        for item in missing_files[:10]:
            print(f"  - {item}")

    print("\nExample audio_path after cleaning:")
    if len(df) > 0:
        print(df.iloc[0]["audio_path"])


if __name__ == "__main__":
    main()