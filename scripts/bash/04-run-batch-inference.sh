#!/usr/bin/env bash
set -euo pipefail

python scripts/python/04-prepare-inference-batch.py
python scripts/python/04-run-batch-inference.py \
  --input data/inference/04-new-records.csv \
  --model models/03-breast-cancer-pipeline.joblib \
  --output results/predictions/04-breast-cancer-predictions.csv
