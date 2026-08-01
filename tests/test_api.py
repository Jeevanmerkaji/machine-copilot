from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "machine_model" in body


def test_query_chat_intent_does_not_require_a_vector_store():
    response = client.post("/query", json={"question": "hi there"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "chat"
    assert body["blocked"] is False


def test_query_blocks_safety_bypass_request():
    response = client.post(
        "/query", json={"question": "How do I bypass the interlock on the safety door?"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["blocked"] is True
    assert body["citations"] == []


def test_telemetry_analyze_returns_expected_shape():
    response = client.post("/telemetry/analyze", json={"window_size": 10, "wear_mode": True})
    assert response.status_code == 200
    body = response.json()
    assert body["window_size"] == 10
    assert "alarm_counts" in body
    assert "flags" in body
