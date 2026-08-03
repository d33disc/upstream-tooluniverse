# External Integrations

**Analysis Date:** 2026-08-03

## APIs & External Services

**LLM and model providers:**
- OpenAI and Azure OpenAI - agentic tools, summarization, composition, and embedding workflows.
  - SDK/Client: `openai`, wrapped by `src/tooluniverse/llm_clients.py` and used by `src/tooluniverse/agentic_tool.py`.
  - Auth: `OPENAI_API_KEY`; Azure uses `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, and optional API-version/model-limit variables.
- Google Gemini - generative model execution through `google-genai` in `src/tooluniverse/llm_clients.py`.
  - SDK/Client: `google-genai`.
  - Auth: `GEMINI_API_KEY`.
- OpenRouter, DeepSeek, and local Ollama - OpenAI-compatible or local model alternatives in `src/tooluniverse/llm_clients.py`.
  - SDK/Client: provider-specific HTTP/OpenAI-compatible clients.
  - Auth: `OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`; Ollama uses `OLLAMA_SERVER_URL` and normally no secret.
- Hugging Face - model/dataset downloads, profile loading, Spaces, and embeddings in `src/tooluniverse/profile.py`, `src/tooluniverse/database_setup/embedder.py`, and `src/tooluniverse/huggingface_tool.py`.
  - SDK/Client: `huggingface_hub`; optional `sentence-transformers`.
  - Auth: `HF_TOKEN` for gated or authenticated resources.
- NVIDIA NIM - hosted biology inference including Evo2 and structure workflows in `src/tooluniverse/evo2_variant_effect_tool.py`, `src/tooluniverse/nvidia_nim_tool.py`, and related NVIDIA adapters.
  - SDK/Client: HTTP via `requests`/`aiohttp`.
  - Auth: `NVIDIA_API_KEY`.

**Literature, search, and knowledge:**
- NCBI/PubMed, Europe PMC, Crossref, OpenAlex, Semantic Scholar, arXiv/bioRxiv, CORE, and Unpaywall - publication search, citations, metadata, retractions, and full text through adapters such as `src/tooluniverse/pubmed_tool.py`, `src/tooluniverse/europe_pmc_tool.py`, `src/tooluniverse/crossref_tool.py`, and `src/tooluniverse/semantic_scholar_tool.py`.
  - SDK/Client: REST/XML clients built on `requests`, `aiohttp`, `xmltodict`, `lxml`, and `beautifulsoup4`.
  - Auth: mostly public; higher limits or gated services use `NCBI_API_KEY`, `SEMANTIC_SCHOLAR_API_KEY`, and `CORE_API_KEY` as catalogued in `src/tooluniverse/config_env.py`.
- Tavily, Jina, Exa, Brave Search, DDGS, and Zotero - general search, web reading, and citation-library access in `src/tooluniverse/*_tool.py` and `src/tooluniverse/config_env.py`.
  - SDK/Client: REST clients and `ddgs`.
  - Auth: `TAVILY_API_KEY`, `JINA_API_KEY`, `EXA_API_KEY`, `BRAVE_API_KEY`, and `ZOTERO_API_KEY` where required.

**Biomedical and scientific data:**
- NCBI resources, UniProt, Ensembl, RCSB PDB, PDBe/EBI, Reactome, ClinVar, GTEx, CELLxGENE, HuBMAP, MGnify, and many other public scientific services - core scientific retrieval across dedicated adapters such as `src/tooluniverse/uniprot_tool.py`, `src/tooluniverse/ensembl_tool.py`, `src/tooluniverse/rcsb_pdb_tool.py`, `src/tooluniverse/reactome_analysis_tool.py`, and `src/tooluniverse/cellxgene_discovery_tool.py`.
  - SDK/Client: primarily declarative JSON in `src/tooluniverse/data/*_tools.json` plus `requests`/`aiohttp`; specialist clients include `rcsb-api`, `graphql-core`, and optional `cellxgene-census`.
  - Auth: most are public; optional/required keys are isolated per adapter.
- BRENDA, OMIM, BioGRID, DisGeNET, CLUE, Addgene, OncoKB, MCule, PharmVar, OpenFDA, USPTO, WHO ICD-11, and Alpha Vantage - authenticated specialist databases catalogued in `src/tooluniverse/config_env.py` and represented by corresponding `src/tooluniverse/*_tool.py` modules.
  - SDK/Client: REST/GraphQL adapters.
  - Auth: `BRENDA_EMAIL` and `BRENDA_PASSWORD`, `OMIM_API_KEY`, `BIOGRID_ACCESS_KEY`/`BIOGRID_API_KEY`, `DISGENET_API_KEY`, `CLUE_API_KEY`, `ADDGENE_API_KEY`, `ONCOKB_API_TOKEN`, `MCULE_API_KEY`, `PHARMVAR_API_KEY`, `FDA_API_KEY`, `USPTO_API_KEY`, ICD client variables, and `ALPHA_VANTAGE_API_KEY`.

**Protocol and distribution:**
- Model Context Protocol hosts - Claude Desktop/Code and other MCP clients connect over stdio or streamable HTTP through `src/tooluniverse/smcp.py`, `src/tooluniverse/smcp_server.py`, and `server.json`.
  - SDK/Client: `mcp` and `fastmcp`.
  - Auth: local stdio needs none; network binds use server security controls in `src/tooluniverse/server_security.py`.
- PyPI and GitHub - Python distribution, source hosting, plugin releases, issue/PR automation, and SDK metadata in `pyproject.toml`, `server.json`, and `.github/workflows/`.
  - SDK/Client: `uv`/pip, GitHub Actions, and `gh` in release workflows.
  - Auth: CI-scoped `GITHUB_TOKEN`; package publication credentials are managed outside source.

## Data Storage

**Databases:**
- SQLite with FTS5 - local document metadata, full-text search, vector bookkeeping, and cached tool results.
  - Connection: filesystem paths passed to `SQLiteStore` and `PersistentCache`; cache paths derive from `TOOLUNIVERSE_CACHE_PATH` or `TOOLUNIVERSE_CACHE_DIR` in `src/tooluniverse/execute_function.py`.
  - Client: Python `sqlite3` in `src/tooluniverse/database_setup/sqlite_store.py` and `src/tooluniverse/cache/sqlite_backend.py`.
- FAISS indexes - per-collection local vector indexes paired with SQLite metadata.
  - Connection: local index paths managed by `src/tooluniverse/database_setup/vector_store.py` and `src/tooluniverse/database_setup/embedding_database.py`.
  - Client: `faiss-cpu==1.12.0`.

**File Storage:**
- Local filesystem for tool definitions, profiles, generated SDK wrappers, downloads, reports, SQLite databases, FAISS indexes, and hook outputs; relevant paths are managed in `src/tooluniverse/execute_function.py`, `src/tooluniverse/profile.py`, and `src/tooluniverse/hooks/`.
- Hugging Face repositories can act as remote profile/config sources through `hf:` URIs in `src/tooluniverse/profile.py` and `src/tooluniverse/smcp_server.py`.

**Caching:**
- In-process LRU plus single-flight suppression and optional SQLite persistence in `src/tooluniverse/cache/memory_cache.py`, `src/tooluniverse/cache/result_cache_manager.py`, and `src/tooluniverse/cache/sqlite_backend.py`.
- Configure with `TOOLUNIVERSE_CACHE_ENABLED`, `TOOLUNIVERSE_CACHE_PERSIST`, `TOOLUNIVERSE_CACHE_MEMORY_SIZE`, `TOOLUNIVERSE_CACHE_DEFAULT_TTL`, `TOOLUNIVERSE_CACHE_SINGLEFLIGHT`, `TOOLUNIVERSE_CACHE_ASYNC_PERSIST`, `TOOLUNIVERSE_CACHE_PATH`, and `TOOLUNIVERSE_CACHE_DIR`.

## Authentication & Identity

**Auth Provider:**
- Environment-variable credentials per external service; there is no central user identity provider.
  - Implementation: `src/tooluniverse/config_env.py` inventories credential names/status, while each adapter reads only its provider variables; missing keys cause tools to skip or report configuration errors.
- Bearer-token protection for network-exposed ToolUniverse servers.
  - Implementation: `src/tooluniverse/server_security.py` validates `TOOLUNIVERSE_API_TOKEN`; middleware in `src/tooluniverse/http_api_server.py` protects all routes except `/health` and refuses unsafe non-loopback binding without a token.

## Monitoring & Observability

**Error Tracking:**
- No hosted error-tracking SDK detected; exceptions and structured tool errors stay in process or CI artifacts.

**Logs:**
- Python `logging` is centralized in `src/tooluniverse/logging_config.py`; stdio mode redirects logs away from MCP JSON-RPC stdout in `src/tooluniverse/smcp_server.py`.
- Runtime verbosity is controlled by `TOOLUNIVERSE_LOG_LEVEL`; `Dockerfile` defaults it to `WARNING`.
- Scheduled live-service health reports run from `.github/workflows/tool-health.yml` and `.github/workflows/weekly-tool-healthcheck.yml`, using `scripts/tool_health_check.py` and `scripts/test_all_tools.py`.
- Coverage is uploaded to Codecov by `.github/workflows/tests.yml`; failure is non-blocking.

## CI/CD & Deployment

**Hosting:**
- PyPI package and MCP registry entry defined by `pyproject.toml` and `server.json`.
- Docker-compatible stdio MCP process defined by `Dockerfile`; HTTP MCP and REST services run via console scripts declared in `pyproject.toml`.
- GitHub Pages documentation deployed by `.github/workflows/deploy-docs.yml`.
- GitHub Releases distribute Claude/Codex plugin bundles via `.github/workflows/auto-release.yml`, `.github/workflows/release-plugin.yml`, and scripts under `scripts/`.

**CI Pipeline:**
- GitHub Actions runs Python 3.12 linting, SDK generation, parallel pytest, coverage, release automation, docs deployment, upstream synchronization, and scheduled external-API health checks under `.github/workflows/`.
- Core tests avoid slow, network, GPU, and API-key cases by default according to `pytest.ini` and `.github/workflows/tests.yml`; live integrations run separately on scheduled/manual workflows.

## Environment Configuration

**Required env vars:**
- Core local/stdio operation requires no external credential; external tools activate according to provider-specific keys.
- Server controls: `TOOLUNIVERSE_API_TOKEN`, `TOOLUNIVERSE_HTTP_HOST`, `TOOLUNIVERSE_THREAD_POOL_SIZE`, `TOOLUNIVERSE_HOME`, `TOOLUNIVERSE_LOG_LEVEL`, and `TOOLUNIVERSE_CACHE_*` in `src/tooluniverse/http_api_server.py`, `src/tooluniverse/smcp_server.py`, and `src/tooluniverse/execute_function.py`.
- LLM/model credentials: `OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `HF_TOKEN`, and `NVIDIA_API_KEY` in `src/tooluniverse/llm_clients.py` and `src/tooluniverse/config_env.py`.
- Scientific/search credentials are catalogued by name in `src/tooluniverse/config_env.py` and MCP-facing essentials are listed in `server.json`; use `tu status` to inspect which integrations are configured.

**Secrets location:**
- Secrets are supplied through process/CI environment variables; `.env` and `.tooluniverse/.env.1password` are present as local configuration mechanisms but their contents are intentionally not read or documented.
- Templates exist at `.env.template`, `src/tooluniverse/.env.template`, `docs/.env.template`, and selected `skills/*/.env.template`; never commit populated values.
- GitHub Actions reads repository secrets through expressions in workflows such as `.github/workflows/weekly-tool-healthcheck.yml`.

## Webhooks & Callbacks

**Incoming:**
- No third-party webhook receiver is detected.
- Interactive network endpoints include FastAPI method calls and health routes in `src/tooluniverse/http_api_server.py`, streamable HTTP MCP in `src/tooluniverse/smcp_server.py`, and local expert-feedback request/response endpoints in `src/tooluniverse/remote/expert_feedback/human_expert_mcp_tools.py`.

**Outgoing:**
- No application-level webhook emitter is detected; tools make direct REST/GraphQL requests to provider APIs.
- CI creates/releases GitHub resources and comments on health/upstream-sync PRs through workflow-scoped GitHub APIs in `.github/workflows/auto-release.yml`, `.github/workflows/tool-health.yml`, and `.github/workflows/sync-upstream.yml`.

---

*Integration audit: 2026-08-03*
