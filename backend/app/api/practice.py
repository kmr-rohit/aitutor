from fastapi import APIRouter

from app.schemas.practice import PracticeEvaluateRequest, PracticeEvaluateResponse
from app.services.practice_service import practice_service

router = APIRouter(prefix="/practice", tags=["practice"])


@router.post("/hld/evaluate", response_model=PracticeEvaluateResponse)
def evaluate_hld(payload: PracticeEvaluateRequest) -> PracticeEvaluateResponse:
    return practice_service.evaluate_hld(payload)


@router.post("/language/evaluate", response_model=PracticeEvaluateResponse)
def evaluate_language(payload: PracticeEvaluateRequest) -> PracticeEvaluateResponse:
    return practice_service.evaluate_language(payload)
