"""Unit tests for ClaudeCliClient._parse_cli_payload.

Regression for the agentic-tool crash `'list' object has no attribute 'get'`:
`claude --print --output-format json` can emit EITHER a single result object OR a
list of stream events ([system, assistant, result]). The parser must handle both,
surface is_error responses as errors, and fall back to assistant text when no
result event is present.
"""

import json

from tooluniverse.llm_clients import ClaudeCliClient

parse = ClaudeCliClient._parse_cli_payload


def test_single_dict_payload():
    content, cost, err = parse(json.dumps({"result": "hello", "cost_usd": 0.01}))
    assert err is None
    assert content == "hello"
    assert cost == 0.01


def test_event_array_payload_extracts_result():
    payload = [
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "hi"}]}},
        {
            "type": "result",
            "is_error": False,
            "result": "final answer",
            "total_cost_usd": 0.02,
        },
    ]
    content, cost, err = parse(json.dumps(payload))
    assert err is None
    assert content == "final answer"
    assert cost == 0.02


def test_event_array_is_error_returns_error():
    payload = [
        {"type": "system", "subtype": "init"},
        {
            "type": "result",
            "is_error": True,
            "result": "API Error: 400 usage limit",
            "total_cost_usd": 0,
        },
    ]
    content, _cost, err = parse(json.dumps(payload))
    assert content is None
    assert "usage limit" in err


def test_event_array_without_result_falls_back_to_assistant_text():
    payload = [
        {"type": "system", "subtype": "init"},
        {
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": "partial"}]},
        },
    ]
    content, _cost, err = parse(json.dumps(payload))
    assert err is None
    assert content == "partial"


def test_unexpected_shape_returns_error():
    content, _cost, err = parse(json.dumps("just a string"))
    assert content is None
    assert err is not None
