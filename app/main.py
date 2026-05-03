from fastapi import FastAPI

from app.schemas import PredictionResponse, SensorReading
from src.predict import predict_failure


app = FastAPI(
    title="Predictive Maintenance API",
    version="1.0.0",
    description="Predicts machine failure risk from industrial sensor readings.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(reading: SensorReading) -> PredictionResponse:
    result = predict_failure(reading.model_dump())
    return PredictionResponse(**result)

