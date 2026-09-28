from backend.database import get_connection


##############################################################
# Programs
##############################################################

def get_programs():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            program
        FROM Programs
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


##############################################################
# Statements
##############################################################

def get_statements():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            step,
            statement
        FROM Statements
        ORDER BY step
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


##############################################################
# Network
##############################################################

def get_network():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            line
        FROM Network
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


##############################################################
# Timers
##############################################################

def get_timers():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            timer,
            preset
        FROM Timers
        ORDER BY timer
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


##############################################################
# Servo Constants
##############################################################

def get_servo_constants():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            constant_value,
            register_used,
            operation
        FROM servo_constants
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


##############################################################
# Global Engineering Search
##############################################################

def search_engineering(keyword):

    conn = get_connection()
    cursor = conn.cursor()

    result = {}

    # Programs
    cursor.execute("""
        SELECT id, program
        FROM Programs
        WHERE program LIKE ?
    """, (f"%{keyword}%",))
    result["programs"] = [dict(r) for r in cursor.fetchall()]

    # Statements
    cursor.execute("""
        SELECT id, step, statement
        FROM Statements
        WHERE CAST(step AS TEXT) LIKE ?
           OR statement LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))
    result["statements"] = [dict(r) for r in cursor.fetchall()]

    # Network
    cursor.execute("""
        SELECT id, line
        FROM Network
        WHERE line LIKE ?
    """, (f"%{keyword}%",))
    result["network"] = [dict(r) for r in cursor.fetchall()]

    # Timers
    cursor.execute("""
        SELECT id, timer, preset
        FROM Timers
        WHERE timer LIKE ?
           OR preset LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))
    result["timers"] = [dict(r) for r in cursor.fetchall()]

    # Servo Constants
    cursor.execute("""
        SELECT
            id,
            constant_value,
            register_used,
            operation
        FROM servo_constants
        WHERE constant_value LIKE ?
           OR register_used LIKE ?
           OR operation LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    result["servo_constants"] = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return result