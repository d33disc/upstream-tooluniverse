#!/usr/bin/env python3
"""
Test MCP Server Space Loading

This script tests whether MCP server can correctly load Space configurations
and expose the tools as expected.

Usage:
    python examples/spaces/test_mcp_space_loading.py
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tooluniverse import ToolUniverse
from tooluniverse.smcp import SMCP


def test_space_loading_directly(space_file, space_name):
    """Test loading Space directly with ToolUniverse"""
    print(f"\n{'='*60}")
    print(f"Testing Direct Loading: {space_name}")
    print(f"{'='*60}")
    
    try:
        tu = ToolUniverse()
        config = tu.load_space(space_file)
        
        print(f"✅ Successfully loaded: {config.get('name')}")
        print(f"   Tools loaded: {len(tu.all_tools)} tools")
        
        # Show some example tools
        print(f"\n   Sample tools:")
        for tool in tu.all_tools[:5]:
            if isinstance(tool, dict):
                print(f"   - {tool.get('name')}")
        
        return True, len(tu.all_tools)
    except Exception as e:
        print(f"❌ Failed to load: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def test_space_loading_with_smcp(space_file, space_name):
    """Test loading Space with SMCP server"""
    print(f"\n{'='*60}")
    print(f"Testing SMCP Server Loading: {space_name}")
    print(f"{'='*60}")
    
    try:
        # Create SMCP server with Space configuration
        server = SMCP(
            name="Test Space Server",
            space=space_file,
            auto_expose_tools=True,
            search_enabled=False,  # Disable search for faster startup
        )
        
        print(f"✅ SMCP server created with Space: {space_name}")
        
        # Check if tools are loaded
        if hasattr(server, 'tooluniverse') and server.tooluniverse:
            tool_count = len(server.tooluniverse.all_tools)
            print(f"   Tools loaded: {tool_count} tools")
            
            # Show some example tools
            print(f"\n   Sample tools:")
            for tool in server.tooluniverse.all_tools[:5]:
                if isinstance(tool, dict):
                    print(f"   - {tool.get('name')}")
            
            return True, tool_count
        else:
            print("   ⚠️  ToolUniverse not found in SMCP server")
            return False, 0
            
    except Exception as e:
        print(f"❌ Failed to create SMCP server: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def test_mcp_tools_list(space_file, space_name):
    """Test if MCP server can list tools correctly"""
    print(f"\n{'='*60}")
    print(f"Testing MCP Tools List: {space_name}")
    print(f"{'='*60}")
    
    try:
        # Create SMCP server
        server = SMCP(
            name="Test Space Server",
            space=space_file,
            auto_expose_tools=True,
            search_enabled=False,
        )
        
        # Simulate MCP tools/list call
        # This would normally be called by an MCP client
        if hasattr(server, 'tooluniverse') and server.tooluniverse:
            tools = server.tooluniverse.all_tools
            
            # Check if tools are exposed
            print(f"✅ Tools available: {len(tools)} tools")
            
            # Check if tools have required MCP format
            mcp_tools = []
            for tool in tools:
                if isinstance(tool, dict):
                    tool_name = tool.get('name')
                    if tool_name:
                        mcp_tools.append(tool_name)
            
            print(f"   MCP-ready tools: {len(mcp_tools)} tools")
            print(f"\n   Sample MCP tool names:")
            for tool_name in mcp_tools[:5]:
                print(f"   - {tool_name}")
            
            return True, len(mcp_tools)
        else:
            print("   ⚠️  ToolUniverse not found")
            return False, 0
            
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def main():
    """Main test function"""
    print("🧪 Testing MCP Server Space Loading")
    print("=" * 60)
    
    # Get the examples/spaces directory
    spaces_dir = Path(__file__).parent
    
    # Test a few key Space configurations
    test_spaces = [
        ("protein-research.yaml", "Protein Research Toolkit"),
        ("genomics.yaml", "Genomics Research Toolkit"),
        ("cheminformatics.yaml", "Cheminformatics Toolkit"),
    ]
    
    results = []
    
    for filename, name in test_spaces:
        space_file = str(spaces_dir / filename)
        
        if not os.path.exists(space_file):
            print(f"⚠️  File not found: {space_file}")
            continue
        
        # Test 1: Direct loading
        direct_success, direct_count = test_space_loading_directly(space_file, name)
        
        # Test 2: SMCP loading
        smcp_success, smcp_count = test_space_loading_with_smcp(space_file, name)
        
        # Test 3: MCP tools list
        list_success, list_count = test_mcp_tools_list(space_file, name)
        
        # Compare counts
        if direct_success and smcp_success:
            if direct_count == smcp_count:
                print(f"\n   ✅ Tool counts match: {direct_count} tools")
            else:
                print(f"\n   ⚠️  Tool count mismatch: Direct={direct_count}, SMCP={smcp_count}")
        
        results.append({
            'name': name,
            'direct': direct_success,
            'smcp': smcp_success,
            'list': list_success,
            'direct_count': direct_count,
            'smcp_count': smcp_count,
            'list_count': list_count,
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for result in results:
        name = result['name']
        direct = "✅" if result['direct'] else "❌"
        smcp = "✅" if result['smcp'] else "❌"
        list_test = "✅" if result['list'] else "❌"
        
        print(f"\n{name}:")
        print(f"  Direct Loading: {direct} ({result['direct_count']} tools)")
        print(f"  SMCP Loading: {smcp} ({result['smcp_count']} tools)")
        print(f"  MCP Tools List: {list_test} ({result['list_count']} tools)")
        
        if result['direct'] and result['smcp'] and result['direct_count'] == result['smcp_count']:
            print(f"  ✅ All tests passed!")
        else:
            print(f"  ⚠️  Some tests failed or counts don't match")
    
    all_passed = all(
        r['direct'] and r['smcp'] and r['list'] and 
        r['direct_count'] == r['smcp_count'] == r['list_count']
        for r in results
    )
    
    print(f"\n🎯 Overall: {'✅ All tests passed!' if all_passed else '⚠️  Some issues found'}")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

