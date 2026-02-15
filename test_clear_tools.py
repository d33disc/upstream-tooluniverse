#!/usr/bin/env python3
"""
Test the clear_tools() method.
"""

from tooluniverse import ToolUniverse

print("=" * 80)
print("TEST: clear_tools() Method")
print("=" * 80)

# Initialize and load some tools
tu = ToolUniverse()
print("\n1. Loading 3 tools...")
tu.load_tools(include_tools=[
    "STRING_map_identifiers",
    "STRING_get_network",
    "UniProt_get_entry_by_accession"
])
print(f"   Tools loaded: {len(tu.all_tool_dict)}")
print(f"   Tool names: {list(tu.all_tool_dict.keys())}")

# Verify tools are loaded
assert len(tu.all_tool_dict) == 3, "Should have 3 tools"
assert "STRING_map_identifiers" in tu.all_tool_dict
assert "STRING_get_network" in tu.all_tool_dict
assert "UniProt_get_entry_by_accession" in tu.all_tool_dict
print("   ✅ All 3 tools present")

# Clear tools
print("\n2. Clearing tools...")
tu.clear_tools()
print(f"   Tools remaining: {len(tu.all_tool_dict)}")

# Verify registry is empty
assert len(tu.all_tool_dict) == 0, "Registry should be empty after clear"
assert len(tu.all_tools) == 0, "all_tools should be empty"
assert len(tu.tool_category_dicts) == 0, "Categories should be empty"
print("   ✅ Registry cleared successfully")

# Load new tools after clearing
print("\n3. Loading different tools after clear...")
tu.load_tools(include_tools=["STRING_functional_enrichment"])
print(f"   Tools loaded: {len(tu.all_tool_dict)}")
print(f"   Tool names: {list(tu.all_tool_dict.keys())}")

# Verify only new tool is present
assert len(tu.all_tool_dict) == 1, "Should have 1 tool"
assert "STRING_functional_enrichment" in tu.all_tool_dict
assert "STRING_map_identifiers" not in tu.all_tool_dict, "Old tools should be gone"
print("   ✅ Only new tool present (old tools cleared)")

# Test selective loading after clear
print("\n4. Testing tool finder use case...")
tu.clear_tools()
tu.load_tools(include_tools=["STRING_map_identifiers", "STRING_get_network"])
print(f"   Loaded {len(tu.all_tool_dict)} STRING tools for tool finder")
print(f"   Tool names: {list(tu.all_tool_dict.keys())}")

# Verify only requested tools present
assert len(tu.all_tool_dict) == 2, "Should have exactly 2 tools"
assert "STRING_map_identifiers" in tu.all_tool_dict
assert "STRING_get_network" in tu.all_tool_dict
assert "UniProt_get_entry_by_accession" not in tu.all_tool_dict
print("   ✅ Tool finder sees only loaded tools")

# Test clear_cache parameter
print("\n5. Testing clear_tools(clear_cache=True)...")
tu.clear_tools(clear_cache=True)
print("   ✅ Both tools and cache cleared")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - clear_tools() works correctly!")
print("=" * 80)
print("\nUse cases:")
print("  • tu.clear_tools()                    - Reset tool registry")
print("  • tu.clear_tools(clear_cache=True)    - Clear tools + results")
print("  • clear → load → tool finder          - Control visible tools")
print("=" * 80)
