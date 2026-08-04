#!/usr/bin/env python3
"""Summarize Chapter 09 deployment checks and plot release readiness."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


VALID_STATUSES = {"passed", "failed", "skipped", "not_run"}
STATUS_COLOURS = {
    "passed": "#16835d",
    "failed": "#c2413b",
    "skipped": "#94a3b8",
    "not_run": "#cbd5e1",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--figure", type=Path, required=True)
    parser.add_argument(
        "--container-status",
        choices=sorted(VALID_STATUSES),
        default="not_run",
    )
    return parser.parse_args()


def normalize_status(value: Any) -> str:
    if isinstance(value, bool):
        return "passed" if value else "failed"
    text = str(value).strip().lower()
    aliases = {"pass": "passed", "ok": "passed", "fail": "failed"}
    status = aliases.get(text, text)
    return status if status in VALID_STATUSES else "not_run"


def load_api_checks(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"API report not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_checks = payload.get("checks", payload.get("tests", payload))

    if isinstance(raw_checks, dict):
        raw_checks = [
            {"name": name, **(value if isinstance(value, dict) else {"status": value})}
            for name, value in raw_checks.items()
        ]
    if not isinstance(raw_checks, list):
        raise ValueError("API report must contain a list or mapping of checks")

    checks: list[dict[str, Any]] = []
    for index, item in enumerate(raw_checks, start=1):
        if not isinstance(item, dict):
            item = {"name": f"api_check_{index}", "status": item}
        name = str(item.get("name") or item.get("test") or f"api_check_{index}")
        status_source = item.get("status", item.get("passed", "not_run"))
        check = {"name": name, "status": normalize_status(status_source)}
        http_status = item.get("http_status", item.get("status_code"))
        if http_status is not None:
            check["http_status"] = http_status
        checks.append(check)
    return checks


def plot_checks(checks: list[dict[str, Any]], path: Path) -> None:
    names = [str(check["name"]).replace("_", " ") for check in checks]
    statuses = [str(check["status"]) for check in checks]
    positions = list(range(len(checks)))

    figure_height = max(3.2, 0.52 * len(checks) + 1.3)
    fig, ax = plt.subplots(figsize=(9, figure_height))
    ax.barh(
        positions,
        [1] * len(checks),
        color=[STATUS_COLOURS[status] for status in statuses],
        height=0.62,
    )
    for position, status in zip(positions, statuses):
        ax.text(0.03, position, status.upper(), va="center", color="white", weight="bold")

    ax.set_yticks(positions, labels=names)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_title("Deployment verification status", loc="left", weight="bold")
    ax.spines[:].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)
    fig.tight_layout()

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    checks = load_api_checks(args.api_report)
    checks.append({"name": "container_verification", "status": args.container_status})

    required = [check for check in checks if check["status"] != "skipped"]
    overall_status = (
        "passed"
        if required and all(check["status"] == "passed" for check in required)
        else "failed"
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "checks": checks,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    plot_checks(checks, args.figure)

    print(f"Overall status: {overall_status}")
    print(f"Report written to {args.output}")
    print(f"Figure written to {args.figure}")
    if overall_status != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

