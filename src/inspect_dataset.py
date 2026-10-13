import os
from pathlib import Path

from dotenv import load_dotenv


def get_local_raw_dir() -> Path:
    load_dotenv()

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


def main():
    raw_dir = get_local_raw_dir()

    if not raw_dir.exists():
        raise FileNotFoundError(
            f"Raw dataset folder not found: {raw_dir}. Run src/download_data.py first."
        )

    print(f"Inspecting dataset folder: {raw_dir}\n")

    file_count = 0
    total_size_mb = 0.0

    for path in sorted(raw_dir.rglob("*")):
        if path.is_file():
            file_count += 1
            size_mb = path.stat().st_size / (1024 * 1024)
            total_size_mb += size_mb
            print(f"{path.relative_to(raw_dir)}  |  {size_mb:.2f} MB")

    print("\nSummary")
    print(f"Files: {file_count}")
    print(f"Total size: {total_size_mb:.2f} MB")


if __name__ == "__main__":
    main()