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

    # Start HTTP API server (single worker with async thread pool)
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

GPU-Optimized Configuration (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For GPU-based inference workloads (default, recommended):

.. code-block:: bash

    # Single worker with async thread pool (default: 20 threads)
    tooluniverse-http-api --host 0.0.0.0 --port 8080

    # High concurrency: increase thread pool size
    tooluniverse-http-api --host 0.0.0.0 --port 8080 --thread-pool-size 50

    # Very high concurrency
    tooluniverse-http-api --host 0.0.0.0 --port 8080 --thread-pool-size 100

**Why single worker for GPU?**

- ✅ Single ToolUniverse instance → Single GPU model in memory (~2GB)
- ✅ Multiple workers → Multiple GPU model copies (~16GB+ wasted memory)
- ✅ High concurrency via async thread pool (20-100 concurrent operations)
- ✅ Efficient GPU memory usage

Multi-Worker Configuration (CPU-Only Workloads)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Only use multiple workers for CPU-only workloads without GPU:

.. code-block:: bash

    # Multiple workers (only for CPU-only operations)
    tooluniverse-http-api --host 0.0.0.0 --port 8080 --workers 8

**Warning**: Multiple workers create separate ToolUniverse instances, each consuming GPU memory if GPU is used.

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

Configuration Options
---------------------

Command-Line Arguments
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    tooluniverse-http-api --help

Available options:

- ``--host`` - Host to bind to (default: 127.0.0.1)
- ``--port`` - Port to bind to (default: 8080)
- ``--workers`` - Number of worker processes (default: 1, recommended for GPU)
- ``--thread-pool-size`` - Async thread pool size per worker (default: 20)
- ``--log-level`` - Log level: debug, info, warning, error, critical
- ``--reload`` - Enable auto-reload for development

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Set thread pool size via environment variable
    export TOOLUNIVERSE_THREAD_POOL_SIZE=50
    tooluniverse-http-api --host 0.0.0.0 --port 8080

Performance Tuning
~~~~~~~~~~~~~~~~~~

For GPU workloads, scale concurrency with thread pool size:

.. code-block:: bash

    # Low traffic (20 concurrent requests)
    tooluniverse-http-api --thread-pool-size 20

    # Medium traffic (50 concurrent requests)
    tooluniverse-http-api --thread-pool-size 50

    # High traffic (100 concurrent requests)
    tooluniverse-http-api --thread-pool-size 100

**Rule of thumb**: ``thread_pool_size = GPU_batch_size × 2 to 5``

Benefits
--------

1. ✅ **Zero Maintenance** - Add ToolUniverse methods → They automatically work over HTTP
2. ✅ **Minimal Client** - Only needs ``requests`` + ``pydantic`` (no ToolUniverse package)
3. ✅ **Full API Access** - All 49+ ToolUniverse methods available remotely
4. ✅ **Stateful** - Server maintains ToolUniverse instance across requests
5. ✅ **Type Discovery** - Client can query available methods at runtime
6. ✅ **Automatic** - Both server and client use introspection/magic methods
7. ✅ **Flexible Install** - Server needs full package, client uses ``tooluniverse[client]``
8. ✅ **GPU-Optimized** - Single worker with async thread pool for efficient GPU usage
9. ✅ **High Concurrency** - 20-100+ concurrent operations via async thread pool

Docker Deployment
-----------------

With GPU Support
~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

    FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

    WORKDIR /app
    COPY . .
    RUN pip install tooluniverse uvicorn fastapi

    EXPOSE 8080

    # Single worker with high thread pool for GPU
    CMD ["tooluniverse-http-api", \
         "--host", "0.0.0.0", \
         "--port", "8080", \
         "--workers", "1", \
         "--thread-pool-size", "50"]

Run with GPU:

.. code-block:: bash

    docker run --gpus all -p 8080:8080 tooluniverse-api

Without GPU (CPU-Only)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

    FROM python:3.12-slim

    WORKDIR /app
    COPY . .
    RUN pip install tooluniverse uvicorn fastapi

    EXPOSE 8080

    # Multiple workers for CPU workloads
    CMD ["tooluniverse-http-api", \
         "--host", "0.0.0.0", \
         "--port", "8080", \
         "--workers", "4"]

Monitoring
----------

GPU Memory Usage
~~~~~~~~~~~~~~~~

Check GPU memory usage:

.. code-block:: bash

    # Monitor GPU in real-time
    watch -n 1 nvidia-smi

Expected output with single worker:

.. code-block:: text

    +-----------------------------------------------------------------------------+
    | Processes:                                                                  |
    |  GPU   PID   Type   Process name                             GPU Memory    |
    |============================================================================|
    |    0   12345  C     python3 tooluniverse-http-api              2048MiB    |
    +-----------------------------------------------------------------------------+

Only ONE process should be using GPU memory.

Server Health
~~~~~~~~~~~~~

.. code-block:: bash

    # Check server health
    curl http://localhost:8080/health

    # Monitor logs
    tooluniverse-http-api --log-level info

Interactive Documentation
--------------------------

Once the server is running, you can access interactive API documentation:

- **Swagger UI**: http://server:8080/docs
- **ReDoc**: http://server:8080/redoc

These provide a web interface to explore and test all API endpoints.
