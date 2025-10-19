Fda Drug Adverse Event Tools
============================

**Configuration File**: ``fda_drug_adverse_event_tools.json``
**Tool Type**: Local
**Tools Count**: 15

This page contains all tools defined in the ``fda_drug_adverse_event_tools.json`` configuration file.

Available Tools
---------------

**FAERS_count_additive_administration_routes** (Type: FDACountAdditiveReactionsTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additive multi-drug data: Enumerate and count administration routes for adverse events across spe...

.. dropdown:: FAERS_count_additive_administration_routes tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_additive_administration_routes``
   * **Type**: ``FDACountAdditiveReactionsTool``
   * **Description**: Additive multi-drug data: Enumerate and count administration routes for adverse events across specified medicinal products, using standardized route codes. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproducts`` (array) (required)
     Array of medicinal product names.

   * ``serious`` (string) (required)
     Filter by seriousness.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_additive_administration_routes",
          "arguments": {
              "medicinalproducts": ["item1", "item2"],
              "serious": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_additive_adverse_reactions** (Type: FDACountAdditiveReactionsTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additive multi-drug data: Aggregate adverse reaction counts across specified medicinal products, ...

.. dropdown:: FAERS_count_additive_adverse_reactions tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_additive_adverse_reactions``
   * **Type**: ``FDACountAdditiveReactionsTool``
   * **Description**: Additive multi-drug data: Aggregate adverse reaction counts across specified medicinal products, stratified by demographics, seriousness, and outcomes. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproducts`` (array) (required)
     Array of medicinal product names.

   * ``patientsex`` (string) (required)
     Filter by patient sex.

   * ``patientagegroup`` (string) (required)
     Filter by patient age group.

   * ``occurcountry`` (string) (required)
     Filter by ISO2 country code of occurrence.

   * ``serious`` (string) (required)
     Filter by seriousness classification.

   * ``seriousnessdeath`` (string) (required)
     Filter for fatal outcomes.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_additive_adverse_reactions",
          "arguments": {
              "medicinalproducts": ["item1", "item2"],
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "occurcountry": "example_value",
              "serious": "example_value",
              "seriousnessdeath": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_additive_event_reports_by_country** (Type: FDACountAdditiveReactionsTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additive multi-drug data: Aggregate report counts by country of occurrence across specified medic...

.. dropdown:: FAERS_count_additive_event_reports_by_country tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_additive_event_reports_by_country``
   * **Type**: ``FDACountAdditiveReactionsTool``
   * **Description**: Additive multi-drug data: Aggregate report counts by country of occurrence across specified medicinal products. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproducts`` (array) (required)
     Array of medicinal product names.

   * ``patientsex`` (string) (required)
     Filter by sex.

   * ``patientagegroup`` (string) (required)
     Filter by age group.

   * ``serious`` (string) (required)
     Filter by seriousness.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_additive_event_reports_by_country",
          "arguments": {
              "medicinalproducts": ["item1", "item2"],
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "serious": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_additive_reaction_outcomes** (Type: FDACountAdditiveReactionsTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additive multi-drug data: Determine reaction outcome counts (e.g., recovered, resolving, fatal) a...

.. dropdown:: FAERS_count_additive_reaction_outcomes tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_additive_reaction_outcomes``
   * **Type**: ``FDACountAdditiveReactionsTool``
   * **Description**: Additive multi-drug data: Determine reaction outcome counts (e.g., recovered, resolving, fatal) across medicinal products using standardized outcome mappings. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproducts`` (array) (required)
     Array of medicinal product names.

   * ``patientsex`` (string) (required)
     No description

   * ``patientagegroup`` (string) (required)
     No description

   * ``occurcountry`` (string) (required)
     No description

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_additive_reaction_outcomes",
          "arguments": {
              "medicinalproducts": ["item1", "item2"],
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "occurcountry": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_additive_reports_by_reporter_country** (Type: FDACountAdditiveReactionsTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additive multi-drug data: Aggregate adverse event reports by primary reporter country across medi...

.. dropdown:: FAERS_count_additive_reports_by_reporter_country tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_additive_reports_by_reporter_country``
   * **Type**: ``FDACountAdditiveReactionsTool``
   * **Description**: Additive multi-drug data: Aggregate adverse event reports by primary reporter country across medicinal products. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproducts`` (array) (required)
     Array of medicinal product names.

   * ``patientsex`` (string) (required)
     Filter by sex.

   * ``patientagegroup`` (string) (required)
     Filter by age group.

   * ``serious`` (string) (required)
     Filter by seriousness.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_additive_reports_by_reporter_country",
          "arguments": {
              "medicinalproducts": ["item1", "item2"],
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "serious": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_additive_seriousness_classification** (Type: FDACountAdditiveReactionsTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additive multi-drug data: Quantify serious vs non-serious classifications across medicinal produc...

.. dropdown:: FAERS_count_additive_seriousness_classification tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_additive_seriousness_classification``
   * **Type**: ``FDACountAdditiveReactionsTool``
   * **Description**: Additive multi-drug data: Quantify serious vs non-serious classifications across medicinal products, annotated per regulatory definitions. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproducts`` (array) (required)
     Array of medicinal product names.

   * ``patientsex`` (string) (required)
     Filter by sex.

   * ``patientagegroup`` (string) (required)
     Filter by age group.

   * ``occurcountry`` (string) (required)
     ISO2 country code filter.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_additive_seriousness_classification",
          "arguments": {
              "medicinalproducts": ["item1", "item2"],
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "occurcountry": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_country_by_drug_event** (Type: FDADrugAdverseEventTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Count the number of adverse event reports per country of occurrence, filtered by drug, patient de...

.. dropdown:: FAERS_count_country_by_drug_event tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_country_by_drug_event``
   * **Type**: ``FDADrugAdverseEventTool``
   * **Description**: Count the number of adverse event reports per country of occurrence, filtered by drug, patient demographics, and seriousness. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproduct`` (string) (required)
     Drug name.

   * ``patientsex`` (string) (required)
     Patient sex, leave it blank if you don't want to apply a filter.

   * ``patientagegroup`` (string) (required)
     Patient age group.

   * ``serious`` (string) (required)
     Whether the event was serious.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_country_by_drug_event",
          "arguments": {
              "medicinalproduct": "example_value",
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "serious": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_death_related_by_drug** (Type: FDADrugAdverseEventTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Count adverse events associated with patient death for a given drug. Data source: FDA Adverse Eve...

.. dropdown:: FAERS_count_death_related_by_drug tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_death_related_by_drug``
   * **Type**: ``FDADrugAdverseEventTool``
   * **Description**: Count adverse events associated with patient death for a given drug. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproduct`` (string) (required)
     Drug name.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_death_related_by_drug",
          "arguments": {
              "medicinalproduct": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_drug_routes_by_event** (Type: FDADrugAdverseEventTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Count the most common routes of administration for drugs involved in adverse event reports. Data ...

.. dropdown:: FAERS_count_drug_routes_by_event tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_drug_routes_by_event``
   * **Type**: ``FDADrugAdverseEventTool``
   * **Description**: Count the most common routes of administration for drugs involved in adverse event reports. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproduct`` (string) (required)
     Drug name.

   * ``serious`` (string) (required)
     Seriousness of event.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_drug_routes_by_event",
          "arguments": {
              "medicinalproduct": "example_value",
              "serious": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_drugs_by_drug_event** (Type: FDADrugAdverseEventTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Count the number of different drugs involved in FDA adverse event reports, filtered by patient de...

.. dropdown:: FAERS_count_drugs_by_drug_event tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_drugs_by_drug_event``
   * **Type**: ``FDADrugAdverseEventTool``
   * **Description**: Count the number of different drugs involved in FDA adverse event reports, filtered by patient details, country, and seriousness. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``patientsex`` (string) (required)
     Patient sex, leave it blank if you don't want to apply a filter.

   * ``patientagegroup`` (string) (required)
     Patient age group.

   * ``occurcountry`` (string) (required)
     Country where event occurred.

   * ``serious`` (string) (required)
     Whether the event was serious.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_drugs_by_drug_event",
          "arguments": {
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "occurcountry": "example_value",
              "serious": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_outcomes_by_drug_event** (Type: FDADrugAdverseEventTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Count the outcome of adverse reactions (recovered, recovering, fatal, unresolved) filtered by dru...

.. dropdown:: FAERS_count_outcomes_by_drug_event tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_outcomes_by_drug_event``
   * **Type**: ``FDADrugAdverseEventTool``
   * **Description**: Count the outcome of adverse reactions (recovered, recovering, fatal, unresolved) filtered by drug, seriousness, and demographics. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproduct`` (string) (required)
     Drug name.

   * ``patientsex`` (string) (required)
     No description

   * ``patientagegroup`` (string) (required)
     No description

   * ``occurcountry`` (string) (required)
     No description

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_outcomes_by_drug_event",
          "arguments": {
              "medicinalproduct": "example_value",
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "occurcountry": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_patient_age_distribution** (Type: FDADrugAdverseEventTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Analyze the age distribution of patients experiencing adverse events for a specific drug. The age...

.. dropdown:: FAERS_count_patient_age_distribution tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_patient_age_distribution``
   * **Type**: ``FDADrugAdverseEventTool``
   * **Description**: Analyze the age distribution of patients experiencing adverse events for a specific drug. The age groups are: Neonate (0-28 days), Infant (29 days - 23 months), Child (2-11 years), Adolescent (12-17 years), Adult (18-64 years), Elderly (65+ years). Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproduct`` (string) (required)
     Drug name.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_patient_age_distribution",
          "arguments": {
              "medicinalproduct": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_reactions_by_drug_event** (Type: FDADrugAdverseEventTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Count the number of adverse reactions reported for a given drug, filtered by patient details, eve...

.. dropdown:: FAERS_count_reactions_by_drug_event tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_reactions_by_drug_event``
   * **Type**: ``FDADrugAdverseEventTool``
   * **Description**: Count the number of adverse reactions reported for a given drug, filtered by patient details, event seriousness, and reaction outcomes. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproduct`` (string) (required)
     Drug name.

   * ``patientsex`` (string) (required)
     Patient sex, leave it blank if you don't want to apply a filter.

   * ``patientagegroup`` (string) (required)
     Patient age group.

   * ``occurcountry`` (string) (required)
     Country where event occurred.

   * ``serious`` (string) (required)
     Whether the event was serious.

   * ``seriousnessdeath`` (string) (required)
     Was death reported?

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_reactions_by_drug_event",
          "arguments": {
              "medicinalproduct": "example_value",
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "occurcountry": "example_value",
              "serious": "example_value",
              "seriousnessdeath": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_reportercountry_by_drug_event** (Type: FDADrugAdverseEventTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Count the number of FDA adverse event reports grouped by the country of the primary reporter. Dat...

.. dropdown:: FAERS_count_reportercountry_by_drug_event tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_reportercountry_by_drug_event``
   * **Type**: ``FDADrugAdverseEventTool``
   * **Description**: Count the number of FDA adverse event reports grouped by the country of the primary reporter. Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproduct`` (string) (required)
     Drug name.

   * ``patientsex`` (string) (required)
     Patient sex, leave it blank if you don't want to apply a filter.

   * ``patientagegroup`` (string) (required)
     Patient age group.

   * ``serious`` (string) (required)
     Whether the event was serious.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_reportercountry_by_drug_event",
          "arguments": {
              "medicinalproduct": "example_value",
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "serious": "example_value"
          }
      }
      result = tu.run(query)


**FAERS_count_seriousness_by_drug_event** (Type: FDADrugAdverseEventTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Count the number of adverse event reports classified as serious or non-serious, filtered by drug ...

.. dropdown:: FAERS_count_seriousness_by_drug_event tool specification

   **Tool Information:**

   * **Name**: ``FAERS_count_seriousness_by_drug_event``
   * **Type**: ``FDADrugAdverseEventTool``
   * **Description**: Count the number of adverse event reports classified as serious or non-serious, filtered by drug and patient demographics. In results, term Serious means: 'The adverse event resulted in death, a life threatening condition, hospitalization, disability, congenital anomaly, or other serious condition', term Non-serious means 'The adverse event did not result in any of the above' Data source: FDA Adverse Event Reporting System (FAERS).

   **Parameters:**

   * ``medicinalproduct`` (string) (required)
     Drug name.

   * ``patientsex`` (string) (required)
     Patient sex, leave it blank if you don't want to apply a filter.

   * ``patientagegroup`` (string) (required)
     Patient age group.

   * ``occurcountry`` (string) (required)
     Country where event occurred.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "FAERS_count_seriousness_by_drug_event",
          "arguments": {
              "medicinalproduct": "example_value",
              "patientsex": "example_value",
              "patientagegroup": "example_value",
              "occurcountry": "example_value"
          }
      }
      result = tu.run(query)


Navigation
----------

* :doc:`tools_config_index` - Back to Tools Overview
* :doc:`../guide/loading_tools` - Loading Local Tools
