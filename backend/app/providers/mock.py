from app.providers.base import LLMProvider, LLMResult, STTProvider, STTResult, TTSProvider


class MockSTTProvider(STTProvider):
    async def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        filename: str = "audio.wav",
    ) -> STTResult:
        _ = (audio_bytes, mime_type, filename)
        return STTResult(text="Aap system design ka load balancer explain kariye", lang="hi-en", confidence=0.95)


class MockTTSProvider(TTSProvider):
    async def speak(self, text: str, voice_id: str, lang_style: str) -> bytes:
        _ = (voice_id, lang_style)
        return text.encode("utf-8")


class MockLLMProvider(LLMProvider):
    async def respond(self, context: list[dict], mode: str, rubric: dict) -> LLMResult:
        _ = rubric
        latest = context[-1]["text"] if context else "topic"
        return LLMResult(
            answer=(
                f"Chalo simple Hinglish me samajhte hain ({mode}). "
                f"Sawal: {latest}. Step by step approach lenge with real-world analogy."
            ),
            hints=[
                "Start with requirement clarification",
                "Discuss tradeoffs before final architecture",
            ],
            followups=["Agar traffic 10x ho jaye to kya badlega?"],
        )
