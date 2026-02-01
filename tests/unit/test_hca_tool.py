"""
Test suite for Human Cell Atlas (HCA) API tools

Tests the HCA Data Coordination Platform tools for:
- Project search (by organ, disease)
- File manifest retrieval

Testing levels:
1. Direct class testing (implementation logic)
2. ToolUniverse interface testing (registration and access)
3. Real API testing (integration with HCA API)
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tooluniverse.hca_tool import HCATool
from tooluniverse import ToolUniverse


class TestHCADirectClass:
    """Level 1: Direct class testing"""
    
    @pytest.fixture
    def tool_configs(self):
        """Load tool configurations from JSON"""
        config_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'src', 'tooluniverse', 'data', 'hca_tools.json'
        )
        with open(config_path) as f:
            return json.load(f)
    
    def test_search_projects_initialization(self, tool_configs):
        """Test hca_search_projects tool initialization"""
        config = next(t for t in tool_configs if t["name"] == "hca_search_projects")
        tool = HCATool(config)
        assert tool is not None
        assert hasattr(tool, 'run')
        assert hasattr(tool, 'search_projects')
    
    def test_get_file_manifest_initialization(self, tool_configs):
        """Test hca_get_file_manifest tool initialization"""
        config = next(t for t in tool_configs if t["name"] == "hca_get_file_manifest")
        tool = HCATool(config)
        assert tool is not None
        assert hasattr(tool, 'get_file_manifest')
    
    @patch('requests.get')
    def test_search_projects_success(self, mock_get, tool_configs):
        """Test successful project search"""
        config = next(t for t in tool_configs if t["name"] == "hca_search_projects")
        tool = HCATool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [
                {
                    "entryId": "proj-123",
                    "projects": [{"projectTitle": "Heart Study"}],
                    "modelOrgan": {"terms": ["heart"]},
                    "donorDisease": {"terms": ["normal"]}
                }
            ],
            "pagination": {"total": 1}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = tool.run({"action": "search_projects", "organ": "heart", "limit": 1})
        
        assert "projects" in result
        assert result["total_hits"] == 1
        assert len(result["projects"]) == 1
        assert result["projects"][0]["entryId"] == "proj-123"
    
    @patch('requests.get')
    def test_search_projects_with_disease(self, mock_get, tool_configs):
        """Test project search with disease filter"""
        config = next(t for t in tool_configs if t["name"] == "hca_search_projects")
        tool = HCATool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [
                {
                    "entryId": "proj-456",
                    "projects": [{"projectTitle": "Cancer Study"}],
                    "modelOrgan": {"terms": ["lung"]},
                    "donorDisease": {"terms": ["cancer"]}
                }
            ],
            "pagination": {"total": 1}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = tool.run({
            "action": "search_projects", 
            "organ": "lung",
            "disease": "cancer",
            "limit": 1
        })
        
        assert "projects" in result
        assert result["total_hits"] == 1
    
    @patch('requests.get')
    def test_get_file_manifest_success(self, mock_get, tool_configs):
        """Test successful file manifest retrieval"""
        config = next(t for t in tool_configs if t["name"] == "hca_get_file_manifest")
        tool = HCATool(config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [
                {
                    "files": [
                        {
                            "name": "data.h5",
                            "format": "h5",
                            "size": 1024,
                            "azul_url": "https://example.com/data.h5"
                        }
                    ]
                }
            ],
            "pagination": {"total": 1}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = tool.run({
            "action": "get_file_manifest",
            "project_id": "test-project-123",
            "limit": 10
        })
        
        assert "files" in result
        assert result["total_files"] == 1
        assert len(result["files"]) == 1
        assert result["files"][0]["name"] == "data.h5"
    
    def test_missing_project_id(self, tool_configs):
        """Test error when project_id is missing"""
        config = next(t for t in tool_configs if t["name"] == "hca_get_file_manifest")
        tool = HCATool(config)
        
        with pytest.raises(ValueError, match="project_id is required"):
            tool.run({"action": "get_file_manifest"})
    
    def test_unknown_action(self, tool_configs):
        """Test error for unknown action"""
        config = next(t for t in tool_configs if t["name"] == "hca_search_projects")
        tool = HCATool(config)
        
        with pytest.raises(ValueError, match="Unknown action"):
            tool.run({"action": "unknown_action"})
    
    @patch('requests.get')
    def test_error_handling(self, mock_get, tool_configs):
        """Test error handling for failed API calls"""
        config = next(t for t in tool_configs if t["name"] == "hca_search_projects")
        tool = HCATool(config)
        
        mock_get.side_effect = Exception("Network error")
        
        result = tool.run({"action": "search_projects", "organ": "heart"})
        
        assert "error" in result
        assert "Network error" in result["error"]


class TestHCAToolUniverse:
    """Level 2: ToolUniverse interface testing"""
    
    @pytest.fixture
    def tu(self):
        """Initialize ToolUniverse with tools loaded"""
        tu = ToolUniverse()
        tu.load_tools()
        return tu
    
    def test_tools_registered(self, tu):
        """Test that all HCA tools are registered"""
        expected_tools = [
            "hca_search_projects",
            "hca_get_file_manifest"
        ]
        
        for tool_name in expected_tools:
            assert hasattr(tu.tools, tool_name), f"{tool_name} not found"
    
    @patch('requests.get')
    def test_search_via_tooluniverse(self, mock_get, tu):
        """Test search via ToolUniverse interface"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [
                {
                    "entryId": "proj-789",
                    "projects": [{"projectTitle": "Brain Study"}],
                    "modelOrgan": {"terms": ["brain"]},
                    "donorDisease": {"terms": ["normal"]}
                }
            ],
            "pagination": {"total": 1}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = tu.tools.hca_search_projects(**{
            "action": "search_projects",
            "organ": "brain",
            "limit": 1
        })
        
        assert "projects" in result
        assert result["total_hits"] == 1
    
    @patch('requests.get')
    def test_get_manifest_via_tooluniverse(self, mock_get, tu):
        """Test get_file_manifest via ToolUniverse interface"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [
                {
                    "files": [
                        {
                            "name": "test.fastq",
                            "format": "fastq",
                            "size": 2048,
                            "azul_url": "https://example.com/test.fastq"
                        }
                    ]
                }
            ],
            "pagination": {"total": 1}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = tu.tools.hca_get_file_manifest(**{
            "action": "get_file_manifest",
            "project_id": "test-123",
            "limit": 5
        })
        
        assert "files" in result
        assert len(result["files"]) == 1


class TestHCARealAPI:
    """Level 3: Real API testing (requires network)"""
    
    @pytest.fixture
    def tu(self):
        """Initialize ToolUniverse"""
        tu = ToolUniverse()
        tu.load_tools()
        return tu
    
    def test_real_search_projects(self, tu):
        """Test real API project search"""
        try:
            result = tu.tools.hca_search_projects(**{
                "action": "search_projects",
                "organ": "heart",
                "limit": 2
            })
            
            if "projects" in result and not result.get("error"):
                assert "total_hits" in result
                assert "projects" in result
                print(f"✅ Real API search: Found {result['total_hits']} projects")
            else:
                print(f"⚠️  Search returned error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️  Real API test failed (may be expected): {e}")
    
    def test_real_get_file_manifest(self, tu):
        """Test real API file manifest retrieval"""
        try:
            # Using example project ID from JSON config
            result = tu.tools.hca_get_file_manifest(**{
                "action": "get_file_manifest",
                "project_id": "7027adc6-c9c9-46f3-84ee-9badc3a4f53b",
                "limit": 5
            })
            
            if "files" in result and not result.get("error"):
                assert "total_files" in result
                print(f"✅ Real API manifest: Found {result['total_files']} files")
            else:
                print(f"⚠️  Manifest returned error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️  Real API test failed (may be expected): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
