"""Contract tests for the Chapter 05 FastAPI application."""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.anyio


async def test_health_reports_artifact_version(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "model_version": "breast-cancer-logistic-v1",
    }


async def test_predict_returns_breast_cancer_contract(
    client: AsyncClient,
    valid_payload: dict[str, float],
) -> None:
    response = await client.post("/predict", json=valid_payload)
    assert response.status_code == 200
    assert response.json() == {
        "prediction": 0,
        "label": "malignant",
        "probability_malignant": 0.982,
        "model_version": "breast-cancer-logistic-v1",
    }


async def test_predict_rejects_missing_feature(
    client: AsyncClient,
    valid_payload: dict[str, float],
) -> None:
    invalid_payload = valid_payload.copy()
    invalid_payload.pop("mean_area")
    response = await client.post("/predict", json=invalid_payload)
    assert response.status_code == 422


async def test_predict_rejects_unknown_field(
    client: AsyncClient,
    valid_payload: dict[str, float],
) -> None:
    invalid_payload = valid_payload | {"unexpected": 1.0}
    response = await client.post("/predict", json=invalid_payload)
    assert response.status_code == 422


async def test_predict_rejects_impossible_radius(
    client: AsyncClient,
    valid_payload: dict[str, float],
) -> None:
    invalid_payload = valid_payload | {"mean_radius": -4.0}
    response = await client.post("/predict", json=invalid_payload)
    assert response.status_code == 422
