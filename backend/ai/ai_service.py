from backend.ai.anomaly_service import anomaly_service
from backend.ai.health_service import health_service
from backend.ai.cycle_intelligence import cycle_intelligence
from backend.ai.predictive_service import predictive_service
from backend.ai.oee_service import oee_service
from backend.machine.machine_engine import engine

class MachineAI:
    def snapshot(self):
        return {
            "health": health_service.get_health(),
            "anomalies": anomaly_service.analyze(),
            "cycles": cycle_intelligence.get_report(),
            "prediction": predictive_service.get_prediction(),
            "oee": oee_service.get_oee(),
            "latest_telemetry": engine.get_latest(),
        }

machine_ai = MachineAI()
