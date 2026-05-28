from __future__ import annotations

import random
from datetime import datetime, timezone
from itertools import count
from typing import Any

from src.predict import predict_failure


MACHINES = {
    "CNC-101": {
        "air_temperature_k": 298.4,
        "process_temperature_k": 309.0,
        "rotational_speed_rpm": 1520,
        "torque_nm": 41.5,
        "tool_wear_min": 34,
    },
    "PUMP-204": {
        "air_temperature_k": 300.1,
        "process_temperature_k": 310.7,
        "rotational_speed_rpm": 1390,
        "torque_nm": 52.0,
        "tool_wear_min": 96,
    },
    "PRESS-330": {
        "air_temperature_k": 302.4,
        "process_temperature_k": 312.9,
        "rotational_speed_rpm": 1215,
        "torque_nm": 66.5,
        "tool_wear_min": 168,
    },
}

_tick = count(1)


def generate_live_telemetry() -> dict[str, Any]:
    step = next(_tick)
    machine_id = random.choice(list(MACHINES))
    baseline = MACHINES[machine_id]
    wear_growth = step % 90

    reading = {
        "air_temperature_k": round(baseline["air_temperature_k"] + random.uniform(-0.6, 1.2), 2),
        "process_temperature_k": round(baseline["process_temperature_k"] + random.uniform(-0.4, 1.6), 2),
        "rotational_speed_rpm": round(baseline["rotational_speed_rpm"] + random.uniform(-65, 35), 2),
        "torque_nm": round(baseline["torque_nm"] + random.uniform(-2.5, 5.0), 2),
        "tool_wear_min": round(baseline["tool_wear_min"] + wear_growth + random.uniform(-3, 3), 2),
    }

    return {
        "machine_id": machine_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sensor_reading": reading,
        "prediction": predict_failure(reading),
    }
