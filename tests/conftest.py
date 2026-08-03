"""Shared fixtures for the Chapter 05 API tests."""

from collections.abc import AsyncIterator

import numpy as np
import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient

import api_import_helper


class DeterministicPipeline:
    """Fitted-pipeline stand-in for testing the breast-cancer HTTP contract."""

    classes_ = np.array([0, 1])

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        assert list(frame.columns) == api_import_helper.api_module.EXPECTED_FEATURE_NAMES
        return np.array([0])

    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        assert len(frame) == 1
        return np.array([[0.982, 0.018]])


@pytest.fixture
def anyio_backend() -> str:
    """Run async tests with asyncio; Trio is not required by this guide."""

    return "asyncio"


@pytest.fixture
def valid_payload() -> dict[str, float]:
    return {
        "mean_radius": 17.99,
        "mean_texture": 10.38,
        "mean_perimeter": 122.8,
        "mean_area": 1001.0,
        "mean_smoothness": 0.1184,
        "mean_compactness": 0.2776,
        "mean_concavity": 0.3001,
        "mean_concave_points": 0.1471,
    }


@pytest.fixture
async def client(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[AsyncClient]:
    artifact = {
        "pipeline": DeterministicPipeline(),
        "model_version": "breast-cancer-logistic-v1",
        "feature_names": api_import_helper.api_module.EXPECTED_FEATURE_NAMES,
        "target_names": {0: "malignant", 1: "benign"},
    }
    monkeypatch.setattr(
        api_import_helper.api_module.joblib,
        "load",
        lambda _path: artifact,
    )

    app = api_import_helper.app
    transport = ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client:
            yield test_client
