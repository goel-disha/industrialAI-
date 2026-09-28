from statistics import mean, median, pstdev
from backend.machine.machine_engine import engine

class CycleIntelligence:
    def get_report(self, limit=100):
        history = engine.get_history(limit=max(500, limit * 10))
        cycles = {}
        for item in history:
            c = item.get("cycle", {})
            n, d = c.get("number"), c.get("duration", 0)
            if n and c.get("complete") and d:
                cycles[int(n)] = float(d)
        values = list(cycles.values())[-limit:]
        if not values:
            return {"cycles": 0, "average": 0, "median": 0, "best": 0,
                    "worst": 0, "std": 0, "trend": 0, "recent": []}
        trend = 0
        if len(values) >= 4:
            half = len(values) // 2
            trend = mean(values[half:]) - mean(values[:half])
        return {
            "cycles": len(values),
            "average": round(mean(values), 3),
            "median": round(median(values), 3),
            "best": round(min(values), 3),
            "worst": round(max(values), 3),
            "std": round(pstdev(values), 3) if len(values) > 1 else 0,
            "trend": round(trend, 3),
            "recent": [{"cycle": n, "duration": round(d, 3)}
                       for n, d in list(cycles.items())[-20:]],
        }

cycle_intelligence = CycleIntelligence()
