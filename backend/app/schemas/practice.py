from pydantic import BaseModel, Field


class PracticeEvaluateRequest(BaseModel):
    prompt: str = Field(min_length=5)
    answer: str = Field(min_length=10)


class PracticeEvaluateResponse(BaseModel):
    overall_score: int
    scores: dict[str, int]
    strengths: list[str]
    improvements: list[str]
    sample_better_answer: str
