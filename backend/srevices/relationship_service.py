from backend.repositries.device_repositries import get_device
from backend.repositries.engineering_repository import (
    get_programs,
    get_statements,
    get_network,
    get_timers,
    get_servo_constants
)
from backend.repositries.motion_repositry import (
    get_registers
)


##############################################################
# Device Relationships
##############################################################

def relationships(tag):

    keyword = tag.upper()

    device = get_device(keyword)

    statements = [
        s for s in get_statements()
        if keyword in s["statement"].upper()
    ]

    network = [
        n for n in get_network()
        if keyword in n["line"].upper()
    ]

    timers = [
        t for t in get_timers()
        if keyword in str(t["timer"]).upper()
    ]

    motion = [
        r for r in get_registers()
        if keyword in r["comment"].upper()
        or keyword in r["address"].upper()
    ]

    programs = get_programs()

    constants = [
        c for c in get_servo_constants()
        if keyword in c["register_used"].upper()
    ]

    return {

        "device": device,

        "programs": programs,

        "statements": statements,

        "network": network,

        "timers": timers,

        "motion_registers": motion,

        "servo_constants": constants

    }