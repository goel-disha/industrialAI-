from backend.repositries.device_repositries import search_devices
from backend.repositries.engineering_repository import search_engineering
from backend.repositries.motion_repositry import (
    get_parameters,
    get_registers
)


##############################################################
# Global Search
##############################################################

def search(keyword):

    engineering = search_engineering(keyword)

    devices = search_devices(keyword)

    parameter_result = [
        p for p in get_parameters()
        if keyword.lower() in str(p["parameter"]).lower()
        or keyword.lower() in str(p["description"]).lower()
    ]

    register_result = [
        r for r in get_registers()
        if keyword.lower() in str(r["address"]).lower()
        or keyword.lower() in str(r["name"]).lower()
        or keyword.lower() in str(r["comment"]).lower()
    ]

    return {

        "devices": devices,

        "programs": engineering["programs"],

        "statements": engineering["statements"],

        "network": engineering["network"],

        "timers": engineering["timers"],

        "servo_constants": engineering["servo_constants"],

        "motion_parameters": parameter_result,

        "motion_registers": register_result

    }