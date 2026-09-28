from statistics import mean
from backend.machine.machine_engine import engine
from backend.machine.production_engine import production

class OEEService:
    def get_oee(self):
        history = engine.get_history(limit=1000)
        total = max(1, production.total_cycles)
        completed = max(0, production.completed_cycles)
        rejected = max(0, production.rejected_cycles)
        quality = max(0, min(100, 100 * completed / total))

        cycles = {}
        for item in history:
            c = item.get("cycle", {})
            if c.get("number") and c.get("complete") and c.get("duration"):
                cycles[int(c["number"])] = float(c["duration"])
        durations = list(cycles.values())[-50:]
        ideal = min(durations) if durations else 1
        actual = mean(durations) if durations else ideal
        performance = max(0, min(100, 100 * ideal / max(actual, 1e-9)))
        availability = 100 * sum(x.get("state") != "IDLE" for x in history) / max(1, len(history))
        oee = availability * performance * quality / 10000
        return {
            "availability": round(availability, 2),
            "performance": round(performance, 2),
            "quality": round(quality, 2),
            "oee": round(oee, 2),
            "total_cycles": total, "completed": completed, "rejected": rejected,
        }

oee_service = OEEService()
