from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.train import FEATURE_COLUMNS


MODEL_PATH = Path("models/model.pkl")


def load_model(model_path: Path = MODEL_PATH) -> Any:
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. Run `python -m src.train` before starting the API."
        )
    return joblib.load(model_path)


def predict_failure(sensor_reading: dict[str, float], model_path: Path | None = None) -> dict[str, Any]:
    model = load_model(model_path or MODEL_PATH)
    frame = pd.DataFrame([sensor_reading], columns=FEATURE_COLUMNS)

    prediction = bool(model.predict(frame)[0])
    probability = float(model.predict_proba(frame)[0][1])
    status = "Machine will fail soon" if prediction else "All good"

    return {
        "failure_prediction": prediction,
        "failure_probability": round(probability, 4),
        "status": status,
    }
