#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f ".venv/bin/activate" ]]; then
  echo "Error: run this script from the repository root after creating .venv." >&2
  exit 1
fi

source .venv/bin/activate
python scripts/python/05-request-prediction.py
