"""IndustrialAI Machine Diagnostic Agent.

This is a tool-using decision engine rather than a free-form chatbot. It
chooses read-only machine tools, gathers evidence, correlates signals, and
returns a structured diagnosis that the frontend can render and audit.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .tools import TOOL_REGISTRY


FAULT_LABELS = {
    "SERVO_LAG": ("Servo lag", "Inspect the affected servo and mechanical load."),
    "VIBRATION": ("Vibration anomaly", "Inspect mechanical vibration, mounting and spindle/axis condition."),
    "STUCK_AXIS": ("Axis motion abnormality", "Check for mechanical obstruction and servo drive status."),
    "SENSOR_NOISE": ("Sensor noise", "Inspect sensor wiring, grounding and signal quality."),
    "CYCLE_DEGRADATION": ("Cycle degradation", "Inspect recent cycle trend and schedule maintenance if degradation persists."),
    "NORMAL": ("Normal operation", "Continue normal monitoring."),
}


class DiagnosticAgent:
    def __init__(self) -> None:
        self.tools = TOOL_REGISTRY

    def _run(self, name: str, **kwargs) -> dict:
        fn = self.tools[name]
        result = fn(**kwargs)
        if not isinstance(result, dict):
            return {"available": True, "value": result}
        return result

    @staticmethod
    def _number(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def investigate(self, question: str = "", trigger: str = "user") -> dict:
        steps: list[dict] = []

        machine = self._run("machine_status")
        steps.append({"tool": "machine_status", "status": "complete" if machine.get("available", True) else "failed"})

        alarms = self._run("active_alarms")
        steps.append({"tool": "active_alarms", "status": "complete" if alarms.get("available", True) else "failed"})

        ml = self._run("ml_diagnostics")
        steps.append({"tool": "ml_diagnostics", "status": "complete" if ml.get("available") else "failed"})

        # Only invoke deeper tools when an abnormality is detected or explicitly requested.
        ml_prediction = ml.get("prediction") if isinstance(ml, dict) else None
        fault = self._extract_fault(ml_prediction)
        abnormal = fault not in (None, "", "NORMAL") or bool(self._extract_alarm_list(alarms))

        if abnormal or any(k in question.lower() for k in ("why", "diagnos", "maintain", "fault", "anomal", "rul")):
            cycles = self._run("cycle_history", limit=10)
            steps.append({"tool": "cycle_history", "status": "complete" if cycles.get("available") else "failed"})
            rul_score = self._number((ml_prediction or {}).get("anomaly_score")) if isinstance(ml_prediction, dict) else 0.0\n            rul = self._run("rul", anomaly_score=rul_score or 0.0)
            steps.append({"tool": "rul", "status": "complete" if rul.get("available") else "failed"})
            maintenance = self._run("maintenance", prediction=ml_prediction if isinstance(ml_prediction, dict) else {})
            steps.append({"tool": "maintenance", "status": "complete" if maintenance.get("available") else "failed"})
        else:
            cycles = {"available": False}
            rul = {"available": False}
            maintenance = {"available": False}

        evidence = self._build_evidence(machine, alarms, ml_prediction, cycles, rul)
        diagnosis = self._build_diagnosis(fault, alarms, evidence, ml_prediction)
        severity = self._severity(fault, alarms, evidence)

        return {
            "agent": "IndustrialAI Machine Diagnostic Agent",
            "version": "1.0",
            "trigger": trigger,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "status": "investigated",
            "severity": severity,
            "diagnosis": diagnosis,
            "evidence": evidence,
            "investigation": steps,
            "ml": ml_prediction,
            "rul": rul.get("result") if isinstance(rul, dict) else None,
            "maintenance": maintenance.get("result") if isinstance(maintenance, dict) else None,
            "machine": machine,
            "alarms": self._extract_alarm_list(alarms),
            "safety": {
                "read_only": True,
                "automatic_machine_control": False,
                "operator_approval_required_for_action": True,
            },
        }

    @staticmethod
    def _extract_fault(prediction: Any) -> str | None:
        if not isinstance(prediction, dict):
            return None
        for key in ("fault", "predicted_fault", "class", "label", "fault_class"):
            value = prediction.get(key)
            if value:
                return str(value).upper()
        nested = prediction.get("prediction")
        if isinstance(nested, dict):
            return DiagnosticAgent._extract_fault(nested)
        return None

    @staticmethod
    def _extract_confidence(prediction: Any) -> float | None:
        if not isinstance(prediction, dict):
            return None
        for key in ("confidence", "fault_confidence", "probability"):
            value = prediction.get(key)
            try:
                value = float(value)
                return value * 100 if value <= 1 else value
            except (TypeError, ValueError):
                pass
        return None

    @staticmethod
    def _extract_alarm_list(alarms: dict) -> list:
        if not isinstance(alarms, dict):
            return []
        for key in ("alarms", "active_alarms", "items", "data"):
            value = alarms.get(key)
            if isinstance(value, list):
                return value
        return []

    def _build_evidence(self, machine, alarms, prediction, cycles, rul) -> list[dict]:
        evidence = []
        fault = self._extract_fault(prediction)
        confidence = self._extract_confidence(prediction)

        if fault:
            evidence.append({
                "type": "ml",
                "finding": f"ML fault classifier reports {fault.replace('_', ' ').lower()}",
                "confidence_percent": round(confidence, 1) if confidence is not None else None,
            })

        active = self._extract_alarm_list(alarms)
        if active:
            evidence.append({"type": "alarm", "finding": f"{len(active)} active machine alarm(s) reported."})
        else:
            evidence.append({"type": "alarm", "finding": "No active machine alarm reported."})

        if isinstance(machine, dict):
            state = machine.get("state") or machine.get("machine_state")
            if state is not None:
                evidence.append({"type": "machine", "finding": f"Machine state is {state}."})

            axes = machine.get("axes")
            if isinstance(axes, dict):
                for axis, data in axes.items():
                    if isinstance(data, dict):
                        error = data.get("position_error") or data.get("pos_error")
                        error_num = self._number(error)
                        if error_num is not None and abs(error_num) > 0:
                            evidence.append({
                                "type": "servo",
                                "finding": f"{axis} position error is {error_num:g}.",
                                "value": error_num,
                            })

        if isinstance(rul, dict) and rul.get("result") is not None:
            evidence.append({"type": "rul", "finding": "RUL analysis was requested for this investigation."})

        return evidence

    def _build_diagnosis(self, fault, alarms, evidence, prediction) -> dict:
        label, recommendation = FAULT_LABELS.get(
            fault or "NORMAL",
            (fault.replace("_", " ").title() if fault else "Insufficient evidence",
             "Continue monitoring and inspect the supporting signals."),
        )
        confidence = self._extract_confidence(prediction)

        if not fault:
            label = "Insufficient ML evidence"
            recommendation = "Complete a machine cycle and verify that ML artifacts are available."

        return {
            "label": label,
            "fault_code": fault or "UNKNOWN",
            "confidence_percent": round(confidence, 1) if confidence is not None else None,
            "recommendation": recommendation,
            "basis": [e["finding"] for e in evidence],
        }

    @staticmethod
    def _severity(fault, alarms, evidence) -> str:
        if DiagnosticAgent._extract_alarm_list(alarms):
            return "HIGH"
        if fault in ("STUCK_AXIS", "SERVO_LAG"):
            return "MEDIUM"
        if fault in ("VIBRATION", "SENSOR_NOISE", "CYCLE_DEGRADATION"):
            return "LOW"
        return "NORMAL"


agent = DiagnosticAgent()
