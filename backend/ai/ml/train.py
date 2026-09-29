import json
import joblib
import numpy as np
import pandas as pd

from datetime import datetime, timezone

from sklearn.ensemble import (
    IsolationForest,
    RandomForestClassifier,
    RandomForestRegressor,
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    confusion_matrix,
)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .config import *


# ---------------------------------------------------------
# Synthetic industrial cycle data
# ---------------------------------------------------------

def generate(n=1000):
    r = np.random.default_rng(RANDOM_STATE)
    rows = []

    for label in FAULT_CLASSES:
        for _ in range(n):
            d = {
                "cycle_duration": max(5.0, r.normal(7.6, 0.08)),
                "busy_ratio": np.clip(r.normal(0.80, 0.025), 0.0, 1.0),
                "state_transitions": max(0.0, r.normal(6, 0.3)),
                "servo_error_count": 0.0,
            }

            for p in ("a1", "a2", "a3"):
                d[f"{p}_mean_pos_error"] = abs(r.normal(0.015, 0.004))
                d[f"{p}_max_pos_error"] = abs(r.normal(0.040, 0.010))
                d[f"{p}_std_pos_error"] = abs(r.normal(0.012, 0.004))
                d[f"{p}_mean_speed"] = 1.0
                d[f"{p}_mean_actual_speed"] = np.clip(r.normal(0.995, 0.015), 0.0, 1.1)
                d[f"{p}_speed_deviation"] = abs(r.normal(0.02, 0.008))
                d[f"{p}_position_std"] = abs(r.normal(0.015, 0.004))

            if label == "SERVO_LAG":
                d["a2_mean_actual_speed"] = np.clip(r.uniform(0.35, 0.65), 0.0, 1.0)
                d["a2_speed_deviation"] = r.uniform(0.35, 0.65)
                d["a2_mean_pos_error"] *= 2.2
                d["a2_max_pos_error"] *= 2.5
                d["cycle_duration"] *= r.uniform(1.08, 1.20)

            elif label == "VIBRATION":
                d["a2_position_std"] *= 4
                d["a3_position_std"] *= 3
                d["a2_std_pos_error"] *= 3
                d["a3_std_pos_error"] *= 2.5

            elif label == "STUCK_AXIS":
                d["a3_mean_actual_speed"] = r.uniform(0.01, 0.05)
                d["a3_speed_deviation"] = r.uniform(0.85, 1.0)
                d["a3_mean_pos_error"] *= 5
                d["a3_max_pos_error"] *= 6
                d["cycle_duration"] *= r.uniform(1.25, 1.55)

            elif label == "SENSOR_NOISE":
                for p in ("a1", "a2", "a3"):
                    d[f"{p}_position_std"] *= 5
                    d[f"{p}_std_pos_error"] *= 4

            elif label == "CYCLE_DEGRADATION":
                d["cycle_duration"] *= r.uniform(1.20, 1.45)
                d["busy_ratio"] = min(0.98, d["busy_ratio"] + 0.08)

            d["label"] = label
            rows.append(d)

    return pd.DataFrame(rows)[FEATURE_COLUMNS + ["label"]]


# ---------------------------------------------------------
# Train all ML models
# ---------------------------------------------------------

def train_all(samples_per_class=1000):

    print("\n========================================")
    print(" INDUSTRIALAI ML TRAINING")
    print("========================================\n")

    df = generate(samples_per_class)

    dataset_path = DATA_DIR / "synthetic_cycle_dataset.csv"

    df.to_csv(
        dataset_path,
        index=False
    )

    print(f"Dataset saved: {dataset_path}")
    print(f"Dataset shape: {df.shape}")

    # -----------------------------------------------------
    # Train / validation split
    # -----------------------------------------------------

    X = df[FEATURE_COLUMNS]
    y = df["label"]

    Xt, Xv, yt, yv = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # -----------------------------------------------------
    # Scaling
    # -----------------------------------------------------

    scaler = StandardScaler()

    A = scaler.fit_transform(Xt)
    B = scaler.transform(Xv)

    # -----------------------------------------------------
    # 1. ANOMALY DETECTION
    # -----------------------------------------------------

    print("\n[1/3] Training Isolation Forest...")

    iso = IsolationForest(
        n_estimators=300,
        contamination=0.05,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    # Train only on NORMAL cycles
    iso.fit(
        A[yt == "NORMAL"]
    )

    anomaly_prediction = (
        iso.predict(B) == -1
    ).astype(int)

    anomaly_truth = (
        yv != "NORMAL"
    ).astype(int)

    anomaly_metrics = {
        "precision": float(
            precision_score(
                anomaly_truth,
                anomaly_prediction,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                anomaly_truth,
                anomaly_prediction,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                anomaly_truth,
                anomaly_prediction,
                zero_division=0,
            )
        ),
    }

    # -----------------------------------------------------
    # 2. FAULT CLASSIFICATION
    # -----------------------------------------------------

    print("[2/3] Training Random Forest classifier...")

    clf = RandomForestClassifier(
        n_estimators=400,
        max_depth=14,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    clf.fit(
        A,
        yt,
    )

    classification_prediction = clf.predict(B)

    classification_metrics = {
        "accuracy": float(
            accuracy_score(
                yv,
                classification_prediction,
            )
        ),
        "precision_weighted": float(
            precision_score(
                yv,
                classification_prediction,
                average="weighted",
                zero_division=0,
            )
        ),
        "recall_weighted": float(
            recall_score(
                yv,
                classification_prediction,
                average="weighted",
                zero_division=0,
            )
        ),
        "f1_weighted": float(
            f1_score(
                yv,
                classification_prediction,
                average="weighted",
                zero_division=0,
            )
        ),
        "confusion_matrix": confusion_matrix(
            yv,
            classification_prediction,
            labels=clf.classes_,
        ).tolist(),
        "classes": clf.classes_.tolist(),
    }

    # -----------------------------------------------------
    # 3. NEXT-CYCLE DURATION REGRESSION
    # -----------------------------------------------------
    #
    # IMPORTANT:
    # We do NOT give the model the current cycle_duration.
    #
    # Instead:
    #
    #   previous cycle features
    #             ↓
    #      predict next duration
    #
    # -----------------------------------------------------

    print("[3/3] Training next-cycle duration regressor...")

    regression_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature != "cycle_duration"
    ]

    # Sort the dataset so each row can represent
    # a previous -> next cycle relationship.
    #
    # The synthetic generator produces blocks of cycles,
    # so we create temporal pairs within each fault class.

    regression_df = df.copy()

    X_reg_current = regression_df[
        regression_features
    ].copy()

    y_reg_next = regression_df[
        "cycle_duration"
    ].shift(-1)

    # Remove the final row because it has no next cycle.
    X_reg_current = X_reg_current.iloc[:-1]
    y_reg_next = y_reg_next.iloc[:-1]

    Xrt, Xrv, yrt, yrv = train_test_split(
        X_reg_current,
        y_reg_next,
        test_size=0.20,
        random_state=RANDOM_STATE,
    )

    regression_scaler = StandardScaler()

    R_train = regression_scaler.fit_transform(
        Xrt
    )

    R_val = regression_scaler.transform(
        Xrv
    )

    reg = RandomForestRegressor(
        n_estimators=400,
        max_depth=16,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    reg.fit(
        R_train,
        yrt,
    )

    regression_prediction = reg.predict(
        R_val
    )

    regression_metrics = {
        "mae_seconds": float(
            mean_absolute_error(
                yrv,
                regression_prediction,
            )
        ),
        "rmse_seconds": float(
            np.sqrt(
                mean_squared_error(
                    yrv,
                    regression_prediction,
                )
            )
        ),
        "r2": float(
            r2_score(
                yrv,
                regression_prediction,
            )
        ),
        "target": "next_cycle_duration",
        "input_features": regression_features,
    }

    # -----------------------------------------------------
    # Save models
    # -----------------------------------------------------

    print("\nSaving trained models...")

    joblib.dump(
        iso,
        ARTIFACT_DIR / "anomaly_model.joblib",
    )

    joblib.dump(
        clf,
        ARTIFACT_DIR / "classifier.joblib",
    )

    joblib.dump(
        reg,
        ARTIFACT_DIR / "cycle_regressor.joblib",
    )

    joblib.dump(
        scaler,
        ARTIFACT_DIR / "scaler.joblib",
    )

    joblib.dump(
        regression_scaler,
        ARTIFACT_DIR / "regression_scaler.joblib",
    )

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    metrics = {

        "dataset": {
            "samples": int(len(df)),
            "features": len(FEATURE_COLUMNS),
            "classes": FAULT_CLASSES,
        },

        "anomaly_detection":
            anomaly_metrics,

        "fault_classification":
            classification_metrics,

        "next_cycle_duration_regression":
            regression_metrics,
    }

    metrics_path = (
        ARTIFACT_DIR / "metrics.json"
    )

    metrics_path.write_text(
        json.dumps(
            metrics,
            indent=2,
        )
    )

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------

    metadata = {

        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "source":
            "synthetic_controlled_fault_data",

        "samples_per_class":
            samples_per_class,

        "features":
            FEATURE_COLUMNS,

        "regression_target":
            "next_cycle_duration",

        "regression_input_features":
            regression_features,
    }

    (
        ARTIFACT_DIR / "metadata.json"
    ).write_text(
        json.dumps(
            metadata,
            indent=2,
        )
    )

    # -----------------------------------------------------
    # Print final results
    # -----------------------------------------------------

    print("\n========================================")
    print(" TRAINING COMPLETE")
    print("========================================")

    print("\nAnomaly Detection")
    print(
        json.dumps(
            anomaly_metrics,
            indent=2,
        )
    )

    print("\nFault Classification")
    print(
        json.dumps(
            classification_metrics,
            indent=2,
        )
    )

    print("\nNext Cycle Duration")
    print(
        json.dumps(
            regression_metrics,
            indent=2,
        )
    )

    print("\nModels saved to:")
    print(ARTIFACT_DIR)

    return metrics


if __name__ == "__main__":

    print(
        json.dumps(
            train_all(),
            indent=2,
        )
    )