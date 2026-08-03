"""Tests for API health, prediction, and validation behavior."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
API_PATH = ROOT / "scripts" / "python" / "05-model-api.py"
MODEL_PATH = ROOT / "models" / "iris-classifier.joblib"

if not MODEL_PATH.exists():
    subprocess.run([sys.executable, ROOT / "scripts/python/02-train-deployment-model.py"], check=True)

spec = importlib.util.spec_from_file_location("model_api", API_PATH)
assert spec and spec.loader
model_api = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = model_api
spec.loader.exec_module(model_api)
client = TestClient(model_api.app)


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_prediction() -> None:
    response = client.post("/predict", json={"sepal_length": 5.1, "sepal_width": 3.5,
                           "petal_length": 1.4, "petal_width": 0.2})
    assert response.status_code == 200
    assert response.json()["predicted_label"] == "setosa"


def test_invalid_measurement_is_rejected() -> None:
    response = client.post("/predict", json={"sepal_length": -1, "sepal_width": 3.5,
                           "petal_length": 1.4, "petal_width": 0.2})
    assert response.status_code == 422
