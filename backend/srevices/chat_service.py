from backend.srevices.live_monitor_services import live_monitor
from backend.srevices.alarm_services import get_active_alarms


def _yes_no(value):
    return "YES" if bool(value) else "NO"


def _machine_summary(data):
    machine = data["machine"]
    safety = data["safety"]
    production = data["production"]
    sequence = data["sequence"]

    safety_text = (
        "No emergency or air-pressure fault is active."
        if not safety["emergency"] and not safety["air_fault"]
        else f"Emergency={_yes_no(safety['emergency'])}, "
             f"Air fault={_yes_no(safety['air_fault'])}."
    )

    return (
        f"Machine state: {machine['state']}. "
        f"Model: {machine['model']}. "
        f"Auto mode: {_yes_no(machine['auto_mode'])}. "
        f"Cycle running: {_yes_no(machine['cycle_running'])}. "
        f"Cycle number: {machine['cycle_number']}. "
        f"Sequence: {sequence['state']}. "
        f"Production completed: {production['completed']} "
        f"of {production['total']}. "
        f"{safety_text}"
    )


def _servo_answer(data):
    servo = data["servo"]
    status = data["servo_status"]

    lines = ["Current servo status:"]
    for key, label in (("axis1", "Axis 1"), ("axis2", "Axis 2"), ("axis3", "Axis 3")):
        axis = servo[key]
        lines.append(
            f"{label}: position={axis.get('position', 0):.1f}, "
            f"target={axis.get('target', 0):.1f}, "
            f"speed={axis.get('actual_speed', 0):.1f}, "
            f"error={axis.get('error', 0):.1f}, "
            f"busy={_yes_no(axis.get('busy'))}, "
            f"complete={_yes_no(axis.get('complete'))}."
        )

    lines.append(
        f"Servo system: ready={_yes_no(status['ready'])}, "
        f"busy={_yes_no(status['busy'])}, "
        f"error={_yes_no(status['error'])}, "
        f"position reached={_yes_no(status['position_reached'])}, "
        f"origin={_yes_no(status['origin'])}."
    )
    return "\n".join(lines)


def _alarm_answer():
    alarms = get_active_alarms()
    if not alarms:
        return "There are currently no active machine alarms."
    lines = [f"There are {len(alarms)} active alarm(s):"]
    for alarm in alarms:
        lines.append(
            f"{alarm['code']} - {alarm['name']} "
            f"({alarm['severity']}): {alarm['message']}."
        )
    return "\n".join(lines)


def _cycle_answer(data):
    machine = data["machine"]
    production = data["production"]
    cycle = data["cycle"]

    duration = cycle.get("current_duration")
    last_duration = cycle.get("last_duration")

    return (
        f"Production: {production['completed']} completed, "
        f"{production['rejected']} rejected, "
        f"{production['total']} total. "
        f"Current cycle: {production['current']}. "
        f"Running: {_yes_no(machine['cycle_running'])}. "
        f"Current duration: {duration if duration is not None else 'N/A'} s. "
        f"Last completed duration: "
        f"{last_duration if last_duration is not None else 'N/A'} s."
    )


def _sequence_answer(data):
    sequence = data["sequence"]
    bits = data["sequence_bits"]

    active = [
        name.replace("_", " ")
        for name, value in bits.items()
        if value
    ]

    active_text = ", ".join(active) if active else "none"
    return (
        f"Current automatic sequence: {sequence['state']}. "
        f"Center travel: {sequence['center_travel']}. "
        f"Center timer: {sequence['center_timer']}. "
        f"Active sequence bits: {active_text}."
    )



def _agent_answer(message):
    from backend.agent.diagnostic_agent import agent
    result = agent.investigate(message, trigger="assistant")
    diagnosis = result["diagnosis"]
    evidence = result.get("evidence", [])
    lines = [
        f"Diagnostic Agent: {diagnosis['label']}.",
        f"Severity: {result['severity']}.",
    ]
    if diagnosis.get("confidence_percent") is not None:
        lines.append(f"ML confidence: {diagnosis['confidence_percent']:.1f}%.")
    lines.append("Evidence:")
    lines.extend(f"- {item['finding']}" for item in evidence[:6])
    lines.append(f"Recommendation: {diagnosis['recommendation']}")
    return {"response": "\n".join(lines), "agent": result}


def _ai_answer():
    try:
        from backend.ai.ml.model_service import ml_service
        result = ml_service.predict_live()
        fault = result.get("predicted_fault", "N/A")
        confidence = float(result.get("fault_confidence", 0)) * 100
        anomaly = "YES" if result.get("anomaly") else "NO"
        score = float(result.get("anomaly_score", 0)) * 100
        return (
            f"Live ML diagnostics are available. "
            f"Anomaly detected: {anomaly}. "
            f"Anomaly score: {score:.1f}%. "
            f"Predicted fault class: {fault}. "
            f"Model confidence: {confidence:.1f}%. "
            f"These are model predictions from the digital-twin telemetry, "
            f"not confirmation of a physical machine fault."
        )
    except Exception as exc:
        return (
            "Live ML diagnostics are not available yet. "
            "Complete at least one machine cycle and ensure the trained "
            f"ML artifacts are loaded. Detail: {str(exc)}"
        )


def chat(message: str):
    text = (message or "").strip().lower()
    data = live_monitor()

    if not text:
        return {
            "response": (
                "Ask me about machine status, servo axes, alarms, "
                "production cycles, the PLC sequence, or AI diagnostics."
            ),
            "mode": "local",
        }

    if any(word in text for word in ("diagnos", "anomal", "maintenance", "root cause", "why is", "why did")):
        result = _agent_answer(message)
        return {
            "response": result["response"],
            "mode": "agent",
            "agent": result["agent"],
            "machine_state": data["machine"]["state"],
            "cycle_number": data["machine"]["cycle_number"],
        }

    if any(word in text for word in ("servo", "axis", "axes", "motor")):
        response = _servo_answer(data)
    elif any(word in text for word in ("alarm", "alarms", "fault", "emergency")):
        response = _alarm_answer()
    elif any(word in text for word in ("cycle", "production", "completed", "rejected")):
        response = _cycle_answer(data)
    elif any(word in text for word in ("sequence", "step", "process")):
        response = _sequence_answer(data)
    elif any(word in text for word in ("ai", "anomaly", "prediction", "predict", "diagnostic", "maintenance")):
        response = _ai_answer()
    elif any(word in text for word in ("model",)):
        response = (
            f"Model {data['machine']['model']} is currently selected. "
            f"The machine is in {data['machine']['state']} and the "
            f"automatic sequence is {data['sequence']['state']}."
        )
    elif any(word in text for word in ("status", "state", "machine", "current", "health")):
        response = _machine_summary(data)
    else:
        response = (
            _machine_summary(data)
            + "\n\nI can also answer specifically about servo axes, "
              "alarms, production cycles, PLC sequence, or AI diagnostics."
        )

    return {
        "response": response,
        "mode": "local",
        "machine_state": data["machine"]["state"],
        "cycle_number": data["machine"]["cycle_number"],
    }
