import base64

import httpx

from app.providers.base import STTProvider, STTResult, TTSProvider


class SarvamSTTProvider(STTProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        mode: str,
        language_code: str,
        timeout_seconds: float,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.mode = mode
        self.language_code = language_code
        self.timeout_seconds = timeout_seconds

    async def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        filename: str = "audio.wav",
    ) -> STTResult:
        url = f"{self.base_url}/speech-to-text"
        headers = {"api-subscription-key": self.api_key}
        files = {"file": (filename, audio_bytes, mime_type)}
        data = {
            "model": self.model,
            "mode": self.mode,
            "language_code": self.language_code,
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            body = response.json()

        return STTResult(
            text=body.get("transcript", ""),
            lang=body.get("language_code") or "unknown",
            confidence=float(body.get("language_probability") or 0.0),
        )


class SarvamTTSProvider(TTSProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        target_language_code: str,
        speaker: str,
        pace: float,
        timeout_seconds: float,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.target_language_code = target_language_code
        self.speaker = speaker
        self.pace = pace
        self.timeout_seconds = timeout_seconds

    async def speak(self, text: str, voice_id: str, lang_style: str) -> bytes:
        _ = lang_style
        url = f"{self.base_url}/text-to-speech"
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "target_language_code": self.target_language_code,
            "speaker": voice_id or self.speaker,
            "model": self.model,
            "pace": self.pace,
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()

        audios = body.get("audios") or []
        if not audios:
            raise ValueError("Sarvam TTS response did not include audio data")

        return base64.b64decode(audios[0])
