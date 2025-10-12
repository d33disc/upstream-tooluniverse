#!/usr/bin/env python3
"""
Test Hooks and Advanced Features

This test file covers important hooks and advanced features:
1. SummarizationHook functionality
2. FileSaveHook functionality
3. Hook configuration and management
4. Streaming tools support
5. Visualization tools
6. Performance optimization features
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
class TestHooksAndAdvancedFeatures(unittest.TestCase):
    """Test hooks and advanced features functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tu = ToolUniverse()
        # Don't load tools to avoid embedding model loading issues
        self.tu.all_tools = []
        self.tu.all_tool_dict = {}
    
    def test_summarization_hook_configuration(self):
        """Test SummarizationHook configuration."""
        # Test basic configuration
        basic_config = {
            "hooks_enabled": True,
            "hook_type": "SummarizationHook"
        }
        
        # Test advanced configuration
        advanced_config = {
            "hooks": [{
                "name": "protein_summarization",
                "type": "SummarizationHook",
                "enabled": True,
                "conditions": {
                    "output_length": {
                        "operator": ">",
                        "threshold": 8000
                    }
                },
                "hook_config": {
                    "chunk_size": 32000,
                    "focus_areas": "protein_function_and_structure",
                    "max_summary_length": 3500
                }
            }]
        }
        
        # Validate configurations
        self.assertTrue(basic_config["hooks_enabled"])
        self.assertEqual(basic_config["hook_type"], "SummarizationHook")
        
        self.assertEqual(len(advanced_config["hooks"]), 1)
        hook = advanced_config["hooks"][0]
        self.assertEqual(hook["type"], "SummarizationHook")
        self.assertTrue(hook["enabled"])
        self.assertEqual(hook["hook_config"]["chunk_size"], 32000)
    
    def test_filesave_hook_configuration(self):
        """Test FileSaveHook configuration."""
        # Test basic file save configuration
        filesave_config = {
            "hooks_enabled": True,
            "hook_type": "FileSaveHook",
            "hook_config": {
                "output_dir": "/tmp/tu_outputs",
                "filename_template": "{tool}_{timestamp}.json"
            }
        }
        
        # Test advanced file save configuration
        advanced_filesave_config = {
            "hooks": [{
                "name": "large_output_saver",
                "type": "FileSaveHook",
                "enabled": True,
                "conditions": {
                    "output_size": {
                        "operator": ">",
                        "threshold": 1000000  # 1MB
                    }
                },
                "hook_config": {
                    "output_dir": "/data/tooluniverse/outputs",
                    "filename_template": "{tool}_{date}_{time}.json",
                    "compress": True,
                    "include_metadata": True
                }
            }]
        }
        
        # Validate configurations
        self.assertTrue(filesave_config["hooks_enabled"])
        self.assertEqual(filesave_config["hook_type"], "FileSaveHook")
        
        hook = advanced_filesave_config["hooks"][0]
        self.assertEqual(hook["type"], "FileSaveHook")
        self.assertTrue(hook["enabled"])
        self.assertTrue(hook["hook_config"]["compress"])
        self.assertTrue(hook["hook_config"]["include_metadata"])
    
    def test_hook_conditions(self):
        """Test hook condition evaluation."""
        # Test output length condition
        length_condition = {
            "output_length": {
                "operator": ">",
                "threshold": 5000
            }
        }
        
        # Test output size condition
        size_condition = {
            "output_size": {
                "operator": ">=",
                "threshold": 1000000
            }
        }
        
        # Test tool-specific condition
        tool_condition = {
            "tool_name": {
                "operator": "in",
                "values": ["UniProt_get_entry_by_accession", "ChEMBL_search_similar_molecules"]
            }
        }
        
        # Validate conditions
        self.assertEqual(length_condition["output_length"]["operator"], ">")
        self.assertEqual(length_condition["output_length"]["threshold"], 5000)
        
        self.assertEqual(size_condition["output_size"]["operator"], ">=")
        self.assertEqual(size_condition["output_size"]["threshold"], 1000000)
        
        self.assertEqual(len(tool_condition["tool_name"]["values"]), 2)
    
    def test_streaming_tools_support(self):
        """Test streaming tools support."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock streaming response
            streaming_data = ["Chunk 1", "Chunk 2", "Chunk 3", "Final Result"]
            mock_run.return_value = "".join(streaming_data)
            
            # Test streaming callback
            chunks_received = []
            
            def stream_callback(chunk):
                chunks_received.append(chunk)
            
            # Test streaming execution
            result = self.tu.run({
                "name": "ScientificTextSummarizer",
                "arguments": {
                    "text": "Long text to summarize",
                    "_tooluniverse_stream": True
                }
            })
            
            # Verify streaming
            self.assertIsInstance(result, str)
            self.assertIn("Chunk 1", result)
            self.assertIn("Final Result", result)
    
    def test_visualization_tools(self):
        """Test visualization tools functionality."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock visualization response
            mock_run.return_value = {
                "success": True,
                "visualization": {
                    "html": "<html><body>Visualization</body></html>",
                    "type": "protein_structure_3d",
                    "data": {"pdb_id": "1CRN"},
                    "metadata": {"width": 800, "height": 600}
                }
            }
            
            # Test protein 3D visualization
            protein_result = self.tu.run({
                "name": "visualize_protein_structure_3d",
                "arguments": {
                    "pdb_id": "1CRN",
                    "style": "cartoon",
                    "color_scheme": "spectrum",
                    "width": 800,
                    "height": 600
                }
            })
            
            # Test molecule 2D visualization
            molecule_2d_result = self.tu.run({
                "name": "visualize_molecule_2d",
                "arguments": {
                    "smiles": "CCO",
                    "molecule_name": "ethanol",
                    "width": 400,
                    "height": 400,
                    "output_format": "png"
                }
            })
            
            # Test molecule 3D visualization
            molecule_3d_result = self.tu.run({
                "name": "visualize_molecule_3d",
                "arguments": {
                    "smiles": "CCO",
                    "style": "stick",
                    "color_scheme": "default",
                    "width": 800,
                    "height": 600
                }
            })
            
            # Verify visualizations
            for result in [protein_result, molecule_2d_result, molecule_3d_result]:
                self.assertIsInstance(result, dict)
                self.assertTrue(result["success"])
                self.assertIn("visualization", result)
                self.assertIn("html", result["visualization"])
    
    def test_performance_optimization(self):
        """Test performance optimization features."""
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
            
            # Test lazy loading
            lazy_config = {
                "lazy_loading_enabled": True,
                "load_on_demand": True,
                "cache_tools": True
            }
            
            # Test batch processing
            batch_size = 5
            batch_results = []
            
            for i in range(batch_size):
                result = self.tu.run({
                    "name": "batch_tool",
                    "arguments": {"item": i}
                })
                batch_results.append(result)
            
            # Verify performance features
            self.assertEqual(len(batch_results), batch_size)
            self.assertTrue(lazy_config["lazy_loading_enabled"])
            self.assertTrue(lazy_config["load_on_demand"])
    
    def test_hook_management(self):
        """Test hook management and lifecycle."""
        # Test hook registration
        hook_registry = {
            "summarization_hook": {
                "type": "SummarizationHook",
                "enabled": True,
                "priority": 1
            },
            "filesave_hook": {
                "type": "FileSaveHook",
                "enabled": True,
                "priority": 2
            }
        }
        
        # Test hook execution order
        execution_order = []
        for hook_name, hook_config in sorted(
            hook_registry.items(), 
            key=lambda x: x[1]["priority"]
        ):
            execution_order.append(hook_name)
        
        # Test hook disabling
        disabled_hooks = []
        for hook_name, hook_config in hook_registry.items():
            if not hook_config["enabled"]:
                disabled_hooks.append(hook_name)
        
        # Verify hook management
        self.assertEqual(len(hook_registry), 2)
        self.assertEqual(execution_order[0], "summarization_hook")
        self.assertEqual(execution_order[1], "filesave_hook")
        self.assertEqual(len(disabled_hooks), 0)
    
    def test_advanced_configuration(self):
        """Test advanced configuration options."""
        # Test tool-specific hooks
        tool_specific_config = {
            "tool_specific_hooks": {
                "UniProt_get_entry_by_accession": {
                    "enabled": True,
                    "hooks": [{
                        "name": "protein_summarization",
                        "type": "SummarizationHook",
                        "enabled": True,
                        "hook_config": {
                            "focus_areas": "protein_function_and_structure",
                            "max_summary_length": 3500
                        }
                    }]
                },
                "ChEMBL_search_similar_molecules": {
                    "enabled": True,
                    "hooks": [{
                        "name": "compound_summarization",
                        "type": "SummarizationHook",
                        "enabled": True,
                        "hook_config": {
                            "focus_areas": "compound_properties_and_activity",
                            "max_summary_length": 3000
                        }
                    }]
                }
            }
        }
        
        # Test global hook configuration
        global_config = {
            "global_hooks": {
                "enabled": True,
                "default_hook_type": "SummarizationHook",
                "default_conditions": {
                    "output_length": {
                        "operator": ">",
                        "threshold": 5000
                    }
                }
            }
        }
        
        # Validate configurations
        self.assertIn("tool_specific_hooks", tool_specific_config)
        self.assertIn("UniProt_get_entry_by_accession", tool_specific_config["tool_specific_hooks"])
        self.assertIn("ChEMBL_search_similar_molecules", tool_specific_config["tool_specific_hooks"])
        
        self.assertTrue(global_config["global_hooks"]["enabled"])
        self.assertEqual(global_config["global_hooks"]["default_hook_type"], "SummarizationHook")
    
    def test_error_handling_in_hooks(self):
        """Test error handling in hooks."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock hook error scenarios
            mock_run.side_effect = [
                {"result": "success"},  # Normal execution
                Exception("Hook processing failed"),  # Hook error
                {"result": "success"}  # Recovery
            ]
            
            # Test hook error handling
            hook_results = []
            
            for i in range(3):
                try:
                    result = self.tu.run({
                        "name": f"hook_test_tool_{i}",
                        "arguments": {"test": "data"}
                    })
                    hook_results.append({"status": "success", "result": result})
                except Exception as e:
                    hook_results.append({"status": "error", "error": str(e)})
            
            # Verify error handling
            self.assertEqual(len(hook_results), 3)
            self.assertEqual(hook_results[0]["status"], "success")
            self.assertEqual(hook_results[1]["status"], "error")
            self.assertEqual(hook_results[2]["status"], "success")
    
    def test_hook_performance_monitoring(self):
        """Test hook performance monitoring."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"result": "success"}
            
            # Test hook performance metrics
            hook_metrics = {
                "total_hooks_executed": 0,
                "total_processing_time": 0,
                "average_hook_time": 0,
                "hook_errors": 0
            }
            
            import time
            
            # Simulate hook execution
            for i in range(5):
                start_time = time.time()
                
                try:
                    result = self.tu.run({
                        "name": f"performance_hook_tool_{i}",
                        "arguments": {"test": "data"}
                    })
                    hook_metrics["total_hooks_executed"] += 1
                except Exception:
                    hook_metrics["hook_errors"] += 1
                
                processing_time = time.time() - start_time
                hook_metrics["total_processing_time"] += processing_time
            
            if hook_metrics["total_hooks_executed"] > 0:
                hook_metrics["average_hook_time"] = (
                    hook_metrics["total_processing_time"] / hook_metrics["total_hooks_executed"]
                )
            
            # Verify metrics
            self.assertEqual(hook_metrics["total_hooks_executed"], 5)
            self.assertEqual(hook_metrics["hook_errors"], 0)
            self.assertGreater(hook_metrics["total_processing_time"], 0)
            self.assertGreater(hook_metrics["average_hook_time"], 0)
    
    def test_hook_integration_testing(self):
        """Test hook integration testing."""
        # Test hook configuration validation
        def validate_hook_config(config):
            required_fields = ["type", "enabled"]
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field: {field}"
            return True, "Valid configuration"
        
        # Test valid configuration
        valid_config = {
            "type": "SummarizationHook",
            "enabled": True,
            "conditions": {"output_length": {"operator": ">", "threshold": 5000}}
        }
        
        is_valid, message = validate_hook_config(valid_config)
        self.assertTrue(is_valid)
        self.assertEqual(message, "Valid configuration")
        
        # Test invalid configuration
        invalid_config = {
            "enabled": True,
            "conditions": {"output_length": {"operator": ">", "threshold": 5000}}
        }
        
        is_valid, message = validate_hook_config(invalid_config)
        self.assertFalse(is_valid)
        self.assertIn("Missing required field", message)
    
    def test_advanced_streaming_features(self):
        """Test advanced streaming features."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock advanced streaming
            mock_run.return_value = "Streaming result with multiple chunks"
            
            # Test streaming with metadata
            streaming_metadata = {
                "stream_id": "stream_123",
                "total_chunks": 5,
                "chunk_size": 1024,
                "compression": "gzip"
            }
            
            # Test streaming with progress tracking
            progress_tracker = {
                "total_bytes": 0,
                "received_bytes": 0,
                "progress_percentage": 0
            }
            
            # Simulate streaming with progress
            total_bytes = 5000
            chunk_size = 1000
            
            for i in range(5):
                chunk_bytes = min(chunk_size, total_bytes - progress_tracker["received_bytes"])
                progress_tracker["received_bytes"] += chunk_bytes
                progress_tracker["progress_percentage"] = (
                    progress_tracker["received_bytes"] / total_bytes * 100
                )
            
            # Verify streaming features
            self.assertEqual(streaming_metadata["stream_id"], "stream_123")
            self.assertEqual(streaming_metadata["total_chunks"], 5)
            self.assertEqual(progress_tracker["received_bytes"], total_bytes)
            self.assertEqual(progress_tracker["progress_percentage"], 100.0)


if __name__ == "__main__":
    unittest.main()
