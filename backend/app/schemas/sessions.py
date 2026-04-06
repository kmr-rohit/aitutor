from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import SessionMode


class SessionCreateRequest(BaseModel):
    mode: SessionMode
    topic: str = Field(min_length=2, max_length=120)
    difficulty: str = Field(default="intermediate")


class SessionResponse(BaseModel):
    id: UUID
    mode: SessionMode
    topic: str
    difficulty: str
    created_at: datetime
    status: str


class SessionTurn(BaseModel):
    role: str
    text: str | None = None
    audio_base64: str | None = None
    audio_mime_type: str | None = None
    audio_filename: str | None = None
    language_style: str = "simple_hinglish"


class SessionEndRequest(BaseModel):
    notes: Optional[str] = None


class SessionReportResponse(BaseModel):
    session_id: UUID
    summary: str
    strengths: list[str]
    improvement_areas: list[str]
    next_20_min_plan: list[str]
    quiz_questions: list[str]
    rubric_scores: dict[str, int]
    detailed_report: str = ""
