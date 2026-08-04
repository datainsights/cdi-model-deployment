#!/usr/bin/env bash
set -euo pipefail

WITH_CONTAINER=false
if [[ "${1:-}" == "--with-container" ]]; then
  WITH_CONTAINER=true
elif [[ $# -gt 0 ]]; then
  echo "Usage: bash scripts/bash/09-run-end-to-end-deployment.sh [--with-container]" >&2
  exit 2
fi

if [[ ! -f "app/main.py" ]]; then
  echo "Run this script from the repository root: app/main.py was not found." >&2
  exit 1
fi

mkdir -p results/figures

echo "[1/5] Running automated tests"
python -m pytest -q

echo "[2/5] Starting the API"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >results/09-uvicorn.log 2>&1 &
API_PID=$!
cleanup() {
  if kill -0 "$API_PID" 2>/dev/null; then
    kill "$API_PID"
    wait "$API_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo "[3/5] Waiting for readiness"
ready=false
for _ in {1..30}; do
  if curl --fail --silent http://127.0.0.1:8000/health >/dev/null; then
    ready=true
    break
  fi
  sleep 1
done
if [[ "$ready" != true ]]; then
  echo "API did not become ready. Inspect results/09-uvicorn.log." >&2
  exit 1
fi

echo "[4/5] Running API contract tests"
if [[ -x "scripts/bash/06-test-api.sh" ]]; then
  bash scripts/bash/06-test-api.sh
else
  echo "scripts/bash/06-test-api.sh is required." >&2
  exit 1
fi

if [[ "$WITH_CONTAINER" == true ]]; then
  echo "[container] Building and testing the container"
  if [[ -x "scripts/bash/07-build-container.sh" ]]; then
    bash scripts/bash/07-build-container.sh
  else
    docker build -t model-deployment:chapter09 .
  fi
else
  echo "[container] Skipped; rerun with --with-container to include it"
fi

echo "[5/5] Creating verification evidence"
summary_args=(
  --api-report results/06-api-test-results.json
  --output results/09-deployment-verification.json
  --figure results/figures/09-deployment-readiness.png
)
if [[ "$WITH_CONTAINER" == true ]]; then
  summary_args+=(--container-status passed)
else
  summary_args+=(--container-status skipped)
fi
python scripts/python/09-summarize-deployment-verification.py "${summary_args[@]}"

echo "End-to-end deployment verification completed."

