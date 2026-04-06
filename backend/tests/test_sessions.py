from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_session_create_end_report_flow() -> None:
    create = client.post(
        "/api/sessions",
        json={"mode": "hld_practice", "topic": "Design URL shortener", "difficulty": "intermediate"},
    )
    assert create.status_code == 200
    session_id = create.json()["id"]

    end = client.post(f"/api/sessions/{session_id}/end", json={})
    assert end.status_code == 200
    assert "next_20_min_plan" in end.json()
    assert "detailed_report" in end.json()

    report = client.get(f"/api/sessions/{session_id}/report")
    assert report.status_code == 200
    assert report.json()["session_id"] == session_id
