from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2500)
    voice_id: str = ""
    language_style: str = "simple_hinglish"


class TTSResponse(BaseModel):
    audio_base64: str
    bytes_length: int


class LLMTestRequest(BaseModel):
    text: str = Field(min_length=1)
    mode: str = "hld_practice"


class LLMTestResponse(BaseModel):
    answer: str
    hints: list[str]
    followups: list[str]


class STTResponse(BaseModel):
    text: str
    lang: str
    confidence: float
