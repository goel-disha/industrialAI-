"""Optional XGBoost fault classifier used by the ensemble layer."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd

from .config import ARTIFACT_DIR, FEATURE_COLUMNS


class XGBoostService:
    def __init__(self) -> None:
        self.model = None
        self.scaler = None
        self.reload()

    def reload(self) -> None:
        model_path = ARTIFACT_DIR / "xgboost_classifier.joblib"
        scaler_path = ARTIFACT_DIR / "xgboost_scaler.joblib"
        self.ready = model_path.exists() and scaler_path.exists()
        if self.ready:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)

    def status(self) -> Dict[str, Any]:
        return {"ready": self.ready, "model": "xgboost_fault_classifier"}

    def predict(self, features: Dict[str, float]) -> Dict[str, Any] | None:
        if not self.ready:
            return None
        X = pd.DataFrame([[features.get(c, 0.0) for c in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        Z = self.scaler.transform(X)
        probabilities = self.model.predict_proba(Z)[0]
        index = int(np.argmax(probabilities))
        return {
            "fault": str(self.model.classes_[index]),
            "confidence": round(float(probabilities[index]), 4),
        }


xgb_service = XGBoostService()
