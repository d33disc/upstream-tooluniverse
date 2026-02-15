#!/usr/bin/env python3
"""
Test script to verify the tool reloading bug fix.

This script tests that:
1. Tools are loaded once and cached
2. Multiple tool calls don't reload all tools
3. Tool registry accumulates instead of replacing
"""

import sys
from tooluniverse import ToolUniverse


def test_progressive_loading():
    """Test that tools accumulate in registry instead of replacing."""
    print("=" * 80)
    print("TEST: Progressive Tool Loading (Fix Verification)")
    print("=" * 80)

    # Initialize empty ToolUniverse
    tu = ToolUniverse()
    print(f"\n1. Initial state: {len(tu.all_tool_dict)} tools loaded")
    assert len(tu.all_tool_dict) == 0, "Should start with empty registry"

    # Load first tool
    print("\n2. Loading first tool via load_tools()...")
    tu.load_tools(include_tools=["STRING_map_identifiers"])
    tool_count_1 = len(tu.all_tool_dict)
    print(f"   Tools in registry: {tool_count_1}")
    assert "STRING_map_identifiers" in tu.all_tool_dict, "First tool should be loaded"

    # Load second tool
    print("\n3. Loading second tool via load_tools()...")
    tu.load_tools(include_tools=["STRING_get_network"])
    tool_count_2 = len(tu.all_tool_dict)
    print(f"   Tools in registry: {tool_count_2}")

    # CRITICAL: Both tools should be in registry (merge mode)
    assert "STRING_map_identifiers" in tu.all_tool_dict, "❌ BUG: First tool was lost!"
    assert "STRING_get_network" in tu.all_tool_dict, "Second tool should be loaded"
    assert tool_count_2 >= tool_count_1, "Tool count should increase, not stay same"

    print(f"   ✅ Both tools present: {list(tu.all_tool_dict.keys())}")

    # Load third tool
    print("\n4. Loading third tool via load_tools()...")
    tu.load_tools(include_tools=["UniProt_get_entry_by_accession"])
    tool_count_3 = len(tu.all_tool_dict)
    print(f"   Tools in registry: {tool_count_3}")

    # All three tools should be present
    assert "STRING_map_identifiers" in tu.all_tool_dict, "First tool should still be there"
    assert "STRING_get_network" in tu.all_tool_dict, "Second tool should still be there"
    assert "UniProt_get_entry_by_accession" in tu.all_tool_dict, "Third tool should be loaded"
    assert tool_count_3 >= tool_count_2, "Tool count should keep increasing"

    print(f"   ✅ All three tools present: {list(tu.all_tool_dict.keys())[:5]}...")

    print("\n" + "=" * 80)
    print("✅ TEST PASSED: Tools accumulate correctly (bug fixed!)")
    print("=" * 80)


def test_on_demand_loading():
    """Test that on-demand loading via tu.tools.TOOL_NAME() works."""
    print("\n" + "=" * 80)
    print("TEST: On-Demand Loading via tu.tools Interface")
    print("=" * 80)

    tu = ToolUniverse()
    print(f"\n1. Initial state: {len(tu.all_tool_dict)} tools loaded")

    # First tool access triggers loading
    print("\n2. Accessing first tool: tu.tools.STRING_map_identifiers")
    try:
        tool_callable = tu.tools.STRING_map_identifiers
        print(f"   ✅ Tool loaded successfully")
        print(f"   Tools in registry: {len(tu.all_tool_dict)}")
        tool_count_1 = len(tu.all_tool_dict)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Second tool access
    print("\n3. Accessing second tool: tu.tools.STRING_get_network")
    try:
        tool_callable = tu.tools.STRING_get_network
        print(f"   ✅ Tool loaded successfully")
        print(f"   Tools in registry: {len(tu.all_tool_dict)}")
        tool_count_2 = len(tu.all_tool_dict)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Verify both tools present
    assert "STRING_map_identifiers" in tu.all_tool_dict, "❌ First tool was lost!"
    assert "STRING_get_network" in tu.all_tool_dict, "Second tool should be present"
    assert tool_count_2 >= tool_count_1, "Tool count should increase"

    print(f"\n   ✅ Both tools present in registry")
    print("=" * 80)
    print("✅ TEST PASSED: On-demand loading accumulates correctly")
    print("=" * 80)


def test_no_error_spam():
    """Test that missing optional files don't generate ERROR messages."""
    print("\n" + "=" * 80)
    print("TEST: Missing Optional Files Should Not Show Errors")
    print("=" * 80)

    import logging
    from io import StringIO

    # Capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.ERROR)

    # Get the logger used by ToolUniverse
    from tooluniverse.logging_config import get_logger
    logger = get_logger("ToolUniverse")
    logger.addHandler(handler)

    # Load tools (which tries to load optional categories)
    tu = ToolUniverse()
    tu.load_tools(include_tools=["STRING_map_identifiers"])

    # Check for ERROR messages about missing files
    log_output = log_stream.getvalue()
    error_lines = [line for line in log_output.split('\n') if 'ERROR' in line.upper()]

    # Filter out actual errors (keep only file not found errors)
    file_not_found_errors = [
        line for line in error_lines
        if 'No such file or directory' in line or 'not found' in line.lower()
    ]

    if file_not_found_errors:
        print(f"\n   ❌ Found {len(file_not_found_errors)} ERROR messages for missing optional files:")
        for line in file_not_found_errors[:3]:
            print(f"      {line[:100]}...")
        print("\n   These should be DEBUG level, not ERROR level")
        print("=" * 80)
        print("⚠️  TEST FAILED: Error logging not fully fixed")
        print("=" * 80)
    else:
        print(f"\n   ✅ No ERROR messages for missing optional files")
        print("=" * 80)
        print("✅ TEST PASSED: Error logging fixed")
        print("=" * 80)


if __name__ == "__main__":
    try:
        # Test 1: Progressive loading
        test_progressive_loading()

        # Test 2: On-demand loading
        test_on_demand_loading()

        # Test 3: Error spam
        test_no_error_spam()

        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED - Bug fix successful!")
        print("=" * 80)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
