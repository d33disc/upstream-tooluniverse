"""Tests for BM25 ranking of tu grep results (Option A).

Contract: GrepToolsTool.run() returns substring matches ranked by relevance,
NOT dict order. BM25 must put name-evidence matches above description-only
matches, and shorter documents (same evidence) above longer ones.

The fixture deliberately places the description-only match FIRST in dict
order so that any dict-order implementation fails these tests.
"""

import pytest


class FakeToolUniverse:
    """Minimal stand-in exposing all_tool_dict for GrepToolsTool."""

    def __init__(self, tools):
        self.all_tool_dict = {t["name"]: t for t in tools}
        self.tool_category_dicts = {}
        self.all_tools = tools


# Dict order is deliberately NOT relevance order: xyz_analysis_tool (the
# description-only match) comes first; UniProt (no match) second.
TOOLS = [
    {
        "name": "xyz_analysis_tool",
        "description": "Perform search across patent databases and report results for the examiner.",
        "type": "AnalysisTool",
        "parameter": {"properties": {"query": {"type": "string"}}},
    },
    {
        "name": "UniProt_get_entry",
        "description": "Get a UniProt entry by accession.",
        "type": "UniProtTool",
        "parameter": {"properties": {"accession": {"type": "string"}}},
    },
    {
        "name": "USPTO_search_enriched_citations",
        "description": "Search office action citations.",
        "type": "DSAPITool",
        "parameter": {"properties": {"query": {"type": "string"}}},
    },
    {
        "name": "pubmed_search_tool",
        "description": "Search PubMed.",
        "type": "PubMedTool",
        "parameter": {"properties": {"query": {"type": "string"}}},
    },
]


@pytest.fixture
def tool():
    from tooluniverse.tool_discovery_tools import GrepToolsTool

    return GrepToolsTool({}, tooluniverse=FakeToolUniverse(TOOLS))


class TestGrepRanking:
    def test_description_match_ranked_below_name_matches(self, tool):
        """The description-only match (xyz_analysis_tool) must sink below the
        two name-evidence matches, even though it is first in dict order."""
        result = tool.run({"pattern": "search", "field": "description"})
        names = [t["name"] for t in result.get("tools", [])]
        assert "xyz_analysis_tool" in names
        assert names[-1] == "xyz_analysis_tool"
        assert names[0] in ("USPTO_search_enriched_citations", "pubmed_search_tool")

    def test_shorter_document_wins_on_equal_evidence(self, tool):
        """Both name matches contain 'search' once; the shorter document
        (pubmed_search_tool) must rank above the longer one."""
        result = tool.run({"pattern": "search", "field": "name"})
        names = [t["name"] for t in result.get("tools", [])]
        assert names[0] == "pubmed_search_tool"
        assert names[1] == "USPTO_search_enriched_citations"
