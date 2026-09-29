"""Train the XGBoost fault classifier from the same controlled dataset."""

from __future__ import annotations

import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score
from xgboost import XGBClassifier

from .config import ARTIFACT_DIR, FEATURE_COLUMNS, RANDOM_STATE, FEATURE_SCHEMA_VERSION
from .train import generate


def train_xgb(samples_per_class: int = 1000):
    df = generate(samples_per_class)
    X = df[FEATURE_COLUMNS]
    y = df["label"]

    classes = sorted(y.unique())
    class_to_id = {name: i for i, name in enumerate(classes)}
    y_id = y.map(class_to_id)

    Xt, Xv, yt, yv = train_test_split(
        X, y_id, test_size=0.20, random_state=RANDOM_STATE, stratify=y_id
    )

    scaler = StandardScaler()
    A = scaler.fit_transform(Xt)
    B = scaler.transform(Xv)

    model = XGBClassifier(
        n_estimators=350,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob",
        num_class=len(classes),
        eval_metric="mlogloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(A, yt)
    pred_id = model.predict(B).astype(int)

    id_to_class = {v: k for k, v in class_to_id.items()}
    pred = [id_to_class[int(i)] for i in pred_id]
    truth = [id_to_class[int(i)] for i in yv]

    metrics = {
        "accuracy": float(accuracy_score(truth, pred)),
        "f1_weighted": float(f1_score(truth, pred, average="weighted")),
        "classes": classes,
    }

    joblib.dump(model, ARTIFACT_DIR / "xgboost_classifier.joblib")
    joblib.dump(scaler, ARTIFACT_DIR / "xgboost_scaler.joblib")
    (ARTIFACT_DIR / "xgboost_metadata.json").write_text(
        json.dumps({
            "class_to_id": class_to_id,
            "metrics": metrics,
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "features": FEATURE_COLUMNS,
        }, indent=2)
    )
    return metrics


if __name__ == "__main__":
    print(json.dumps(train_xgb(), indent=2))
