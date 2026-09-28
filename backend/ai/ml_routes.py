from fastapi import APIRouter
from .ml.model_service import ml_service
from .ml.train import train_all
from .ml.train_xgb import train_xgb
from .ml.train_lstm import train_lstm
from .ml.lstm_service import lstm_service
from .maintenance_service import maintenance_service

router = APIRouter(
    prefix="/ai/ml",
    tags=["AI / ML"]
)


@router.get("/status")
def ml_status():
    status = ml_service.status()
    status["models"]["lstm_fault_classifier"] = lstm_service.ready
    return status


@router.get("/metrics")
def ml_metrics():
    return ml_service.metrics


@router.get("/predict")
def ml_predict():
    return ml_service.predict_live()


@router.get("/lstm-predict")
def ml_lstm_predict():
    result = lstm_service.predict_live()
    if result is None:
        return {"ready": False, "message": "Train the LSTM first with POST /ai/ml/train-lstm"}
    return result


@router.get("/maintenance")
def ml_maintenance():
    prediction = ml_service.predict_live()
    return maintenance_service.recommend(prediction)


@router.get("/explain")
def ml_explain():
    prediction = ml_service.predict_live()
    return prediction.get("explanation", {})


@router.post("/train")
def ml_train():
    metrics = train_all()
    ml_service.reload()
    return {
        "status": "success",
        "message": "Core ML models retrained successfully",
        "metrics": metrics
    }


@router.post("/train-xgb")
def ml_train_xgb():
    metrics = train_xgb()
    ml_service.reload()
    return {
        "status": "success",
        "message": "XGBoost fault classifier trained successfully",
        "metrics": metrics
    }


@router.post("/train-lstm")
def ml_train_lstm():
    metrics = train_lstm()
    lstm_service.reload()
    return {
        "status": "success",
        "message": "LSTM fault classifier trained successfully",
        "metrics": metrics
    }
