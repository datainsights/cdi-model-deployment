#!/usr/bin/env python3
"""Verify the Python environment required by the Model Deployment guide."""

from __future__ import annotations

import importlib
import platform
import sys
from pathlib import Path


REQUIRED_MODULES = (
    "fastapi",
    "httpx",
    "joblib",
    "matplotlib",
    "numpy",
    "pandas",
    "pydantic",
    "pytest",
    "sklearn",
    "uvicorn",
)


def main() -> int:
    """Print environment details and return a shell-friendly status code."""
    repository_root = Path(__file__).resolve().parents[2]
    expected_environment = repository_root / ".venv"
    active_environment = Path(sys.prefix).resolve()

    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Interpreter: {Path(sys.executable).resolve()}")

    environment_matches = active_environment == expected_environment.resolve()
    print(f"Repository .venv active: {'yes' if environment_matches else 'no'}")

    missing_modules: list[str] = []
    for module_name in REQUIRED_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            missing_modules.append(module_name)
            print(f"[missing] {module_name}")
        else:
            version = getattr(module, "__version__", "version unavailable")
            print(f"[ok] {module_name}: {version}")

    if not environment_matches:
        print("\nActivate this repository's .venv and run the check again.")
    if missing_modules:
        print("\nInstall missing packages with:")
        print("  python -m pip install -r requirements.txt")

    if not environment_matches or missing_modules:
        return 1

    print("\nEnvironment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

