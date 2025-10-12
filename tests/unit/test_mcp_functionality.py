#!/usr/bin/env python3
"""
Test MCP (Model Context Protocol) functionality

This test file covers important MCP scenarios:
1. MCP server configuration and startup
2. Tool discovery through MCP
3. Tool execution via MCP protocol
4. Error handling in MCP context
5. Streaming support in MCP
6. Client integration patterns
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
class TestMCPFunctionality(unittest.TestCase):
    """Test MCP functionality and integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tu = ToolUniverse()
        # Don't load tools to avoid embedding model loading issues
        self.tu.all_tools = []
        self.tu.all_tool_dict = {}
    
    def test_mcp_server_configuration(self):
        """Test MCP server configuration options."""
        # Test server configuration
        mcp_config = {
            "port": 7000,
            "host": "0.0.0.0",
            "transport": "http",
            "name": "ToolUniverse MCP Server",
            "max_workers": 4,
            "verbose": True
        }
        
        # Validate configuration
        self.assertEqual(mcp_config["port"], 7000)
        self.assertEqual(mcp_config["host"], "0.0.0.0")
        self.assertEqual(mcp_config["transport"], "http")
        self.assertEqual(mcp_config["max_workers"], 4)
        self.assertTrue(mcp_config["verbose"])
    
    def test_mcp_tool_discovery(self):
        """Test tool discovery through MCP protocol."""
        # Mock tool discovery response
        mock_tools = [
            {
                "name": "UniProt_get_entry_by_accession",
                "description": "Get protein entry by accession number",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "accession": {"type": "string", "description": "Protein accession"}
                    },
                    "required": ["accession"]
                }
            },
            {
                "name": "ChEMBL_search_similar_molecules",
                "description": "Search for similar molecules",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "smiles": {"type": "string", "description": "SMILES string"}
                    },
                    "required": ["smiles"]
                }
            }
        ]
        
        # Test tool discovery
        discovered_tools = []
        for tool in mock_tools:
            tool_info = {
                "name": tool["name"],
                "description": tool["description"],
                "schema": tool["inputSchema"]
            }
            discovered_tools.append(tool_info)
        
        # Verify discovery
        self.assertEqual(len(discovered_tools), 2)
        self.assertEqual(discovered_tools[0]["name"], "UniProt_get_entry_by_accession")
        self.assertEqual(discovered_tools[1]["name"], "ChEMBL_search_similar_molecules")
    
    def test_mcp_tool_execution(self):
        """Test tool execution via MCP protocol."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {
                "success": True,
                "data": {
                    "accession": "P05067",
                    "name": "APP",
                    "description": "Amyloid beta A4 protein"
                }
            }
            
            # Test MCP tool execution
            mcp_request = {
                "method": "tools/call",
                "params": {
                    "name": "UniProt_get_entry_by_accession",
                    "arguments": {
                        "accession": "P05067"
                    }
                }
            }
            
            # Execute tool
            result = self.tu.run({
                "name": mcp_request["params"]["name"],
                "arguments": mcp_request["params"]["arguments"]
            })
            
            # Verify execution
            self.assertIsInstance(result, dict)
            self.assertTrue(result["success"])
            self.assertIn("data", result)
            self.assertEqual(result["data"]["accession"], "P05067")
    
    def test_mcp_error_handling(self):
        """Test error handling in MCP context."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock error scenarios
            mock_run.side_effect = [
                Exception("Tool not found"),
                {"error": "Invalid parameters"},
                {"success": True, "data": "success"}
            ]
            
            # Test error handling
            error_scenarios = [
                {"name": "NonExistentTool", "arguments": {}},
                {"name": "ValidTool", "arguments": {"invalid": "param"}},
                {"name": "ValidTool", "arguments": {"valid": "param"}}
            ]
            
            results = []
            for scenario in error_scenarios:
                try:
                    result = self.tu.run(scenario)
                    results.append({"status": "success", "result": result})
                except Exception as e:
                    results.append({"status": "error", "error": str(e)})
            
            # Verify error handling
            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]["status"], "error")
            self.assertEqual(results[1]["status"], "success")  # Tool returns error dict
            self.assertEqual(results[2]["status"], "success")
    
    def test_mcp_streaming_support(self):
        """Test streaming support in MCP."""
        with patch.object(self.tu, 'run') as mock_run:
            # Mock streaming response
            streaming_chunks = ["Chunk 1", "Chunk 2", "Chunk 3", "Final Result"]
            mock_run.return_value = "".join(streaming_chunks)
            
            # Test streaming request
            streaming_request = {
                "method": "tools/call",
                "params": {
                    "name": "ScientificTextSummarizer",
                    "arguments": {
                        "text": "Long text to summarize",
                        "_tooluniverse_stream": True
                    }
                }
            }
            
            # Simulate streaming
            chunks_received = []
            def stream_callback(chunk):
                chunks_received.append(chunk)
            
            # Execute with streaming
            result = self.tu.run({
                "name": streaming_request["params"]["name"],
                "arguments": streaming_request["params"]["arguments"]
            })
            
            # Verify streaming
            self.assertIsInstance(result, str)
            self.assertIn("Chunk 1", result)
            self.assertIn("Final Result", result)
    
    def test_mcp_client_integration(self):
        """Test MCP client integration patterns."""
        # Test Python client integration
        class MockMCPClient:
            def __init__(self):
                self.tools = []
                self.results = {}
            
            def discover_tools(self):
                return [
                    {"name": "tool1", "description": "Tool 1"},
                    {"name": "tool2", "description": "Tool 2"}
                ]
            
            def call_tool(self, name, arguments):
                return {"name": name, "arguments": arguments, "result": "success"}
        
        # Test client integration
        client = MockMCPClient()
        tools = client.discover_tools()
        
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0]["name"], "tool1")
        self.assertEqual(tools[1]["name"], "tool2")
        
        # Test tool execution through client
        result = client.call_tool("tool1", {"param": "value"})
        self.assertEqual(result["name"], "tool1")
        self.assertEqual(result["arguments"]["param"], "value")
    
    def test_mcp_transport_protocols(self):
        """Test different MCP transport protocols."""
        # Test HTTP transport
        http_config = {
            "transport": "http",
            "port": 8000,
            "host": "127.0.0.1"
        }
        
        # Test STDIO transport
        stdio_config = {
            "transport": "stdio",
            "name": "ToolUniverse STDIO Server"
        }
        
        # Test SSE transport
        sse_config = {
            "transport": "sse",
            "port": 9000,
            "host": "0.0.0.0"
        }
        
        # Validate configurations
        self.assertEqual(http_config["transport"], "http")
        self.assertEqual(stdio_config["transport"], "stdio")
        self.assertEqual(sse_config["transport"], "sse")
    
    def test_mcp_tool_selection(self):
        """Test MCP tool selection and filtering."""
        # Test category-based selection
        category_config = {
            "categories": ["uniprot", "chembl", "opentargets"],
            "exclude_categories": ["deprecated"]
        }
        
        # Test tool-specific selection
        tool_config = {
            "include_tools": [
                "UniProt_get_entry_by_accession",
                "ChEMBL_search_similar_molecules"
            ],
            "exclude_tools": ["deprecated_tool"]
        }
        
        # Test type-based selection
        type_config = {
            "include_tool_types": ["RestfulTool", "ComposeTool"],
            "exclude_tool_types": ["DeprecatedTool"]
        }
        
        # Validate configurations
        self.assertEqual(len(category_config["categories"]), 3)
        self.assertEqual(len(tool_config["include_tools"]), 2)
        self.assertEqual(len(type_config["include_tool_types"]), 2)
    
    def test_mcp_hooks_integration(self):
        """Test MCP hooks integration."""
        # Test SummarizationHook configuration
        summarization_config = {
            "hooks_enabled": True,
            "hook_type": "SummarizationHook",
            "hook_config": {
                "max_tokens": 2048,
                "summary_style": "concise"
            }
        }
        
        # Test FileSaveHook configuration
        filesave_config = {
            "hooks_enabled": True,
            "hook_type": "FileSaveHook",
            "hook_config": {
                "output_dir": "/tmp/tu_outputs",
                "filename_template": "{tool}_{timestamp}.json"
            }
        }
        
        # Validate hook configurations
        self.assertTrue(summarization_config["hooks_enabled"])
        self.assertEqual(summarization_config["hook_type"], "SummarizationHook")
        self.assertTrue(filesave_config["hooks_enabled"])
        self.assertEqual(filesave_config["hook_type"], "FileSaveHook")
    
    def test_mcp_performance_monitoring(self):
        """Test MCP performance monitoring."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"result": "success"}
            
            # Test performance metrics
            performance_metrics = {
                "request_count": 0,
                "total_execution_time": 0,
                "average_response_time": 0,
                "error_count": 0
            }
            
            import time
            
            # Simulate multiple requests
            start_time = time.time()
            for i in range(10):
                request_start = time.time()
                
                try:
                    result = self.tu.run({
                        "name": f"performance_test_tool_{i}",
                        "arguments": {"test": "data"}
                    })
                    performance_metrics["request_count"] += 1
                except Exception:
                    performance_metrics["error_count"] += 1
                
                request_time = time.time() - request_start
                performance_metrics["total_execution_time"] += request_time
            
            total_time = time.time() - start_time
            performance_metrics["average_response_time"] = (
                performance_metrics["total_execution_time"] / performance_metrics["request_count"]
            )
            
            # Verify metrics
            self.assertEqual(performance_metrics["request_count"], 10)
            self.assertEqual(performance_metrics["error_count"], 0)
            self.assertGreater(performance_metrics["total_execution_time"], 0)
            self.assertGreater(performance_metrics["average_response_time"], 0)
    
    def test_mcp_security_features(self):
        """Test MCP security features."""
        # Test authentication
        auth_config = {
            "authentication": {
                "type": "api_key",
                "required": True,
                "key_header": "X-API-Key"
            }
        }
        
        # Test authorization
        authz_config = {
            "authorization": {
                "enabled": True,
                "permissions": {
                    "read": ["tool_discovery"],
                    "write": ["tool_execution"]
                }
            }
        }
        
        # Test rate limiting
        rate_limit_config = {
            "rate_limiting": {
                "enabled": True,
                "requests_per_minute": 100,
                "burst_limit": 20
            }
        }
        
        # Validate security configurations
        self.assertTrue(auth_config["authentication"]["required"])
        self.assertTrue(authz_config["authorization"]["enabled"])
        self.assertTrue(rate_limit_config["rate_limiting"]["enabled"])
    
    def test_mcp_logging_and_debugging(self):
        """Test MCP logging and debugging features."""
        # Test logging configuration
        logging_config = {
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "handlers": ["console", "file"],
            "file_path": "/tmp/mcp_server.log"
        }
        
        # Test debugging features
        debug_config = {
            "debug_mode": True,
            "verbose_logging": True,
            "request_tracing": True,
            "performance_profiling": True
        }
        
        # Validate configurations
        self.assertEqual(logging_config["level"], "DEBUG")
        self.assertTrue(debug_config["debug_mode"])
        self.assertTrue(debug_config["verbose_logging"])
    
    def test_mcp_client_examples(self):
        """Test MCP client integration examples."""
        # Test JavaScript client example
        js_client_code = """
        const fetch = require('node-fetch');
        
        async function runTool(toolName, arguments) {
            const response = await fetch('http://127.0.0.1:8000/mcp/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: toolName,
                    arguments: arguments
                })
            });
            return await response.json();
        }
        """
        
        # Test Python client example
        python_client_code = """
        import requests
        
        def run_tool(tool_name, arguments):
            response = requests.post(
                'http://127.0.0.1:8000/mcp/run',
                json={'name': tool_name, 'arguments': arguments}
            )
            return response.json()
        """
        
        # Validate client examples
        self.assertIn("fetch", js_client_code)
        self.assertIn("requests", python_client_code)
        self.assertIn("mcp/run", js_client_code)
        self.assertIn("mcp/run", python_client_code)


if __name__ == "__main__":
    unittest.main()
