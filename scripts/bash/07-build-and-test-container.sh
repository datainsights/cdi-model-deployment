#!/usr/bin/env bash
set -Eeuo pipefail

IMAGE_NAME="${IMAGE_NAME:-cdi-model-api}"
IMAGE_TAG="${IMAGE_TAG:-07}"
CONTAINER_NAME="${CONTAINER_NAME:-cdi-model-api-07-test}"
HOST_PORT="${HOST_PORT:-8000}"
CONTAINER_PORT="${CONTAINER_PORT:-8000}"
HEALTH_PATH="${HEALTH_PATH:-/health}"
WAIT_SECONDS="${WAIT_SECONDS:-30}"

IMAGE_REF="${IMAGE_NAME}:${IMAGE_TAG}"
BASE_URL="http://127.0.0.1:${HOST_PORT}"

cleanup() {
  docker rm --force "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM

if ! command -v docker >/dev/null 2>&1; then
  echo "[FAIL] Docker is not installed or is not on PATH." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "[FAIL] The Docker engine is not available." >&2
  exit 1
fi

if [[ ! -f Dockerfile ]]; then
  echo "[FAIL] Dockerfile was not found. Run this script from the repository root." >&2
  exit 1
fi

if docker container inspect "${CONTAINER_NAME}" >/dev/null 2>&1; then
  echo "[INFO] Removing an earlier test container named ${CONTAINER_NAME}."
  docker rm --force "${CONTAINER_NAME}" >/dev/null
fi

echo "[INFO] Building ${IMAGE_REF}."
docker build --tag "${IMAGE_REF}" .

echo "[INFO] Starting ${CONTAINER_NAME} on ${BASE_URL}."
docker run \
  --detach \
  --name "${CONTAINER_NAME}" \
  --publish "${HOST_PORT}:${CONTAINER_PORT}" \
  "${IMAGE_REF}" >/dev/null

echo "[INFO] Waiting for ${BASE_URL}${HEALTH_PATH}."
for ((attempt = 1; attempt <= WAIT_SECONDS; attempt++)); do
  if curl --fail --silent --show-error "${BASE_URL}${HEALTH_PATH}" >/dev/null 2>&1; then
    echo "[PASS] Container health endpoint returned a successful response."
    break
  fi

  if ! docker container inspect "${CONTAINER_NAME}" \
    --format '{{.State.Running}}' 2>/dev/null | grep -qx true; then
    echo "[FAIL] The container stopped before becoming ready." >&2
    docker logs "${CONTAINER_NAME}" >&2 || true
    exit 1
  fi

  if ((attempt == WAIT_SECONDS)); then
    echo "[FAIL] The API did not become ready within ${WAIT_SECONDS} seconds." >&2
    docker logs "${CONTAINER_NAME}" >&2 || true
    exit 1
  fi

  sleep 1
done

if [[ -x scripts/bash/06-test-api.sh ]]; then
  echo "[INFO] Running the Chapter 06 API contract checks."
  API_BASE_URL="${BASE_URL}" bash scripts/bash/06-test-api.sh
elif [[ -f scripts/bash/06-test-api.sh ]]; then
  echo "[INFO] Running the Chapter 06 API contract checks."
  API_BASE_URL="${BASE_URL}" bash scripts/bash/06-test-api.sh
else
  echo "[WARN] scripts/bash/06-test-api.sh was not found; health check only."
fi

echo "[PASS] Verified image ${IMAGE_REF}."
