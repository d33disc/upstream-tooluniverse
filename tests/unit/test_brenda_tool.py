"""Unit tests for BRENDA tool."""
import pytest
import json
from unittest.mock import patch, MagicMock

class TestBRENDAToolDirect:
    @pytest.fixture
    def tool_config(self):
        with open("src/tooluniverse/data/brenda_tools.json") as f:
            return json.load(f)[0]

    @pytest.fixture
    def tool(self, tool_config):
        from tooluniverse.brenda_tool import BRENDATool
        return BRENDATool(tool_config)

    def test_missing_ec_number(self, tool):
        result = tool.run({"operation": "get_km"})
        assert result["status"] == "error"

class TestBRENDAToolInterface:
    @pytest.fixture
    def tu(self):
        from tooluniverse import ToolUniverse
        tu = ToolUniverse()
        tu.load_tools()
        return tu

    def test_tools_registered(self, tu):
        assert hasattr(tu.tools, "BRENDA_get_km")
        assert hasattr(tu.tools, "BRENDA_get_kcat")
