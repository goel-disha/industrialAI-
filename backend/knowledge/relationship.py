from backend.repositries.device_repositries import get_device
from backend.repositries.program_repositry import get_programs
from backend.repositries.motion_repositry import get_motion
from backend.repositries.position_repositry import get_positions
from backend.repositries.timer_repositry import get_timers
from backend.repositries.statement_repositry import get_statements


def find_device_relationships(tag: str):

    device = get_device(tag)

    if device is None:
        return {
            "error": "Device not found"
        }

    relationships = {

        "device": device,

        "programs": [],

        "motion": [],

        "positions": [],

        "timers": [],

        "statements": []

    }

    for program in get_programs():

        relationships["programs"].append(program)

    
    for motion in get_motion():

        relationships["motion"].append(motion)

    
    for position in get_positions():

        relationships["positions"].append(position)

    
    for timer in get_timers():

        relationships["timers"].append(timer)

    
    for statement in get_statements():

        relationships["statements"].append(statement)

    return relationships