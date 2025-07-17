# model_api.py

import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np

# Load all models from the models/ folder
MODEL_DIR = "models"
models = {}

for fname in os.listdir(MODEL_DIR):
    if fname.endswith(".joblib"):
        model_name = fname.replace(".joblib", "")
        model_path = os.path.join(MODEL_DIR, fname)
        models[model_name] = joblib.load(model_path)

# Initialize FastAPI app
app = FastAPI()

# Define input format
class InputData(BaseModel):
    Pclass: int
    Sex: int
    Age: float
    Fare: float
    Embarked: int

class PredictionOutput(BaseModel):
    model: str
    prediction: int

# API endpoint for listing available models
@app.get("/models")
def get_model_list():
    return {"available_models": list(models.keys())}

# API endpoint for predicting using a selected model
@app.post("/predict/{model_name}", response_model=PredictionOutput)
def predict(model_name: str, input_data: InputData):
    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")

    model = models[model_name]

    # Convert input into DataFrame
    input_df = pd.DataFrame([input_data.dict()])

    try:
        prediction = model.predict(input_df)[0]
        return PredictionOutput(model=model_name, prediction=int(prediction))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")