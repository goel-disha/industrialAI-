from backend.database import get_connection

def get_timers():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Timers")

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def search_timer(keyword):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *

    FROM Timers

    WHERE

    timer LIKE ?

    OR preset LIKE ?

    """,

    (

        f"%{keyword}%",

        f"%{keyword}%"

    ))

    rows = cursor.fetchall()

    conn.close()

    return [dict(r) for r in rows]