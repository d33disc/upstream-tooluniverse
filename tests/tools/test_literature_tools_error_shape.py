#!/usr/bin/env python3
"""
Contract-style tests to ensure literature tools return meaningful, consistent
shapes on basic validation failures (e.g., missing query).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tooluniverse.europe_pmc_tool import EuropePMCTool
from tooluniverse.pmc_tool import PMCTool
from tooluniverse.semantic_scholar_tool import SemanticScholarTool


@pytest.mark.unit
@pytest.mark.parametrize(
    "tool_cls",
    [
        EuropePMCTool,
        SemanticScholarTool,
    ],
)
def test_missing_query_returns_error_envelope(tool_cls):
    tool = tool_cls({"name": "x"})
    result = tool.run({"limit": 1})

    assert result["status"] == "error"
    assert "query" in result["error"]


@pytest.mark.unit
def test_pmc_missing_query_returns_legacy_error_list():
    result = PMCTool({"name": "x"}).run({"limit": 1})

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)
    assert "error" in result[0]
    assert result[0].get("retryable") is False
