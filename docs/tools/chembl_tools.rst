Chembl Tools
============

**Configuration File**: ``chembl_tools.json``
**Tool Type**: Local
**Tools Count**: 1

This page contains all tools defined in the ``chembl_tools.json`` configuration file.

Available Tools
---------------

**ChEMBL_search_similar_molecules** (Type: ChEMBLTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Search for molecules similar to a given SMILES, chembl_id, or compound or drug name, using the Ch...

.. dropdown:: ChEMBL_search_similar_molecules tool specification

   **Tool Information:**

   * **Name**: ``ChEMBL_search_similar_molecules``
   * **Type**: ``ChEMBLTool``
   * **Description**: Search for molecules similar to a given SMILES, chembl_id, or compound or drug name, using the ChEMBL Web Services.

   **Parameters:**

   * ``query`` (string) (required)
     SMILES string, chembl_id, or compound or drug name.

   * ``similarity_threshold`` (integer) (optional)
     Similarity threshold (0–100).

   * ``max_results`` (integer) (optional)
     Maximum number of results to return.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "ChEMBL_search_similar_molecules",
          "arguments": {
              "query": "example_value"
          }
      }
      result = tu.run(query)


Navigation
----------

* :doc:`tools_config_index` - Back to Tools Overview
* :doc:`../guide/loading_tools` - Loading Local Tools
