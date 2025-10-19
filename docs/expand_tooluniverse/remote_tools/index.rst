Remote Tools
============

Remote tools allow you to integrate external services, APIs, or tools running on different servers with ToolUniverse.

What are Remote Tools?
----------------------

Remote tools connect ToolUniverse with external services and systems. They provide:

- **Scalability**: Offload heavy computation to dedicated servers
- **Integration**: Connect with existing systems and services
- **Flexibility**: Use tools in different programming languages
- **Isolation**: Keep sensitive operations separate

**Best for:**
- External API integrations
- Microservice connections
- Cloud-based AI services
- Proprietary system connections

Quick Start
-----------

**I want to quickly try remote tools:**
→ :doc:`tutorial` - Learn basic remote tool integration

**I want to create an MCP server:**
→ :doc:`mcp_server` - Learn MCP server development

**I want to contribute a remote tool:**
→ :doc:`../contributing/remote_tools` - Submit your tool to ToolUniverse

**I want to learn advanced patterns:**
→ :doc:`advanced_patterns` - Circuit breakers, load balancing, etc.

Key Concepts
------------

**MCP (Model Context Protocol)**
- Standardized protocol for tool communication
- Language agnostic
- Supports authentication and error handling
- Recommended approach for remote tools

**REST API Integration**
- Simple HTTP-based integration
- Good for existing APIs
- Easier to implement but less standardized

**Configuration**
- Remote tools defined in JSON configuration files
- Specify server URLs, authentication, and parameters
- No ``__init__.py`` modifications needed

**Self-Use vs Contribution**
- **Self-Use**: Local server or private deployment
- **Contribution**: Public server or detailed deployment docs

Examples
--------

MCP Server
~~~~~~~~~~

.. code-block:: python

   from fastapi import FastAPI
   from tooluniverse.smcp import SMCP
   import uvicorn

   app = FastAPI(title="My MCP Server")
   mcp = SMCP()

   @mcp.tool("text_processor")
   def text_processor(text: str, operation: str = "uppercase") -> dict:
       """Process text with various operations."""
       if operation == "uppercase":
           result = text.upper()
       elif operation == "lowercase":
           result = text.lower()
       elif operation == "reverse":
           result = text[::-1]
       else:
           raise ValueError(f"Unknown operation: {operation}")
       
       return {
           "result": result,
           "operation": operation,
           "original": text
       }

   app.mount("/mcp", mcp.app)

   if __name__ == "__main__":
       uvicorn.run(app, host="0.0.0.0", port=8000)

REST API Wrapper
~~~~~~~~~~~~~~~~

.. code-block:: python

   from tooluniverse.tool_registry import register_tool
   import requests

   @register_tool('RESTAPITool', config={
       "name": "rest_api_call",
       "type": "RESTAPITool",
       "description": "Make REST API calls to external services",
       "parameter": {
           "type": "object",
           "properties": {
               "url": {"type": "string", "description": "API endpoint URL"},
               "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
               "headers": {"type": "object", "description": "HTTP headers"},
               "data": {"type": "object", "description": "Request body data"}
           },
           "required": ["url"]
       }
   })
   class RESTAPITool:
       def run(self, arguments):
           try:
               url = arguments["url"]
               method = arguments.get("method", "GET").upper()
               headers = arguments.get("headers", {})
               data = arguments.get("data", {})

               response = requests.request(
                   method=method,
                   url=url,
                   headers=headers,
                   json=data if method in ["POST", "PUT"] else None
               )

               response.raise_for_status()
               return {
                   "status_code": response.status_code,
                   "data": response.json() if response.content else None,
                   "success": True
               }
           except Exception as e:
               return {"error": str(e), "success": False}

Connecting to Remote Tools
--------------------------

**MCP Auto-Discovery**
.. code-block:: python

   from tooluniverse import ToolUniverse
   from tooluniverse.mcp_tool_registry import load_mcp_tools_to_tooluniverse

   tu = ToolUniverse()
   tu.load_tools()

   # Auto-discover tools from MCP server
   load_mcp_tools_to_tooluniverse(
       tu,
       mcp_server_url="http://localhost:8000",
       tool_prefix="remote_"
   )

**Configuration File**
.. code-block:: json

   [
     {
       "type": "RemoteTool",
       "name": "my_remote_tool",
       "description": "My remote tool",
       "parameter": {
         "type": "object",
         "properties": {
           "input": {"type": "string", "description": "Input parameter"}
         },
         "required": ["input"]
       },
       "remote_info": {
         "server_type": "MCP",
         "transport": "http",
         "url": "http://localhost:8000/mcp"
       }
     }
   ]

Common Patterns
---------------

**Error Handling**
.. code-block:: python

   def run(self, arguments):
       try:
           # Make remote call
           result = self.call_remote_service(arguments)
           return {"result": result, "success": True}
       except requests.Timeout:
           return {"error": "Request timeout", "success": False}
       except requests.ConnectionError:
           return {"error": "Connection failed", "success": False}
       except Exception as e:
           return {"error": str(e), "success": False}

**Authentication**
.. code-block:: python

   def __init__(self, tool_config=None):
       super().__init__(tool_config)
       self.api_key = self.config.get("settings", {}).get("api_key")
       self.base_url = self.config.get("settings", {}).get("base_url")

   def run(self, arguments):
       headers = {"Authorization": f"Bearer {self.api_key}"}
       # Use headers in request

**Caching**
.. code-block:: python

   from functools import lru_cache

   @lru_cache(maxsize=100)
   def cached_remote_call(self, url, params):
       # Make remote call
       return result

**Rate Limiting**
.. code-block:: python

   import time
   from collections import defaultdict

   class RateLimiter:
       def __init__(self, max_requests=100, window_size=60):
           self.max_requests = max_requests
           self.window_size = window_size
           self.requests = defaultdict(list)

       def is_allowed(self, client_id):
           now = time.time()
           client_requests = self.requests[client_id]
           
           # Remove old requests
           client_requests[:] = [req_time for req_time in client_requests 
                               if now - req_time < self.window_size]
           
           if len(client_requests) >= self.max_requests:
               return False
           
           client_requests.append(now)
           return True

Troubleshooting
---------------

**Connection Errors**
- Check server URL and port
- Verify network connectivity
- Check firewall settings

**Authentication Failures**
- Verify API keys and tokens
- Check authentication headers
- Ensure credentials are valid

**Timeout Issues**
- Increase timeout settings
- Check server performance
- Implement retry logic

**Tool Discovery Problems**
- Verify MCP server is running
- Check tool registration
- Ensure proper configuration

Next Steps
----------

* 📚 **Tutorial**: :doc:`tutorial` - Learn remote tool integration
* 🔧 **MCP Server**: :doc:`mcp_server` - Learn MCP server development
* 🚀 **Advanced**: :doc:`advanced_patterns` - Learn advanced patterns
* 🎁 **Contributing**: :doc:`../contributing/remote_tools` - Submit tools to ToolUniverse
* 🔍 **Compare**: :doc:`../reference/comparison` - Compare with local tools

.. tip::
   **Getting Started**: We recommend starting with the tutorial to understand basic concepts, then choosing the appropriate guide based on your needs. MCP is the recommended approach for new remote tools.
