from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_hld_evaluate() -> None:
    res = client.post(
        "/api/practice/hld/evaluate",
        json={
            "prompt": "Design a rate limiter",
            "answer": "I will start with requirements and discuss tradeoff between latency and cost using cache and queue.",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["overall_score"] >= 1
    assert "scores" in body


def test_language_evaluate() -> None:
    res = client.post(
        "/api/practice/language/evaluate",
        json={
            "prompt": "Explain Go channels",
            "answer": "Go channels coordinate goroutines. Discuss runtime behavior, edge case handling, and memory usage.",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["overall_score"] >= 1
