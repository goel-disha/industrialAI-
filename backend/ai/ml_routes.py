from fastapi import APIRouter
from .ml.model_service import ml_service
from .ml.train import train_all
from .ml.train_xgb import train_xgb
from .maintenance_service import maintenance_service

router = APIRouter(
    prefix="/ai/ml",
    tags=["AI / ML"]
)


@router.get("/status")
def ml_status():
    return ml_service.status()


@router.get("/metrics")
def ml_metrics():
    return ml_service.metrics


@router.get("/predict")
def ml_predict():
    return ml_service.predict_live()


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
