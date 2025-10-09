Unified Guideline Tools
=======================

**Configuration File**: ``unified_guideline_tools.json``
**Tool Type**: Local
**Tools Count**: 4

This page contains all tools defined in the ``unified_guideline_tools.json`` configuration file.

Available Tools
---------------

**EuropePMC_Guidelines_Search** (Type: EuropePMCGuidelinesTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Search Europe PMC for clinical guidelines and evidence-based recommendations. Europe PMC provides...

.. dropdown:: EuropePMC_Guidelines_Search tool specification

   **Tool Information:**

   * **Name**: ``EuropePMC_Guidelines_Search``
   * **Type**: ``EuropePMCGuidelinesTool``
   * **Description**: Search Europe PMC for clinical guidelines and evidence-based recommendations. Europe PMC provides free access to a comprehensive archive of life sciences literature, including clinical practice guidelines from international sources.

   **Parameters:**

   * ``query`` (string) (required)
     Medical condition, treatment, or clinical topic to search for (e.g., 'diabetes', 'cardiovascular disease', 'mental health')

   * ``limit`` (integer) (optional)
     Maximum number of guidelines to return (default: 10)

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "EuropePMC_Guidelines_Search",
          "arguments": {
              "query": "example_value"
          }
      }
      result = tu.run(query)


**NICE_Clinical_Guidelines_Search** (Type: NICEWebScrapingTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Search NICE (National Institute for Health and Care Excellence) clinical guidelines and evidence-...

.. dropdown:: NICE_Clinical_Guidelines_Search tool specification

   **Tool Information:**

   * **Name**: ``NICE_Clinical_Guidelines_Search``
   * **Type**: ``NICEWebScrapingTool``
   * **Description**: Search NICE (National Institute for Health and Care Excellence) clinical guidelines and evidence-based recommendations. Provides access to official NICE guidelines covering diagnosis, treatment, and care pathways for various medical conditions.

   **Parameters:**

   * ``query`` (string) (required)
     Medical condition, treatment, or clinical topic to search for in NICE guidelines (e.g., 'diabetes', 'hypertension', 'cancer screening')

   * ``limit`` (integer) (optional)
     Maximum number of clinical guidelines to return (default: 10)

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "NICE_Clinical_Guidelines_Search",
          "arguments": {
              "query": "example_value"
          }
      }
      result = tu.run(query)


**PubMed_Guidelines_Search** (Type: PubMedGuidelinesTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Search PubMed for peer-reviewed clinical practice guidelines using NCBI E-utilities. Filters resu...

.. dropdown:: PubMed_Guidelines_Search tool specification

   **Tool Information:**

   * **Name**: ``PubMed_Guidelines_Search``
   * **Type**: ``PubMedGuidelinesTool``
   * **Description**: Search PubMed for peer-reviewed clinical practice guidelines using NCBI E-utilities. Filters results specifically for guideline and practice guideline publication types. Provides access to high-quality, evidence-based clinical guidelines from medical journals worldwide.

   **Parameters:**

   * ``query`` (string) (required)
     Medical condition, treatment, or clinical topic to search for (e.g., 'diabetes', 'hypertension management', 'cancer treatment')

   * ``limit`` (integer) (optional)
     Maximum number of guidelines to return (default: 10)

   * ``api_key`` (string) (optional)
     Optional NCBI API key for higher rate limits. Get your free key at https://www.ncbi.nlm.nih.gov/account/

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "PubMed_Guidelines_Search",
          "arguments": {
              "query": "example_value"
          }
      }
      result = tu.run(query)


**TRIP_Database_Guidelines_Search** (Type: TRIPDatabaseTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Search TRIP Database (Turning Research into Practice) for evidence-based clinical guidelines. TRI...

.. dropdown:: TRIP_Database_Guidelines_Search tool specification

   **Tool Information:**

   * **Name**: ``TRIP_Database_Guidelines_Search``
   * **Type**: ``TRIPDatabaseTool``
   * **Description**: Search TRIP Database (Turning Research into Practice) for evidence-based clinical guidelines. TRIP is a specialized clinical search engine that focuses on high-quality evidence-based content, particularly clinical guidelines from reputable sources worldwide.

   **Parameters:**

   * ``query`` (string) (required)
     Medical condition, treatment, or clinical question (e.g., 'diabetes management', 'stroke prevention', 'antibiotic therapy')

   * ``limit`` (integer) (optional)
     Maximum number of guidelines to return (default: 10)

   * ``search_type`` (string) (optional)
     Type of content to search for (default: 'guideline'). Options include 'guideline', 'systematic-review', 'evidence-based-synopses'

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "TRIP_Database_Guidelines_Search",
          "arguments": {
              "query": "example_value"
          }
      }
      result = tu.run(query)


Navigation
----------

* :doc:`tools_config_index` - Back to Tools Overview
* :doc:`../guide/loading_tools` - Loading Local Tools
