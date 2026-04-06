from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.nudges import NudgeAckRequest, NudgeScheduleRequest, StreakResponse
from app.services.nudge_service import nudge_service

router = APIRouter(prefix="/nudges", tags=["nudges"])


@router.post("/schedule")
def schedule_nudge(payload: NudgeScheduleRequest) -> dict:
    import uuid

    nudge_id = uuid.uuid4()
    nudge_service.schedule(
        user_id=payload.user_id,
        nudge_id=nudge_id,
        channel=payload.channel,
        message=payload.message,
        scheduled_for=payload.scheduled_for,
    )
    return {"nudge_id": str(nudge_id), "status": "scheduled"}


@router.post("/ack", response_model=StreakResponse)
def acknowledge_nudge(payload: NudgeAckRequest) -> StreakResponse:
    try:
        streak = nudge_service.acknowledge(payload.user_id, payload.nudge_id)
        return StreakResponse(user_id=payload.user_id, **streak)
    except (KeyError, PermissionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/streaks/{user_id}", response_model=StreakResponse)
def get_streak(user_id: UUID) -> StreakResponse:
    streak = nudge_service.get_streak(user_id)
    return StreakResponse(user_id=user_id, **streak)
