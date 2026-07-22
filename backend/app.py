from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import get_connection
from backend.srevices.device_service import (
    devices,
    device,
)
from backend.srevices.motion_service import(motion)

from backend.srevices.network_service import(network)

from backend.srevices.position_service import(position)

from backend.srevices.program_service import(programs)

from backend.srevices.statement_service import(statement)

from backend.srevices.timer_service import(timer)

from backend.srevices.dashboard_service import dashboard
from backend.srevices.explorer_service import explorer
from backend.srevices.search_service import search
from backend.srevices.relationship_service import relationships

from backend.srevices.live_service import live
from backend.srevices.event_service import events
from backend.srevices.machine_service import status
import threading
import time

from backend.machine.machine_engine import engine

def machine_loop():

    while True:

        engine.update()

        time.sleep(0.1)      # 100 ms scan time

app = FastAPI(title="IndustrialAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

threading.Thread(
    target=machine_loop,
    daemon=True
).start()


@app.get("/")
def home():
    return {
        "Project": "IndustrialAI",
        "Version": "0.1",
        "Status": "Running"
    }


@app.get("/devices")
def get_all_devices():

    return devices()

@app.get("/devices/{tag}")
def get_device(tag: str):

    return device(tag)

@app.get("/motion")
def get_motion():

    return motion()

@app.get("/timers")
def get_timer():

    return timer()

@app.get("/positions")
def get_position():
    return position()

@app.get("/programs")
def get_program():
    return programs()


@app.get("/statements")
def get_statement():
    return statement()

@app.get("/network")
def get_network():
    return network()

@app.get("/search")
def global_search(query:str):

    return search(query)

@app.get("/dashboard")
def get_dashboard():

    return dashboard()

@app.get("/explorer")
def get_explorer():

    return explorer()

@app.get("/relationships/{tag}")
def find_device_relationships(tag: str):

    return relationships(tag)

@app.get("/live")
def get_live():

    return live()

@app.get("/events")
def get_events():

    return events()

@app.get("/machine")
def machine():

    return status()

@app.get("/project")
def project():

    try:
        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Devices")
        device_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Programs")
        programs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Motion")
        motion = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Positions")
        positions = cursor.fetchone()[0]

        conn.close()

        data = {
            "project": "AUTO_TAPPING",
            "devices": device_count,
            "programs": programs,
            "motion_parameters": motion,
            "positions": positions,
            "version": "0.1"
        }

        print("PROJECT:", data)

        return data

    except Exception as e:
        print("PROJECT ERROR:", e)
        raise