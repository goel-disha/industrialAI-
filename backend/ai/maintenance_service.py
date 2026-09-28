"""Predictive-maintenance decision layer built on ML predictions and live state."""

from __future__ import annotations

from typing import Any, Dict


class MaintenanceService:
    RULES = {
        "SERVO_LAG": {
            "priority": "HIGH",
            "action": "Inspect servo following error, coupling, drive tuning and encoder feedback.",
            "systems": ["servo drive", "encoder", "mechanical coupling"],
        },
        "STUCK_AXIS": {
            "priority": "CRITICAL",
            "action": "Stop the machine safely and inspect the affected axis for obstruction or drive fault.",
            "systems": ["servo drive", "mechanics", "limit switches"],
        },
        "VIBRATION": {
            "priority": "MEDIUM",
            "action": "Inspect vibration source, bearings, mounting, alignment and motion profile.",
            "systems": ["bearings", "mounting", "alignment"],
        },
        "SENSOR_NOISE": {
            "priority": "MEDIUM",
            "action": "Inspect sensor wiring, grounding, shielding and sensor health.",
            "systems": ["sensor", "wiring", "grounding"],
        },
        "CYCLE_DEGRADATION": {
            "priority": "MEDIUM",
            "action": "Review cycle-time trend and inspect components contributing to increased motion time.",
            "systems": ["motion profile", "servo system", "mechanics"],
        },
    }

    def recommend(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        fault = str(prediction.get("predicted_fault", "NORMAL"))
        confidence = float(prediction.get("fault_confidence", 0.0))
        anomaly = bool(prediction.get("anomaly", False))
        rule = self.RULES.get(fault)

        if fault == "NORMAL" and not anomaly:
            return {
                "status": "NO_ACTION",
                "priority": "LOW",
                "message": "No predictive-maintenance action is currently indicated.",
                "confidence": confidence,
                "next_cycle_duration": prediction.get("predicted_next_cycle_duration"),
            }

        if rule is None:
            return {
                "status": "REVIEW",
                "priority": "MEDIUM",
                "message": "An anomaly was detected; inspect the latest telemetry before maintenance intervention.",
                "confidence": confidence,
            }

        return {
            "status": "MAINTENANCE_RECOMMENDED",
            "priority": rule["priority"],
            "fault": fault,
            "confidence": confidence,
            "message": rule["action"],
            "systems_to_inspect": rule["systems"],
            "machine_state": prediction.get("machine_state"),
            "cycle_number": prediction.get("cycle_number"),
        }


maintenance_service = MaintenanceService()
