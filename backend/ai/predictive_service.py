from statistics import mean
from backend.machine.machine_engine import engine

class PredictiveService:
    def _axis_trend(self, axis, history):
        values = []
        for item in history:
            a = item.get(axis, {})
            target = float(a.get("target", 0) or 0)
            position = float(a.get("position", 0) or 0)
            if target:
                values.append(abs(target - position))
        values = values[-100:]
        if len(values) < 10:
            return {"risk": "INSUFFICIENT_DATA", "trend": 0, "baseline": 0}
        half = len(values) // 2
        early, recent = mean(values[:half]), mean(values[half:])
        trend = recent - early
        risk = "HIGH" if recent > max(5000, early * 2) else (
            "MEDIUM" if recent > max(2500, early * 1.35) else "LOW"
        )
        return {"risk": risk, "trend": round(trend, 3),
                "baseline": round(early, 3),
                "recent_mean_error": round(recent, 3)}

    def get_prediction(self):
        history = engine.get_history(limit=1000)
        return {
            "model": "engineering_trend_baseline",
            "axes": {a: self._axis_trend(a, history)
                     for a in ("axis1", "axis2", "axis3")},
            "note": "Baseline trend detector; train an ML model after sufficient labeled history.",
        }

predictive_service = PredictiveService()
