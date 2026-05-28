# Predictive Maintenance MLOps Project

This project predicts industrial machine failure from sensor readings and exposes the model through a FastAPI service. It also includes a live dashboard that simulates real-time machine telemetry so the project looks like a practical monitoring system during demos.

## Project Structure

```text
.
|-- app/
|   |-- main.py              # FastAPI app and live dashboard
|   |-- schemas.py           # Request/response models
|-- data/
|   |-- ai4i2020.csv         # Full dataset if downloaded
|   |-- sample_sensor_data.csv
|-- models/
|   |-- .gitkeep
|-- src/
|   |-- predict.py           # Model loading and prediction logic
|   |-- simulator.py         # Real-time telemetry simulator
|   |-- train.py             # Training pipeline
|-- tests/
|   |-- test_api.py
|-- Dockerfile
|-- Jenkinsfile
|-- requirements.txt
```

## Local Setup

```powershell
python -m pip install -r requirements.txt
python -m src.train --data-path data\ai4i2020.csv
python -m uvicorn app.main:app --reload
```

Open the live dashboard:

```text
http://127.0.0.1:8000/
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

- `GET /` - real-time predictive maintenance dashboard
- `GET /health` - API health check
- `GET /live` - simulated live machine telemetry plus prediction
- `POST /predict` - prediction for a manual sensor payload

Example prediction payload:

```json
{
  "air_temperature_k": 298.1,
  "process_temperature_k": 308.6,
  "rotational_speed_rpm": 1551,
  "torque_nm": 42.8,
  "tool_wear_min": 0
}
```

The response includes:

- failure prediction
- failure probability
- risk level
- maintenance priority
- estimated time to failure
- maintenance recommendation

## Tests

```powershell
python -m pytest
```

## Docker

Docker is optional for local testing. If Docker is not available on your desktop, run the Python/FastAPI workflow locally and use Docker on AWS EC2 or Jenkins later.

```powershell
docker build -t predictive-maintenance-api .
docker run --rm -p 8000:8000 predictive-maintenance-api
```

## Jenkins and AWS

The `Jenkinsfile` builds the Docker image, runs training and tests inside the image, pushes to Amazon ECR, and deploys to a target EC2 instance over SSH.

Required Jenkins credentials:

- `aws-region`: Secret text, for example `ap-south-1`
- `aws-account-id`: Secret text
- `deploy-host`: Secret text, public DNS or IP of deployment EC2
- `deploy-user`: Secret text, SSH user such as `ubuntu`
- `deploy-ssh-key`: SSH private key credential

Required Jenkins environment:

- Docker installed and usable by the `jenkins` user
- AWS CLI installed
- Jenkins AWS credentials configured through environment, instance profile, or Jenkins credentials binding
