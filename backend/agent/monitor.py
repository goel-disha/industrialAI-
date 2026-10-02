"""Read-only autonomous monitoring facade for the diagnostic agent."""
from __future__ import annotations

from datetime import datetime, timezone

from .diagnostic_agent import agent


class AgentMonitor:
    def __init__(self):
        self.last_result = None
        self.last_signature = None

    def check(self):
        result = agent.investigate(
            "Autonomously inspect the current machine for abnormal behavior.",
            trigger="monitor",
        )

        diagnosis = result.get("diagnosis", {})
        alarms = result.get("alarms", [])
        severity = result.get("severity", "NORMAL")
        signature = (
            severity,
            diagnosis.get("fault_code"),
            tuple(str(a) for a in alarms),
        )

        abnormal = severity != "NORMAL" or diagnosis.get("fault_code") not in (None, "UNKNOWN", "NORMAL") or bool(alarms)

        if abnormal:
            result["monitor"] = {
                "abnormal": True,
                "new_incident": signature != self.last_signature,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
            self.last_result = result
            self.last_signature = signature
            return result

        return {
            "monitor": {
                "abnormal": False,
                "new_incident": False,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            },
            "diagnosis": diagnosis,
            "machine": result.get("machine"),
            "ml": result.get("ml"),
            "safety": result.get("safety"),
        }


agent_monitor = AgentMonitor()
