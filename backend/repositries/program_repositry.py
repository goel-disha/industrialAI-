from backend.database import get_connection

def get_programs():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Programs")

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]

def search_program(keyword):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *

    FROM Programs

    WHERE

    program LIKE ?

    """,

    (

        f"%{keyword}%",

    ))

    rows = cursor.fetchall()

    conn.close()

    return [dict(r) for r in rows]