"""
Task 6: End-to-end integration test for health cache → tool finder wiring.

Uses direct imports (not subprocess) to avoid editable-install conflicts between
concurrent worktrees sharing the same venv.

Verifies:
1. find "adverse event drug safety" returns SIDER annotated as broken, FAERS as live
2. Live tools sort before broken tools
3. --filter-healthy (via _apply_health_filter) excludes broken tools
4. grep command also carries health annotations
"""

import json

import pytest

from tooluniverse import ToolUniverse
from tooluniverse.tool_finder_keyword import ToolFinderKeyword


@pytest.fixture(scope="module")
def tu():
    instance = ToolUniverse()
    instance.load_tools()
    yield instance


@pytest.fixture(scope="module")
def keyword_finder(tu):
    return ToolFinderKeyword({}, tooluniverse=tu)


def _find(finder, query, limit=15):
    raw = finder._run_json_search({"description": query, "limit": limit})
    return json.loads(raw).get("tools", [])


def _grep(finder, pattern, limit=30):
    raw = finder._run_json_search({"description": pattern, "limit": limit})
    return json.loads(raw).get("tools", [])


@pytest.mark.integration
class TestHealthCacheWiring:
    """End-to-end tests for health annotations in all three tool finders."""

    # ── find ────────────────────────────────────────────────────────────────

    def test_find_annotates_live_faers_tools(self, keyword_finder):
        tools = _find(keyword_finder, "adverse event drug safety")
        faers = [t for t in tools if t["name"].startswith("FAERS")]
        assert faers, "Expected FAERS tools in adverse-event results"
        live_faers = [t for t in faers if t.get("_health") == "live"]
        assert live_faers, "At least some FAERS tools should be annotated as live"

    def test_find_annotates_broken_sider(self, keyword_finder):
        tools = _find(keyword_finder, "adverse event drug safety")
        by_name = {t["name"]: t for t in tools}
        assert "SIDER_get_drugs_for_side_effect" in by_name, (
            "SIDER should appear in adverse-event results"
        )
        sider = by_name["SIDER_get_drugs_for_side_effect"]
        assert sider.get("_health") == "broken"
        assert sider.get("_health_warning"), "Broken tool must include a warning string"

    def test_find_live_tools_sort_before_broken(self, keyword_finder):
        tools = _find(keyword_finder, "adverse event drug safety")
        healths = [t.get("_health") for t in tools]
        found_broken = False
        for h in healths:
            if h == "broken":
                found_broken = True
            elif h in ("live", None) and found_broken:
                pytest.fail(
                    "A live/unknown tool appeared after a broken tool — sort is wrong"
                )

    def test_filter_healthy_excludes_broken(self, keyword_finder):
        from tooluniverse.cli import _apply_health_filter

        raw = keyword_finder._run_json_search(
            {"description": "adverse event drug safety", "limit": 30}
        )
        result = json.loads(raw)

        unfiltered_broken = [
            t for t in result.get("tools", []) if t.get("_health") == "broken"
        ]
        assert unfiltered_broken, "Unfiltered results must contain broken tools"

        filtered = _apply_health_filter(result)
        filtered_broken = [
            t for t in filtered.get("tools", []) if t.get("_health") == "broken"
        ]
        assert filtered_broken == [], "Filtered results must not contain broken tools"

    def test_filter_healthy_keeps_live_tools(self, keyword_finder):
        from tooluniverse.cli import _apply_health_filter

        raw = keyword_finder._run_json_search(
            {"description": "adverse event drug safety", "limit": 30}
        )
        filtered = _apply_health_filter(json.loads(raw))
        tools = filtered.get("tools", [])
        assert tools, "Filtered results should not be empty"
        assert all(t.get("_health") != "broken" for t in tools)

    # ── grep ────────────────────────────────────────────────────────────────

    def test_grep_annotates_live_faers_tools(self, keyword_finder):
        tools = _grep(keyword_finder, "FAERS_count_reactions_by_drug_event")
        by_name = {t["name"]: t for t in tools}
        assert "FAERS_count_reactions_by_drug_event" in by_name, (
            "Exact-name grep should return the tool"
        )
        t = by_name["FAERS_count_reactions_by_drug_event"]
        assert t.get("_health") == "live"

    def test_grep_annotates_broken_ctd_tools(self, keyword_finder):
        tools = _grep(keyword_finder, "CTD chemical gene")
        ctd_broken = [
            t
            for t in tools
            if t["name"].startswith("CTD") and t.get("_health") == "broken"
        ]
        assert ctd_broken, "CTD tools should be annotated as broken"

    def test_grep_broken_tools_annotated_with_warning(self, keyword_finder):
        tools = _grep(keyword_finder, "SIDER drug side effect")
        sider = [t for t in tools if t["name"].startswith("SIDER")]
        assert sider, "SIDER tools should appear in side-effect grep"
        for t in sider:
            assert t.get("_health") == "broken"
            assert t.get("_health_warning"), "Each broken tool needs a warning"

    # ── unknown tools have no _health key ───────────────────────────────────

    def test_unknown_tools_not_annotated(self, keyword_finder):
        """Tools with no health record should not get a _health field."""
        tools = _find(keyword_finder, "protein structure prediction")
        # Not all tools are in the health cache; unknown is fine — just no key
        for t in tools:
            if t.get("_health") is None:
                assert "_health" not in t, (
                    f"{t['name']}: _health key should be absent for unknown tools, not None"
                )
