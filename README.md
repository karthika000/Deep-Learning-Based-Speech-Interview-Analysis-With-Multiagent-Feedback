# Voice-Interview-Agent

This project is a deep learning-based voice interview coach that analyzes spoken interview answers using audio-based prediction models and an agentic feedback layer. The system predicts interview-related scores from speech and converts the predicted scores and acoustic indicators into structured coaching feedback for interview improvement.

The system predicts:

- Speaking skills
- Confidence score
- Interview score
- Overall performance

The feedback layer uses predicted scores together with acoustic indicators such as speaking rate, pause ratio, pitch variation, and energy to generate human-readable feedback using judge, critic, supporter, and coach agents.

---

## Dataset

This project uses the RecruitView dataset.

The full dataset is not stored in this GitHub repository because it is large and access-restricted. Each collaborator must obtain official dataset access and use their own Hugging Face token.

The following files and folders are ignored by Git:

- Raw videos
- Extracted audio files
- Generated acoustic features
- HuBERT embedding files
- Trained model checkpoints
- Output result files

---

## Environment Setup

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

---

## Install Requirements

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

---

## Install FFmpeg

FFmpeg is required to extract audio from video files.

### macOS

```bash
brew install ffmpeg
```

### Ubuntu / WSL

```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows

```bash
winget install Gyan.FFmpeg
```

Verify installation:

```bash
ffmpeg -version
```

---

## Hugging Face Setup

Create a local `.env` file from the example file:

```bash
cp .env.example .env
```

Then add your Hugging Face token inside `.env`.

Example:

```env
HF_TOKEN=your_huggingface_token_here
```

---

## Project Structure

```text
Voice-Interview-Agent/
│
├── agents/
│   ├── run_feedback_demo.py
│   ├── feedback_pipeline.py
│   ├── schemas.py
│   └── ...
│
├── data/
│   ├── raw/
│   └── processed/
│       ├── audio_wav/
│       ├── splits/
│       │   ├── train.csv
│       │   ├── val.csv
│       │   └── test.csv
│       ├── metadata_audio.csv
│       ├── acoustic_features.csv
│       ├── train_embeddings.npz
│       ├── val_embeddings.npz
│       └── test_embeddings.npz
│
├── notebooks/
│   └── 01_dl_model_experiments.ipynb
│
├── outputs/
│   ├── agent_inputs/
│   ├── models/
│   ├── plots/
│   └── results/
│
├── src/
│   ├── download_dataset.py
│   ├── inspect_dataset.py
│   ├── extract_audio.py
│   ├── fix_metadata_audio_paths.py
│   ├── create_splits.py
│   ├── check_targets.py
│   ├── extract_acoustic_features.py
│   └── config.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Execution Order

Run the following commands in order from the project root.

---

## Step 1: Download Dataset

```bash
python src/download_dataset.py
```

This downloads the RecruitView dataset using the Hugging Face token.

If your script is named `download_data.py`, use:

```bash
python src/download_data.py
```

---

## Step 2: Inspect Dataset

```bash
python src/inspect_dataset.py
```

This checks the dataset structure, available files, and metadata columns.

---

## Step 3: Extract Audio from Videos

```bash
python src/extract_audio.py
```

This extracts WAV audio files from the video clips and stores them under:

```text
data/processed/audio_wav/
```

It also creates or updates:

```text
data/processed/metadata_audio.csv
```

---

## Step 4: Fix Audio Paths in Metadata

```bash
python src/fix_metadata_audio_paths.py
```

This normalizes the `audio_path` column in `metadata_audio.csv`.

Expected audio path format:

```text
data/processed/audio_wav/vid_0004.wav
```

The `video_path` column is kept only for reference. The deep learning pipeline uses only `audio_path`.

---

## Step 5: Create User-Independent Splits

```bash
python src/create_splits.py
```

This creates train, validation, and test splits using `user_no`.

Output files:

```text
data/processed/splits/train.csv
data/processed/splits/val.csv
data/processed/splits/test.csv
```

The split is user-independent, meaning the same participant does not appear in more than one split.

---

## Step 6: Check Target Columns

```bash
python src/check_targets.py
```

This checks that the required target columns are available.

Required targets:

```text
speaking_skills
confidence_score
interview_score
overall_performance
```

---

## Step 7: Extract Acoustic Features

```bash
python src/extract_acoustic_features.py
```

This extracts handcrafted acoustic features from the WAV files.

Generated file:

```text
data/processed/acoustic_features.csv
```

Extracted features include:

- Duration
- Energy mean
- Energy variation
- Maximum energy
- Pause ratio
- Voiced ratio
- Pitch mean
- Pitch variation
- Minimum pitch
- Maximum pitch
- Speaking rate

This step may take time because pitch extraction is computationally expensive.

---

## Step 8: Run Deep Learning Experiments

Open the notebook:

```text
notebooks/01_dl_model_experiments.ipynb
```

Run all cells in order.

This notebook performs:

1. Acoustic feature baseline training
2. HuBERT embedding extraction
3. HuBERT embedding model training
4. Fusion model training
5. Model comparison
6. Plot generation
7. Agent input JSON generation

Generated embedding files:

```text
data/processed/train_embeddings.npz
data/processed/val_embeddings.npz
data/processed/test_embeddings.npz
```

Generated model files:

```text
outputs/models/acoustic_baseline_random_forest.joblib
outputs/models/embedding_model.pt
outputs/models/proposed_fusion_model.pt
```

Generated result files:

```text
outputs/results/acoustic_baseline_results.json
outputs/results/embedding_model_results.json
outputs/results/proposed_fusion_model_results.json
outputs/results/model_comparison_results.csv
```

Generated plots:

```text
outputs/plots/average_mae_comparison.png
outputs/plots/average_pearson_comparison.png
outputs/plots/fusion_predicted_vs_actual_overall_performance.png
```

Generated agent input files:

```text
outputs/agent_inputs/demo_agent_input.json
outputs/agent_inputs/demo_agent_inputs.json
```

---

## Step 9: Run Agentic Feedback Demo

Run the feedback demo:

```bash
python agents/run_feedback_demo.py
```

The agentic layer reads the demo JSON input and generates structured feedback using:

- Judge Agent
- Critic Agent
- Supporter Agent
- Coach Agent

The input file should be a single JSON object, for example:

```text
outputs/agent_inputs/demo_agent_input.json
```

---

## Output of the agent feedback


The notebook generates schema-compatible demo files under:

```text
outputs/agent_inputs/
```

---

## Notes

This project is intended for interview coaching and self-improvement. It is not intended for automated hiring decisions, candidate ranking, or rejection.

The full dataset, extracted audio, generated embeddings, and trained model checkpoints are not stored in GitHub. They must be generated locally by following the execution steps above.

The dataset is too big and it need access if want to use the dataset you may need access https://huggingface.co/datasets/AI4A-lab/RecruitView