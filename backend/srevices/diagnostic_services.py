from backend.machine.plc_memory import plc

from backend.machine.machine_engine import engine
from backend.machine.servo_engine import axis1, axis2, axis3


# ==========================================================
# PLC Diagnostics
# ==========================================================

def diagnostics():

    # ------------------------------------------------------
    # Machine State
    # ------------------------------------------------------

    machine_state = getattr(engine, "state", "UNKNOWN")

    # ------------------------------------------------------
    # Auto Mode
    # ------------------------------------------------------

    auto_mode = int(plc.read("M500") or 0)

    # ------------------------------------------------------
    # Safety
    # ------------------------------------------------------

    emergency = int(plc.read("M90") or 0)

    air_fault = int(plc.read("M91") or 0)

    # ------------------------------------------------------
    # Cycle
    # ------------------------------------------------------

    cycle_running = int(plc.read("L501") or 0)

    cycle_complete = int(plc.read("L502") or 0)

    # ------------------------------------------------------
    # Model
    # ------------------------------------------------------

    model = getattr(
        engine,
        "current_model",
        int(plc.read("D1800") or 1)
    )

    # ------------------------------------------------------
    # Servo Status
    # ------------------------------------------------------

    servo = {

        "axis1": {
            "position": axis1.position,
            "target": axis1.target,
            "busy": axis1.busy,
            "complete": axis1.complete
        },

        "axis2": {
            "position": axis2.position,
            "target": axis2.target,
            "busy": axis2.busy,
            "complete": axis2.complete
        },

        "axis3": {
            "position": axis3.position,
            "target": axis3.target,
            "busy": axis3.busy,
            "complete": axis3.complete
        }

    }

    # ------------------------------------------------------
    # PLC Position Registers
    # ------------------------------------------------------

    positions = {

        "axis1": int(plc.read("D1100") or 0),

        "axis2": int(plc.read("D1110") or 0),

        "axis3": int(plc.read("D1120") or 0)

    }

    # ------------------------------------------------------
    # Digital Inputs
    # ------------------------------------------------------

    inputs = {

        "X20_cycle_start": int(plc.read("X20") or 0),

        "X21_cycle_stop": int(plc.read("X21") or 0),

        "X23_reset": int(plc.read("X23") or 0),

        "X30_part_entry": int(plc.read("X30") or 0),

        "X33_center_forward": int(plc.read("X33") or 0),

        "X34_center_reverse": int(plc.read("X34") or 0)

    }

    # ------------------------------------------------------
    # Digital Outputs
    # ------------------------------------------------------

    outputs = {

        "Y46_center_forward": int(plc.read("Y46") or 0),

        "Y47_center_reverse": int(plc.read("Y47") or 0)

    }

    # ------------------------------------------------------
    # Servo Completion Bits
    # ------------------------------------------------------

    completion = {

        "axis1": int(plc.read("L610") or 0),

        "axis2": int(plc.read("L611") or 0),

        "axis3": int(plc.read("L612") or 0)

    }

    # ------------------------------------------------------
    # Overall Status
    # ------------------------------------------------------

    if emergency:

        status = "EMERGENCY"

    elif air_fault:

        status = "AIR_FAULT"

    elif cycle_running:

        status = "RUNNING"

    elif cycle_complete:

        status = "COMPLETE"

    else:

        status = "IDLE"

    # ------------------------------------------------------
    # Return Diagnostics
    # ------------------------------------------------------

    return {

        "machine": {

            "state": machine_state,

            "status": status,

            "model": model,

            "auto_mode": bool(auto_mode),

            "cycle_running": bool(cycle_running),

            "cycle_complete": bool(cycle_complete)

        },

        "safety": {

            "emergency": bool(emergency),

            "air_fault": bool(air_fault)

        },

        "servo": servo,

        "positions": positions,

        "completion": completion,

        "inputs": inputs,

        "outputs": outputs

    }