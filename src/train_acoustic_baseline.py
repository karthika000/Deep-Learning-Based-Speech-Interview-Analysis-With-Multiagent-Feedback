from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scipy.stats import pearsonr, spearmanr

from config import (
    PROJECT_ROOT,
    TRAIN_CSV,
    TEST_CSV,
    ACOUSTIC_FEATURES_CSV,
    TARGET_COLUMNS,
    MODEL_DIR,
    RESULTS_DIR,
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
]


def ensure_output_dirs():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def calculate_metrics(y_true, y_pred, target_columns):
    """
    Calculate regression metrics for each target
    """

    results = {}

    for index, target in enumerate(target_columns):
        true_values = y_true[:, index]
        predicted_values = y_pred[:, index]

        results[target] = {
            "MAE": float(mean_absolute_error(true_values, predicted_values)),
            "RMSE": float(mean_squared_error(true_values, predicted_values, squared=False)),
            "R2": float(r2_score(true_values, predicted_values)),
            "Pearson": float(pearsonr(true_values, predicted_values)[0]),
            "Spearman": float(spearmanr(true_values, predicted_values)[0]),
        }

    results["average"] = {
        metric: float(np.nanmean([results[target][metric] for target in target_columns]))
        for metric in ["MAE", "RMSE", "R2", "Pearson", "Spearman"]
    }

    return results

def load_dataset():
    """
    Load train/test split CSVs and merge them with acoustic features.
    """

    if not ACOUSTIC_FEATURES_CSV.exists():
        raise FileNotFoundError(
            f"{ACOUSTIC_FEATURES_CSV} not found. "
            "Run src/extract_acoustic_features.py first."
        )

    train_df = pd.read_csv(TRAIN_CSV)
    test_df = pd.read_csv(TEST_CSV)
    features_df = pd.read_csv(ACOUSTIC_FEATURES_CSV)

    train_merged = train_df.merge(features_df, on="audio_path", how="inner")
    test_merged = test_df.merge(features_df, on="audio_path", how="inner")

    if len(train_merged) == 0:
        raise ValueError("Train merge produced 0 rows. Check audio_path values.")

    if len(test_merged) == 0:
        raise ValueError("Test merge produced 0 rows. Check audio_path values.")

    print("Dataset loaded successfully.")
    print(f"Train rows: {len(train_merged)}")
    print(f"Test rows:  {len(test_merged)}")

    return train_merged, test_merged


def main():
    print("Training Acoustic Feature Baseline...")

    ensure_output_dirs()

    train_df, test_df = load_dataset()

    missing_feature_cols = [
        col for col in ACOUSTIC_COLUMNS if col not in train_df.columns
    ]

    if missing_feature_cols:
        raise KeyError(f"Missing acoustic feature columns: {missing_feature_cols}")

    missing_target_cols = [
        col for col in TARGET_COLUMNS if col not in train_df.columns
    ]

    if missing_target_cols:
        raise KeyError(f"Missing target columns: {missing_target_cols}")

    X_train = train_df[ACOUSTIC_COLUMNS].values
    y_train = train_df[TARGET_COLUMNS].values

    X_test = test_df[ACOUSTIC_COLUMNS].values
    y_test = test_df[TARGET_COLUMNS].values

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        max_depth=None,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    results = calculate_metrics(
        y_true=y_test,
        y_pred=predictions,
        target_columns=TARGET_COLUMNS,
    )

    model_path = MODEL_DIR / "acoustic_baseline_random_forest.joblib"
    results_path = RESULTS_DIR / "acoustic_baseline_results.json"

    joblib.dump(model, model_path)

    with open(results_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print("\nAcoustic baseline training completed.")
    print(f"Model saved to:   {model_path}")
    print(f"Results saved to: {results_path}")

    print("\nAverage results:")
    for metric, value in results["average"].items():
        print(f"{metric}: {value:.4f}")


if __name__ == "__main__":
    main()