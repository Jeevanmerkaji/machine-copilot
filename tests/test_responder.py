from app.agents.nodes import responder as responder_module


def _state(**overrides):
    state = {
        "question": "What should I check for alarm ALM-4021?",
        "machine_model": "Apex-3200",
        "intent": "alarm_lookup",
        "blocked": False,
        "reranked_chunks": [
            {"chunk_id": "a1", "source": "apex3200_alarms.json", "text": "Torque the retaining nut to 28 Nm."}
        ],
    }
    state.update(overrides)
    return state


def test_respond_returns_block_reason_when_already_blocked():
    state = _state(blocked=True, block_reason="blocked reason text")
    result = responder_module.respond(state)
    assert result["answer"] == "blocked reason text"
    assert result["citations"] == []


def test_respond_chat_intent_short_circuits_without_calling_gateway(monkeypatch):
    called = False

    def fake_generate(*args, **kwargs):
        nonlocal called
        called = True
        return "should not be used"

    monkeypatch.setattr(responder_module, "generate", fake_generate)
    state = _state(intent="chat", reranked_chunks=[])
    result = responder_module.respond(state)
    assert "Machine Copilot" in result["answer"]
    assert called is False


def test_respond_happy_path_returns_grounded_answer_and_citations(monkeypatch):
    monkeypatch.setattr(responder_module, "generate", lambda *a, **k: "Torque the retaining nut to 28 Nm.")
    state = _state()
    result = responder_module.respond(state)
    assert result["blocked"] is False
    assert result["citations"] == ["apex3200_alarms.json"]


def test_respond_blocks_ungrounded_numeric_claim(monkeypatch):
    monkeypatch.setattr(responder_module, "generate", lambda *a, **k: "Torque the retaining nut to 99 Nm.")
    state = _state()
    result = responder_module.respond(state)
    assert result["blocked"] is True
    assert "99 Nm" in result["answer"]
