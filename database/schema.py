import sqlite3

conn = sqlite3.connect("database/project.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Devices(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT,
    type TEXT,
    address INTEGER,
    comment TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Motion(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    axis TEXT,
    parameter TEXT,
    value TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Positions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    axis INTEGER,
    position_no INTEGER,
    position REAL,
    speed REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Timers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timer TEXT,
    preset TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Programs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Statements(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step INTEGER,
    statement TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Network(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS LiveValues(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tag TEXT UNIQUE,

    value TEXT,

    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS MachineEvents(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    timestamp TEXT,

    state TEXT,

    event TEXT,

    severity TEXT

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS MachineState(

    id INTEGER PRIMARY KEY,

    state TEXT,

    program TEXT,

    boxes_today INTEGER,

    cycle_time REAL,

    axis_position INTEGER,

    axis_speed INTEGER,

    updated_at TEXT

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS device_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT UNIQUE,
    comment TEXT)               
""");



conn.commit()
conn.close()

print("Database Created Successfully")