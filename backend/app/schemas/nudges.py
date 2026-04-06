from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NudgeScheduleRequest(BaseModel):
    user_id: UUID
    channel: str = Field(default="whatsapp")
    message: str
    scheduled_for: datetime


class NudgeAckRequest(BaseModel):
    user_id: UUID
    nudge_id: UUID


class StreakResponse(BaseModel):
    user_id: UUID
    current_streak_days: int
    last_active_at: datetime | None = None
