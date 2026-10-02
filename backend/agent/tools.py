"""Read-only tools exposed to the IndustrialAI diagnostic agent.

The tools deliberately return plain JSON-safe dictionaries so the agent can
reason over the existing machine, ML, alarm and maintenance services without
coupling the UI to implementation details.
"""
from __future__ import annotations

from typing import Any
import importlib


def _safe_call(module_name: str, function_name: str, default: Any = None, *args, **kwargs):
    try:
        module = importlib.import_module(module_name)
        fn = getattr(module, function_name)
        return fn(*args, **kwargs)
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}", "value": default}


def _unwrap(value: Any) -> Any:
    if isinstance(value, dict) and "value" in value and value.get("available") is False:
        return value
    return value


def get_machine_status() -> dict:
    result = _safe_call("backend.live_monitor_services", "live_monitor", {})
    result = _unwrap(result)
    return result if isinstance(result, dict) else {"available": False, "value": result}


def get_active_alarms() -> dict:
    result = _safe_call("backend.live_monitor_services", "get_active_alarms", [])
    result = _unwrap(result)
    if isinstance(result, dict):
        return result
    return {"available": True, "alarms": result or []}


def get_ml_diagnostics() -> dict:
    try:
        from backend.ai.ml.model_service import ml_service
        prediction = ml_service.predict_live()
        return {"available": True, "prediction": prediction}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def get_rul() -> dict:
    candidates = [
        ("backend.ai.ml.rul_service", "predict_rul"),
        ("backend.ai.rul_service", "predict_rul"),
    ]
    for module_name, fn_name in candidates:
        result = _safe_call(module_name, fn_name, None)
        if not (isinstance(result, dict) and result.get("available") is False):
            return {"available": True, "result": result}
    return {"available": False, "error": "RUL service is unavailable"}


def get_maintenance() -> dict:
    candidates = [
        ("backend.ai.ml.maintenance_service", "get_maintenance_recommendation"),
        ("backend.ai.maintenance_service", "get_maintenance_recommendation"),
    ]
    for module_name, fn_name in candidates:
        result = _safe_call(module_name, fn_name, None)
        if not (isinstance(result, dict) and result.get("available") is False):
            return {"available": True, "result": result}
    return {"available": False, "error": "Maintenance service is unavailable"}


def get_cycle_history(limit: int = 10) -> dict:
    """Best-effort access to cycle intelligence/history without assuming one DB schema."""
    candidates = [
        ("backend.ai.cycle_intelligence", "get_cycle_history"),
        ("backend.ai.cycle_intelligence", "recent_cycles"),
        ("backend.production_engine", "get_cycle_history"),
    ]
    for module_name, fn_name in candidates:
        result = _safe_call(module_name, fn_name, None, limit=limit)
        if not (isinstance(result, dict) and result.get("available") is False):
            return {"available": True, "cycles": result}
    return {"available": False, "error": "Cycle history service is unavailable"}


def get_servo_status(axis: str | None = None) -> dict:
    machine = get_machine_status()
    servo = machine.get("servo") if isinstance(machine, dict) else None
    axes = machine.get("axes") if isinstance(machine, dict) else None

    if axis and isinstance(axes, dict):
        key = axis.lower().replace("axis", "").strip()
        aliases = {"1": "a1", "2": "a2", "3": "a3"}
        target = aliases.get(key, axis.lower())
        return {"available": True, "axis": target, "status": axes.get(target, axes.get(axis))}

    return {"available": True, "servo": servo, "axes": axes}


TOOL_REGISTRY = {
    "machine_status": get_machine_status,
    "active_alarms": get_active_alarms,
    "ml_diagnostics": get_ml_diagnostics,
    "rul": get_rul,
    "maintenance": get_maintenance,
    "cycle_history": get_cycle_history,
    "servo_status": get_servo_status,
}
