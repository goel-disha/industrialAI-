from backend.repositries.device_repositries import (
    get_all_devices,
)
from backend.repositries.motion_repositry import (
    get_runtime,
    get_parameters,
    get_registers
)
from backend.repositries.machine_repository import (
    get_machine_runtime,
    get_events
)
from backend.repositries.engineering_repository import (
    get_programs,
    get_timers
)
from backend.machine.plc_memory import (
    plc
)


##############################################################
# Dashboard
##############################################################

def get_dashboard():

    runtime = get_machine_runtime()

    axis_runtime = get_runtime()

    motion_parameters = get_parameters()

    motion_registers = get_registers()

    devices = get_all_devices()

    programs = get_programs()

    timers = get_timers()

    events = get_events(10)

    # Active model search in PLC memory
    model = 1
    model_bits = ["L800", "L802", "L804", "L806", "L808", "L810", "L812", "L814", "L816", "L818", "L820", "L822"]
    for i, bit in enumerate(model_bits):
        if int(plc.read(bit) or 0):
            model = i + 1
            break

    # Format events to what the frontend expects
    formatted_events = []
    for e in events:
        formatted_events.append({
            "time": e.get("timestamp", ""),
            "message": f"{e.get('event', '')} ({e.get('severity', '')})"
        })

    # Read current axis values
    axis1_pos = int(plc.read("D1100") or 0)
    axis2_pos = int(plc.read("D1110") or 0)
    axis3_pos = int(plc.read("D1120") or 0)

    # Core objects
    machine = {

        "machine": "AUTO TAPPING",

        "state": "RUNNING" if int(plc.read("L501") or 0) else "READY",

        "ready": int(plc.read("M500") or 1),

        "busy": int(plc.read("L501") or 0),

        "error": int(plc.read("M90") or 0),

        "servo_on": int(plc.read("M500") or 1)

    }


    production = {

        "boxes_today": int(plc.read("D2000") or 0),

        "good_boxes": int(plc.read("D2002") or 0),

        "rejected_boxes": int(plc.read("D2004") or 0),

        "cycle_time": float(plc.read("D2010") or 0),

        "efficiency": float(plc.read("D2020") or 0)

    }


    statistics = {

        "devices": len(devices),

        "programs": len(programs),

        "timers": len(timers),

        "axes": len(axis_runtime),

        "motion_parameters": len(motion_parameters),

        "motion_registers": len(motion_registers)

    }


    # Combined return payload
    return {

        # Nesting
        "machine_info": machine,

        "production": production,

        "statistics": statistics,

        "axis_runtime": axis_runtime,

        "recent_events": events,

        # Backwards compatible flat fields
        "machine": "AUTO TAPPING",

        "state": "RUNNING" if int(plc.read("L501") or 0) else "READY",

        "program": f"MODEL_{model}",

        "running": bool(int(plc.read("L501") or 0)),

        "plc": "Mitsubishi MELSEC-Q",

        "project": "AUTO_TAPPING",

        "status": "RUNNING" if int(plc.read("L501") or 0) else "READY",

        "boxes_today": int(plc.read("D2000") or 0),

        "cycle_time": float(plc.read("D2010") or 0),

        "efficiency": float(plc.read("D2020") or 0),

        "axis_position": f"A1: {axis1_pos} | A2: {axis2_pos} | A3: {axis3_pos}",

        "axis_speed": int(plc.read("D80") or 100),

        "events": formatted_events

    }