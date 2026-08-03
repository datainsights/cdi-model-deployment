#!/usr/bin/env python3
"""Run validated batch inference with the saved pipeline."""

from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "iris-classifier.joblib"
INPUT_PATH = ROOT / "data" / "inference" / "04-inference-input.csv"
OUTPUT_PATH = ROOT / "results" / "04-batch-predictions.csv"


def main() -> None:
    artifact = joblib.load(MODEL_PATH)
    columns = artifact["feature_names"]
    if INPUT_PATH.exists():
        frame = pd.read_csv(INPUT_PATH)
    else:
        frame = pd.DataFrame([[5.1, 3.5, 1.4, 0.2], [6.7, 3.1, 4.7, 1.5]], columns=columns)
        INPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(INPUT_PATH, index=False)
    if list(frame.columns) != columns:
        raise ValueError(f"Expected columns in this order: {columns}")
    predictions = artifact["pipeline"].predict(frame)
    output = frame.copy()
    output["predicted_class"] = predictions
    output["predicted_label"] = [artifact["target_names"][value] for value in predictions]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False)
    print(f"Predictions written to {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
