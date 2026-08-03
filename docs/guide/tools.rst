Available Tools
===============

ToolUniverse contains 2,500+ tools spanning scientific databases, APIs,
analysis packages, models, and local compute. The catalog changes frequently,
so this page explains how to query the live registry instead of duplicating a
hand-maintained list.

Browse the Generated Catalog
----------------------------

The generated :doc:`../tools/tools_config_index` groups tool definitions by
their source configuration and links to detailed schemas.

Use the CLI
-----------

The ``tu`` CLI reads the installed registry:

.. code-block:: bash

   tu status
   tu list --mode categories
   tu find "protein structure analysis" --limit 10
   tu info UniProt_get_entry_by_accession

``tu find`` performs deterministic local keyword/BM25 ranking. Use ``tu grep``
when you know an exact name or term. Always inspect a candidate with ``tu info``
before execution because parameter names vary across tools.

Use MCP Compact Mode
--------------------

MCP clients normally see a small discovery surface while every backend tool
remains reachable through ``execute_tool``:

``list_tools``
   Browse and paginate tools or categories.

``grep_tools``
   Search names and descriptions by text or regular expression.

``find_tools``
   Rank tools semantically from a natural-language request.

``get_tool_info``
   Retrieve the exact schema for a selected tool.

``execute_tool``
   Run a tool with schema-validated arguments.

Use Python
----------

.. code-block:: python

   from tooluniverse import ToolUniverse

   tu = ToolUniverse()
   tu.load_tools()

   categories = sorted({
       tool.get("category") for tool in tu.all_tools if tool.get("category")
   })
   print(len(tu.all_tools), "loaded tools")
   print(categories[:10])

   spec = tu.tool_specification("UniProt_get_entry_by_accession")
   print(spec)

For complete discovery examples, see :doc:`finding_tools`,
:doc:`listing_tools`, and :doc:`python_guide`.

Inventory Notes
---------------

``tu status`` reports the tools available in the current installation and
configuration. ``TOOL_MANIFEST.json`` is a dated health snapshot and may cover
fewer tools than the runtime registry; do not use it as a permanent catalog
count.
