Space Configuration System
==============================

Space is a powerful configuration system that allows you to easily load, share, and manage tool configurations for ToolUniverse. It supports both simple presets and complex workspaces with AI integration.

Quick Start
-----------

Load a Space configuration in just one line:

.. code-block:: python

   from tooluniverse import ToolUniverse
   
   # Load from local file
   tu = ToolUniverse()
   config = tu.load_space("./my-config.yaml")
   
   # Or load from HuggingFace
   config = tu.load_space("hf:username/repo")

Command Line Usage
------------------

Use Space configurations with MCP servers:

.. code-block:: bash

   # Load local file
   tooluniverse-smcp-stdio --load "./my-config.yaml"
   
   # Load from HuggingFace
   tooluniverse-smcp-stdio --load "hf:username/repo"
   
   # Load from HTTP URL
   tooluniverse-smcp-stdio --load "https://example.com/config.yaml"

What is Space?
------------------

Space is a unified system for managing tool configurations that supports:

- **Presets**: Simple tool collections for specific domains
- **Workspaces**: Complete environments with tools, AI config, and workflows
- **Sharing**: Easy sharing via HuggingFace Hub, HTTP URLs, or local files
- **Versioning**: Support for versioned configurations
- **Validation**: Built-in configuration validation

Configuration Types
-------------------

Preset (Simple)
~~~~~~~~~~~~~~~

A preset is a collection of tools with basic configuration:

.. code-block:: yaml

   name: "Drug Discovery Essentials"
   version: "1.0.0"
   description: "Essential tools for drug discovery"
   
   tools:
     include_tools:
       - "ChEMBL_search_similar_molecules"
       - "search_clinical_trials"
       - "OpenTargets_get_disease_id_description_by_name"
     exclude_tools: ["slow_tool"]

Workspace (Advanced)
~~~~~~~~~~~~~~~~~~~~

A workspace includes tools plus AI configuration and workflows:

.. code-block:: yaml

   name: "Complete Research Environment"
   version: "2.0.0"
   
   tools:
     categories: ["agents", "drug_discovery_agents", "fda_drug_label"]
   
   llm_config:
     mode: "default"
     default_provider: "CHATGPT"
     models:
       default: "gpt-4o"
     temperature: 0.3
   
   hooks:
     - type: "SummarizationHook"
       enabled: true
       config:
         max_length: 500
         include_key_points: true

Loading Configurations
----------------------

HuggingFace Hub
~~~~~~~~~~~~~~~

Load configurations from HuggingFace Hub:

.. code-block:: python

   # Simple format
   tu.load_space("username/repo-name")
   
   # With version
   tu.load_space("username/repo-name@v1.0.0")
   
   # Explicit format
   tu.load_space("hf:username/repo-name")

Local Files
~~~~~~~~~~~

Load from local files:

.. code-block:: python

   # Relative path
   tu.load_space("./my-config.yaml")
   
   # Absolute path
   tu.load_space("/path/to/config.yaml")
   
   # File protocol
   tu.load_space("file:///path/to/config.yaml")

HTTP URLs
~~~~~~~~~

Load from any HTTP URL:

.. code-block:: python

   tu.load_space("https://example.com/config.yaml")

Configuration Overrides
-----------------------

Override Space settings with parameters:

.. code-block:: python

   # Load configuration with overrides
   config = tu.load_space(
       "./my-config.yaml",
       exclude_tools=["slow_tool"],      # Additional exclusions
       include_tools=["extra_tool"],     # Additional inclusions
       tool_type=["ChEMBL"]              # Override categories
   )

Configuration Merging
---------------------

Command line arguments take priority over Space configuration:

.. code-block:: bash

   # Space provides defaults, command line overrides
   tooluniverse-smcp-stdio \
       --load "./my-config.yaml" \
       --exclude-tools "problematic_tool" \
       --hooks

Creating Configurations
-----------------------

Basic Preset
~~~~~~~~~~~~

Create a simple preset:

.. code-block:: python

   from tooluniverse.space import validate_with_schema
   import yaml
   
   # Create preset configuration
   config = {
       "name": "My Research Toolkit",
       "version": "1.0.0",
       "description": "Tools for my research",
       "tools": {
           "categories": ["ChEMBL", "clinical_trials"],
           "exclude_tools": ["slow_tool"]
       }
   }
   
   # Validate and fill defaults
   is_valid, errors, processed_config = validate_with_schema(
       yaml.dump(config), fill_defaults_flag=True
   )
   
   # Save
   with open("./my-toolkit.yaml", "w") as f:
       yaml.dump(processed_config, f, default_flow_style=False)

Advanced Workspace
~~~~~~~~~~~~~~~~~~

Create a complete workspace:

.. code-block:: python

   from tooluniverse.space import validate_with_schema
   import yaml
   
   # Create workspace configuration
   config = {
       "name": "Complete Research Environment",
       "version": "1.0.0",
       "description": "Full research setup",
   
       "tools": {
           "categories": ["ChEMBL", "clinical_trials", "EuropePMC"]
       },
       "llm_config": {
           "default_provider": "CHATGPT",
           "models": {"default": "gpt-4o"},
           "temperature": 0.7
       },
       "hooks": [
           {"type": "output_summarization", "enabled": True}
       ]
   }
   
   # Validate and fill defaults
   is_valid, errors, processed_config = validate_with_schema(
       yaml.dump(config), fill_defaults_flag=True
   )
   
   # Save
   with open("./workspace.yaml", "w") as f:
       yaml.dump(processed_config, f, default_flow_style=False)

Configuration Validation
------------------------

Validate configurations before using:

.. code-block:: python

   from tooluniverse.space import validate_yaml_file_with_schema
   
   # Validate file with default filling
   is_valid, errors, processed_config = validate_yaml_file_with_schema(
       "./my-config.yaml", fill_defaults_flag=True
   )
   if not is_valid:
       print("Validation errors:")
       for error in errors:
           print(f"  - {error}")

Command Line Validation
~~~~~~~~~~~~~~~~~~~~~~~

Validate from command line using Python:

.. code-block:: bash

   # Validate configuration using Python
   python -c "
   from tooluniverse.space import validate_yaml_file_with_schema
   is_valid, errors, data = validate_yaml_file_with_schema('my-config.yaml')
   print('✅ Configuration is valid' if is_valid else f'❌ Found {len(errors)} validation error(s): {errors}')
   "

Configuration Schema
--------------------

Basic Fields
~~~~~~~~~~~~

.. code-block:: yaml

   name: "Configuration Name"           # Required
   version: "1.0.0"                    # Required
   author: "Author Name"               # Optional
   description: "Description"          # Optional
   tags: ["tag1", "tag2"]             # Optional

Tool Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   tools:
     categories: ["ChEMBL", "clinical_trials"]    # Tool categories
     include_tools: ["tool1", "tool2"]            # Specific tools
     exclude_tools: ["tool3"]                     # Excluded tools
     include_tool_types: ["OpenTarget"]           # Tool types
     exclude_tool_types: ["Unknown"]              # Excluded types
     custom:                                       # Custom tools
       - name: "CustomTool"
         type: "AgenticTool"
         description: "Custom tool description"
         prompt: "Tool prompt template..."

Prompt Templates
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   
     template_name: |
       Multi-line prompt template
       with placeholders: {variable}
       
       Use for: {purpose}

LLM Configuration
~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   llm_config:
     mode: "default"  # or "fallback"
     default_provider: "CHATGPT"  # CHATGPT, GEMINI, OPENROUTER, VLLM
     models:
       default: "gpt-4o"  # Only 'default' is used by AgenticTools
     temperature: 0.3

Hooks Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   hooks:
     - type: "SummarizationHook"
       enabled: true
       config:
         max_length: 500
         include_key_points: true
     
     - type: "FileSaveHook"
       enabled: true
       config:
         output_dir: "./outputs"
         file_prefix: "analysis"

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   required_env:
     - "OPENAI_API_KEY"  # For CHATGPT provider
     - "GEMINI_API_KEY"  # For GEMINI provider
     - "OPENROUTER_API_KEY"  # For OPENROUTER provider

Usage Instructions
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   
