#!/usr/bin/env python3
"""
Test MCP Server Space Loading via stdio (simulated)

This script simulates how MCP server would load Space configurations
when called via command line with --load parameter.

Usage:
    python examples/spaces/test_mcp_stdio_space.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_mcp_stdio_with_space(space_file, space_name):
    """Test MCP server stdio mode with Space configuration"""
    print(f"\n{'='*60}")
    print(f"Testing MCP stdio with Space: {space_name}")
    print(f"{'='*60}")
    
    # Check if file exists
    if not os.path.exists(space_file):
        print(f"❌ File not found: {space_file}")
        return False
    
    # Test command that would be used
    cmd = [
        sys.executable,
        "-m", "tooluniverse.smcp_server",
        "--load", space_file,
        "--name", f"Test-{space_name}",
        "--no-search",  # Disable search for faster testing
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print(f"\n📝 Note: This would start an MCP server in stdio mode")
    print(f"   In real usage, this would be called by Claude Desktop or other MCP clients")
    
    # Instead of actually running stdio (which would block), we test the SMCP initialization
    try:
        from tooluniverse.smcp import SMCP
        
        # Create SMCP server with Space configuration (simulating what stdio would do)
        server = SMCP(
            name=f"Test-{space_name}",
            space=space_file,
            auto_expose_tools=True,
            search_enabled=False,
        )
        
        print(f"\n✅ SMCP server initialized successfully")
        
        if hasattr(server, 'tooluniverse') and server.tooluniverse:
            tool_count = len(server.tooluniverse.all_tools)
            print(f"   Tools loaded: {tool_count} tools")
            
            # Check Space metadata
            if hasattr(server, 'space_metadata') and server.space_metadata:
                print(f"   Space name: {server.space_metadata.get('name', 'N/A')}")
                print(f"   Space version: {server.space_metadata.get('version', 'N/A')}")
            
            # Show some example tools
            print(f"\n   Sample tools exposed to MCP:")
            for tool in server.tooluniverse.all_tools[:5]:
                if isinstance(tool, dict):
                    print(f"   - {tool.get('name')}")
            
            return True, tool_count
        else:
            print("   ⚠️  ToolUniverse not found")
            return False, 0
            
    except Exception as e:
        print(f"❌ Failed to initialize SMCP server: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def main():
    """Main test function"""
    print("🧪 Testing MCP Server Space Loading (stdio simulation)")
    print("=" * 60)
    
    # Get the examples/spaces directory
    spaces_dir = Path(__file__).parent
    
    # Test key Space configurations
    test_spaces = [
        ("protein-research.yaml", "Protein Research"),
        ("genomics.yaml", "Genomics"),
        ("cheminformatics.yaml", "Cheminformatics"),
    ]
    
    results = []
    
    for filename, name in test_spaces:
        space_file = str(spaces_dir / filename)
        success, tool_count = test_mcp_stdio_with_space(space_file, name)
        results.append({
            'name': name,
            'success': success,
            'tool_count': tool_count,
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status}: {result['name']} - {result['tool_count']} tools")
    
    all_passed = all(r['success'] for r in results)
    
    print(f"\n🎯 Results: {sum(1 for r in results if r['success'])}/{len(results)} tests passed")
    
    if all_passed:
        print("🎉 All MCP Space loading tests passed!")
        print("\n💡 MCP server can successfully load Space configurations via:")
        print("   - Command line: tooluniverse-smcp-stdio --load <space-file>")
        print("   - Python API: SMCP(space='<space-file>')")
    else:
        print("⚠️  Some tests failed")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

