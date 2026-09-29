"""Train the optional LSTM on sequential synthetic cycle features."""

from __future__ import annotations

import json
import joblib
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from .config import ARTIFACT_DIR, FEATURE_COLUMNS, FAULT_CLASSES, RANDOM_STATE, FEATURE_SCHEMA_VERSION
from .train import generate
from .lstm_model import FaultLSTM


def train_lstm(samples_per_class: int = 1000, seq_len: int = 10, epochs: int = 15):
    df = generate(samples_per_class)
    X = df[FEATURE_COLUMNS].to_numpy(dtype=np.float32)
    labels = {name: i for i, name in enumerate(FAULT_CLASSES)}
    y = df["label"].map(labels).to_numpy(dtype=np.int64)

    scaler = StandardScaler()
    X = scaler.fit_transform(X).astype(np.float32)

    sequences, targets = [], []
    for end in range(seq_len - 1, len(X)):
        sequences.append(X[end - seq_len + 1:end + 1])
        targets.append(y[end])

    sequences = np.asarray(sequences, dtype=np.float32)
    targets = np.asarray(targets, dtype=np.int64)
    train_idx, val_idx = train_test_split(
        np.arange(len(targets)), test_size=0.2, random_state=RANDOM_STATE, stratify=targets
    )

    torch.manual_seed(RANDOM_STATE)
    model = FaultLSTM(len(FEATURE_COLUMNS), num_classes=len(FAULT_CLASSES))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = nn.CrossEntropyLoss()

    train_ds = TensorDataset(torch.tensor(sequences[train_idx]), torch.tensor(targets[train_idx]))
    loader = DataLoader(train_ds, batch_size=64, shuffle=True)

    model.train()
    for _ in range(epochs):
        for xb, yb in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

    model.eval()
    with torch.no_grad():
        pred = model(torch.tensor(sequences[val_idx])).argmax(dim=1).numpy()

    metrics = {
        "accuracy": float(accuracy_score(targets[val_idx], pred)),
        "f1_weighted": float(f1_score(targets[val_idx], pred, average="weighted")),
        "sequence_length": seq_len,
        "epochs": epochs,
        "classes": FAULT_CLASSES,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "features": FEATURE_COLUMNS,
        "source": "synthetic_controlled_fault_data",
    }

    torch.save(
        {"state_dict": model.state_dict(), "input_size": len(FEATURE_COLUMNS), "num_classes": len(FAULT_CLASSES)},
        ARTIFACT_DIR / "lstm_fault_classifier.pt",
    )
    joblib.dump(scaler, ARTIFACT_DIR / "lstm_scaler.joblib")
    (ARTIFACT_DIR / "lstm_metadata.json").write_text(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    print(json.dumps(train_lstm(), indent=2))
