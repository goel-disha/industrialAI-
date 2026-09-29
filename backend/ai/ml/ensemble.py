"""Ensemble inference for the IndustrialAI predictive-maintenance stack.

Combines the existing Isolation Forest + Random Forest outputs with an
optional XGBoost model when it is available. The ensemble is deliberately
conservative: anomaly detection remains independent and the fault decision
uses confidence-weighted model agreement.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class AIEnsemble:
    def combine(
        self,
        anomaly: bool,
        anomaly_score: float,
        rf_fault: str,
        rf_confidence: float,
        xgb_fault: Optional[str] = None,
        xgb_confidence: float = 0.0,
    ) -> Dict[str, Any]:
        if xgb_fault and xgb_confidence > 0:
            if xgb_fault == rf_fault:
                fault = rf_fault
                confidence = (rf_confidence + xgb_confidence) / 2.0
                agreement = "AGREE"
            elif xgb_confidence > rf_confidence:
                fault = xgb_fault
                confidence = xgb_confidence
                agreement = "DISAGREE_XGB_DOMINANT"
            else:
                fault = rf_fault
                confidence = rf_confidence
                agreement = "DISAGREE_RF_DOMINANT"
        else:
            fault = rf_fault
            confidence = rf_confidence
            agreement = "RF_ONLY"

        return {
            "anomaly": bool(anomaly),
            "anomaly_score": round(float(anomaly_score), 4),
            "predicted_fault": fault,
            "confidence": round(float(confidence), 4),
            "model_agreement": agreement,
            "confidence_note": "Model probability agreement; not calibrated probability of failure.",
            "models_used": ["isolation_forest", "random_forest"]
            + (["xgboost"] if xgb_fault else []),
        }


ensemble = AIEnsemble()
