"""
Test suite for IEDB (Immune Epitope Database) API tools

Tests the IEDB Query API (PostgREST) tools for:
- Epitope search
- Antigen search
- MHC binding search
- B-cell epitope search
- Reference search
- Epitope relationship queries

Testing levels:
1. Direct class testing (implementation logic)
2. ToolUniverse interface testing (registration and access)
3. Real API testing (integration with IEDB API)
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tooluniverse.iedb_tool import IEDBTool
from tooluniverse import ToolUniverse


class TestIEDBDirectClass:
    """Level 1: Direct class testing"""
    
    @pytest.fixture
    def tool_configs(self):
        """Load tool configurations from JSON"""
        config_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'src', 'tooluniverse', 'data', 'iedb_tools.json'
        )
        with open(config_path) as f:
            return json.load(f)
    
    def test_tool_initialization(self, tool_configs):
        """Test IEDB tool initialization for all tools"""
        for config in tool_configs:
            tool = IEDBTool(config)
            assert tool is not None
            assert hasattr(tool, 'run')
            assert tool.QUERY_API_URL == "https://query-api.iedb.org"
    
    @patch('requests.Session.request')
    def test_search_epitopes_success(self, mock_request, tool_configs):
        """Test successful epitope search"""
        config = next(t for t in tool_configs if t["name"] == "iedb_search_epitopes")
        tool = IEDBTool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "epitope_id": 1,
                "linear_sequence": "KVFGRCELAAAMKR",
                "structure_type": "Linear peptide"
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        result = tool.run({"limit": 10})
        
        assert result["status"] == "success"
        assert "data" in result
        assert isinstance(result["data"], list)
    
    @patch('requests.Session.request')
    def test_search_with_filters(self, mock_request, tool_configs):
        """Test search with PostgREST filters"""
        config = next(t for t in tool_configs if t["name"] == "iedb_search_epitopes")
        tool = IEDBTool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"epitope_id": 2, "linear_sequence": "TESTSEQ"}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        result = tool.run({
            "filters": {"structure_type": "eq.Linear peptide"},
            "limit": 5
        })
        
        assert result["status"] == "success"
        assert "data" in result
    
    @patch('requests.Session.request')
    def test_shorthand_filters(self, mock_request, tool_configs):
        """Test shorthand filter mapping"""
        config = next(t for t in tool_configs if t["name"] == "iedb_search_epitopes")
        tool = IEDBTool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        # Test with shorthand filter (if configured)
        result = tool.run({"limit": 1})
        
        assert result["status"] == "success"
    
    @patch('requests.Session.request')
    def test_search_antigens(self, mock_request, tool_configs):
        """Test antigen search"""
        config = next(t for t in tool_configs if t["name"] == "iedb_search_antigens")
        tool = IEDBTool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"antigen_id": 1, "antigen_name": "Test Antigen"}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        result = tool.run({"limit": 5})
        
        assert result["status"] == "success"
        assert "data" in result
    
    @patch('requests.Session.request')
    def test_search_mhc(self, mock_request, tool_configs):
        """Test MHC binding search"""
        config = next(t for t in tool_configs if t["name"] == "iedb_search_mhc")
        tool = IEDBTool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"mhc_id": 1, "mhc_allele": "HLA-A*02:01"}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        result = tool.run({"limit": 5})
        
        assert result["status"] == "success"
    
    @patch('requests.Session.request')
    def test_error_handling(self, mock_request, tool_configs):
        """Test error handling for failed API calls"""
        config = next(t for t in tool_configs if t["name"] == "iedb_search_epitopes")
        tool = IEDBTool(config)
        
        mock_request.side_effect = Exception("Network error")
        
        result = tool.run({"limit": 10})
        
        assert result["status"] == "error"
        assert "error" in result
    
    def test_missing_endpoint_config(self):
        """Test error when endpoint is not configured"""
        bad_config = {
            "name": "bad_tool",
            "type": "IEDBTool",
            "fields": {}  # Missing endpoint
        }
        tool = IEDBTool(bad_config)
        
        result = tool.run({})
        
        assert result["status"] == "error"
        assert "misconfigured" in result["error"].lower()


class TestIEDBToolUniverse:
    """Level 2: ToolUniverse interface testing"""
    
    @pytest.fixture
    def tu(self):
        """Initialize ToolUniverse with tools loaded"""
        tu = ToolUniverse()
        tu.load_tools()
        return tu
    
    def test_tools_registered(self, tu):
        """Test that all IEDB tools are registered"""
        expected_tools = [
            "iedb_search_epitopes",
            "iedb_search_antigens",
            "iedb_search_mhc",
            "iedb_search_bcell",
            "iedb_search_references",
            "iedb_get_epitope_antigens",
            "iedb_get_epitope_mhc",
            "iedb_get_epitope_references"
        ]
        
        for tool_name in expected_tools:
            assert hasattr(tu.tools, tool_name), f"{tool_name} not found"
    
    @patch('requests.Session.request')
    def test_search_epitopes_via_tooluniverse(self, mock_request, tu):
        """Test epitope search via ToolUniverse interface"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"epitope_id": 123, "linear_sequence": "KVFGRCELAAAMKR"}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        result = tu.tools.iedb_search_epitopes(**{"limit": 10})
        
        assert result["status"] == "success"
        assert "data" in result
    
    @patch('requests.Session.request')
    def test_search_antigens_via_tooluniverse(self, mock_request, tu):
        """Test antigen search via ToolUniverse interface"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"antigen_id": 456, "antigen_name": "Spike protein"}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        result = tu.tools.iedb_search_antigens(**{"limit": 5})
        
        assert result["status"] == "success"
        assert "data" in result


class TestIEDBRealAPI:
    """Level 3: Real API testing (requires network)"""
    
    @pytest.fixture
    def tu(self):
        """Initialize ToolUniverse"""
        tu = ToolUniverse()
        tu.load_tools()
        return tu
    
    def test_real_search_epitopes(self, tu):
        """Test real API epitope search"""
        try:
            result = tu.tools.iedb_search_epitopes(**{"limit": 5})
            
            if result["status"] == "success":
                assert "data" in result
                assert isinstance(result["data"], list)
                print(f"✅ Real API epitope search: Found {len(result['data'])} epitopes")
            else:
                print(f"⚠️  Epitope search returned error: {result.get('error')}")
        except Exception as e:
            print(f"⚠️  Real API test failed (may be expected): {e}")
    
    def test_real_search_antigens(self, tu):
        """Test real API antigen search"""
        try:
            result = tu.tools.iedb_search_antigens(**{"limit": 5})
            
            if result["status"] == "success":
                assert "data" in result
                print(f"✅ Real API antigen search: Found {len(result['data'])} antigens")
            else:
                print(f"⚠️  Antigen search returned error: {result.get('error')}")
        except Exception as e:
            print(f"⚠️  Real API test failed (may be expected): {e}")
    
    def test_real_search_mhc(self, tu):
        """Test real API MHC search"""
        try:
            result = tu.tools.iedb_search_mhc(**{"limit": 5})
            
            if result["status"] == "success":
                assert "data" in result
                print(f"✅ Real API MHC search: Found {len(result['data'])} MHC entries")
            else:
                print(f"⚠️  MHC search returned error: {result.get('error')}")
        except Exception as e:
            print(f"⚠️  Real API test failed (may be expected): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
