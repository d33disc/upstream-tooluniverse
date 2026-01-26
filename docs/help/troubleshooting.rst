Troubleshooting Tutorial
=====================

This Tutorial helps you diagnose and resolve common issues with ToolUniverse.

Quick Diagnostic
----------------

Run this diagnostic script to check your ToolUniverse installation:

.. code-block:: python

   from tooluniverse import ToolUniverse

   # Run basic system check
   try:
       tu = ToolUniverse()
       tu.load_tools()
       print(f"✅ ToolUniverse working correctly! {len(tu.all_tools)} tools loaded.")
   except Exception as e:
       print(f"❌ Issue detected: {e}")

.. tabs::

   .. tab:: Installation Issues

      Most common installation problems and solutions.

   .. tab:: Runtime Errors

      Errors that occur during tool execution.

   .. tab:: Performance Issues

      Slow queries and optimization tips.

   .. tab:: API Connectivity

      Network and API-related problems.

Installation Issues
-------------------

ImportError: No module named 'tooluniverse'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Python can't find the ToolUniverse module.

**Diagnosis:**

.. code-block:: bash

   python -c "import tooluniverse; print(tooluniverse.__version__)"

**Solutions:**

.. tabs::

   .. tab:: Standard Installation

      .. code-block:: bash

         pip install tooluniverse

   .. tab:: Development Installation

      .. code-block:: bash

         git clone https://github.com/zitniklab/tooluniverse
         cd tooluniverse
         pip install -e .

   .. tab:: Virtual Environment

      .. code-block:: bash

         python -m venv tooluniverse_env
         source tooluniverse_env/bin/activate  # Linux/Mac
         # tooluniverse_env\Scripts\activate  # Windows
         pip install tooluniverse

Dependency conflicts
~~~~~~~~~~~~~~~~~~~~

**Symptom:** Conflicting package versions during installation.

**Check dependencies:**

.. code-block:: bash

   pip check

**Solutions:**

1. **Create clean environment:**

   .. code-block:: bash

      conda create -n tooluniverse python=3.10
      conda activate tooluniverse
      pip install tooluniverse

2. **Update conflicting packages:**

   .. code-block:: bash

      pip install --upgrade requests urllib3 certifi

3. **Install specific versions:**

   .. code-block:: bash

      pip install 'requests>=2.25.0,<3.0.0'

Runtime Errors
--------------

Tool not found errors
~~~~~~~~~~~~~~~~~~~~~

**Symptom:** ``ToolNotFoundError: Tool 'XYZ' not found``

**Diagnosis:**

.. code-block:: python

   from tooluniverse import ToolUniverse

   tu = ToolUniverse()
   tu.load_tools()

   # List available tools
   print("Available tools:")
   for tool_name in tu.list_tools():
       print(f"  - {tool_name}")

**Solutions:**

1. **Check tool name spelling:**

   .. code-block:: python

      # Correct tool names
      correct_names = [
          "OpenTargets_get_associated_targets_by_disease_efoId",
          "PubChem_get_compound_info",
          "UniProt_get_function_by_accession"
      ]

2. **Verify tool is loaded:**

   .. code-block:: python

      if "OpenTargets_tool" not in tu.list_tools():
          print("OpenTargets tool not loaded")
          # Check for missing dependencies

3. **Manual tool loading:**

   .. code-block:: python

      from tooluniverse.opentargets_tool import OpenTargetsTool
      tool = OpenTargetsTool()
      tu.register_tool(tool)

API Authentication errors
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** ``401 Unauthorized`` or ``403 Forbidden`` errors.

**Diagnosis:**

.. code-block:: python

   import os

   # Check if API keys are set
   api_keys = {
       'OPENTARGETS_API_KEY': os.getenv('OPENTARGETS_API_KEY'),
       'NCBI_API_KEY': os.getenv('NCBI_API_KEY'),
       'CHEMBL_API_KEY': os.getenv('CHEMBL_API_KEY')
   }

   for key, value in api_keys.items():
       status = "✓ Set" if value else "✗ Missing"
       print(f"{key}: {status}")

**Solutions:**

1. **Set API keys:**

   .. code-block:: bash

      export OPENTARGETS_API_KEY="your_key_here"
      export NCBI_API_KEY="your_ncbi_key"

2. **In Python:**

   .. code-block:: python

      import os
      os.environ['OPENTARGETS_API_KEY'] = 'your_key_here'

3. **Use .env file:**

   .. code-block:: bash

      # Create .env file
      echo "OPENTARGETS_API_KEY=your_key" >> .env
      echo "NCBI_API_KEY=your_ncbi_key" >> .env

   .. code-block:: python

      from dotenv import load_dotenv
      load_dotenv()

Rate limiting errors
~~~~~~~~~~~~~~~~~~~~

**Symptom:** ``429 Too Many Requests`` or ``RateLimitExceeded``

**Diagnosis:**

.. code-block:: python

   # Check rate limit status
   from tooluniverse.utils import check_rate_limits

   status = check_rate_limits()
   print(f"Rate limit status: {status}")

**Solutions:**

1. **Add delays between requests:**

   .. code-block:: python

      import time

      for query in queries:
           result = tu.run(query)
           time.sleep(1)  # Wait 1 second between requests

2. **Use batch processing:**

   .. code-block:: python

      # Process in smaller batches
      batch_size = 5
      for i in range(0, len(queries), batch_size):
           batch = queries[i:i+batch_size]
           results = tu.run_batch(batch)
           time.sleep(2)  # Pause between batches

3. **Get API keys for higher limits:**

   Most services offer higher rate limits with API keys.

Network & Connectivity
-----------------------

Connection timeouts
~~~~~~~~~~~~~~~~~~~

**Symptom:** ``ConnectionTimeout`` or ``ReadTimeout`` errors.

**Diagnosis:**

.. code-block:: python

   import requests

   # Test basic connectivity
   try:
       response = requests.get('https://httpbin.org/delay/1', timeout=5)
       print(f"Network OK: {response.status_code}")
   except requests.exceptions.Timeout:
       print("Network timeout - check connection")

**Solutions:**

1. **Increase timeout:**

   .. code-block:: python

      tu = ToolUniverse(timeout=30)  # 30 second timeout

2. **Check network connection:**

   .. code-block:: bash

      ping google.com
      curl -I https://platform-api.opentargets.org

3. **Configure proxy (if needed):**

   .. code-block:: python

      import os
      os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
      os.environ['HTTPS_PROXY'] = 'http://proxy.company.com:8080'

SSL Certificate errors
~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** ``SSLError`` or certificate verification failures.

**Solutions:**

1. **Update certificates:**

   .. code-block:: bash

      pip install --upgrade certifi requests urllib3

2. **Temporary bypass (not recommended for production):**

   .. code-block:: python

      import ssl
      ssl._create_default_https_context = ssl._create_unverified_context

3. **Corporate firewall:**

   Contact your IT department for proper certificate configuration.

Performance Issues
------------------

Slow query performance
~~~~~~~~~~~~~~~~~~~~~~

**Diagnosis:**

.. code-block:: python

   import time
   from tooluniverse import ToolUniverse

   tu = ToolUniverse()

   # Time a query
   start_time = time.time()
   result = tu.run({"name": "tool_name", "arguments": {}})
   elapsed = time.time() - start_time

   print(f"Query took {elapsed:.2f} seconds")

**Optimization strategies:**

1. **Enable caching:**

   .. code-block:: python

      import os
      os.environ["TOOLUNIVERSE_CACHE_DEFAULT_TTL"] = "3600"  # 1 hour
      tu = ToolUniverse()
      result = tu.run(..., use_cache=True)

2. **Use async operations:**

   .. code-block:: python

      import asyncio

      async def run_queries():
           tasks = [tu.run_async(query) for query in queries]
           results = await asyncio.gather(*tasks)
           return results

3. **Batch similar queries:**

   .. code-block:: python

      # Instead of individual queries by gene symbol, prefer accession-based queries
      accession_info = []
      for accession in accessions:
           info = tu.run({
               "name": "UniProt_get_function_by_accession",
               "arguments": {"accession": accession}
           })
           accession_info.append(info)

      # Use batch processing
      queries = [
           {"name": "UniProt_get_function_by_accession", "arguments": {"accession": accession}}
           for accession in accessions
      ]
      results = tu.run_batch(queries)

Memory usage issues
~~~~~~~~~~~~~~~~~~~

**Symptom:** High memory consumption or ``MemoryError``.

**Diagnosis:**

.. code-block:: python

   import psutil
   import os

   process = psutil.Process(os.getpid())
   memory_mb = process.memory_info().rss / 1024 / 1024
   print(f"Memory usage: {memory_mb:.1f} MB")

**Solutions:**

1. **Process data in chunks:**

   .. code-block:: python

      def process_large_dataset(data, chunk_size=100):
           for i in range(0, len(data), chunk_size):
               chunk = data[i:i+chunk_size]
               yield tu.run_batch(chunk)

2. **Clear cache periodically:**

   .. code-block:: python

      tu.clear_cache()

3. **Use generators for large results:**

   .. code-block:: python

      def yield_results(queries):
           for query in queries:
               yield tu.run(query)

MCP Server Issues
-----------------

MCP server won't start
~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Server fails to start or crashes immediately.

**Diagnosis:**

.. code-block:: bash

   # Test server directly
   python -m tooluniverse.smcp_server --debug

**Solutions:**

1. **Check port availability:**

   .. code-block:: bash

      # Check if port is in use
      lsof -i :3000  # Linux/Mac
      netstat -an | findstr :3000  # Windows

2. **Use different port:**

   .. code-block:: bash

      python -m tooluniverse.smcp_server --port 3001

3. **Check permissions:**

   .. code-block:: bash

      # Ensure user can bind to port
      sudo python -m tooluniverse.smcp_server  # If needed

Claude/AI assistant not finding tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Diagnosis:**

1. **Verify MCP server is running:**

   .. code-block:: bash

      curl http://localhost:3000/health

2. **Check Claude configuration:**

   Ensure MCP server is properly configured in Claude Desktop settings.

**Solutions:**

1. **Restart both server and Claude**
2. **Check Claude logs** for connection errors
3. **Verify tool registration:**

   .. code-block:: python

      # In MCP server
      tools = tu.list_tools()
      print(f"Registered {len(tools)} tools")

Advanced Debugging
------------------

Enable debug logging
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging

   # Enable debug logging
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger('tooluniverse')
   logger.setLevel(logging.DEBUG)

   # Now run your code
   tu = ToolUniverse()

Capture detailed error information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import traceback

   try:
       result = tu.run(query)
   except Exception as e:
       print(f"Error: {e}")
       print(f"Type: {type(e).__name__}")
       print("Traceback:")
       traceback.print_exc()

Profile performance bottlenecks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import cProfile
   import pstats

   # Profile your code
   profiler = cProfile.Profile()
   profiler.enable()

   # Your ToolUniverse code here
   tu = ToolUniverse()
   result = tu.run(query)

   profiler.disable()

   # Analyze results
   stats = pstats.Stats(profiler)
   stats.sort_stats('cumulative')
   stats.print_stats(10)

Getting Help
------------

If none of these solutions work:

1. **Check the FAQ**: :doc:`faq`
2. **Search GitHub issues**: `Issues <https://github.com/zitniklab/tooluniverse/issues>`_
3. **Create a bug report** with:

   - ToolUniverse version: ``tooluniverse.__version__``
   - Python version: ``python --version``
   - Operating system
   - Full error message and traceback
   - Minimal code example that reproduces the issue

4. **Join our community**: Discord server link

.. note::
=========
   When reporting issues, please run the diagnostic script first:

   .. code-block:: python

      from tooluniverse.diagnostics import run_diagnostic
      print(run_diagnostic())

   Include this output in your bug report.
