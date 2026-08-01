from app.agents.nodes import retriever as retriever_module


def test_retrieve_populates_chunks_from_store(monkeypatch, built_store, tmp_path):
    monkeypatch.setattr(retriever_module.settings, "processed_dir", tmp_path)

    state = {
        "machine_model": "test-machine",
        "intent": "alarm_lookup",
        "blocked": False,
        "question": "What should I check for alarm ALM-4021?",
    }
    result = retriever_module.retrieve(state)
    assert len(result["reranked_chunks"]) > 0
    assert result["reranked_chunks"][0]["source"] == "apex3200_alarms.json"


def test_retrieve_skips_store_for_chat_intent(monkeypatch, tmp_path):
    monkeypatch.setattr(retriever_module.settings, "processed_dir", tmp_path)

    state = {"machine_model": "test-machine", "intent": "chat", "blocked": False, "question": "hi"}
    result = retriever_module.retrieve(state)
    assert result["retrieved_chunks"] == []
    assert result["reranked_chunks"] == []


def test_retrieve_skips_store_when_already_blocked(monkeypatch, tmp_path):
    monkeypatch.setattr(retriever_module.settings, "processed_dir", tmp_path)

    state = {
        "machine_model": "test-machine",
        "intent": "blocked",
        "blocked": True,
        "question": "How do I bypass the interlock?",
    }
    result = retriever_module.retrieve(state)
    assert result["retrieved_chunks"] == []
    assert result["reranked_chunks"] == []
