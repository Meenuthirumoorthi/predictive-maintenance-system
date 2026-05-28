from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.schemas import LiveTelemetryResponse, PredictionResponse, SensorReading
from src.predict import predict_failure
from src.simulator import generate_live_telemetry


app = FastAPI(
    title="Predictive Maintenance API",
    version="1.0.0",
    description="Predicts machine failure risk from industrial sensor readings.",
)


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Predictive Maintenance System</title>
  <style>
    :root {
      --bg: #eef2f7;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #647084;
      --line: #dde3ee;
      --ok: #16845b;
      --warn: #b7791f;
      --bad: #c53030;
      --accent: #2563eb;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    header {
      padding: 20px 28px;
      background: #0f172a;
      color: white;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }
    h1 { margin: 0; font-size: 24px; font-weight: 700; }
    h2 { margin: 0 0 14px; font-size: 18px; }
    main { padding: 24px; max-width: 1180px; margin: 0 auto; }
    .layout {
      display: grid;
      grid-template-columns: 390px minmax(0, 1fr);
      gap: 18px;
      align-items: start;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 16px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    }
    .form-row { margin-bottom: 14px; }
    .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0; margin-bottom: 8px; }
    .value { font-size: 26px; font-weight: 700; line-height: 1.1; }
    input, select {
      width: 100%;
      height: 42px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      color: var(--ink);
      font-size: 15px;
      background: #fbfcfe;
    }
    input:focus, select:focus {
      outline: 2px solid rgba(37, 99, 235, 0.2);
      border-color: var(--accent);
    }
    button {
      width: 100%;
      height: 44px;
      border: 0;
      border-radius: 6px;
      background: var(--accent);
      color: white;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
    }
    button.secondary {
      margin-top: 10px;
      background: #334155;
    }
    .status {
      display: inline-flex;
      align-items: center;
      min-height: 32px;
      padding: 6px 10px;
      border-radius: 6px;
      font-weight: 700;
      background: #e8f5ef;
      color: var(--ok);
    }
    .status.Warning { background: #fff7df; color: var(--warn); }
    .status.Critical { background: #ffe8e8; color: var(--bad); }
    .wide { grid-column: span 2; }
    .meter {
      height: 14px;
      background: #e8edf5;
      border-radius: 999px;
      overflow: hidden;
      margin-top: 12px;
    }
    .bar {
      height: 100%;
      width: 0%;
      background: var(--accent);
      transition: width .4s ease, background .4s ease;
    }
    .bar.Warning { background: var(--warn); }
    .bar.Critical { background: var(--bad); }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 12px 10px; border-bottom: 1px solid var(--line); font-size: 14px; }
    th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0; }
    .recommendation { font-size: 17px; line-height: 1.5; }
    .result-title { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 18px; }
    .result-panel { border-left: 5px solid var(--ok); }
    .result-panel.Warning { border-left-color: var(--warn); }
    .result-panel.Critical { border-left-color: var(--bad); }
    .empty {
      min-height: 360px;
      display: grid;
      place-items: center;
      text-align: center;
      color: var(--muted);
    }
    .history {
      margin-top: 16px;
      display: grid;
      gap: 10px;
    }
    .history-item {
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fbfcfe;
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
    }
    .subtle { color: #cbd5e1; font-size: 13px; }
    @media (max-width: 820px) {
      header { align-items: flex-start; flex-direction: column; }
      .layout { grid-template-columns: 1fr; }
      .grid { grid-template-columns: 1fr; }
      .wide { grid-column: span 1; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Predictive Maintenance System</h1>
    <div class="subtle" id="updated">Model ready</div>
  </header>
  <main>
    <section class="layout">
      <form class="panel" id="prediction-form">
        <h2>Machine Sensor Input</h2>
        <div class="form-row">
          <div class="label">Machine</div>
          <select id="machine">
            <option value="CNC-101">CNC-101</option>
            <option value="PUMP-204">PUMP-204</option>
            <option value="PRESS-330">PRESS-330</option>
          </select>
        </div>
        <div class="form-row">
          <div class="label">Air temperature (K)</div>
          <input id="air_temperature_k" type="number" step="0.1" value="298.1">
        </div>
        <div class="form-row">
          <div class="label">Process temperature (K)</div>
          <input id="process_temperature_k" type="number" step="0.1" value="308.6">
        </div>
        <div class="form-row">
          <div class="label">Rotational speed (rpm)</div>
          <input id="rotational_speed_rpm" type="number" step="1" value="1551">
        </div>
        <div class="form-row">
          <div class="label">Torque (Nm)</div>
          <input id="torque_nm" type="number" step="0.1" value="42.8">
        </div>
        <div class="form-row">
          <div class="label">Tool wear (min)</div>
          <input id="tool_wear_min" type="number" step="1" value="0">
        </div>
        <button type="submit">Predict Failure Risk</button>
        <button type="button" class="secondary" id="load-live">Load Live Machine Reading</button>
      </form>

      <div>
        <section class="panel result-panel" id="result-panel">
          <div class="empty" id="empty-state">
            <div>
              <h2>Run a prediction</h2>
              <p>Enter current sensor readings or load a live reading to see maintenance risk, priority, and recommended action.</p>
            </div>
          </div>
          <div id="result" hidden>
            <div class="result-title">
              <div>
                <div class="label">Selected Machine</div>
                <div class="value" id="result-machine">-</div>
              </div>
              <div class="status" id="risk">-</div>
            </div>
            <section class="grid">
              <div>
                <div class="label">Failure Probability</div>
                <div class="value" id="probability">0%</div>
                <div class="meter"><div class="bar" id="bar"></div></div>
              </div>
              <div>
                <div class="label">Maintenance Priority</div>
                <div class="value" id="priority">-</div>
              </div>
              <div>
                <div class="label">Estimated Time To Failure</div>
                <div class="value" id="time-to-failure">-</div>
              </div>
              <div>
                <div class="label">Current Status</div>
                <div class="value" id="status-text">-</div>
              </div>
            </section>
            <div class="label">Recommendation</div>
            <div class="recommendation" id="recommendation">-</div>
          </div>
        </section>

        <section class="panel history">
          <h2>Recent Predictions</h2>
          <div id="history-list">
            <div class="history-item">
              <span>No predictions yet</span>
              <span class="status">Ready</span>
            </div>
          </div>
        </section>
      </div>
    </section>
  </main>
  <script>
    const fields = [
      "air_temperature_k",
      "process_temperature_k",
      "rotational_speed_rpm",
      "torque_nm",
      "tool_wear_min"
    ];
    const history = [];

    function getPayload() {
      return Object.fromEntries(fields.map((field) => [
        field,
        Number(document.getElementById(field).value)
      ]));
    }

    function fillForm(reading) {
      fields.forEach((field) => {
        document.getElementById(field).value = reading[field];
      });
    }

    function renderPrediction(machineId, prediction) {
      const probability = Math.round(prediction.failure_probability * 100);
      document.getElementById("empty-state").hidden = true;
      document.getElementById("result").hidden = false;
      document.getElementById("result-machine").textContent = machineId;
      document.getElementById("risk").textContent = prediction.risk_level;
      document.getElementById("risk").className = "status " + prediction.risk_level;
      document.getElementById("result-panel").className = "panel result-panel " + prediction.risk_level;
      document.getElementById("probability").textContent = probability + "%";
      document.getElementById("priority").textContent = prediction.maintenance_priority;
      document.getElementById("time-to-failure").textContent =
        prediction.estimated_time_to_failure_hours === null
          ? "Not expected"
          : prediction.estimated_time_to_failure_hours + " hrs";
      document.getElementById("status-text").textContent = prediction.status;
      document.getElementById("recommendation").textContent = prediction.recommendation;
      document.getElementById("updated").textContent = "Last prediction: " + new Date().toLocaleString();

      const bar = document.getElementById("bar");
      bar.style.width = probability + "%";
      bar.className = "bar " + prediction.risk_level;

      history.unshift({ machineId, risk: prediction.risk_level, probability });
      history.splice(5);
      document.getElementById("history-list").innerHTML = history.map((item) => `
        <div class="history-item">
          <span>${item.machineId} - ${item.probability}% failure probability</span>
          <span class="status ${item.risk}">${item.risk}</span>
        </div>
      `).join("");
    }

    async function predictCurrentReading(event) {
      event.preventDefault();
      const machineId = document.getElementById("machine").value;
      const response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(getPayload())
      });
      const prediction = await response.json();
      renderPrediction(machineId, prediction);
    }

    async function loadLiveReading() {
      const response = await fetch("/live");
      const data = await response.json();
      document.getElementById("machine").value = data.machine_id;
      fillForm(data.sensor_reading);
      renderPrediction(data.machine_id, data.prediction);
    }

    document.getElementById("prediction-form").addEventListener("submit", predictCurrentReading);
    document.getElementById("load-live").addEventListener("click", loadLiveReading);
  </script>
</body>
</html>
"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(reading: SensorReading) -> PredictionResponse:
    result = predict_failure(reading.model_dump())
    return PredictionResponse(**result)


@app.get("/live", response_model=LiveTelemetryResponse)
def live() -> LiveTelemetryResponse:
    return LiveTelemetryResponse(**generate_live_telemetry())
