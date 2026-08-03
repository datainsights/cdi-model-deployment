#!/usr/bin/env python3
"""Load the persisted pipeline and verify its deployment contract."""

from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "iris-classifier.joblib"


def main() -> None:
    artifact = joblib.load(MODEL_PATH)
    required = {"pipeline", "feature_names", "target_names", "model_version"}
    missing = required.difference(artifact)
    if missing:
        raise ValueError(f"Model artifact is missing: {sorted(missing)}")
    print(f"Loaded model version {artifact['model_version']}")
    print(f"Expected features: {artifact['feature_names']}")


if __name__ == "__main__":
    main()
