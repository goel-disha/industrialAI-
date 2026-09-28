import sqlite3

conn = sqlite3.connect("database/project.db")
cursor = conn.cursor()

############################################################
# Engineering Tables
############################################################

cursor.execute("""
CREATE TABLE IF NOT EXISTS Devices(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT UNIQUE,
    type TEXT,
    address INTEGER,
    comment TEXT,
    current_value TEXT DEFAULT '0'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS device_comments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT UNIQUE,
    comment TEXT
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
CREATE TABLE IF NOT EXISTS Timers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timer TEXT,
    preset TEXT
)
""")

############################################################
# Motion Engineering
############################################################

cursor.execute("""
CREATE TABLE IF NOT EXISTS motion_parameters(
    parameter TEXT PRIMARY KEY,
    axis1_value TEXT,
    axis2_value TEXT,
    axis3_value TEXT,
    unit TEXT,
    description TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS motion_registers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT UNIQUE,
    axis INTEGER,
    name TEXT,
    comment TEXT,
    datatype TEXT,
    value TEXT,
    access TEXT,
    category TEXT,
    unit TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS servo_constants(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    constant_value TEXT,
    register_used TEXT,
    operation TEXT
)
""")

############################################################
# Runtime Tables
############################################################

cursor.execute("""
CREATE TABLE IF NOT EXISTS axis_runtime(
    axis INTEGER PRIMARY KEY,
    target_position REAL,
    command_speed REAL,
    acceleration REAL,
    deceleration REAL,
    servo_on INTEGER,
    in_position INTEGER,
    alarm INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS live_values(
    tag TEXT PRIMARY KEY,
    value TEXT,
    datatype TEXT,
    category TEXT,
    description TEXT,
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
    id INTEGER PRIMARY KEY CHECK(id=1),

    state TEXT,
    current_program TEXT,
    current_step INTEGER,

    boxes_today INTEGER,
    cycle_time REAL,

    axis1_position REAL,
    axis2_position REAL,
    axis3_position REAL,

    updated_at TEXT
)
""")

##############################################################
# PLC Register Master
##############################################################

cursor.execute("""
CREATE TABLE IF NOT EXISTS servo_devices (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    address TEXT UNIQUE NOT NULL,

    device_type TEXT NOT NULL,

    axis INTEGER,

    symbol TEXT,

    description TEXT,

    datatype TEXT,

    current_value TEXT DEFAULT '0',

    simulated INTEGER DEFAULT 1

)
""")

##########################################################
# Servo Sequence
##############################################################

cursor.execute("""
CREATE TABLE IF NOT EXISTS servo_sequence(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    step_no INTEGER,

    step_name TEXT,

    plc_bit TEXT,

    condition TEXT,

    action TEXT,

    next_step INTEGER,

    servo_axis INTEGER,

    comment TEXT

)
""")

##############################################################
# Servo Commands
##############################################################

cursor.execute("""
CREATE TABLE IF NOT EXISTS servo_commands(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    axis INTEGER,

    command_name TEXT,

    register_address TEXT,

    value TEXT,

    description TEXT

)
""")

############################################################
# Remove Old Tables
############################################################

cursor.execute("DROP TABLE IF EXISTS Motion")
cursor.execute("DROP TABLE IF EXISTS Positions")

############################################################

conn.commit()
conn.close()

print("Database Created Successfully")