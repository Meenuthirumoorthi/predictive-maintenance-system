# Predictive Maintenance MLOps Project

End-to-end starter project for predicting industrial equipment failure from sensor data, serving the model with FastAPI, packaging it with Docker, and automating build/test/deploy through Jenkins and AWS ECR.

## Project Structure

```text
.
├── app/
│   ├── main.py              # FastAPI application
│   └── schemas.py           # Request/response models
├── data/
│   └── sample_sensor_data.csv
├── models/
│   └── .gitkeep
├── src/
│   ├── predict.py           # Model loading and inference helper
│   └── train.py             # Training pipeline
├── tests/
│   └── test_api.py
├── Dockerfile
├── Jenkinsfile
└── requirements.txt
```

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.train
uvicorn app.main:app --reload
```

Open the API docs at:

```text
http://127.0.0.1:8000/docs
```

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

## Tests

```powershell
pytest
```

## Docker

```powershell
docker build -t predictive-maintenance-api .
docker run --rm -p 8000:8000 predictive-maintenance-api
```

## Using the AI4I 2020 Dataset

The included CSV is a tiny sample so the project runs immediately. For the full dataset, download the AI4I 2020 Predictive Maintenance Dataset from UCI or Kaggle and pass its path to the trainer:

```powershell
python -m src.train --data-path path\to\ai4i2020.csv --model-path models\model.pkl
```

The trainer expects columns equivalent to:

- `Air temperature [K]`
- `Process temperature [K]`
- `Rotational speed [rpm]`
- `Torque [Nm]`
- `Tool wear [min]`
- `Machine failure`

It also accepts this repo's normalized column names.

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

