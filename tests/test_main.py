import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.bot import ChatbotEngine, PERSONAS
from app.core.memory import ConversationMemory

client = TestClient(app)

def test_root_html_render():
    response = client.get("/")
    assert response.status_code == 200
    assert "Nexus AI" in response.text
    assert "persona-picker" in response.text

def test_personas_endpoint():
    response = client.get("/api/personas")
    assert response.status_code == 200
    data = response.json()
    assert "assistant" in data
    assert "coder" in data
    assert data["assistant"]["name"] == "Nova"

def test_regular_chat_endpoint():
    payload = {
        "session_id": "test-session-1",
        "message": "Hello there",
        "persona": "assistant"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    assert "Nova" in body["response"]

def test_streaming_chat_endpoint():
    params = {
        "session_id": "test-stream-session",
        "message": "What is 10 + 20",
        "persona": "assistant"
    }
    response = client.get("/api/chat/stream", params=params)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "Result: `10 + 20 = 30`" in response.text

def test_history_and_clear():
    session_id = "test-history-session"
    # Add message
    client.post("/api/chat", json={
        "session_id": session_id,
        "message": "Test memory",
        "persona": "assistant"
    })
    # Fetch history
    history_resp = client.get(f"/api/history/{session_id}")
    assert history_resp.status_code == 200
    messages = history_resp.json()
    assert len(messages) >= 2  # user + bot

    # Clear history
    del_resp = client.delete(f"/api/history/{session_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "cleared"

    # Verify cleared
    history_cleared = client.get(f"/api/history/{session_id}")
    assert len(history_cleared.json()) == 0

def test_core_math_evaluation():
    engine = ChatbotEngine()
    res = engine.generate_response("calculate 15 * 4")
    assert "60" in res

def test_core_coder_persona():
    engine = ChatbotEngine()
    res = engine.generate_response("write python function", persona_key="coder")
    assert "def process_data" in res
