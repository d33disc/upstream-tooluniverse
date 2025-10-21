# Space Example Configurations

This directory contains example Space configurations demonstrating different use cases and complexity levels.

## Configuration Files

### 1. `drug-discovery.yaml`
**Purpose**: Essential tools for drug discovery research
**Complexity**: Preset (intermediate)
**Tools**: ChEMBL, Clinical Trials, OpenTargets, FDA data
**Use Case**: Chemical compound analysis, clinical trial search, safety assessment

### 2. `literature-search.yaml`
**Purpose**: Scientific literature search and analysis
**Complexity**: Preset (intermediate)
**Tools**: EuropePMC, Semantic Scholar, PubTator, arXiv, Crossref
**Use Case**: Paper search, citation analysis, systematic reviews

### 3. `clinical-research.yaml`
**Purpose**: Clinical research and regulatory affairs
**Complexity**: Preset (intermediate)
**Tools**: Clinical Trials, FDA, Monarch, EFO, HPA
**Use Case**: Trial design, safety monitoring, regulatory submissions

### 4. `full-workspace.yaml`
**Purpose**: Complete research environment
**Complexity**: Workspace (advanced)
**Tools**: 32 categories covering all major domains (449 tools)
**Features**: LLM config, hooks, comprehensive tool coverage
**Use Case**: End-to-end research workflows

## Tool Configuration

### Recommended: Explicit Tool List (include_tools)
List specific tools for clarity and transparency:

```yaml
tools:
  include_tools:
    - "ChEMBL_search_molecule"
    - "ClinicalTrials_search_studies"
```

**Benefits**:
- Users know exactly what tools are loaded
- No surprises or hidden tools
- Easy to share and reproduce

### Alternative: Category Loading (categories)
Load all tools from categories (convenience method):

```yaml
tools:
  categories:
    - "ChEMBL"
    - "clinical_trials"
```

**Use when**:
- Exploring available tools
- Want all tools from a category
- Less control needed

### Optional: Exclusions (exclude_tools)
Remove specific tools:

```yaml
tools:
  categories: ["ChEMBL"]
  exclude_tools:
    - "ChEMBL_old_version"
```

**Rarely needed**, only when excluding problematic tools.

## LLM Configuration

**Note**: LLM configuration is only needed for complete workspace files (like `full-workspace.yaml`). 
Simple tool collections (like `literature-search.yaml`, `drug-discovery.yaml`) don't need LLM config.

### Default Mode (Recommended)
Space LLM config provides defaults for AgenticTools:

```yaml
llm_config:
  mode: "default"  # Space config as default
  # Direct AgenticTool api_type values
  # Supported values: CHATGPT, GEMINI, OPENROUTER, VLLM
  default_provider: "CHATGPT"
  models:
    default: "gpt-4o"           # Used by all AgenticTools
  temperature: 0.3              # 0.0-2.0 range
```

**Priority**: Space config > Built-in default

**Use case**: You want to standardize LLM settings across all tools.

### Fallback Mode
Space LLM config as backup when tool's API fails:

```yaml
llm_config:
  mode: "fallback"  # Space config as fallback
  default_provider: "CHATGPT"
  models:
    default: "gpt-4o"           # Used by all AgenticTools
  temperature: 0.3
```

**Priority**: Built-in default, then fallback to Space if API unavailable

**Use case**: Tools have specific LLM preferences, but you want a reliable fallback.

### Example: Tool with Specific Config

```json
{
  "name": "SpecializedTool",
  "type": "AgenticTool",
  "configs": {
    "api_type": "GEMINI",
    "model_id": "gemini-pro"
  }
}
```

**Note**: All AgenticTools use the `default` model from Space configuration.

- **Default mode**: Uses Space default (CHATGPT)
- **Fallback mode**: Uses tool's built-in default first, falls back to Space if unavailable

### Space LLM Configuration Fields

| Field | Type | Required | Description | Maps to AgenticTool |
|-------|------|----------|-------------|-------------------|
| `mode` | string | Yes | `"default"` or `"fallback"` | Environment variable |
| `default_provider` | string | No | AgenticTool api_type values | `api_type` field |
| `models` | object | No | Model configuration (only `default` used) | `model_id` field |
| `temperature` | float | No | 0.0-2.0 | `temperature` field |

### Supported Provider Values

| Space Provider | Required API Keys |
|-------------------|-------------------|
| `CHATGPT` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| `GEMINI` | `GEMINI_API_KEY` |
| `OPENROUTER` | `OPENROUTER_API_KEY` |
| `VLLM` | `VLLM_SERVER_URL` |

### AgenticTool Direct Configuration Fields

These fields can be set directly in AgenticTool JSON configurations:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `api_type` | string | `"CHATGPT"` | `"CHATGPT"`, `"GEMINI"`, `"OPENROUTER"`, `"VLLM"` |
| `model_id` | string | `"o1-mini"` | Model identifier |
| `temperature` | float | `0.1` | 0.0-2.0 |
| `return_json` | boolean | `false` | Return JSON format |
| `max_retries` | integer | `5` | Maximum retry attempts |
| `retry_delay` | integer | `5` | Delay between retries (seconds) |
| `return_metadata` | boolean | `true` | Include metadata in response |
| `validate_api_key` | boolean | `true` | Validate API key on init |
| `fallback_api_type` | string | `null` | Fallback API type |
| `fallback_model_id` | string | `null` | Fallback model ID |
| `use_global_fallback` | boolean | `true` | Use global fallback chain |
| `gemini_model_id` | string | `"gemini-2.0-flash"` | Gemini-specific model |
| `llm_task` | string | `"default"` | Task type for model selection |

## Usage Examples

### Loading a Preset
```python
from tooluniverse import ToolUniverse

# Load drug discovery configuration
tu = ToolUniverse()
config = tu.load_space("./drug-discovery.yaml")

# Use with overrides
config = tu.load_space("./drug-discovery.yaml", 
                          exclude_tools=["slow_tool"])
```

### Loading from File
```python
# Load local configuration
config = tu.load_space("./drug-discovery.yaml")

# Load from HuggingFace
config = tu.load_space("hf:username/repo")
```

### Command Line Usage
```bash
# Load local file via MCP server
tooluniverse-smcp-stdio --load "./drug-discovery.yaml"

# Load from HuggingFace
tooluniverse-smcp-stdio --load "hf:username/repo"

# Load from HTTP URL
tooluniverse-smcp-stdio --load "https://example.com/config.yaml"
```

## Configuration Structure

### Basic Preset
```yaml
name: "Preset Name"
version: "1.0.0"
description: "Description"
tools:
  # Recommended: explicit tool list
  include_tools:
    - "ChEMBL_search_molecule"
    - "ClinicalTrials_search_studies"
  # Optional: exclude problematic tools
  exclude_tools:
    - "problematic_tool"
```

### Full Workspace
```yaml
name: "Complete Research Workspace"
version: "1.0.0"
description: "Complete research environment with tools, LLM configuration, hooks, and workflow templates"
tags: ["research", "comprehensive", "workspace", "ai-powered", "multi-domain"]

tools:
  # Use categories for comprehensive coverage
  categories:
    - "agents"                    # AI agents and analysis tools
    - "drug_discovery_agents"     # Drug discovery AI agents
    - "fda_drug_label"           # FDA drug information
    - "opentarget"               # OpenTargets drug-target-disease data
    # ... 28 more categories

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
  - type: "FileSaveHook"
    enabled: true
    config:
      output_dir: "./outputs"
      file_prefix: "analysis"

