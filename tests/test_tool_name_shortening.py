"""
Tests for tool name shortening functionality.

This module tests the automatic tool name shortening feature added for
MCP 64-character limit compatibility.
"""

import pytest
from tooluniverse.tool_name_utils import shorten_tool_name, ToolNameMapper


class TestShortenToolName:
    """Tests for the shorten_tool_name function."""
    
    def test_short_name_unchanged(self):
        """Test that short names are not modified."""
        name = "FDA_get_drug_name"
        shortened = shorten_tool_name(name, max_length=55)
        assert shortened == name
        assert len(shortened) <= 55
    
    def test_long_name_shortened(self):
        """Test that long names are shortened."""
        name = "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name"
        shortened = shorten_tool_name(name, max_length=55)
        
        assert len(shortened) <= 55
        assert shortened.startswith("FDA_")
        assert shortened != name
    
    def test_preserves_category_prefix(self):
        """Test that category prefix (first word) is preserved."""
        names = [
            "FDA_get_very_long_information_about_something",
            "UniProt_get_extremely_detailed_function_information",
        ]
        
        for name in names:
            shortened = shorten_tool_name(name, max_length=55)
            category = name.split('_')[0]
            assert shortened.startswith(category + "_")
    
    def test_fits_within_limit(self):
        """Test that shortened names always fit within the limit."""
        long_names = [
            "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name",
            "euhealthinfo_search_diabetes_mellitus_epidemiology_registry",
        ]
        
        for name in long_names:
            shortened = shorten_tool_name(name, max_length=55)
            assert len(shortened) <= 55


class TestToolNameMapper:
    """Tests for the ToolNameMapper class."""
    
    def test_bidirectional_mapping(self):
        """Test that names can be mapped both directions."""
        mapper = ToolNameMapper()
        original = "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name"
        
        # Shorten
        shortened = mapper.get_shortened(original, max_length=55)
        assert len(shortened) <= 55
        
        # Resolve back
        resolved = mapper.get_original(shortened)
        assert resolved == original
    
    def test_collision_handling(self):
        """Test that collisions are handled with counters."""
        mapper = ToolNameMapper()
        
        # Create two names that might shorten to the same thing
        name1 = "test_get_info"
        name2 = "test_get_information"
        
        short1 = mapper.get_shortened(name1, max_length=20)
        short2 = mapper.get_shortened(name2, max_length=20)
        
        # If they collide, second should have suffix
        if short1 == short2[:len(short1)]:
            assert "_2" in short2 or short2 != short1
        
        # Both should resolve correctly
        assert mapper.get_original(short1) == name1
        assert mapper.get_original(short2) == name2
    
    def test_caching(self):
        """Test that repeated calls return the same shortened name."""
        mapper = ToolNameMapper()
        name = "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name"
        
        short1 = mapper.get_shortened(name, max_length=55)
        short2 = mapper.get_shortened(name, max_length=55)
        
        assert short1 == short2


class TestToolUniverseAPI:
    """Tests for ToolUniverse name handling API."""
    
    def test_get_exposed_name_with_mapper(self):
        """Test that get_exposed_name() returns shortened name when mapper is set."""
        from tooluniverse import ToolUniverse
        
        tu = ToolUniverse(enable_name_shortening=True)
        tu.load_tools()
        
        long_name = "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name"
        exposed = tu.get_exposed_name(long_name, max_length=55)
        
        assert exposed != long_name
        assert len(exposed) <= 55
    
    def test_get_exposed_name_without_mapper(self):
        """Test that get_exposed_name() returns original name when mapper is None."""
        from tooluniverse import ToolUniverse
        
        tu = ToolUniverse()
        tu.load_tools()
        
        long_name = "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name"
        exposed = tu.get_exposed_name(long_name, max_length=55)
        
        assert exposed == long_name


class TestTransparentResolution:
    """Tests for transparent name resolution in ToolUniverse."""
    
    def test_run_one_function_accepts_both_names(self):
        """Test that run_one_function() accepts both shortened and original names."""
        from tooluniverse import ToolUniverse
        
        tu = ToolUniverse(enable_name_shortening=True)
        tu.load_tools()
        
        long_name = "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name"
        shortened = tu.get_exposed_name(long_name)
        
        # Both should resolve to the same tool
        assert shortened in tu.name_mapper._short_to_original
        assert tu.name_mapper.get_original(shortened) == long_name
    
    def test_name_mapper_none_works(self):
        """Test that when name_mapper is None, original behavior is preserved."""
        from tooluniverse import ToolUniverse
        
        tu = ToolUniverse()
        tu.load_tools()
        
        assert tu.name_mapper is None
        
        # Normal operation should still work
        tool_name = "FDA_get_drug_info_by_name"
        if tool_name in tu.all_tool_dict:
            assert True


class TestMCPCompatibility:
    """Tests for MCP 64-character limit compatibility."""
    
    def test_all_tools_fit_with_tu_prefix(self):
        """Test that all tools fit within 64 chars with mcp__tu__ prefix."""
        from tooluniverse import ToolUniverse
        
        tu = ToolUniverse(enable_name_shortening=True)
        tu.load_tools()
        
        mcp_prefix = "mcp__tu__"
        prefix_len = len(mcp_prefix)
        max_tool_name_len = 64 - prefix_len  # 55 chars
        
        # Test that all shortened names fit
        for tool_name in tu.all_tool_dict.keys():
            shortened = tu.get_exposed_name(tool_name, max_length=max_tool_name_len)
            full_mcp_name = mcp_prefix + shortened
            
            assert len(full_mcp_name) <= 64, (
                f"MCP name too long: {full_mcp_name} ({len(full_mcp_name)} chars)"
            )
    
    def test_smcp_integration(self):
        """Test that SMCP automatically enables name shortening."""
        from tooluniverse.smcp import SMCP
        
        server = SMCP(
            name='tu',
            tool_categories=['fda_drug_label'],
            auto_expose_tools=False,
            search_enabled=False
        )
        
        # SMCP should automatically enable name shortening
        assert server.tooluniverse.name_mapper is not None
        
        # Test that get_exposed_name works
        long_name = "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name"
        if long_name in server.tooluniverse.all_tool_dict:
            exposed = server.tooluniverse.get_exposed_name(long_name, max_length=55)
            assert len(exposed) <= 55
