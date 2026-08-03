<!-- refreshed: 2026-08-03 -->
# Architecture

**Analysis Date:** 2026-08-03

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                  Connection / transport surfaces                │
├──────────────────┬──────────────────┬──────────────────┬──────────────────┤
│ Python SDK       │ MCP (stdio/HTTP) │ REST / client    │ CLI              │
│ `__init__.py`    │ `smcp_server.py`  │ `http_api_*.py` │ `cli.py`         │
└────────┬─────────┴────────┬─────────┴────────┬─────────┴─────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            ▼
┌────────────────────────────────────────────────────────────┐
│               Shared orchestration core                       │
│ `src/tooluniverse/execute_function.py` (`ToolUniverse`)       │
│ discovery → schema validation → execution → hooks/cache       │
└──────────────────────────────┬──────────────────────────────┘
                             │
              ┌──────────────┬──────────────┐
              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌───────────────┐
│ Registries  │ │ Config/data │ │ Tool adapters │
│ `tool_      │ │ `data/*.json`│ │ `*_tool.py`,  │
│ registry.py`│ │ profiles     │ │ `tools/*.py`  │
└──────┬──────┘ └──────┬──────┘ └───────┬───────┘
       └────────────────┴───────────────────────┘
                             ▼
┌────────────────────────────────────────────────────────────┐
│ External scientific APIs, local compute, files, subprocesses,     │
│ remote MCP servers, caches, and embedding/vector stores          │
└────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Public package | Exports `ToolUniverse`, `BaseTool`, profiles, SMCP, HTTP client, and lazy tool-class access | `src/tooluniverse/__init__.py` |
| Orchestration core | Loads tool specifications, resolves names, validates calls, initializes adapters, runs single/batch calls, applies hooks, and manages lifecycle | `src/tooluniverse/execute_function.py` |
| Base contract | Applies defaults, validates JSON-schema inputs, provides caching and the common `run()` contract | `src/tooluniverse/base_tool.py` |
| Registry | Registers adapter classes/configs and lazily imports built-in or entry-point-contributed tools | `src/tooluniverse/tool_registry.py` |
| Default catalog | Maps category names to packaged JSON tool-definition files | `src/tooluniverse/default_config.py` |
| Discovery | Implements keyword, embedding, and LLM-assisted tool selection | `src/tooluniverse/tool_finder_keyword.py`, `src/tooluniverse/tool_finder_embedding.py`, `src/tooluniverse/tool_finder_llm.py` |
| MCP adapter | Extends FastMCP, exposes proxy or full tool surfaces, and dispatches calls to the shared core | `src/tooluniverse/smcp.py` |
| MCP launchers | Parse transport/profile/hook flags and start stdio, HTTP, or SSE servers | `src/tooluniverse/smcp_server.py` |
| REST adapter | Introspects public `ToolUniverse` methods and exposes generic FastAPI routes through a singleton manager | `src/tooluniverse/http_api_server.py` |
| CLI adapter | Implements discovery, inspection, execution, status, health, build, and server commands | `src/tooluniverse/cli.py` |
| Tool implementations | Translate normalized arguments into an API request, computation, workflow, or remote call | `src/tooluniverse/*_tool.py`, `src/tooluniverse/tools/*.py` |
| Profile subsystem | Loads and validates workspace, local, URL, and hosted profile configuration | `src/tooluniverse/profile/loader.py`, `src/tooluniverse/profile/validator.py` |
| Cache subsystem | Provides memory/SQLite result caching behind a common manager | `src/tooluniverse/cache/result_cache_manager.py` |

## Pattern Overview

**Overall:** Configuration-driven plugin architecture with a shared application core and multiple transport adapters.

**Key Characteristics:**
- Every connection surface converges on `ToolUniverse` in `src/tooluniverse/execute_function.py`; transport code adapts protocol details but does not own scientific execution.
- JSON definitions in `src/tooluniverse/data/*.json` describe public tool names, schemas, and adapter types separately from Python implementations.
- `src/tooluniverse/tool_registry.py` uses decorators, a generated static lazy registry in `src/tooluniverse/_lazy_registry_static.py`, namespace package extension, and Python entry points to defer imports and accept add-on packages.
- Tool instances are created on demand and retained in `ToolUniverse` state; definitions can be filtered by category/profile without importing every optional dependency.
- Cross-cutting validation, caching, hooks, logging, and error normalization surround adapter calls in the core and `BaseTool`.

## Layers

**Connection Layer:**
- Purpose: Translate Python, CLI, MCP, REST, or framework-specific inputs and outputs.
- Location: `src/tooluniverse/__init__.py`, `src/tooluniverse/cli.py`, `src/tooluniverse/smcp.py`, `src/tooluniverse/smcp_server.py`, `src/tooluniverse/http_api_server.py`, `src/tooluniverse/http_client.py`, `src/tooluniverse/smolagent_tool.py`
- Contains: Console entry points, FastMCP tools, FastAPI routes/models, and client adapters.
- Depends on: The orchestration layer.
- Used by: Humans, scripts, notebooks, MCP hosts, web clients, and agent frameworks.

**Orchestration Layer:**
- Purpose: Provide the authoritative lifecycle, discovery, schema inspection, and execution behavior.
- Location: `src/tooluniverse/execute_function.py`
- Contains: `ToolUniverse`, `ToolNamespace`, callable proxies, loading/filtering, sync/batch execution, and cleanup.
- Depends on: Registry, configuration, profiles, hooks, cache, and tool adapters.
- Used by: Every connection layer.

**Discovery and Metadata Layer:**
- Purpose: Locate tools and supply exact input specifications without initializing all implementations.
- Location: `src/tooluniverse/tool_registry.py`, `src/tooluniverse/tool_finder_keyword.py`, `src/tooluniverse/tool_finder_embedding.py`, `src/tooluniverse/tool_discovery_tools.py`, `src/tooluniverse/data/*.json`
- Contains: Lazy module mappings, tool configs, BM25/embedding search, and schema inspection.
- Depends on: Packaged definitions, optional embedding providers, and plugin metadata.
- Used by: `ToolUniverse`, compact MCP proxy tools, and `tu` discovery commands.

**Tool Adapter Layer:**
- Purpose: Execute one scientific operation behind the common `run(arguments, ...)` contract.
- Location: `src/tooluniverse/base_tool.py`, `src/tooluniverse/*_tool.py`, `src/tooluniverse/tools/*.py`, `src/tooluniverse/remote/`
- Contains: API clients, database queries, local computations, agents, file operations, and remote-service adapters.
- Depends on: External services/libraries and shared utility modules.
- Used by: The orchestration layer after a tool name is resolved.

**Infrastructure Layer:**
- Purpose: Supply caching, profiles, logging, security guards, hooks, task persistence, and embedding stores.
- Location: `src/tooluniverse/cache/`, `src/tooluniverse/profile/`, `src/tooluniverse/database_setup/`, `src/tooluniverse/logging_config.py`, `src/tooluniverse/server_security.py`, `src/tooluniverse/output_hook.py`
- Contains: SQLite/memory stores, validators/loaders, thread-safe state, and execution policies.
- Depends on: Standard library and declared infrastructure dependencies.
- Used by: Core and transport layers.

## Data Flow

### Primary Request Path

1. A caller enters through the SDK export (`src/tooluniverse/__init__.py:26`), CLI (`src/tooluniverse/cli.py:1754`), MCP launcher (`src/tooluniverse/smcp_server.py:1018`), or REST application (`src/tooluniverse/http_api_server.py:166`).
2. The transport converts its request to a tool name plus arguments and delegates to the persistent `ToolUniverse` instance in `src/tooluniverse/execute_function.py:305`.
3. `ToolUniverse.load_tools()` merges packaged JSON definitions, profile/workspace sources, auto-discovered configs, and filters (`src/tooluniverse/execute_function.py:895`).
4. `run_one_function()` resolves aliases/names, validates arguments against the selected definition, and initializes the registered adapter lazily (`src/tooluniverse/execute_function.py:3018`).
5. The adapter follows `BaseTool.run()` or a compatible registered contract, talks to its external/local backend, and returns Python data (`src/tooluniverse/base_tool.py`).
6. The core applies cache/hook/output handling and the connection layer serializes the result for Python, JSON-RPC, HTTP JSON, or terminal output.

### Compact Discovery and Execution Flow

1. Compact MCP or `tu` clients call `list_tools`, `grep_tools`, `find_tools`, or `get_tool_info` through `src/tooluniverse/smcp.py` or `src/tooluniverse/cli.py`.
2. Discovery reads specifications and search indexes without exposing every backend tool in the protocol context; `src/tooluniverse/tool_finder_keyword.py` provides deterministic keyword search and `src/tooluniverse/tool_finder_embedding.py` provides semantic search.
3. After schema inspection, `execute_tool` forwards the chosen backend name and exact arguments to `ToolUniverse`; backend tools remain loaded even when only proxy tools are protocol-visible.

### Extension Loading Flow

1. Built-in classes register with `@register_tool` from `src/tooluniverse/tool_registry.py` or appear in `src/tooluniverse/_lazy_registry_static.py`.
2. Packaged definitions enter through category mappings in `src/tooluniverse/default_config.py`; workspace `.py`/`.json` files and profiles enter through `ToolUniverse.load_tools()`.
3. Installed sub-packages extend the `tooluniverse` namespace in `src/tooluniverse/__init__.py` and may contribute class/config registries through entry points.

**State Management:**
- A `ToolUniverse` object owns loaded specifications, initialized adapter instances, namespace proxies, hook state, executor resources, and workspace/profile context in `src/tooluniverse/execute_function.py`.
- The REST server shares one lazily initialized instance behind a lock in `src/tooluniverse/http_api_server.py:86`.
- MCP servers own a `ToolUniverse` instance inside `SMCP` and use a configurable `ThreadPoolExecutor` for blocking tools in `src/tooluniverse/smcp.py`.
- Module-level registries and lazy caches in `src/tooluniverse/tool_registry.py` are process-global; result caches may persist through SQLite in `src/tooluniverse/cache/sqlite_backend.py`.

## Key Abstractions

**ToolUniverse:**
- Purpose: Single authoritative facade for loading, inspecting, selecting, executing, and closing tools.
- Examples: `src/tooluniverse/execute_function.py`, `src/tooluniverse/__init__.py`
- Pattern: Stateful facade/orchestrator shared by all transports.

**Tool Definition:**
- Purpose: Declarative name, description, parameter schema, adapter `type`, and optional execution metadata.
- Examples: `src/tooluniverse/data/special_tools.json`, `src/tooluniverse/data/uniprot_tools.json`, `src/tooluniverse/default_config.py`
- Pattern: Configuration separated from implementation.

**BaseTool / Registered Adapter:**
- Purpose: Convert a validated argument dictionary into one backend operation while presenting a uniform call contract.
- Examples: `src/tooluniverse/base_tool.py`, `src/tooluniverse/uniprot_tool.py`, `src/tooluniverse/tools/UniProt_get_entry_by_accession.py`
- Pattern: Strategy selected from a registry; optional defaults and cache behavior live in the base class.

**Tool Registry:**
- Purpose: Map config `type` values and public tool names to implementation modules/classes without eagerly importing the full catalog.
- Examples: `src/tooluniverse/tool_registry.py`, `src/tooluniverse/_lazy_registry_static.py`
- Pattern: Decorator registry plus lazy plugin discovery.

**Profile:**
- Purpose: Define a reusable subset/configuration of the catalog and merge it with workspace settings.
- Examples: `src/tooluniverse/profile/loader.py`, `src/tooluniverse/profile/validator.py`, `src/tooluniverse/data/default_profile.yaml`
- Pattern: Validated configuration overlay.

**Output Hook:**
- Purpose: Post-process or persist large results without changing individual tool adapters.
- Examples: `src/tooluniverse/output_hook.py`, `src/tooluniverse/summarization_hook.py`, `src/tooluniverse/file_save_hook.py`
- Pattern: Execution pipeline middleware.

## Entry Points

**Python SDK:**
- Location: `src/tooluniverse/__init__.py`
- Triggers: `from tooluniverse import ToolUniverse`.
- Responsibilities: Export the facade and optional integrations; support lazy tool-class lookup.

**Default MCP stdio:**
- Location: `src/tooluniverse/smcp_server.py:1018`
- Triggers: `tooluniverse` console script in `pyproject.toml`.
- Responsibilities: Start a compact stdio MCP server with discovery proxies and backend execution.

**Configurable MCP servers:**
- Location: `src/tooluniverse/smcp_server.py:53`, `src/tooluniverse/smcp_server.py:190`, `src/tooluniverse/smcp_server.py:628`
- Triggers: `tooluniverse-mcp`, `tooluniverse-smcp-server`, `tooluniverse-smcp-stdio`, or `tooluniverse-smcp`.
- Responsibilities: Parse transport, category, profile, workspace, hook, host, and port options and instantiate `SMCP`.

**REST API:**
- Location: `src/tooluniverse/http_api_server_cli.py`, `src/tooluniverse/http_api_server.py`
- Triggers: `tooluniverse-http-api` or module execution.
- Responsibilities: Secure network binding, expose health/method discovery, and dispatch generic method calls.

**Operational CLI:**
- Location: `src/tooluniverse/cli.py:1754`
- Triggers: `tu`.
- Responsibilities: Discover, inspect, run, test, diagnose, and serve tools from a shell.

**Datastore CLI:**
- Location: `src/tooluniverse/database_setup/cli.py`
- Triggers: `tu-datastore`.
- Responsibilities: Build, package, synchronize, and search embedding-backed tool/datastore indexes.

## Architectural Constraints

- **Threading:** Most tool implementations are synchronous. MCP and REST offload blocking calls to `ThreadPoolExecutor` instances in `src/tooluniverse/smcp.py` and `src/tooluniverse/http_api_server.py`; batch execution also uses worker pools in `src/tooluniverse/execute_function.py`.
- **Global state:** Registry dictionaries and import caches in `src/tooluniverse/tool_registry.py`, the REST `_tu_manager` and `_thread_pool` in `src/tooluniverse/http_api_server.py`, and environment-driven settings are process-wide.
- **Circular imports:** `src/tooluniverse/__init__.py` deliberately delays MCP patching until core imports finish. Keep tool modules dependent on `base_tool.py`/`tool_registry.py`, not package-level eager imports.
- **Optional dependencies:** Lazy import and graceful fallbacks are required because individual tools have heterogeneous dependencies; do not eagerly import the entire catalog from transport or package initialization code.
- **Protocol stability:** All transports must route execution through `ToolUniverse`; adding transport-specific execution logic creates behavioral drift.
- **Schema-first calls:** Public callers must inspect the chosen definition before execution because argument names differ across tools; preserve JSON-schema validation at the core boundary.
- **Workspace precedence:** Explicit workspace, environment-configured workspace, local `.tooluniverse`, and global workspace behavior is resolved centrally in `src/tooluniverse/execute_function.py:549`.

## Anti-Patterns

### Bypassing the Shared Core

**What happens:** A CLI, MCP, or REST handler imports a scientific adapter and invokes it directly.
**Why it's wrong:** It skips profile/category selection, aliases, validation, caching, hooks, error normalization, and lifecycle cleanup, so transports behave differently.
**Do this instead:** Convert protocol input to the standard call shape and dispatch through `ToolUniverse.run_one_function()` in `src/tooluniverse/execute_function.py:3018`.

### Eager Catalog Imports

**What happens:** Package or server startup imports all modules under `src/tooluniverse/` or `src/tooluniverse/tools/`.
**Why it's wrong:** The catalog contains hundreds of adapters with optional scientific dependencies; eager imports increase startup cost and make unrelated missing packages fatal.
**Do this instead:** Register the implementation in `src/tooluniverse/tool_registry.py` and update/generated lazy metadata in `src/tooluniverse/_lazy_registry_static.py` using the established generation workflow.

### Embedding Schema in Transport Code

**What happens:** An MCP/REST/CLI endpoint duplicates a tool's parameter names or description.
**Why it's wrong:** The JSON definition becomes inconsistent with protocol-specific copies and schema inspection no longer predicts execution.
**Do this instead:** Keep the canonical specification under `src/tooluniverse/data/*.json` and have transports render or proxy that definition.

### Returning Ambiguous Failures

**What happens:** A tool returns `None`, `[]`, `{}`, or a raw exception for an operational failure.
**Why it's wrong:** Callers cannot distinguish failure from a legitimate empty scientific result.
**Do this instead:** Use `tool_error()` and the structured exception taxonomy in `src/tooluniverse/base_tool.py` and `src/tooluniverse/exceptions.py`.

## Error Handling

**Strategy:** Validate at the orchestration boundary, normalize known failures into structured responses, isolate optional import failures, and translate protocol-level errors at the outer adapter.

**Patterns:**
- `BaseTool.tool_error()` returns `status`, `error`, `error_type`, and optional remediation text from `src/tooluniverse/base_tool.py`.
- Typed exceptions such as `ToolValidationError`, `ToolAuthError`, `ToolRateLimitError`, and `ToolUnavailableError` live in `src/tooluniverse/exceptions.py`.
- Lazy import failures are recorded per tool by `mark_tool_unavailable()` in `src/tooluniverse/tool_registry.py`, allowing the rest of the catalog to load.
- REST converts dispatch failures to `CallMethodResponse`/HTTP errors in `src/tooluniverse/http_api_server.py`; MCP serializes errors at the FastMCP boundary in `src/tooluniverse/smcp.py`.
- `ToolUniverse.close()` in `src/tooluniverse/execute_function.py:4089` owns executor and adapter cleanup; use context/lifecycle cleanup for embedded use.

## Cross-Cutting Concerns

**Logging:** Use named loggers from `src/tooluniverse/logging_config.py`; stdio MCP launchers reconfigure logs to stderr so JSON-RPC stdout remains clean.
**Validation:** Tool arguments use JSON Schema in `src/tooluniverse/base_tool.py` and definitions under `src/tooluniverse/data/`; profiles use `src/tooluniverse/profile/validator.py`.
**Authentication:** Tool credentials come from environment/workspace configuration. Network transports use bind guards and bearer-token checks from `src/tooluniverse/server_security.py`; individual adapters handle service-specific credentials.
**Caching:** Central result behavior is provided by `src/tooluniverse/cache/`; semantic discovery artifacts are managed by `src/tooluniverse/tool_finder_embedding.py` and `src/tooluniverse/database_setup/`.
**Extensibility:** Prefer registered adapters plus JSON definitions, workspace tool files, or namespace/entry-point plugins over modifications to transport layers.

---

*Architecture analysis: 2026-08-03*
