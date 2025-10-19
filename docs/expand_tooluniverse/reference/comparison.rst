Tool Types and Usage Scenarios Comparison
==========================================

This document provides clear comparisons between different tool types and usage scenarios to help you choose the right approach.

Tool Types: Local vs Remote
----------------------------

| Dimension | Local Tools | Remote Tools |
|-----------|-------------|--------------|
| **Implementation** | Python class (BaseTool) | MCP server + JSON config |
| **File Location** | ``src/tooluniverse/xxx_tool.py`` | ``data/remote_tools/xxx_tools.json`` |
| **Registration** | ``@register_tool`` + modify ``__init__.py`` | JSON configuration file |
| **Runtime Environment** | ToolUniverse process | Independent server process |
| **Communication** | Direct function calls | HTTP/stdio protocol |
| **Dependencies** | Python package dependencies | Independent deployment |
| **Use Cases** | API wrappers, data processing, lightweight computation | Microservice integration, heavy computation, cross-language tools |

Local Tools: Self-Use vs Contribution
-------------------------------------

| Dimension | Self-Use | Contribution to Repository |
|-----------|----------|---------------------------|
| **File Location** | Anywhere in your project | ``src/tooluniverse/xxx_tool.py`` |
| **Config Definition** | ``@register_tool('Type', config={...})`` | ``data/xxx_tools.json`` |
| **Modify __init__.py** | ❌ Not required | ✅ **Must modify 4 locations** |
| **Tool Loading** | ``import`` or ``register_custom_tool()`` | Automatic loading |
| **Testing** | Optional | Required (>90% coverage) |
| **Documentation** | Optional | Required (docstrings + examples) |
| **Examples** | Optional | Required (in ``examples/``) |
| **Code Quality** | Optional | Required (pre-commit checks) |

Remote Tools: Self-Use vs Contribution
---------------------------------------

| Dimension | Self-Use | Contribution to Repository |
|-----------|----------|---------------------------|
| **Config Location** | Anywhere in your project | ``data/remote_tools/`` |
| **Config Loading** | Manual specification | Automatic loading |
| **Server Deployment** | Local or private | Public access or detailed deployment docs |
| **Server Code** | Can be private | Should be in ``remote/`` directory |
| **Modify __init__.py** | ❌ Not required | ❌ Not required |
| **Testing** | Optional | Required (integration tests) |
| **Documentation** | Optional | Required (server README + API docs) |
| **Examples** | Optional | Required (in ``examples/``) |

Self-Use Tool Loading Methods
-----------------------------

**Local Tools - Self-Use Loading:**

**Method 1: Decorator with Config (Simplest)**
.. code-block:: python

   from tooluniverse.tool_registry import register_tool
   from tooluniverse.base_tool import BaseTool

   @register_tool('MyTool', config={
       "name": "my_tool",
       "type": "MyTool",
       "description": "My custom tool",
       "parameter": {
           "type": "object",
           "properties": {
               "input": {"type": "string"}
           },
           "required": ["input"]
       }
   })
   class MyTool(BaseTool):
       def run(self, arguments):
           return {"result": arguments["input"].upper()}

   # Import to register
   from my_tool import MyTool

   # Use with ToolUniverse
   from tooluniverse import ToolUniverse
   tu = ToolUniverse()
   tu.load_tools()
   result = tu.run_one_function({
       "name": "my_tool",
       "arguments": {"input": "hello"}
   })

**Method 2: Runtime Registration (More Flexible)**
.. code-block:: python

   from tooluniverse import ToolUniverse
   from tooluniverse.base_tool import BaseTool

   class MyTool(BaseTool):
       def run(self, arguments):
           return {"result": arguments["input"].upper()}

   tu = ToolUniverse()

   # Register at runtime
   tu.register_custom_tool(
       tool_class=MyTool,
       tool_name="MyTool",
       tool_config={
           "name": "my_tool",
           "type": "MyTool",
           "description": "My custom tool",
           "parameter": {
               "type": "object",
               "properties": {
                   "input": {"type": "string"}
               },
               "required": ["input"]
           }
       }
   )

   # Use immediately
   result = tu.run_one_function({
       "name": "my_tool",
       "arguments": {"input": "hello"}
   })

**Method 3: Configuration File**
.. code-block:: python

   # my_tools.json
   [{
       "name": "my_tool",
       "type": "MyTool",
       "description": "My custom tool",
       "parameter": {
           "type": "object",
           "properties": {
               "input": {"type": "string"}
           },
           "required": ["input"]
       }
   }]

   # my_tool.py
   from tooluniverse.tool_registry import register_tool
   from tooluniverse.base_tool import BaseTool

   @register_tool('MyTool')  # No config here
   class MyTool(BaseTool):
       def run(self, arguments):
           return {"result": arguments["input"].upper()}

   # main.py
   from tooluniverse import ToolUniverse
   from my_tool import MyTool

   # Load custom config
   tu = ToolUniverse(tool_files={
       "my_tools": "path/to/my_tools.json"
   })
   tu.load_tools()

**Remote Tools - Self-Use Loading:**

**Method 1: MCP Auto-Loader**
.. code-block:: python

   from tooluniverse import ToolUniverse
   from tooluniverse.mcp_tool_registry import load_mcp_tools_to_tooluniverse

   tu = ToolUniverse()
   tu.load_tools()

   # Auto-discover and load tools from MCP server
   load_mcp_tools_to_tooluniverse(tu, server_urls=[
       "http://localhost:8000",
       "http://my-server.com:8001"
   ])

   # Use discovered tools
   result = tu.run_one_function({
       "name": "mcp_discovered_tool",
       "arguments": {"param": "value"}
   })

**Method 2: Custom Configuration File**
.. code-block:: python

   # my_remote_tools.json
   [{
       "type": "RemoteTool",
       "name": "my_remote_tool",
       "description": "My remote tool",
       "parameter": {
           "type": "object",
           "properties": {
               "input": {"type": "string"}
           },
           "required": ["input"]
       },
       "remote_info": {
           "server_type": "MCP",
           "transport": "http",
           "url": "http://localhost:8000/mcp"
       }
   }]

   # Load custom remote tools
   from tooluniverse import ToolUniverse
   tu = ToolUniverse(tool_files={
       "my_remote_tools": "path/to/my_remote_tools.json"
   })
   tu.load_tools()

   result = tu.run_one_function({
       "name": "my_remote_tool",
       "arguments": {"input": "hello"}
   })

**Method 3: MCPAutoLoaderTool Configuration**
.. code-block:: python

   # In your config file
   {
       "name": "my_mcp_loader",
       "type": "MCPAutoLoaderTool",
       "server_url": "http://localhost:8000",
       "tool_prefix": "my_",
       "auto_register": true
   }

Decision Tree
-------------

**I want to...**

**🚀 Quickly test a tool idea**
→ Use :doc:`../quick_start` (Local tool with decorator)

**📚 Learn tool development systematically**
→ Choose based on your needs:
   - **Local tools**: :doc:`../local_tools/tutorial` (API wrappers, data processing)
   - **Remote tools**: :doc:`../remote_tools/tutorial` (microservices, heavy computation)

**🎁 Contribute tools to the community**
→ Choose based on tool type:
   - **Local tools**: :doc:`../contributing/local_tools` (must modify ``__init__.py``)
   - **Remote tools**: :doc:`../contributing/remote_tools` (must deploy server)

**🔍 Understand the architecture**
→ See :doc:`architecture` (system design and internals)

Key Takeaways
--------------

**For Self-Use:**
- **Local tools**: Flexible loading, no core code changes needed
- **Remote tools**: Need running server, config file specifies connection

**For Contribution:**
- **Local tools**: Must modify ``__init__.py`` in 4 locations (critical!)
- **Remote tools**: Must provide public server or deployment docs

**Common Mistakes:**
- Trying to contribute without modifying ``__init__.py`` (Local tools)
- Forgetting to deploy server publicly (Remote tools)
- Putting config in wrong location (``data/`` vs ``data/remote_tools/``)

**Quick Reference:**
- **Self-use Local**: Decorator + config in same file
- **Contribute Local**: Separate files + modify ``__init__.py``
- **Self-use Remote**: Config file + local server
- **Contribute Remote**: Config in ``remote_tools/`` + public server
