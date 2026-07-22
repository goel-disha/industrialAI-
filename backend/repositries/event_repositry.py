from backend.database import get_connection


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

    return [dict(r) for r in rows]