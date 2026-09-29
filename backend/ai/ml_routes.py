from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .ml.model_service import ml_service
from .ml.train import train_all
from .ml.train_xgb import train_xgb
from .ml.train_lstm import train_lstm
from .ml.lstm_service import lstm_service
from .maintenance_service import maintenance_service
from .fault_injection_service import fault_injection_service
from .rul_service import rul_service
from .model_performance_service import get_model_performance


router = APIRouter(prefix="/ai/ml", tags=["AI / ML"])


class FaultInjectionPayload(BaseModel):
    fault: str
    severity: float = Field(default=0.6, ge=0.05, le=1.0)
    axis: str = "a2"


@router.get("/status")
def ml_status():
    status = ml_service.status()
    status["models"]["lstm_fault_classifier"] = lstm_service.ready
    status["fault_injection"] = fault_injection_service.status()
    return status


@router.get("/metrics")
def ml_metrics():
    return ml_service.metrics


@router.get("/performance")
def ml_performance():
    return get_model_performance()


@router.get("/predict")
def ml_predict():
    injection = fault_injection_service.status()
    if not injection["active"]:
        return ml_service.predict_live()

    rows = ml_service.get_latest_cycle()
    if not rows:
        raise HTTPException(status_code=503, detail="No telemetry available for fault-injection inference.")

    from .ml.features import cycle_to_features
    base_features = cycle_to_features(rows)
    simulated_features = fault_injection_service.apply(base_features)
    cycle = rows[-1].get("cycle", {}) or {}
    return ml_service.predict_features(
        simulated_features,
        context={
            "machine_state": rows[-1].get("state", "IDLE"),
            "cycle_number": cycle.get("number", 0),
            "cycle_running": cycle.get("running", False),
            "timestamp": rows[-1].get("timestamp"),
            "samples_used": len(rows),
            "simulation": {
                "injection": injection["injection"],
                "base_features": base_features,
            },
        },
    )


@router.get("/lstm-predict")
def ml_lstm_predict():
    result = lstm_service.predict_live()
    if result is None:
        return {"ready": False, "message": "Train the LSTM first with POST /ai/ml/train-lstm"}
    return result


@router.get("/maintenance")
def ml_maintenance():
    return maintenance_service.recommend(ml_predict())


@router.get("/rul")
def ml_rul():
    prediction = ml_service.predict_live()
    return rul_service.predict(prediction.get("anomaly_score", 0.0))


@router.get("/explain")
def ml_explain():
    return ml_predict().get("explanation", {})


@router.get("/fault-injection")
def fault_injection_status():
    return fault_injection_service.status()


@router.post("/fault-injection")
def fault_injection(payload: FaultInjectionPayload):
    try:
        return fault_injection_service.set(
            fault=payload.fault,
            severity=payload.severity,
            axis=payload.axis,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/fault-injection")
def clear_fault_injection():
    return fault_injection_service.clear()


@router.post("/train")
def ml_train():
    metrics = train_all()
    ml_service.reload()
    return {"status": "success", "message": "Core ML models retrained successfully", "metrics": metrics}


@router.post("/train-xgb")
def ml_train_xgb():
    metrics = train_xgb()
    ml_service.reload()
    return {"status": "success", "message": "XGBoost fault classifier trained successfully", "metrics": metrics}


@router.post("/train-lstm")
def ml_train_lstm():
    metrics = train_lstm()
    lstm_service.reload()
    return {"status": "success", "message": "LSTM fault classifier trained successfully", "metrics": metrics}
