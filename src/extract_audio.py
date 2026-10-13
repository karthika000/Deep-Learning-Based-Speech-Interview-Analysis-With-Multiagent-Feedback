import os
import json
import subprocess
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm


def get_local_raw_dir() -> Path:
    repo_uri = os.getenv("HF_REPO_URI")
    data_dir = Path(os.getenv("DATA_DIR", "data"))

    if not repo_uri:
        raise ValueError("HF_REPO_URI is missing.")

    if repo_uri.startswith("hf://buckets/"):
        key = repo_uri.replace("hf://buckets/", "").replace("/", "__")
    elif repo_uri.startswith("https://huggingface.co/datasets/"):
        key = repo_uri.replace("https://huggingface.co/datasets/", "").strip("/").replace("/", "__")
    else:
        key = repo_uri.strip("/").replace("/", "__")

    return data_dir / "raw" / key


def find_metadata_file(raw_dir: Path) -> Path:
    candidates = []

    for pattern in ["*.json", "*.jsonl", "*.csv", "*.parquet"]:
        candidates.extend(raw_dir.rglob(pattern))

    if not candidates:
        raise FileNotFoundError(
            "No metadata file found. Expected JSON, JSONL, CSV, or Parquet."
        )

    # Prefer likely metadata files
    priority_words = ["metadata", "data", "annotations", "labels"]

    for word in priority_words:
        for path in candidates:
            if word in path.name.lower():
                return path

    return candidates[0]


def load_metadata(metadata_path: Path) -> pd.DataFrame:
    suffix = metadata_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(metadata_path)

    if suffix == ".jsonl":
        rows = []
        with open(metadata_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
        return pd.DataFrame(rows)

    if suffix == ".json":
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return pd.DataFrame(data)

        if isinstance(data, dict):
            # Common format: {"train": [...], "validation": [...], "test": [...]}
            if all(isinstance(v, list) for v in data.values()):
                frames = []
                for split_name, rows in data.items():
                    df = pd.DataFrame(rows)
                    df["original_split"] = split_name
                    frames.append(df)
                return pd.concat(frames, ignore_index=True)

            return pd.DataFrame([data])

    if suffix == ".parquet":
        return pd.read_parquet(metadata_path)

    raise ValueError(f"Unsupported metadata format: {metadata_path}")


def find_video_file(raw_dir: Path, file_name: str) -> Path | None:
    file_name = str(file_name)

    # Direct match
    direct_matches = list(raw_dir.rglob(file_name))
    if direct_matches:
        return direct_matches[0]

    # Basename match
    basename = Path(file_name).name
    basename_matches = list(raw_dir.rglob(basename))
    if basename_matches:
        return basename_matches[0]

    # Sometimes metadata may not include extension
    stem = Path(file_name).stem
    possible_extensions = [".mp4", ".mov", ".mkv", ".avi"]

    for ext in possible_extensions:
        matches = list(raw_dir.rglob(stem + ext))
        if matches:
            return matches[0]

    return None


def extract_audio_ffmpeg(video_path: Path, audio_path: Path, sample_rate: int) -> None:
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-acodec",
        "pcm_s16le",
        str(audio_path),
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def main():
    load_dotenv()

    sample_rate = int(os.getenv("SAMPLE_RATE", "16000"))
    data_dir = Path(os.getenv("DATA_DIR", "data"))

    raw_dir = get_local_raw_dir()
    audio_dir = data_dir / "processed" / "audio_wav"
    metadata_out = data_dir / "processed" / "metadata_audio.csv"

    if not raw_dir.exists():
        raise FileNotFoundError(
            f"Raw dataset folder not found: {raw_dir}. Run src/download_data.py first."
        )

    metadata_path = find_metadata_file(raw_dir)
    print(f"Using metadata file: {metadata_path}")

    df = load_metadata(metadata_path)

    if "file_name" not in df.columns:
        raise KeyError(
            f"'file_name' column not found in metadata. Available columns: {list(df.columns)}"
        )

    audio_paths = []
    video_paths = []
    missing_files = []
    failed_files = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Extracting audio"):
        file_name = row["file_name"]
        video_path = find_video_file(raw_dir, file_name)

        if video_path is None:
            audio_paths.append(None)
            video_paths.append(None)
            missing_files.append(file_name)
            continue

        audio_name = Path(str(file_name)).with_suffix(".wav").name
        audio_path = audio_dir / audio_name

        if not audio_path.exists():
            try:
                extract_audio_ffmpeg(video_path, audio_path, sample_rate)
            except subprocess.CalledProcessError:
                audio_paths.append(None)
                video_paths.append(str(video_path))
                failed_files.append(file_name)
                continue

        audio_paths.append(str(audio_path))
        video_paths.append(str(video_path))

    df["video_path"] = video_paths
    df["audio_path"] = audio_paths

    metadata_out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(metadata_out, index=False)

    print("\nAudio extraction completed.")
    print(f"Processed metadata saved to: {metadata_out}")
    print(f"Audio folder: {audio_dir}")
    print(f"Missing video files: {len(missing_files)}")
    print(f"Failed audio extractions: {len(failed_files)}")

    if missing_files:
        print("\nFirst missing examples:")
        print(missing_files[:5])

    if failed_files:
        print("\nFirst failed examples:")
        print(failed_files[:5])


if __name__ == "__main__":
    main()