import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_chat_requires_question():
    response = client.post("/api/v1/chat", json={"session_id": "test-session", "question": ""})
    assert response.status_code in (400, 422)


def test_ingest_mock_mode():
    response = client.post("/api/v1/ingest", json={"query": "finance"})
    assert response.status_code == 200
    body = response.json()
    assert "fetched" in body and "inserted" in body


def test_chat_history_empty_session():
    response = client.get("/api/v1/chat/history/nonexistent-session")
    assert response.status_code == 200
    assert response.json()["messages"] == []
