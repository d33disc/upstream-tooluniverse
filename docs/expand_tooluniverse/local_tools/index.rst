Local Tools
===========

Local tools are Python classes that run within the ToolUniverse process. They provide high performance and easy integration for custom functionality.

What are Local Tools?
---------------------

Local tools extend ToolUniverse with custom Python functionality. They run in the same process as ToolUniverse and provide:

- **High Performance**: No network overhead
- **Easy Development**: Simple Python classes
- **Automatic Discovery**: Tools auto-register with decorators
- **Full Integration**: Access to all ToolUniverse features

**Best for:**
- Data processing and analysis
- File manipulation utilities
- Simple API wrappers
- Computational tools

Quick Start
-----------

**I want to quickly try creating a local tool:**
→ :doc:`../quick_start` - 5-minute tutorial to create your first tool

**I want to learn local tool development:**
→ :doc:`tutorial` - Comprehensive guide with examples

**I want to contribute a local tool:**
→ :doc:`../contributing/local_tools` - Submit your tool to ToolUniverse

**I want to understand advanced features:**
→ :doc:`advanced_features` - Learn BaseTool capabilities

Key Concepts
------------

**Tool Registration**
- Use ``@register_tool`` decorator to register your tool
- Tools are automatically discovered by ToolUniverse
- Configuration can be inline or in separate JSON files

**BaseTool Class**
- All local tools must inherit from ``BaseTool``
- Implement the ``run()`` method with your tool logic
- Add ``validate_input()`` for parameter validation

**Configuration**
- Define tool parameters using JSON Schema
- Specify required and optional parameters
- Add examples and descriptions

**Self-Use vs Contribution**
- **Self-Use**: Config in decorator, no ``__init__.py`` changes
- **Contribution**: Config in JSON file, must modify ``__init__.py``

Examples
--------

Simple Calculator
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tooluniverse.tool_registry import register_tool
   from tooluniverse.base_tool import BaseTool

   @register_tool('Calculator', config={
       "name": "calculator",
       "type": "Calculator",
       "description": "Basic mathematical operations",
       "parameter": {
           "type": "object",
           "properties": {
               "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
               "a": {"type": "number"},
               "b": {"type": "number"}
           },
           "required": ["operation", "a", "b"]
       }
   })
   class Calculator(BaseTool):
       def run(self, arguments):
           operation = arguments["operation"]
           a = arguments["a"]
           b = arguments["b"]

           if operation == "add":
               result = a + b
           elif operation == "subtract":
               result = a - b
           elif operation == "multiply":
               result = a * b
           elif operation == "divide":
               if b == 0:
                   return {"error": "Division by zero", "success": False}
               result = a / b

           return {"result": result, "success": True}

API Wrapper
~~~~~~~~~~~

.. code-block:: python

   @register_tool('WeatherAPI', config={
       "name": "weather_api",
       "type": "WeatherAPI",
       "description": "Get weather data from OpenWeatherMap",
       "parameter": {
           "type": "object",
           "properties": {
               "city": {"type": "string", "description": "City name"},
               "country": {"type": "string", "description": "Country code"}
           },
           "required": ["city"]
       },
       "settings": {
           "api_key": "env:OPENWEATHER_API_KEY",
           "base_url": "https://api.openweathermap.org/data/2.5/weather"
       }
   })
   class WeatherAPI(BaseTool):
       def __init__(self, tool_config=None):
           super().__init__(tool_config)
           self.api_key = self.config.get("settings", {}).get("api_key")
           self.base_url = self.config.get("settings", {}).get("base_url")

       def run(self, arguments):
           import requests
           
           city = arguments["city"]
           country = arguments.get("country", "")
           
           params = {
               "q": f"{city},{country}" if country else city,
               "appid": self.api_key,
               "units": "metric"
           }
           
           try:
               response = requests.get(self.base_url, params=params)
               response.raise_for_status()
               data = response.json()
               
               return {
                   "city": data["name"],
                   "temperature": data["main"]["temp"],
                   "description": data["weather"][0]["description"],
                   "success": True
               }
           except Exception as e:
               return {"error": str(e), "success": False}

Common Patterns
---------------

**Input Validation**
.. code-block:: python

   def validate_input(self, **kwargs):
       """Validate input parameters."""
       if "required_param" not in kwargs:
           raise ValueError("required_param is required")
       
       if not isinstance(kwargs["required_param"], str):
           raise ValueError("required_param must be a string")

**Error Handling**
.. code-block:: python

   def run(self, arguments):
       try:
           # Your tool logic here
           result = self.process_data(arguments)
           return {"result": result, "success": True}
       except ValueError as e:
           return {"error": f"Invalid input: {str(e)}", "success": False}
       except Exception as e:
           return {"error": f"Unexpected error: {str(e)}", "success": False}

**Using Environment Variables**
.. code-block:: python

   def __init__(self, tool_config=None):
       super().__init__(tool_config)
       self.api_key = self.config.get("settings", {}).get("api_key")

**Caching Results**
.. code-block:: python

   from functools import lru_cache

   @lru_cache(maxsize=100)
   def expensive_calculation(self, n):
       # Expensive computation here
       return result

Troubleshooting
---------------

**Tool not found**
- Check if tool is imported
- Verify ``@register_tool`` decorator
- Ensure ToolUniverse is instantiated after import

**Parameter errors**
- Check parameter definitions in config
- Verify required parameters are listed
- Ensure parameter types are correct

**Execution failures**
- Verify class inherits from ``BaseTool``
- Check ``__init__`` calls ``super().__init__(tool_config)``
- Ensure ``run()`` returns dict with ``"success"`` field

**Import errors**
- Check module name matches file name
- Verify class name matches exactly
- Ensure all dependencies are installed

Next Steps
----------

* 🚀 **Quick Start**: :doc:`../quick_start` - Create your first tool in 5 minutes
* 📚 **Tutorial**: :doc:`tutorial` - Learn local tool development
* 🎁 **Contributing**: :doc:`../contributing/local_tools` - Submit tools to ToolUniverse
* 🔧 **Advanced**: :doc:`advanced_features` - Learn advanced BaseTool capabilities
* 🔍 **Compare**: :doc:`../reference/comparison` - Compare with remote tools

.. tip::
   **Getting Started**: We recommend starting with the quick start tutorial to understand the basics, then following the comprehensive tutorial for detailed development guidance.
