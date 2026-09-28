from backend.machine.plc_memory import plc
from backend.database import get_connection


##############################################################
# Machine Status
##############################################################

def get_machine_status():

    return {

        "machine": "AUTO TAPPING",

        "state": "RUNNING" if int(plc.read("L501") or 0) else "READY",

        "ready": bool(int(plc.read("M500") or 1)),

        "busy": bool(int(plc.read("L501") or 0)),

        "error": bool(int(plc.read("M90") or 0)),

        "servo_on": bool(int(plc.read("M500") or 1))

    }


##############################################################
# Production Status
##############################################################

def get_production_status():

    return {

        "boxes_today": int(plc.read("D2000") or 0),

        "good_boxes": int(plc.read("D2002") or 0),

        "rejected_boxes": int(plc.read("D2004") or 0),

        "cycle_time": float(plc.read("D2010") or 0),

        "efficiency": float(plc.read("D2020") or 0)

    }


##############################################################
# Servo Status
##############################################################

def get_servo_status():

    return {

        "axis1_target": int(plc.read("D300") or 0),

        "axis2_target": int(plc.read("D500") or 0),

        "axis3_target": int(plc.read("D700") or 0),

        "axis1_position": int(plc.read("D1100") or 0),

        "axis2_position": int(plc.read("D1110") or 0),

        "axis3_position": int(plc.read("D1120") or 0),

        "axis1_complete": bool(int(plc.read("L610") or 0)),

        "axis2_complete": bool(int(plc.read("L611") or 0)),

        "axis3_complete": bool(int(plc.read("L612") or 0))

    }


##############################################################
# Complete Runtime
##############################################################

def get_machine_runtime():

    return {

        **get_machine_status(),

        **get_production_status(),

        **get_servo_status()

    }


##############################################################
# Get Machine Events
##############################################################

def get_events(limit=30):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM MachineEvents

        ORDER BY id DESC

        LIMIT ?

    """,(limit,))

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


##############################################################
# Add Machine Event
##############################################################

def add_event(timestamp, state, event, severity):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO MachineEvents

        (

            timestamp,

            state,

            event,

            severity

        )

        VALUES

        (

            ?, ?, ?, ?

        )

    """,

    (

        timestamp,

        state,

        event,

        severity

    ))

    conn.commit()

    conn.close()