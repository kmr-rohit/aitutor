from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "AI Learn Backend"
    app_env: str = "dev"
    api_prefix: str = "/api"

    default_explanation_style: str = "simple_hinglish"
    default_tutor_tone: str = "warm_supportive"

    llm_provider: str = "mock"
    stt_provider: str = "mock"
    tts_provider: str = "mock"

    sarvam_api_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    sarvam_base_url: str = "https://api.sarvam.ai"
    sarvam_stt_model: str = "saaras:v3"
    sarvam_stt_mode: str = "codemix"
    sarvam_stt_language_code: str = "unknown"
    sarvam_tts_model: str = "bulbul:v3"
    sarvam_tts_language_code: str = "hi-IN"
    sarvam_tts_speaker: str = "shubh"
    sarvam_tts_pace: float = 1.0

    request_timeout_seconds: float = 30.0
    enable_hinglish_refiner: bool = True
    hinglish_refiner_model: str = ""
    enable_deep_report: bool = True
    deep_report_model: str = ""


settings = Settings()
