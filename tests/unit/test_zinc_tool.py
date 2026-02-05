"""Unit tests for ZINCTool."""

import pytest
from unittest.mock import patch, MagicMock

from tooluniverse.zinc_tool import ZINCTool


class TestZINCTool:
    """Test suite for ZINCTool."""

    @pytest.fixture
    def tool(self):
        """Create a tool instance with default config."""
        return ZINCTool({"timeout": 10})

    def test_missing_zinc_id(self, tool):
        """Test error when zinc_id is missing."""
        result = tool.run({"operation": "get_substance"})
        assert result["status"] == "error"
        assert "zinc_id" in result["error"]

    def test_missing_name(self, tool):
        """Test error when name is missing for search."""
        result = tool.run({"operation": "search_by_name"})
        assert result["status"] == "error"
        assert "name" in result["error"]

    def test_missing_smiles(self, tool):
        """Test error when smiles is missing for structure search."""
        result = tool.run({"operation": "search_by_smiles"})
        assert result["status"] == "error"
        assert "smiles" in result["error"]

    def test_unknown_operation(self, tool):
        """Test error for unknown operation."""
        result = tool.run({"operation": "invalid_op"})
        assert result["status"] == "error"
        assert "Unknown operation" in result["error"]

    @patch("tooluniverse.zinc_tool.requests.get")
    def test_get_substance_success(self, mock_get, tool):
        """Test successful substance retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "zinc_id": "ZINC000000000001",
            "smiles": "CC(C)C",
            "mwt": 58.12,
            "logp": 1.5,
        }
        mock_get.return_value = mock_response

        result = tool.run({"operation": "get_substance", "zinc_id": "ZINC000000000001"})

        assert result["status"] == "success"
        assert "smiles" in result["data"]

    @patch("tooluniverse.zinc_tool.requests.get")
    def test_get_catalogs_success(self, mock_get, tool):
        """Test getting catalogs."""
        mock_response = MagicMock()
        mock_response.status_code = 404  # Will use fallback
        mock_get.return_value = mock_response

        result = tool.run({"operation": "get_catalogs"})

        assert result["status"] == "success"
        assert "catalogs" in result["data"]


class TestZINCToolInterface:
    """Test ZINCTool through ToolUniverse interface."""

    def test_tool_registered(self):
        """Test that ZINCTool is properly registered."""
        from tooluniverse import ToolUniverse

        tu = ToolUniverse()
        tu.load_tools()

        assert hasattr(tu.tools, "ZINC_get_substance")
        assert hasattr(tu.tools, "ZINC_search_by_name")
        assert hasattr(tu.tools, "ZINC_search_by_smiles")
        assert hasattr(tu.tools, "ZINC_get_catalogs")
