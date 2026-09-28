from backend.database import get_connection


##############################################################
# Axis Runtime
##############################################################

def get_runtime():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            axis,
            target_position,
            command_speed,
            acceleration,
            deceleration,
            servo_on,
            in_position,
            alarm
        FROM axis_runtime
        ORDER BY axis
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


##############################################################
# Motion Parameters
##############################################################

def get_parameters():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            parameter,
            axis1_value,
            axis2_value,
            axis3_value,
            unit,
            description
        FROM motion_parameters
        ORDER BY parameter
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


##############################################################
# Motion Registers
##############################################################

def get_registers():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            address,
            axis,
            name,
            comment,
            datatype,
            value,
            access,
            category,
            unit
        FROM motion_registers
        ORDER BY axis, address
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


##############################################################
# Single Motion Register
##############################################################

def get_register(address):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            address,
            axis,
            name,
            comment,
            datatype,
            value,
            access,
            category,
            unit
        FROM motion_registers
        WHERE address = ?
    """, (address,))

    row = cursor.fetchone()

    conn.close()

    return dict(row) if row else None


##############################################################
# Registers of One Axis
##############################################################

def get_axis_registers(axis):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            address,
            axis,
            name,
            comment,
            datatype,
            value,
            access,
            category,
            unit
        FROM motion_registers
        WHERE axis = ?
        ORDER BY address
    """, (axis,))

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]