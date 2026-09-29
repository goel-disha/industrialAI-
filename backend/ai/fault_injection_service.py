"""Controlled AI what-if fault injection.

This layer perturbs the ML feature vector only; it does not alter PLC commands
or the machine-control state. It is intended for safe AI validation and demos.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class FaultInjectionService:
    FAULTS = {
        "SERVO_LAG",
        "VIBRATION",
        "STUCK_AXIS",
        "SENSOR_NOISE",
        "CYCLE_DEGRADATION",
    }
    AXES = {"a1", "a2", "a3"}

    def __init__(self):
        self.active: Optional[Dict[str, Any]] = None

    def set(self, fault: str, severity: float = 0.6, axis: str = "a2"):
        fault = fault.upper().strip()
        axis = axis.lower().strip()
        if fault not in self.FAULTS:
            raise ValueError(f"Unsupported fault. Choose from {sorted(self.FAULTS)}")
        if axis not in self.AXES:
            raise ValueError("Axis must be a1, a2 or a3")
        severity = max(0.05, min(1.0, float(severity)))
        self.active = {"fault": fault, "severity": severity, "axis": axis}
        return self.status()

    def clear(self):
        self.active = None
        return self.status()

    def status(self):
        return {"active": self.active is not None, "injection": self.active}

    def apply(self, features: Dict[str, float]) -> Dict[str, float]:
        out = dict(features)
        if not self.active:
            return out

        fault = self.active["fault"]
        s = float(self.active["severity"])
        axis = self.active["axis"]

        if fault == "SERVO_LAG":
            out[f"{axis}_mean_actual_speed"] *= 1 - 0.75 * s
            out[f"{axis}_speed_deviation"] = max(
                out[f"{axis}_speed_deviation"], 0.25 + 0.55 * s
            )
            out[f"{axis}_mean_pos_error"] *= 1 + 2.0 * s
            out[f"{axis}_max_pos_error"] *= 1 + 2.5 * s
            out["cycle_duration"] *= 1 + 0.12 * s

        elif fault == "VIBRATION":
            out[f"{axis}_position_std"] *= 1 + 5.0 * s
            out[f"{axis}_std_pos_error"] *= 1 + 3.0 * s

        elif fault == "STUCK_AXIS":
            out[f"{axis}_mean_actual_speed"] *= max(0.02, 1 - 0.95 * s)
            out[f"{axis}_speed_deviation"] = max(
                out[f"{axis}_speed_deviation"], 0.65 + 0.3 * s
            )
            out[f"{axis}_mean_pos_error"] *= 1 + 5.0 * s
            out[f"{axis}_max_pos_error"] *= 1 + 6.0 * s
            out["cycle_duration"] *= 1 + 0.35 * s

        elif fault == "SENSOR_NOISE":
            for a in ("a1", "a2", "a3"):
                out[f"{a}_position_std"] *= 1 + 4.0 * s
                out[f"{a}_std_pos_error"] *= 1 + 3.0 * s

        elif fault == "CYCLE_DEGRADATION":
            out["cycle_duration"] *= 1 + 0.45 * s
            out["busy_ratio"] = min(0.99, out["busy_ratio"] + 0.12 * s)
            out["state_transitions"] += 2.0 * s

        return out


fault_injection_service = FaultInjectionService()
