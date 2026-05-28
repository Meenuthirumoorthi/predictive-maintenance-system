from fastapi.testclient import TestClient

from app.main import app
from src.train import load_dataset, save_model, train_model


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint(tmp_path, monkeypatch) -> None:
    data = load_dataset("data/sample_sensor_data.csv")
    model, _, _ = train_model(data)
    model_path = tmp_path / "model.pkl"
    save_model(model, model_path)

    monkeypatch.setattr("src.predict.MODEL_PATH", model_path)

    client = TestClient(app)
    response = client.post(
        "/predict",
        json={
            "air_temperature_k": 298.1,
            "process_temperature_k": 308.6,
            "rotational_speed_rpm": 1551,
            "torque_nm": 42.8,
            "tool_wear_min": 0,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "failure_prediction" in body
    assert 0 <= body["failure_probability"] <= 1
    assert body["risk_level"] in {"Normal", "Warning", "Critical"}
    assert body["status"] in {"All good", "Failure risk increasing", "Machine will fail soon"}


def test_live_endpoint(tmp_path, monkeypatch) -> None:
    data = load_dataset("data/sample_sensor_data.csv")
    model, _, _ = train_model(data)
    model_path = tmp_path / "model.pkl"
    save_model(model, model_path)

    monkeypatch.setattr("src.predict.MODEL_PATH", model_path)

    client = TestClient(app)
    response = client.get("/live")

    assert response.status_code == 200
    body = response.json()
    assert body["machine_id"]
    assert "sensor_reading" in body
    assert "prediction" in body
