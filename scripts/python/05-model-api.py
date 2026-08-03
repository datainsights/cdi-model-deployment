#!/usr/bin/env python3
"""Serve predictions from the persisted scikit-learn pipeline."""

from functools import lru_cache
from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "iris-classifier.joblib"


class IrisFeatures(BaseModel):
    sepal_length: float = Field(gt=0)
    sepal_width: float = Field(gt=0)
    petal_length: float = Field(gt=0)
    petal_width: float = Field(gt=0)


class Prediction(BaseModel):
    predicted_class: int
    predicted_label: str
    model_version: str


@lru_cache
def load_artifact() -> dict:
    return joblib.load(MODEL_PATH)


app = FastAPI(title="CDI Iris Model API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=Prediction)
def predict(features: IrisFeatures) -> Prediction:
    artifact = load_artifact()
    values = [[features.sepal_length, features.sepal_width, features.petal_length, features.petal_width]]
    frame = pd.DataFrame(values, columns=artifact["feature_names"])
    predicted_class = int(artifact["pipeline"].predict(frame)[0])
    return Prediction(predicted_class=predicted_class,
                      predicted_label=artifact["target_names"][predicted_class],
                      model_version=artifact["model_version"])
