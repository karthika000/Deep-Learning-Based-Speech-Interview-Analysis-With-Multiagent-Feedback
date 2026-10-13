from pathlib import Path


# ============================================================
# Project root
# ============================================================
# This points to the main project folder:
# VOICE-INTERVIEW-AGENT/
#
# Since this file is inside src/config.py:
# Path(__file__) = VOICE-INTERVIEW-AGENT/src/config.py
# parents[1]     = VOICE-INTERVIEW-AGENT/

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ============================================================
# Data paths
# ============================================================

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

AUDIO_DIR = PROCESSED_DIR / "audio_wav"

METADATA_AUDIO_CSV = PROCESSED_DIR / "metadata_audio.csv"

SPLITS_DIR = PROCESSED_DIR / "splits"

TRAIN_CSV = SPLITS_DIR / "train.csv"
VAL_CSV = SPLITS_DIR / "val.csv"
TEST_CSV = SPLITS_DIR / "test.csv"


# ============================================================
# Processed feature files
# ============================================================
# These files will be created later by the DL pipeline.

ACOUSTIC_FEATURES_CSV = PROCESSED_DIR / "acoustic_features.csv"

TRAIN_EMBEDDINGS = PROCESSED_DIR / "train_embeddings.npz"
VAL_EMBEDDINGS = PROCESSED_DIR / "val_embeddings.npz"
TEST_EMBEDDINGS = PROCESSED_DIR / "test_embeddings.npz"


# ============================================================
# Output paths
# ============================================================

OUTPUT_DIR = PROJECT_ROOT / "outputs"

MODEL_DIR = OUTPUT_DIR / "models"
RESULTS_DIR = OUTPUT_DIR / "results"
PLOTS_DIR = OUTPUT_DIR / "plots"


# ============================================================
# Target columns
# ============================================================
# These are the interview-related scores we want to predict.
# We are not using answer_score for now because this project is
# currently audio-only. answer_score is more content/transcript-based.

TARGET_COLUMNS = [
    "speaking_skills",
    "confidence_score",
    "interview_score",
    "overall_performance",
]


# ============================================================
# Audio settings
# ============================================================
# wav2vec2 / HuBERT models commonly use 16 kHz audio.

SAMPLE_RATE = 16000

# To keep training and embedding extraction practical,
# long audio files will be trimmed to this maximum duration.
# You can increase this later if needed.

MAX_AUDIO_SECONDS = 60


# ============================================================
# Pretrained speech model
# ============================================================
# This model will be used later for extracting deep speech embeddings.
# HuBERT is a strong pretrained speech representation model.

SSL_MODEL_NAME = "facebook/hubert-base-ls960"

# Alternative option:
# SSL_MODEL_NAME = "facebook/wav2vec2-base"


# ============================================================
# Training settings
# ============================================================

SEED = 42

BATCH_SIZE = 32

EPOCHS = 80

LEARNING_RATE = 1e-3

PATIENCE = 10

# Use "cuda" if GPU is available.
# The training scripts will automatically fall back to CPU if needed.

DEVICE = "cuda"