Geo Tools
=========

**Configuration File**: ``geo_tools.json``
**Tool Type**: Local
**Tools Count**: 1

This page contains all tools defined in the ``geo_tools.json`` configuration file.

Available Tools
---------------

**GEO_search_expression_data** (Type: GEORESTTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Search gene expression data from the GEO database. GEO is a public repository that archives and f...

.. dropdown:: GEO_search_expression_data tool specification

   **Tool Information:**

   * **Name**: ``GEO_search_expression_data``
   * **Type**: ``GEORESTTool``
   * **Description**: Search gene expression data from the GEO database. GEO is a public repository that archives and freely distributes microarray, next-generation sequencing, and other forms of high-throughput functional genomics data.

   **Parameters:**

   * ``query`` (string) (required)
     Search query (e.g., 'cancer', 'diabetes', 'microarray')

   * ``organism`` (string) (optional)
     Organism name (e.g., 'Homo sapiens', 'Mus musculus')

   * ``study_type`` (string) (optional)
     Type of study (e.g., 'expression', 'methylation', 'genome')

   * ``platform`` (string) (optional)
     Platform used (e.g., 'GPL96', 'GPL570')

   * ``date_range`` (string) (optional)
     Date range in format 'YYYY:YYYY' (e.g., '2020:2023')

   * ``limit`` (integer) (optional)
     Maximum number of results to return (default: 50)

   * ``sort`` (string) (optional)
     Sort order ('relevance', 'date', 'title')

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "GEO_search_expression_data",
          "arguments": {
              "query": "example_value"
          }
      }
      result = tu.run(query)


Navigation
----------

* :doc:`tools_config_index` - Back to Tools Overview
* :doc:`../guide/loading_tools` - Loading Local Tools
