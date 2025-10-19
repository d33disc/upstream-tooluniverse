Remote Tools Tutorial
=====================

Learn how to create and integrate remote tools with ToolUniverse. Remote tools run on separate servers and are accessed via MCP (Model Context Protocol) or REST APIs.

.. note::
   💡 **Self-Use**: This tutorial covers using remote tools in your own projects.
   
   🚀 **Contributing**: If you want to contribute remote tools to the ToolUniverse repository, see :doc:`../contributing/remote_tools` for additional steps.

What are Remote Tools?
----------------------

Remote tools allow you to integrate external services, APIs, or tools running on different servers. They provide:

- **Scalability**: Offload heavy computation to dedicated servers
- **Integration**: Connect with existing systems and services
- **Flexibility**: Use tools in different programming languages
- **Isolation**: Keep sensitive operations separate

**Best for:**
- External API integrations
- Microservice connections
- Cloud-based AI services
- Proprietary system connections

Quick Start with MCP
--------------------

Here's the fastest way to integrate a remote tool using MCP (Model Context Protocol):

.. code-block:: python

   # Configure MCP tools in your ToolUniverse setup
   from tooluniverse import ToolUniverse
   from tooluniverse.mcp_tool_registry import load_mcp_tools_to_tooluniverse

   # Initialize ToolUniverse
   tu = ToolUniverse()

   # Load MCP tools from a remote server
   load_mcp_tools_to_tooluniverse(
       tu,
       mcp_server_url="http://localhost:8000",
       tool_prefix="remote_"
   )

   # Use remote tools
   result = tu.run_one_function({
       "name": "remote_complex_analysis",
       "arguments": {"data": [1, 2, 3, 4, 5]}
   })

MCP (Model Context Protocol) Integration
----------------------------------------

MCP is the recommended way to integrate remote tools with ToolUniverse. It provides a standardized protocol for tool communication.

Setting up an MCP Server
~~~~~~~~~~~~~~~~~~~~~~~~~

Create a simple MCP server:

.. code-block:: python

   # mcp_server.py
   from fastapi import FastAPI
   from tooluniverse.smcp import SMCP
   import uvicorn

   app = FastAPI()
   mcp = SMCP()

   @mcp.tool("complex_analysis")
   def complex_analysis(data: list) -> dict:
       """Perform complex analysis on data."""
       # Heavy computation here
       result = sum(data) * 2  # Simplified example
       return {"analysis_result": result, "data_points": len(data)}

   @mcp.tool("weather_forecast")
   def weather_forecast(city: str, days: int = 7) -> dict:
       """Get weather forecast for a city."""
       # Simulate API call
       return {
           "city": city,
           "forecast": [{"day": i, "temp": 20 + i, "condition": "sunny"} for i in range(days)]
       }

   # Mount MCP endpoints
   app.mount("/mcp", mcp.app)

   if __name__ == "__main__":
       uvicorn.run(app, host="0.0.0.0", port=8000)

Connecting to MCP Servers
~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect to remote MCP servers from ToolUniverse:

.. code-block:: python

   from tooluniverse import ToolUniverse
   from tooluniverse.mcp_tool_registry import load_mcp_tools_to_tooluniverse

   # Initialize ToolUniverse
   tu = ToolUniverse()

   # Load tools from multiple MCP servers
   load_mcp_tools_to_tooluniverse(
       tu,
       mcp_server_url="http://localhost:8000",
       tool_prefix="local_",
       auth_token="your-api-token"
   )

   load_mcp_tools_to_tooluniverse(
       tu,
       mcp_server_url="https://remote-server.com/mcp",
       tool_prefix="cloud_",
       auth_token="cloud-api-token"
   )

   # Use tools from different servers
   result1 = tu.run_one_function({
       "name": "local_complex_analysis",
       "arguments": {"data": [1, 2, 3]}
   })

   result2 = tu.run_one_function({
       "name": "cloud_weather_forecast",
       "arguments": {"city": "New York", "days": 5}
   })

REST API Integration
--------------------

For simple REST API integration, create wrapper tools:

Basic REST API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~

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
               "data": {"type": "object", "description": "Request body data"},
               "params": {"type": "object", "description": "URL parameters"}
           },
           "required": ["url"]
       },
       "settings": {
           "default_timeout": 30,
           "max_retries": 3
       }
   })
   class RESTAPITool:
       def __init__(self, tool_config=None):
           self.tool_config = tool_config or {}
           self.default_timeout = self.tool_config.get("settings", {}).get("default_timeout", 30)
           self.max_retries = self.tool_config.get("settings", {}).get("max_retries", 3)

       def run(self, arguments):
           try:
               url = arguments["url"]
               method = arguments.get("method", "GET").upper()
               headers = arguments.get("headers", {})
               data = arguments.get("data", {})
               params = arguments.get("params", {})

               response = requests.request(
                   method=method,
                   url=url,
                   headers=headers,
                   json=data if method in ["POST", "PUT"] else None,
                   params=params,
                   timeout=self.default_timeout
               )

               response.raise_for_status()

               return {
                   "status_code": response.status_code,
                   "data": response.json() if response.content else None,
                   "headers": dict(response.headers),
                   "success": True
               }
           except requests.RequestException as e:
               return {"error": str(e), "success": False}

Specialized API Wrappers
------------------------

OpenAI API Wrapper
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @register_tool('OpenAITool', config={
       "name": "openai_completion",
       "type": "OpenAITool",
       "description": "Generate text completions using OpenAI API",
       "parameter": {
           "type": "object",
           "properties": {
               "prompt": {"type": "string", "description": "Text prompt"},
               "model": {"type": "string", "enum": ["gpt-3.5-turbo", "gpt-4"], "default": "gpt-3.5-turbo"},
               "max_tokens": {"type": "integer", "minimum": 1, "maximum": 4000, "default": 100},
               "temperature": {"type": "number", "minimum": 0, "maximum": 2, "default": 0.7}
           },
           "required": ["prompt"]
       },
       "settings": {
           "api_key": "env:OPENAI_API_KEY",
           "base_url": "https://api.openai.com/v1"
       }
   })
   class OpenAITool:
       def __init__(self, tool_config=None):
           self.tool_config = tool_config or {}
           self.api_key = self.tool_config.get("settings", {}).get("api_key")
           self.base_url = self.tool_config.get("settings", {}).get("base_url")

       def run(self, arguments):
           try:
               import openai

               openai.api_key = self.api_key

               response = openai.ChatCompletion.create(
                   model=arguments.get("model", "gpt-3.5-turbo"),
                   messages=[{"role": "user", "content": arguments["prompt"]}],
                   max_tokens=arguments.get("max_tokens", 100),
                   temperature=arguments.get("temperature", 0.7)
               )

               return {
                   "completion": response.choices[0].message.content,
                   "usage": response.usage,
                   "model": response.model,
                   "success": True
               }
           except Exception as e:
               return {"error": str(e), "success": False}

Weather API Wrapper
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @register_tool('WeatherAPITool', config={
       "name": "weather_api",
       "type": "WeatherAPITool",
       "description": "Get weather data from OpenWeatherMap API",
       "parameter": {
           "type": "object",
           "properties": {
               "city": {"type": "string", "description": "City name"},
               "country_code": {"type": "string", "description": "Country code (e.g., 'US')"},
               "units": {"type": "string", "enum": ["metric", "imperial", "kelvin"], "default": "metric"}
           },
           "required": ["city"]
       },
       "settings": {
           "api_key": "env:OPENWEATHER_API_KEY",
           "base_url": "https://api.openweathermap.org/data/2.5/weather"
       }
   })
   class WeatherAPITool:
       def __init__(self, tool_config=None):
           self.tool_config = tool_config or {}
           self.api_key = self.tool_config.get("settings", {}).get("api_key")
           self.base_url = self.tool_config.get("settings", {}).get("base_url")

       def run(self, arguments):
           try:
               city = arguments["city"]
               country_code = arguments.get("country_code")
               units = arguments.get("units", "metric")

               params = {
                   "q": f"{city},{country_code}" if country_code else city,
                   "appid": self.api_key,
                   "units": units
               }

               response = requests.get(self.base_url, params=params)
               response.raise_for_status()

               data = response.json()

               return {
                   "city": data["name"],
                   "country": data["sys"]["country"],
                   "temperature": data["main"]["temp"],
                   "feels_like": data["main"]["feels_like"],
                   "humidity": data["main"]["humidity"],
                   "pressure": data["main"]["pressure"],
                   "description": data["weather"][0]["description"],
                   "wind_speed": data["wind"]["speed"],
                   "success": True
               }
           except Exception as e:
               return {"error": str(e), "success": False}

Testing Remote Tools
--------------------

Unit Testing
~~~~~~~~~~~~

Test remote tools with mocked responses:

.. code-block:: python

   import pytest
   from unittest.mock import patch, Mock

   class TestRemoteAPITool:
       @patch('requests.get')
       def test_successful_request(self, mock_get):
           mock_response = Mock()
           mock_response.json.return_value = {"result": "success"}
           mock_response.raise_for_status.return_value = None
           mock_get.return_value = mock_response

           tool = RESTAPITool()
           result = tool.run({"url": "https://api.example.com/test"})

           assert result["success"] is True
           assert result["data"]["result"] == "success"

       @patch('requests.get')
       def test_request_failure(self, mock_get):
           mock_get.side_effect = requests.RequestException("Connection error")

           tool = RESTAPITool()
           result = tool.run({"url": "https://api.example.com/test"})

           assert result["success"] is False
           assert "error" in result

Integration Testing
~~~~~~~~~~~~~~~~~~~

Test with actual remote services:

.. code-block:: python

   def test_weather_api_integration():
       tool = WeatherAPITool()
       result = tool.run({"city": "London"})

       assert result["success"] is True
       assert "temperature" in result
       assert "city" in result

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Problem
     - Solution
   * - Connection timeout
     - Increase timeout setting, check network connectivity
   * - Authentication failed
     - Verify API keys and authentication headers
   * - Service unavailable
     - Implement retry logic and circuit breaker
   * - Rate limiting
     - Add rate limiting and exponential backoff
   * - SSL certificate errors
     - Update certificates or disable SSL verification for testing

Debugging Tools
~~~~~~~~~~~~~~~

Enable detailed logging:

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)

   # Enable requests logging
   import urllib3
   urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

   # Test connectivity
   import requests
   response = requests.get("https://api.example.com/health", timeout=10)
   print(f"Status: {response.status_code}")

Next Steps
----------

Now that you can integrate remote tools:

* 🏠 **Local Tools**: :doc:`../local_tools/tutorial` - Learn about local tool development
* 🚀 **Contributing**: :doc:`../contributing/remote_tools` - Submit your tools to ToolUniverse
* 🔧 **Advanced Patterns**: :doc:`advanced_patterns` - Advanced development patterns
* 🤖 **AI Integration**: :doc:`../guide/building_ai_scientists/mcp_integration` - Connect with AI assistants

.. tip::
   **Integration tip**: Start with simple REST API wrappers, then move to MCP for more complex integrations. Always implement proper error handling and monitoring!
