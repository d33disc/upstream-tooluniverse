HTTP API - Remote Access
=========================

The ToolUniverse HTTP API server provides remote access to all ToolUniverse methods via HTTP/REST endpoints.

**Key Feature**: When you add or modify methods in ToolUniverse, the server and client automatically support them with zero manual updates!

Quick Start
-----------

Start Server
~~~~~~~~~~~~

On the machine with ToolUniverse installed:

.. code-block:: bash

    # Install full ToolUniverse package
    pip install tooluniverse

    # Start HTTP API server (8 workers by default)
    tooluniverse-http-api --host 0.0.0.0 --port 8080

Use Client
~~~~~~~~~~

On any machine that needs to call ToolUniverse remotely:

.. code-block:: bash

    # Install with minimal dependencies
    pip install tooluniverse[client]
    # This only installs: requests>=2.32.0, pydantic>=2.11.0

.. code-block:: python

    from tooluniverse import ToolUniverseClient

    client = ToolUniverseClient("http://your-server:8080")

    # Use exactly like local ToolUniverse!
    client.load_tools(
        tool_type=['tool_finder', 'opentarget', 'fda_drug_label',
                  'special_tools', 'monarch', 'fda_drug_adverse_event',
                  'ChEMBL', 'EuropePMC', 'semantic_scholar', 
                  'pubtator', 'EFO']
    )

    # Get tool specification
    spec = client.tool_specification("UniProt_get_entry_by_accession")

    # Execute tool
    result = client.run_one_function(
        function_call_json={
            "name": "UniProt_get_entry_by_accession",
            "arguments": {"accession": "P05067"}
        }
    )

How It Works
------------

Auto-Discovery (Server)
~~~~~~~~~~~~~~~~~~~~~~~

The server uses Python introspection to automatically discover all public methods:

.. code-block:: python

    import inspect

    # Automatically discovers ALL public methods
    for name, method in inspect.getmembers(ToolUniverse, inspect.isfunction):
        if not name.startswith('_'):
            # Extract signature, parameters, docstring
            # Methods are now callable via HTTP!

**Result**: 49+ methods including ``load_tools``, ``prepare_tool_prompts``, ``tool_specification``, ``run_one_function``, etc.

Dynamic Proxying (Client)
~~~~~~~~~~~~~~~~~~~~~~~~~~

The client uses ``__getattr__`` magic to intercept any method call:

.. code-block:: python

    class ToolUniverseClient:
        def __getattr__(self, method_name):
            # Intercepts ANY method call
            def proxy(**kwargs):
                # Forwards to server via HTTP
                return requests.post(url, json={
                    "method": method_name,
                    "kwargs": kwargs
                })
            return proxy

**Workflow Example**:

When you call ``client.load_tools(tool_type=['uniprot'])``:

1. Python looks for ``load_tools`` attribute → NOT FOUND
2. Calls ``__getattr__("load_tools")`` → Returns proxy function
3. Proxy called with ``tool_type=['uniprot']``
4. HTTP POST to server: ``{"method": "load_tools", "kwargs": {...}}``
5. Server calls ``tu.load_tools(tool_type=['uniprot'])``
6. Result returned to client

**Result**: ANY method works automatically, even future ones you haven't written yet!

API Endpoints
-------------

The server exposes the following REST endpoints:

- ``GET /`` - API information
- ``GET /health`` - Health check
- ``GET /api/methods`` - List all available methods with signatures
- ``POST /api/call`` - Call any ToolUniverse method
- ``POST /api/reset`` - Reset ToolUniverse instance
- ``GET /docs`` - Interactive Swagger UI documentation
- ``GET /redoc`` - Alternative ReDoc documentation

Example Usage
-------------

List Available Methods
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from tooluniverse import ToolUniverseClient

    client = ToolUniverseClient("http://localhost:8080")

    # See what methods are available
    methods = client.list_available_methods()
    for m in methods[:10]:
        print(f"{m['name']}: {m['docstring']}")

    # Get help for specific method
    client.help("load_tools")

Load and Use Tools
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = ToolUniverseClient("http://server:8080")

    # Load specific tools
    client.load_tools(tool_type=['uniprot', 'ChEMBL'])

    # Get tool specification
    spec = client.tool_specification("UniProt_get_entry_by_accession")

    # Execute tool
    result = client.run_one_function({
        "name": "UniProt_get_entry_by_accession",
        "arguments": {"accession": "P05067"}
    })

Health Check
~~~~~~~~~~~~

.. code-block:: python

    health = client.health_check()
    print(f"Status: {health['status']}")
    print(f"Loaded tools: {health['loaded_tools_count']}")

Production Deployment
---------------------

Multi-Worker Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

For production use with high concurrency:

.. code-block:: bash

    # 8 workers (default)
    tooluniverse-http-api --host 0.0.0.0 --port 8080

    # Custom number of workers
    tooluniverse-http-api --host 0.0.0.0 --port 8080 --workers 16

Development Mode
~~~~~~~~~~~~~~~~

For development with auto-reload:

.. code-block:: bash

    tooluniverse-http-api --host 127.0.0.1 --port 8080 --reload

Installation
------------

Server Installation
~~~~~~~~~~~~~~~~~~~

Install the full ToolUniverse package on the server:

.. code-block:: bash

    pip install tooluniverse

Client Installation
~~~~~~~~~~~~~~~~~~~

Install with minimal dependencies on client machines:

.. code-block:: bash

    pip install tooluniverse[client]

This only installs:

- ``requests>=2.32.0``
- ``pydantic>=2.11.0``

Testing
-------

Run Unit Tests
~~~~~~~~~~~~~~

.. code-block:: bash

    pytest tests/test_http_api_server.py -v

Run Examples
~~~~~~~~~~~~

.. code-block:: bash

    python examples/http_api_usage_example.py

Test Client Import
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python -c "from tooluniverse import ToolUniverseClient; print('✅ Client imported successfully')"

Implementation Files
--------------------

Core Implementation
~~~~~~~~~~~~~~~~~~~

- ``src/tooluniverse/http_api_server.py`` - FastAPI server with auto-discovery
- ``src/tooluniverse/http_api_server_cli.py`` - CLI entry point
- ``src/tooluniverse/http_client.py`` - Auto-proxying client (minimal dependencies)

Examples & Tests
~~~~~~~~~~~~~~~~

- ``examples/http_api_usage_example.py`` - 7 comprehensive usage examples
- ``tests/test_http_api_server.py`` - Comprehensive test suite

Benefits
--------

1. ✅ **Zero Maintenance** - Add ToolUniverse methods → They automatically work over HTTP
2. ✅ **Minimal Client** - Only needs ``requests`` + ``pydantic`` (no ToolUniverse package)
3. ✅ **Full API Access** - All 49+ ToolUniverse methods available remotely
4. ✅ **Stateful** - Server maintains ToolUniverse instance across requests
5. ✅ **Type Discovery** - Client can query available methods at runtime
6. ✅ **Automatic** - Both server and client use introspection/magic methods
7. ✅ **Flexible Install** - Server needs full package, client uses ``tooluniverse[client]``
8. ✅ **Production Ready** - Multi-worker support with 8 workers by default

Interactive Documentation
--------------------------

Once the server is running, you can access interactive API documentation:

- **Swagger UI**: http://server:8080/docs
- **ReDoc**: http://server:8080/redoc

These provide a web interface to explore and test all API endpoints.
