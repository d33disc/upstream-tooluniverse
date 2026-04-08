#!/usr/bin/env python3
"""
Direct SMCP integration tests.

Historical note: this module once contained a TestSMCPHTTPServer class that
spawned ``tooluniverse.smcp_server`` as a subprocess and POSTed raw JSON to
``/health``, ``/tools``, and ``/mcp``. Those tests were not runnable against
the current FastMCP transport: FastMCP does not provide ``/health`` or
``/tools`` REST endpoints, and its ``streamable-http`` transport requires a
proper MCP client rather than raw HTTP POSTs. Every test body consisted of a
``pytest.skip(...)`` on the first line, so the class produced seven
permanent skips while contributing zero coverage. It was removed in favor of
``TestSMCPDirectIntegration`` below, which exercises the SMCP server directly
via its Python API — covering the same server bootstrap and tool-loading
paths without needing a subprocess or an HTTP client.

If HTTP-transport coverage is wanted in the future, add a test module that
uses the FastMCP Python client against an in-process server.
"""

import os
import sys

import pytest

# Ensure src/ is importable
CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(CURRENT_DIR, "..", "..", "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

try:
    from tooluniverse.smcp import SMCP  # type: ignore
except ImportError:
    # Fallback for when running from different directory
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from tooluniverse.smcp import SMCP  # type: ignore


class TestSMCPDirectIntegration:
    """Test SMCP server directly without HTTP."""

    @pytest.mark.asyncio
    async def test_smcp_server_direct_startup(self):
        """Test SMCP server startup directly."""
        server = SMCP(
            name="Direct Test Server",
            tool_categories=["uniprot", "pubmed"],
            search_enabled=True,
            max_workers=2,
        )

        # Test server initialization
        assert server.name == "Direct Test Server"
        assert server.search_enabled is True

        # Test tool loading
        tools = await server.get_tools()
        assert isinstance(tools, dict)
        assert len(tools) > 0

        print(f"✅ Direct server started with {len(tools)} tools")

    @pytest.mark.asyncio
    async def test_smcp_with_hooks_direct(self):
        """Test SMCP server with hooks enabled directly."""
        server = SMCP(
            name="Hooks Test Server",
            tool_categories=["uniprot", "pubmed"],
            search_enabled=True,
            max_workers=2,
            hooks_enabled=True,
            hook_type="SummarizationHook",
        )

        # Test server initialization
        assert server.hooks_enabled is True
        assert server.hook_type == "SummarizationHook"

        # Test tool loading
        tools = await server.get_tools()
        assert isinstance(tools, dict)
        assert len(tools) > 0

        # Check if hook manager exists
        if hasattr(server.tooluniverse, "hook_manager"):
            hook_manager = server.tooluniverse.hook_manager
            print(f"✅ Hook manager found with {len(hook_manager.hooks)} hooks")
        else:
            print("⚠️ No hook manager found")

        print(f"✅ Hooks-enabled server started with {len(tools)} tools")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
