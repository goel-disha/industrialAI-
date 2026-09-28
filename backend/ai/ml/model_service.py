import json
import joblib
import numpy as np
import pandas as pd

from .config import ARTIFACT_DIR, FEATURE_COLUMNS
from .features import cycle_to_features

from backend.machine.machine_engine import engine


class MLModelService:

    def __init__(self):
        self.reload()

    # ---------------------------------------------------------
    # Load trained ML artifacts
    # ---------------------------------------------------------

    def reload(self):

        required_files = [
            "anomaly_model.joblib",
            "classifier.joblib",
            "cycle_regressor.joblib",
            "scaler.joblib",
            "regression_scaler.joblib",
        ]

        paths = [
            ARTIFACT_DIR / filename
            for filename in required_files
        ]

        self.ready = all(
            path.exists()
            for path in paths
        )

        if self.ready:

            self.iso = joblib.load(
                ARTIFACT_DIR / "anomaly_model.joblib"
            )

            self.clf = joblib.load(
                ARTIFACT_DIR / "classifier.joblib"
            )

            self.reg = joblib.load(
                ARTIFACT_DIR / "cycle_regressor.joblib"
            )

            self.sc = joblib.load(
                ARTIFACT_DIR / "scaler.joblib"
            )

            self.reg_sc = joblib.load(
                ARTIFACT_DIR / "regression_scaler.joblib"
            )

        metrics_path = (
            ARTIFACT_DIR / "metrics.json"
        )

        self.metrics = (
            json.loads(
                metrics_path.read_text()
            )
            if metrics_path.exists()
            else {}
        )

    # ---------------------------------------------------------
    # Service status
    # ---------------------------------------------------------

    def status(self):

        return {
            "ready": self.ready,
            "features": FEATURE_COLUMNS,
            "models": {
                "anomaly_detection": self.ready,
                "fault_classification": self.ready,
                "next_cycle_duration": self.ready,
            },
        }

    # ---------------------------------------------------------
    # Extract latest completed cycle
    # ---------------------------------------------------------

    def get_latest_cycle(self):

        history = engine.get_history(
            limit=6000
        )

        if not history:
            return []

        # Get cycle numbers from telemetry
        cycle_numbers = []

        for row in history:

            cycle = row.get("cycle", {})

            if isinstance(cycle, dict):

                number = cycle.get(
                    "number",
                    0
                )

                if number:
                    cycle_numbers.append(
                        number
                    )

        if not cycle_numbers:
            return history[-300:]

        latest_cycle = max(
            cycle_numbers
        )

        cycle_rows = [

            row

            for row in history

            if isinstance(
                row.get("cycle", {}),
                dict
            )
            and row["cycle"].get(
                "number",
                0
            ) == latest_cycle
        ]

        return cycle_rows

    # ---------------------------------------------------------
    # Prepare feature vector
    # ---------------------------------------------------------

    def build_features(self, rows):

        features = cycle_to_features(
            rows
        )

        # Classification / anomaly model
        X = pd.DataFrame(
            [
                [
                    features[column]
                    for column in FEATURE_COLUMNS
                ]
            ],
            columns=FEATURE_COLUMNS,
        )

        # Regression model DOES NOT use cycle_duration
        regression_features = [

            column

            for column in FEATURE_COLUMNS

            if column != "cycle_duration"
        ]

        X_reg = X[
            regression_features
        ]

        return (
            features,
            X,
            X_reg,
        )

    # ---------------------------------------------------------
    # Live ML prediction
    # ---------------------------------------------------------

    def predict_live(self):

        if not self.ready:

            raise RuntimeError(
                "ML models are not trained. "
                "Run python -m backend.ai.ml.train"
            )

        rows = self.get_latest_cycle()

        if not rows:

            raise RuntimeError(
                "No telemetry available for ML inference."
            )

        features, X, X_reg = (
            self.build_features(rows)
        )

        # -----------------------------------------------------
        # Classification / anomaly scaling
        # -----------------------------------------------------

        Z = self.sc.transform(
            X
        )

        # -----------------------------------------------------
        # Isolation Forest
        # -----------------------------------------------------

        raw_score = float(
            self.iso.decision_function(
                Z
            )[0]
        )

        anomaly = bool(
            self.iso.predict(
                Z
            )[0] == -1
        )

        # This is an anomaly score,
        # NOT a probability.
        anomaly_score = float(
            np.clip(
                0.5 - raw_score,
                0,
                1,
            )
        )

        # -----------------------------------------------------
        # Fault classification
        # -----------------------------------------------------

        predicted_fault = str(
            self.clf.predict(
                Z
            )[0]
        )

        probabilities = (
            self.clf.predict_proba(
                Z
            )[0]
        )

        fault_confidence = float(
            max(probabilities)
        )

        # -----------------------------------------------------
        # Next-cycle duration prediction
        # -----------------------------------------------------

        R = self.reg_sc.transform(
            X_reg
        )

        predicted_duration = float(
            self.reg.predict(
                R
            )[0]
        )

        # -----------------------------------------------------
        # Current machine information
        # -----------------------------------------------------

        latest = rows[-1]

        cycle = latest.get(
            "cycle",
            {}
        )

        if not isinstance(
            cycle,
            dict
        ):
            cycle = {}

        return {

            "anomaly":
                anomaly,

            "anomaly_score":
                round(
                    anomaly_score,
                    4
                ),

            "predicted_fault":
                predicted_fault,

            "fault_confidence":
                round(
                    fault_confidence,
                    4
                ),

            "predicted_next_cycle_duration":
                round(
                    predicted_duration,
                    4
                ),

            "machine_state":
                latest.get(
                    "state",
                    "IDLE"
                ),

            "cycle_number":
                cycle.get(
                    "number",
                    0
                ),

            "cycle_running":
                cycle.get(
                    "running",
                    False
                ),

            "timestamp":
                latest.get(
                    "timestamp"
                ),

            "samples_used":
                len(rows),

            "features":
                features,
        }


ml_service = MLModelService()