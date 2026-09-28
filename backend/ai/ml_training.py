import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

def train_isolation_forest(X: np.ndarray, output_path: str):
    model = IsolationForest(n_estimators=200, contamination="auto", random_state=42)
    model.fit(X)
    joblib.dump(model, output_path)
    return model

def predict(model, X: np.ndarray):
    return model.predict(X), model.decision_function(X)
