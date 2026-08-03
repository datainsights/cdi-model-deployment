#!/usr/bin/env python3
"""Create a compact monitoring summary from batch prediction data."""

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PREDICTIONS_PATH = ROOT / "results" / "04-batch-predictions.csv"
REPORT_PATH = ROOT / "results" / "monitoring" / "08-prediction-summary.json"


def main() -> None:
    frame = pd.read_csv(PREDICTIONS_PATH)
    report = {"row_count": len(frame), "missing_values": frame.isna().sum().to_dict(),
              "prediction_counts": frame["predicted_label"].value_counts().to_dict()}
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Monitoring summary written to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
