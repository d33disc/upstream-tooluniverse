ToolUniverse Architecture
=============================

This document provides a comprehensive overview of ToolUniverse's code architecture, directory organization, core components, tool discovery/execution flow, MCP integration, and extension points.

Overview
--------

ToolUniverse follows a modular, registry-based architecture centered around the unified `ToolUniverse` engine. It connects to massive scientific databases and APIs through tool registration, configuration, and auto-discovery, providing a consistent interface for upper-layer agents, applications, and MCP clients.

.. code-block:: text

   ┌────────────────────┐
   │ Applications/Agents│  ← Your business logic, conversational systems, scripts
   └──────────┬─────────┘
              │ Python API/MCP
   ┌──────────▼─────────┐
   │  ToolUniverse Core │  ← Tool loading, registration, routing, execution
   └──────────┬─────────┘
              │ Registry/Config
   ┌──────────▼─────────┐
   │ Tool Implementation│  ← OpenFDA, OpenTargets, UniProt, PubChem, GWAS...
   │     Modules        │
   └──────────┬─────────┘
              │ HTTP/GraphQL/Local
   ┌──────────▼─────────┐
   │External Services/DB│
   └────────────────────┘

Repository Structure Tree
-------------------------

.. code-block:: text

   ToolUniverse/
   ├── src/tooluniverse/                          # Core package directory
   │   ├── __init__.py                           # Package exports, lazy loading control
   │   │
   │   ├── # Core Engine & Registry
   │   ├── execute_function.py                   # ToolUniverse main engine class
   │   ├── base_tool.py                         # BaseTool base class & exceptions
   │   ├── tool_registry.py                     # Tool registration & discovery
   │   ├── default_config.py                    # Default tool file configurations
   │   ├── logging_config.py                    # Logging setup
   │   └── utils.py                             # Utility functions
   │   │
   │   ├── # Tool Implementation Modules
   │   ├── openfda_tool.py                      # FDA drug labels & data
   │   ├── openfda_adv_tool.py                  # FDA adverse events
   │   ├── ctg_tool.py                          # ClinicalTrials.gov
   │   ├── graphql_tool.py                      # OpenTargets GraphQL APIs
   │   ├── uniprot_tool.py                      # UniProt protein database
   │   ├── pubchem_tool.py                      # PubChem chemical database
   │   ├── reactome_tool.py                     # Reactome pathway database
   │   ├── europe_pmc_tool.py                   # Europe PMC literature
   │   ├── semantic_scholar_tool.py             # Semantic Scholar papers
   │   ├── gwas_tool.py                         # GWAS Catalog genetics
   │   ├── hpa_tool.py                          # Human Protein Atlas
   │   ├── rcsb_pdb_tool.py                     # Protein Data Bank
   │   ├── medlineplus_tool.py                  # MedlinePlus health info
   │   ├── restful_tool.py                      # Generic REST APIs (Monarch)
   │   ├── url_tool.py                          # Web scraping & PDF extraction
   │   ├── pubtator_tool.py                     # PubTator literature mining
   │   ├── xml_tool.py                          # XML data processing
   │   ├── admetai_tool.py                      # ADMET AI predictions
   │   ├── alphafold_tool.py                    # AlphaFold protein structures
   │   ├── chem_tool.py                         # ChEMBL chemical bioactivity
   │   ├── compose_tool.py                      # Tool composition & workflows
   │   ├── package_tool.py                      # Local package tools
   │   ├── dataset_tool.py                      # Local dataset access
   │   ├── mcp_client_tool.py                   # MCP client for remote tools
   │   ├── remote_tool.py                       # Remote tool abstractions
   │   ├── agentic_tool.py                      # Agentic behavior tools
   │   ├── enrichr_tool.py                      # Enrichr gene set analysis
   │   ├── efo_tool.py                          # Experimental Factor Ontology
   │   ├── gene_ontology_tool.py                # Gene Ontology
   │   ├── humanbase_tool.py                    # HumanBase networks
   │   ├── dailymed_tool.py                     # DailyMed drug labels
   │   ├── uspto_tool.py                        # USPTO patent data
   │   ├── uspto_downloader_tool.py             # USPTO bulk downloads
   │   ├── openalex_tool.py                     # OpenAlex scholarly data
   │   └── boltz_tool.py                        # Boltz protein folding
   │   │
   │   ├── # Tool Discovery & Search
   │   ├── tool_finder_keyword.py               # Keyword-based tool search
   │   ├── tool_finder_embedding.py             # Embedding-based tool search
   │   ├── tool_finder_llm.py                   # LLM-powered tool discovery
   │   ├── remote/docker_llm/                   # Docker-based LLM provisioning helpers
   │   ├── DockerLLMProvisioner.py              # Compose tool for Docker LLM MCP auto-registration
   │   ├── embedding_database.py                # Tool embedding database
   │   └── embedding_sync.py                    # Embedding synchronization
   │   │
   │   ├── # MCP Integration & Servers
   │   ├── smcp.py                              # FastMCP wrapper (SMCP class)
   │   ├── smcp_server.py                       # MCP server entry points
   │   ├── mcp_integration.py                   # ToolUniverse MCP methods injection
   │   └── mcp_tool_registry.py                 # MCP tool registry & URLs
   │   │
   │   ├── # Configuration & Data
   │   ├── data/                                # Tool configurations
   │   │   ├── *.json                          # Tool instance definitions
   │   │   ├── packages/                       # Package-related configs
   │   │   └── remote_tools/                   # Remote/MCP tool definitions
   │   │
   │   ├── # Tool Collections & Workflows
   │   ├── toolsets/                           # Organized tool collections
   │   │   ├── bioinformatics/                # Bioinformatics toolset
   │   │   ├── research/                      # Research toolset
   │   │   └── software_dev/                  # Software development tools
   │   │
   │   ├── compose_scripts/                    # Workflow composition scripts
   │   │   ├── __init__.py
   │   │   ├── biomarker_discovery.py         # Biomarker discovery workflow
   │   │   ├── comprehensive_drug_discovery.py # Drug discovery pipeline
   │   │   ├── drug_safety_analyzer.py        # Drug safety analysis
   │   │   ├── literature_tool.py             # Literature analysis
   │   │   ├── output_summarizer.py           # Result summarization
   │   │   ├── tool_description_optimizer.py  # Tool description optimization
   │   │   ├── tool_discover.py               # Tool discovery workflows
   │   │   └── tool_graph_composer.py         # Tool graph composition
   │   │
   │   ├── # External Integrations & Examples
   │   ├── remote/                             # External system integrations
   │   │   ├── expert_feedback/               # Human expert feedback system
   │   │   ├── expert_feedback_mcp/           # MCP-enabled expert feedback
   │   │   ├── boltz/                         # Boltz integration
   │   │   ├── depmap_24q2/                   # DepMap data integration
   │   │   ├── immune_compass/                # Immune system tools
   │   │   ├── pinnacle/                      # Pinnacle integration
   │   │   ├── transcriptformer/              # Transcriptformer model
   │   │   └── uspto_downloader/              # USPTO downloader service
   │   │
   │   ├── # Visualization & UI
   │   ├── scripts/                           # Utility scripts
   │   │   ├── generate_tool_graph.py         # Tool graph generation
   │   │   └── visualize_tool_graph.py        # Tool graph visualization
   │   ├── tool_graph_web_ui.py               # Web-based tool graph UI
   │   │
   │   ├── # Configuration Templates
   │   ├── template/                          # Configuration templates
   │   │   ├── file_save_hook_config.json     # File save hook template
   │   │   └── hook_config.json               # General hook template
   │   │
   │   ├── # Output Processing
   │   ├── output_hook.py                     # Output processing hooks
   │   ├── extended_hooks.py                  # Extended hook functionality
   │   │
   │   └── # Testing
   │       └── test/                          # Unit & integration tests
   │           ├── *.py                       # Test modules
   │           ├── *.xml                      # Test data
   │           └── *.parquet                  # Test datasets
   │
   ├── # Documentation
   ├── docs/                                  # Sphinx documentation
   │   ├── _build/                           # Built documentation
   │   ├── _static/                          # Static assets
   │   ├── _templates/                       # Doc templates
   │   ├── api/                              # API documentation
   │   ├── expand_tooluniverse/              # Extension guides
   │   ├── guide/                            # User guides
   │   ├── reference/                        # Reference docs
   │   ├── tutorials/                        # Tutorials
   │   └── *.rst                             # Documentation source
   │
   ├── # Root-level Files
   ├── pyproject.toml                        # Project config, dependencies, CLI
   ├── smcp_tooluniverse_server.py          # Simplified MCP server launcher
   ├── README.md                             # Project overview
   ├── README_USAGE.md                       # Usage documentation
   ├── LICENSE                               # License file
   ├── uv.lock                              # UV lock file
   │
   ├── # Build & Meta
   ├── build_docs.sh                        # Documentation build script
   ├── internal/                            # Internal data & utilities
   ├── img/                                 # Images & assets
   └── generated_tool_*                     # Generated tool files

Core Components
---------------

**Engine & Registry**

- `execute_function.py`: Core `ToolUniverse` engine class responsible for:
  - Reading tool configurations (local JSON, default configs) and building `all_tools`/`all_tool_dict`
  - Mapping tool types to concrete classes (`tool_type_mappings`) and instantiation
  - Tool execution routing (`run_tool`), validation, and result processing
  - Handling MCP auto-loaders, temporary clients (with `mcp_integration.py`)

- `base_tool.py`: `BaseTool` base class and exception types. Supports:
  - Loading default configurations from `tooluniverse.data` package
  - Parameter validation, required parameter extraction, function call validation

- `tool_registry.py`: Tool registration and discovery:
  - `@register_tool` decorator for registering tool classes
  - Lazy loading registry (on-demand module imports) and full discovery
  - Smart matching of configuration JSON to modules and tool types

- `default_config.py`: Default tool configuration file list
- `logging_config.py`, `utils.py`: Logging setup and utility functions

**Tool Implementation Classes**

Available tool classes (alphabetically organized):

`ADMETAITool`, `AgenticTool`, `AlphaFoldRESTTool`, `BoltzTool`, `ChEMBLTool`, `ClinicalTrialsDetailsTool`, `ClinicalTrialsSearchTool`, `ComposeTool`, `DatasetTool`, `DiseaseTargetScoreTool`, `EFOTool`, `EmbeddingDatabase`, `EmbeddingSync`, `EnrichrTool`, `EuropePMCTool`, `FDACountAdditiveReactionsTool`, `FDADrugAdverseEventTool`, `FDADrugLabelGetDrugGenericNameTool`, `FDADrugLabelSearchIDTool`, `FDADrugLabelSearchTool`, `FDADrugLabelTool`, `GWASAssociationByID`, `GWASAssociationSearch`, `GWASAssociationsForSNP`, `GWASAssociationsForStudy`, `GWASAssociationsForTrait`, `GWASSNPByID`, `GWASSNPSearch`, `GWASSNPsForGene`, `GWASStudiesForTrait`, `GWASStudyByID`, `GWASStudySearch`, `GWASVariantsForTrait`, `GeneOntologyTool`, `GetSPLBySetIDTool`, `HPAGetGeneJSONTool`, `HPAGetGeneXMLTool`, `HumanBaseTool`, `MCPAutoLoaderTool`, `MCPClientTool`, `MedlinePlusRESTTool`, `MonarchDiseasesForMultiplePhenoTool`, `MonarchTool`, `OpenAlexTool`, `OpentargetGeneticsTool`, `OpentargetTool`, `OpentargetToolDrugNameMatch`, `PackageTool`, `PubChemRESTTool`, `PubTatorTool`, `RCSBTool`, `ReactomeRESTTool`, `RemoteTool`, `SearchSPLTool`, `SemanticScholarTool`, `ToolFinderEmbedding`, `ToolFinderKeyword`, `ToolFinderLLM`, `URLHTMLTagTool`, `URLToPDFTextTool`, `USPTODownloaderTool`, `USPTOOpenDataPortalTool`, `UniProtRESTTool`, `XMLDatasetTool`

**Data & Configuration**

- `data/*.json`: Tool configuration manifests for each data source or category
- `data/packages/*`: Package-related extension configurations
- `data/remote_tools/*`: Remote tool/MCP definitions
- `toolsets/`: Scenario-organized tool collections (`bioinformatics/`, `research/`, `software_dev/`)

**MCP Integration & Servers**

- `smcp.py`: FastMCP wrapper providing `SMCP` and `create_smcp_server`
- `smcp_server.py`: Package MCP server entry points (exposed via `pyproject.toml` CLI)
- `mcp_integration.py`: Injects `load_mcp_tools`, `discover_mcp_tools` methods into `ToolUniverse`
- `mcp_tool_registry.py`: MCP tool registry for URLs and tool discovery
- Root `smcp_tooluniverse_server.py`: Simplified startup script for local quick server startup

**External Ecosystem & Extension Examples**

- `remote/`: External system integrations including:
  - `expert_feedback/`: Human expert feedback system
  - `expert_feedback_mcp/`: MCP-enabled expert feedback
  - `boltz/`: Boltz protein folding integration
  - `depmap_24q2/`: DepMap cancer dependency data integration
  - `immune_compass/`: Immune system analysis tools
  - `pinnacle/`: Pinnacle platform integration
  - `transcriptformer/`: Transcriptformer model integration
  - `uspto_downloader/`: USPTO patent downloader service

Execution Flow (Configuration to Invocation)
---------------------------------------------

1. **Configuration Loading**
   - Engine startup reads `default_tool_files` and `data/*.json` to build tool manifest
   - Each JSON entry defines a tool instance: `name`, `type`, `description`, `parameter` (JSON Schema), endpoints, etc.

2. **Tool Registration & Mapping**
   - `tool_registry.py` maintains "tool type → tool class" mappings
   - Supports both full import discovery and lazy loading mappings (smart config-to-module matching)

3. **Instantiation & Default Configuration**
   - Based on `type`, finds corresponding class (e.g., `FDADrugLabelTool`)
   - Merges `BaseTool` default configurations with entry-specific config

4. **Execution & Validation**
   - `ToolUniverse.run_tool(tool_name, params)`:
     - Locate instance by name → Parameter validation (required fields) → Call concrete implementation
     - Unified error handling and return structure

5. **Composition/Discovery & Graphs**
   - Use `compose_tool.py` or `compose_scripts/` for orchestration
   - Leverage `tool_finder_*` (keyword/embedding/LLM) for tool retrieval
   - Visualize tool relationships and call chains via scripts or `tool_graph_web_ui.py`

MCP Integration
---------------

**Server Side:**
- `smcp.py` provides `SMCP` object for one-click exposure of all ToolUniverse tools
- `smcp_server.py` and root `smcp_tooluniverse_server.py` provide convenient startup
- `pyproject.toml` exposes commands: `tooluniverse-mcp`, `tooluniverse-smcp*`, etc.

**Client/Remote Tools:**
- `mcp_client_tool.py`, `mcp_integration.py` support discovery and dynamic registration from remote MCP servers
- `MCPAutoLoaderTool` can auto-discover and batch-register remote tools by URL with configurable prefixes and timeouts
- `list_mcp_connections()` shows loaded remote connections and tool counts

Configuration & Data Conventions
---------------------------------

**Tool Configuration Structure** (`data/*.json` files):

.. code-block:: json

   {
     "name": "FDADrugLabelGetDrugGenericName",
     "type": "FDADrugLabelGetDrugGenericNameTool",
     "description": "Get generic name for an FDA drug label",
     "parameter": {
       "type": "object",
       "properties": {
         "drug_name": {"type": "string", "required": true}
       }
     },
     "endpoint": "https://api.fda.gov/drug/label.json",
     "method": "GET"
   }

**Naming & Mapping Conventions:**
- `*_tools.json` typically corresponds to `*_tool.py` modules
- `tool_registry.py` performs smart matching
- Can use `@register_tool` for explicit registration at class definition

Extension Points
----------------

**Adding New Data Source Tools:**

1. Create `xxx_tool.py` in `src/tooluniverse/` inheriting from `BaseTool`
2. Use `@register_tool('YourToolType')` for registration, or rely on naming conventions
3. Add one or more tool entries in `data/xxx_tools.json`

**Integrating Remote MCP Tools:**

- Use `MCPAutoLoaderTool` with server URL for auto-discovery
- Or use `ToolUniverse.load_mcp_tools([...])` for runtime dynamic loading

**Composition & Workflows:**

- Use `compose_tool.py` or add scripts in `compose_scripts/` for complex call chains
- Leverage `tool_finder_*` for retrieval and routing assistance

Tool Loading Cheat Sheet
------------------------

- Package data is loaded from the JSON files mapped in :mod:`default_config.py` plus everything under ``src/tooluniverse/data/``.
- Remote/MCP entries are merged from both the packaged ``data/remote_tools`` directory **and** the user override folder ``~/.tooluniverse/remote_tools``. Dropping a JSON config there makes the tool visible without code changes.
- The runtime builds three main registries:

  1. ``tool_files`` → category JSON manifests (local tools)
  2. ``data/remote_tools`` → bundled remote definitions
  3. ``~/.tooluniverse/remote_tools`` → user/automation supplied remote definitions

- Use ``ToolUniverse.load_tools()`` to refresh the registry after adding new files without restarting the host process.

Remote MCP Provisioning
-----------------------

- ``DockerLLMProvisioner`` (compose tool) and ``scripts/provision_docker_llm.py`` automate standing up an MCP-enabled LLM in Docker, poll its ``/health`` endpoint, and emit the JSON configs under ``~/.tooluniverse/remote_tools`` so the new tool registers instantly.
- Remote stubs created from bundled configs (e.g., expert feedback, DepMap) are read-only until you connect ToolUniverse to the actual MCP server. You can:

  1. Call ``ToolUniverse.load_mcp_tools(["http://server:port/mcp"])`` to ingest tools live, or
  2. Provision a local container via ``DockerLLMProvisioner`` or the CLI helper to host the endpoints yourself.
- The `RemoteTool` error message now includes these activation instructions when an agent accidentally calls an offline remote tool.

Catalog Navigation Tips
-----------------------

- ``ToolNavigatorTool`` combines the full catalog (including remote/VSD entries) with lightweight scoring—use it to shortlist relevant tools before running long compositions.
- ``ToolFinderKeyword`` / ``ToolFinderEmbedding`` provide complementary search modalities; both now benefit from the expanded metadata listed in ``~/.tooluniverse/remote_tools``.
- For big collections consider building category-specific shortlists in ``toolsets/`` and surfacing them via ``ToolNavigatorTool`` filters or custom compose tools.

Directory Quick Reference
--------------------------

- **Core Package**: `src/tooluniverse/`
- **Tool Implementations**: Various `*_tool.py` files in same directory
- **Tool Configurations**: `src/tooluniverse/data/*.json`
- **Tool Collections**: `src/tooluniverse/toolsets/`
- **Composition Scripts**: `src/tooluniverse/compose_scripts/`
- **MCP & Servers**: `src/tooluniverse/smcp.py`, `src/tooluniverse/smcp_server.py`, root `smcp_tooluniverse_server.py`
- **External Integrations**: `src/tooluniverse/remote/`
- **Visualization & Graphs**: `src/tooluniverse/scripts/`, `src/tooluniverse/tool_graph_web_ui.py`
- **Temp/cache outputs**: user cache directory (macOS: `~/Library/Caches/ToolUniverse`, Linux: `~/.cache/tooluniverse`, Windows: `%LOCALAPPDATA%\\ToolUniverse\\Cache`)

Summary
-------

ToolUniverse provides a complete ecosystem from tool discovery and execution to remote integration (MCP) through clear registry mechanisms, standardized JSON configurations, and rich tool modules. You can quickly extend new data sources or capabilities by adding modules and configurations without modifying the engine. The composition and visualization tools enable building explainable, reusable scientific workflows.
