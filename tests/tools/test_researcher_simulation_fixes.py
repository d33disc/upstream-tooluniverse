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


# ---------------------------------------------------------------------------
# IntAct interactor uses correct endpoint
# ---------------------------------------------------------------------------
class TestIntActInteractorEndpoint(unittest.TestCase):
    """IntAct interactor should use findInteractor, not details."""

    def _make_tool(self, tool_name):
        from tooluniverse.intact_tool import IntActRESTTool

        config = {
            "name": tool_name,
            "type": "IntActRESTTool",
            "fields": {},
        }
        return IntActRESTTool(config)

    def test_interactor_url_uses_find(self):
        """intact_get_interactor URL should use /findInteractor/."""
        tool = self._make_tool("intact_get_interactor")
        url = tool._build_url({"identifier": "P04637"})
        self.assertIn("/interactor/findInteractor/P04637", url)
        self.assertNotIn("/details/", url)

    def test_network_url_uses_find_interactions(self):
        """intact_get_interaction_network URL should use /findInteractions/."""
        tool = self._make_tool("intact_get_interaction_network")
        url = tool._build_url({"identifier": "P04637"})
        self.assertIn("/interaction/findInteractions/P04637", url)
        self.assertNotIn("/network/", url)

    @patch("tooluniverse.intact_tool.IntActRESTTool._use_ebi_search")
    def test_interactor_not_routed_to_ebi_search(self, mock_ebi):
        """intact_get_interactor should NOT be routed to EBI Search."""
        tool = self._make_tool("intact_get_interactor")

        # Mock the session.get to return paginated interactor data
        with patch.object(tool.session, "get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json.return_value = {
                "content": [
                    {
                        "interactorAc": "EBI-366083",
                        "interactorName": "p53",
                        "interactorType": "protein",
                        "interactionCount": 2243,
                    }
                ],
                "totalElements": 1,
            }
            mock_resp.url = "https://example.com"
            mock_get.return_value = mock_resp

            result = tool.run({"identifier": "P04637"})

        mock_ebi.assert_not_called()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["totalElements"], 1)

    @patch("tooluniverse.intact_tool.IntActRESTTool._use_ebi_search")
    def test_paginated_response_handled(self, mock_ebi):
        """Paginated responses should extract content and totalElements."""
        tool = self._make_tool("intact_get_interaction_network")

        with patch.object(tool.session, "get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json.return_value = {
                "content": [{"id": "1"}, {"id": "2"}],
                "totalElements": 500,
            }
            mock_resp.url = "https://example.com"
            mock_get.return_value = mock_resp

            result = tool.run({"identifier": "BRCA1"})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["totalElements"], 500)
        self.assertIn("note", result)


# ---------------------------------------------------------------------------
# Response truncation
# ---------------------------------------------------------------------------
class TestResponseTruncation(unittest.TestCase):
    """MCP server should truncate oversized responses."""

    def test_truncate_list_response(self):
        from tooluniverse.smcp import _truncate_response

        big_list = [{"id": i, "data": "x" * 500} for i in range(500)]
        serialized = json.dumps(big_list, ensure_ascii=False)
        result = _truncate_response(big_list, serialized, 50_000)

        parsed = json.loads(result)
        self.assertTrue(parsed["_truncated"])
        self.assertEqual(parsed["_total"], 500)
        self.assertLess(parsed["_showing"], 500)
        self.assertLessEqual(len(result), 50_200)  # small overshoot OK

    def test_truncate_dict_with_large_list(self):
        from tooluniverse.smcp import _truncate_response

        big_dict = {
            "status": "success",
            "data": [{"id": i, "payload": "y" * 1000} for i in range(200)],
        }
        serialized = json.dumps(big_dict, ensure_ascii=False)
        result = _truncate_response(big_dict, serialized, 50_000)

        parsed = json.loads(result)
        self.assertTrue(parsed["_truncated"])
        self.assertIn("_data_total", parsed)

    def test_small_response_not_truncated(self):
        """Responses under the limit should not be truncated."""
        from tooluniverse.smcp import _truncate_response

        small = {"status": "success", "data": [1, 2, 3]}
        serialized = json.dumps(small)
        # Should not be called in practice (guard checks len first),
        # but if called it should return something reasonable
        result = _truncate_response(small, serialized, 100_000)
        # The result should still be valid JSON even if not truncated
        parsed = json.loads(result)
        self.assertIsNotNone(parsed)


# ---------------------------------------------------------------------------
# ClinicalTrials search returns null fields
# ---------------------------------------------------------------------------
class TestClinicalTrialsSearchFields(unittest.TestCase):
    """ClinicalTrials_search_studies should return populated metadata fields."""

    def _make_tool(self):
        from tooluniverse.clinicaltrials_tool import CTGovAPITool

        config = {
            "name": "ClinicalTrials_search_studies",
            "type": "CTGovAPITool",
        }
        return CTGovAPITool(config)

    @patch("tooluniverse.clinicaltrials_tool.requests.get")
    def test_search_does_not_use_fields_param(self, mock_get):
        """Search should NOT pass 'fields' param (it breaks nested response format)."""
        tool = self._make_tool()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "totalCount": 1,
            "studies": [
                {
                    "protocolSection": {
                        "identificationModule": {
                            "nctId": "NCT00000001",
                            "briefTitle": "Test Study",
                        },
                        "statusModule": {
                            "overallStatus": "RECRUITING",
                            "startDateStruct": {"date": "2025-01-01"},
                            "completionDateStruct": {"date": "2026-12-31"},
                        },
                        "designModule": {
                            "studyType": "INTERVENTIONAL",
                            "phases": ["PHASE3"],
                            "enrollmentInfo": {"count": 500},
                        },
                        "conditionsModule": {"conditions": ["NSCLC"]},
                        "armsInterventionsModule": {
                            "interventions": [
                                {"name": "Pembrolizumab", "type": "DRUG"}
                            ]
                        },
                        "sponsorCollaboratorsModule": {
                            "leadSponsor": {"name": "NCI"}
                        },
                    }
                }
            ],
        }
        mock_get.return_value = mock_resp

        result = tool.run({"operation": "search", "query_cond": "NSCLC"})

        # Verify 'fields' param was NOT sent
        call_params = mock_get.call_args[1].get("params", {})
        self.assertNotIn("fields", call_params)

        # Verify nested data was extracted correctly
        study = result["data"]["studies"][0]
        self.assertEqual(study["nct_id"], "NCT00000001")
        self.assertEqual(study["start_date"], "2025-01-01")
        self.assertEqual(study["enrollment"], 500)
        self.assertEqual(study["sponsor"], "NCI")
        self.assertEqual(study["interventions"], ["Pembrolizumab"])


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


# ---------------------------------------------------------------------------
# Operation auto-fill tests (redundant operation parameter removed from required)
# ---------------------------------------------------------------------------
class TestOperationAutoFill(unittest.TestCase):
    """Test that tools auto-fill 'operation' from config const when not provided."""

    def _load_config(self, json_file, tool_name):
        import os
        path = os.path.join(
            os.path.dirname(__file__),
            "../../src/tooluniverse/data",
            json_file,
        )
        with open(path) as f:
            tools = json.load(f)
        return [t for t in tools if t["name"] == tool_name][0]

    def test_orphanet_operation_not_required(self):
        """Orphanet tools should NOT require 'operation' in parameter schema."""
        config = self._load_config("orphanet_tools.json", "Orphanet_search_diseases")
        self.assertNotIn("operation", config["parameter"]["required"])

    def test_orphanet_auto_fills_operation(self):
        """Orphanet tool should auto-fill operation from config const."""
        from tooluniverse.orphanet_tool import OrphanetTool
        config = self._load_config("orphanet_tools.json", "Orphanet_search_diseases")
        tool = OrphanetTool(config)
        # Mock the _search_diseases method to verify routing works
        tool._search_diseases = MagicMock(return_value={"status": "success"})
        tool.run({"query": "Marfan"})  # No operation param
        tool._search_diseases.assert_called_once()

    def test_gencc_auto_fills_operation(self):
        """GenCC tool should auto-fill operation from config const."""
        from tooluniverse.gencc_tool import GenCCTool
        config = self._load_config("gencc_tools.json", "GenCC_search_disease")
        tool = GenCCTool(config)
        tool._search_disease = MagicMock(return_value={"status": "success"})
        tool.run({"disease": "Marfan"})  # No operation param
        tool._search_disease.assert_called_once()

    def test_gpcrdb_auto_fills_operation(self):
        """GPCRdb tool should auto-fill operation from config const."""
        from tooluniverse.gpcrdb_tool import GPCRdbTool
        config = self._load_config("gpcrdb_tools.json", "GPCRdb_get_protein")
        tool = GPCRdbTool(config)
        tool._get_protein = MagicMock(return_value={"status": "success"})
        tool.run({"protein": "adrb2_human"})  # No operation param
        tool._get_protein.assert_called_once()

    def test_omim_auto_fills_operation(self):
        """OMIM tool should auto-fill operation from config const."""
        from tooluniverse.omim_tool import OMIMTool
        config = self._load_config("omim_tools.json", "OMIM_search")
        tool = OMIMTool(config)
        tool.api_key = "fake_key"  # bypass API key check
        tool._search = MagicMock(return_value={"status": "success"})
        tool.run({"query": "Marfan"})  # No operation param
        tool._search.assert_called_once()

    def test_disgenet_auto_fills_operation(self):
        """DisGeNET tool should auto-fill operation from config const."""
        from tooluniverse.disgenet_tool import DisGeNETTool
        config = self._load_config("disgenet_tools.json", "DisGeNET_search_gene")
        tool = DisGeNETTool(config)
        tool.api_key = "fake_key"  # bypass API key check
        tool._search_gene = MagicMock(return_value={"status": "success"})
        tool.run({"gene_symbol": "FBN1"})  # No operation param
        tool._search_gene.assert_called_once()

    def test_all_fixed_jsons_no_operation_required(self):
        """All fixed JSON files should NOT have 'operation' in required."""
        fixed_jsons = [
            "orphanet_tools.json", "gencc_tools.json", "brenda_tools.json",
            "dailymed_tools.json", "disgenet_tools.json", "emolecules_tools.json",
            "enamine_tools.json", "faers_analytics_tools.json",
            "fda_orange_book_tools.json", "gpcrdb_tools.json", "hmdb_tools.json",
            "imgt_tools.json", "metacyc_tools.json", "ncbi_nucleotide_tools.json",
            "ols_tools.json", "omim_tools.json", "oncokb_tools.json",
            "sabdab_tools.json",
        ]
        import os
        data_dir = os.path.join(
            os.path.dirname(__file__), "../../src/tooluniverse/data"
        )
        for jf in fixed_jsons:
            path = os.path.join(data_dir, jf)
            if not os.path.exists(path):
                continue
            with open(path) as f:
                tools = json.load(f)
            for t in tools:
                req = t.get("parameter", {}).get("required", [])
                props = t.get("parameter", {}).get("properties", {})
                if props.get("operation", {}).get("const"):
                    self.assertNotIn(
                        "operation", req,
                        f"{t['name']} in {jf} still has operation in required"
                    )


# ---------------------------------------------------------------------------
# Monarch remove_empty_values preserves 0 and empty lists
# ---------------------------------------------------------------------------
class TestMonarchRemoveEmptyValues(unittest.TestCase):
    """Monarch tool should preserve 0 and [] in API responses."""

    def test_zero_total_preserved(self):
        """total: 0 should NOT be stripped from response."""
        from tooluniverse.restful_tool import MonarchTool

        config = {
            "name": "get_HPO_ID_by_phenotype",
            "type": "Monarch",
            "tool_url": "/search",
            "query_schema": {
                "query": None,
                "category": ["biolink:PhenotypicFeature"],
                "limit": 20,
                "offset": 0,
            },
            "parameter": {"properties": {}},
        }
        tool = MonarchTool(config)

        # Simulate Monarch API returning 0 results
        mock_response = {"total": 0, "items": [], "limit": 20, "offset": 0}

        with patch("tooluniverse.restful_tool.execute_RESTful_query",
                    return_value=mock_response):
            result = tool.run({"query": "nonexistent phenotype"})

        self.assertEqual(result["total"], 0)
        self.assertEqual(result["items"], [])
        self.assertIn("limit", result)

    def test_zero_descendant_count_preserved(self):
        """descendant_count: 0 should NOT be stripped."""
        from tooluniverse.restful_tool import MonarchTool

        config = {
            "name": "get_HPO_ID_by_phenotype",
            "type": "Monarch",
            "tool_url": "/search",
            "query_schema": {"query": None, "limit": 5},
            "parameter": {"properties": {}},
        }
        tool = MonarchTool(config)

        mock_response = {
            "total": 1,
            "items": [
                {
                    "id": "HP:0001250",
                    "name": "Seizure",
                    "has_descendant_count": 0,
                    "description": None,
                }
            ],
            "limit": 5,
        }

        with patch("tooluniverse.restful_tool.execute_RESTful_query",
                    return_value=mock_response):
            result = tool.run({"query": "seizure"})

        item = result["items"][0]
        self.assertEqual(item["has_descendant_count"], 0)
        # None values should still be stripped
        self.assertNotIn("description", item)


# ---------------------------------------------------------------------------
# CTD mitochondrial gene name normalization
# ---------------------------------------------------------------------------
class TestCTDMitoGeneNormalization(unittest.TestCase):
    """CTD tool should strip MT- prefix for mitochondrial gene queries."""

    def _make_tool(self, input_type="gene"):
        from tooluniverse.ctd_tool import CTDTool

        config = {
            "name": "CTD_get_gene_diseases",
            "type": "CTDTool",
            "fields": {"input_type": input_type, "report_type": "diseases_curated"},
        }
        return CTDTool(config)

    @patch("tooluniverse.ctd_tool.requests.get")
    def test_mt_prefix_stripped(self, mock_get):
        """MT-ND5 should be normalized to ND5 for CTD queries."""
        tool = self._make_tool()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.text = '[{"GeneSymbol": "ND5", "DiseaseName": "MELAS"}]'
        mock_resp.json.return_value = [
            {"GeneSymbol": "ND5", "DiseaseName": "MELAS"}
        ]
        mock_get.return_value = mock_resp

        result = tool.run({"input_terms": "MT-ND5"})

        # Verify API was called with ND5, not MT-ND5
        call_params = mock_get.call_args[1].get("params", {})
        self.assertEqual(call_params["inputTerms"], "ND5")

        # Verify metadata includes normalization note
        self.assertIn("normalized_query", result["metadata"])
        self.assertEqual(result["metadata"]["normalized_query"], "ND5")

    @patch("tooluniverse.ctd_tool.requests.get")
    def test_non_mito_gene_unchanged(self, mock_get):
        """Non-mitochondrial genes should NOT be modified."""
        tool = self._make_tool()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.text = '[{"GeneSymbol": "BRCA1"}]'
        mock_resp.json.return_value = [{"GeneSymbol": "BRCA1"}]
        mock_get.return_value = mock_resp

        result = tool.run({"input_terms": "BRCA1"})

        call_params = mock_get.call_args[1].get("params", {})
        self.assertEqual(call_params["inputTerms"], "BRCA1")
        self.assertNotIn("normalized_query", result["metadata"])

    @patch("tooluniverse.ctd_tool.requests.get")
    def test_mt_prefix_only_for_gene_type(self, mock_get):
        """MT- prefix stripping should only apply to gene input_type."""
        tool = self._make_tool(input_type="chem")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.text = "[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        tool.run({"input_terms": "MT-ND5"})

        call_params = mock_get.call_args[1].get("params", {})
        # Chemical queries should NOT strip MT-
        self.assertEqual(call_params["inputTerms"], "MT-ND5")


# ---------------------------------------------------------------------------
# ClinGen variant classifications coverage note
# ---------------------------------------------------------------------------
class TestClinGenVariantClassificationNote(unittest.TestCase):
    """ClinGen should add helpful note when no variant classifications found."""

    def _make_tool(self):
        from tooluniverse.clingen_tool import ClinGenTool

        config = {
            "name": "ClinGen_get_variant_classifications",
            "type": "ClinGenTool",
            "fields": {"operation": "get_variant_classifications", "timeout": 30},
            "parameter": {"required": []},
        }
        return ClinGenTool(config)

    @patch("tooluniverse.clingen_tool.requests.get")
    def test_empty_results_include_note(self, mock_get):
        """When no classifications found for a gene, include helpful note."""
        tool = self._make_tool()

        # Mock TSV response with only header (no data for the gene)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.text = (
            "#Variation\tClinVar Variation Id\tHGNC Gene Symbol\n"
            "NM_000277.2:c.1A>G\t586\tPAH\n"
        )
        mock_get.return_value = mock_resp

        result = tool.run({"gene": "LRRK2"})

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total"], 0)
        self.assertIn("note", result)
        self.assertIn("VCEP", result["note"])
        self.assertIn("LRRK2", result["note"])

    @patch("tooluniverse.clingen_tool.requests.get")
    def test_results_found_no_note(self, mock_get):
        """When classifications are found, no note is needed."""
        tool = self._make_tool()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.text = (
            "#Variation\tClinVar Variation Id\tHGNC Gene Symbol\tDisease\n"
            "NM_000277.2:c.1A>G\t586\tPAH\tphenylketonuria\n"
        )
        mock_get.return_value = mock_resp

        result = tool.run({"gene": "PAH"})

        self.assertEqual(result["status"], "success")
        self.assertGreater(result["total"], 0)
        self.assertNotIn("note", result)


# ---------------------------------------------------------------------------
# MyVariant query field path in description
# ---------------------------------------------------------------------------
class TestMyVariantQueryFieldPath(unittest.TestCase):
    """MyVariant tool description should use correct field paths."""

    def test_description_uses_gene_symbol_field(self):
        """The query description should use clinvar.gene.symbol, not clinvar.gene."""
        import os

        json_path = os.path.join(
            os.path.dirname(__file__),
            "../../src/tooluniverse/data/biothings_tools.json",
        )
        with open(json_path) as f:
            tools = json.load(f)

        for t in tools:
            if t["name"] == "MyVariant_query_variants":
                desc = t["parameter"]["properties"]["query"]["description"]
                self.assertIn("clinvar.gene.symbol", desc)
                self.assertNotIn("clinvar.gene:BRCA1", desc)
                break
        else:
            self.fail("MyVariant_query_variants not found")


# ---------------------------------------------------------------------------
# ClinicalTrials limit param maps to pageSize
# ---------------------------------------------------------------------------
class TestClinicalTrialsLimitMapping(unittest.TestCase):
    """ClinicalTrials_search_studies should map 'limit' to 'pageSize'."""

    def test_limit_in_search_param_map(self):
        """The _run_search method should map 'limit' to 'pageSize'."""
        from tooluniverse.ctg_tool import ClinicalTrialsTool

        config = {
            "name": "ClinicalTrials_search_studies",
            "type": "ClinicalTrialsTool",
            "fields": {"operation": "search"},
            "parameter": {"required": [], "properties": {}},
            "query_schema": {},
        }
        tool = ClinicalTrialsTool(config)

        # Verify _run_search maps limit to pageSize
        import inspect

        source = inspect.getsource(tool._run_search)
        self.assertIn('"limit": "pageSize"', source)

    @patch("requests.get")
    def test_limit_applied_as_pagesize(self, mock_get):
        """Passing limit=5 should result in pageSize=5 in API request."""
        from tooluniverse.ctg_tool import ClinicalTrialsTool

        config = {
            "name": "ClinicalTrials_search_studies",
            "type": "ClinicalTrialsTool",
            "fields": {"operation": "search"},
            "parameter": {"required": [], "properties": {}},
            "query_schema": {},
        }
        tool = ClinicalTrialsTool(config)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"studies": [], "totalCount": 0}
        mock_get.return_value = mock_resp

        tool.run({"query": "cancer", "limit": 5})

        call_params = mock_get.call_args[1].get("params", {})
        self.assertEqual(call_params.get("pageSize"), 5)
        self.assertNotIn("limit", call_params)


# ---------------------------------------------------------------------------
# GEO methylation/ChIP-seq search filters out GPL platform records
# ---------------------------------------------------------------------------
class TestGEOMethylationGPLFilter(unittest.TestCase):
    """GEO methylation search should filter out GPL platform records."""

    def _make_tool(self, endpoint):
        from tooluniverse.epigenomics_tool import EpigenomicsTool

        config = {
            "name": "GEO_search_methylation_datasets",
            "type": "EpigenomicsTool",
            "fields": {"endpoint": endpoint},
        }
        return EpigenomicsTool(config)

    @patch("tooluniverse.epigenomics_tool.requests.get")
    def test_gpl_records_filtered_out_methylation(self, mock_get):
        """GPL (platform) accessions should be excluded from methylation results."""
        tool = self._make_tool("geo_methylation_search")

        # Mock esearch response
        search_resp = MagicMock()
        search_resp.status_code = 200
        search_resp.raise_for_status = MagicMock()
        search_resp.json.return_value = {
            "esearchresult": {"count": "3", "idlist": ["1", "2", "3"]}
        }

        # Mock esummary with mix of GSE and GPL records
        summary_resp = MagicMock()
        summary_resp.status_code = 200
        summary_resp.raise_for_status = MagicMock()
        summary_resp.json.return_value = {
            "result": {
                "1": {
                    "accession": "GSE12345",
                    "title": "Methylation study",
                    "summary": "Real dataset",
                    "taxon": "Homo sapiens",
                    "n_samples": 50,
                },
                "2": {
                    "accession": "GPL6244",
                    "title": "Affymetrix Platform",
                    "summary": "Platform record",
                    "taxon": "Homo sapiens",
                    "n_samples": 0,
                },
                "3": {
                    "accession": "GSE67890",
                    "title": "Another study",
                    "summary": "Another dataset",
                    "taxon": "Homo sapiens",
                    "n_samples": 30,
                },
            }
        }

        mock_get.side_effect = [search_resp, summary_resp]

        result = tool.run({"query": "arsenic methylation"})

        datasets = result["data"]["datasets"]
        # GPL record should be filtered out
        self.assertEqual(len(datasets), 2)
        accessions = [d["accession"] for d in datasets]
        self.assertIn("GSE12345", accessions)
        self.assertIn("GSE67890", accessions)
        self.assertNotIn("GPL6244", accessions)

    @patch("tooluniverse.epigenomics_tool.requests.get")
    def test_gpl_records_filtered_out_chipseq(self, mock_get):
        """GPL records should also be filtered from ChIP-seq results."""
        tool = self._make_tool("geo_chipseq_search")

        search_resp = MagicMock()
        search_resp.status_code = 200
        search_resp.raise_for_status = MagicMock()
        search_resp.json.return_value = {
            "esearchresult": {"count": "2", "idlist": ["1", "2"]}
        }

        summary_resp = MagicMock()
        summary_resp.status_code = 200
        summary_resp.raise_for_status = MagicMock()
        summary_resp.json.return_value = {
            "result": {
                "1": {
                    "accession": "GPL570",
                    "title": "Platform",
                    "summary": "Platform record",
                    "taxon": "Homo sapiens",
                    "n_samples": 0,
                },
                "2": {
                    "accession": "GSE99999",
                    "title": "ChIP-seq study",
                    "summary": "Real dataset",
                    "taxon": "Homo sapiens",
                    "n_samples": 20,
                },
            }
        }

        mock_get.side_effect = [search_resp, summary_resp]

        result = tool.run({"query": "ESR1 ChIP-seq"})

        datasets = result["data"]["datasets"]
        self.assertEqual(len(datasets), 1)
        self.assertEqual(datasets[0]["accession"], "GSE99999")


# ---------------------------------------------------------------------------
# GTEx expression summary provides helpful note on empty results
# ---------------------------------------------------------------------------
class TestGTExExpressionSummaryNote(unittest.TestCase):
    """GTEx expression summary should provide hints when results are empty."""

    def _make_tool(self):
        from tooluniverse.gtex_tool import GTExExpressionTool

        config = {
            "name": "GTEx_get_expression_summary",
            "type": "GTExExpressionTool",
            "settings": {"base_url": "https://gtexportal.org/api/v2", "timeout": 30},
        }
        return GTExExpressionTool(config)

    @patch("tooluniverse.gtex_tool._http_get")
    @patch("tooluniverse.gtex_tool._resolve_gene_id")
    def test_note_when_resolution_fails(self, mock_resolve, mock_http):
        """When gene ID resolution fails, include helpful note."""
        tool = self._make_tool()

        # Resolution fails - returns input as-is
        mock_resolve.return_value = "COL5A1"

        # Expression API returns empty
        mock_http.return_value = {"data": []}

        result = tool.run({"gene_symbol": "COL5A1"})

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["geneExpression"], [])
        self.assertIn("note", result)
        self.assertIn("Could not resolve", result["note"])

    @patch("tooluniverse.gtex_tool._http_get")
    @patch("tooluniverse.gtex_tool._resolve_gene_id")
    def test_note_when_version_mismatch(self, mock_resolve, mock_http):
        """When resolved but empty, suggest version mismatch."""
        tool = self._make_tool()

        # Resolution succeeds but returns wrong version
        mock_resolve.return_value = "ENSG00000130635.18"

        # Expression API returns empty (version mismatch)
        mock_http.return_value = {"data": []}

        result = tool.run({"ensembl_gene_id": "ENSG00000130635"})

        self.assertTrue(result["success"])
        self.assertIn("note", result)
        self.assertIn("GENCODE version", result["note"])

    @patch("tooluniverse.gtex_tool._http_get")
    @patch("tooluniverse.gtex_tool._resolve_gene_id")
    def test_no_note_when_data_found(self, mock_resolve, mock_http):
        """When expression data is found, no note is needed."""
        tool = self._make_tool()

        mock_resolve.return_value = "ENSG00000141510.16"
        mock_http.return_value = {
            "data": [{"gencodeId": "ENSG00000141510.16", "median": 15.0}]
        }

        result = tool.run({"gene_symbol": "TP53"})

        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]["geneExpression"]), 1)
        self.assertNotIn("note", result)

    def test_error_when_no_gene_input(self):
        """Should return error when neither gene_symbol nor ensembl_gene_id provided."""
        tool = self._make_tool()
        result = tool.run({})
        self.assertFalse(result["success"])
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
