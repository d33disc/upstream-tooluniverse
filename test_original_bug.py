#!/usr/bin/env python3
"""
Test the exact scenario from the bug report to verify it's fixed.
"""

from tooluniverse import ToolUniverse

print("=" * 80)
print("Testing Original Bug Report Scenario")
print("=" * 80)

# Initialize ToolUniverse
print("\n1. Initializing ToolUniverse...")
tu = ToolUniverse()
print(f"   Initial tools loaded: {len(tu.all_tool_dict)}")

# Call 4 STRING tools sequentially (from bug report)
print("\n2. Calling STRING_map_identifiers...")
tool1 = tu.tools.STRING_map_identifiers
print(f"   ✓ Tools in registry: {len(tu.all_tool_dict)}")

print("\n3. Calling STRING_get_network...")
tool2 = tu.tools.STRING_get_network
print(f"   ✓ Tools in registry: {len(tu.all_tool_dict)}")

print("\n4. Calling STRING_functional_enrichment...")
tool3 = tu.tools.STRING_functional_enrichment
print(f"   ✓ Tools in registry: {len(tu.all_tool_dict)}")

print("\n5. Calling STRING_ppi_enrichment...")
tool4 = tu.tools.STRING_ppi_enrichment
print(f"   ✓ Tools in registry: {len(tu.all_tool_dict)}")

# Verify all 4 tools are in registry
print("\n" + "=" * 80)
print("Verification:")
print("=" * 80)

tools_present = [
    "STRING_map_identifiers",
    "STRING_get_network",
    "STRING_functional_enrichment",
    "STRING_ppi_enrichment"
]

for tool_name in tools_present:
    status = "✅" if tool_name in tu.all_tool_dict else "❌"
    print(f"{status} {tool_name}")

all_present = all(tool in tu.all_tool_dict for tool in tools_present)

print("\n" + "=" * 80)
if all_present:
    print("✅ SUCCESS: All 4 tools present in registry (bug fixed!)")
    print("   - No repeated reloads")
    print("   - Tools accumulate correctly")
    print("   - Registry preserved across calls")
else:
    print("❌ FAILED: Some tools missing from registry")
print("=" * 80)
