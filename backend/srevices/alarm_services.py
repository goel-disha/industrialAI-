from backend.machine.plc_memory import plc


# ==========================================================
# Alarm Definitions
# ==========================================================

ALARM_DEFINITIONS = {

    "M90": {
        "code": "E001",
        "name": "Emergency Stop",
        "severity": "CRITICAL",
        "message": "Emergency stop is active"
    },

    "M91": {
        "code": "E002",
        "name": "Air Pressure Fault",
        "severity": "HIGH",
        "message": "Air pressure fault is active"
    }

}


# ==========================================================
# Read Active Alarms
# ==========================================================

def get_alarms():

    alarms = []

    for address, definition in ALARM_DEFINITIONS.items():

        active = int(plc.read(address) or 0)

        alarms.append({

            "address": address,

            "code": definition["code"],

            "name": definition["name"],

            "severity": definition["severity"],

            "message": definition["message"],

            "active": bool(active)

        })

    return alarms


# ==========================================================
# Active Alarms Only
# ==========================================================

def get_active_alarms():

    alarms = get_alarms()

    return [

        alarm

        for alarm in alarms

        if alarm["active"]

    ]


# ==========================================================
# Alarm Summary
# ==========================================================

def alarm_summary():

    alarms = get_alarms()

    active = [

        alarm

        for alarm in alarms

        if alarm["active"]

    ]

    critical = [

        alarm

        for alarm in active

        if alarm["severity"] == "CRITICAL"

    ]

    high = [

        alarm

        for alarm in active

        if alarm["severity"] == "HIGH"

    ]

    return {

        "total": len(alarms),

        "active": len(active),

        "critical": len(critical),

        "high": len(high),

        "alarms": active

    }


# ==========================================================
# Reset Alarms
# ==========================================================

def reset_alarms():

    plc.write("M90", 0)

    plc.write("M91", 0)

    return {

        "status": "success",

        "message": "Emergency and alarm conditions reset"

    }