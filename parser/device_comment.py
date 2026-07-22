import re
import sqlite3
import pdfplumber


PDF_PATH = "docs/gxworks_exports/device_comment.pdf"
DB_PATH = "database/project.db"


def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag TEXT UNIQUE,
            comment TEXT
        )
    """)


def parse_pdf():

    rows = []

    device_pattern = re.compile(
        r'^([A-Z]+[0-9A-F]+)\s+(.+)$'
    )

    with pdfplumber.open(PDF_PATH) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            for line in text.split("\n"):

                line = line.strip()

                if (
                    not line
                    or line.startswith("Device Name")
                ):
                    continue

                match = device_pattern.match(line)

                if match:

                    tag = match.group(1).strip()
                    comment = match.group(2).strip()

                    rows.append((tag, comment))

    return rows


def save(rows):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    create_table(cursor)

    cursor.executemany("""
        INSERT OR REPLACE INTO device_comments(tag, comment)
        VALUES (?, ?)
    """, rows)

    conn.commit()

    conn.close()


if __name__ == "__main__":

    devices = parse_pdf()

    print(f"Found {len(devices)} comments")

    save(devices)

    print("Finished")