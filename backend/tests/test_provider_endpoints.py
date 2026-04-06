import base64

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_llm_provider_test_endpoint() -> None:
    res = client.post("/api/providers/llm/test", json={"text": "Explain load balancer simply"})
    assert res.status_code == 200
    body = res.json()
    assert body["answer"]
    assert isinstance(body["hints"], list)


def test_tts_provider_test_endpoint() -> None:
    res = client.post(
        "/api/providers/tts/test",
        json={"text": "Hello from test", "voice_id": "", "language_style": "simple_hinglish"},
    )
    assert res.status_code == 200
    body = res.json()
    decoded = base64.b64decode(body["audio_base64"])
    assert body["bytes_length"] == len(decoded)


def test_stt_provider_test_endpoint() -> None:
    files = {"file": ("sample.wav", b"fake-audio-bytes", "audio/wav")}
    res = client.post("/api/providers/stt/test", files=files)
    assert res.status_code == 200
    body = res.json()
    assert body["text"]
    assert "lang" in body
