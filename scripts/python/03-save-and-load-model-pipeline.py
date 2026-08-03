#!/usr/bin/env python3
"""Create and verify the model artifact used in Model Deployment Chapter 03."""

from datetime import datetime, timezone
from pathlib import Path
import platform

import joblib
import numpy as np
import sklearn
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


RANDOM_STATE = 42
MODEL_PATH = Path("models/03-breast-cancer-pipeline.joblib")
MODEL_VERSION = "breast-cancer-logistic-v1"
FEATURE_NAMES = [
    "mean radius",
    "mean texture",
    "mean perimeter",
    "mean area",
    "mean smoothness",
    "mean compactness",
    "mean concavity",
    "mean concave points",
]
TARGET_NAMES = {0: "malignant", 1: "benign"}
REQUIRED_ARTIFACT_KEYS = {
    "pipeline",
    "model_version",
    "feature_names",
    "target_names",
    "trained_at_utc",
    "python_version",
    "scikit_learn_version",
}


def load_training_data():
    """Return the deterministic train/test split established in Chapter 02."""
    dataset = load_breast_cancer(as_frame=True)
    missing_features = sorted(set(FEATURE_NAMES) - set(dataset.data.columns))
    if missing_features:
        raise ValueError(f"Dataset is missing features: {missing_features}")

    features = dataset.data.loc[:, FEATURE_NAMES]
    target = dataset.target
    return train_test_split(
        features,
        target,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=target,
    )


def build_pipeline() -> Pipeline:
    """Construct the preprocessing and classifier pipeline."""
    return Pipeline(
        steps=[
            ("scale", StandardScaler()),
            (
                "classifier",
                LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
            ),
        ]
    )


def validate_artifact(artifact: dict) -> Pipeline:
    """Validate artifact metadata and return its fitted pipeline."""
    missing_keys = REQUIRED_ARTIFACT_KEYS - artifact.keys()
    if missing_keys:
        raise ValueError(
            f"Model artifact is missing required keys: {sorted(missing_keys)}"
        )
    if artifact["feature_names"] != FEATURE_NAMES:
        raise ValueError("Saved feature contract does not match the application contract.")
    if artifact["target_names"] != TARGET_NAMES:
        raise ValueError("Saved target mapping does not match the application contract.")

    pipeline = artifact["pipeline"]
    expected_classes = np.array(sorted(TARGET_NAMES))
    if not np.array_equal(pipeline.classes_, expected_classes):
        raise RuntimeError(
            f"Unexpected fitted class order: {pipeline.classes_.tolist()}"
        )
    return pipeline


def main() -> None:
    """Fit, save, reload, validate, and verify the complete pipeline."""
    X_train, X_test, y_train, _ = load_training_data()
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    predictions_before = pipeline.predict(X_test)
    probabilities_before = pipeline.predict_proba(X_test)
    artifact = {
        "pipeline": pipeline,
        "model_version": MODEL_VERSION,
        "feature_names": FEATURE_NAMES,
        "target_names": TARGET_NAMES,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "scikit_learn_version": sklearn.__version__,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)

    loaded_artifact = joblib.load(MODEL_PATH)
    loaded_pipeline = validate_artifact(loaded_artifact)
    predictions_after = loaded_pipeline.predict(X_test)
    probabilities_after = loaded_pipeline.predict_proba(X_test)

    if not np.array_equal(predictions_before, predictions_after):
        raise RuntimeError("Class predictions changed after serialization.")
    if not np.allclose(probabilities_before, probabilities_after):
        raise RuntimeError("Class probabilities changed after serialization.")

    malignant_index = np.where(loaded_pipeline.classes_ == 0)[0].item()
    malignant_probability = probabilities_after[:, malignant_index]

    print(f"Saved artifact: {MODEL_PATH}")
    print(f"Model version: {loaded_artifact['model_version']}")
    print(f"Fitted class order: {loaded_pipeline.classes_.tolist()}")
    print(f"Verified predictions: {len(predictions_after)}")
    print(
        "Malignant probability range: "
        f"{malignant_probability.min():.3f} to {malignant_probability.max():.3f}"
    )
    print("Round-trip verification: passed")


if __name__ == "__main__":
    main()
