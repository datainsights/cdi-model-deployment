#!/usr/bin/env python3
"""Run the Model API test suite through pytest."""

import subprocess
import sys

if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", "-q", "tests"]))
