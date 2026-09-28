from backend.repositries.device_repositries import get_all_devices
from backend.repositries.engineering_repository import (
    get_programs,
    get_statements,
    get_network,
    get_timers,
    get_servo_constants
)
from backend.repositries.motion_repositry import (
    get_parameters,
    get_registers
)


##############################################################
# Engineering Explorer
##############################################################

def explorer():

    return {

        "devices": get_all_devices(),

        "programs": get_programs(),

        "statements": get_statements(),

        "network": get_network(),

        "timers": get_timers(),

        "motion_parameters": get_parameters(),

        "motion_registers": get_registers(),

        "servo_constants": get_servo_constants()

    }