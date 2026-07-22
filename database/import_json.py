import sqlite3
import json
from pathlib import Path

DATABASE = "database/project.db"
JSON_FOLDER = Path("database")

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()


#######################################################
# Devices
#######################################################

def import_devices():

    file = JSON_FOLDER / "device_tags.json"

    if not file.exists():
        return

    with open(file, "r", encoding="utf-8") as f:
        devices = json.load(f)

    for d in devices:

        cursor.execute("""
        INSERT INTO Devices(tag,type,address,comment)
        VALUES(?,?,?,?)
        """,
        (
            d.get("tag",""),
            d.get("type",""),
            d.get("address",0),
            d.get("comment","")
        ))

    print(f"Imported {len(devices)} devices")


#######################################################
# Motion
#######################################################

def import_motion():

    file = JSON_FOLDER / "motion.json"

    if not file.exists():
        print("motion.json not found")
        return

    with open(file, "r", encoding="utf-8") as f:
        motions = json.load(f)

    count = 0

    for axis, parameters in motions.items():

        for parameter, value in parameters.items():

            cursor.execute("""
            INSERT INTO Motion(axis, parameter, value)
            VALUES (?, ?, ?)
            """,
            (
                axis,
                parameter,
                value
            ))

            count += 1

    print(f"Imported {count} motion parameters")


#######################################################
# Position Table
#######################################################

def import_positions():

    file = JSON_FOLDER / "positions.json"

    if not file.exists():
        return

    with open(file,"r",encoding="utf-8") as f:
        positions = json.load(f)

    for p in positions:

        cursor.execute("""
        INSERT INTO Positions
        (axis,position_no,position,speed)

        VALUES(?,?,?,?)
        """,

        (
            p.get("axis",0),
            p.get("position_no",0),
            p.get("position",""),
            p.get("speed",""),
        ))

    print(f"Imported {len(positions)} positions")


#######################################################
# Timers
#######################################################

def import_timers():

    file = JSON_FOLDER / "timers.json"

    if not file.exists():
        return

    with open(file,"r",encoding="utf-8") as f:
        timers = json.load(f)

    for t in timers:

        cursor.execute("""
        INSERT INTO Timers(timer,preset)

        VALUES(?,?)
        """,

        (
            t.get("timer",""),
            t.get("preset","")
        ))

    print(f"Imported {len(timers)} timers")


#######################################################
# Statements
#######################################################

def import_statements():

    file = JSON_FOLDER / "statements.json"

    if not file.exists():
        return

    with open(file,"r",encoding="utf-8") as f:
        statements = json.load(f)

    for s in statements:

        cursor.execute("""
        INSERT INTO Statements(step,statement)

        VALUES(?,?)
        """,

        (
            s.get("step",0),
            s.get("statement","")
        ))

    print(f"Imported {len(statements)} statements")


#######################################################
# Programs
#######################################################

def import_programs():

    file = JSON_FOLDER / "programs.json"

    if not file.exists():
        print("programs.json not found")
        return

    with open(file, "r", encoding="utf-8") as f:
        programs = json.load(f)

    count = 0

    for program in programs:

        cursor.execute("""
        INSERT INTO Programs(program)
        VALUES(?)
        """, (program,))

        count += 1

    print(f"Imported {count} programs")


#######################################################
# Network
#######################################################

def import_network():

    file = JSON_FOLDER / "network.json"

    if not file.exists():
        return

    with open(file,"r",encoding="utf-8") as f:
        network = json.load(f)

    count =0

    for n in network:

        cursor.execute("""
        INSERT INTO Network(line)

        VALUES(?)
        """,(n,))

        count += 1

    print(f"Imported {len(network)} network lines")


#######################################################
# Main
#######################################################

def main():

    print("Importing JSON files...\n")

    import_devices()
    import_motion()
    import_positions()
    import_timers()
    import_programs()
    import_statements()
    import_network()

    conn.commit()

    conn.close()

    print("\nFinished importing all data!")


if __name__ == "__main__":
    main()