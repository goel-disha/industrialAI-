from fastapi import APIRouter
from .ml.model_service import ml_service
from .ml.train import train_all

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


@router.post("/train")
def ml_train():
    metrics = train_all()

    ml_service.reload()

    return {
        "status": "success",
        "message": "ML models retrained successfully",
        "metrics": metrics
    }