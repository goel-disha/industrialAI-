from statistics import mean

from backend.machine.machine_engine import engine
from backend.machine.plc_memory import plc


class AnomalyService:
    POSITION_ERROR_LIMIT = 5000.0
    SPEED_DEVIATION_RATIO = 0.35

    # Number of consecutive telemetry samples required
    # before considering an axis stuck.
    STUCK_SAMPLES = 30

    # Minimum actual speed required before evaluating
    # command-vs-actual speed deviation.
    MIN_ACTUAL_SPEED = 1.0

    CYCLE_DEVIATION_RATIO = 0.25

    def __init__(self):
        self.event_history = []
        self.max_events = 500

    @staticmethod
    def _num(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _event(
        self,
        code,
        severity,
        message,
        axis=None,
        value=None,
        threshold=None
    ):
        item = {
            "code": code,
            "severity": severity,
            "message": message,
            "axis": axis,
            "value": value,
            "threshold": threshold
        }

        self.event_history.append(item)
        self.event_history = self.event_history[-self.max_events:]

        return item

    def _axis_checks(self, history, name):
        anomalies = []

        latest = history[-1].get(name, {})

        # ---------------------------------------------------------
        # 1. POSITION ERROR
        # ---------------------------------------------------------

        position = self._num(latest.get("position"))
        target = self._num(latest.get("target"))

        error = abs(target - position)

        if latest.get("complete") and error > self.POSITION_ERROR_LIMIT:
            anomalies.append(
                self._event(
                    "POSITION_ERROR",
                    "WARNING",
                    f"{name} has a large position error.",
                    name,
                    round(error, 3),
                    self.POSITION_ERROR_LIMIT
                )
            )

        # ---------------------------------------------------------
        # 2. SPEED DEVIATION
        # ---------------------------------------------------------

        command = abs(self._num(latest.get("speed")))
        actual = abs(self._num(latest.get("actual_speed")))

        busy = bool(latest.get("busy"))

        if (
            busy
            and command > 1
            and actual >= self.MIN_ACTUAL_SPEED
        ):
            ratio = abs(command - actual) / command

            if ratio > self.SPEED_DEVIATION_RATIO:
                anomalies.append(
                    self._event(
                        "SPEED_DEVIATION",
                        "WARNING",
                        f"{name} actual speed deviates from command speed.",
                        name,
                        round(ratio, 3),
                        self.SPEED_DEVIATION_RATIO
                    )
                )

        # ---------------------------------------------------------
        # 3. SERVO ERROR
        # ---------------------------------------------------------

        if latest.get("error"):
            anomalies.append(
                self._event(
                    "SERVO_ERROR",
                    "CRITICAL",
                    f"{name} reports a servo error.",
                    name,
                    True,
                    False
                )
            )

        # ---------------------------------------------------------
        # 4. MOTION STUCK
        # ---------------------------------------------------------

        recent = history[-self.STUCK_SAMPLES:]

        if len(recent) >= self.STUCK_SAMPLES:

            busy_samples = [
                bool(x.get(name, {}).get("busy"))
                for x in recent
            ]

            positions = [
                self._num(x.get(name, {}).get("position"))
                for x in recent
            ]

            # Axis must be continuously busy and position must
            # remain practically unchanged.
            if (
                all(busy_samples)
                and max(positions) - min(positions) < 1e-6
            ):
                anomalies.append(
                    self._event(
                        "MOTION_STUCK",
                        "CRITICAL",
                        f"{name} is busy but its position has not changed.",
                        name,
                        0,
                        1
                    )
                )

        return anomalies

    def _cycle_check(self, history):
        durations = {}

        for item in history:
            cycle = item.get("cycle", {})

            number = cycle.get("number")
            duration = self._num(cycle.get("duration"))

            if (
                number
                and cycle.get("complete")
                and duration > 0
            ):
                durations[int(number)] = duration

        values = list(durations.values())

        # Need enough completed cycles to establish a baseline.
        if len(values) < 4:
            return []

        baseline = values[:-1]
        current = values[-1]

        avg = mean(baseline)

        if (
            avg
            and abs(current - avg) / avg
            > self.CYCLE_DEVIATION_RATIO
        ):
            return [
                self._event(
                    "CYCLE_DURATION_ANOMALY",
                    "WARNING",
                    "Latest completed cycle differs materially from the recent baseline.",
                    value=round(current, 3),
                    threshold=round(
                        avg * (1 + self.CYCLE_DEVIATION_RATIO),
                        3
                    )
                )
            ]

        return []

    def analyze(self, history=None):

        history = (
            history
            if history is not None
            else engine.get_history(limit=300)
        )

        if not history:
            return {
                "status": "NO_DATA",
                "health_score": 100,
                "anomalies": [],
                "counts": {
                    "critical": 0,
                    "warning": 0,
                    "info": 0
                }
            }

        latest = history[-1]

        anomalies = []

        # ---------------------------------------------------------
        # AXIS ANALYSIS
        # ---------------------------------------------------------

        for axis in ("axis1", "axis2", "axis3"):
            anomalies.extend(
                self._axis_checks(history, axis)
            )

        # ---------------------------------------------------------
        # CYCLE ANALYSIS
        # ---------------------------------------------------------

        anomalies.extend(
            self._cycle_check(history)
        )

        # ---------------------------------------------------------
        # SAFETY ANALYSIS
        # ---------------------------------------------------------

        try:

            if int(plc.read("M90") or 0):
                anomalies.append(
                    self._event(
                        "EMERGENCY_STOP",
                        "CRITICAL",
                        "Emergency stop is active."
                    )
                )

            if int(plc.read("M91") or 0):
                anomalies.append(
                    self._event(
                        "AIR_PRESSURE",
                        "CRITICAL",
                        "Air-pressure fault is active."
                    )
                )

        except Exception:
            pass

        # ---------------------------------------------------------
        # MACHINE STATE ANALYSIS
        # ---------------------------------------------------------

        known_states = {
            "IDLE",
            "SERVO1",
            "SERVO2_3_POS2",
            "CENTER_FORWARD",
            "CENTER_REVERSE",
            "SERVO2_3_POS1",
            "RETURN_HOME"
        }

        state = latest.get("state", "IDLE")

        if state not in known_states:
            anomalies.append(
                self._event(
                    "UNEXPECTED_STATE",
                    "WARNING",
                    f"Unexpected machine state: {state}"
                )
            )

        # ---------------------------------------------------------
        # REMOVE DUPLICATE ANOMALIES
        # ---------------------------------------------------------

        unique = {}

        for item in anomalies:
            key = (
                item["code"],
                item.get("axis")
            )

            unique[key] = item

        anomalies = list(unique.values())

        # ---------------------------------------------------------
        # COUNTS
        # ---------------------------------------------------------

        critical = sum(
            x["severity"] == "CRITICAL"
            for x in anomalies
        )

        warning = sum(
            x["severity"] == "WARNING"
            for x in anomalies
        )

        info = sum(
            x["severity"] == "INFO"
            for x in anomalies
        )

        # ---------------------------------------------------------
        # HEALTH SCORE
        # ---------------------------------------------------------

        score = max(
            0,
            min(
                100,
                100
                - critical * 30
                - warning * 10
                - info * 2
            )
        )

        if critical:
            status = "CRITICAL"
        elif warning:
            status = "WARNING"
        else:
            status = "HEALTHY"

        return {
            "status": status,
            "health_score": score,
            "timestamp": latest.get("timestamp"),
            "machine_state": state,
            "cycle_number": latest.get(
                "cycle", {}
            ).get("number", 0),
            "anomalies": anomalies,
            "counts": {
                "critical": critical,
                "warning": warning,
                "info": info
            }
        }

    def history(self, limit=100):
        return self.event_history[-limit:]


anomaly_service = AnomalyService()