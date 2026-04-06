import base64

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_voice_socket_with_audio_payload() -> None:
    create = client.post(
        "/api/sessions",
        json={"mode": "hld_practice", "topic": "Design cache", "difficulty": "intermediate"},
    )
    session_id = create.json()["id"]

    with client.websocket_connect(f"/api/sessions/{session_id}/voice") as ws:
        ws.send_json(
            {
                "role": "learner",
                "audio_base64": base64.b64encode(b"fake-audio").decode("utf-8"),
                "language_style": "simple_hinglish",
            }
        )
        data = ws.receive_json()

    assert data["role"] == "tutor"
    assert data["text"]
    assert "audio_base64" in data
