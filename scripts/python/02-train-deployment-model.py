#!/usr/bin/env python3
"""Train and evaluate the classification pipeline used throughout the guide."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "iris-classifier.joblib"
METRICS_PATH = ROOT / "results" / "metrics" / "02-model-metrics.json"
RANDOM_STATE = 42


def build_pipeline() -> Pipeline:
    return Pipeline([("scale", StandardScaler()), ("classifier", LogisticRegression(max_iter=1_000))])


def main() -> None:
    data = load_iris(as_frame=True)
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.25, stratify=data.target, random_state=RANDOM_STATE
    )
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "feature_names": list(data.feature_names),
                 "target_names": list(data.target_names), "model_version": "0.1.0"}, MODEL_PATH)
    metrics = {"accuracy": accuracy_score(y_test, predictions),
               "classification_report": classification_report(
                   y_test, predictions, target_names=data.target_names, output_dict=True)}
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Model written to {MODEL_PATH.relative_to(ROOT)}")
    print(f"Accuracy: {metrics['accuracy']:.3f}")


if __name__ == "__main__":
    main()
