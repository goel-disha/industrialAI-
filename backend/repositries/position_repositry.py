from backend.database import get_connection


def get_positions():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Positions")

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]



def search_position(keyword):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *

    FROM Positions

    WHERE

    axis LIKE ?

    OR position_no LIKE ?

    OR speed LIKE ?

    """,

    (

        f"%{keyword}%",

        f"%{keyword}%",

        f"%{keyword}%"

    ))

    rows = cursor.fetchall()

    conn.close()

    return [dict(r) for r in rows]