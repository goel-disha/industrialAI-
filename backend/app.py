# pyrefly: ignore [missing-import]

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import threading
import time

from backend.database import get_connection
from backend.machine.machine_engine import engine
from backend.srevices.ai_routes import router as ai_router
from backend.ai.ml_routes import router as ml_router
from backend.agent.routes import router as agent_router

# ==========================================================
# Services
# ==========================================================

from backend.srevices.device_service import device_service
from backend.srevices.chat_service import chat

from backend.srevices.event_services import (
    get_events,
    clear_events
)

from backend.srevices.motion_service import (
    motion,
    runtime,
    parameters,
    registers,
    register,
    axis_registers
)

from backend.srevices.engineering_services import (
    programs,
    statements,
    network,
    timers,
    servo_constants
)

from backend.srevices.dashboard_service import dashboard

from backend.srevices.machine_service import (
    machine,
    events
)

from backend.srevices.alarm_services import (
    get_alarms,
    get_active_alarms,
    alarm_summary,
    reset_alarms
)

from backend.srevices.search_service import search

from backend.srevices.explorer_service import explorer

from backend.srevices.relationship_service import relationships

from backend.srevices.diagnostic_services import diagnostics

from backend.srevices.live_monitor_services import (
    live_monitor,
    telemetry_history,
    telemetry_since,
    telemetry_latest,
    cycle_info,
    sequence_history
)

import backend.srevices.control_services as control_services


# ==========================================================
# Request Models
# ==========================================================

class ModelSelectPayload(BaseModel):
    model: int


class ModeSelectPayload(BaseModel):
    auto_mode: bool


class ChatPayload(BaseModel):
    message: str


# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(
    title="IndustrialAI API",
    version="1.0"
)


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)



# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():

    return {
        "project": "IndustrialAI",
        "version": "1.0",
        "status": "Running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "IndustrialAI API"
    }


# ==========================================================
# Dashboard
# ==========================================================

@app.get("/dashboard")
def get_dashboard():

    return dashboard()


# ==========================================================
# Machine
# ==========================================================

@app.get("/machine")
def get_machine():

    return machine()


app.include_router(ai_router)
app.include_router(ml_router)
app.include_router(agent_router)

# ==========================================================
# Events
# ==========================================================

@app.get("/events")
def get_event_history():

    return get_events()


@app.post("/events/clear")
def clear_event_history():

    return clear_events()


# ==========================================================
# Devices
# ==========================================================

@app.get("/devices")
def get_devices():

    """
    Return all devices from the servo_devices table.
    """

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            address,
            current_value
        FROM servo_devices
        ORDER BY address
    """)

    rows = cursor.fetchall()

    conn.close()

    result = []

    for row in rows:

        value = row["current_value"]

        try:
            active = int(value) != 0
        except (ValueError, TypeError):
            active = False

        result.append({
            "address": row["address"],
            "value": value,
            "active": active
        })

    return {
        "count": len(result),
        "devices": result
    }


# ==========================================================
# Single Device
# ==========================================================

@app.get("/devices/{address}")
def get_device(address: str):

    value = device_service.read(address)

    if value is None:

        return {
            "status": "error",
            "message": f"Device {address} not found"
        }

    return {
        "address": address,
        "value": value
    }


# ==========================================================
# Machine Memory Snapshot
# ==========================================================

@app.get("/machine/snapshot")
def get_machine_snapshot():

    model = 1

    try:

        model_value = device_service.read("D1800")

        if model_value is not None:

            model_value = int(model_value)

            if 1 <= model_value <= 12:
                model = model_value

    except (ValueError, TypeError):

        model = 1

    return device_service.snapshot(model)


# ==========================================================
# Servo Status
# ==========================================================

@app.get("/machine/servo")
def get_servo_status():

    return device_service.servo_status()


# ==========================================================
# Machine PLC Bits
# ==========================================================

@app.get("/machine/bits")
def get_machine_bits():

    return device_service.machine_bits()


# ==========================================================
# Model Positions
# ==========================================================

@app.get("/machine/model/{model}")
def get_model_positions(model: int):

    if model < 1 or model > 12:

        return {
            "status": "error",
            "message": "Model must be between 1 and 12"
        }

    return {
        "model": model,
        "positions": device_service.model_positions(model)
    }


# ==========================================================
# Motion
# ==========================================================

@app.get("/motion")
def get_motion():

    return motion()


@app.get("/motion/runtime")
def get_runtime():

    return runtime()


@app.get("/motion/parameters")
def get_parameters():

    return parameters()


@app.get("/motion/registers")
def get_registers():

    return registers()


@app.get("/motion/register/{address}")
def get_register(address: str):

    return register(address)


@app.get("/motion/axis/{axis}")
def get_axis(axis: int):

    return axis_registers(axis)


# ==========================================================
# PLC Diagnostics
# ==========================================================

@app.get("/diagnostics")
def get_diagnostics():

    return diagnostics()


# ==========================================================
# Alarms
# ==========================================================

@app.get("/alarms")
def alarms():

    return get_alarms()


@app.get("/alarms/active")
def active_alarms():

    return get_active_alarms()


@app.get("/alarms/summary")
def alarms_summary():

    return alarm_summary()


@app.post("/alarms/reset")
def alarms_reset():

    return reset_alarms()


# ==========================================================
# Engineering
# ==========================================================

@app.get("/programs")
def get_programs():

    return programs()


@app.get("/statements")
def get_statements():

    return statements()


@app.get("/network")
def get_network():

    return network()


@app.get("/timers")
def get_timers():

    return timers()


@app.get("/servo/constants")
def get_servo_constants():

    return servo_constants()


# ==========================================================
# Live Monitor
# ==========================================================

@app.get("/live")
def get_live():
    return live_monitor()

@app.get("/telemetry/latest")
def get_telemetry_latest():
    return {
        "status": "success",
        "data": telemetry_latest()
    }


@app.get("/telemetry/history")
def get_telemetry_history(limit: int = 100):
    data = telemetry_history(limit)

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


@app.get("/telemetry/since")
def get_telemetry_since(seconds: int = 60):
    data = telemetry_since(seconds)

    return {
        "status": "success",
        "count": len(data),
        "seconds": seconds,
        "data": data
    }


@app.get("/telemetry/cycle")
def get_telemetry_cycle():
    return {
        "status": "success",
        "data": cycle_info()
    }


@app.get("/telemetry/sequence")
def get_telemetry_sequence(limit: int = 100):
    data = sequence_history(limit)

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }

# ==========================================================
# Explorer
# ==========================================================

@app.get("/explorer")
def get_explorer():

    return explorer()


# ==========================================================
# Search
# ==========================================================

@app.get("/search")
def global_search(query: str):

    return search(query)


# ==========================================================
# Relationships
# ==========================================================

@app.get("/relationships/{address}")
def get_relationships(address: str):

    return relationships(address)


# ==========================================================
# Project Summary
# ==========================================================

@app.get("/project")
def project():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM servo_devices"
    )

    devices_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM Programs"
    )

    programs_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM Statements"
    )

    statements_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM Network"
    )

    networks_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM Timers"
    )

    timers_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM motion_parameters"
    )

    motion_parameters_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM motion_registers"
    )

    motion_registers_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM servo_constants"
    )

    servo_constants_count = cursor.fetchone()[0]

    conn.close()

    return {

        "project": "AUTO_TAPPING",

        "plc": "Mitsubishi MELSEC-Q",

        "servo_devices": devices_count,

        "programs": programs_count,

        "statements": statements_count,

        "network": networks_count,

        "timers": timers_count,

        "motion_parameters": motion_parameters_count,

        "motion_registers": motion_registers_count,

        "servo_constants": servo_constants_count,

        "version": "1.0"
    }


# ==========================================================
# Machine Control
# ==========================================================

@app.post("/control/start")
def control_start():

    control_services.start_machine()

    return {
        "status": "success",
        "message": "Cycle start command sent"
    }


@app.post("/control/stop")
def control_stop():

    control_services.stop_machine()

    return {
        "status": "success",
        "message": "Cycle stop command sent"
    }


@app.post("/control/emergency")
def control_emergency():

    control_services.emergency_stop()

    return {
        "status": "success",
        "message": "Emergency stop activated"
    }


@app.post("/control/reset")
def control_reset():

    control_services.reset_emergency()

    return {
        "status": "success",
        "message": "Emergency / alarms reset"
    }


# ==========================================================
# Model Selection
# ==========================================================

@app.post("/control/model")
def control_model(
    payload: ModelSelectPayload
):

    if payload.model < 1 or payload.model > 12:

        return {
            "status": "error",
            "message": (
                "Invalid model selection. "
                "Must be 1 to 12."
            )
        }

    control_services.select_model(
        payload.model
    )

    return {
        "status": "success",
        "message": (
            f"Model {payload.model} selected"
        )
    }


# ==========================================================
# Control Mode
# ==========================================================

@app.post("/control/mode")
def control_mode(
    payload: ModeSelectPayload
):

    control_services.set_control_mode(
        payload.auto_mode
    )

    state_str = (
        "Auto"
        if payload.auto_mode
        else "Manual"
    )

    return {
        "status": "success",
        "message": (
            f"Mode set to {state_str}"
        )
    }


# ==========================================================
# Mock Chat Endpoint
# ==========================================================

@app.post("/chat")
def chat_endpoint(payload: ChatPayload):
    return chat(payload.message)