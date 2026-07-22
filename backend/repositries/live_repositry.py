from backend.database import get_connection


def get_all_live():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM LiveValues")

    rows = cursor.fetchall()

    conn.close()

    return [dict(r) for r in rows]


def get_live(tag):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM LiveValues WHERE tag=?",
        (tag,)
    )

    row = cursor.fetchone()

    conn.close()

    return dict(row) if row else None


def update_live(tag, value, timestamp):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO LiveValues(tag,value,timestamp)

    VALUES(?,?,?)

    ON CONFLICT(tag)

    DO UPDATE SET

        value=excluded.value,

        timestamp=excluded.timestamp
    """,

    (

        tag,

        str(value),

        timestamp

    ))

    conn.commit()

    conn.close()