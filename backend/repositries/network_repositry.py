from backend.database import get_connection

def get_network():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Network")

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]



def search_network(keyword):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *

    FROM Network

    WHERE

    line LIKE ?

    """,

    (

        f"%{keyword}%",


    ))

    rows = cursor.fetchall()

    conn.close()

    return [dict(r) for r in rows]