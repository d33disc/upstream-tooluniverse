"""Tests for bugs found during researcher persona simulations.

Covers:
- Orphanet_get_gene_diseases: gene symbol resolution (FBN1 -> fibrillin 1)
- IntAct network: fallback to EBI Search when direct API returns 404
- SemanticScholar: error responses are proper dicts, not fake paper results
- BioGRID chemical interactions: rejects chemical-only queries
- ChEMBL_search_mechanisms: test example uses correct parameter name
"""

import json
import unittest
from unittest.mock import MagicMock, patch, PropertyMock


# ---------------------------------------------------------------------------
# Orphanet gene symbol resolution
# ---------------------------------------------------------------------------
class TestOrphanetGeneSymbolResolution(unittest.TestCase):
    """Orphanet_get_gene_diseases should accept gene symbols like FBN1."""

    def _make_tool(self):
        from tooluniverse.orphanet_tool import OrphanetTool

        config = {
            "name": "Orphanet_get_gene_diseases",
            "type": "OrphanetTool",
            "parameter": {"required": ["operation", "gene_name"]},
        }
        return OrphanetTool(config)

    @patch("tooluniverse.orphanet_tool.requests.get")
    def test_gene_symbol_resolved_to_full_name(self, mock_get):
        """When gene name search returns 404, resolve symbol and retry."""
        tool = self._make_tool()

        # First call: /genes/names/FBN1 -> 404
        resp_404 = MagicMock()
        resp_404.status_code = 404
        resp_404.raise_for_status = MagicMock(
            side_effect=__import__("requests").exceptions.HTTPError(response=resp_404)
        )

        # Second call: /genes?page=1 -> gene list with FBN1 symbol
        resp_genes = MagicMock()
        resp_genes.status_code = 200
        resp_genes.json.return_value = {
            "data": {
                "results": [
                    {"HGNC": "3603", "name": "fibrillin 1", "symbol": "FBN1"},
                    {"HGNC": "1234", "name": "other gene", "symbol": "OTHER"},
                ]
            }
        }

        # Third call: /genes/names/fibrillin%201 -> success
        resp_success = MagicMock()
        resp_success.status_code = 200
        resp_success.raise_for_status = MagicMock()
        resp_success.json.return_value = {
            "data": {
                "results": [
                    {
                        "ORPHAcode": "558",
                        "Preferred term": "Marfan syndrome",
                        "DisorderGeneAssociation": [
                            {
                                "Gene": {
                                    "Symbol": "FBN1",
                                    "name": "fibrillin 1",
                                    "GeneType": "gene with protein product",
                                    "Locus": [],
                                },
                                "DisorderGeneAssociationType": "Disease-causing germline mutation(s) in",
                                "DisorderGeneAssociationStatus": "Assessed",
                            }
                        ],
                    }
                ]
            }
        }

        mock_get.side_effect = [resp_404, resp_genes, resp_success]

        result = tool.run(
            {"operation": "get_gene_diseases", "gene_name": "FBN1"}
        )

        self.assertEqual(result["status"], "success")
        self.assertGreater(result["data"]["disease_count"], 0)
        self.assertEqual(result["data"]["diseases"][0]["genes"][0]["symbol"], "FBN1")

    @patch("tooluniverse.orphanet_tool.requests.get")
    def test_full_gene_name_works_directly(self, mock_get):
        """Full gene names like 'fibrillin' should work on first try."""
        tool = self._make_tool()

        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {
            "data": {
                "results": [
                    {
                        "ORPHAcode": "558",
                        "Preferred term": "Marfan syndrome",
                        "DisorderGeneAssociation": [],
                    }
                ]
            }
        }
        mock_get.return_value = resp

        result = tool.run(
            {"operation": "get_gene_diseases", "gene_name": "fibrillin"}
        )
        self.assertEqual(result["status"], "success")
        # Should only make 1 API call (no symbol resolution needed)
        self.assertEqual(mock_get.call_count, 1)


# ---------------------------------------------------------------------------
# IntAct network fallback to EBI Search
# ---------------------------------------------------------------------------
class TestIntActNetworkFallback(unittest.TestCase):
    """intact_get_interaction_network should fall back to EBI Search."""

    def _make_tool(self):
        from tooluniverse.intact_tool import IntActRESTTool

        config = {
            "name": "intact_get_interaction_network",
            "type": "IntActRESTTool",
            "fields": {
                "endpoint": "https://www.ebi.ac.uk/intact/ws/interaction/network/{identifier}"
            },
        }
        return IntActRESTTool(config)

    @patch("tooluniverse.intact_tool.IntActRESTTool._use_ebi_search")
    def test_network_uses_ebi_search(self, mock_ebi):
        """Network queries should route to EBI Search for reliability."""
        mock_ebi.return_value = {
            "status": "success",
            "data": [{"id": "EBI-123"}],
            "count": 1,
            "hitCount": 100,
            "interaction_ids": ["EBI-123"],
        }

        tool = self._make_tool()
        result = tool.run({"identifier": "BRCA1"})

        mock_ebi.assert_called_once()
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["count"], 0)


# ---------------------------------------------------------------------------
# SemanticScholar proper error format
# ---------------------------------------------------------------------------
class TestSemanticScholarErrorFormat(unittest.TestCase):
    """SemanticScholar should return proper error dicts, not fake paper results."""

    def _make_tool(self):
        from tooluniverse.semantic_scholar_tool import SemanticScholarTool

        config = {
            "name": "SemanticScholar_search_papers",
            "type": "SemanticScholarTool",
        }
        return SemanticScholarTool(config)

    def test_missing_query_returns_error_dict(self):
        """Missing query should return dict with status='error', not a list."""
        tool = self._make_tool()
        result = tool.run({})

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "error")
        self.assertIn("query", result["error"])

    @patch("tooluniverse.semantic_scholar_tool.request_with_retry")
    def test_api_error_returns_error_dict(self, mock_request):
        """API errors should return dict with status='error', not a fake paper list."""
        tool = self._make_tool()

        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.reason = "Too Many Requests"
        mock_request.return_value = mock_resp

        result = tool._search("test query", 5)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "error")
        self.assertIn("429", result["error"])
        self.assertTrue(result["retryable"])

    @patch("tooluniverse.semantic_scholar_tool.request_with_retry")
    def test_invalid_json_returns_error_dict(self, mock_request):
        """Invalid JSON response should return dict with status='error'."""
        tool = self._make_tool()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.side_effect = ValueError("Invalid JSON")
        mock_request.return_value = mock_resp

        result = tool._search("test query", 5)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "error")
        self.assertIn("invalid JSON", result["error"])


# ---------------------------------------------------------------------------
# BioGRID chemical interaction guard
# ---------------------------------------------------------------------------
class TestBioGRIDChemicalGuard(unittest.TestCase):
    """BioGRID_get_chemical_interactions should reject chemical-only queries."""

    def _make_tool(self):
        from tooluniverse.biogrid_tool import BioGRIDRESTTool

        config = {
            "name": "BioGRID_get_chemical_interactions",
            "type": "BioGRIDRESTTool",
            "fields": {"endpoint": "/interactions/", "return_format": "JSON"},
            "parameter": {"required": []},
        }
        return BioGRIDRESTTool(config)

    def test_chemical_only_returns_error(self):
        """Chemical-only search should return an error, not misleading PPI data."""
        tool = self._make_tool()
        result = tool.run({"chemical_names": ["Imatinib"]})

        self.assertEqual(result["status"], "error")
        self.assertIn("chemical-only", result["error"])

    def test_no_params_returns_error(self):
        """No gene or chemical names should return an error."""
        tool = self._make_tool()
        result = tool.run({})

        self.assertEqual(result["status"], "error")
        self.assertIn("gene_names", result["error"])


# ---------------------------------------------------------------------------
# ChEMBL_search_mechanisms test example parameter
# ---------------------------------------------------------------------------
class TestChEMBLMechanismsTestExample(unittest.TestCase):
    """ChEMBL_search_mechanisms test examples should use documented params."""

    def test_test_examples_use_documented_params(self):
        """Verify test_examples use drug_chembl_id, not drug_chembl_id__exact."""
        import os

        json_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "src",
            "tooluniverse",
            "data",
            "chembl_tools.json",
        )
        with open(json_path) as f:
            tools = json.load(f)

        mechanisms_tool = None
        for tool in tools:
            if tool["name"] == "ChEMBL_search_mechanisms":
                mechanisms_tool = tool
                break

        self.assertIsNotNone(mechanisms_tool, "ChEMBL_search_mechanisms not found")

        for i, example in enumerate(mechanisms_tool.get("test_examples", [])):
            self.assertNotIn(
                "drug_chembl_id__exact",
                example,
                f"test_examples[{i}] uses drug_chembl_id__exact instead of drug_chembl_id",
            )


if __name__ == "__main__":
    unittest.main()
