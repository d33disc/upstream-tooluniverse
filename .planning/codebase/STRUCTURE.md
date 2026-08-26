# Codebase Structure

**Analysis Date:** 2026-08-03

## Directory Layout

```text
ToolUniverse/
├── src/tooluniverse/          # Installable Python package and runtime core
│   ├── data/                  # Packaged JSON definitions, schemas, profiles, remote configs
│   ├── tools/                 # Generated/thin per-public-tool implementation modules
│   ├── cache/                 # Memory and SQLite result caching
│   ├── profile/               # Profile loading and validation
│   ├── database_setup/        # Embedding/vector datastore pipeline and CLI
│   ├── remote/                # Deployable remote scientific workloads
│   ├── compose_scripts/       # Multi-tool research workflow implementations
│   └── *_tool.py              # Shared/backend-specific tool adapter modules
├── tests/                     # Primary pytest unit, integration, API, and tool tests
├── skills/                    # Source orchestration skills and their references/evals/scripts
├── plugin/                    # Claude/Codex plugin packaging and selected skill links
├── plugins/                   # Additional plugin distributions
├── examples/                  # Runnable usage examples grouped by domain/surface
├── docs/                      # Sphinx documentation source and developer guides
├── scripts/                   # Repository maintenance, validation, build, and release scripts
├── web/                       # Browser-facing assets/applications
├── mcpb/                      # MCP bundle packaging assets
├── data/                      # Repository-level generated/shared data artifacts
├── .github/                   # CI workflows and GitHub metadata
├── .planning/codebase/        # Generated GSD repository maps
├── pyproject.toml             # Package metadata, dependencies, entry points, tool configuration
├── uv.lock                    # Locked Python dependency graph
├── server.json                # MCP host/server manifest
└── Dockerfile                 # Container build entry
```

## Directory Purposes

**`src/tooluniverse/`:**
- Purpose: Houses the installable `tooluniverse` package and nearly all production runtime behavior.
- Contains: Core facade, registries, transport adapters, tool implementations, hooks, clients, security, data, caching, profiles, and remote workloads.
- Key files: `src/tooluniverse/execute_function.py`, `src/tooluniverse/base_tool.py`, `src/tooluniverse/tool_registry.py`, `src/tooluniverse/smcp.py`, `src/tooluniverse/cli.py`

**`src/tooluniverse/data/`:**
- Purpose: Supplies package resources that describe the catalog independently from implementation code.
- Contains: `*_tools.json` definitions, `schemas/`, `packages/`, `remote_tools/`, `broken_apis/`, and `default_profile.yaml`.
- Key files: `src/tooluniverse/data/special_tools.json`, `src/tooluniverse/data/finder_tools.json`, `src/tooluniverse/data/default_profile.yaml`, `src/tooluniverse/data/schemas/profile_schema.json`

**`src/tooluniverse/tools/`:**
- Purpose: Stores fine-grained public tool modules used by the lazy registry.
- Contains: Files named after public tool names, commonly one operation per module, plus generated metadata.
- Key files: `src/tooluniverse/tools/.tool_metadata.json`, `src/tooluniverse/tools/UniProt_get_entry_by_accession.py`

**`src/tooluniverse/cache/`:**
- Purpose: Centralizes cached tool-result storage.
- Contains: In-memory cache, SQLite backend, and coordinating result manager.
- Key files: `src/tooluniverse/cache/result_cache_manager.py`, `src/tooluniverse/cache/memory_cache.py`, `src/tooluniverse/cache/sqlite_backend.py`

**`src/tooluniverse/profile/`:**
- Purpose: Resolves and validates reusable catalog/workspace configuration.
- Contains: Local/remote profile loader and schema validators.
- Key files: `src/tooluniverse/profile/loader.py`, `src/tooluniverse/profile/validator.py`

**`src/tooluniverse/database_setup/`:**
- Purpose: Builds and queries embedding/vector-backed scientific datastores.
- Contains: CLI, pipeline, provider resolution, embedding generation, SQLite/vector stores, packaging, and Hugging Face synchronization.
- Key files: `src/tooluniverse/database_setup/cli.py`, `src/tooluniverse/database_setup/pipeline.py`, `src/tooluniverse/database_setup/vector_store.py`

**`src/tooluniverse/remote/`:**
- Purpose: Groups server-side implementations for computational tools deployed separately from the main process.
- Contains: Workload directories such as `src/tooluniverse/remote/boltz/`, `src/tooluniverse/remote/scvi/`, and `src/tooluniverse/remote/enformer/`.
- Key files: Each workload's implementation/deployment files plus matching definitions under `src/tooluniverse/data/remote_tools/`.

**`src/tooluniverse/compose_scripts/`:**
- Purpose: Implements opinionated multi-tool research workflows and tool-graph composition helpers.
- Contains: Drug discovery, safety, literature, biomarker, metadata, and graph scripts.
- Key files: `src/tooluniverse/compose_scripts/comprehensive_drug_discovery.py`, `src/tooluniverse/compose_scripts/tool_graph_composer.py`

**`tests/`:**
- Purpose: Verifies public APIs, core behavior, integrations, datastore support, and individual adapters.
- Contains: Root regression tests plus `tests/unit/`, `tests/integration/`, `tests/api/`, `tests/tools/`, `tests/examples/`, and `tests/test_database_setup/`.
- Key files: `tests/conftest.py`, `tests/unit/`, `tests/integration/`

**`skills/`:**
- Purpose: Defines the source library of research and development orchestration skills consumed by agents.
- Contains: One directory per skill with `SKILL.md`, optional `references/`, `scripts/`, `assets/`, and `evals/`.
- Key files: `skills/tooluniverse/SKILL.md`, `skills/create-tooluniverse-skill/SKILL.md`, `skills/devtu-create-tool/SKILL.md`

**`plugin/` and `plugins/`:**
- Purpose: Package ToolUniverse for agent/plugin hosts.
- Contains: Commands, agents, hooks, scripts, manifests, and skill links or distributions.
- Key files: `plugin/.claude-plugin/`, `plugin/agents/`, `plugin/commands/`, `plugin/skills/`

**`examples/`:**
- Purpose: Demonstrates embedded, MCP, HTTP, caching, agentic, and domain-specific usage.
- Contains: Standalone scripts and grouped examples such as `examples/mcp/`, `examples/compact_mode/`, `examples/remote_tools/`, and `examples/databases/`.
- Key files: `examples/README.md`, `examples/http_api_usage_example.py`, `examples/compact_mode/`

**`docs/`:**
- Purpose: Builds end-user and developer documentation.
- Contains: Sphinx configuration/RST, reference generators, API/guide sections, translations, and developer design/tutorial documents.
- Key files: `docs/conf.py`, `docs/index.rst`, `docs/dev_docs/Interaction_Surfaces.md`, `docs/dev_docs/Adding_Tools_Tutorial.md`

**`scripts/`:**
- Purpose: Provides repository-level automation for catalog generation, checks, releases, docs, and maintenance.
- Contains: Python and shell utilities; inspect an existing neighboring script before adding another.
- Key files: `scripts/` (task-specific entry points), `src/tooluniverse/scripts/` (package-adjacent graph/filter utilities)

## Key File Locations

**Entry Points:**
- `src/tooluniverse/__init__.py`: Embedded Python public exports and lazy attribute lookup.
- `src/tooluniverse/cli.py`: `tu` command-line entry point.
- `src/tooluniverse/smcp_server.py`: MCP stdio/HTTP/SSE console launchers.
- `src/tooluniverse/http_api_server_cli.py`: REST server console launcher.
- `src/tooluniverse/http_api_server.py`: FastAPI application and generic method dispatch.
- `src/tooluniverse/database_setup/cli.py`: `tu-datastore` entry point.
- `src/tooluniverse/doctor.py`: Installation/runtime diagnostics entry point.
- `pyproject.toml`: Authoritative `[project.scripts]` mapping for console commands.

**Configuration:**
- `pyproject.toml`: Project metadata, dependencies, build settings, entry points, Ruff, mypy, and pytest configuration.
- `uv.lock`: Exact dependency resolution; use `uv` and do not introduce another package manager.
- `src/tooluniverse/default_config.py`: Category-to-definition-file catalog mapping.
- `src/tooluniverse/data/default_profile.yaml`: Seed profile for workspaces.
- `src/tooluniverse/data/schemas/`: Packaged validation schemas.
- `server.json`: MCP server registration manifest.
- `.env.template`: Documented environment-variable names; never place secrets in tracked files.
- `.pre-commit-config.yaml`: Repository commit-time checks.
- `.markdownlint.json`: Markdown lint behavior.
- `Dockerfile`: Container packaging.

**Core Logic:**
- `src/tooluniverse/execute_function.py`: `ToolUniverse` facade and execution pipeline.
- `src/tooluniverse/base_tool.py`: Shared tool contract, defaults, validation, and structured errors.
- `src/tooluniverse/tool_registry.py`: Decorator/config registry and lazy plugin discovery.
- `src/tooluniverse/_lazy_registry_static.py`: Generated public-name-to-module map.
- `src/tooluniverse/smcp.py`: FastMCP integration and compact proxy surface.
- `src/tooluniverse/tool_finder_keyword.py`: Deterministic keyword/BM25 discovery.
- `src/tooluniverse/tool_finder_embedding.py`: Semantic discovery.
- `src/tooluniverse/output_hook.py`: Output-processing pipeline.
- `src/tooluniverse/server_security.py`: Network bind and token policies.

**Testing:**
- `tests/unit/`: Fast isolated tests for core components.
- `tests/integration/`: Cross-component and dependency-aware tests.
- `tests/api/`: Public API/transport behavior.
- `tests/tools/`: Tool-specific behavior and regression coverage.
- `tests/test_database_setup/`: Datastore pipeline/store behavior.
- `tests/examples/`: Executable example validation.
- `src/tooluniverse/test/`: Package-local tests retained alongside runtime sources; prefer `tests/` for new general coverage unless matching an established package-local suite.

**Documentation and Examples:**
- `docs/dev_docs/Interaction_Surfaces.md`: Canonical connection/discovery map.
- `docs/dev_docs/Adding_Tools_Tutorial.md`: Tool contribution path.
- `docs/dev_docs/Embedding_Search.md`: Semantic index behavior.
- `docs/dev_docs/MCP_Server_Tutorial.md`: MCP deployment/configuration.
- `examples/`: Surface- and domain-specific executable demonstrations.

## Naming Conventions

**Files:**
- Runtime modules use lowercase snake case: `src/tooluniverse/tool_registry.py`, `src/tooluniverse/http_api_server.py`.
- Backend families usually end in `_tool.py`: `src/tooluniverse/uniprot_tool.py`, `src/tooluniverse/openfda_tool.py`.
- Catalog definitions usually end in `_tools.json`: `src/tooluniverse/data/uniprot_tools.json`.
- Fine-grained lazy tool modules mirror the public tool name and may use mixed/provider capitalization: `src/tooluniverse/tools/UniProt_get_entry_by_accession.py`.
- Tests begin with `test_` and should mirror the component or behavior: `tests/unit/test_<component>.py`, `tests/tools/test_<provider>.py`.
- Skills use kebab-case directories with an uppercase `SKILL.md`: `skills/tooluniverse-variant-interpretation/SKILL.md`.

**Directories:**
- Python packages use lowercase snake case: `src/tooluniverse/database_setup/`, `src/tooluniverse/compose_scripts/`.
- Domain skill/plugin directories use kebab case: `skills/tooluniverse-admet-prediction/`.
- Test grouping uses lowercase functional categories: `tests/unit/`, `tests/integration/`, `tests/api/`, `tests/tools/`.

## Where to Add New Code

**New Scientific API or Tool Family:**
- Primary adapter: `src/tooluniverse/<provider>_tool.py` when several public operations share a client/implementation.
- Tool definitions: `src/tooluniverse/data/<provider>_tools.json`.
- Catalog category: Add the definition path to `src/tooluniverse/default_config.py` when it belongs in the built-in catalog.
- Registration/lazy discovery: Follow `docs/dev_docs/Adding_Tools_Tutorial.md` and regenerate `src/tooluniverse/_lazy_registry_static.py`; do not hand-build transport endpoints.
- Tests: `tests/tools/test_<provider>_tool.py` for provider behavior and `tests/integration/test_<provider>_integration.py` only when live/cross-component coverage is necessary.
- Example: `examples/<provider>_example.py` when users need a workflow beyond test coverage.

**New Fine-Grained Generated Tool:**
- Implementation: `src/tooluniverse/tools/<PublicToolName>.py` using the existing generated/thin-module convention.
- Metadata: Update through the repository's generation workflow affecting `src/tooluniverse/tools/.tool_metadata.json` and `src/tooluniverse/_lazy_registry_static.py`, not by creating inconsistent manual mappings.
- Tests: Match the generator or provider suite under `tests/tools/`.

**New Core Feature:**
- Public lifecycle/discovery/execution behavior: `src/tooluniverse/execute_function.py`.
- Reusable adapter behavior: `src/tooluniverse/base_tool.py` or a focused sibling helper in `src/tooluniverse/`.
- Registry/plugin behavior: `src/tooluniverse/tool_registry.py`.
- Tests: Start in `tests/unit/test_<feature>.py`; add `tests/integration/` coverage only for multi-layer behavior.
- Keep `src/tooluniverse/__init__.py` limited to stable exports and lazy/optional integration setup.

**New Connection Surface Behavior:**
- MCP protocol: `src/tooluniverse/smcp.py`; launcher flags only in `src/tooluniverse/smcp_server.py`.
- REST protocol: `src/tooluniverse/http_api_server.py`; process/CLI flags in `src/tooluniverse/http_api_server_cli.py`.
- Shell commands: `src/tooluniverse/cli.py`.
- HTTP client behavior: `src/tooluniverse/http_client.py`.
- Tests: `tests/api/` for protocol contracts and `tests/unit/` for isolated helpers.
- Always delegate scientific execution to `src/tooluniverse/execute_function.py`.

**New Discovery Strategy:**
- Implementation: `src/tooluniverse/tool_finder_<strategy>.py`.
- Public tool configuration: `src/tooluniverse/data/finder_tools.json` if exposed as a catalog tool.
- MCP/CLI wiring: Reuse the discovery proxy boundary in `src/tooluniverse/smcp.py` and `src/tooluniverse/cli.py`.
- Tests: `tests/unit/test_tool_finder_<strategy>.py` plus targeted integration coverage for index/provider dependencies.

**New Profile or Workspace Behavior:**
- Loading/resolution: `src/tooluniverse/profile/loader.py` and the workspace boundary in `src/tooluniverse/execute_function.py`.
- Validation: `src/tooluniverse/profile/validator.py` and the matching schema under `src/tooluniverse/data/schemas/`.
- Tests: `tests/unit/` for validation/resolution and `tests/integration/` for remote profile sources.

**New Cache Backend:**
- Implementation: `src/tooluniverse/cache/<backend>.py`.
- Coordination: `src/tooluniverse/cache/result_cache_manager.py`.
- Tests: `tests/unit/test_<backend>_cache.py` or the closest existing cache suite.

**New Remote Computational Tool:**
- Service implementation/deployment: `src/tooluniverse/remote/<workload>/`.
- Client-facing definition: `src/tooluniverse/data/remote_tools/<workload>_tools.json`.
- Local adapter/registration: Follow the closest existing workload such as `src/tooluniverse/remote/boltz/` and its catalog definition.
- Tests: Isolated client tests under `tests/tools/`; mark live deployment checks as integration tests.

**New Multi-Tool Workflow:**
- Runtime composition: `src/tooluniverse/compose_scripts/<workflow>.py` when it is Python orchestration.
- Agent-facing reusable procedure: `skills/tooluniverse-<workflow>/SKILL.md` with optional `references/`, `scripts/`, and `evals/`.
- Tests/evaluations: `tests/` for Python behavior; `<skill>/evals/` for skill quality.

**Utilities:**
- Shared runtime helpers: Add a focused module under `src/tooluniverse/` only when multiple production components use it; prefer existing modules such as `src/tooluniverse/utils.py`, `src/tooluniverse/logging_config.py`, and `src/tooluniverse/server_security.py`.
- Repository automation: `scripts/`.
- Package-specific graph/filter automation shipped with the package: `src/tooluniverse/scripts/`.

## Special Directories

**`.tooluniverse/`:**
- Purpose: Repository-local ToolUniverse workspace containing profile/environment setup and user tool/config inputs.
- Generated: Partly; runtime may seed `profile.yaml` and local state.
- Committed: Selected templates/documentation may be committed; secret-bearing `.env` content must not be read or committed.

**`.planning/codebase/`:**
- Purpose: Stores generated codebase maps used by GSD planning/execution commands.
- Generated: Yes.
- Committed: Repository policy determines tracking; treat files as generated planning artifacts.

**`src/tooluniverse/data/`:**
- Purpose: Package resources installed with ToolUniverse.
- Generated: Mixed; many definitions are authored, while indexes/metadata may be generated.
- Committed: Yes for required package resources.

**`src/tooluniverse/tools/`:**
- Purpose: Lazy per-tool modules and metadata.
- Generated: Largely generated or mechanically maintained.
- Committed: Yes.

**`plugin/skills/`:**
- Purpose: Exposes selected source skills through plugin packaging.
- Generated: Mixed; preflight detects multiple symlinks here.
- Committed: Plugin manifests/links are repository assets; preserve symlink targets and avoid recursive writes through them.

**`.venv/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`:**
- Purpose: Local interpreter and tool caches.
- Generated: Yes.
- Committed: No; never add production code or durable artifacts here.

**`docs/` generated artifacts:**
- Purpose: Sphinx source plus some generated doctrees/reference outputs.
- Generated: Mixed.
- Committed: Follow existing file-specific practice; place authored docs in the source hierarchy and use existing generators for derived references.

---

*Structure analysis: 2026-08-03*
