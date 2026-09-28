from backend.ai.anomaly_service import anomaly_service

class HealthService:
    def get_health(self):
        result = anomaly_service.analyze()
        axis = {"axis1": 100, "axis2": 100, "axis3": 100}
        for item in result["anomalies"]:
            name = item.get("axis")
            if name in axis:
                axis[name] = max(0, axis[name] - (30 if item["severity"] == "CRITICAL" else 10))
        return {
            "status": result["status"],
            "health_score": result["health_score"],
            "axis_health": axis,
            "anomaly_count": len(result["anomalies"]),
            "critical_count": result["counts"]["critical"],
            "warning_count": result["counts"]["warning"],
            "machine_state": result["machine_state"],
            "cycle_number": result["cycle_number"],
            "timestamp": result["timestamp"],
        }

health_service = HealthService()
