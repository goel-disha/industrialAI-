from pathlib import Path
ML_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = ML_DIR / "artifacts"
DATA_DIR = ML_DIR / "data"
ARTIFACT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 42
FEATURE_SCHEMA_VERSION = 3

FEATURE_COLUMNS = [
    "cycle_duration",
    "busy_ratio",
    "state_transitions",
    "servo_error_count",
] + [
    f"{axis}_{feature}"
    for axis in ("a1", "a2", "a3")
    for feature in (
        "mean_pos_error",
        "max_pos_error",
        "std_pos_error",
        "mean_speed",
        "mean_actual_speed",
        "speed_deviation",
        "position_std",
        "motion_jitter",
    )
]

FAULT_CLASSES = [
    "NORMAL",
    "SERVO_LAG",
    "VIBRATION",
    "STUCK_AXIS",
    "SENSOR_NOISE",
    "CYCLE_DEGRADATION",
]
