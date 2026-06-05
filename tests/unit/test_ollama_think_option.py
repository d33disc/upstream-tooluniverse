"""Unit tests for the tuned Ollama fallback options (think / temperature).

`qwen3.5:35b-a3b` is a thinking-capable model: left to default it spends ~3k tokens
reasoning before answering, so a bounded `num_predict` yields EMPTY content and every
agentic call pays a 14-118s latency tax. The tuned fallback entry sends `think=False`
(direct, valid output, 5-19x faster) and `temperature=0.0` (deterministic). These tests
pin both the wiring (OllamaClient forwards `think` into the payload) and the config
(the default chain entry carries the tuned options).
"""

from tooluniverse.agentic_tool import DEFAULT_FALLBACK_CHAIN, AgenticTool
from tooluniverse.llm_clients import OllamaClient


def _sticky_ollama_tool(captured):
    """An AgenticTool whose active backend is sticky-OLLAMA (the state after a prior
    runtime fallback), with a capturing fake client — no network, no __init__."""
    tool = AgenticTool.__new__(AgenticTool)
    tool._global_fallback_chain = DEFAULT_FALLBACK_CHAIN
    tool._api_type = tool._current_api_type = "OLLAMA"
    tool._model_id = tool._current_model_id = "qwen3.5:35b-a3b"
    tool._use_global_fallback = True
    tool._temperature = 1.0
    tool._return_json = False
    tool._max_retries = 1
    tool._retry_delay = 0
    tool.name = "T"
    tool.logger = type("L", (), {"info": staticmethod(lambda *a, **k: None)})()

    class _FakeClient:
        def infer(self, **kw):
            captured.update(kw)
            return "ok"

    tool._llm_client = _FakeClient()
    return tool


class _FakeResp:
    def __init__(self, content):
        self._content = content

    def raise_for_status(self):
        pass

    def json(self):
        return {"message": {"content": self._content}}


def _client_capturing(captured):
    client = OllamaClient.__new__(OllamaClient)
    client.model_name = "qwen3.5:35b-a3b"
    client.server_url = "http://localhost:11434"
    client.logger = type("L", (), {"error": staticmethod(lambda *a, **k: None)})()

    class _Req:
        ConnectionError = Exception

        @staticmethod
        def post(url, json=None, timeout=None):
            captured["payload"] = json
            return _FakeResp("ok")

    client._requests = _Req()
    return client


def test_infer_forwards_think_false_into_payload():
    captured = {}
    client = _client_capturing(captured)
    client.infer(
        messages=[{"role": "user", "content": "hi"}],
        temperature=0.0,
        max_tokens=None,
        return_json=False,
        think=False,
    )
    assert captured["payload"]["think"] is False
    assert captured["payload"]["options"]["temperature"] == 0.0


def test_infer_omits_think_when_not_set():
    captured = {}
    client = _client_capturing(captured)
    client.infer(
        messages=[{"role": "user", "content": "hi"}],
        temperature=0.5,
        max_tokens=None,
        return_json=False,
    )
    assert "think" not in captured["payload"]


def test_default_chain_ollama_entry_carries_tuned_options():
    ollama = next(e for e in DEFAULT_FALLBACK_CHAIN if e["api_type"] == "OLLAMA")
    assert ollama["model_id"] == "qwen3.5:35b-a3b"
    assert ollama["options"] == {"think": False, "temperature": 0.0}


def test_sticky_ollama_primary_applies_tuned_options():
    """Regression: after a fallback, OLLAMA becomes the sticky active backend. Its tuned
    options must still apply (else warm calls revert to temp 1.0 + thinking on)."""
    captured = {}
    tool = _sticky_ollama_tool(captured)
    tool._buffered_infer_with_fallback([{"role": "user", "content": "hi"}], None)
    assert captured["think"] is False
    assert captured["temperature"] == 0.0


def test_chain_options_lookup_by_backend():
    tool = _sticky_ollama_tool({})
    assert tool._chain_options_for("OLLAMA", "qwen3.5:35b-a3b") == {
        "think": False,
        "temperature": 0.0,
    }
    assert tool._chain_options_for("CLAUDE_CLI", "haiku") == {}
