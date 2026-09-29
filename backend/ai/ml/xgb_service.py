"""Optional XGBoost fault classifier used by the ensemble layer."""

from __future__ import annotations

import json
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd

from .config import ARTIFACT_DIR, FEATURE_COLUMNS, FEATURE_SCHEMA_VERSION


class XGBoostService:
    def __init__(self) -> None:
        self.model = None
        self.scaler = None
        self.id_to_class = {}
        self.schema_compatible = False
        self.reload()

    def reload(self) -> None:
        model_path = ARTIFACT_DIR / "xgboost_classifier.joblib"
        scaler_path = ARTIFACT_DIR / "xgboost_scaler.joblib"
        metadata_path = ARTIFACT_DIR / "xgboost_metadata.json"
        self.ready = model_path.exists() and scaler_path.exists() and metadata_path.exists()
        if self.ready:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            metadata = json.loads(metadata_path.read_text())
            class_to_id = metadata.get("class_to_id", {})
            self.id_to_class = {int(v): str(k) for k, v in class_to_id.items()}
            self.schema_compatible = metadata.get("feature_schema_version") == FEATURE_SCHEMA_VERSION

    def status(self) -> Dict[str, Any]:
        return {"ready": self.ready and self.schema_compatible, "model": "xgboost_fault_classifier", "schema_compatible": self.schema_compatible}

    def predict(self, features: Dict[str, float]) -> Dict[str, Any] | None:
        if not self.ready or not self.schema_compatible:
            return None
        X = pd.DataFrame([[features.get(c, 0.0) for c in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        Z = self.scaler.transform(X)
        probabilities = self.model.predict_proba(Z)[0]
        index = int(np.argmax(probabilities))
        class_id = int(self.model.classes_[index])
        return {
            "fault": self.id_to_class.get(class_id, str(class_id)),
            "confidence": round(float(probabilities[index]), 4),
        }


xgb_service = XGBoostService()
