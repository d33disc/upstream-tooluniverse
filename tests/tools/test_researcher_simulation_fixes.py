"""Tests for bugs found during researcher persona simulations.

Covers:
- Orphanet_get_gene_diseases: gene symbol resolution (FBN1 -> fibrillin 1)
- IntAct network: fallback to EBI Search when direct API returns 404
- SemanticScholar: error responses are proper dicts, not fake paper results
- BioGRID chemical interactions: rejects chemical-only queries
- ChEMBL_search_mechanisms: test example uses correct parameter name
- ClinVar condition search: uses [dis] field tag
- Enrichr: output size limited to prevent combinatorial explosion
- PMC: include_abstract warns when no PMIDs available
- PharmGKB: example annotation ID is valid
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


# ---------------------------------------------------------------------------
# ClinVar condition search uses [dis] field tag
# ---------------------------------------------------------------------------
class TestClinVarConditionFieldTag(unittest.TestCase):
    """ClinVar condition searches must use [dis] field tag for eSearch."""

    def _make_tool(self):
        from tooluniverse.clinvar_tool import ClinVarSearchVariants

        config = {
            "name": "ClinVarSearchVariants",
            "type": "ClinVarSearchVariants",
            "fields": {},
        }
        return ClinVarSearchVariants(config)

    @patch("tooluniverse.clinvar_tool.ClinVarRESTTool._make_request")
    def test_condition_uses_dis_field_tag(self, mock_request):
        """Condition searches should append [dis] field tag."""
        mock_request.return_value = {
            "status": "success",
            "data": {
                "esearchresult": {
                    "count": "5",
                    "idlist": ["1", "2", "3", "4", "5"],
                    "querytranslation": "",
                }
            },
        }
        tool = self._make_tool()
        tool.run({"gene": "TP53", "condition": "Li-Fraumeni syndrome"})

        call_args = mock_request.call_args
        term = call_args[1]["params"]["term"] if "params" in (call_args[1] or {}) else call_args[0][1]["term"]
        self.assertIn("[dis]", term)
        self.assertIn("[gene]", term)

    @patch("tooluniverse.clinvar_tool.ClinVarRESTTool._make_request")
    def test_condition_only_uses_dis_field_tag(self, mock_request):
        """Condition-only search should use [dis] field tag."""
        mock_request.return_value = {
            "status": "success",
            "data": {
                "esearchresult": {
                    "count": "10",
                    "idlist": [],
                    "querytranslation": "",
                }
            },
        }
        tool = self._make_tool()
        tool.run({"condition": "Breast cancer"})

        call_args = mock_request.call_args
        params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("params", {})
        self.assertIn("[dis]", params["term"])
        self.assertIn('"Breast cancer"', params["term"])


# ---------------------------------------------------------------------------
# GxA gene_id client-side filter uses exact match
# ---------------------------------------------------------------------------
class TestGxAGeneFilter(unittest.TestCase):
    """GxA_get_experiment_expression should filter genes by exact ID match."""

    def _make_tool(self):
        from tooluniverse.gxa_tool import GxATool

        config = {
            "name": "GxA_get_experiment_expression",
            "type": "GxATool",
            "fields": {"endpoint": "get_experiment_expression"},
        }
        return GxATool(config)

    @patch("tooluniverse.gxa_tool.requests.get")
    def test_gene_id_filters_exactly(self, mock_get):
        """gene_id filter should match only the exact gene, not substrings."""
        tool = self._make_tool()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "experiment": {"description": "Test experiment"},
            "columnHeaders": [
                {"assayGroupId": "g1", "factorValue": "brain", "factorValueOntologyTermId": "", "assayGroupSummary": {"replicates": 3}},
            ],
            "profiles": {
                "rows": [
                    {"id": "ENSG00000130234", "name": "ACE2", "expressions": [{"value": 5.0}]},
                    {"id": "ENSG00000999999", "name": "OTHER", "expressions": [{"value": 3.0}]},
                    {"id": "ENSG00000130234X", "name": "NOTACE2", "expressions": [{"value": 1.0}]},
                ]
            },
        }
        mock_get.return_value = mock_resp

        result = tool.run({"experiment_accession": "E-MTAB-2836", "gene_id": "ENSG00000130234"})

        profiles = result["data"]["gene_profiles"]
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["gene_id"], "ENSG00000130234")


# ---------------------------------------------------------------------------
# Enrichr output size limit
# ---------------------------------------------------------------------------
class TestEnrichrOutputLimit(unittest.TestCase):
    """Enrichr should limit path output to prevent combinatorial explosion."""

    def _make_tool(self):
        from tooluniverse.enrichr_tool import EnrichrTool

        config = {
            "name": "enrichr_gene_enrichment_analysis",
            "type": "EnrichrTool",
        }
        return EnrichrTool(config)

    @patch("tooluniverse.enrichr_tool.EnrichrTool.get_official_gene_name",
           side_effect=lambda g: g)
    @patch("tooluniverse.enrichr_tool.EnrichrTool.submit_gene_list",
           return_value="12345")
    @patch("tooluniverse.enrichr_tool.EnrichrTool.get_enrichment_results")
    def test_paths_limited_to_prevent_explosion(self, mock_enrich, mock_submit, mock_gene):
        """ranked_paths and connections should be truncated."""
        # Mock enrichment results with many terms to create many paths
        mock_enrich.return_value = {
            "TestLib": [
                # [rank, term_name, p-value, z-score, combined_score, genes, ...]
                [1, f"Term_{i}", 0.001, -2.0, 10.0 - i * 0.1, ["GENE1", "GENE2"], 0, 0, 0]
                for i in range(30)
            ]
        }
        tool = self._make_tool()
        connected_path, connections = tool.enrichr_api(
            ["GENE1", "GENE2"], ["TestLib"]
        )

        # connected_path limited to 20
        self.assertLessEqual(len(connected_path), 20)

        # Each connection limited to 5 paths
        for key, paths in connections.items():
            self.assertLessEqual(len(paths), 5)


# ---------------------------------------------------------------------------
# PMC include_abstract warning
# ---------------------------------------------------------------------------
class TestPMCAbstractWarning(unittest.TestCase):
    """PMC should warn when include_abstract fails due to missing PMIDs."""

    def _make_tool(self):
        from tooluniverse.pmc_tool import PMCTool

        config = {"name": "PMC_search_papers", "type": "PMCTool"}
        return PMCTool(config)

    @patch("tooluniverse.pmc_tool.request_with_retry")
    def test_abstract_note_when_no_pmids(self, mock_request):
        """When no PMIDs available, results should have abstract_note."""
        tool = self._make_tool()

        # Mock search response
        search_resp = MagicMock()
        search_resp.status_code = 200
        search_resp.raise_for_status = MagicMock()
        search_resp.json.return_value = {
            "esearchresult": {"idlist": ["123456"]}
        }

        # Mock summary response (XML with no PMID in ArticleIds)
        summary_resp = MagicMock()
        summary_resp.status_code = 200
        summary_resp.raise_for_status = MagicMock()
        summary_resp.text = """<?xml version="1.0"?>
<eSummaryResult>
  <DocSum>
    <Id>123456</Id>
    <Item Name="Title" Type="String">Test Article</Item>
    <Item Name="ArticleIds" Type="List">
      <Item Name="pmc" Type="String">PMC123456</Item>
    </Item>
  </DocSum>
</eSummaryResult>"""

        mock_request.side_effect = [search_resp, summary_resp]

        results = tool._search("test query", limit=5, include_abstract=True)

        self.assertEqual(len(results), 1)
        self.assertIn("abstract_note", results[0])
        self.assertIn("PubMed_search_articles", results[0]["abstract_note"])


# ---------------------------------------------------------------------------
# PharmGKB example annotation ID validity
# ---------------------------------------------------------------------------
class TestPharmGKBExampleID(unittest.TestCase):
    """PharmGKB description example IDs should match test_examples."""

    def test_description_example_id_matches_test_examples(self):
        """The example ID in the description should be a valid one."""
        import os

        json_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "src",
            "tooluniverse",
            "data",
            "pharmgkb_tools.json",
        )
        with open(json_path) as f:
            tools = json.load(f)

        for tool in tools:
            if tool["name"] != "PharmGKB_get_clinical_annotations":
                continue
            # Check the annotation_id description example matches a known-good ID
            ann_param = tool["parameter"]["properties"].get("annotation_id", {})
            desc = ann_param.get("description", "")
            # The example ID 1449309855 was broken; should now be 1447954390
            self.assertNotIn("1449309855", desc)
            self.assertIn("1447954390", desc)
            break


# ---------------------------------------------------------------------------
# ChEMBL target_chembl_id maps to __exact API param
# ---------------------------------------------------------------------------
class TestChEMBLTargetFilter(unittest.TestCase):
    """ChEMBL_search_mechanisms should map target_chembl_id to __exact."""

    def _make_tool(self):
        from tooluniverse.chem_tool import ChEMBLRESTTool

        config = {
            "name": "ChEMBL_search_mechanisms",
            "type": "ChEMBLRESTTool",
            "fields": {"endpoint": "mechanism"},
            "parameter": {"required": []},
        }
        return ChEMBLRESTTool(config)

    def test_target_chembl_id_mapped_to_exact(self):
        """target_chembl_id should be mapped to target_chembl_id__exact in params."""
        tool = self._make_tool()
        params = tool._build_params({"target_chembl_id": "CHEMBL4096", "limit": 5})

        self.assertIn("target_chembl_id__exact", params)
        self.assertEqual(params["target_chembl_id__exact"], "CHEMBL4096")
        # Should NOT have bare target_chembl_id (it's in the exclusion list)
        self.assertNotIn("target_chembl_id", params)

    def test_assay_chembl_id_mapped_to_exact(self):
        """assay_chembl_id should be mapped to assay_chembl_id__exact in params."""
        tool = self._make_tool()
        params = tool._build_params({"assay_chembl_id": "CHEMBL1000001", "limit": 5})

        self.assertIn("assay_chembl_id__exact", params)
        self.assertEqual(params["assay_chembl_id__exact"], "CHEMBL1000001")


# ---------------------------------------------------------------------------
# GTEx gene ID resolution and dataset defaults
# ---------------------------------------------------------------------------
class TestGTExGeneIdResolution(unittest.TestCase):
    """GTEx V2 should resolve gene symbols to versioned GENCODE IDs."""

    def _make_tool(self):
        from tooluniverse.gtex_v2_tool import GTExV2Tool

        config = {
            "name": "GTEx_get_median_gene_expression",
            "type": "GTExV2Tool",
            "parameter": {"required": ["operation"]},
        }
        return GTExV2Tool(config)

    @patch("tooluniverse.gtex_v2_tool.requests.get")
    def test_gene_symbol_resolved_to_versioned_id(self, mock_get):
        """Gene symbols like TP53 should be resolved to versioned GENCODE IDs."""
        tool = self._make_tool()

        # First call: /reference/gene resolves TP53 -> ENSG00000141510.18
        resolve_resp = MagicMock()
        resolve_resp.status_code = 200
        resolve_resp.json.return_value = {
            "data": [{"gencodeId": "ENSG00000141510.18", "geneSymbol": "TP53"}]
        }

        # Second call: /expression/medianGeneExpression with resolved ID
        expr_resp = MagicMock()
        expr_resp.status_code = 200
        expr_resp.json.return_value = {
            "data": [
                {
                    "gencodeId": "ENSG00000141510.18",
                    "tissueSiteDetailId": "Liver",
                    "median": 15.2,
                }
            ],
            "paging_info": {"numberOfPages": 1},
        }

        mock_get.side_effect = [resolve_resp, expr_resp]

        result = tool.run({
            "operation": "get_median_gene_expression",
            "gencode_id": "TP53",
        })

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["num_results"], 1)
        # Verify the resolution call was made
        first_call_url = mock_get.call_args_list[0][0][0]
        self.assertIn("/reference/gene", first_call_url)

    @patch("tooluniverse.gtex_v2_tool.requests.get")
    def test_versioned_id_not_re_resolved(self, mock_get):
        """Already versioned IDs (containing '.') should not trigger resolution."""
        tool = self._make_tool()

        expr_resp = MagicMock()
        expr_resp.status_code = 200
        expr_resp.json.return_value = {
            "data": [{"gencodeId": "ENSG00000141510.18", "median": 10.0}],
            "paging_info": {},
        }
        mock_get.return_value = expr_resp

        result = tool.run({
            "operation": "get_median_gene_expression",
            "gencode_id": "ENSG00000141510.18",
        })

        self.assertEqual(result["status"], "success")
        # Only 1 call (expression), no resolution call
        self.assertEqual(mock_get.call_count, 1)
        self.assertIn("medianGeneExpression", mock_get.call_args[0][0])

    def test_gene_expression_defaults_to_gtex_v8(self):
        """_get_gene_expression should default to gtex_v8 not gtex_v10."""
        tool = self._make_tool()
        # Check via the handler directly — dataset_id default
        import inspect
        source = inspect.getsource(tool._get_gene_expression)
        self.assertIn("gtex_v8", source)

    def test_median_expression_defaults_to_gtex_v8(self):
        """_get_median_gene_expression should default to gtex_v8."""
        tool = self._make_tool()
        import inspect
        source = inspect.getsource(tool._get_median_gene_expression)
        self.assertIn("gtex_v8", source)


class TestGTExWrapperDefaults(unittest.TestCase):
    """GTEx wrapper functions should default to gtex_v8."""

    def test_median_wrapper_defaults_v8(self):
        """GTEx_get_median_gene_expression wrapper should default to gtex_v8."""
        import inspect
        from tooluniverse.tools.GTEx_get_median_gene_expression import (
            GTEx_get_median_gene_expression,
        )
        sig = inspect.signature(GTEx_get_median_gene_expression)
        default = sig.parameters["dataset_id"].default
        self.assertEqual(default, "gtex_v8")

    def test_gene_expression_wrapper_defaults_v8(self):
        """GTEx_get_gene_expression wrapper should default to gtex_v8."""
        import inspect
        from tooluniverse.tools.GTEx_get_gene_expression import (
            GTEx_get_gene_expression,
        )
        sig = inspect.signature(GTEx_get_gene_expression)
        default = sig.parameters["dataset_id"].default
        self.assertEqual(default, "gtex_v8")


if __name__ == "__main__":
    unittest.main()
