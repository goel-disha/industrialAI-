import sqlite3
from datetime import datetime


DATABASE = "database/project.db"


class EventEngine:

    def __init__(self):

        self.previous_state = None

    def log(self, state):

        if state == self.previous_state:
            return

        self.previous_state = state

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS MachineEvents(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT,

            state TEXT,

            event TEXT,

            severity TEXT

        )

        """)

        event = self.get_event(state)

        severity = self.get_severity(state)

        cursor.execute("""

        INSERT INTO MachineEvents(

            timestamp,

            state,

            event,

            severity

        )

        VALUES(?,?,?,?)

        """,

        (

            datetime.now().strftime("%H:%M:%S"),

            state,

            event,

            severity

        ))

        conn.commit()

        conn.close()

    def get_event(self, state):

        events = {

            "WAITING":"Waiting for Box",

            "BOX_DETECTED":"Box Detected",

            "CONVEYOR_STOPPED":"Conveyor Stopped",

            "SERVO_DOWN":"Servo Moving Down",

            "TAPPING":"Auto Tapping Started",

            "SERVO_UP":"Servo Moving Up",

            "CONVEYOR_START":"Conveyor Started",

            "BOX_EXIT":"Finished Box Left"

        }

        return events.get(state,state)

    def get_severity(self,state):

        return "INFO"


event_engine = EventEngine()