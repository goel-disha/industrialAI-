from collections import deque
from statistics import mean, pstdev

class FeatureEngine:
    def __init__(self, window_size=120):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)

    @staticmethod
    def _num(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _axis(self, axis, previous=None):
        position = self._num(axis.get("position"))
        target = self._num(axis.get("target"))
        command = self._num(axis.get("speed"))
        actual = self._num(axis.get("actual_speed"))
        previous_position = self._num(previous.get("position")) if previous else position
        error = target - position
        return {
            "position": position,
            "target": target,
            "position_error": error,
            "abs_position_error": abs(error),
            "command_speed": command,
            "actual_speed": actual,
            "speed_error": command - actual,
            "speed_ratio": actual / command if abs(command) > 1e-9 else 0.0,
            "movement_delta": position - previous_position,
            "busy": bool(axis.get("busy", False)),
            "complete": bool(axis.get("complete", False)),
            "error": bool(axis.get("error", False)),
        }

    def transform(self, snapshot):
        previous = self.history[-1] if self.history else None
        result = {
            "timestamp": snapshot.get("timestamp"),
            "scan": snapshot.get("scan", 0),
            "state": snapshot.get("state", "IDLE"),
            "model": snapshot.get("model", 1),
            "cycle_number": snapshot.get("cycle", {}).get("number", 0),
            "cycle_running": bool(snapshot.get("cycle", {}).get("running", False)),
            "cycle_complete": bool(snapshot.get("cycle", {}).get("complete", False)),
            "cycle_duration": self._num(snapshot.get("cycle", {}).get("duration")),
        }
        for name in ("axis1", "axis2", "axis3"):
            result[name] = self._axis(
                snapshot.get(name, {}),
                previous.get(name, {}) if previous else None,
            )
        result["servo_error_count"] = sum(int(result[a]["error"]) for a in ("axis1", "axis2", "axis3"))
        result["busy_axis_count"] = sum(int(result[a]["busy"]) for a in ("axis1", "axis2", "axis3"))
        self.history.append(snapshot)
        return result

    def batch(self, snapshots):
        return [self.transform(x) for x in snapshots]

    def statistics(self):
        values = [
            self._num(x.get("cycle", {}).get("duration"))
            for x in self.history
            if self._num(x.get("cycle", {}).get("duration")) > 0
        ]
        return {
            "samples": len(self.history),
            "cycle_duration_mean": round(mean(values), 4) if values else 0,
            "cycle_duration_std": round(pstdev(values), 4) if len(values) > 1 else 0,
        }

feature_engine = FeatureEngine()
