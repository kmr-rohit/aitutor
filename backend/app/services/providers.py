from app.core.config import settings
from app.providers.base import LLMProvider, STTProvider, TTSProvider
from app.providers.mock import MockLLMProvider, MockSTTProvider, MockTTSProvider
from app.providers.openai_provider import OpenAILLMProvider
from app.providers.sarvam import SarvamSTTProvider, SarvamTTSProvider


def get_stt_provider() -> STTProvider:
    if settings.stt_provider == "sarvam" and settings.sarvam_api_key:
        return SarvamSTTProvider(
            api_key=settings.sarvam_api_key,
            base_url=settings.sarvam_base_url,
            model=settings.sarvam_stt_model,
            mode=settings.sarvam_stt_mode,
            language_code=settings.sarvam_stt_language_code,
            timeout_seconds=settings.request_timeout_seconds,
        )
    return MockSTTProvider()


def get_tts_provider() -> TTSProvider:
    if settings.tts_provider == "sarvam" and settings.sarvam_api_key:
        return SarvamTTSProvider(
            api_key=settings.sarvam_api_key,
            base_url=settings.sarvam_base_url,
            model=settings.sarvam_tts_model,
            target_language_code=settings.sarvam_tts_language_code,
            speaker=settings.sarvam_tts_speaker,
            pace=settings.sarvam_tts_pace,
            timeout_seconds=settings.request_timeout_seconds,
        )
    return MockTTSProvider()


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return OpenAILLMProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=settings.request_timeout_seconds,
        )
    return MockLLMProvider()
