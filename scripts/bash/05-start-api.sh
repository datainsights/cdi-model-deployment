#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f ".venv/bin/activate" ]]; then
  echo "Error: run this script from the repository root after creating .venv." >&2
  exit 1
fi

source .venv/bin/activate

if [[ ! -f "models/03-breast-cancer-pipeline.joblib" ]]; then
  echo "Error: models/03-breast-cancer-pipeline.joblib was not found." >&2
  echo "Run the Chapter 03 save-and-load script first." >&2
  exit 1
fi

if ! command -v fastapi >/dev/null 2>&1; then
  echo "Error: FastAPI CLI is not installed in the active environment." >&2
  echo "Run: python -m pip install -r requirements.txt" >&2
  exit 1
fi

exec fastapi dev scripts/python/05-serving-predictions-api.py
