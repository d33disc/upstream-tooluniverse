MCP Support
===========

**Complete guide to Model Context Protocol (MCP) integration with ToolUniverse**

ToolUniverse provides comprehensive support for the Model Context Protocol (MCP), enabling seamless integration with AI assistants, reasoning models, and agentic systems. This guide covers everything you need to know about using ToolUniverse through MCP.

What is MCP?
------------

The Model Context Protocol (MCP) is a standardized protocol that enables AI assistants to securely connect to external tools and data sources. ToolUniverse implements MCP through the Scientific Model Context Protocol (SMCP), extending standard MCP capabilities with scientific domain expertise.

Key Benefits:
- **Standardized Integration**: Connect to any MCP-compatible AI assistant
- **Scientific Tool Access**: Direct access to 600+ scientific tools
- **Intelligent Discovery**: AI-powered tool search and recommendation
- **Secure Communication**: Standardized protocol ensures secure tool execution
- **Production Ready**: High-performance architecture for real-world applications

MCP Architecture Overview
-------------------------

.. code-block:: text

   AI Assistant (Claude, ChatGPT, Gemini, etc.)
           │
           │ MCP Protocol
           │
   ┌─────────────────┐
   │ ToolUniverse    │ ← MCP Server
   │   MCP Server    │
   └─────────────────┘
           │
           │ Tool Execution
           │
   ┌─────────────────┐
   │ Scientific      │
   │ Tools (600+)    │
   └─────────────────┘

ToolUniverse MCP Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ToolUniverse provides two main MCP server implementations:

1. **`tooluniverse-smcp`** - Full-featured server with configurable transport (HTTP, SSE, stdio)
2. **`tooluniverse-smcp-stdio`** - Specialized server for stdio transport (optimized for desktop AI applications)

Both servers expose the same comprehensive set of scientific tools through the MCP protocol.

Quick Start
-----------

For basic MCP server setup and configuration, see the comprehensive guide in :ref:`mcp-server-functions`.

MCP Server Configuration
-------------------------

Transport Options
~~~~~~~~~~~~~~~~~

ToolUniverse MCP servers support multiple transport protocols:

**HTTP Transport** (Default)
   - Best for web-based applications and remote access
   - Supports RESTful API endpoints
   - Configurable host and port

**STDIO Transport**
   - Optimized for desktop AI applications
   - Direct process communication
   - Lower latency for local applications

**Server-Sent Events (SSE)**
   - Real-time streaming capabilities
   - Suitable for interactive applications
   - Supports long-running operations

Tool Selection
~~~~~~~~~~~~~~~

Configure which tools are available through the MCP server. For detailed configuration options including category-based loading, tool-specific loading, and type-based filtering, see :ref:`category-based-loading`, :ref:`tool-specific-loading`, and :ref:`type-based-filtering`.

Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~~~

Hook Configuration
^^^^^^^^^^^^^^^^^^^

Enable intelligent output processing hooks for MCP servers. For comprehensive hook configuration including SummarizationHook and FileSaveHook, see :ref:`hook-configuration`.

Performance Tuning
^^^^^^^^^^^^^^^^^^

Optimize server performance for your use case. For detailed performance configuration options, see :ref:`server-configuration`.

AI Assistant Integration
------------------------

ToolUniverse MCP servers are compatible with major AI assistants and platforms:

Claude Desktop
~~~~~~~~~~~~~~

Integrate ToolUniverse with Claude Desktop for powerful desktop-based scientific research.

.. seealso::
   For complete Claude Desktop integration, see :doc:`building_ai_scientists/claude_desktop`

ChatGPT API
~~~~~~~~~~~

Connect ToolUniverse to ChatGPT API for programmatic AI-scientist workflows.

.. seealso::
   For ChatGPT API integration, see :doc:`building_ai_scientists/chatgpt_api`

Gemini CLI
~~~~~~~~~~

Use ToolUniverse with Gemini CLI for command-line scientific research.

.. seealso::
   For Gemini CLI integration, see :doc:`building_ai_scientists/gemini_cli`

Claude Code
~~~~~~~~~~~

Integrate ToolUniverse with Claude Code for IDE-based scientific development.

.. seealso::
   For Claude Code integration, see :doc:`building_ai_scientists/claude_code`

Qwen Code
~~~~~~~~~

Connect ToolUniverse to Qwen Code for terminal-based scientific workflows.

.. seealso::
   For Qwen Code integration, see :doc:`building_ai_scientists/qwen_code`

GPT Codex CLI
~~~~~~~~~~~~~

Use ToolUniverse with GPT Codex CLI for advanced command-line research capabilities.

.. seealso::
   For GPT Codex CLI integration, see :doc:`building_ai_scientists/codex_cli`

MCP Protocol Details
--------------------

Tool Discovery
~~~~~~~~~~~~~~

MCP clients can discover available tools through the standard MCP protocol. For detailed tool discovery methods and examples, see :ref:`mcp-server-integration`.

Tool Execution
~~~~~~~~~~~~~~

Execute tools through the MCP protocol. For comprehensive tool execution patterns and MCP client examples, see :ref:`mcp-client-integration`.

Error Handling
~~~~~~~~~~~~~~

MCP provides standardized error handling. For detailed error handling patterns and troubleshooting, see :ref:`error-handling-validation`.

MCP Server Management
---------------------

Server Status
~~~~~~~~~~~~~

Monitor MCP server status and health. For server management commands and status monitoring, see :ref:`discovery-commands`.

Logging and Debugging
~~~~~~~~~~~~~~~~~~~~~

Enable comprehensive logging for debugging. For detailed logging configuration and debugging options, see :ref:`tooluniverse-logging-configuration`.

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~~~

Monitor MCP server performance. For performance monitoring and optimization, see :ref:`performance-optimization`.

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~~

**MCP Server Not Starting**
   - Check if port is available
   - Verify ToolUniverse installation
   - Check server logs for error messages

**Tools Not Available**
   - Verify tool categories are loaded
   - Check tool names are correct
   - Ensure tools are not excluded

**Connection Issues**
   - Verify transport protocol matches client expectations
   - Check firewall settings for HTTP transport
   - Ensure proper authentication for remote connections

**Performance Issues**
   - Increase worker threads
   - Enable caching for repeated tool calls
   - Use specific tool categories instead of loading all tools

For comprehensive troubleshooting guide, see :ref:`troubleshooting`.

Debug Commands
~~~~~~~~~~~~~~

Useful debugging commands and validation methods. For complete debugging command reference, see :ref:`discovery-commands`.

Best Practices
--------------

Security
~~~~~~~~

- Use HTTPS in production environments
- Implement proper authentication and authorization
- Regularly update ToolUniverse and MCP dependencies
- Monitor server logs for suspicious activity

Performance
~~~~~~~~~~

- Load only necessary tool categories
- Use appropriate worker thread counts
- Enable caching for frequently used tools
- Monitor server metrics and adjust configuration

Reliability
~~~~~~~~~~~

- Implement proper error handling in MCP clients
- Use retry mechanisms for transient failures
- Monitor server health and restart if needed
- Keep backup configurations for critical deployments

For detailed best practices and production deployment guidance, see :ref:`performance-optimization`.

Related Documentation
--------------------

Core MCP Components
~~~~~~~~~~~~~~~~~~~

- :doc:`tool_caller` - Tool execution engine and MCP server implementation
- :doc:`loading_tools` - Tool loading and MCP server configuration
- :doc:`interaction_protocol` - ToolUniverse interaction protocol and MCP schema

AI Assistant Integration
~~~~~~~~~~~~~~~~~~~~~~~~

- :doc:`building_ai_scientists/index` - Complete guide to building AI scientists
- :doc:`building_ai_scientists/claude_desktop` - Claude Desktop integration
- :doc:`building_ai_scientists/chatgpt_api` - ChatGPT API integration
- :doc:`building_ai_scientists/gemini_cli` - Gemini CLI integration
- :doc:`building_ai_scientists/claude_code` - Claude Code integration
- :doc:`building_ai_scientists/qwen_code` - Qwen Code integration
- :doc:`building_ai_scientists/codex_cli` - GPT Codex CLI integration

Advanced Features
~~~~~~~~~~~~~~~~~

- :doc:`hooks/index` - Output processing hooks for MCP servers
- :doc:`scientific_workflows` - Building complex workflows with MCP
- :doc:`tool_composition` - Composing tools for advanced research

Examples and Tutorials
~~~~~~~~~~~~~~~~~~~~~~

- :doc:`examples` - Practical MCP usage examples
- :doc:`../tutorials/index` - Comprehensive tutorials for MCP integration

API Reference
~~~~~~~~~~~~~

- :doc:`../api_comprehensive` - Complete SMCP API documentation
- :doc:`../api_quick_reference` - Quick reference for common MCP operations

External Resources
~~~~~~~~~~~~~~~~~~

- `Model Context Protocol Specification <https://modelcontextprotocol.io/>`_
- `MCP GitHub Repository <https://github.com/modelcontextprotocol>`_
- `ToolUniverse GitHub Repository <https://github.com/tooluniverse/tooluniverse>`_

Summary
-------

ToolUniverse's MCP support provides a powerful, standardized way to integrate scientific tools with AI assistants. The SMCP implementation extends standard MCP capabilities with scientific domain expertise, making it easy to build sophisticated AI-scientist workflows.

Key takeaways:

- **Easy Integration**: Simple setup with major AI assistants
- **Comprehensive Tools**: Access to 600+ scientific tools through MCP
- **Flexible Configuration**: Multiple transport options and tool selection
- **Production Ready**: High-performance, secure, and reliable
- **Extensive Documentation**: Complete guides for all major AI platforms

Start with the :doc:`building_ai_scientists/index` guide to begin building your AI scientist, or explore specific integrations for your preferred AI assistant.
