Alphafold Tools
===============

**Configuration File**: ``alphafold_tools.json``
**Tool Type**: Local
**Tools Count**: 3

This page contains all tools defined in the ``alphafold_tools.json`` configuration file.

Available Tools
---------------

**alphafold_get_annotations** (Type: AlphaFoldRESTTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve AlphaFold variant annotations (e.g., missense mutations) for a given UniProt accession (...

.. dropdown:: alphafold_get_annotations tool specification

   **Tool Information:**

   * **Name**: ``alphafold_get_annotations``
   * **Type**: ``AlphaFoldRESTTool``
   * **Description**: Retrieve AlphaFold variant annotations (e.g., missense mutations) for a given UniProt accession (e.g., 'P69905'). Input must be a UniProt accession, entry name, or CRC64 checksum, along with an annotation type (currently only 'MUTAGEN'). Use this tool to explore predicted pathogenicity or functional effects of substitutions. If you only have a protein/gene name, resolve it with `uniprot_search`. For experimentally curated variants, use `UniProt_get_disease_variants_by_accession`. To view the full 3D structure, call `alphafold_get_prediction`; for overall model metadata, use `alphafold_get_summary`.

   **Parameters:**

   * ``qualifier`` (string) (required)
     Protein identifier: UniProt accession, entry name, or CRC64 checksum.

   * ``type`` (string) (required)
     Annotation type (currently only 'MUTAGEN' is supported).

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "alphafold_get_annotations",
          "arguments": {
              "qualifier": "example_value",
              "type": "example_value"
          }
      }
      result = tu.run(query)


**alphafold_get_prediction** (Type: AlphaFoldRESTTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve full AlphaFold 3D structure predictions for a given protein. Input must be a UniProt acc...

.. dropdown:: alphafold_get_prediction tool specification

   **Tool Information:**

   * **Name**: ``alphafold_get_prediction``
   * **Type**: ``AlphaFoldRESTTool``
   * **Description**: Retrieve full AlphaFold 3D structure predictions for a given protein. Input must be a UniProt accession (e.g., 'P69905'), UniProt entry name (e.g., 'HBA_HUMAN'), or CRC64 checksum. Returns residue-level metadata including sequence, per-residue confidence scores (pLDDT), and structure download links (PDB, CIF, PAE). If you do not know the accession, first call `uniprot_search` to resolve it from a protein/gene name, or `UniProt_get_entry_by_accession` if you already have the accession and want UniProt details. For a quick overview, use `alphafold_get_summary`. For mutation/variant impact, see `alphafold_get_annotations.

   **Parameters:**

   * ``qualifier`` (string) (required)
     Protein identifier: UniProt accession (e.g., 'P69905'), entry name (e.g., 'HBA_HUMAN'), or CRC64 checksum.

   * ``sequence_checksum`` (string) (required)
     Optional CRC64 checksum of the UniProt sequence.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "alphafold_get_prediction",
          "arguments": {
              "qualifier": "example_value",
              "sequence_checksum": "example_value"
          }
      }
      result = tu.run(query)


**alphafold_get_summary** (Type: AlphaFoldRESTTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve summary details of AlphaFold 3D models for a given protein. Input must be a UniProt acce...

.. dropdown:: alphafold_get_summary tool specification

   **Tool Information:**

   * **Name**: ``alphafold_get_summary``
   * **Type**: ``AlphaFoldRESTTool``
   * **Description**: Retrieve summary details of AlphaFold 3D models for a given protein. Input must be a UniProt accession, entry name, or CRC64 checksum. Returns lightweight information such as sequence length, coverage, confidence scores, experimental method, resolution, oligomeric state, and structural entities. If you only know the protein/gene name, first use `uniprot_search` to find the accession. For full residue-level 3D predictions with downloadable coordinates, call `alphafold_get_prediction`. For curated variants, see `UniProt_get_disease_variants_by_accession`; for predicted mutation effects, use `alphafold_get_annotations`.

   **Parameters:**

   * ``qualifier`` (string) (required)
     Protein identifier: UniProt accession, entry name, or CRC64 checksum.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "alphafold_get_summary",
          "arguments": {
              "qualifier": "example_value"
          }
      }
      result = tu.run(query)


Navigation
----------

* :doc:`tools_config_index` - Back to Tools Overview
* :doc:`../guide/loading_tools` - Loading Local Tools
