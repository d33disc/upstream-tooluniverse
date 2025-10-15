Result Caching
==============

ToolUniverse ships with a two-tier result cache (in-memory + SQLite) so
expensive tool calls can be reused across runs without any extra setup. This
page explains what is cached, how to configure the cache, and how to inspect or
clear cached entries.

Overview
--------

* **In-memory LRU** – Fastest path for repeated calls during a single session.
* **SQLite persistence** – Stores results in ``~/.tooluniverse/cache.sqlite`` by
  default so results survive restarts (path configurable via environment
  variables).
* **Per-tool fingerprints** – Each tool automatically fingerprints its source
  code and parameter schema. When either changes, the cache key changes and old
  entries are ignored.

Quick Start
-----------

Caching is enabled by default. You only need to pass ``use_cache=True`` when
calling a tool to reuse results:

.. code-block:: python

    from tooluniverse import ToolUniverse

    tu = ToolUniverse()
    result = tu.run({
        "name": "UniProt_get_entry_by_accession",
        "arguments": {"accession": "P05067"},
    }, use_cache=True)

    # Second call reuses the cached payload
    cached = tu.run({
        "name": "UniProt_get_entry_by_accession",
        "arguments": {"accession": "P05067"},
    }, use_cache=True)

Configuration
-------------

Use environment variables to tune cache behavior before creating a
``ToolUniverse`` instance:

===============================  ==============================================
Variable                         Description
===============================  ==============================================
``TOOLUNIVERSE_CACHE_ENABLED``   Turn caching on/off (``true`` by default)
``TOOLUNIVERSE_CACHE_PERSIST``   Enable SQLite persistence (``true`` by default)
``TOOLUNIVERSE_CACHE_PATH``      Full path to the SQLite file
``TOOLUNIVERSE_CACHE_DIR``       Directory for the SQLite file (default:
                                 ``~/.tooluniverse``) if ``CACHE_PATH`` unset
``TOOLUNIVERSE_CACHE_MEMORY_SIZE``  Max entries in the in-memory LRU (default 256)
``TOOLUNIVERSE_CACHE_DEFAULT_TTL``  Expiration in seconds (None disables TTL)
``TOOLUNIVERSE_CACHE_SINGLEFLIGHT``  Deduplicate concurrent misses (``true``)
===============================  ==============================================

Example configuration:

.. code-block:: python

    import os
    from tooluniverse import ToolUniverse

    os.environ["TOOLUNIVERSE_CACHE_PATH"] = "/tmp/tooluniverse/cache.sqlite"
    os.environ["TOOLUNIVERSE_CACHE_MEMORY_SIZE"] = "1024"
    os.environ["TOOLUNIVERSE_CACHE_DEFAULT_TTL"] = "3600"  # expire after 1 hour

    tu = ToolUniverse()

Inspecting & Managing Cache
---------------------------

``ToolUniverse`` exposes helpers to understand and control the cache:

.. code-block:: python

    stats = tu.get_cache_stats()
    print(stats)

    # Export persisted entries (returns an iterator of dicts)
    entries = list(tu.dump_cache())

    # Clear all cached data (both layers)
    tu.clear_cache()

Versioning & TTL
----------------

Every tool inherits a default fingerprint (`get_cache_version`) that combines
its source code and parameter schema. You can override the hook in a custom tool
if you want finer control (for example, adding a manual ``STATIC_CACHE_VERSION``
counter). Tools can also override ``get_cache_ttl`` to specify per-result
expiration.

Best Practices
--------------

* Use caching for deterministic or idempotent operations (read-only API calls,
  expensive computations, etc.).
* Set an explicit TTL when results are time-sensitive.
* Call ``tu.clear_cache()`` in long-running services if you need a fresh start.
* For hands-on demos, run ``examples/cache_usage_example.py`` (basic walkthrough)
  or ``examples/cache_stress_test.py`` (randomized load test with summary stats).
