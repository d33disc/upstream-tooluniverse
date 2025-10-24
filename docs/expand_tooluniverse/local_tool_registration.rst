Local Tool Registration
=================================

Learn how to create, register, and use custom tools locally within ToolUniverse. This Tutorial covers everything from basic tool creation to advanced patterns and best practices.

Overview
--------

Local tools are Python classes that run within the same process as ToolUniverse. They provide the most efficient way to extend ToolUniverse functionality for your specific research needs.

Quick Start
-----------

Here's the fastest way to create and register a local tool:

.. code-block:: python

   # my_custom_tool.py - Place in src/tooluniverse/
   from tooluniverse.tool_registry import register_tool
   from tooluniverse.base_tool import BaseTool
   from typing import Dict, Any

   @register_tool('ProteinCalculator', config={
       "name": "protein_molecular_weight",
       "type": "ProteinCalculator",
       "description": "Calculate molecular weight of protein sequences",
       "parameter": {
           "type": "object",
           "properties": {
               "sequence": {"type": "string", "description": "Protein sequence (single letter amino acid codes)"}
           },
           "required": ["sequence"]
       }
   })
   class ProteinCalculator(BaseTool):
       """Calculate molecular weight of protein sequences."""

       def __init__(self, tool_config: Dict[str, Any] = None):
           super().__init__(tool_config)
           # Amino acid molecular weights (in Daltons)
           self.aa_weights = {
               'A': 89.09, 'R': 174.20, 'N': 132.12, 'D': 133.10,
               'C': 121.16, 'Q': 146.15, 'E': 147.13, 'G': 75.07,
               'H': 155.16, 'I': 131.17, 'L': 131.17, 'K': 146.19,
               'M': 149.21, 'F': 165.19, 'P': 115.13, 'S': 105.09,
               'T': 119.12, 'W': 204.23, 'Y': 181.19, 'V': 117.15
           }

       def execute(self, sequence: str, **kwargs) -> Dict[str, Any]:
           """Calculate molecular weight of a protein sequence."""
           # Validate inputs
           self.validate_input(sequence=sequence)

           # Clean sequence (remove whitespace, convert to uppercase)
           clean_sequence = sequence.strip().upper()

           # Calculate molecular weight
           total_weight = sum(self.aa_weights.get(aa, 0) for aa in clean_sequence)
           # Subtract water molecules for peptide bonds
           water_weight = (len(clean_sequence) - 1) * 18.015
           molecular_weight = total_weight - water_weight

           return {
               "molecular_weight": round(molecular_weight, 2),
               "sequence_length": len(clean_sequence),
               "sequence": clean_sequence,
               "success": True
           }

       def validate_input(self, **kwargs) -> None:
           """Validate input parameters."""
           sequence = kwargs.get('sequence')

           if not sequence:
               raise ValueError("Sequence is required")

           if not isinstance(sequence, str):
               raise ValueError("Sequence must be a string")

           if len(sequence.strip()) == 0:
               raise ValueError("Sequence cannot be empty")

   # Usage
   from tooluniverse import ToolUniverse

   tu = ToolUniverse()
   tu.load_tools()  # Auto-discovers and loads your tool

   result = tu.run_one_function({
       "name": "protein_molecular_weight",
       "arguments": {"sequence": "GIVEQCCTSICSLYQLENYCN"}
   })

Step-by-Step Tool Creation
--------------------------

**Important: Inherit from BaseTool**

All ToolUniverse tools should inherit from the ``BaseTool`` class. This provides:


BaseTool Class
--------------

ToolUniverse provides the ``BaseTool`` class as the foundation for all custom tools. Inheriting from ``BaseTool`` ensures your tools follow ToolUniverse standards and provides several benefits:

**Core Features:**
- **Standardized Interface**: All tools use the same ``execute()`` method signature
- **Built-in Validation**: Automatic input validation framework via ``validate_input()``
- **Configuration Management**: Built-in handling of tool configuration
- **Error Handling**: Consistent error handling patterns
- **Logging Support**: Integrated logging capabilities
- **Type Safety**: Better IDE support with type hints

**BaseTool Structure:**
.. code-block:: python

   from tooluniverse.base_tool import BaseTool
   from typing import Dict, Any

   class MyTool(BaseTool):
       def __init__(self, tool_config: Dict[str, Any] = None):
           super().__init__(tool_config)
           # Initialize your tool here

       def execute(self, param1: str, param2: int = 10, **kwargs) -> Dict[str, Any]:
           """Main execution method - implement your tool logic here."""
           # Validate inputs
           self.validate_input(param1=param1, param2=param2)

           # Your tool logic here
           result = self._process_data(param1, param2)

           return {"result": result, "success": True}

       def validate_input(self, **kwargs) -> None:
           """Validate input parameters."""
           param1 = kwargs.get('param1')
           param2 = kwargs.get('param2', 10)

           if not param1 or not isinstance(param1, str):
               raise ValueError("param1 must be a non-empty string")

           if not isinstance(param2, int) or param2 < 0:
               raise ValueError("param2 must be a non-negative integer")

**Key Methods:**
- ``__init__(tool_config)``: Initialize tool with configuration
- ``execute(**kwargs)``: Main execution method (required)
- ``validate_input(**kwargs)``: Input validation (recommended)
- ``config``: Access to tool configuration
- ``logger``: Built-in logging instance


- **Standardized Interface**: Consistent ``execute()`` method signature
- **Built-in Validation**: Automatic input validation framework
- **Error Handling**: Standardized error handling patterns
- **Configuration Management**: Built-in configuration handling
- **Logging Support**: Integrated logging capabilities
- **Type Hints**: Better IDE support and code clarity

1. **Create Your Tool File**

   Create a new Python file:

   .. code-block:: python

      # weather_tool.py
      from tooluniverse.tool_registry import register_tool
      from tooluniverse.base_tool import BaseTool
      from typing import Dict, Any
      import requests

      @register_tool('WeatherTool', config={
          "name": "weather_lookup",
          "type": "WeatherTool",
          "description": "Get current weather for a city",
          "parameter": {
              "type": "object",
              "properties": {
                  "city": {"type": "string", "description": "City name"},
                  "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"}
              },
              "required": ["city"]
          },
          "settings": {
              "api_key": "env:WEATHER_API_KEY",
              "base_url": "https://api.openweathermap.org/data/2.5/weather"
          }
      })
      class WeatherTool(BaseTool):
          """Get current weather for a city."""

          def __init__(self, tool_config: Dict[str, Any] = None):
              super().__init__(tool_config)
              self.api_key = self.config.get("settings", {}).get("api_key")
              self.base_url = self.config.get("settings", {}).get("base_url")

          def execute(self, city: str, units: str = "metric", **kwargs) -> Dict[str, Any]:
              """Get current weather for a city."""
              # Validate inputs
              self.validate_input(city=city, units=units)

              try:
                  response = requests.get(
                      self.base_url,
                      params={"q": city, "appid": self.api_key, "units": units}
                  )
                  response.raise_for_status()

                  data = response.json()
                  return {
                      "city": data["name"],
                      "temperature": data["main"]["temp"],
                      "description": data["weather"][0]["description"],
                      "humidity": data["main"]["humidity"],
                      "success": True
                  }
              except Exception as e:
                  return {"error": str(e), "success": False}

          def validate_input(self, **kwargs) -> None:
              """Validate input parameters."""
              city = kwargs.get('city')
              units = kwargs.get('units', 'metric')

              if not city:
                  raise ValueError("City is required")

              if not isinstance(city, str):
                  raise ValueError("City must be a string")

              if units not in ["metric", "imperial"]:
                  raise ValueError("Units must be 'metric' or 'imperial'")

2. **Test Your Tool**

   .. code-block:: python

      from tooluniverse import ToolUniverse

      tu = ToolUniverse()
      tu.load_tools()

      # Test the tool
      result = tu.run_one_function({
          "name": "weather_lookup",
          "arguments": {"city": "London", "units": "metric"}
      })
      print(result)

Tool Registration Methods
-------------------------

Method 1: Decorator Registration (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``@register_tool`` decorator for automatic registration:

.. code-block:: python

   from tooluniverse.tool_registry import register_tool

   @register_tool('MyTool', config={
       "name": "my_tool",
       "type": "MyTool",
       "description": "Description of what the tool does",
       "parameter": {
           "type": "object",
           "properties": {
               "param1": {"type": "string", "description": "Parameter description"},
               "param2": {"type": "integer", "minimum": 0, "default": 10}
           },
           "required": ["param1"]
       }
   })
   class MyTool:
       def run(self, arguments):
           # Tool implementation
           pass

Method 2: Manual Registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register tools manually for more control:

.. code-block:: python

   from tooluniverse.tool_registry import ToolRegistry

   # Create tool instance
   tool = MyTool()

   # Create tool configuration
   tool_config = {
       "name": "my_tool",
       "type": "MyTool",
       "description": "Description of what the tool does",
       "parameter": {
           "type": "object",
           "properties": {
               "param1": {"type": "string", "description": "Parameter description"}
           },
           "required": ["param1"]
       }
   }

   # Register with ToolUniverse
   registry = ToolRegistry()
   registry.register_tool(tool_config, tool)

Method 3: Configuration File Registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a JSON configuration file:

.. code-block:: json

   {
       "tools": [
           {
               "name": "my_tool",
               "type": "MyTool",
               "description": "Description of what the tool does",
               "module_path": "my_tools.my_module",
               "class_name": "MyTool",
               "parameter": {
                   "type": "object",
                   "properties": {
                       "param1": {"type": "string", "description": "Parameter description"}
                   },
                   "required": ["param1"]
               }
           }
       ]
   }

Load configuration file:

.. code-block:: python

   from tooluniverse import ToolUniverse

   # Load tools from configuration file
   tu = ToolUniverse()
   tu.load_tools_from_config("my_tools_config.json")

Common Tool Patterns
--------------------

API Wrapper Tool
~~~~~~~~~~~~~~~~

.. code-block:: python

   from tooluniverse.base_tool import BaseTool
   from typing import Dict, Any

   @register_tool('APITool', config={
       "name": "api_wrapper",
       "type": "APITool",
       "description": "Wrapper for external API",
       "parameter": {
           "type": "object",
           "properties": {
               "url": {"type": "string", "description": "API endpoint URL"},
               "method": {"type": "string", "enum": ["GET", "POST"], "default": "GET"},
               "data": {"type": "object", "description": "Request data"}
           },
           "required": ["url"]
       }
   })
   class APITool(BaseTool):
       """Wrapper for external API calls."""

       def execute(self, url: str, method: str = "GET", data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
           """Make API call to specified URL."""
           self.validate_input(url=url, method=method)

           try:
               if method == "GET":
                   response = requests.get(url)
               else:
                   response = requests.post(url, json=data or {})

               response.raise_for_status()
               return {"data": response.json(), "success": True}
           except Exception as e:
               return {"error": str(e), "success": False}

       def validate_input(self, **kwargs) -> None:
           """Validate input parameters."""
           url = kwargs.get('url')
           method = kwargs.get('method', 'GET')

           if not url or not isinstance(url, str):
               raise ValueError("URL must be a non-empty string")

           if method not in ["GET", "POST"]:
               raise ValueError("Method must be 'GET' or 'POST'")

File Processor Tool
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tooluniverse.base_tool import BaseTool
   from typing import Dict, Any

   @register_tool('FileProcessor', config={
       "name": "file_processor",
       "type": "FileProcessor",
       "description": "Process files and return results",
       "parameter": {
           "type": "object",
           "properties": {
               "file_path": {"type": "string", "description": "Path to input file"},
               "operation": {"type": "string", "enum": ["read", "analyze", "convert"], "default": "read"}
           },
           "required": ["file_path"]
       }
   })
   class FileProcessor(BaseTool):
       """Process files and return results."""

       def execute(self, file_path: str, operation: str = "read", **kwargs) -> Dict[str, Any]:
           """Process file based on specified operation."""
           self.validate_input(file_path=file_path, operation=operation)

           try:
               with open(file_path, 'r') as f:
                   content = f.read()

               if operation == "analyze":
                   result = self._analyze_content(content)
               elif operation == "convert":
                   result = self._convert_content(content)
               else:
                   result = {"content": content}

               return {"result": result, "success": True}
           except Exception as e:
               return {"error": str(e), "success": False}

       def validate_input(self, **kwargs) -> None:
           """Validate input parameters."""
           file_path = kwargs.get('file_path')
           operation = kwargs.get('operation', 'read')

           if not file_path or not isinstance(file_path, str):
               raise ValueError("File path must be a non-empty string")

           if operation not in ["read", "analyze", "convert"]:
               raise ValueError("Operation must be 'read', 'analyze', or 'convert'")

       def _analyze_content(self, content: str) -> Dict[str, Any]:
           """Analyze file content."""
           return {"lines": len(content.split('\n')), "chars": len(content)}

       def _convert_content(self, content: str) -> Dict[str, Any]:
           """Convert file content."""
           return {"converted": content.upper()}

Database Tool
~~~~~~~~~~~~~

.. code-block:: python

   from tooluniverse.base_tool import BaseTool
   from typing import Dict, Any

   @register_tool('DatabaseTool', config={
       "name": "database_query",
       "type": "DatabaseTool",
       "description": "Query database and return results",
       "parameter": {
           "type": "object",
           "properties": {
               "query": {"type": "string", "description": "SQL query"},
               "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100}
           },
           "required": ["query"]
       },
       "settings": {
           "database_url": "env:DATABASE_URL"
       }
   })
   class DatabaseTool(BaseTool):
       """Query database and return results."""

       def __init__(self, tool_config: Dict[str, Any] = None):
           super().__init__(tool_config)
           self.db_url = self.config.get("settings", {}).get("database_url")

       def execute(self, query: str, limit: int = 100, **kwargs) -> Dict[str, Any]:
           """Execute database query."""
           self.validate_input(query=query, limit=limit)

           try:
               import sqlite3

               conn = sqlite3.connect(self.db_url)
               cursor = conn.cursor()

               cursor.execute(f"{query} LIMIT {limit}")
               results = cursor.fetchall()

               columns = [description[0] for description in cursor.description]
               data = [dict(zip(columns, row)) for row in results]

               conn.close()

               return {"data": data, "count": len(data), "success": True}
           except Exception as e:
               return {"error": str(e), "success": False}

       def validate_input(self, **kwargs) -> None:
           """Validate input parameters."""
           query = kwargs.get('query')
           limit = kwargs.get('limit', 100)

           if not query or not isinstance(query, str):
               raise ValueError("Query must be a non-empty string")

           if not isinstance(limit, int) or limit < 1 or limit > 1000:
               raise ValueError("Limit must be an integer between 1 and 1000")

Advanced Tool Features
----------------------

Adding Caching
~~~~~~~~~~~~~~

.. code-block:: python

   from functools import lru_cache
   import hashlib
   import json
   from tooluniverse.base_tool import BaseTool
   from typing import Dict, Any

   class CachedTool(BaseTool):
       """Tool with caching capabilities."""

       def __init__(self, tool_config: Dict[str, Any] = None):
           super().__init__(tool_config)
           self.cache_enabled = self.config.get("settings", {}).get("cache_enabled", True)

       def execute(self, **kwargs) -> Dict[str, Any]:
           """Execute with caching support."""
           if self.cache_enabled:
               cache_key = self._generate_cache_key(kwargs)
               cached_result = self._get_from_cache(cache_key)
               if cached_result:
                   return cached_result

           result = self._process_arguments(kwargs)

           if self.cache_enabled:
               self._save_to_cache(cache_key, result)

           return result

       def _generate_cache_key(self, arguments: Dict[str, Any]) -> str:
           """Generate a unique cache key."""
           cache_data = dict(arguments)
           cache_string = json.dumps(cache_data, sort_keys=True)
           return hashlib.md5(cache_string.encode()).hexdigest()

       def _get_from_cache(self, cache_key: str) -> Dict[str, Any]:
           """Get result from cache."""
           # Implement your caching logic here
           return None

       def _save_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
           """Save result to cache."""
           # Implement your caching logic here
           pass

       def _process_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
           """Process arguments and return result."""
           # Implement your tool logic here
           return {"result": "processed", "success": True}

Rate Limiting
~~~~~~~~~~~~~

.. code-block:: python

   import time
   from collections import deque

   class RateLimitedTool:
       def __init__(self, tool_config=None):
           self.tool_config = tool_config or {}
           self.rate_limit = self.tool_config.get("settings", {}).get("rate_limit", 10)
           self.request_times = deque()

       def _enforce_rate_limit(self):
           now = time.time()

           # Remove old requests outside the time window
           while self.request_times and now - self.request_times[0] >= 1.0:
               self.request_times.popleft()

           # Check if we've hit the rate limit
           if len(self.request_times) >= self.rate_limit:
               sleep_time = 1.0 - (now - self.request_times[0])
               if sleep_time > 0:
                   time.sleep(sleep_time)

           self.request_times.append(now)

       def run(self, arguments):
           self._enforce_rate_limit()
           return self._process_arguments(arguments)

Error Handling and Retries
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   import random
   from requests.exceptions import RequestException

   class RobustTool:
       def __init__(self, tool_config=None):
           self.tool_config = tool_config or {}
           self.max_retries = self.tool_config.get("settings", {}).get("max_retries", 3)
           self.retry_delay = self.tool_config.get("settings", {}).get("retry_delay", 1.0)

       def run(self, arguments):
           last_exception = None

           for attempt in range(self.max_retries + 1):
               try:
                   return self._process_arguments(arguments)
               except RequestException as e:
                   last_exception = e
                   if attempt < self.max_retries:
                       # Exponential backoff with jitter
                       delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                       time.sleep(delay)
                   continue

           return {"error": f"Failed after {self.max_retries} retries: {str(last_exception)}", "success": False}

Tool Configuration
------------------

Configuration Schema
~~~~~~~~~~~~~~~~~~~~

All tools require a configuration that follows this schema:

.. code-block:: python

   config = {
       "name": "tool_name",           # Unique identifier for the tool
       "type": "ToolClassName",       # Python class name
       "description": "What it does", # Human-readable description
       "parameter": {                 # JSON Schema for parameters
           "type": "object",
           "properties": {
               "param1": {"type": "string", "description": "Description"},
               "param2": {"type": "integer", "minimum": 0, "default": 10}
           },
           "required": ["param1"]
       },
       "settings": {                  # Optional tool-specific settings
           "api_key": "env:API_KEY",  # Environment variable reference
           "timeout": 30,
           "retries": 3
       }
   }

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Use environment variables for sensitive configuration:

.. code-block:: python

   "settings": {
       "api_key": "env:OPENAI_API_KEY",
       "database_url": "env:DATABASE_URL",
       "secret_token": "env:SECRET_TOKEN"
   }

Set these in your environment:

.. code-block:: bash

   export OPENAI_API_KEY="your-api-key"
   export DATABASE_URL="postgresql://user:pass@localhost/db"
   export SECRET_TOKEN="your-secret-token"

Parameter Validation
~~~~~~~~~~~~~~~~~~~~

Use JSON Schema to define and validate parameters:

.. code-block:: python

   "parameter": {
       "type": "object",
       "properties": {
           "query": {
               "type": "string",
               "description": "Search query",
               "minLength": 1
           },
           "limit": {
               "type": "integer",
               "description": "Maximum results",
               "minimum": 1,
               "maximum": 100,
               "default": 10
           },
           "filters": {
               "type": "object",
               "properties": {
                   "category": {"type": "string", "enum": ["A", "B", "C"]},
                   "date_range": {"type": "array", "items": {"type": "string"}}
               }
           }
       },
       "required": ["query"]
   }

Best Practices
--------------

BaseTool Inheritance
~~~~~~~~~~~~~~~~~~~~

**Always inherit from BaseTool:**

.. code-block:: python

   from tooluniverse.base_tool import BaseTool
   from typing import Dict, Any

   class MyTool(BaseTool):
       def __init__(self, tool_config: Dict[str, Any] = None):
           super().__init__(tool_config)
           # Initialize your tool

       def execute(self, param1: str, **kwargs) -> Dict[str, Any]:
           """Main execution method."""
           self.validate_input(param1=param1)
           # Your logic here
           return {"result": "success", "success": True}

       def validate_input(self, **kwargs) -> None:
           """Validate inputs."""
           param1 = kwargs.get('param1')
           if not param1:
               raise ValueError("param1 is required")

**Benefits of BaseTool inheritance:**
- Consistent interface across all tools
- Built-in validation framework
- Standardized error handling
- Configuration management
- Logging support
- Type safety

Error Handling
~~~~~~~~~~~~~~

Always implement proper error handling:

.. code-block:: python

   def execute(self, param1: str, **kwargs) -> Dict[str, Any]:
       """Execute with proper error handling."""
       try:
           # Validate inputs first
           self.validate_input(param1=param1)

           # Your tool logic here
           result = self.process_data(param1)
           return {"result": result, "success": True}

       except ValueError as e:
           # Input validation errors
           return {"error": f"Invalid input: {str(e)}", "success": False}
       except requests.RequestException as e:
           # Network errors
           return {"error": f"Network error: {str(e)}", "success": False}
       except Exception as e:
           # Unexpected errors
           return {"error": f"Unexpected error: {str(e)}", "success": False}

Input Validation
~~~~~~~~~~~~~~~~

Validate inputs before processing:

.. code-block:: python

   def validate_input(self, **kwargs) -> None:
       """Validate input parameters."""
       param1 = kwargs.get('param1')
       param2 = kwargs.get('param2', 10)

       # Validate required parameters
       if not param1:
           raise ValueError("param1 is required")

       if not isinstance(param1, str):
           raise ValueError("param1 must be a string")

       if len(param1.strip()) == 0:
           raise ValueError("param1 cannot be empty")

       # Validate parameter types and ranges
       if not isinstance(param2, int) or param2 < 1 or param2 > 100:
           raise ValueError("param2 must be an integer between 1 and 100")

Consistent Return Format
~~~~~~~~~~~~~~~~~~~~~~~~

Always return a dictionary with consistent structure:

.. code-block:: python

   # Success response
   return {
       "data": result_data,
       "success": True,
       "metadata": {"count": len(result_data), "timestamp": datetime.now().isoformat()}
   }

   # Error response
   return {
       "error": "Error message",
       "success": False,
       "error_code": "VALIDATION_ERROR"
   }

Logging
~~~~~~~

Add logging for debugging and monitoring:

.. code-block:: python

   from tooluniverse.base_tool import BaseTool
   from typing import Dict, Any

   class MyTool(BaseTool):
       def __init__(self, tool_config: Dict[str, Any] = None):
           super().__init__(tool_config)
           # BaseTool provides self.logger automatically

       def execute(self, param1: str, **kwargs) -> Dict[str, Any]:
           """Execute with logging."""
           self.logger.info(f"Running tool with param1: {param1}")

           try:
               # Validate inputs
               self.validate_input(param1=param1)

               # Process data
               result = self.process_data(param1)

               self.logger.info(f"Tool completed successfully")
               return {"result": result, "success": True}

           except Exception as e:
               self.logger.error(f"Tool failed: {str(e)}")
               return {"error": str(e), "success": False}

       def process_data(self, param1: str) -> str:
           """Process the input data."""
           self.logger.debug(f"Processing data: {param1}")
           return f"Processed: {param1}"

Testing Your Tools
------------------

Unit Testing
~~~~~~~~~~~~

Create unit tests for your tools:

.. code-block:: python

   # test_my_tool.py
   import pytest
   from tooluniverse.my_tool import MyTool

   def test_my_tool_success():
       tool = MyTool()
       result = tool.execute(message="test")
       assert result["success"] is True
       assert "processed_message" in result

   def test_my_tool_missing_parameter():
       tool = MyTool()
       with pytest.raises(ValueError):
           tool.execute()  # Missing required parameter

   def test_my_tool_validation():
       tool = MyTool()
       with pytest.raises(ValueError):
           tool.execute(message="")  # Empty message should fail validation

Integration Testing
~~~~~~~~~~~~~~~~~~~

Test with ToolUniverse integration:

.. code-block:: python

   def test_tool_integration():
       from tooluniverse import ToolUniverse

       tu = ToolUniverse()
       tu.load_tools()

       result = tu.run_one_function({
           "name": "my_tool",
           "arguments": {"message": "integration test"}
       })

       assert result["success"] is True

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Problem
     - Solution
   * - Tool not found
     - Check file name ends with ``_tool.py`` and is in ``src/tooluniverse/``
   * - Import error
     - Test: ``python -c "from tooluniverse.your_tool import YourTool"``
   * - Config error
     - Validate JSON: ``json.loads(json.dumps(config))``
   * - Runtime error
     - Add try/catch, return ``{"error": str(e), "success": False}``
   * - Wrong parameters
     - Check parameter schema matches your ``execute()`` method
   * - BaseTool inheritance issues
     - Ensure your class inherits from ``BaseTool`` and calls ``super().__init__()``
   * - Validation errors
     - Implement ``validate_input()`` method for proper input validation

Debugging Tools
~~~~~~~~~~~~~~~

Enable debug logging:

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)

   from tooluniverse import ToolUniverse
   tu = ToolUniverse()
   tu.load_tools()

Check tool registration:

.. code-block:: python

   # List all registered tools
   print(tu.available_tools)

   # Check specific tool config
   tool_info = tu.tool_configurations.get("my_tool")
   print(tool_info)

Testing Checklist
~~~~~~~~~~~~~~~~~

Before deploying your tool, verify:

- [ ] File ends with ``_tool.py``
- [ ] Placed in ``src/tooluniverse/``
- [ ] Class inherits from ``BaseTool``
- [ ] Class has ``__init__(self, tool_config: Dict[str, Any] = None)``
- [ ] Class has ``execute(self, **kwargs) -> Dict[str, Any]`` method
- [ ] Class has ``validate_input(self, **kwargs) -> None`` method
- [ ] Config has all required fields (``name``, ``type``, ``description``, ``parameter``)
- [ ] Returns consistent format (``success: True/False``)
- [ ] Error handling implemented
- [ ] Unit tests written
- [ ] Integration test works

Next Steps
----------

Now that you can create local tools:

* 🔗 **Remote Tools**: :doc:`remote_tool_registration` - Learn about remote tool integration
* 📤 **Contributing**: :doc:`contributing_tools` - Submit your tools to ToolUniverse
* 🤖 **AI Integration**: :doc:`../guide/building_ai_scientists/mcp_integration` - Connect your tools with AI assistants
* 🔬 **Scientific Workflows**: :doc:`../guide/scientific_workflows` - Build research pipelines

.. tip::
   **Development tip**: Start simple, test thoroughly, and gradually add complexity. The ToolUniverse community is here to help if you get stuck!
