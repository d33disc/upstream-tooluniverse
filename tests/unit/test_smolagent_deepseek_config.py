"""Regression guard: smolagent tools must not be pinned to the HMS Azure endpoint.

advanced_literature_search_agent (and open_deep_research_agent) shipped with every
model block pinned to AzureOpenAIModel at https://azure-ai.hms.edu with
env:AZURE_OPENAI_API_KEY. Without that key the tool failed with "Missing credentials".
The fix points all smolagent model blocks at DeepSeek through its OpenAI-compatible API.
"""

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_DATA_FILE = (
    Path(__file__).parent.parent.parent
    / "src"
    / "tooluniverse"
    / "data"
    / "smolagent_tools.json"
)


def _tools():
    return json.loads(_DATA_FILE.read_text())


def _model_blocks(node):
    """Yield every dict that looks like a model config, recursively."""
    if isinstance(node, dict):
        if "provider" in node and "model_id" in node:
            yield node
        for value in node.values():
            yield from _model_blocks(value)
    elif isinstance(node, list):
        for value in node:
            yield from _model_blocks(value)


def test_no_azure_pin_remains():
    raw = _DATA_FILE.read_text()
    assert "AzureOpenAIModel" not in raw
    assert "azure-ai.hms.edu" not in raw
    assert "AZURE_OPENAI_API_KEY" not in raw


def test_all_models_point_at_deepseek():
    for tool in _tools():
        blocks = list(_model_blocks(tool))
        assert blocks, tool["name"]
        for model in blocks:
            assert model["provider"] == "OpenAIModel", model
            assert model["model_id"] == "deepseek-v4-pro", model
            assert model["api_key"] == "env:DEEPSEEK_API_KEY", model
            assert model["api_base"] == "https://api.deepseek.com", model


def test_model_initializes_against_deepseek(monkeypatch):
    smolagents = pytest.importorskip("smolagents")
    OpenAIModel = smolagents.OpenAIModel

    from tooluniverse.smolagent_tool import SmolAgentTool

    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-key")
    tool = next(t for t in _tools() if t["name"] == "advanced_literature_search_agent")
    st = SmolAgentTool(
        {"name": tool["name"], "type": "SmolAgentTool", "settings": tool["settings"]}
    )
    model = st._init_model()

    assert isinstance(model, OpenAIModel)
    assert model.model_id == "deepseek-v4-pro"
    assert model.client_kwargs["api_key"] == "sk-test-key"
    assert model.client_kwargs["base_url"] == "https://api.deepseek.com"
