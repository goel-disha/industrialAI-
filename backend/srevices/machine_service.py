from backend.machine.plc_memory import plc
from backend.machine.machine_engine import engine
from backend.machine.auto_engine import auto
from backend.machine.production_engine import production


# ==========================================================
# Machine Status
# ==========================================================

def machine():

    emergency = bool(
        int(plc.read("M90") or 0)
    )

    air_fault = bool(
        int(plc.read("M91") or 0)
    )

    auto_mode = bool(
        int(plc.read("M500") or 0)
    )

    return {

        "state": engine.state,

        "model": engine.current_model,

        "auto_mode": auto_mode,

        "cycle_running":
            production.cycle_running,

        "cycle_complete":
            production.cycle_complete,

        "safety": {

            "emergency": emergency,

            "air_fault": air_fault,

            "safe":
                not emergency
                and not air_fault

        },

        "sequence": {

            "state": auto.state,

            "center_timer":
                auto.center_timer,

            "center_travel":
                auto.center_travel

        }

    }


# ==========================================================
# Machine Events
# ==========================================================

def events():

    return {

        "cycle": {

            "total":
                production.total_cycles,

            "completed":
                production.completed_cycles,

            "rejected":
                production.rejected_cycles,

            "current":
                production.current_cycle

        },

        "machine": {

            "state":
                engine.state,

            "model":
                engine.current_model

        },

        "servo": {

            "axis1_complete":
                bool(int(plc.read("L610") or 0)),

            "axis2_complete":
                bool(int(plc.read("L611") or 0)),

            "axis3_complete":
                bool(int(plc.read("L612") or 0))

        }

    }