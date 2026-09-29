"""Collect model evaluation metadata for the AI dashboard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .ml.config import ARTIFACT_DIR


def _read(name: str) -> Dict[str, Any]:
    path: Path = ARTIFACT_DIR / name
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def get_model_performance() -> Dict[str, Any]:
    core = _read("metrics.json")
    xgb = _read("xgboost_metadata.json")
    lstm = _read("lstm_metadata.json")

    return {
        "core_models": core,
        "xgboost": xgb,
        "lstm": lstm,
        "artifacts": {
            "core": (ARTIFACT_DIR / "classifier.joblib").exists(),
            "xgboost": (ARTIFACT_DIR / "xgboost_classifier.joblib").exists(),
            "lstm": (ARTIFACT_DIR / "lstm_fault_classifier.pt").exists(),
            "shap": True,
        },
    }
