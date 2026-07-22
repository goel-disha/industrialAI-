from backend.database import get_connection

def get_statements():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Statements")

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]



def search_statement(keyword):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *

    FROM Statements

    WHERE

    CAST(step AS TEXT) LIKE ?

    OR statement LIKE ?

    """,

    (

        f"%{keyword}%",

        f"%{keyword}%"

    ))

    rows = cursor.fetchall()

    conn.close()

    return [dict(r) for r in rows]