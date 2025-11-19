External Service Integration
============================

Learn how to integrate external APIs and services with ToolUniverse using configuration files.

What are External Services?
---------------------------

External services are APIs, web services, or tools that run outside of ToolUniverse and are accessed via HTTP requests. They provide:

- **API Integration**: Connect with existing web services
- **No Code Required**: Configure through JSON files
- **Easy Management**: Add/remove services without code changes
- **Scalability**: Offload processing to external systems

Quick Start
-----------

**How to add an external service:**

1. **Find the API** you want to integrate
2. **Create a configuration file** with the API details
3. **Add to ToolUniverse** configuration
4. **Use the service** via ToolUniverse's standard interface

Configuration Example
---------------------

Create a JSON configuration file for your external service:

.. code-block:: json

   {
     "name": "weather_api",
     "type": "external_service",
     "description": "Get weather information for any location",
     "base_url": "https://api.weather.com/v1",
     "endpoints": {
       "current_weather": {
         "path": "/current",
         "method": "GET",
         "parameters": {
           "location": {"type": "string", "required": true},
           "units": {"type": "string", "default": "metric"}
         }
       }
     },
     "authentication": {
       "type": "api_key",
       "header": "X-API-Key",
       "value": "your_api_key_here"
     }
   }

Using External Services
-----------------------

Once configured, use external services like any other ToolUniverse tool:

.. code-block:: python

   from tooluniverse import ToolUniverse

   tu = ToolUniverse()
   tu.load_tools()  # Loads all configured tools including external services

   # Use external service
   result = tu.run({
       "name": "weather_api",
       "endpoint": "current_weather",
       "arguments": {
           "location": "New York",
           "units": "metric"
       }
   })
   print(result)

Common Service Types
--------------------

**REST APIs**
- Most common type
- Use standard HTTP methods (GET, POST, PUT, DELETE)
- Support JSON request/response

**GraphQL APIs**
- Query-based APIs
- Single endpoint with flexible queries
- Support for complex data fetching

**Webhook Services**
- Event-driven services
- Real-time notifications
- Asynchronous processing

Configuration Reference
-----------------------

**Required Fields:**
- ``name``: Unique identifier for the service
- ``type``: Must be "external_service"
- ``description``: Human-readable description
- ``base_url``: Base URL of the API
- ``endpoints``: Available API endpoints

**Optional Fields:**
- ``authentication``: API key, OAuth, or other auth methods
- ``timeout``: Request timeout in seconds
- ``retry_attempts``: Number of retry attempts
- ``rate_limiting``: Rate limiting configuration

Troubleshooting
---------------

**Common Issues:**

**Connection errors**
- Check the base_url is correct
- Verify network connectivity
- Check firewall settings

**Authentication errors**
- Verify API key is correct
- Check authentication method
- Ensure proper headers are set

**Parameter errors**
- Check parameter names match API documentation
- Verify required parameters are provided
- Check parameter types are correct

Next Steps
----------

* 🏠 **Local Tools**: :doc:`../local_tools/tutorial` - Learn about local tool development
* 🚀 **Contributing**: :doc:`../contributing/remote_tools` - Submit external services to ToolUniverse
* 🔍 **Architecture**: :doc:`../reference/architecture` - Understand ToolUniverse internals

.. tip::
   **Integration tip**: Start with simple APIs and gradually add complexity. Always test your configuration thoroughly!
