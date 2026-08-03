#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"

python scripts/python/06-test-api.py \
  --base-url "$BASE_URL" \
  --output results/06-api-test-results.json
