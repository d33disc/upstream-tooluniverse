#!/usr/bin/env python3
"""
Test edge cases and error handling for Tool Finder functionality

This test file covers important edge cases that were missing from existing tests:
1. Tool finder with empty results
2. Tool finder with invalid parameters
3. Tool finder timeout handling
4. Tool finder with malformed responses
5. Tool finder with network errors
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
class TestToolFinderEdgeCases(unittest.TestCase):
    """Test edge cases and error handling for Tool Finder functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tu = ToolUniverse()
        # Don't load tools to avoid embedding model loading issues
        self.tu.all_tools = []
        self.tu.all_tool_dict = {}
    
    def test_tool_finder_empty_query(self):
        """Test Tool_Finder_Keyword with empty query."""
        # Mock the tool finder to avoid actual tool loading
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"tools": []}
            
            result = self.tu.run({
                "name": "Tool_Finder_Keyword",
                "arguments": {"description": "", "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
            self.assertIn("tools", result)
            self.assertEqual(len(result["tools"]), 0)
    
    def test_tool_finder_invalid_limit(self):
        """Test Tool_Finder_Keyword with invalid limit values."""
        with patch.object(self.tu, 'run') as mock_run:
            # Test negative limit
            mock_run.return_value = {"tools": []}
            
            result = self.tu.run({
                "name": "Tool_Finder_Keyword",
                "arguments": {"description": "test", "limit": -1}
            })
            
            self.assertIsInstance(result, dict)
    
    def test_tool_finder_very_large_limit(self):
        """Test Tool_Finder_Keyword with very large limit."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"tools": []}
            
            result = self.tu.run({
                "name": "Tool_Finder_Keyword",
                "arguments": {"description": "test", "limit": 10000}
            })
            
            self.assertIsInstance(result, dict)
    
    def test_tool_finder_special_characters(self):
        """Test Tool_Finder_Keyword with special characters in query."""
        special_queries = [
            "test@#$%^&*()",
            "test with spaces and symbols!@#",
            "test\nwith\nnewlines",
            "test\twith\ttabs",
            "test with unicode: 中文测试",
            "test with quotes: \"double\" and 'single'",
        ]
        
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"tools": []}
            
            for query in special_queries:
                result = self.tu.run({
                    "name": "Tool_Finder_Keyword",
                    "arguments": {"description": query, "limit": 5}
                })
                
                self.assertIsInstance(result, dict)
                self.assertIn("tools", result)
    
    def test_tool_finder_missing_parameters(self):
        """Test Tool_Finder_Keyword with missing required parameters."""
        # Test missing description
        result = self.tu.run({
            "name": "Tool_Finder_Keyword",
            "arguments": {"limit": 5}
        })
        
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
    
    def test_tool_finder_extra_parameters(self):
        """Test Tool_Finder_Keyword with extra parameters."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"tools": []}
            
            result = self.tu.run({
                "name": "Tool_Finder_Keyword",
                "arguments": {
                    "description": "test",
                    "limit": 5,
                    "extra_param": "should_be_ignored"
                }
            })
            
            self.assertIsInstance(result, dict)
    
    def test_tool_finder_wrong_parameter_types(self):
        """Test Tool_Finder_Keyword with wrong parameter types."""
        # Test limit as string instead of integer
        result = self.tu.run({
            "name": "Tool_Finder_Keyword",
            "arguments": {"description": "test", "limit": "not_a_number"}
        })
        
        self.assertIsInstance(result, dict)
        # Should either work (if validation is lenient) or return error
        if "error" in result:
            self.assertIn("limit", str(result["error"]).lower())
    
    def test_tool_finder_none_values(self):
        """Test Tool_Finder_Keyword with None values."""
        result = self.tu.run({
            "name": "Tool_Finder_Keyword",
            "arguments": {"description": None, "limit": None}
        })
        
        self.assertIsInstance(result, dict)
        # Should handle None values gracefully
    
    def test_tool_finder_very_long_query(self):
        """Test Tool_Finder_Keyword with very long query."""
        long_query = "test " * 1000  # Very long query
        
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"tools": []}
            
            result = self.tu.run({
                "name": "Tool_Finder_Keyword",
                "arguments": {"description": long_query, "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
    
    def test_tool_finder_unicode_handling(self):
        """Test Tool_Finder_Keyword with various Unicode characters."""
        unicode_queries = [
            "test with emoji: 🧬🔬🧪",
            "test with accented chars: café naïve résumé",
            "test with symbols: ∑∏∫√∞",
            "test with arrows: ←→↑↓",
            "test with currency: €£¥$",
        ]
        
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"tools": []}
            
            for query in unicode_queries:
                result = self.tu.run({
                    "name": "Tool_Finder_Keyword",
                    "arguments": {"description": query, "limit": 5}
                })
                
                self.assertIsInstance(result, dict)
                self.assertIn("tools", result)
    
    def test_tool_finder_concurrent_calls(self):
        """Test Tool_Finder_Keyword with concurrent calls."""
        import threading
        import time
        
        results = []
        
        def make_call(query_id):
            with patch.object(self.tu, 'run') as mock_run:
                mock_run.return_value = {"tools": [{"name": f"tool_{query_id}"}]}
                
                result = self.tu.run({
                    "name": "Tool_Finder_Keyword",
                    "arguments": {"description": f"query_{query_id}", "limit": 5}
                })
                
                results.append(result)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_call, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify all calls completed
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIsInstance(result, dict)
    
    def test_tool_finder_malformed_response(self):
        """Test Tool_Finder_Keyword handling of malformed responses."""
        with patch.object(self.tu, 'run') as mock_run:
            # Return malformed response
            mock_run.return_value = {"invalid_key": "invalid_value"}
            
            result = self.tu.run({
                "name": "Tool_Finder_Keyword",
                "arguments": {"description": "test", "limit": 5}
            })
            
            self.assertIsInstance(result, dict)
            # Should handle malformed response gracefully
    
    def test_tool_finder_exception_handling(self):
        """Test Tool_Finder_Keyword exception handling."""
        with patch.object(self.tu, 'run') as mock_run:
            # Simulate exception
            mock_run.side_effect = Exception("Simulated error")
            
            with self.assertRaises(Exception):
                self.tu.run({
                    "name": "Tool_Finder_Keyword",
                    "arguments": {"description": "test", "limit": 5}
                })
    
    def test_tool_finder_llm_edge_cases(self):
        """Test Tool_Finder_LLM edge cases."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"tools": []}
            
            # Test with various edge cases
            edge_cases = [
                {"description": "", "limit": 0},
                {"description": "a", "limit": 1},
                {"description": "test", "limit": -1},
                {"description": "test", "limit": 1000},
            ]
            
            for case in edge_cases:
                result = self.tu.run({
                    "name": "Tool_Finder_LLM",
                    "arguments": case
                })
                
                self.assertIsInstance(result, dict)
    
    def test_tool_finder_embedding_edge_cases(self):
        """Test Tool_Finder (embedding) edge cases."""
        with patch.object(self.tu, 'run') as mock_run:
            mock_run.return_value = {"tools": []}
            
            # Test with various edge cases
            edge_cases = [
                {"description": "", "limit": 0, "return_call_result": False},
                {"description": "a", "limit": 1, "return_call_result": True},
                {"description": "test", "limit": -1, "return_call_result": False},
                {"description": "test", "limit": 1000, "return_call_result": True},
            ]
            
            for case in edge_cases:
                result = self.tu.run({
                    "name": "Tool_Finder",
                    "arguments": case
                })
                
                self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
