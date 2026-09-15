"""FastAPI inference server for manufacturing defect prediction"""

from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

app = FastAPI()

# Load trained model

model_path = Path("model/model.pkl")

try:
    if not model_path.exists():
        raise FileNotFoundError
except FileNotFoundError:
    print("File does not exist. Run model.py first.")
    model = None
else:
    with open(model_path, "rb") as f:
        model = pickle.load(f)


class ManufacturingData(BaseModel):
    batch_id: int
    timestamp: datetime   # ignored during prediction
    operator_id: str
    temperature: float
    pressure: float
    speed: float
    humidity: float
    material_lot: str


def transform(data: ManufacturingData):

    operator_map = {"OP01": 0, "OP02": 1, "OP03": 2, "OP04": 3}
    material_map = {"LOT-A": 0, "LOT-B": 2, "LOT-C": 1}

    row = [
        data.batch_id,
        operator_map.get(data.operator_id, -1),
        data.temperature,
        data.pressure,
        data.speed,
        data.humidity,
        material_map.get(data.material_lot, -1)
    ]

    columns = [
        "batch_id",
        "operator_id",
        "temperature",
        "pressure",
        "speed",
        "humidity",
        "material_lot"
    ]

    return pd.DataFrame([row], columns=columns)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict(data: ManufacturingData):

    features = transform(data)

    pred_class = model.predict(features)[0]
    pred_prob = model.predict_proba(features)[0][1]

    status = "Not defective" if pred_class == 0 else "Defective"

    return {
        "status": status,
        "probability": float(pred_prob)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
