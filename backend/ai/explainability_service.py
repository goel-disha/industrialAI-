"""Explainable-AI layer for live IndustrialAI predictions.

SHAP is used when available. A deterministic Random-Forest feature-importance
fallback keeps the API usable if SHAP cannot be imported in a deployment.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from .ml.config import FEATURE_COLUMNS


class ExplainabilityService:
    def explain_classifier(self, model: Any, X: pd.DataFrame, top_k: int = 8) -> Dict[str, Any]:
        values: List[Dict[str, Any]] = []
        method = "feature_importance_fallback"

        try:
            import shap

            explainer = shap.TreeExplainer(model)
            raw = explainer.shap_values(X)
            if isinstance(raw, list):
                pred_index = int(np.argmax(model.predict_proba(X)[0]))
                contributions = np.asarray(raw[pred_index])[0]
            else:
                arr = np.asarray(raw)
                if arr.ndim == 3:
                    pred_index = int(np.argmax(model.predict_proba(X)[0]))
                    contributions = arr[0, :, pred_index]
                else:
                    contributions = arr.reshape(-1)
            method = "SHAP"
            order = np.argsort(np.abs(contributions))[::-1][:top_k]
            for i in order:
                values.append({
                    "feature": FEATURE_COLUMNS[int(i)],
                    "impact": round(float(contributions[int(i)]), 6),
                    "direction": "increases_risk" if contributions[int(i)] > 0 else "reduces_risk",
                    "value": round(float(X.iloc[0, int(i)]), 6),
                })
        except Exception:
            if hasattr(model, "feature_importances_"):
                importance = np.asarray(model.feature_importances_)
                order = np.argsort(importance)[::-1][:top_k]
                for i in order:
                    values.append({
                        "feature": FEATURE_COLUMNS[int(i)],
                        "impact": round(float(importance[int(i)]), 6),
                        "direction": "important_feature",
                        "value": round(float(X.iloc[0, int(i)]), 6),
                    })

        return {"method": method, "top_features": values}


explainability_service = ExplainabilityService()
