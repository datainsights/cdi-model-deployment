#!/usr/bin/env bash
set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPOSITORY_ROOT"

echo "Checking system tools..."

for command_name in python quarto git; do
  if command -v "$command_name" >/dev/null 2>&1; then
    echo "[ok] $command_name: $(command -v "$command_name")"
  else
    echo "[missing] $command_name"
    exit 1
  fi
done

if command -v docker >/dev/null 2>&1; then
  echo "[optional] docker: $(command -v docker)"
else
  echo "[optional] docker not found; install it before Chapter 07"
fi

echo
echo "Checking Python environment..."
python scripts/python/01-check-environment.py

