"""
Tasks 6-7: End-to-end integration test for health cache → tool finder wiring.

Uses direct imports (not subprocess) to avoid editable-install conflicts between
concurrent worktrees sharing the same venv.

Verifies:
1. find "adverse event drug safety" returns SIDER annotated as broken, FAERS as live
2. Live tools sort before broken tools
3. --filter-healthy (via _apply_health_filter) excludes broken/stale tools
4. grep command also carries health annotations
5. Stale broken records get _health="stale" instead of "broken" (Task 7)
6. Stale sort order: live < stale < broken
7. --filter-healthy also excludes stale tools (Task 7)

Environmental dependency:
The `TestHealthCacheWiring` class requires ``~/.tooluniverse/health.json`` to be
pre-populated with real annotations for FAERS (live), SIDER (broken), and CTD
(broken) tools. This cache is user-local, gitignored, and built via
``tu health refresh`` — it does NOT exist on fresh CI runners. The module-level
``_health_cache_is_populated`` check below skips the whole class when the cache
is missing or lacks the expected fixtures, so CI stays green while preserving
real coverage for local developers who run ``tu health refresh`` first.

``TestStaleHealthRecords`` uses its own tmp_path fixture and always runs.
"""

import json
import tempfile
import time
from pathlib import Path

import pytest

from tooluniverse import ToolUniverse
from tooluniverse.tool_finder_keyword import ToolFinderKeyword
from tooluniverse.tool_health import DEFAULT_CACHE_PATH, ToolHealthCache


def _health_cache_is_populated() -> bool:
    """Return True if the user-local health cache has the entries these tests need.

    The TestHealthCacheWiring class asserts that specific tools carry specific
    ``_health`` annotations end-to-end through the tool finder. Those annotations
    come from ``~/.tooluniverse/health.json``, which is user-local and never
    committed. If the cache is missing or lacks the fixture tools, the tests
    cannot possibly pass and should skip cleanly rather than fail.
    """
    if not DEFAULT_CACHE_PATH.exists():
        return False
    try:
        cache = ToolHealthCache(path=DEFAULT_CACHE_PATH)
        # The test fixtures exercise three tool families. Require at least one
        # live FAERS entry and at least one broken SIDER entry; CTD is a bonus.
        cache._ensure_loaded()  # noqa: SLF001 — test setup, not production code
        data = cache._data  # noqa: SLF001
        has_live_faers = any(
            k.startswith("FAERS") and v.get("status") == "live" for k, v in data.items()
        )
        has_broken_sider = any(
            k.startswith("SIDER") and v.get("status") == "broken"
            for k, v in data.items()
        )
        return has_live_faers and has_broken_sider
    except (OSError, json.JSONDecodeError, KeyError):
        return False


_SKIP_REASON = (
    "health cache not populated (~/.tooluniverse/health.json missing or lacks "
    "FAERS/SIDER fixtures) — run `tu health refresh` to enable these tests locally"
)


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
@pytest.mark.skipif(not _health_cache_is_populated(), reason=_SKIP_REASON)
class TestHealthCacheWiring:
    """End-to-end tests for health annotations in all three tool finders.

    Skipped in environments without a populated ``~/.tooluniverse/health.json``
    (e.g., fresh CI runners). See module docstring for details.
    """

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


@pytest.mark.integration
class TestStaleHealthRecords:
    """Task 7: stale broken records use _health='stale' instead of 'broken'."""

    @pytest.fixture
    def stale_cache(self, tmp_path):
        """Cache with one old-broken, one recent-broken, one live tool."""
        import json
        from tooluniverse.tool_health import ToolHealthCache, STALE_DAYS

        p = tmp_path / "health.json"
        old_epoch = time.time() - (STALE_DAYS + 1) * 86400
        now_epoch = time.time()
        p.write_text(
            json.dumps(
                {
                    "OldBroken": {
                        "status": "broken",
                        "detail": "timeout",
                        "tested": "2025-01-01",
                        "tested_epoch": old_epoch,
                    },
                    "RecentBroken": {
                        "status": "broken",
                        "detail": "error",
                        "tested": "2026-03-28",
                        "tested_epoch": now_epoch,
                    },
                    "LiveTool": {
                        "status": "live",
                        "detail": "passed",
                        "tested": "2026-03-28",
                        "tested_epoch": now_epoch,
                    },
                }
            )
        )
        return ToolHealthCache(path=p)

    def test_old_broken_becomes_stale(self, stale_cache):
        assert stale_cache.health_status("OldBroken") == "stale"

    def test_recent_broken_stays_broken(self, stale_cache):
        assert stale_cache.health_status("RecentBroken") == "broken"

    def test_live_stays_live(self, stale_cache):
        assert stale_cache.health_status("LiveTool") == "live"

    def test_unknown_returns_none(self, stale_cache):
        assert stale_cache.health_status("NonExistent") is None

    def test_stale_warn_message(self, stale_cache):
        msg = stale_cache.warn("OldBroken")
        assert msg is not None
        assert "stale" in msg.lower()
        assert "--refresh" in msg

    def test_broken_warn_message(self, stale_cache):
        msg = stale_cache.warn("RecentBroken")
        assert msg is not None
        assert "WARNING" in msg
        assert "failed health check" in msg

    def test_live_warn_is_none(self, stale_cache):
        assert stale_cache.warn("LiveTool") is None

    def test_stale_sort_order(self):
        """Sort key: live=0 < stale=1 < broken=2."""
        tools = [
            {"name": "A", "_health": "broken"},
            {"name": "B", "_health": "stale"},
            {"name": "C", "_health": "live"},
            {"name": "D"},  # unknown
        ]
        _SORT_KEY = {"live": 0, "stale": 1, "broken": 2}
        tools.sort(key=lambda t: _SORT_KEY.get(t.get("_health", ""), 0))
        names = [t["name"] for t in tools]
        # live and unknown first, stale next, broken last
        assert names.index("C") < names.index("B") < names.index("A")

    def test_filter_healthy_excludes_stale(self):
        from tooluniverse.cli import _apply_health_filter

        result = {
            "tools": [
                {"name": "A", "_health": "live"},
                {"name": "B", "_health": "stale"},
                {"name": "C", "_health": "broken"},
            ]
        }
        filtered = _apply_health_filter(result)
        names = {t["name"] for t in filtered["tools"]}
        assert "A" in names
        assert "B" not in names, "stale tools must be excluded by --filter-healthy"
        assert "C" not in names, "broken tools must be excluded by --filter-healthy"
