from backend.machine.plc_memory import plc


def start_machine():
    # Safety checks
    if int(plc.read("M90") or 0):
        return {
            "status": "error",
            "message": "Emergency stop is active"
        }

    if int(plc.read("M91") or 0):
        return {
            "status": "error",
            "message": "Air fault is active"
        }

    # Put machine into AUTO mode
    plc.write("M500", 1)

    # Machine ready / safety conditions
    plc.write("X21", 1)
    plc.write("L540", 0)
    plc.write("L541", 0)

    # Simulate physical CYCLE START pushbutton
    plc.write("X20", 1)

    # Internal auto-cycle start command
    plc.write("L501", 1)

    return {
        "status": "success",
        "message": "Automatic machine cycle started",
        "mode": "AUTO",
        "cycle_start": True,
        "M500": plc.read("M500"),
        "X20": plc.read("X20"),
        "L501": plc.read("L501")
    }


# ==========================================================
# STOP MACHINE
# ==========================================================

def stop_machine():

    # Remove cycle start
    plc.write("L501", 0)

    # Remove physical start command
    plc.write("X20", 0)

    # Internal stop request
    plc.write("L540", 1)

    return {
        "status": "success",
        "message": "Machine stopped"
    }


# ==========================================================
# EMERGENCY STOP
# ==========================================================

def emergency_stop():

    # Emergency stop
    plc.write("M90", 1)

    # Stop automatic cycle
    plc.write("L501", 0)

    # Remove start command
    plc.write("X20", 0)

    # Stop request
    plc.write("L540", 1)

    return {
        "status": "success",
        "message": "Emergency stop activated"
    }


# ==========================================================
# RESET
# ==========================================================

def reset_emergency():

    # Reset input
    plc.write("X23", 1)

    # Clear emergency / air fault
    plc.write("M90", 0)
    plc.write("M91", 0)

    # Clear stop requests
    plc.write("L540", 0)
    plc.write("L541", 0)

    # Normal stop input
    plc.write("X21", 1)

    # Remove start command
    plc.write("X20", 0)
    plc.write("L501", 0)

    # Reset pulse
    plc.write("X23", 0)

    return {
        "status": "success",
        "message": "Machine reset successfully"
    }


# ==========================================================
# SELECT MODEL
# ==========================================================

def select_model(model):

    model = int(model)

    if model < 1 or model > 12:
        return {
            "status": "error",
            "message": "Invalid model"
        }

    model_bits = {
        1: "L800",
        2: "L802",
        3: "L804",
        4: "L806",
        5: "L808",
        6: "L810",
        7: "L812",
        8: "L814",
        9: "L816",
        10: "L818",
        11: "L820",
        12: "L822"
    }

    # Clear all model selection bits
    for bit in model_bits.values():
        plc.write(bit, 0)

    # Select requested model
    plc.write(model_bits[model], 1)

    # Store selected model
    plc.write("D1800", model)

    return {
        "status": "success",
        "model": model,
        "message": f"Model {model} selected"
    }


# ==========================================================
# AUTO / MANUAL MODE
# ==========================================================

def set_control_mode(auto_mode):

    auto_mode = bool(auto_mode)

    if auto_mode:

        plc.write("M500", 1)

        return {
            "status": "success",
            "mode": "Auto",
            "message": "Auto mode enabled"
        }

    else:

        # Disable automatic cycle
        plc.write("M500", 0)

        plc.write("L501", 0)
        plc.write("X20", 0)

        return {
            "status": "success",
            "mode": "Manual",
            "message": "Manual mode enabled"
        }