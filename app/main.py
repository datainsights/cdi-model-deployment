#!/usr/bin/env python3
"""Serve predictions from the Chapter 03 breast-cancer pipeline artifact."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field


MODEL_PATH = Path("models/03-breast-cancer-pipeline.joblib")
POSITIVE_CLASS = 0
EXPECTED_FEATURE_NAMES = [
    "mean radius",
    "mean texture",
    "mean perimeter",
    "mean area",
    "mean smoothness",
    "mean compactness",
    "mean concavity",
    "mean concave points",
]
EXPECTED_TARGET_NAMES = {0: "malignant", 1: "benign"}
API_TO_MODEL_FIELDS = {
    "mean_radius": "mean radius",
    "mean_texture": "mean texture",
    "mean_perimeter": "mean perimeter",
    "mean_area": "mean area",
    "mean_smoothness": "mean smoothness",
    "mean_compactness": "mean compactness",
    "mean_concavity": "mean concavity",
    "mean_concave_points": "mean concave points",
}


class PredictionRequest(BaseModel):
    """Validated measurements for one tumour observation."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "mean_radius": 17.99,
                    "mean_texture": 10.38,
                    "mean_perimeter": 122.8,
                    "mean_area": 1001.0,
                    "mean_smoothness": 0.1184,
                    "mean_compactness": 0.2776,
                    "mean_concavity": 0.3001,
                    "mean_concave_points": 0.1471,
                }
            ]
        },
    )

    mean_radius: float = Field(gt=0)
    mean_texture: float = Field(ge=0)
    mean_perimeter: float = Field(gt=0)
    mean_area: float = Field(gt=0)
    mean_smoothness: float = Field(ge=0)
    mean_compactness: float = Field(ge=0)
    mean_concavity: float = Field(ge=0)
    mean_concave_points: float = Field(ge=0)

    def to_model_frame(self) -> pd.DataFrame:
        """Return a one-row frame with the exact Chapter 03 feature names."""

        values = self.model_dump()
        row = {
            model_name: values[api_name]
            for api_name, model_name in API_TO_MODEL_FIELDS.items()
        }
        return pd.DataFrame([row], columns=EXPECTED_FEATURE_NAMES)


class PredictionResponse(BaseModel):
    """Stable response for a successful breast-cancer prediction."""

    prediction: int
    label: Literal["malignant", "benign"]
    probability_malignant: float = Field(ge=0.0, le=1.0)
    model_version: str


class HealthResponse(BaseModel):
    """Readiness response returned after artifact validation."""

    status: Literal["ready"]
    model_version: str


def load_and_validate_artifact(path: Path) -> tuple[object, str, dict[int, str]]:
    """Load the Chapter 03 artifact and validate its serving metadata."""

    artifact = joblib.load(path)
    required = {"pipeline", "model_version", "feature_names", "target_names"}
    if not isinstance(artifact, dict) or not required.issubset(artifact):
        raise ValueError("Model artifact does not satisfy the Chapter 03 contract.")
    if artifact["feature_names"] != EXPECTED_FEATURE_NAMES:
        raise ValueError("Artifact feature names do not match the API contract.")
    if artifact["target_names"] != EXPECTED_TARGET_NAMES:
        raise ValueError("Artifact target names do not match the API contract.")

    pipeline = artifact["pipeline"]
    if list(pipeline.classes_) != [0, 1]:
        raise ValueError("Artifact classes must be ordered as [0, 1].")
    return pipeline, str(artifact["model_version"]), artifact["target_names"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load and validate the fitted artifact once per application process."""

    pipeline, model_version, target_names = load_and_validate_artifact(MODEL_PATH)
    app.state.model = pipeline
    app.state.model_version = model_version
    app.state.target_names = target_names
    yield
    app.state.model = None


app = FastAPI(
    title="CDI Breast Cancer Prediction API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    """Report whether the validated pipeline is ready."""

    if getattr(request.app.state, "model", None) is None:
        raise HTTPException(status_code=503, detail="Model is not ready")
    return HealthResponse(
        status="ready",
        model_version=request.app.state.model_version,
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    """Return the predicted class and malignant-class probability."""

    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not ready")

    frame = payload.to_model_frame()
    try:
        predicted_class = int(model.predict(frame)[0])
        positive_index = list(model.classes_).index(POSITIVE_CLASS)
        probability = float(model.predict_proba(frame)[0, positive_index])
        label = request.app.state.target_names[predicted_class]
    except (AttributeError, IndexError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail="Input could not be processed by the model",
        ) from exc

    return PredictionResponse(
        prediction=predicted_class,
        label=label,
        probability_malignant=probability,
        model_version=request.app.state.model_version,
    )
