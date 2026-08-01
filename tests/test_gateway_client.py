import logging

from app.gateway import client as gateway_client


def test_generate_uses_offline_fallback_when_no_api_key(monkeypatch):
    monkeypatch.setattr(gateway_client.settings, "anthropic_api_key", "")
    monkeypatch.setattr(gateway_client.settings, "offline_mode", False)
    answer = gateway_client.generate("What should I check?", ["Some retrieved context."], "system prompt")
    assert "offline mode" in answer
    assert "Some retrieved context." in answer


def test_generate_offline_fallback_with_no_context(monkeypatch):
    monkeypatch.setattr(gateway_client.settings, "anthropic_api_key", "")
    monkeypatch.setattr(gateway_client.settings, "offline_mode", False)
    answer = gateway_client.generate("Anything?", [], "system prompt")
    assert "couldn't find anything" in answer


def test_generate_forces_offline_mode_even_with_key_present(monkeypatch):
    monkeypatch.setattr(gateway_client.settings, "anthropic_api_key", "fake-key")
    monkeypatch.setattr(gateway_client.settings, "offline_mode", True)
    answer = gateway_client.generate("Question", ["context text"], "system")
    assert "offline mode" in answer


def test_generate_cloud_failure_logs_and_does_not_leak_raw_exception(monkeypatch, caplog):
    import anthropic

    monkeypatch.setattr(gateway_client.settings, "anthropic_api_key", "fake-key")
    monkeypatch.setattr(gateway_client.settings, "offline_mode", False)

    class FakeMessages:
        def create(self, **kwargs):
            raise RuntimeError("secret internal detail: invalid api key xyz123")

    class FakeClient:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)

    with caplog.at_level(logging.ERROR, logger="app.gateway.client"):
        answer = gateway_client.generate("question", ["context"], "system")

    assert "cloud model unavailable" in answer
    assert "secret internal detail" not in answer
    assert any("cloud model call failed" in r.message for r in caplog.records)
