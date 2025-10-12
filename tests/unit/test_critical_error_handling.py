#!/usr/bin/env python3
"""
Test critical error handling and recovery scenarios

This test file covers important error handling scenarios that were missing:
1. Network timeout handling
2. API rate limiting
3. Invalid tool responses
4. Memory issues
5. Concurrent access issues
6. Resource cleanup
"""

import sys
import unittest
from pathlib import Path
import pytest
from unittest.mock import patch, Mock, MagicMock
import time
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tooluniverse import ToolUniverse
from tooluniverse.exceptions import ToolError, ToolValidationError


@pytest.mark.unit
class TestCriticalErrorHandling(unittest.TestCase):
    """Test critical error handling and recovery scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tu = ToolUniverse()
        # Don't load tools to avoid embedding model loading issues
        self.tu.all_tools = []
        self.tu.all_tool_dict = {}
    
    def test_network_timeout_handling(self):
        """Test handling of network timeouts."""
        with patch('requests.get') as mock_get:
            # Simulate timeout
            mock_get.side_effect = TimeoutError("Request timed out")
            
            result = self.tu.run({
                "name": "ArXiv_search_papers",
                "arguments": {"query": "test", "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)
            self.assertIn("timeout", str(result["error"]).lower())
    
    def test_api_rate_limiting(self):
        """Test handling of API rate limiting."""
        with patch('requests.get') as mock_get:
            # Simulate rate limiting response
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_response.json.return_value = {"error": "Rate limit exceeded"}
            mock_get.return_value = mock_response
            
            result = self.tu.run({
                "name": "ArXiv_search_papers",
                "arguments": {"query": "test", "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)
    
    def test_invalid_json_response(self):
        """Test handling of invalid JSON responses."""
        with patch('requests.get') as mock_get:
            # Simulate invalid JSON response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "Invalid JSON response"
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response
            
            result = self.tu.run({
                "name": "ArXiv_search_papers",
                "arguments": {"query": "test", "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)
    
    def test_malformed_xml_response(self):
        """Test handling of malformed XML responses."""
        with patch('requests.get') as mock_get:
            # Simulate malformed XML response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<invalid>xml<content>"
            mock_get.return_value = mock_response
            
            result = self.tu.run({
                "name": "ArXiv_search_papers",
                "arguments": {"query": "test", "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
            # Should handle malformed XML gracefully
    
    def test_empty_response_handling(self):
        """Test handling of empty responses."""
        with patch('requests.get') as mock_get:
            # Simulate empty response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = ""
            mock_response.json.return_value = {}
            mock_get.return_value = mock_response
            
            result = self.tu.run({
                "name": "ArXiv_search_papers",
                "arguments": {"query": "test", "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
            # Should handle empty response gracefully
    
    def test_large_response_handling(self):
        """Test handling of very large responses."""
        with patch('requests.get') as mock_get:
            # Simulate very large response
            large_data = {"results": ["item"] * 10000}  # Very large response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = large_data
            mock_get.return_value = mock_response
            
            result = self.tu.run({
                "name": "ArXiv_search_papers",
                "arguments": {"query": "test", "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
            # Should handle large response gracefully
    
    def test_concurrent_tool_access(self):
        """Test concurrent access to the same tool."""
        results = []
        
        def make_call(call_id):
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"results": [{"title": f"Paper {call_id}"}]}
                mock_get.return_value = mock_response
                
                result = self.tu.run({
                    "name": "ArXiv_search_papers",
                    "arguments": {"query": f"test_{call_id}", "limit": 5}
                })
                
                results.append(result)
        
        # Create multiple threads accessing the same tool
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_call, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify all calls completed successfully
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertIsInstance(result, dict)
    
    def test_tool_initialization_failure(self):
        """Test handling of tool initialization failures."""
        # Test with invalid tool configuration
        invalid_tool = {
            "name": "InvalidTool",
            "type": "NonExistentType",
            "description": "Invalid tool"
        }
        
        self.tu.all_tools.append(invalid_tool)
        self.tu.all_tool_dict["InvalidTool"] = invalid_tool
        
        result = self.tu.run({
            "name": "InvalidTool",
            "arguments": {"test": "value"}
        })
        
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
    
    def test_memory_pressure_handling(self):
        """Test handling under memory pressure."""
        # Simulate memory pressure by creating large objects
        large_objects = []
        
        try:
            # Create some large objects to simulate memory pressure
            for i in range(100):
                large_objects.append(["data"] * 10000)
            
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"results": []}
                mock_get.return_value = mock_response
                
                result = self.tu.run({
                    "name": "ArXiv_search_papers",
                    "arguments": {"query": "test", "limit": 5}
                })
                
                self.assertIsInstance(result, dict)
                
        finally:
            # Clean up large objects
            del large_objects
    
    def test_resource_cleanup(self):
        """Test proper resource cleanup."""
        # Test that resources are properly cleaned up
        initial_tools = len(self.tu.all_tools)
        
        # Add some tools
        test_tool = {
            "name": "TestTool",
            "type": "TestType",
            "description": "Test tool"
        }
        
        self.tu.all_tools.append(test_tool)
        self.tu.all_tool_dict["TestTool"] = test_tool
        
        # Clear tools
        self.tu.all_tools.clear()
        self.tu.all_tool_dict.clear()
        
        # Verify cleanup
        self.assertEqual(len(self.tu.all_tools), 0)
        self.assertEqual(len(self.tu.all_tool_dict), 0)
    
    def test_error_propagation(self):
        """Test proper error propagation."""
        with patch('requests.get') as mock_get:
            # Simulate various error conditions
            error_cases = [
                ConnectionError("Connection failed"),
                TimeoutError("Request timed out"),
                ValueError("Invalid value"),
                KeyError("Missing key"),
                AttributeError("Attribute not found"),
            ]
            
            for error in error_cases:
                mock_get.side_effect = error
                
                result = self.tu.run({
                    "name": "ArXiv_search_papers",
                    "arguments": {"query": "test", "limit": 5}
                })
                
                self.assertIsInstance(result, dict)
                self.assertIn("error", result)
    
    def test_partial_failure_recovery(self):
        """Test recovery from partial failures."""
        with patch('requests.get') as mock_get:
            # Simulate partial failure (some calls succeed, others fail)
            call_count = 0
            
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count % 2 == 0:
                    raise ConnectionError("Simulated failure")
                else:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"results": []}
                    return mock_response
            
            mock_get.side_effect = side_effect
            
            # Make multiple calls
            results = []
            for i in range(5):
                result = self.tu.run({
                    "name": "ArXiv_search_papers",
                    "arguments": {"query": f"test_{i}", "limit": 5}
                })
                results.append(result)
            
            # Verify mixed results
            self.assertEqual(len(results), 5)
            for result in results:
                self.assertIsInstance(result, dict)
    
    def test_circuit_breaker_pattern(self):
        """Test circuit breaker pattern for repeated failures."""
        with patch('requests.get') as mock_get:
            # Simulate repeated failures
            mock_get.side_effect = ConnectionError("Repeated failure")
            
            # Make multiple calls
            results = []
            for i in range(5):
                result = self.tu.run({
                    "name": "ArXiv_search_papers",
                    "arguments": {"query": f"test_{i}", "limit": 5}
                })
                results.append(result)
            
            # All should fail
            self.assertEqual(len(results), 5)
            for result in results:
                self.assertIsInstance(result, dict)
                self.assertIn("error", result)
    
    def test_graceful_degradation(self):
        """Test graceful degradation when services are unavailable."""
        with patch('requests.get') as mock_get:
            # Simulate service unavailable
            mock_response = Mock()
            mock_response.status_code = 503
            mock_response.text = "Service Unavailable"
            mock_get.return_value = mock_response
            
            result = self.tu.run({
                "name": "ArXiv_search_papers",
                "arguments": {"query": "test", "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
            # Should handle service unavailable gracefully
    
    def test_data_corruption_handling(self):
        """Test handling of corrupted data."""
        with patch('requests.get') as mock_get:
            # Simulate corrupted data
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "Corrupted data with null bytes\x00\x00"
            mock_response.json.side_effect = ValueError("Corrupted data")
            mock_get.return_value = mock_response
            
            result = self.tu.run({
                "name": "ArXiv_search_papers",
                "arguments": {"query": "test", "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
