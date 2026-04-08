#!/usr/bin/env python3
"""
Unit tests for Semantic Scholar tool stability and error shaping.
"""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tooluniverse.semantic_scholar_tool import SemanticScholarTool


class _FakeResponse:
    def __init__(self, status_code=200, payload=None, reason=""):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.reason = reason
        self.headers = {}

    def json(self):
        return self._payload


@pytest.mark.unit
def test_semantic_scholar_returns_list_on_error(monkeypatch):
    tool = SemanticScholarTool({"name": "SemanticScholar_search_papers"})
    monkeypatch.setattr(tool, "_enforce_rate_limit", lambda has_api_key: None)

    def fake_request_with_retry(*args, **kwargs):
        return _FakeResponse(status_code=429, reason="Too Many Requests")

    monkeypatch.setattr(
        "tooluniverse.semantic_scholar_tool.request_with_retry", fake_request_with_retry
    )

    result = tool.run({"query": "x", "limit": 1})

    # run() returns envelope dict with status/error keys
    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "429" in result["error"]
    assert result["retryable"] is True


@pytest.mark.unit
def test_semantic_scholar_include_abstract_enriches_missing_abstract(monkeypatch):
    tool = SemanticScholarTool({"name": "SemanticScholar_search_papers"})
    monkeypatch.setattr(tool, "_enforce_rate_limit", lambda has_api_key: None)

    def fake_request_with_retry(session, method, url, *, params=None, **kwargs):
        if url.endswith("/paper/search"):
            return _FakeResponse(
                status_code=200,
                payload={
                    "data": [
                        {
                            "paperId": "abc",
                            "externalIds": {},
                            "title": "T",
                            "abstract": None,
                            "year": 2024,
                            "venue": "V",
                            "url": "https://example.test/paper",
                            "authors": [{"name": "A"}],
                            "citationCount": 1,
                            "referenceCount": 2,
                            "isOpenAccess": True,
                            "openAccessPdf": {},
                        }
                    ]
                },
            )
        if url.endswith("/paper/abc"):
            return _FakeResponse(
                status_code=200,
                payload={
                    "abstract": "Filled abstract.",
                    "externalIds": {"DOI": "10.1000/example"},
                    "openAccessPdf": {"url": "https://example.test/pdf"},
                },
            )
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(
        "tooluniverse.semantic_scholar_tool.request_with_retry", fake_request_with_retry
    )

    result = tool.run({"query": "x", "limit": 1, "include_abstract": True})

    # run() returns envelope dict with data list
    assert isinstance(result, dict)
    assert result["status"] == "success"
    papers = result["data"]
    assert len(papers) == 1
    assert papers[0]["abstract"] == "Filled abstract."
    assert papers[0]["doi"] == "10.1000/example"
    assert papers[0]["doi_url"] == "https://doi.org/10.1000/example"
    assert papers[0]["open_access_pdf_url"] == "https://example.test/pdf"


# =====================================================================
# DVS-FORK-PATCH tests: semantic-scholar-rate-limit
#
# Guard the fork-specific behavior documented in semantic_scholar_tool.py
# under the `DVS-FORK-PATCH` sentinel block. If these tests disappear or
# start passing against upstream's constant-branch throttle, the rate
# limit patch has been lost during an upstream merge — re-apply it.
# =====================================================================


def _fresh_tool(monkeypatch):
    """Reset the class-level last-request clock so timing tests are deterministic."""
    SemanticScholarTool._last_request_time = 0.0
    return SemanticScholarTool({"name": "SemanticScholar_search_papers"})


@pytest.mark.unit
def test_rate_limit_default_is_safe_even_with_api_key(monkeypatch):
    """Personal API keys are 1 req/sec; setting the key must NOT lower the floor."""
    monkeypatch.delenv("SEMANTIC_SCHOLAR_MIN_INTERVAL", raising=False)
    monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "sk-test-personal-tier")
    tool = _fresh_tool(monkeypatch)

    sleeps: list[float] = []
    monkeypatch.setattr(
        "tooluniverse.semantic_scholar_tool.time.sleep", lambda s: sleeps.append(s)
    )

    # Two back-to-back calls: first seeds the clock, second must sleep ~1.05s.
    tool._enforce_rate_limit(has_api_key=True)
    tool._enforce_rate_limit(has_api_key=True)

    assert sleeps, "second call should have slept"
    # Allow small scheduling slack; the key point is we are NOT in the 0.02s branch.
    assert sleeps[-1] >= 1.0, (
        f"expected >=1.0s sleep under default floor, got {sleeps[-1]:.4f}s "
        "(upstream 0.02s floor may have leaked back in — check DVS-FORK-PATCH block)"
    )


@pytest.mark.unit
def test_rate_limit_env_override_allows_faster_tier(monkeypatch):
    """Commercial-tier key holders can opt down via SEMANTIC_SCHOLAR_MIN_INTERVAL."""
    monkeypatch.setenv("SEMANTIC_SCHOLAR_MIN_INTERVAL", "0.02")
    tool = _fresh_tool(monkeypatch)

    sleeps: list[float] = []
    monkeypatch.setattr(
        "tooluniverse.semantic_scholar_tool.time.sleep", lambda s: sleeps.append(s)
    )

    tool._enforce_rate_limit(has_api_key=True)
    tool._enforce_rate_limit(has_api_key=True)

    assert sleeps, "second call should have slept"
    assert sleeps[-1] < 0.1, (
        f"override to 0.02s should cap sleep below 0.1s, got {sleeps[-1]:.4f}s"
    )


@pytest.mark.unit
def test_rate_limit_malformed_override_fails_safe(monkeypatch):
    """Garbage in SEMANTIC_SCHOLAR_MIN_INTERVAL must not silently disable throttling."""
    monkeypatch.setenv("SEMANTIC_SCHOLAR_MIN_INTERVAL", "not-a-number")
    tool = _fresh_tool(monkeypatch)

    sleeps: list[float] = []
    monkeypatch.setattr(
        "tooluniverse.semantic_scholar_tool.time.sleep", lambda s: sleeps.append(s)
    )

    tool._enforce_rate_limit(has_api_key=False)
    tool._enforce_rate_limit(has_api_key=False)

    assert sleeps and sleeps[-1] >= 1.0, (
        f"malformed override should fall back to 1.05s, got {sleeps[-1] if sleeps else 'no sleep'}"
    )


@pytest.mark.unit
def test_rate_limit_no_sleep_when_interval_already_elapsed(monkeypatch):
    """If enough wall time has passed, no sleep is needed."""
    monkeypatch.delenv("SEMANTIC_SCHOLAR_MIN_INTERVAL", raising=False)
    tool = _fresh_tool(monkeypatch)
    # Pretend the last request was ages ago.
    SemanticScholarTool._last_request_time = time.time() - 10.0

    sleeps: list[float] = []
    monkeypatch.setattr(
        "tooluniverse.semantic_scholar_tool.time.sleep", lambda s: sleeps.append(s)
    )

    tool._enforce_rate_limit(has_api_key=True)

    assert not sleeps, f"expected no sleep, got {sleeps}"
