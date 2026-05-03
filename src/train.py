from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = [
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
]
TARGET_COLUMN = "machine_failure"

AI4I_COLUMN_MAP = {
    "Air temperature [K]": "air_temperature_k",
    "Process temperature [K]": "process_temperature_k",
    "Rotational speed [rpm]": "rotational_speed_rpm",
    "Torque [Nm]": "torque_nm",
    "Tool wear [min]": "tool_wear_min",
    "Machine failure": "machine_failure",
}


def load_dataset(data_path: Path) -> pd.DataFrame:
    data = pd.read_csv(data_path)
    data = data.rename(columns=AI4I_COLUMN_MAP)

    missing = [column for column in [*FEATURE_COLUMNS, TARGET_COLUMN] if column not in data.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")

    return data[[*FEATURE_COLUMNS, TARGET_COLUMN]].dropna()


def train_model(data: pd.DataFrame) -> tuple[Pipeline, float, str]:
    x = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN]

    stratify = y if y.nunique() > 1 and y.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=stratify,
    )

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    max_depth=8,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, zero_division=0)
    return model, accuracy, report


def save_model(model: Pipeline, model_path: Path) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the predictive maintenance model.")
    parser.add_argument("--data-path", type=Path, default=Path("data/sample_sensor_data.csv"))
    parser.add_argument("--model-path", type=Path, default=Path("models/model.pkl"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = load_dataset(args.data_path)
    model, accuracy, report = train_model(data)
    save_model(model, args.model_path)

    print(f"Saved model to {args.model_path}")
    print(f"Validation accuracy: {accuracy:.3f}")
    print(report)


if __name__ == "__main__":
    main()

