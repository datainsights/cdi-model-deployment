#!/usr/bin/env python3
"""Create the deterministic example inference batch used in Chapter 04."""

from pathlib import Path

import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split


RANDOM_STATE = 42
OUTPUT_PATH = Path("data/inference/04-new-records.csv")
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


def main() -> None:
    """Write an unlabelled batch drawn from the Chapter 02 test partition."""
    dataset = load_breast_cancer(as_frame=True)
    features = dataset.data.loc[:, FEATURE_NAMES]
    _, test_features, _, _ = train_test_split(
        features,
        dataset.target,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=dataset.target,
    )

    batch = test_features.head(12).copy()
    batch.insert(0, "record_id", [f"BC-{index:04d}" for index in batch.index])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    batch.to_csv(OUTPUT_PATH, index=False)

    print(f"Inference batch written: {OUTPUT_PATH}")
    print(f"Rows: {len(batch)}")
    print(f"Feature columns: {len(FEATURE_NAMES)}")


if __name__ == "__main__":
    main()
