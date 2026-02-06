#!/usr/bin/env python3
"""
Unit tests for EuropePMC_get_fulltext_snippets (fullTextXML snippet extraction).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tooluniverse.europe_pmc_tool import EuropePMCFullTextSnippetsTool


class _FakeResponse:
    def __init__(self, *, status_code=200, text="", url=""):
        self.status_code = status_code
        self.text = text
        self.url = url or "https://example.test"


@pytest.mark.unit
def test_europe_pmc_fulltext_snippets_finds_terms_in_xml(monkeypatch):
    tool = EuropePMCFullTextSnippetsTool({"name": "EuropePMC_get_fulltext_snippets"})

    xml_payload = """<?xml version="1.0" encoding="UTF-8"?>
<article>
  <front>
    <article-meta>
      <title-group>
        <article-title>A. baumannii readily evolved resistance to meropenem, ciprofloxacin, and gentamicin</article-title>
      </title-group>
    </article-meta>
  </front>
  <body>
    <sec>
      <title>A. lwoffii only evolved resistance to ciprofloxacin</title>
      <p>Selection experiments were set up.</p>
    </sec>
  </body>
</article>
"""

    def fake_request_with_retry(session, method, url, *, timeout=None, max_attempts=None, **kwargs):
        assert url.endswith("/PMC11237425/fullTextXML")
        return _FakeResponse(status_code=200, text=xml_payload, url=url)

    monkeypatch.setattr(
        "tooluniverse.europe_pmc_tool.request_with_retry", fake_request_with_retry
    )

    out = tool.run(
        {
            "pmcid": "PMC11237425",
            "terms": ["ciprofloxacin", "meropenem", "lwoffii"],
            "window_chars": 60,
            "max_snippets_per_term": 2,
            "max_total_chars": 2000,
        }
    )

    assert out["status"] == "success"
    assert out["snippets_count"] >= 3
    assert any("evolved resistance to ciprofloxacin" in s["snippet"].lower() for s in out["snippets"])

