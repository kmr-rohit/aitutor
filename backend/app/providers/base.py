from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class STTResult:
    text: str
    lang: str
    confidence: float


@dataclass
class LLMResult:
    answer: str
    hints: list[str]
    followups: list[str]


class STTProvider(ABC):
    @abstractmethod
    async def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        filename: str = "audio.wav",
    ) -> STTResult: ...


class TTSProvider(ABC):
    @abstractmethod
    async def speak(self, text: str, voice_id: str, lang_style: str) -> bytes: ...


class LLMProvider(ABC):
    @abstractmethod
    async def respond(self, context: list[dict], mode: str, rubric: dict) -> LLMResult: ...
