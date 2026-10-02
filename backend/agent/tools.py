"""Read-only tools exposed to the IndustrialAI diagnostic agent."""
from __future__ import annotations

from typing import Any
import importlib


def _call(module_name: str, object_name: str, method: str | None = None, *args, **kwargs):
    try:
        module = importlib.import_module(module_name)
        obj = getattr(module, object_name)
        if method:
            obj = getattr(obj, method)
        return {"available": True, "value": obj(*args, **kwargs)}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def get_machine_status() -> dict:
    result = _call("backend.srevices.live_monitor_services", "live_monitor")
    return result.get("value", result)


def get_active_alarms() -> dict:
    result = _call("backend.srevices.alarm_services", "get_active_alarms")
    value = result.get("value")
    return {"available": result.get("available", False), "alarms": value or [], **({"error": result["error"]} if not result.get("available") else {})}


def get_ml_diagnostics() -> dict:
    try:
        from backend.ai.ml.model_service import ml_service
        return {"available": True, "prediction": ml_service.predict_live()}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def get_cycle_history(limit: int = 10) -> dict:
    result = _call("backend.ai.cycle_intelligence", "cycle_intelligence", "get_report", limit=limit)
    if result.get("available"):
        return {"available": True, "report": result["value"]}
    return result


def get_rul(anomaly_score: float = 0.0) -> dict:
    result = _call("backend.ai.rul_service", "rul_service", "predict", anomaly_score=anomaly_score)
    if result.get("available"):
        return {"available": True, "result": result["value"]}
    return result


def get_maintenance(prediction: dict | None = None) -> dict:
    prediction = prediction or {}
    result = _call("backend.ai.maintenance_service", "maintenance_service", "recommend", prediction)
    if result.get("available"):
        return {"available": True, "result": result["value"]}
    return result


def get_servo_status(axis: str | None = None) -> dict:
    machine = get_machine_status()
    if not isinstance(machine, dict):
        return {"available": False, "error": "Machine status unavailable"}

    servo = machine.get("servo", {})
    if axis:
        key = axis.lower().replace("axis", "").strip()
        aliases = {"1": "axis1", "2": "axis2", "3": "axis3"}
        target = aliases.get(key, axis.lower())
        return {"available": True, "axis": target, "status": servo.get(target)}
    return {"available": True, "servo": servo, "servo_status": machine.get("servo_status", {})}


TOOL_REGISTRY = {
    "machine_status": get_machine_status,
    "active_alarms": get_active_alarms,
    "ml_diagnostics": get_ml_diagnostics,
    "cycle_history": get_cycle_history,
    "rul": get_rul,
    "maintenance": get_maintenance,
    "servo_status": get_servo_status,
}
