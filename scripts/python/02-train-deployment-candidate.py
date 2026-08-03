#!/usr/bin/env python3
"""Train and evaluate the deployment candidate used in the Model Deployment guide."""

from pathlib import Path

import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


RANDOM_STATE = 42
FEATURES = [
    "mean radius",
    "mean texture",
    "mean perimeter",
    "mean area",
    "mean smoothness",
    "mean compactness",
    "mean concavity",
    "mean concave points",
]
OUTPUT_PATH = Path("results/metrics/02-deployment-candidate-metrics.csv")


def load_training_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load the teaching dataset and return the documented feature contract."""
    dataset = load_breast_cancer(as_frame=True)
    X = dataset.data.loc[:, FEATURES].copy()
    y = dataset.target.copy()

    if X.isna().any().any():
        raise ValueError("The selected training features contain missing values.")
    if set(y.unique()) != {0, 1}:
        raise ValueError("Expected binary target values 0 and 1.")

    return X, y


def build_pipeline() -> Pipeline:
    """Create the complete preprocessing and classification pipeline."""
    return Pipeline(
        steps=[
            ("scale", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def main() -> None:
    """Fit the candidate, evaluate it, and write reproducible metrics."""
    X, y = load_training_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    malignant_class_index = list(pipeline.classes_).index(0)
    y_probability_malignant = pipeline.predict_proba(X_test)[
        :, malignant_class_index
    ]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision_malignant": precision_score(y_test, y_pred, pos_label=0),
        "recall_malignant": recall_score(y_test, y_pred, pos_label=0),
        "f1_malignant": f1_score(y_test, y_pred, pos_label=0),
        "roc_auc_malignant": roc_auc_score(
            (y_test == 0).astype(int),
            y_probability_malignant,
        ),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(OUTPUT_PATH, index=False)

    print(f"Training observations: {len(X_train)}")
    print(f"Test observations: {len(X_test)}")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.3f}")
    print(f"Metrics written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
