#!/usr/bin/env python3
"""Send one breast-cancer prediction request to the local Chapter 05 API."""

import httpx


API_URL = "http://127.0.0.1:8000/predict"
PAYLOAD = {
    "mean_radius": 17.99,
    "mean_texture": 10.38,
    "mean_perimeter": 122.8,
    "mean_area": 1001.0,
    "mean_smoothness": 0.1184,
    "mean_compactness": 0.2776,
    "mean_concavity": 0.3001,
    "mean_concave_points": 0.1471,
}


def main() -> None:
    """Call the local prediction endpoint and display its JSON response."""

    response = httpx.post(API_URL, json=PAYLOAD, timeout=10.0)
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
