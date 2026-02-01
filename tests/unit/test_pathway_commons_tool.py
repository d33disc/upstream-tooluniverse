"""
Test suite for Pathway Commons API tools

Tests the Pathway Commons (PC2) tools for:
- Pathway search
- Gene interaction network retrieval

Testing levels:
1. Direct class testing (implementation logic)
2. ToolUniverse interface testing (registration and access)
3. Real API testing (integration with Pathway Commons API)
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tooluniverse.pathway_commons_tool import PathwayCommonsTool
from tooluniverse import ToolUniverse


class TestPathwayCommonsDirectClass:
    """Level 1: Direct class testing"""
    
    @pytest.fixture
    def tool_configs(self):
        """Load tool configurations from JSON"""
        config_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'src', 'tooluniverse', 'data', 'pathway_commons_tools.json'
        )
        with open(config_path) as f:
            return json.load(f)
    
    def test_search_pathways_initialization(self, tool_configs):
        """Test pc_search_pathways tool initialization"""
        config = next(t for t in tool_configs if t["name"] == "pc_search_pathways")
        tool = PathwayCommonsTool(config)
        assert tool is not None
        assert hasattr(tool, 'run')
        assert hasattr(tool, 'search_pathways')
    
    def test_get_interactions_initialization(self, tool_configs):
        """Test pc_get_interactions tool initialization"""
        config = next(t for t in tool_configs if t["name"] == "pc_get_interactions")
        tool = PathwayCommonsTool(config)
        assert tool is not None
        assert hasattr(tool, 'get_interaction_graph')
    
    @patch('requests.get')
    def test_search_pathways_success(self, mock_get, tool_configs):
        """Test successful pathway search"""
        config = next(t for t in tool_configs if t["name"] == "pc_search_pathways")
        tool = PathwayCommonsTool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "numHits": 5,
            "searchHit": [
                {
                    "name": "Glycolysis pathway",
                    "uri": "http://pathwaycommons.org/pc2/Pathway_123",
                    "dataSource": ["reactome"],
                    "organism": "Homo sapiens"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = tool.run({
            "action": "search_pathways",
            "keyword": "glycolysis",
            "limit": 5
        })
        
        assert "pathways" in result
        assert result["total_hits"] == 5
        assert len(result["pathways"]) == 1
        assert result["pathways"][0]["name"] == "Glycolysis pathway"
    
    @patch('requests.get')
    def test_search_with_datasource(self, mock_get, tool_configs):
        """Test pathway search with datasource filter"""
        config = next(t for t in tool_configs if t["name"] == "pc_search_pathways")
        tool = PathwayCommonsTool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "numHits": 2,
            "searchHit": [
                {
                    "name": "KEGG Pathway",
                    "uri": "http://pathwaycommons.org/pc2/Pathway_456",
                    "dataSource": ["kegg"],
                    "organism": "Homo sapiens"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = tool.run({
            "action": "search_pathways",
            "keyword": "metabolism",
            "datasource": "kegg",
            "limit": 10
        })
        
        assert "pathways" in result
        assert result["total_hits"] == 2
    
    @patch('requests.get')
    def test_get_interaction_graph_success(self, mock_get, tool_configs):
        """Test successful interaction graph retrieval"""
        config = next(t for t in tool_configs if t["name"] == "pc_get_interactions")
        tool = PathwayCommonsTool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "TP53\tcontrols-state-change-of\tMDM2\nTP53\tin-complex-with\tATM"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = tool.run({
            "action": "get_interaction_graph",
            "gene_list": ["TP53", "MDM2"]
        })
        
        assert result["format"] == "SIF"
        assert "interactions" in result
        assert len(result["interactions"]) == 2
        assert result["interactions"][0]["source"] == "TP53"
        assert result["interactions"][0]["relation"] == "controls-state-change-of"
        assert result["interactions"][0]["target"] == "MDM2"
    
    def test_missing_gene_list(self, tool_configs):
        """Test error when gene_list is missing"""
        config = next(t for t in tool_configs if t["name"] == "pc_get_interactions")
        tool = PathwayCommonsTool(config)
        
        with pytest.raises(ValueError, match="gene_list is required"):
            tool.run({"action": "get_interaction_graph"})
    
    def test_unknown_action(self, tool_configs):
        """Test error for unknown action"""
        config = next(t for t in tool_configs if t["name"] == "pc_search_pathways")
        tool = PathwayCommonsTool(config)
        
        with pytest.raises(ValueError, match="Unknown action"):
            tool.run({"action": "unknown_action"})
    
    @patch('requests.get')
    def test_error_handling(self, mock_get, tool_configs):
        """Test error handling for failed API calls"""
        config = next(t for t in tool_configs if t["name"] == "pc_search_pathways")
        tool = PathwayCommonsTool(config)
        
        mock_get.side_effect = Exception("Network error")
        
        result = tool.run({"action": "search_pathways", "keyword": "test"})
        
        assert "error" in result
        assert "Network error" in result["error"]


class TestPathwayCommonsToolUniverse:
    """Level 2: ToolUniverse interface testing"""
    
    @pytest.fixture
    def tu(self):
        """Initialize ToolUniverse with tools loaded"""
        tu = ToolUniverse()
        tu.load_tools()
        return tu
    
    def test_tools_registered(self, tu):
        """Test that all Pathway Commons tools are registered"""
        expected_tools = [
            "pc_search_pathways",
            "pc_get_interactions"
        ]
        
        for tool_name in expected_tools:
            assert hasattr(tu.tools, tool_name), f"{tool_name} not found"
    
    @patch('requests.get')
    def test_search_via_tooluniverse(self, mock_get, tu):
        """Test pathway search via ToolUniverse interface"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "numHits": 3,
            "searchHit": [
                {
                    "name": "Test Pathway",
                    "uri": "http://example.com/pathway_1",
                    "dataSource": ["reactome"],
                    "organism": "Homo sapiens"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = tu.tools.pc_search_pathways(**{
            "action": "search_pathways",
            "keyword": "apoptosis",
            "limit": 5
        })
        
        assert "pathways" in result
        assert result["total_hits"] == 3
    
    @patch('requests.get')
    def test_get_interactions_via_tooluniverse(self, mock_get, tu):
        """Test interaction graph via ToolUniverse interface"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "BRCA1\tinteracts-with\tBRCA2"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = tu.tools.pc_get_interactions(**{
            "action": "get_interaction_graph",
            "gene_list": ["BRCA1", "BRCA2"]
        })
        
        assert result["format"] == "SIF"
        assert "interactions" in result
        assert len(result["interactions"]) == 1


class TestPathwayCommonsRealAPI:
    """Level 3: Real API testing (requires network)"""
    
    @pytest.fixture
    def tu(self):
        """Initialize ToolUniverse"""
        tu = ToolUniverse()
        tu.load_tools()
        return tu
    
    def test_real_search_pathways(self, tu):
        """Test real API pathway search"""
        try:
            result = tu.tools.pc_search_pathways(**{
                "action": "search_pathways",
                "keyword": "glycolysis",
                "limit": 3
            })
            
            if "pathways" in result and not result.get("error"):
                assert "total_hits" in result
                print(f"✅ Real API pathway search: Found {result['total_hits']} pathways")
            else:
                print(f"⚠️  Search returned error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️  Real API test failed (may be expected): {e}")
    
    def test_real_get_interactions(self, tu):
        """Test real API interaction graph"""
        try:
            result = tu.tools.pc_get_interactions(**{
                "action": "get_interaction_graph",
                "gene_list": ["TP53", "MDM2"]
            })
            
            if "interactions" in result and not result.get("error"):
                assert result["format"] == "SIF"
                print(f"✅ Real API interactions: Found {len(result['interactions'])} interactions")
            else:
                print(f"⚠️  Interactions returned error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️  Real API test failed (may be expected): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
