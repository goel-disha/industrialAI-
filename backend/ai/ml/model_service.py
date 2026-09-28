import json
import joblib
import numpy as np
import pandas as pd

from .config import ARTIFACT_DIR, FEATURE_COLUMNS
from .features import cycle_to_features
from .ensemble import ensemble
from .xgb_service import xgb_service
from .explainability_service import explainability_service
from backend.machine.machine_engine import engine


class MLModelService:
    def __init__(self):
        self.reload()

    def reload(self):
        required_files = [
            "anomaly_model.joblib",
            "classifier.joblib",
            "cycle_regressor.joblib",
            "scaler.joblib",
            "regression_scaler.joblib",
        ]
        paths = [ARTIFACT_DIR / filename for filename in required_files]
        self.ready = all(path.exists() for path in paths)
        if self.ready:
            self.iso = joblib.load(ARTIFACT_DIR / "anomaly_model.joblib")
            self.clf = joblib.load(ARTIFACT_DIR / "classifier.joblib")
            self.reg = joblib.load(ARTIFACT_DIR / "cycle_regressor.joblib")
            self.sc = joblib.load(ARTIFACT_DIR / "scaler.joblib")
            self.reg_sc = joblib.load(ARTIFACT_DIR / "regression_scaler.joblib")
        xgb_service.reload()
        metrics_path = ARTIFACT_DIR / "metrics.json"
        self.metrics = json.loads(metrics_path.read_text()) if metrics_path.exists() else {}

    def status(self):
        return {
            "ready": self.ready,
            "features": FEATURE_COLUMNS,
            "models": {
                "anomaly_detection": self.ready,
                "random_forest_fault_classifier": self.ready,
                "xgboost_fault_classifier": xgb_service.ready,
                "next_cycle_duration": self.ready,
                "explainability": self.ready,
            },
        }

    def get_latest_cycle(self):
        history = engine.get_history(limit=6000)
        if not history:
            return []
        cycle_numbers = []
        for row in history:
            cycle = row.get("cycle", {})
            if isinstance(cycle, dict) and cycle.get("number"):
                cycle_numbers.append(cycle["number"])
        if not cycle_numbers:
            return history[-300:]
        latest_cycle = max(cycle_numbers)
        return [
            row for row in history
            if isinstance(row.get("cycle", {}), dict)
            and row["cycle"].get("number", 0) == latest_cycle
        ]

    def build_features(self, rows):
        features = cycle_to_features(rows)
        X = pd.DataFrame([[features[column] for column in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        regression_features = [column for column in FEATURE_COLUMNS if column != "cycle_duration"]
        return features, X, X[regression_features]

    def predict_live(self):
        if not self.ready:
            raise RuntimeError("ML models are not trained. Run python -m backend.ai.ml.train")
        rows = self.get_latest_cycle()
        if not rows:
            raise RuntimeError("No telemetry available for ML inference.")

        features, X, X_reg = self.build_features(rows)
        Z = self.sc.transform(X)

        raw_score = float(self.iso.decision_function(Z)[0])
        anomaly = bool(self.iso.predict(Z)[0] == -1)
        anomaly_score = float(np.clip(0.5 - raw_score, 0, 1))

        rf_fault = str(self.clf.predict(Z)[0])
        probabilities = self.clf.predict_proba(Z)[0]
        rf_confidence = float(max(probabilities))

        xgb_prediction = xgb_service.predict(features)
        combined = ensemble.combine(
            anomaly=anomaly,
            anomaly_score=anomaly_score,
            rf_fault=rf_fault,
            rf_confidence=rf_confidence,
            xgb_fault=xgb_prediction["fault"] if xgb_prediction else None,
            xgb_confidence=xgb_prediction["confidence"] if xgb_prediction else 0.0,
        )

        R = self.reg_sc.transform(X_reg)
        predicted_duration = float(self.reg.predict(R)[0])
        explanation = explainability_service.explain_classifier(self.clf, X)

        latest = rows[-1]
        cycle = latest.get("cycle", {})
        if not isinstance(cycle, dict):
            cycle = {}

        return {
            "anomaly": combined["anomaly"],
            "anomaly_score": combined["anomaly_score"],
            "predicted_fault": combined["predicted_fault"],
            "fault_confidence": combined["confidence"],
            "model_agreement": combined["model_agreement"],
            "models_used": combined["models_used"],
            "xgboost": xgb_prediction,
            "predicted_next_cycle_duration": round(predicted_duration, 4),
            "machine_state": latest.get("state", "IDLE"),
            "cycle_number": cycle.get("number", 0),
            "cycle_running": cycle.get("running", False),
            "timestamp": latest.get("timestamp"),
            "samples_used": len(rows),
            "explanation": explanation,
            "features": features,
        }


ml_service = MLModelService()
