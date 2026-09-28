from backend.machine.plc_memory import plc
from backend.machine.machine_engine import engine
from backend.machine.auto_engine import auto
from backend.machine.servo_engine import axis1, axis2, axis3
from backend.machine.production_engine import production


def dashboard():

    return {
        # ======================================================
        # Machine
        # ======================================================

        "machine": {
            "state": engine.state,
            "model": engine.current_model,
            "scan_count": engine.scan_count,

            "auto_mode": bool(
                int(plc.read("M500") or 0)
            ),

            "cycle_running": production.cycle_running,
            "cycle_complete": production.cycle_complete,
        },

        # ======================================================
        # Safety
        # ======================================================

        "safety": {
            "emergency": bool(
                int(plc.read("M90") or 0)
            ),

            "air_fault": bool(
                int(plc.read("M91") or 0)
            ),

            "safe": (
                not int(plc.read("M90") or 0)
                and not int(plc.read("M91") or 0)
            ),
        },

        # ======================================================
        # Servo
        # ======================================================

        "servo": {

            "axis1": {
                "position": axis1.position,
                "target": axis1.target,
                "busy": axis1.busy,
                "complete": axis1.complete,
            },

            "axis2": {
                "position": axis2.position,
                "target": axis2.target,
                "busy": axis2.busy,
                "complete": axis2.complete,
            },

            "axis3": {
                "position": axis3.position,
                "target": axis3.target,
                "busy": axis3.busy,
                "complete": axis3.complete,
            },
        },

        # ======================================================
        # Centering
        # ======================================================

        "centering": {
            "forward": bool(
                int(plc.read("Y46") or 0)
            ),

            "reverse": bool(
                int(plc.read("Y47") or 0)
            ),

            "forward_limit": bool(
                int(plc.read("X33") or 0)
            ),

            "reverse_limit": bool(
                int(plc.read("X34") or 0)
            ),

            "part_centered": bool(
                int(plc.read("L509") or 0)
            ),
        },

        # ======================================================
        # Production
        # ======================================================

        "production": production.get_status(),

        # ======================================================
        # Position Registers
        # ======================================================

        "positions": {
            "axis1": plc.read("D1100"),
            "axis2": plc.read("D1110"),
            "axis3": plc.read("D1120"),
        },

        # ======================================================
        # Completion
        # ======================================================

        "completion": {
            "axis1": bool(
                int(plc.read("L610") or 0)
            ),

            "axis2": bool(
                int(plc.read("L611") or 0)
            ),

            "axis3": bool(
                int(plc.read("L612") or 0)
            ),
        },

        # ======================================================
        # Auto Sequence
        # ======================================================

        "sequence": {
            "state": auto.state,
            "model": auto.model,
            "center_timer": auto.center_timer,
            "center_travel": auto.center_travel,
        },

        # ======================================================
        # Important PLC Inputs
        # ======================================================

        "inputs": {
            "cycle_start": plc.read("X20"),
            "cycle_stop": plc.read("X21"),
            "reset": plc.read("X23"),

            "part_entry": plc.read("X30"),

            "center_forward": plc.read("X33"),
            "center_reverse": plc.read("X34"),
        },

        # ======================================================
        # Outputs
        # ======================================================

        "outputs": {
            "center_forward": plc.read("Y46"),
            "center_reverse": plc.read("Y47"),
        },
    }