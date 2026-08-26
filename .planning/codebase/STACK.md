# Technology Stack

**Analysis Date:** 2026-08-03

## Languages

**Primary:**
- Python 3.10+ - Package, CLI, MCP/HTTP servers, scientific tool adapters, indexing, and tests under `src/tooluniverse/`, `scripts/`, and `tests/`; CI and the container standardize on Python 3.12 in `.github/workflows/tests.yml` and `Dockerfile`.

**Secondary:**
- JSON - Declarative definitions for 2,500+ tools in `src/tooluniverse/data/*.json`, MCP metadata in `server.json`, and plugin manifests under `plugin/`.
- Markdown/reStructuredText - Skills and product documentation in `skills/*/SKILL.md`, `docs/`, `README.md`, and `wiki/`.
- Shell - Build, release, plugin synchronization, and integration checks in `scripts/*.sh`, `plugin/*.sh`, `mcpb/build.sh`, and `tests/e2e_claude_code.sh`.
- HTML/CSS/JavaScript - Embedded local web interfaces and graph visualizations in `src/tooluniverse/remote/expert_feedback/human_expert_mcp_tools.py` and `src/tooluniverse/tool_graph_web_ui.py`.

## Runtime

**Environment:**
- CPython >=3.10 - Declared in `pyproject.toml`; Python 3.12 is the supported CI/container runtime in `.github/workflows/tests.yml`, `.github/workflows/tool-health.yml`, and `Dockerfile`.
- Linux is the production/CI baseline - GitHub Actions uses Ubuntu and `Dockerfile` uses `python:3.12-slim`; local development is also supported on macOS through the pure-Python package and platform guidance in `src/tooluniverse/database_setup/sqlite_store.py`.

**Package Manager:**
- uv 0.12.x locally, with `uv` used by CI - Dependency resolution is locked by `uv.lock`; packaging uses setuptools through `pyproject.toml`.
- Lockfile: `uv.lock` present.

## Frameworks

**Core:**
- FastMCP >=3.4.5,<4.0.0 and MCP >=1.29.0,<2.0.0 - stdio and streamable-HTTP Model Context Protocol surfaces implemented in `src/tooluniverse/smcp.py` and launched by `src/tooluniverse/smcp_server.py`.
- FastAPI >=0.116.0, Uvicorn >=0.36.0, and Pydantic >=2.11.0 - typed REST service and request/response models in `src/tooluniverse/http_api_server.py` and `src/tooluniverse/http_api_server_cli.py`.
- Requests >=2.32.0 and aiohttp - synchronous and asynchronous HTTP access across tool adapters such as `src/tooluniverse/base_rest_tool.py` and `src/tooluniverse/async_base.py`.
- Flask >=2.0.0 - lightweight local visualization and specialist web services such as `src/tooluniverse/tool_graph_web_ui.py`.

**Testing:**
- pytest >=7.0 - unit, integration, API, tool, and database suites configured by `pytest.ini`.
- pytest-cov >=4.0, pytest-asyncio >=0.21.0, pytest-xdist >=3.0, pytest-mock >=3.14.0, and requests-mock >=1.12.1 - coverage, async, parallel, and HTTP test support declared in `pyproject.toml`.

**Build/Dev:**
- setuptools + wheel - PEP 517 build backend declared in `pyproject.toml` and `mcpb/pyproject.toml`.
- Ruff >=0.14.5 - linting/format checks configured in `pyproject.toml`; CI pins Ruff 0.15.22 in `.github/workflows/tests.yml`.
- mypy targeting Python 3.12 - incremental type checking configured in `pyproject.toml`.
- Sphinx with Furo, Shibuya, MyST, and related extensions - documentation build configured in `docs/conf.py`, `docs/requirements.txt`, and `docs/Makefile`.
- Docker - slim Python image for the stdio MCP deployment in `Dockerfile`.

## Key Dependencies

**Critical:**
- `fastmcp` and `mcp` - Shared MCP protocol runtime for compact proxy tools and the complete backend registry in `src/tooluniverse/smcp.py`.
- `fastapi`, `uvicorn`, and `pydantic` - REST transport, schema validation, and OpenAPI generation in `src/tooluniverse/http_api_server.py`.
- `requests`, `aiohttp`, `graphql-core`, `xmltodict`, `lxml`, and `beautifulsoup4` - REST, GraphQL, XML, and HTML integration primitives used throughout `src/tooluniverse/*_tool.py`.
- `numpy`, `pandas`, `sympy`, `networkx`, and `epam.indigo` - numerical, tabular, symbolic, graph, and cheminformatics foundations used by scientific tools under `src/tooluniverse/`.
- `openai` and `google-genai` - hosted LLM clients implemented in `src/tooluniverse/llm_clients.py`; additional providers use OpenAI-compatible HTTP interfaces there.
- `faiss-cpu==1.12.0` and `huggingface_hub` - semantic tool discovery and persisted vector search in `src/tooluniverse/database_setup/vector_store.py`, `src/tooluniverse/database_setup/embedder.py`, and `src/tooluniverse/tool_finder_embedding.py`.

**Infrastructure:**
- SQLite from the Python standard library, including FTS5 - local document index and persistent result cache in `src/tooluniverse/database_setup/sqlite_store.py` and `src/tooluniverse/cache/sqlite_backend.py`.
- Playwright >=1.55.0 - browser-backed retrieval tools under `src/tooluniverse/`.
- MarkItDown with all converters, pdfplumber, PyMuPDF-compatible `fitz`, lxml, and openpyxl - document, PDF, XML, and spreadsheet ingestion in `src/tooluniverse/unified_guideline_tools.py` and related adapters.
- `sentence-transformers`, RDKit, Biopython, CellxGene Census, TileDB-SOMA, ADMET-AI, plotting, and structural-biology packages - opt-in domains grouped under `[project.optional-dependencies]` in `pyproject.toml`.

## Configuration

**Environment:**
- Configure credentials and runtime switches with environment variables; discovery/status lives in `src/tooluniverse/config_env.py`, while individual adapters read only their required variables.
- `.env`, `.env.template`, `src/tooluniverse/.env.template`, and specialist templates exist, but secret-bearing contents are not part of this analysis. `python-dotenv` is declared in `pyproject.toml` for local loading.
- Common runtime controls include `TOOLUNIVERSE_HOME`, `TOOLUNIVERSE_CACHE_*`, `TOOLUNIVERSE_API_TOKEN`, `TOOLUNIVERSE_HTTP_HOST`, `TOOLUNIVERSE_THREAD_POOL_SIZE`, and `TOOLUNIVERSE_LOG_LEVEL`, implemented in `src/tooluniverse/execute_function.py`, `src/tooluniverse/http_api_server.py`, and `src/tooluniverse/logging_config.py`.

**Build:**
- `pyproject.toml` is the canonical package, dependency, entry-point, Ruff, and mypy configuration.
- `uv.lock` pins the resolved Python dependency graph; do not introduce a second root package manager.
- `server.json` is the Model Context Protocol registry manifest; `mcpb/pyproject.toml` and `mcpb/manifest.json` define the native MCP bundle.
- `Dockerfile` installs the published PyPI package and launches `tooluniverse-smcp-stdio`.

## Platform Requirements

**Development:**
- Use Python 3.12 with `uv` and the `dev` dependency group from `pyproject.toml`; SQLite must include FTS5 for hybrid search in `src/tooluniverse/database_setup/sqlite_store.py`.
- Native scientific libraries may require compilers, BLAS/LAPACK, Graphviz, image/PDF libraries, and browser assets; the complete Ubuntu set is installed in `.github/workflows/tests.yml`.
- Generate typed SDK wrappers from declarative definitions with `python scripts/build_tools.py`; CI caches generated files under `src/tooluniverse/tools/`.

**Production:**
- Publishable Python package on PyPI, declared by `pyproject.toml` and registered through `server.json` for `uvx` stdio execution.
- Containerized stdio MCP server on Python 3.12 slim via `Dockerfile`; streamable HTTP MCP and FastAPI REST are alternate processes exposed by scripts in `pyproject.toml`.
- GitHub Pages hosts Sphinx documentation through `.github/workflows/deploy-docs.yml`.

---

*Stack analysis: 2026-08-03*
