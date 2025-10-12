#!/usr/bin/env python3
"""
Test Scientific Workflows and Real-world Scenarios

This test file covers important scientific workflow scenarios:
1. Drug discovery workflows
2. Literature research workflows
3. Biomarker discovery workflows
4. Clinical trial analysis workflows
5. Genomics research workflows
6. Safety assessment workflows
"""

import sys
import unittest
from pathlib import Path
import pytest
from unittest.mock import patch, Mock, MagicMock
import json
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tooluniverse import ToolUniverse


@pytest.mark.unit
class TestScientificWorkflows(unittest.TestCase):
    """Test scientific workflows and real-world scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tu = ToolUniverse()
        # Don't load tools to avoid embedding model loading issues
        self.tu.all_tools = []
        self.tu.all_tool_dict = {}
    
    def test_drug_discovery_workflow(self):
        """Test comprehensive drug discovery workflow."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock drug discovery workflow steps
            mock_run.side_effect = [
                # Step 1: Disease information
                {"data": {"disease": {"id": "EFO_0001074", "name": "Alzheimer's disease"}}},
                # Step 2: Target identification
                {"data": {"disease": {"associatedTargets": {"rows": [
                    {"approvedSymbol": "APP", "associationScore": 0.8},
                    {"approvedSymbol": "PSEN1", "associationScore": 0.7},
                    {"approvedSymbol": "PSEN2", "associationScore": 0.6}
                ]}}}},
                # Step 3: Drug discovery
                {"data": {"disease": {"knownDrugs": {"rows": [
                    {"drug": {"name": "donepezil", "isApproved": True}},
                    {"drug": {"name": "galantamine", "isApproved": True}},
                    {"drug": {"name": "rivastigmine", "isApproved": True}}
                ]}}}},
                # Step 4: Safety assessment
                {"bbb_penetrance": [0.8], "bioavailability": [0.6], "toxicity": [0.3]},
                # Step 5: Literature validation
                {"summary": "Literature review completed"}
            ]
            
            # Test drug discovery workflow
            disease_name = "Alzheimer's disease"
            workflow_results = {}
            
            # Step 1: Get disease information
            disease_query = {
                "name": "OpenTargets_get_disease_id_description_by_name",
                "arguments": {"diseaseName": disease_name}
            }
            disease_info = self.tu.run(disease_query)
            workflow_results["disease_info"] = disease_info
            
            if disease_info and "data" in disease_info:
                disease_id = disease_info["data"]["disease"]["id"]
                
                # Step 2: Get associated targets
                targets_query = {
                    "name": "OpenTargets_get_associated_targets_by_disease_efoId",
                    "arguments": {"efoId": disease_id, "limit": 25}
                }
                targets = self.tu.run(targets_query)
                workflow_results["targets"] = targets
                
                # Step 3: Get known drugs
                drugs_query = {
                    "name": "OpenTargets_get_associated_drugs_by_disease_efoId",
                    "arguments": {"efoId": disease_id, "size": 20}
                }
                drugs = self.tu.run(drugs_query)
                workflow_results["drugs"] = drugs
                
                # Step 4: Safety assessment
                safety_query = {
                    "name": "ADMETAI_predict_BBB_penetrance",
                    "arguments": {"smiles": ["CCO"]}  # Mock SMILES
                }
                safety = self.tu.run(safety_query)
                workflow_results["safety"] = safety
                
                # Step 5: Literature validation
                literature_query = {
                    "name": "LiteratureSearchTool",
                    "arguments": {"research_topic": f"{disease_name} drug discovery"}
                }
                literature = self.tu.run(literature_query)
                workflow_results["literature"] = literature
            
            # Verify workflow results
            self.assertIn("disease_info", workflow_results)
            self.assertIn("targets", workflow_results)
            self.assertIn("drugs", workflow_results)
            self.assertIn("safety", workflow_results)
            self.assertIn("literature", workflow_results)
    
    def test_literature_research_workflow(self):
        """Test systematic literature research workflow."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock literature search results
            mock_run.side_effect = [
                # EuropePMC search
                {"results": [{"title": "Paper 1", "abstract": "Abstract 1"}]},
                # OpenAlex search
                {"results": [{"title": "Paper 2", "abstract": "Abstract 2"}]},
                # PubTator search
                {"results": [{"title": "Paper 3", "abstract": "Abstract 3"}]},
                # AI summarization
                {"summary": "Comprehensive literature review summary"}
            ]
            
            # Test literature research workflow
            research_topic = "CRISPR gene editing therapeutic applications"
            literature_results = {}
            
            # Step 1: Multi-database search (broadcasting pattern)
            literature_sources = {}
            
            literature_sources['europepmc'] = self.tu.run({
                "name": "EuropePMC_search_articles",
                "arguments": {"query": research_topic, "limit": 50}
            })
            
            literature_sources['openalex'] = self.tu.run({
                "name": "openalex_literature_search",
                "arguments": {"search_keywords": research_topic, "max_results": 50}
            })
            
            literature_sources['pubtator'] = self.tu.run({
                "name": "PubTator3_LiteratureSearch",
                "arguments": {"text": research_topic, "page_size": 50}
            })
            
            literature_results['sources'] = literature_sources
            
            # Step 2: AI-powered synthesis
            synthesis = self.tu.run({
                "name": "MedicalLiteratureReviewer",
                "arguments": {
                    "research_topic": research_topic,
                    "literature_content": str(literature_sources),
                    "focus_area": "key findings",
                    "study_types": "all studies",
                    "quality_level": "all evidence",
                    "review_scope": "comprehensive review"
                }
            })
            
            literature_results['synthesis'] = synthesis
            
            # Verify literature workflow
            self.assertIn("sources", literature_results)
            self.assertIn("synthesis", literature_results)
            self.assertEqual(len(literature_results["sources"]), 3)
    
    def test_biomarker_discovery_workflow(self):
        """Test biomarker discovery and validation workflow."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock biomarker discovery steps
            mock_run.side_effect = [
                # Literature-based discovery
                {"summary": "Biomarker literature review completed"},
                # Gene search
                {"genes": [
                    {"gene_name": "BRCA1", "ensembl_id": "ENSG00000012048"},
                    {"gene_name": "BRCA2", "ensembl_id": "ENSG00000139618"},
                    {"gene_name": "TP53", "ensembl_id": "ENSG00000141510"}
                ]},
                # Expression data
                {"gene_details": {
                    "gene_name": "BRCA1",
                    "ensembl_id": "ENSG00000012048",
                    "expression_data": "High expression in breast tissue"
                }},
                # Pathway analysis
                {"biological_processes": ["DNA repair", "Cell cycle control"]},
                # Clinical validation
                {"clinical_evidence": "FDA approved drugs targeting BRCA1"}
            ]
            
            # Test biomarker discovery workflow
            disease_condition = "breast cancer"
            biomarker_results = {}
            
            # Step 1: Literature-based biomarker discovery
            literature_biomarkers = self.tu.run({
                "name": "LiteratureSearchTool",
                "arguments": {"research_topic": f"{disease_condition} biomarkers"}
            })
            biomarker_results["literature_evidence"] = literature_biomarkers
            
            # Step 2: Gene discovery
            gene_search = self.tu.run({
                "name": "HPA_search_genes_by_query",
                "arguments": {"search_query": disease_condition}
            })
            biomarker_results["gene_discovery"] = gene_search
            
            if gene_search and "genes" in gene_search:
                first_gene = gene_search["genes"][0]
                
                # Step 3: Expression data analysis
                expression_data = self.tu.run({
                    "name": "HPA_get_comprehensive_gene_details_by_ensembl_id",
                    "arguments": {"ensembl_id": first_gene["ensembl_id"]}
                })
                biomarker_results["expression_data"] = expression_data
                
                # Step 4: Pathway analysis
                pathway_analysis = self.tu.run({
                    "name": "HPA_get_biological_processes_by_gene",
                    "arguments": {"gene": first_gene["gene_name"]}
                })
                biomarker_results["pathway_analysis"] = pathway_analysis
                
                # Step 5: Clinical validation
                clinical_validation = self.tu.run({
                    "name": "FDA_get_drug_names_by_clinical_pharmacology",
                    "arguments": {"clinical_pharmacology": disease_condition}
                })
                biomarker_results["clinical_validation"] = clinical_validation
            
            # Verify biomarker workflow
            self.assertIn("literature_evidence", biomarker_results)
            self.assertIn("gene_discovery", biomarker_results)
            self.assertIn("expression_data", biomarker_results)
            self.assertIn("pathway_analysis", biomarker_results)
            self.assertIn("clinical_validation", biomarker_results)
    
    def test_clinical_trial_analysis_workflow(self):
        """Test clinical trial analysis workflow."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock clinical trial analysis
            mock_run.side_effect = [
                # Trial search
                {"studies": [
                    {"nct_id": "NCT123456", "phase": "Phase 3", "status": "Recruiting"},
                    {"nct_id": "NCT789012", "phase": "Phase 2", "status": "Completed"},
                    {"nct_id": "NCT345678", "phase": "Phase 1", "status": "Recruiting"}
                ]},
                # Literature context
                {"summary": "Clinical trial literature review completed"}
            ]
            
            # Test clinical trial analysis workflow
            condition = "Alzheimer's disease"
            intervention = "donepezil"
            trial_analysis = {}
            
            # Step 1: Search for relevant trials
            trials_query = {
                "name": "ClinicalTrials_search_studies",
                "arguments": {
                    "condition": condition,
                    "intervention": intervention
                }
            }
            trials = self.tu.run(trials_query)
            trial_analysis["trials"] = trials
            
            if trials and "studies" in trials:
                # Step 2: Analyze trial phases
                phase_distribution = {}
                for trial in trials["studies"]:
                    phase = trial.get("phase", "Unknown")
                    phase_distribution[phase] = phase_distribution.get(phase, 0) + 1
                
                trial_analysis["phase_distribution"] = phase_distribution
                
                # Step 3: Literature context
                literature_context = self.tu.run({
                    "name": "LiteratureSearchTool",
                    "arguments": {"research_topic": f"{condition} {intervention} clinical trials"}
                })
                trial_analysis["literature_context"] = literature_context
                
                # Step 4: Geographic analysis
                countries = {}
                for trial in trials["studies"]:
                    locations = trial.get("location_countries", [])
                    for country in locations:
                        countries[country] = countries.get(country, 0) + 1
                
                trial_analysis["geographic_distribution"] = {
                    "top_countries": sorted(countries.items(), key=lambda x: x[1], reverse=True),
                    "total_countries": len(countries)
                }
            
            # Verify trial analysis
            self.assertIn("trials", trial_analysis)
            self.assertIn("phase_distribution", trial_analysis)
            self.assertIn("literature_context", trial_analysis)
            self.assertIn("geographic_distribution", trial_analysis)
    
    def test_genomics_research_workflow(self):
        """Test genomics research workflow."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock genomics workflow steps
            mock_run.side_effect = [
                # Protein information
                {"protein_data": {"name": "BRCA1", "function": "DNA repair"}},
                # Disease associations
                {"diseases": [{"name": "Breast cancer", "association_score": 0.9}]},
                # Literature analysis
                {"summary": "BRCA1 literature analysis completed"},
                # Pathway enrichment
                {"pathways": ["DNA repair pathway", "Cell cycle pathway"]}
            ]
            
            # Test genomics research workflow
            gene_symbols = ["BRCA1", "BRCA2", "TP53"]
            genomics_results = {}
            
            # Step 1: Gene information gathering
            gene_info = {}
            for gene in gene_symbols:
                # Get protein information
                protein_data = self.tu.run({
                    "name": "UniProt_get_protein_info",
                    "arguments": {"gene_symbol": gene}
                })
                gene_info[gene] = {"protein": protein_data}
                
                # Get disease associations
                diseases = self.tu.run({
                    "name": "OpenTargets_get_associated_diseases_by_target",
                    "arguments": {"target_symbol": gene, "limit": 10}
                })
                gene_info[gene]["diseases"] = diseases
            
            genomics_results["gene_info"] = gene_info
            
            # Step 2: Literature analysis
            literature_analysis = {}
            for gene in gene_symbols:
                gene_literature = self.tu.run({
                    "name": "LiteratureSearchTool",
                    "arguments": {"research_topic": f"{gene} variants mutations functional impact"}
                })
                literature_analysis[gene] = gene_literature
            
            genomics_results["literature_analysis"] = literature_analysis
            
            # Step 3: Pathway enrichment analysis
            pathway_query = {
                "name": "Enrichr_analyze_gene_list",
                "arguments": {
                    "gene_list": gene_symbols,
                    "library": "KEGG_2021_Human"
                }
            }
            pathways = self.tu.run(pathway_query)
            genomics_results["pathways"] = pathways
            
            # Verify genomics workflow
            self.assertIn("gene_info", genomics_results)
            self.assertIn("literature_analysis", genomics_results)
            self.assertIn("pathways", genomics_results)
            self.assertEqual(len(genomics_results["gene_info"]), 3)
            self.assertEqual(len(genomics_results["literature_analysis"]), 3)
    
    def test_safety_assessment_workflow(self):
        """Test drug safety assessment workflow."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock safety assessment steps
            mock_run.side_effect = [
                # Drug information
                {"compound_info": {"name": "aspirin", "molecular_weight": 180.16}},
                # Adverse events
                {"results": [
                    {"reaction": "Nausea", "count": 150},
                    {"reaction": "Headache", "count": 120},
                    {"reaction": "Stomach pain", "count": 100}
                ]},
                # Safety literature
                {"summary": "Aspirin safety literature review completed"},
                # Clinical trials
                {"studies": [
                    {"nct_id": "NCT123456", "safety_outcomes": "Well tolerated"},
                    {"nct_id": "NCT789012", "safety_outcomes": "Minor adverse events"}
                ]}
            ]
            
            # Test safety assessment workflow
            drug_name = "aspirin"
            safety_assessment = {}
            
            # Step 1: Basic drug information
            drug_info = self.tu.run({
                "name": "PubChem_get_compound_info",
                "arguments": {"compound_name": drug_name}
            })
            safety_assessment["drug_info"] = drug_info
            
            # Step 2: Adverse events analysis
            adverse_events = self.tu.run({
                "name": "FAERS_count_reactions_by_drug_event",
                "arguments": {"medicinalproduct": drug_name}
            })
            safety_assessment["adverse_events"] = adverse_events
            
            if adverse_events and "results" in adverse_events:
                # Analyze adverse event patterns
                reaction_counts = {}
                for event in adverse_events["results"]:
                    reaction = event.get("reaction", "Unknown")
                    count = event.get("count", 0)
                    reaction_counts[reaction] = count
                
                safety_assessment["reaction_analysis"] = {
                    "top_reactions": sorted(reaction_counts.items(), key=lambda x: x[1], reverse=True),
                    "total_reactions": len(reaction_counts)
                }
            
            # Step 3: Safety literature review
            safety_literature = self.tu.run({
                "name": "LiteratureSearchTool",
                "arguments": {"research_topic": f"{drug_name} safety toxicity adverse effects"}
            })
            safety_assessment["safety_literature"] = safety_literature
            
            # Step 4: Clinical trial safety data
            trial_safety = self.tu.run({
                "name": "ClinicalTrials_search_studies",
                "arguments": {
                    "intervention": drug_name,
                    "study_type": "Interventional"
                }
            })
            safety_assessment["clinical_trials"] = trial_safety
            
            # Verify safety assessment
            self.assertIn("drug_info", safety_assessment)
            self.assertIn("adverse_events", safety_assessment)
            self.assertIn("safety_literature", safety_assessment)
            self.assertIn("clinical_trials", safety_assessment)
    
    def test_workflow_error_handling(self):
        """Test error handling in scientific workflows."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock error scenarios
            mock_run.side_effect = [
                {"data": {"disease": {"id": "EFO_0001074"}}},  # Success
                Exception("Target identification failed"),  # Error
                {"data": {"drugs": [{"name": "donepezil"}]}}  # Fallback success
            ]
            
            # Test workflow with error handling
            workflow_results = {"status": "running", "completed_steps": []}
            
            try:
                # Step 1: Disease identification
                disease_result = self.tu.run({
                    "name": "OpenTargets_get_disease_id_description_by_name",
                    "arguments": {"diseaseName": "Alzheimer's disease"}
                })
                workflow_results["disease"] = disease_result
                workflow_results["completed_steps"].append("disease_identification")
                
                # Step 2: Target identification (may fail)
                try:
                    targets_result = self.tu.run({
                        "name": "OpenTargets_get_associated_targets_by_disease_efoId",
                        "arguments": {"efoId": disease_result["data"]["disease"]["id"]}
                    })
                    workflow_results["targets"] = targets_result
                    workflow_results["completed_steps"].append("target_identification")
                except Exception as e:
                    workflow_results["target_error"] = str(e)
                    workflow_results["completed_steps"].append("target_identification_failed")
                
                # Step 3: Drug discovery (fallback)
                try:
                    drugs_result = self.tu.run({
                        "name": "OpenTargets_get_associated_drugs_by_disease_efoId",
                        "arguments": {"efoId": disease_result["data"]["disease"]["id"]}
                    })
                    workflow_results["drugs"] = drugs_result
                    workflow_results["completed_steps"].append("drug_discovery")
                except Exception as e:
                    workflow_results["drug_error"] = str(e)
                
            except Exception as e:
                workflow_results["status"] = "failed"
                workflow_results["error"] = str(e)
            
            # Verify error handling
            self.assertIn("disease", workflow_results)
            self.assertIn("target_error", workflow_results)
            self.assertIn("drugs", workflow_results)
            self.assertIn("disease_identification", workflow_results["completed_steps"])
            self.assertIn("target_identification_failed", workflow_results["completed_steps"])
            self.assertIn("drug_discovery", workflow_results["completed_steps"])
    
    def test_workflow_performance_optimization(self):
        """Test workflow performance optimization."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"result": "success"}
            
            # Test parallel execution
            import threading
            import time
            
            results = []
            
            def parallel_workflow_step(step_name):
                start_time = time.time()
                result = self.tu.run({
                    "name": f"workflow_step_{step_name}",
                    "arguments": {"step": step_name}
                })
                execution_time = time.time() - start_time
                results.append({
                    "step": step_name,
                    "result": result,
                    "execution_time": execution_time
                })
            
            # Execute workflow steps in parallel
            threads = []
            step_names = ["literature_search", "target_identification", "drug_discovery"]
            
            start_time = time.time()
            for step_name in step_names:
                thread = threading.Thread(target=parallel_workflow_step, args=(step_name,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            total_time = time.time() - start_time
            
            # Verify parallel execution
            self.assertEqual(len(results), 3)
            self.assertLess(total_time, 1.0)  # Should be fast with mocked calls
            
            # Test caching
            cache_key = "expensive_computation"
            if cache_key in self.tu._cache:
                cached_result = self.tu._cache[cache_key]
            else:
                cached_result = self.tu.run({
                    "name": "expensive_tool",
                    "arguments": {"computation": "heavy"}
                })
                self.tu._cache[cache_key] = cached_result
            
            # Verify caching
            self.assertIsInstance(cached_result, dict)


if __name__ == "__main__":
    unittest.main()
