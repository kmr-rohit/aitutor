import base64

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.providers import LLMTestRequest, LLMTestResponse, STTResponse, TTSRequest, TTSResponse
from app.services.providers import get_llm_provider, get_stt_provider, get_tts_provider

router = APIRouter(prefix="/providers", tags=["providers"])


@router.post("/stt/test", response_model=STTResponse)
async def test_stt(file: UploadFile = File(...)) -> STTResponse:
    try:
        data = await file.read()
        result = await get_stt_provider().transcribe(
            audio_bytes=data,
            mime_type=file.content_type or "audio/wav",
            filename=file.filename or "audio.wav",
        )
        return STTResponse(text=result.text, lang=result.lang, confidence=result.confidence)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"STT provider error: {exc}") from exc


@router.post("/tts/test", response_model=TTSResponse)
async def test_tts(payload: TTSRequest) -> TTSResponse:
    try:
        audio = await get_tts_provider().speak(
            text=payload.text,
            voice_id=payload.voice_id,
            lang_style=payload.language_style,
        )
        return TTSResponse(audio_base64=base64.b64encode(audio).decode("utf-8"), bytes_length=len(audio))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"TTS provider error: {exc}") from exc


@router.post("/llm/test", response_model=LLMTestResponse)
async def test_llm(payload: LLMTestRequest) -> LLMTestResponse:
    try:
        provider = get_llm_provider()
        result = await provider.respond(
            context=[{"role": "learner", "text": payload.text}],
            mode=payload.mode,
            rubric={"clarity": 10, "tradeoffs": 10, "scalability": 10},
        )
        return LLMTestResponse(answer=result.answer, hints=result.hints, followups=result.followups)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"LLM provider error: {exc}") from exc
