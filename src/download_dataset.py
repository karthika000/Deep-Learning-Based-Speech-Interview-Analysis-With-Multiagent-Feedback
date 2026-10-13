import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import snapshot_download


def run_command(command: list[str]) -> None:
    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


def normalize_dataset_repo_id(repo_uri: str) -> str:
    """
    Converts supported dataset repo formats into normal HF repo_id.

    Supported:
    - username/dataset-name
    - https://huggingface.co/datasets/username/dataset-name
    """
    repo_uri = repo_uri.strip()

    if repo_uri.startswith("https://huggingface.co/datasets/"):
        return repo_uri.replace("https://huggingface.co/datasets/", "").strip("/")

    return repo_uri.strip("/")


def main():
    load_dotenv()

    repo_uri = os.getenv("HF_REPO_URI")
    hf_token = os.getenv("HF_TOKEN")
    data_dir = Path(os.getenv("DATA_DIR", "data"))

    if not repo_uri:
        raise ValueError("HF_REPO_URI is missing. Add it to your .env file.")

    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Optional login. If HF_TOKEN is empty, this assumes user already ran: hf auth login
    if hf_token:
        run_command(["hf", "auth", "login", "--token", hf_token])

    # Case 1: Hugging Face Storage Bucket
    if repo_uri.startswith("hf://buckets/"):
        bucket_key = repo_uri.replace("hf://buckets/", "").replace("/", "__")
        target_dir = raw_dir / bucket_key
        target_dir.mkdir(parents=True, exist_ok=True)

        print(f"Detected Hugging Face bucket URI: {repo_uri}")
        print(f"Syncing bucket to: {target_dir}")

        run_command([
            "hf",
            "buckets",
            "sync",
            repo_uri,
            str(target_dir),
        ])

        print("Bucket sync completed.")
        print(f"Local raw dataset path: {target_dir}")
        return

    # Case 2: Normal Hugging Face dataset repo
    repo_id = normalize_dataset_repo_id(repo_uri)
    target_dir = raw_dir / repo_id.replace("/", "__")
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"Detected Hugging Face dataset repo: {repo_id}")
    print(f"Downloading dataset to: {target_dir}")

    snapshot_download(
        repo_id=repo_id,
        repo_type="dataset",
        token=hf_token or True,
        local_dir=str(target_dir),
        local_dir_use_symlinks=False,
        resume_download=True,
    )

    print("Dataset download completed.")
    print(f"Local raw dataset path: {target_dir}")


if __name__ == "__main__":
    main()