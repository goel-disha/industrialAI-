from backend.repositries.device_repositries import get_all_devices
from backend.repositries.motion_repositry import get_motion
from backend.repositries.position_repositry import get_positions
from backend.repositries.program_repositry import get_programs
from backend.repositries.timer_repositry import get_timers
from backend.repositries.network_repositry import get_network
from backend.machine.machine_engine import engine
from backend.repositries.event_repositry import get_events
from backend.repositries.live_repositry import get_all_live


def dashboard():

    devices = get_all_devices()
    motion = get_motion()
    positions = get_positions()
    programs = get_programs()
    timers = get_timers()
    network = get_network()
    latest_events = get_events(5)
    live_values = get_all_live()

    # Read machine data only once
    machine_data = engine.dashboard()

    return {

        "project": "AUTO_TAPPING",

        "plc": "Mitsubishi",

        "devices": len(devices),

        "programs": len(programs),

        "motion_parameters": len(motion),

        "positions": len(positions),

        "timers": len(timers),

        "network": len(network),

        "status": "Healthy",

        "machine": machine_data["machine"],

        "state": machine_data["state"],

        "boxes_today": machine_data["boxes_today"],

        "good_boxes": machine_data["good_boxes"],

        "rejected_boxes": machine_data["rejected_boxes"],

        "current_cycle": machine_data["current_cycle"],

        "cycle_time": machine_data["cycle_time"],

        "efficiency": machine_data["efficiency"],

        "axis_position": machine_data["axis_position"],

        "axis_speed": machine_data["axis_speed"],

        "ready": machine_data["ready"],

        "busy": machine_data["busy"],

        "error": machine_data["error"],

        "servo_on": machine_data["servo_on"],

        "updated_at": machine_data["updated_at"],

        "events": latest_events,

        "live": live_values,

        "running" : "yes"

    }