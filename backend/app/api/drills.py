from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.services.drill_scenarios import get_random_scenario, evaluate_answer
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/drills", tags=["Scam Drills"])


class DrillAnswerRequest(BaseModel):
    scenario_id: str
    selected_option: str


@router.get("/scenario")
def get_drill_scenario(
    current_user: User = Depends(get_current_user)
):
    """Return a random scam drill scenario for the user to solve."""
    scenario = get_random_scenario()
    return scenario


@router.post("/answer")
def submit_drill_answer(
    answer: DrillAnswerRequest,
    current_user: User = Depends(get_current_user)
):
    """Evaluate the user's answer to a scam drill scenario."""
    result = evaluate_answer(answer.scenario_id, answer.selected_option)
    if "error" in result:
        return {"status": "error", "message": result["error"]}
    return result
