#!/usr/bin/env python3
"""Simulate deployment events and generate Chapter 08 monitoring artifacts."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RANDOM_SEED = 42
RESULTS_DIR = Path("results")
FIGURES_DIR = RESULTS_DIR / "figures"
ERROR_THRESHOLD = 0.02
LATENCY_THRESHOLD_MS = 180.0
MISSING_THRESHOLD = 0.03
POSITIVE_RATE_LOWER = 0.25
POSITIVE_RATE_UPPER = 0.55


def simulate_events() -> pd.DataFrame:
    """Create deterministic request-level records with a late-period shift."""
    rng = np.random.default_rng(RANDOM_SEED)
    rows: list[dict[str, object]] = []
    start = pd.Timestamp("2026-07-21", tz="UTC")

    for day_index in range(14):
        shifted = day_index >= 10
        requests = int(rng.integers(360, 520))
        day = start + pd.Timedelta(days=day_index)

        feature = rng.normal(0.9 if shifted else 0.0, 1.05, requests)
        missing_probability = 0.055 if shifted else 0.012
        feature_missing = rng.random(requests) < missing_probability
        observed_feature = feature.copy()
        observed_feature[feature_missing] = np.nan

        linear_score = -0.55 + 0.85 * np.nan_to_num(observed_feature, nan=0.0)
        probability = 1 / (1 + np.exp(-linear_score))
        prediction = (probability >= 0.5).astype(int)

        latency = rng.lognormal(
            mean=np.log(135 if shifted else 65), sigma=0.32, size=requests
        )
        error_probability = 0.045 if shifted else 0.008
        is_error = rng.random(requests) < error_probability

        for event_index in range(requests):
            timestamp = day + pd.Timedelta(
                seconds=int(rng.integers(0, 24 * 60 * 60))
            )
            rows.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "request_id": f"req-{day_index:02d}-{event_index:04d}",
                    "model_version": "churn-pipeline-1.2.0",
                    "status_code": 500 if is_error[event_index] else 200,
                    "latency_ms": round(float(latency[event_index]), 2),
                    "feature_value": observed_feature[event_index],
                    "feature_missing": bool(feature_missing[event_index]),
                    "prediction": int(prediction[event_index]),
                    "probability": round(float(probability[event_index]), 6),
                    "is_error": bool(is_error[event_index]),
                }
            )

    return pd.DataFrame(rows)


def aggregate_daily(events: pd.DataFrame) -> pd.DataFrame:
    """Aggregate operational and prediction signals by UTC date."""
    working = events.copy()
    working["date"] = pd.to_datetime(working["timestamp"], utc=True).dt.date
    return working.groupby("date", as_index=False).agg(
        requests=("request_id", "size"),
        error_rate=("is_error", "mean"),
        p95_latency_ms=("latency_ms", lambda values: values.quantile(0.95)),
        missing_rate=("feature_missing", "mean"),
        positive_rate=("prediction", "mean"),
        mean_probability=("probability", "mean"),
    )


def evaluate_alerts(daily: pd.DataFrame) -> pd.DataFrame:
    """Evaluate each daily metric against explicit monitoring rules."""
    alert_rows: list[dict[str, object]] = []
    rules = (
        ("error_rate", "maximum", ERROR_THRESHOLD),
        ("p95_latency_ms", "maximum", LATENCY_THRESHOLD_MS),
        ("missing_rate", "maximum", MISSING_THRESHOLD),
    )

    for row in daily.itertuples(index=False):
        for metric, comparison, threshold in rules:
            value = float(getattr(row, metric))
            alert_rows.append(
                {
                    "date": row.date,
                    "metric": metric,
                    "value": value,
                    "comparison": comparison,
                    "threshold": threshold,
                    "status": "ALERT" if value > threshold else "OK",
                }
            )

        positive_rate = float(row.positive_rate)
        outside_range = not POSITIVE_RATE_LOWER <= positive_rate <= POSITIVE_RATE_UPPER
        alert_rows.append(
            {
                "date": row.date,
                "metric": "positive_rate",
                "value": positive_rate,
                "comparison": "outside_range",
                "threshold": f"{POSITIVE_RATE_LOWER}-{POSITIVE_RATE_UPPER}",
                "status": "ALERT" if outside_range else "OK",
            }
        )

    return pd.DataFrame(alert_rows)


def population_stability_index(
    reference: pd.Series, current: pd.Series, bins: int = 10
) -> tuple[float, np.ndarray]:
    """Calculate PSI using reference quantile bins."""
    reference = reference.dropna().to_numpy()
    current = current.dropna().to_numpy()
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    reference_counts, _ = np.histogram(reference, bins=edges)
    current_counts, _ = np.histogram(current, bins=edges)
    epsilon = 1e-6
    reference_share = np.clip(reference_counts / reference_counts.sum(), epsilon, None)
    current_share = np.clip(current_counts / current_counts.sum(), epsilon, None)
    psi = np.sum((current_share - reference_share) * np.log(current_share / reference_share))
    return float(psi), edges


def plot_dashboard(daily: pd.DataFrame) -> None:
    """Create a compact daily monitoring dashboard."""
    dates = pd.to_datetime(daily["date"])
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=True)
    color = "#036281"
    alert = "#c2410c"

    axes[0, 0].plot(dates, daily["requests"], marker="o", color=color)
    axes[0, 0].set_title("Request volume")
    axes[0, 0].set_ylabel("Requests")

    axes[0, 1].plot(dates, daily["error_rate"] * 100, marker="o", color=color)
    axes[0, 1].axhline(ERROR_THRESHOLD * 100, color=alert, linestyle="--")
    axes[0, 1].set_title("Error rate")
    axes[0, 1].set_ylabel("Percent")

    axes[1, 0].plot(dates, daily["p95_latency_ms"], marker="o", color=color)
    axes[1, 0].axhline(LATENCY_THRESHOLD_MS, color=alert, linestyle="--")
    axes[1, 0].set_title("p95 latency")
    axes[1, 0].set_ylabel("Milliseconds")

    axes[1, 1].plot(dates, daily["positive_rate"] * 100, marker="o", color=color)
    axes[1, 1].axhline(POSITIVE_RATE_LOWER * 100, color=alert, linestyle="--")
    axes[1, 1].axhline(POSITIVE_RATE_UPPER * 100, color=alert, linestyle="--")
    axes[1, 1].set_title("Positive prediction rate")
    axes[1, 1].set_ylabel("Percent")

    for axis in axes.flat:
        axis.grid(alpha=0.2)
        axis.tick_params(axis="x", rotation=35)
        axis.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Deployment monitoring dashboard", fontsize=16, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "08-monitoring-dashboard.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_drift(reference: pd.Series, current: pd.Series, psi: float) -> None:
    """Visualise the reference and current feature distributions."""
    fig, axis = plt.subplots(figsize=(9, 5.5))
    axis.hist(reference.dropna(), bins=28, density=True, alpha=0.55, label="Reference", color="#036281")
    axis.hist(current.dropna(), bins=28, density=True, alpha=0.50, label="Current", color="#f59e0b")
    axis.set_title(f"Feature distribution drift (PSI = {psi:.3f})", fontweight="bold")
    axis.set_xlabel("Feature value")
    axis.set_ylabel("Density")
    axis.legend(frameon=False)
    axis.grid(axis="y", alpha=0.2)
    axis.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "08-feature-drift.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Run the complete monitoring demonstration."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    events = simulate_events()
    daily = aggregate_daily(events)
    alerts = evaluate_alerts(daily)

    event_dates = pd.to_datetime(events["timestamp"], utc=True).dt.date
    split_date = sorted(event_dates.unique())[7]
    reference = events.loc[event_dates < split_date, "feature_value"]
    current = events.loc[event_dates >= split_date, "feature_value"]
    psi, edges = population_stability_index(reference, current)
    drift = pd.DataFrame(
        {
            "feature": ["feature_value"],
            "reference_observations": [reference.notna().sum()],
            "current_observations": [current.notna().sum()],
            "psi": [psi],
            "quantile_bins": [len(edges) - 1],
        }
    )

    events.to_csv(RESULTS_DIR / "08-inference-events.csv", index=False)
    daily.to_csv(RESULTS_DIR / "08-daily-monitoring-metrics.csv", index=False)
    alerts.to_csv(RESULTS_DIR / "08-monitoring-alerts.csv", index=False)
    drift.to_csv(RESULTS_DIR / "08-drift-summary.csv", index=False)
    plot_dashboard(daily)
    plot_drift(reference, current, psi)

    alert_count = int((alerts["status"] == "ALERT").sum())
    print(f"Events generated: {len(events):,}")
    print(f"Daily windows: {len(daily)}")
    print(f"Threshold breaches: {alert_count}")
    print(f"Feature PSI: {psi:.3f}")
    print(f"Artifacts written to {RESULTS_DIR}")


if __name__ == "__main__":
    main()

