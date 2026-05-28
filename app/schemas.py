from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    air_temperature_k: float = Field(..., gt=250, lt=400)
    process_temperature_k: float = Field(..., gt=250, lt=450)
    rotational_speed_rpm: float = Field(..., gt=0, lt=5000)
    torque_nm: float = Field(..., ge=0, lt=500)
    tool_wear_min: float = Field(..., ge=0, lt=1000)


class PredictionResponse(BaseModel):
    failure_prediction: bool
    failure_probability: float
    risk_level: str
    maintenance_priority: str
    recommendation: str
    estimated_time_to_failure_hours: int | None
    status: str


class LiveTelemetryResponse(BaseModel):
    machine_id: str
    timestamp: str
    sensor_reading: SensorReading
    prediction: PredictionResponse
