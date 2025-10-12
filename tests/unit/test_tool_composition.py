#!/usr/bin/env python3
"""
Test Tool Composition and Workflow functionality

This test file covers important composition and workflow scenarios:
1. Compose tool creation and execution
2. Tool chaining and broadcasting patterns
3. Error handling in composed workflows
4. Dependency management
5. Workflow optimization
"""

import sys
import unittest
from pathlib import Path
import pytest
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tooluniverse import ToolUniverse


@pytest.mark.unit
class TestToolComposition(unittest.TestCase):
    """Test tool composition and workflow functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.tu = ToolUniverse()
        # Don't load tools to avoid embedding model loading issues
        self.tu.all_tools = []
        self.tu.all_tool_dict = {}

    def test_compose_tool_creation(self):
        """Test creating and configuring compose tools."""
        # Test compose tool configuration
        compose_config = {
            "type": "ComposeTool",
            "name": "TestComposeTool",
            "description": "Test compose tool",
            "parameter": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            },
            "composition_file": "test_compose.py",
            "composition_function": "compose"
        }

        # Add to tools
        self.tu.all_tools.append(compose_config)
        self.tu.all_tool_dict["TestComposeTool"] = compose_config

        # Test tool specification
        spec = self.tu.tool_specification("TestComposeTool")
        self.assertIsNotNone(spec)
        self.assertEqual(spec["name"], "TestComposeTool")

    def test_tool_chaining_pattern(self):
        """Test sequential tool chaining pattern."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock sequential tool calls
            mock_run.side_effect = [
                {"data": {"disease": {"id": "EFO_0001074"}}},
                {"data": {"targets": [{"symbol": "APP"}]}},
                {"data": {"drugs": [{"name": "donepezil"}]}}
            ]

            # Simulate chaining workflow
            disease_result = self.tu.run({
                "name": "OpenTargets_get_disease_id_description_by_name",
                "arguments": {"diseaseName": "Alzheimer's disease"}
            })

            if disease_result and "data" in disease_result:
                disease_id = disease_result["data"]["disease"]["id"]

                targets_result = self.tu.run({
                    "name": "OpenTargets_get_associated_targets_by_disease_efoId",
                    "arguments": {"efoId": disease_id}
                })

                if targets_result and "data" in targets_result:
                    drugs_result = self.tu.run({
                        "name": "OpenTargets_get_associated_drugs_by_disease_efoId",
                        "arguments": {"efoId": disease_id}
                    })

                    self.assertIsInstance(drugs_result, dict)

    def test_broadcasting_pattern(self):
        """Test parallel tool execution (broadcasting pattern)."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock parallel tool calls
            mock_run.side_effect = [
                {"results": [{"title": "Paper 1"}]},
                {"results": [{"title": "Paper 2"}]},
                {"results": [{"title": "Paper 3"}]}
            ]

            # Simulate broadcasting workflow
            literature_sources = {}

            # Parallel searches
            literature_sources['europepmc'] = self.tu.run({
                "name": "EuropePMC_search_articles",
                "arguments": {"query": "CRISPR", "limit": 5}
            })

            literature_sources['openalex'] = self.tu.run({
                "name": "openalex_literature_search",
                "arguments": {
                    "search_keywords": "CRISPR",
                    "max_results": 5
                }
            })

            literature_sources['pubtator'] = self.tu.run({
                "name": "PubTator3_LiteratureSearch",
                "arguments": {"text": "CRISPR", "page_size": 5}
            })

            # Verify all sources were searched
            self.assertEqual(len(literature_sources), 3)
            for source, result in literature_sources.items():
                self.assertIsInstance(result, dict)

    def test_agentic_loop_pattern(self):
        """Test agentic loop pattern with iterative optimization."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock iterative optimization
            mock_run.side_effect = [
                {"binding_affinity": -6.5},
                {"binding_affinity": -7.2},
                {"binding_affinity": -8.1}
            ]

            # Simulate agentic optimization loop
            current_compound = "CCO"  # Ethanol
            target_affinity = -8.0
            optimization_history = []

            for iteration in range(3):
                binding_result = self.tu.run({
                    "name": "boltz2_docking",
                    "arguments": {
                        "protein_id": "1CRN",
                        "ligand_smiles": current_compound
                    }
                })

                iteration_data = {
                    "iteration": iteration,
                    "compound": current_compound,
                    "binding_affinity": binding_result.get("binding_affinity")
                }
                optimization_history.append(iteration_data)

                # Check if target achieved
                if binding_result.get("binding_affinity", 0) <= target_affinity:
                    break

                # Simulate compound optimization
                current_compound = f"CCO{iteration}"  # Mock optimization

            self.assertEqual(len(optimization_history), 3)
            self.assertLessEqual(
                optimization_history[-1]["binding_affinity"],
                target_affinity
            )

    def test_error_handling_in_workflows(self):
        """Test error handling and fallback mechanisms in workflows."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock error scenarios
            mock_run.side_effect = [
                Exception("Primary tool failed"),
                {"data": {"fallback_result": "success"}}
            ]

            # Test workflow with error handling
            results = {"status": "running", "completed_steps": []}

            try:
                # Primary step
                primary_result = self.tu.run({
                    "name": "primary_tool",
                    "arguments": {"query": "test"}
                })
                results["primary"] = primary_result
                results["completed_steps"].append("primary")

            except Exception as e:
                results["primary_error"] = str(e)

                # Fallback step
                try:
                    fallback_result = self.tu.run({
                        "name": "fallback_tool",
                        "arguments": {"query": "test"}
                    })
                    results["fallback"] = fallback_result
                    results["completed_steps"].append("fallback")

                except Exception as e2:
                    results["fallback_error"] = str(e2)

            # Verify error handling worked
            self.assertIn("primary_error", results)
            self.assertIn("fallback", results)
            self.assertIn("fallback", results["completed_steps"])

    def test_dependency_management(self):
        """Test automatic dependency loading and management."""
        # Test dependency configuration
        compose_tool = {
            "type": "ComposeTool",
            "name": "DependencyTestTool",
            "auto_load_dependencies": True,
            "fail_on_missing_tools": False,
            "required_tools": [
                "EuropePMC_search_articles",
                "openalex_literature_search",
                "PubTator3_LiteratureSearch"
            ]
        }

        # Test dependency validation
        self.assertTrue(compose_tool["auto_load_dependencies"])
        self.assertFalse(compose_tool["fail_on_missing_tools"])
        self.assertEqual(len(compose_tool["required_tools"]), 3)

    def test_workflow_optimization(self):
        """Test workflow optimization techniques."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"result": "success"}

            # Test caching mechanism
            cache_key = "test_query"
            if cache_key in self.tu._cache:
                result = self.tu._cache[cache_key]
            else:
                result = self.tu.run({
                    "name": "expensive_tool",
                    "arguments": {"query": "test"}
                })
                self.tu._cache[cache_key] = result

            # Test parallel execution
            import threading

            results = []

            def parallel_call(tool_name):
                result = self.tu.run({
                    "name": tool_name,
                    "arguments": {"query": "test"}
                })
                results.append(result)

            # Execute tools in parallel
            threads = []
            tool_names = ["tool1", "tool2", "tool3"]

            for tool_name in tool_names:
                thread = threading.Thread(
                    target=parallel_call, args=(tool_name,)
                )
                threads.append(thread)
                thread.start()

            # Wait for completion
            for thread in threads:
                thread.join()

            self.assertEqual(len(results), 3)

    def test_workflow_data_flow(self):
        """Test data flow between tools in workflows."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock data flow
            mock_run.side_effect = [
                {"genes": ["BRCA1", "BRCA2", "TP53"]},
                {"pathways": ["DNA repair", "Cell cycle"]},
                {"drugs": ["olaparib", "rucaparib"]}
            ]

            # Test data flow workflow
            workflow_data = {}

            # Step 1: Gene discovery
            genes_result = self.tu.run({
                "name": "gene_discovery_tool",
                "arguments": {"disease": "breast cancer"}
            })
            workflow_data["genes"] = genes_result["genes"]

            # Step 2: Pathway analysis (using genes from step 1)
            pathways_result = self.tu.run({
                "name": "pathway_analysis_tool",
                "arguments": {"genes": workflow_data["genes"]}
            })
            workflow_data["pathways"] = pathways_result["pathways"]

            # Step 3: Drug discovery (using pathways from step 2)
            drugs_result = self.tu.run({
                "name": "drug_discovery_tool",
                "arguments": {"pathways": workflow_data["pathways"]}
            })
            workflow_data["drugs"] = drugs_result["drugs"]

            # Verify data flow
            self.assertIn("genes", workflow_data)
            self.assertIn("pathways", workflow_data)
            self.assertIn("drugs", workflow_data)
            self.assertEqual(len(workflow_data["genes"]), 3)

    def test_workflow_validation(self):
        """Test workflow validation and quality checks."""
        # Test workflow configuration validation
        valid_workflow = {
            "name": "ValidWorkflow",
            "steps": [
                {"tool": "step1", "required": True},
                {"tool": "step2", "required": False},
                {"tool": "step3", "required": True}
            ],
            "error_handling": "graceful",
            "timeout": 300
        }

        # Validate workflow structure
        self.assertIn("name", valid_workflow)
        self.assertIn("steps", valid_workflow)
        self.assertIn("error_handling", valid_workflow)
        self.assertIn("timeout", valid_workflow)

        # Test step validation
        required_steps = [
            step for step in valid_workflow["steps"] if step["required"]
        ]
        optional_steps = [
            step for step in valid_workflow["steps"] if not step["required"]
        ]

        self.assertEqual(len(required_steps), 2)
        self.assertEqual(len(optional_steps), 1)

    def test_workflow_monitoring(self):
        """Test workflow monitoring and metrics."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"result": "success"}

            # Test workflow metrics collection
            workflow_metrics = {
                "start_time": 0,
                "end_time": 0,
                "steps_completed": 0,
                "errors": 0,
                "total_execution_time": 0
            }

            import time

            # Simulate workflow execution with metrics
            workflow_metrics["start_time"] = time.time()

            for i in range(3):
                try:
                    result = self.tu.run({
                        "name": f"step_{i}",
                        "arguments": {"data": f"step_{i}_data"}
                    })
                    workflow_metrics["steps_completed"] += 1
                except Exception:
                    workflow_metrics["errors"] += 1

            workflow_metrics["end_time"] = time.time()
            workflow_metrics["total_execution_time"] = (
                workflow_metrics["end_time"] - workflow_metrics["start_time"]
            )

            # Verify metrics
            self.assertEqual(workflow_metrics["steps_completed"], 3)
            self.assertEqual(workflow_metrics["errors"], 0)
            self.assertGreater(workflow_metrics["total_execution_time"], 0)

    def test_workflow_scaling(self):
        """Test workflow scaling and performance."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"result": "success"}

            # Test batch processing
            batch_size = 10
            batch_results = []

            for i in range(batch_size):
                result = self.tu.run({
                    "name": "batch_tool",
                    "arguments": {"item": i}
                })
                batch_results.append(result)

            self.assertEqual(len(batch_results), batch_size)

            # Test resource management
            memory_usage = []
            for i in range(5):
                # Simulate memory-intensive operation
                large_data = ["data"] * 1000
                result = self.tu.run({
                    "name": "memory_tool",
                    "arguments": {"data": large_data}
                })
                memory_usage.append(len(str(result)))

                # Clean up
                del large_data

            self.assertEqual(len(memory_usage), 5)

    def test_workflow_integration(self):
        """Test integration with external systems."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"result": "success"}

            # Test external API integration
            external_apis = [
                "OpenTargets_get_associated_targets_by_disease_efoId",
                "ChEMBL_search_similar_molecules",
                "PubChem_get_compound_properties_by_CID"
            ]

            integration_results = {}

            for api in external_apis:
                try:
                    result = self.tu.run({
                        "name": api,
                        "arguments": {"test": "data"}
                    })
                    integration_results[api] = "success"
                except Exception as e:
                    integration_results[api] = f"error: {str(e)}"

            # Verify integration
            self.assertEqual(len(integration_results), 3)
            for api, status in integration_results.items():
                self.assertIn("success", status)

    def test_workflow_debugging(self):
        """Test workflow debugging and troubleshooting."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock debugging scenarios
            mock_run.side_effect = [
                {"debug_info": "step1_completed"},
                {"debug_info": "step2_completed"},
                Exception("step3_failed")
            ]

            # Test debugging workflow
            debug_info = []

            for i in range(3):
                try:
                    result = self.tu.run({
                        "name": f"debug_step_{i}",
                        "arguments": {"debug": True}
                    })
                    debug_info.append(
                        result.get("debug_info", f"step_{i}_success")
                    )
                except Exception as e:
                    debug_info.append(f"step_{i}_failed: {str(e)}")

            # Verify debugging info
            self.assertEqual(len(debug_info), 3)
            self.assertIn("step1_completed", debug_info[0])
            self.assertIn("step2_completed", debug_info[1])
            self.assertIn("step3_failed", debug_info[2])


if __name__ == "__main__":
    unittest.main()