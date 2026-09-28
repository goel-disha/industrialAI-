from fastapi import APIRouter, Query
from backend.ai.ai_service import machine_ai
from backend.ai.anomaly_service import anomaly_service
from backend.ai.health_service import health_service
from backend.ai.cycle_intelligence import cycle_intelligence
from backend.ai.predictive_service import predictive_service
from backend.ai.oee_service import oee_service

router = APIRouter(prefix="/ai", tags=["Industrial AI"])

@router.get("/snapshot")
def snapshot():
    return machine_ai.snapshot()

@router.get("/health")
def health():
    return health_service.get_health()

@router.get("/anomalies")
def anomalies():
    return anomaly_service.analyze()

@router.get("/anomalies/history")
def anomaly_history(limit: int = Query(100, ge=1, le=500)):
    return {"data": anomaly_service.history(limit)}

@router.get("/cycles")
def cycles(limit: int = Query(100, ge=5, le=500)):
    return cycle_intelligence.get_report(limit)

@router.get("/prediction")
def prediction():
    return predictive_service.get_prediction()

@router.get("/oee")
def oee():
    return oee_service.get_oee()
