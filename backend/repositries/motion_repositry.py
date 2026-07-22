from backend.database import get_connection


def get_motion():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Motion")

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]

def search_motion(keyword):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *

    FROM Motion

    WHERE

    axis LIKE ?

    OR parameter LIKE ?

    OR value LIKE ?

    """,

    (

        f"%{keyword}%",

        f"%{keyword}%",

        f"%{keyword}%"

    ))

    rows = cursor.fetchall()

    conn.close()

    return [dict(r) for r in rows]