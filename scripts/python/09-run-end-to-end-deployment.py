#!/usr/bin/env python3
"""Run the reproducible training, inference, testing, and monitoring sequence."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STEPS = ["02-train-deployment-model.py", "03-save-and-load-model-pipeline.py",
         "04-run-batch-inference.py", "06-test-model-api.py", "08-monitor-prediction-data.py"]


def main() -> None:
    for script_name in STEPS:
        print(f"\nRunning {script_name}", flush=True)
        subprocess.run([sys.executable, ROOT / "scripts" / "python" / script_name], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
