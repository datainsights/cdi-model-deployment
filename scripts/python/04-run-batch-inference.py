#!/usr/bin/env python3
"""Validate a CSV batch and generate predictions with a saved pipeline artifact."""

import argparse
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


REQUIRED_ARTIFACT_KEYS = {
    "pipeline",
    "model_version",
    "feature_names",
    "target_names",
}
POSITIVE_CLASS = 0


def parse_args() -> argparse.Namespace:
    """Parse command-line paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def require_file(path: Path, label: str) -> None:
    """Fail with a clear message when a required file is unavailable."""
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")


def load_artifact(path: Path) -> dict:
    """Load and validate the model artifact contract."""
    require_file(path, "Model artifact")
    artifact = joblib.load(path)
    if not isinstance(artifact, dict):
        raise TypeError("Model artifact must be a dictionary.")

    missing = sorted(REQUIRED_ARTIFACT_KEYS - artifact.keys())
    if missing:
        raise ValueError(f"Model artifact is missing required keys: {missing}")

    pipeline = artifact["pipeline"]
    if not hasattr(pipeline, "predict") or not hasattr(pipeline, "predict_proba"):
        raise TypeError("Saved pipeline must support predict() and predict_proba().")
    if POSITIVE_CLASS not in pipeline.classes_:
        raise ValueError(
            f"Positive class {POSITIVE_CLASS!r} is absent from "
            f"fitted classes {pipeline.classes_.tolist()}."
        )
    return artifact


def validate_input(data: pd.DataFrame, feature_names: list[str]) -> None:
    """Validate the incoming batch against the saved feature contract."""
    required = {"record_id", *feature_names}
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if data.empty:
        raise ValueError("The inference batch contains no rows.")
    if data["record_id"].isna().any():
        raise ValueError("record_id contains missing values.")
    if data["record_id"].duplicated().any():
        raise ValueError("record_id must be unique within a batch.")

    non_numeric = [name for name in feature_names if not pd.api.types.is_numeric_dtype(data[name])]
    if non_numeric:
        raise TypeError(f"Feature columns must be numeric: {non_numeric}")
    if data.loc[:, feature_names].isna().any().any():
        raise ValueError("Feature values contain missing data.")
    if not np.isfinite(data.loc[:, feature_names].to_numpy()).all():
        raise ValueError("Feature values must be finite.")


def build_results(data: pd.DataFrame, artifact: dict) -> pd.DataFrame:
    """Generate and validate the stable prediction output."""
    pipeline = artifact["pipeline"]
    feature_names = artifact["feature_names"]
    features = data.loc[:, feature_names].copy()
    predictions = pipeline.predict(features)
    probabilities = pipeline.predict_proba(features)
    positive_index = list(pipeline.classes_).index(POSITIVE_CLASS)
    positive_probabilities = probabilities[:, positive_index]
    target_names = artifact["target_names"]

    results = pd.DataFrame(
        {
            "record_id": data["record_id"].to_numpy(),
            "prediction": predictions,
            "prediction_label": [target_names[int(value)] for value in predictions],
            "malignant_probability": positive_probabilities,
            "model_version": artifact["model_version"],
            "predicted_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    )

    if len(results) != len(data):
        raise RuntimeError("Prediction row count does not match input row count.")
    if results["malignant_probability"].isna().any():
        raise RuntimeError("Prediction probabilities contain missing values.")
    if not results["malignant_probability"].between(0, 1).all():
        raise RuntimeError("Prediction probabilities fall outside [0, 1].")
    return results


def main() -> None:
    """Run validated batch inference and write an auditable CSV."""
    args = parse_args()
    require_file(args.input, "Inference batch")
    artifact = load_artifact(args.model)
    data = pd.read_csv(args.input)
    validate_input(data, artifact["feature_names"])
    results = build_results(data, artifact)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False)

    print(f"Model version: {artifact['model_version']}")
    print(f"Input rows: {len(data)}")
    print(f"Output rows: {len(results)}")
    print(f"Class counts: {results['prediction_label'].value_counts().to_dict()}")
    print(f"Predictions written: {args.output}")


if __name__ == "__main__":
    main()
