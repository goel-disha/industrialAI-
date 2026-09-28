from backend.database import get_connection
from backend.machine.plc_memory import plc


###########################################################
# All Servo Devices
###########################################################

def get_all_devices():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM servo_devices
        ORDER BY device_type, address
    """)

    rows = cursor.fetchall()

    conn.close()

    devices = []

    for row in rows:

        device = dict(row)

        # Replace database value with live PLC value
        live_value = plc.read(device["address"])

        if live_value is not None:
            device["current_value"] = live_value

        devices.append(device)

    return devices


###########################################################
# Single Device
###########################################################

def get_device(address: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM servo_devices
        WHERE address = ?
    """, (address,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    device = dict(row)

    live_value = plc.read(device["address"])

    if live_value is not None:
        device["current_value"] = live_value

    return device


###########################################################
# Search Devices
###########################################################

def search_devices(keyword: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM servo_devices
        WHERE
            address LIKE ?
            OR symbol LIKE ?
            OR description LIKE ?
            OR device_type LIKE ?
        ORDER BY address
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    rows = cursor.fetchall()

    conn.close()

    devices = []

    for row in rows:

        device = dict(row)

        live_value = plc.read(device["address"])

        if live_value is not None:
            device["current_value"] = live_value

        devices.append(device)

    return devices