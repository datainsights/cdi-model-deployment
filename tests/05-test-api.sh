#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f ".venv/bin/activate" ]]; then
  echo "Error: run this script from the repository root after creating .venv." >&2
  exit 1
fi

source .venv/bin/activate

if ! command -v pytest >/dev/null 2>&1; then
  echo "Error: pytest is not installed in the active environment." >&2
  echo "Run: python -m pip install -r requirements.txt" >&2
  exit 1
fi

pytest -q tests/test_05_api.py
