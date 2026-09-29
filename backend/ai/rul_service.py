"""Transparent trend-based degradation/RUL estimator.

This is intentionally not presented as a trained failure-time model. It uses
recent completed-cycle trends and the live ML anomaly score to estimate
remaining cycles until a configurable degradation threshold.
"""

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from backend.machine.machine_engine import engine


class RULService:
    def __init__(self, target_degradation: float = 1.0):
        self.target_degradation = target_degradation

    def predict(self, anomaly_score: float = 0.0) -> Dict[str, Any]:
        history = engine.get_history(limit=6000)
        grouped = {}
        for row in history:
            cycle = row.get("cycle", {})
            if isinstance(cycle, dict):
                number = cycle.get("number")
                duration = cycle.get("duration")
                if number and duration and float(duration) > 0:
                    grouped.setdefault(int(number), float(duration))

        durations = np.asarray(
            [grouped[k] for k in sorted(grouped)],
            dtype=float,
        )

        if len(durations) < 5:
            return {
                "status": "INSUFFICIENT_HISTORY",
                "method": "trend_based_degradation",
                "required_cycles": 5,
                "available_cycles": int(len(durations)),
            }

        recent = durations[-5:]
        baseline = float(np.mean(durations[: max(3, len(durations) // 2)]))
        current = float(np.mean(recent[-3:]))

        duration_degradation = max(
            0.0,
            (current - baseline) / max(baseline, 1e-6),
        )
        degradation = float(
            np.clip(
                0.55 * duration_degradation
                + 0.45 * float(anomaly_score),
                0.0,
                1.0,
            )
        )

        x = np.arange(len(recent), dtype=float)
        slope = float(np.polyfit(x, recent, 1)[0]) if len(recent) >= 2 else 0.0
        normalized_slope = max(0.0, slope / max(baseline, 1e-6))

        if normalized_slope <= 0.001:
            remaining = 9999
            risk = "LOW"
        else:
            remaining = int(
                max(
                    1,
                    min(
                        9999,
                        (1.0 - degradation)
                        / normalized_slope,
                    ),
                )
            )
            risk = "HIGH" if remaining < 20 else "MEDIUM" if remaining < 75 else "LOW"

        health = int(round(max(0.0, 100.0 * (1.0 - degradation))))

        return {
            "status": "ESTIMATED",
            "method": "trend_based_degradation",
            "health_percent": health,
            "degradation_index": round(degradation, 4),
            "degradation_rate_per_cycle": round(normalized_slope, 6),
            "estimated_remaining_cycles": remaining,
            "maintenance_risk": risk,
            "baseline_cycle_duration": round(baseline, 4),
            "recent_cycle_duration": round(current, 4),
            "cycle_count_used": int(len(durations)),
            "note": "Heuristic degradation estimate; validate with real failure-history data before operational use.",
        }


rul_service = RULService()
