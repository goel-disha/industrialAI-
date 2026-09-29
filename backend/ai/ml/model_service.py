import json
import joblib
import numpy as np
import pandas as pd

from .config import ARTIFACT_DIR, FEATURE_COLUMNS, FEATURE_SCHEMA_VERSION
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
        metadata_path = ARTIFACT_DIR / "metadata.json"
        self.metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
        self.schema_compatible = self.metadata.get("feature_schema_version") == FEATURE_SCHEMA_VERSION

    def status(self):
        return {
            "ready": self.ready,
            "features": FEATURE_COLUMNS,
            "models": {
                "anomaly_detection": self.ready and self.schema_compatible,
                "random_forest_fault_classifier": self.ready and self.schema_compatible,
                "xgboost_fault_classifier": xgb_service.ready,
                "next_cycle_duration": self.ready and self.schema_compatible,
                "explainability": self.ready and self.schema_compatible,
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
        X = pd.DataFrame(
            [[features[column] for column in FEATURE_COLUMNS]],
            columns=FEATURE_COLUMNS,
        )
        regression_features = [
            column for column in FEATURE_COLUMNS
            if column != "cycle_duration"
        ]
        return features, X, X[regression_features]

    def predict_features(self, features, context=None):
        if not self.ready:
            raise RuntimeError("ML models are not trained.")
        if not self.schema_compatible:
            raise RuntimeError(
                "ML artifacts use an incompatible feature schema. "
                "Retrain with: python -m backend.ai.ml.train"
            )

        features = {column: float(features.get(column, 0.0)) for column in FEATURE_COLUMNS}
        X = pd.DataFrame(
            [[features[column] for column in FEATURE_COLUMNS]],
            columns=FEATURE_COLUMNS,
        )
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

        regression_features = [
            column for column in FEATURE_COLUMNS
            if column != "cycle_duration"
        ]
        R = self.reg_sc.transform(X[regression_features])
        predicted_duration = float(self.reg.predict(R)[0])
        explanation = explainability_service.explain_classifier(self.clf, X)

        result = {
            "anomaly": combined["anomaly"],
            "anomaly_score": combined["anomaly_score"],
            "predicted_fault": combined["predicted_fault"],
            "fault_confidence": combined["confidence"],
            "model_agreement": combined["model_agreement"],
            "models_used": combined["models_used"],
            "xgboost": xgb_prediction,
            "predicted_next_cycle_duration": round(predicted_duration, 4),
            "explanation": explanation,
            "features": features,
        }
        if context:
            result.update(context)
        return result

    def predict_live(self):
        if not self.ready:
            raise RuntimeError("ML models are not trained. Run python -m backend.ai.ml.train")
        rows = self.get_latest_cycle()
        if not rows:
            raise RuntimeError("No telemetry available for ML inference.")

        cycle_numbers = [
            int((row.get("cycle") or {}).get("number", 0))
            for row in rows
            if (row.get("cycle") or {}).get("number")
        ]
        if not cycle_numbers:
            raise RuntimeError("No cycle telemetry available for ML inference.")

        completed_cycles = {}
        for row in rows:
            cycle = row.get("cycle", {}) or {}
            number = cycle.get("number")
            if number and cycle.get("complete"):
                completed_cycles.setdefault(int(number), []).append(row)

        if not completed_cycles:
            raise RuntimeError("No completed cycle telemetry available for ML inference.")

        inference_cycle = max(completed_cycles)
        inference_rows = completed_cycles[inference_cycle]
        features, _, _ = self.build_features(inference_rows)

        current = rows[-1]
        current_cycle = current.get("cycle", {}) or {}

        return self.predict_features(
            features,
            context={
                "machine_state": current.get("state", "IDLE"),
                "cycle_number": current_cycle.get("number", inference_cycle),
                "cycle_running": current_cycle.get("running", False),
                "inference_cycle_number": inference_cycle,
                "inference_cycle_complete": True,
                "timestamp": current.get("timestamp"),
                "samples_used": len(inference_rows),
            },
        )


ml_service = MLModelService()
