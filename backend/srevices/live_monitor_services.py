from datetime import datetime, timezone

from backend.machine.plc_memory import plc
from backend.machine.machine_engine import engine
from backend.machine.auto_engine import auto
from backend.machine.servo_engine import (
    servo,
    axis1,
    axis2,
    axis3
)
from backend.machine.production_engine import production


# ==============================================================
# SAFE PLC READ
# ==============================================================

def read_bit(address):
    """
    Safely read a PLC bit.

    Missing / None values are treated as 0.
    """
    return int(
        plc.read(address) or 0
    )


def read_value(address):
    """
    Safely read a PLC numeric value.
    """
    value = plc.read(address)

    if value is None:
        return 0

    try:
        return float(value)

    except (
        ValueError,
        TypeError
    ):
        return value


# ==============================================================
# LIVE MONITOR
# ==============================================================

def live_monitor():

    # ----------------------------------------------------------
    # Get current servo telemetry
    # ----------------------------------------------------------

    servo_data = servo.telemetry()

    # ----------------------------------------------------------
    # MachineEngine is the authoritative source for cycle state
    # ----------------------------------------------------------

    cycle = engine.get_cycle_info()

    # A cycle is complete when:
    # - a cycle has actually started
    # - MachineEngine has recorded an end_time
    cycle_complete = (
        cycle["end_time"] is not None
        and cycle["cycle_number"] > 0
        and not cycle["running"]
    )

    return {

        # ======================================================
        # TIMESTAMP
        # ======================================================

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),


        # ======================================================
        # MACHINE
        # ======================================================

        "machine": {

            "state":
                engine.state,

            "model":
                engine.current_model,

            "auto_mode":
                bool(
                    read_bit("M500")
                ),

            "running":
                engine.running,

            # IMPORTANT:
            # Use MachineEngine rather than ProductionEngine
            # for actual machine cycle state.
            "cycle_running":
                cycle["running"],

            "cycle_complete":
                cycle_complete,

            "cycle_number":
                engine.cycle_number,

            "cycle_duration":
                cycle["current_duration"]
        },


        # ======================================================
        # SAFETY
        # ======================================================

        "safety": {

            "emergency":
                bool(
                    read_bit("M90")
                ),

            "air_fault":
                bool(
                    read_bit("M91")
                ),

            "cycle_stop":
                bool(
                    read_bit("L540")
                ),

            "reset":
                bool(
                    read_bit("L541")
                )
        },


        # ======================================================
        # SERVO
        # ======================================================

        "servo": {

            "axis1":
                servo_data["axis1"],

            "axis2":
                servo_data["axis2"],

            "axis3":
                servo_data["axis3"],

            "scan_count":
                servo_data["scan_count"]
        },


        # ======================================================
        # DIRECT POSITION FEEDBACK
        # ======================================================

        "positions": {

            "axis1":
                read_value("D1100"),

            "axis2":
                read_value("D1110"),

            "axis3":
                read_value("D1120")
        },


        # ======================================================
        # CENTERING
        # ======================================================

        "centering": {

            "forward":
                read_bit("Y46"),

            "reverse":
                read_bit("Y47"),

            "forward_limit":
                read_bit("X33"),

            "reverse_limit":
                read_bit("X34"),

            "part_centered":
                read_bit("L509")
        },


        # ======================================================
        # PRODUCTION
        # ======================================================

        "production": {

            # These remain owned by ProductionEngine.
            "total":
                production.total_cycles,

            "completed":
                production.completed_cycles,

            "rejected":
                production.rejected_cycles,

            "current":
                production.current_cycle,

            # IMPORTANT:
            # Actual machine cycle state comes from MachineEngine.
            "cycle_running":
                cycle["running"],

            "cycle_complete":
                cycle_complete
        },


        # ======================================================
        # CYCLE
        # ======================================================

        "cycle": {

            "number":
                cycle["cycle_number"],

            "running":
                cycle["running"],

            "start_time":
                cycle["start_time"],

            "end_time":
                cycle["end_time"],

            "current_duration":
                cycle["current_duration"],

            "last_duration":
                cycle["last_cycle_duration"]
        },


        # ======================================================
        # AUTO SEQUENCE
        # ======================================================

        "sequence": {

            "state":
                getattr(
                    auto,
                    "state",
                    "IDLE"
                ),

            "center_timer":
                getattr(
                    auto,
                    "center_timer",
                    0
                ),

            "center_travel":
                getattr(
                    auto,
                    "center_travel",
                    0
                )
        },


        # ======================================================
        # SEQUENCE BITS
        # ======================================================

        "sequence_bits": {

            "cycle_start":
                read_bit("L501"),

            "servo1_run":
                read_bit("L502"),

            "servo2_position2":
                read_bit("L504"),

            "servo3_position2":
                read_bit("L506"),

            "center_forward":
                read_bit("L508"),

            "center_forward_complete":
                read_bit("L509"),

            "center_reverse":
                read_bit("L510"),

            "center_reverse_complete":
                read_bit("L511"),

            "servo2_position1":
                read_bit("L516"),

            "servo3_position1":
                read_bit("L518"),

            "home":
                read_bit("L1020")
        },


        # ======================================================
        # SERVO STATUS
        # ======================================================

        "servo_status": {

            "ready":
                read_bit("L710"),

            "busy":
                read_bit("L712"),

            "error":
                read_bit("L714"),

            "position_reached":
                read_bit("L718"),

            "origin":
                read_bit("L720")
        },


        # ======================================================
        # PLC INPUTS
        # ======================================================

        "inputs": {

            "X0_qd77_ready":
                read_bit("X0"),

            "X1_sync":
                read_bit("X1"),

            "X4_axis1_mcode":
                read_bit("X4"),

            "X5_axis2_mcode":
                read_bit("X5"),

            "X6_axis3_mcode":
                read_bit("X6"),

            "X8_axis1_error":
                read_bit("X8"),

            "X9_axis2_error":
                read_bit("X9"),

            "X10_axis3_error":
                read_bit("X10"),

            "X20_cycle_start":
                read_bit("X20"),

            "X21_cycle_stop":
                read_bit("X21"),

            "X22_emergency":
                read_bit("X22"),

            "X23_reset":
                read_bit("X23"),

            "X24_auto_manual":
                read_bit("X24"),

            "X25_home":
                read_bit("X25"),

            "X33_center_forward":
                read_bit("X33"),

            "X34_center_reverse":
                read_bit("X34")
        },


        # ======================================================
        # PLC OUTPUTS
        # ======================================================

        "outputs": {

            "Y46_center_forward":
                read_bit("Y46"),

            "Y47_center_reverse":
                read_bit("Y47")
        },


        # ======================================================
        # IMPORTANT RELAYS
        # ======================================================

        "relays": {

            "M90_emergency":
                read_bit("M90"),

            "M91_air_fault":
                read_bit("M91"),

            "M500_auto":
                read_bit("M500"),

            "M100_manual":
                read_bit("M100")
        },


        # ======================================================
        # MODEL SELECTION
        # ======================================================

        "models": {

            "model1":
                read_bit("L800"),

            "model2":
                read_bit("L802"),

            "model3":
                read_bit("L804"),

            "model4":
                read_bit("L806"),

            "model5":
                read_bit("L808"),

            "model6":
                read_bit("L810"),

            "model7":
                read_bit("L812"),

            "model8":
                read_bit("L814"),

            "model9":
                read_bit("L816"),

            "model10":
                read_bit("L818"),

            "model11":
                read_bit("L820"),

            "model12":
                read_bit("L822")
        },


        # ======================================================
        # ENGINE STATUS
        # ======================================================

        "engine": {

            "scan_count":
                engine.scan_count,

            "history_size":
                len(
                    engine.telemetry_history
                ),

            "uptime":
                round(
                    datetime.now(
                        timezone.utc
                    ).timestamp()
                    - engine.start_time,
                    3
                )
        }
    }


# ==============================================================
# TELEMETRY HISTORY
# ==============================================================

def telemetry_history(limit=100):

    return engine.get_history(
        limit
    )


def telemetry_since(seconds=60):

    return engine.get_history_since(
        seconds
    )


def telemetry_latest():

    return engine.get_latest()


# ==============================================================
# CYCLE HISTORY
# ==============================================================

def cycle_info():

    return engine.get_cycle_info()


def sequence_history(limit=100):

    return engine.get_sequence_history(
        limit
    )