from backend.database import get_connection


def get_all_devices():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Devices
        ORDER BY tag
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(r) for r in rows]


def get_device(tag):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM Devices

    WHERE tag=?

    """,(tag,))

    row = cursor.fetchone()

    conn.close()

    if row:

        return dict(row)

    return None


def search_device(keyword):

    conn=get_connection()

    cursor=conn.cursor()

    cursor.execute("""

    SELECT *

    FROM Devices

    WHERE

    tag LIKE ?

    OR comment LIKE ?

    """,

    (

    f"%{keyword}%",

    f"%{keyword}%"

    ))

    rows=cursor.fetchall()

    conn.close()

    return [dict(r) for r in rows]