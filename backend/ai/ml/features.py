from typing import Iterable, Dict
import numpy as np

from .config import FEATURE_COLUMNS


def num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _motion_jitter(positions, span):
    """Estimate high-frequency position jitter, not total travel variation."""
    if len(positions) < 3:
        return 0.0
    values = np.asarray(positions, dtype=float)
    second_diff = np.diff(values, n=2)
    return float(np.std(second_diff) / max(span, 1.0))


def cycle_to_features(rows: Iterable[dict]) -> Dict[str, float]:
    """
    Convert one completed machine cycle into dimensionless, scale-stable
    features. Servo positions are normalized by that axis' travel span and
    speeds are normalized by commanded speed, so the model is independent of
    PLC pulse/micrometre register magnitudes.
    """
    rows = list(rows)
    if not rows:
        raise ValueError("No telemetry rows supplied.")

    durations = [
        num((r.get("cycle") or {}).get("duration"))
        for r in rows
        if (r.get("cycle") or {}).get("complete")
    ]
    out = {
        "cycle_duration": next((x for x in reversed(durations) if x > 0), 0.0)
    }

    states = [r.get("state", "IDLE") for r in rows]
    out["busy_ratio"] = float(np.mean([s != "IDLE" for s in states]))
    out["state_transitions"] = float(
        sum(states[i] != states[i - 1] for i in range(1, len(states)))
    )
    out["servo_error_count"] = float(
        sum(bool((r.get(axis) or {}).get("error"))
            for r in rows for axis in ("axis1", "axis2", "axis3"))
    )

    for axis, prefix in (("axis1", "a1"), ("axis2", "a2"), ("axis3", "a3")):
        samples = [r.get(axis, {}) or {} for r in rows]

        positions = [num(x.get("position")) for x in samples]
        targets = [num(x.get("target")) for x in samples]
        span = max(max((abs(x) for x in targets), default=0.0),
                   max((abs(x) for x in positions), default=0.0), 1.0)

        pos_errors = [abs(t - p) / span for t, p in zip(targets, positions)]

        commands = [
            abs(num(x.get("command_speed", x.get("speed"))))
            for x in samples
        ]
        actuals = [
            abs(num(x.get("actual_speed", x.get("speed"))))
            for x in samples
        ]

        speed_ratios = [
            a / c if c > 1e-9 else 0.0
            for a, c in zip(actuals, commands)
        ]
        deviations = [
            abs(c - a) / c if c > 1e-9 else 0.0
            for a, c in zip(actuals, commands)
        ]

        normalized_positions = [p / span for p in positions]
        jitter = _motion_jitter(positions, span)

        out.update({
            f"{prefix}_mean_pos_error": float(np.mean(pos_errors)),
            f"{prefix}_max_pos_error": float(np.max(pos_errors)),
            f"{prefix}_std_pos_error": float(np.std(pos_errors)),
            f"{prefix}_mean_speed": float(np.mean([1.0 if c > 1e-9 else 0.0 for c in commands])),
            f"{prefix}_mean_actual_speed": float(np.mean(speed_ratios)),
            f"{prefix}_speed_deviation": float(np.mean(deviations)),
            f"{prefix}_position_std": float(np.std(normalized_positions)),
            f"{prefix}_motion_jitter": jitter,
        })

    return {k: float(out.get(k, 0.0)) for k in FEATURE_COLUMNS}
