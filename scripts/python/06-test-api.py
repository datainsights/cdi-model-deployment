#!/usr/bin/env python3
"""Run contract-focused smoke tests against a live prediction API."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import httpx


VALID_PAYLOAD = {
    "mean_radius": 17.99,
    "mean_texture": 10.38,
    "mean_perimeter": 122.80,
    "mean_area": 1001.0,
    "mean_smoothness": 0.11840,
    "mean_compactness": 0.27760,
    "mean_concavity": 0.30010,
    "mean_concave_points": 0.14710,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL of the running API.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/06-api-test-results.json"),
        help="Path for the JSON test report.",
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser.parse_args()


def record(
    name: str,
    response: httpx.Response,
    expected_status: int,
    required_keys: tuple[str, ...] = (),
) -> dict[str, Any]:
    try:
        body: Any = response.json()
    except ValueError:
        body = response.text

    keys_present = isinstance(body, dict) and all(key in body for key in required_keys)
    passed = response.status_code == expected_status and (
        not required_keys or keys_present
    )
    return {
        "name": name,
        "passed": passed,
        "expected_status": expected_status,
        "actual_status": response.status_code,
        "required_keys": list(required_keys),
        "response": body,
    }


def run_tests(base_url: str, timeout: float) -> list[dict[str, Any]]:
    url = base_url.rstrip("/")
    invalid_payload = dict(VALID_PAYLOAD)
    invalid_payload["mean_radius"] = -1
    missing_payload = dict(VALID_PAYLOAD)
    missing_payload.pop("mean_texture")

    with httpx.Client(timeout=timeout) as client:
        return [
            record("health", client.get(f"{url}/health"), 200, ("status",)),
            record(
                "valid_prediction",
                client.post(f"{url}/predict", json=VALID_PAYLOAD),
                200,
                ("prediction",),
            ),
            record(
                "missing_required_field",
                client.post(f"{url}/predict", json=missing_payload),
                422,
                ("detail",),
            ),
            record(
                "invalid_boundary",
                client.post(f"{url}/predict", json=invalid_payload),
                422,
                ("detail",),
            ),
        ]


def main() -> int:
    args = parse_args()

    try:
        results = run_tests(args.base_url, args.timeout)
    except httpx.RequestError as exc:
        print(f"Could not reach the API: {exc}", file=sys.stderr)
        return 2

    report = {
        "base_url": args.base_url,
        "passed": sum(item["passed"] for item in results),
        "total": len(results),
        "tests": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    for item in results:
        marker = "PASS" if item["passed"] else "FAIL"
        print(f"[{marker}] {item['name']}: HTTP {item['actual_status']}")
    print(f"Report written to {args.output}")

    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
