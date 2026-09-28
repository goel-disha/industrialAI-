"""Live LSTM inference over the most recent completed machine cycles."""

from __future__ import annotations

import json
from typing import Any, Dict

import joblib
import numpy as np
import torch

from .config import ARTIFACT_DIR, FEATURE_COLUMNS, FAULT_CLASSES
from .features import cycle_to_features
from .lstm_model import FaultLSTM
from backend.machine.machine_engine import engine


class LSTMService:
    def __init__(self, sequence_length: int = 10):
        self.sequence_length = sequence_length
        self.reload()

    def reload(self):
        model_path = ARTIFACT_DIR / "lstm_fault_classifier.pt"
        scaler_path = ARTIFACT_DIR / "lstm_scaler.joblib"
        metadata_path = ARTIFACT_DIR / "lstm_metadata.json"
        self.ready = model_path.exists() and scaler_path.exists() and metadata_path.exists()
        if not self.ready:
            return
        checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
        self.model = FaultLSTM(
            checkpoint["input_size"],
            num_classes=checkpoint["num_classes"],
        )
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()
        self.scaler = joblib.load(scaler_path)
        metadata = json.loads(metadata_path.read_text())
        self.sequence_length = int(metadata.get("sequence_length", self.sequence_length))

    def status(self) -> Dict[str, Any]:
        return {"ready": self.ready, "model": "lstm_fault_classifier", "sequence_length": self.sequence_length}

    def _cycle_rows(self):
        history = engine.get_history(limit=6000)
        grouped = {}
        for row in history:
            cycle = row.get("cycle", {})
            if isinstance(cycle, dict) and cycle.get("number"):
                grouped.setdefault(int(cycle["number"]), []).append(row)
        return [grouped[k] for k in sorted(grouped)][-self.sequence_length:]

    def predict_live(self):
        if not self.ready:
            return None
        groups = self._cycle_rows()
        if len(groups) < self.sequence_length:
            return {"ready": True, "status": "INSUFFICIENT_HISTORY", "required_cycles": self.sequence_length, "available_cycles": len(groups)}

        vectors = []
        for rows in groups:
            f = cycle_to_features(rows)
            vectors.append([f[c] for c in FEATURE_COLUMNS])
        X = self.scaler.transform(np.asarray(vectors, dtype=np.float32)).astype(np.float32)

        with torch.no_grad():
            logits = self.model(torch.tensor(X).unsqueeze(0))
            probabilities = torch.softmax(logits, dim=1).numpy()[0]
        index = int(np.argmax(probabilities))
        return {
            "ready": True,
            "predicted_fault": FAULT_CLASSES[index],
            "confidence": round(float(probabilities[index]), 4),
            "sequence_length": len(groups),
        }


lstm_service = LSTMService()
