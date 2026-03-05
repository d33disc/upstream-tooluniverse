"""Tests for literature search tool fixes (Feature-81B).

Covers:
- Feature-81B-001: PubMed PMCID double-prefix
- Feature-81B-002: PubMed limit=0 honoured
- Feature-81B-003: ArXiv quoted-phrase query building
- Feature-81B-004: OpenAlex empty-search validation
- Feature-81B-005: ArXiv return_schema oneOf (error vs array)
"""

import json
import re
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Feature-81B-001: PubMed PMCID double-prefix
# ---------------------------------------------------------------------------
class TestPubMedPMCID(unittest.TestCase):
    """Ensure PMC IDs are not double-prefixed (PMCPMC...)."""

    def _make_tool(self):
        from tooluniverse.pubmed_tool import PubMedRESTTool

        config = {
            "name": "PubMed_search_articles",
            "type": "PubMedRESTTool",
            "fields": {
                "endpoint": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                "method": "GET",
                "db": "pubmed",
                "retmode": "json",
            },
            "parameter": {"type": "object", "properties": {}, "required": []},
        }
        return PubMedRESTTool(config)

    def test_pmcid_already_prefixed(self):
        """When esummary returns value='PMC12345', result should be 'PMC12345' not 'PMCPMC12345'."""
        tool = self._make_tool()

        # Simulate a batch summary response where PMC value already has prefix
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "result": {
                "uids": ["12345"],
                "12345": {
                    "uid": "12345",
                    "pubdate": "2024 Jan",
                    "title": "Test Article",
                    "authors": [{"name": "Smith J"}],
                    "fulljournalname": "Test Journal",
                    "elocationid": "doi: 10.1234/test",
                    "pubtype": ["Journal Article"],
                    "articleids": [
                        {"idtype": "pubmed", "value": "12345"},
                        {"idtype": "pmc", "value": "PMC9999999"},
                    ],
                },
            }
        }

        with patch.object(tool, "_enforce_rate_limit"):
            with patch(
                "tooluniverse.pubmed_tool.request_with_retry", return_value=mock_resp
            ):
                result = tool._fetch_summaries(["12345"])

        self.assertEqual(result["status"], "success")
        article = result["data"][0]
        self.assertEqual(article["pmcid"], "PMC9999999")
        self.assertIn("/PMC9999999/", article["pmc_url"])
        self.assertNotIn("PMCPMC", article["pmcid"])

    def test_pmcid_numeric_only(self):
        """When esummary returns value='9999999' (no prefix), result should be 'PMC9999999'."""
        tool = self._make_tool()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "result": {
                "uids": ["12345"],
                "12345": {
                    "uid": "12345",
                    "pubdate": "2024 Jan",
                    "title": "Test Article",
                    "authors": [],
                    "fulljournalname": "Test Journal",
                    "elocationid": "",
                    "pubtype": [],
                    "articleids": [
                        {"idtype": "pmc", "value": "9999999"},
                    ],
                },
            }
        }

        with patch.object(tool, "_enforce_rate_limit"):
            with patch(
                "tooluniverse.pubmed_tool.request_with_retry", return_value=mock_resp
            ):
                result = tool._fetch_summaries(["12345"])

        self.assertEqual(result["status"], "success")
        article = result["data"][0]
        self.assertEqual(article["pmcid"], "PMC9999999")


# ---------------------------------------------------------------------------
# Feature-81B-002: PubMed limit=0 honoured
# ---------------------------------------------------------------------------
class TestPubMedLimit(unittest.TestCase):
    """Ensure limit=0 sends retmax=0 instead of being silently ignored."""

    def _make_tool(self):
        from tooluniverse.pubmed_tool import PubMedRESTTool

        config = {
            "name": "PubMed_search_articles",
            "type": "PubMedRESTTool",
            "fields": {
                "endpoint": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                "method": "GET",
                "db": "pubmed",
                "retmode": "json",
            },
            "parameter": {"type": "object", "properties": {}, "required": []},
        }
        return PubMedRESTTool(config)

    def test_limit_zero_sets_retmax(self):
        """limit=0 should set retmax=0, not fall through to NCBI default."""
        tool = self._make_tool()
        params = tool._build_params({"query": "test", "limit": 0})
        self.assertIn("retmax", params)
        self.assertEqual(params["retmax"], 0)

    def test_limit_none_omits_retmax(self):
        """limit=None should not set retmax (use NCBI default)."""
        tool = self._make_tool()
        params = tool._build_params({"query": "test"})
        self.assertNotIn("retmax", params)

    def test_limit_positive(self):
        """limit=5 should set retmax=5."""
        tool = self._make_tool()
        params = tool._build_params({"query": "test", "limit": 5})
        self.assertEqual(params["retmax"], 5)


# ---------------------------------------------------------------------------
# Feature-81B-003: ArXiv quoted-phrase query building
# ---------------------------------------------------------------------------
class TestArXivQueryBuilding(unittest.TestCase):
    """Ensure _build_search_query handles quoted phrases and special chars."""

    def _make_tool(self):
        from tooluniverse.arxiv_tool import ArXivTool

        config = {
            "name": "ArXiv_search_papers",
            "type": "ArXivTool",
            "parameter": {"type": "object", "properties": {}, "required": []},
        }
        return ArXivTool(config)

    def test_quoted_phrase_preserved(self):
        """Quoted phrases should be kept intact, not split into individual words."""
        tool = self._make_tool()
        result = tool._build_search_query('"protein folding" prediction')
        # The quoted phrase should appear as a single token
        self.assertIn('all:"protein folding"', result)
        self.assertIn("all:prediction", result)
        # Should NOT have broken quotes like all:"protein
        self.assertNotIn('all:"protein AND', result)

    def test_single_word(self):
        """Single word should become all:<word>."""
        tool = self._make_tool()
        result = tool._build_search_query("CRISPR")
        self.assertEqual(result, "all:CRISPR")

    def test_hyphenated_terms(self):
        """Hyphenated terms like 'SARS-CoV-2' should stay as one token."""
        tool = self._make_tool()
        result = tool._build_search_query("SARS-CoV-2 spike protein")
        self.assertIn("all:SARS-CoV-2", result)

    def test_prefix_passthrough(self):
        """Queries with arXiv prefixes should pass through unchanged."""
        tool = self._make_tool()
        result = tool._build_search_query("au:Smith ti:quantum")
        self.assertEqual(result, "au:Smith ti:quantum")

    def test_boolean_passthrough(self):
        """Queries with AND/OR should pass through unchanged."""
        tool = self._make_tool()
        result = tool._build_search_query("quantum AND computing")
        self.assertEqual(result, "quantum AND computing")

    def test_multi_word_and_joined(self):
        """Multi-word queries without quotes should AND-join each word."""
        tool = self._make_tool()
        result = tool._build_search_query("machine learning transformers")
        self.assertEqual(
            result, "all:machine AND all:learning AND all:transformers"
        )


# ---------------------------------------------------------------------------
# Feature-81B-004: OpenAlex empty-search validation
# ---------------------------------------------------------------------------
class TestOpenAlexEmptySearch(unittest.TestCase):
    """Ensure empty search queries are rejected, not sent to OpenAlex."""

    def test_openalex_tool_empty_search(self):
        """OpenAlexTool.run() should return error for empty search_keywords."""
        from tooluniverse.openalex_tool import OpenAlexTool

        config = {
            "name": "openalex_literature_search",
            "type": "OpenAlexTool",
            "parameter": {"type": "object", "properties": {}, "required": []},
        }
        tool = OpenAlexTool(config)
        result = tool.run({"search_keywords": ""})
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_openalex_tool_none_search(self):
        """OpenAlexTool.run() should return error when no search is provided."""
        from tooluniverse.openalex_tool import OpenAlexTool

        config = {
            "name": "openalex_literature_search",
            "type": "OpenAlexTool",
            "parameter": {"type": "object", "properties": {}, "required": []},
        }
        tool = OpenAlexTool(config)
        result = tool.run({})
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_openalex_rest_empty_search_stripped(self):
        """OpenAlexRESTTool should strip empty 'search' from params."""
        from tooluniverse.openalex_tool import OpenAlexRESTTool

        config = {
            "name": "openalex_search_works",
            "type": "OpenAlexRESTTool",
            "fields": {
                "path": "/works",
                "path_params": [],
                "param_map": {"per_page": "per-page"},
                "default_params": {},
            },
            "parameter": {"type": "object", "properties": {}, "required": []},
        }
        tool = OpenAlexRESTTool(config)
        _, params = tool._build_url_and_params({"search": "", "per_page": 5})
        # Empty search should be dropped from params
        self.assertNotIn("search", params)


# ---------------------------------------------------------------------------
# Feature-81B-005: ArXiv return_schema uses oneOf
# ---------------------------------------------------------------------------
class TestArXivReturnSchema(unittest.TestCase):
    """Ensure the ArXiv tool JSON schema has oneOf for array/error responses."""

    def test_schema_has_oneof(self):
        """arxiv_tools.json return_schema should use oneOf pattern."""
        import os

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "src",
            "tooluniverse",
            "data",
            "arxiv_tools.json",
        )
        with open(schema_path) as f:
            tools = json.load(f)

        search_tool = next(t for t in tools if t["name"] == "ArXiv_search_papers")
        return_schema = search_tool["return_schema"]

        # Must have oneOf with both array (success) and object (error) variants
        self.assertIn("oneOf", return_schema)
        types = [s.get("type") for s in return_schema["oneOf"]]
        self.assertIn("array", types)
        self.assertIn("object", types)


if __name__ == "__main__":
    unittest.main()
