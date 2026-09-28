# IndustrialAI — AI/ML Stack

## Pipeline

PLC / servo telemetry -> edge feature engineering -> anomaly detection -> fault classification -> sequence model -> ensemble -> explainability -> predictive maintenance -> dashboard.

## Models

- Isolation Forest: unsupervised anomaly detection.
- Random Forest: multi-class fault classification.
- XGBoost: second fault classifier used for model agreement.
- Random Forest Regressor: next-cycle duration prediction.
- PyTorch LSTM: sequential fault classification from the latest cycle window.
- SHAP: local feature-level explanations, with Random Forest feature importance as a fallback.

## Fault classes

`NORMAL`, `SERVO_LAG`, `VIBRATION`, `STUCK_AXIS`, `SENSOR_NOISE`, `CYCLE_DEGRADATION`

## API

- `GET /ai/ml/status`
- `GET /ai/ml/metrics`
- `GET /ai/ml/predict`
- `GET /ai/ml/lstm-predict`
- `GET /ai/ml/explain`
- `GET /ai/ml/maintenance`
- `POST /ai/ml/train`
- `POST /ai/ml/train-xgb`
- `POST /ai/ml/train-lstm`

## Local setup

```powershell
python -m pip install -r requirements.txt
python -m backend.ai.ml.train
python -m backend.ai.ml.train_xgb
python -m backend.ai.ml.train_lstm
```

Start the backend normally, then open `/ai` in the React application.

## Important evaluation note

The initial training pipeline uses controlled synthetic fault data. The reported metrics therefore measure performance on the synthetic benchmark, not production machine reliability. The next project stage is to collect real completed-cycle telemetry, label faults, create a time-aware train/validation/test split, and report performance on held-out real cycles.
