"""FastAPI routes for the IndustrialAI diagnostic agent."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .diagnostic_agent import agent
from .monitor import agent_monitor

router = APIRouter(prefix="/ai/agent", tags=["AI Agent"])


class AgentRequest(BaseModel):
    question: str = Field(default="Run AI diagnostics on the latest completed cycle.")
    trigger: str = Field(default="user")


@router.get("/status")
def agent_status():
    return {
        "agent": "IndustrialAI Machine Diagnostic Agent",
        "ready": True,
        "mode": "read_only",
        "monitoring": "on_demand",
        "capabilities": [
            "machine_status",
            "active_alarms",
            "ml_diagnostics",
            "cycle_history",
            "rul",
            "maintenance",
            "evidence_based_diagnosis",
            "autonomous_monitoring",
        ],
    }


@router.post("/investigate")
def investigate(payload: AgentRequest):
    return agent.investigate(payload.question, payload.trigger)


@router.get("/monitor")
def monitor():
    return agent_monitor.check()
