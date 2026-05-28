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


def build_maintenance_context(sensor_reading: dict[str, float], probability: float) -> dict[str, Any]:
    torque = sensor_reading["torque_nm"]
    speed = sensor_reading["rotational_speed_rpm"]
    tool_wear = sensor_reading["tool_wear_min"]
    process_temp = sensor_reading["process_temperature_k"]

    operating_stress = 0.0
    if torque >= 60:
        operating_stress += 0.18
    if speed <= 1300:
        operating_stress += 0.12
    if tool_wear >= 150:
        operating_stress += 0.16
    if process_temp >= 312:
        operating_stress += 0.08

    adjusted_probability = min(0.99, probability + operating_stress)

    if adjusted_probability >= 0.65:
        return {
            "probability": adjusted_probability,
            "risk_level": "Critical",
            "maintenance_priority": "Immediate inspection",
            "recommendation": "Schedule maintenance now. Check tool wear, torque load, and heat dissipation.",
            "estimated_time_to_failure_hours": 6,
            "status": "Machine will fail soon",
        }
    if adjusted_probability >= 0.35:
        return {
            "probability": adjusted_probability,
            "risk_level": "Warning",
            "maintenance_priority": "Inspect within 24 hours",
            "recommendation": "Monitor closely and plan preventive maintenance during the next available stop.",
            "estimated_time_to_failure_hours": 24,
            "status": "Failure risk increasing",
        }
    return {
        "probability": adjusted_probability,
        "risk_level": "Normal",
        "maintenance_priority": "Routine monitoring",
        "recommendation": "Continue normal operation and keep monitoring sensor trends.",
        "estimated_time_to_failure_hours": None,
        "status": "All good",
    }


def predict_failure(sensor_reading: dict[str, float], model_path: Path | None = None) -> dict[str, Any]:
    model = load_model(model_path or MODEL_PATH)
    frame = pd.DataFrame([sensor_reading], columns=FEATURE_COLUMNS)

    model_prediction = bool(model.predict(frame)[0])
    probability = float(model.predict_proba(frame)[0][1])
    context = build_maintenance_context(sensor_reading, probability)
    prediction = model_prediction or context["risk_level"] in {"Critical", "Warning"}

    return {
        "failure_prediction": prediction,
        "failure_probability": round(context["probability"], 4),
        "risk_level": context["risk_level"],
        "maintenance_priority": context["maintenance_priority"],
        "recommendation": context["recommendation"],
        "estimated_time_to_failure_hours": context["estimated_time_to_failure_hours"],
        "status": context["status"],
    }
