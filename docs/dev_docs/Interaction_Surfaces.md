# ToolUniverse — Interaction Surfaces

How an outside codebase, agent, or human reaches into ToolUniverse and pulls
information together iteratively.

ToolUniverse exposes **~2,300 scientific tools across ~510 categories**,
**~134 orchestration skills**, and **~10 entry points**. The point of this
document is to make every entry point and every layer findable from one page.

---

## TL;DR — The 5 Discovery Entry Points

Outside agents converge on these five primitives regardless of transport
(MCP, HTTP, Python, CLI):

| # | Entry              | Backend                            | Best for                                                |
|---|--------------------|------------------------------------|---------------------------------------------------------|
| 1 | `grep_tools`       | `tool_finder_keyword.py` (BM25)    | exact strings, regex, deterministic, no GPU             |
| 2 | `find_tools`       | `tool_finder_embedding.py` (FAISS) | semantic / natural language; needs embeddings cache     |
| 3 | `list_tools`       | registry enumeration               | browse categories, count, paginate                      |
| 4 | `get_tool_info`    | schema introspection               | exact parameter schema before any call                  |
| 5 | `execute_tool`     | `execute_function.py`              | run any of the ~2,300 backend tools                     |

The reasoning layer above this is `tu-llm` (skill `/tu-llm`) and the
`Tool_Finder_LLM` agentic tool — both decide *which combination* of tools
answers a multi-hop question.

**Rule:** never skip step 4. Parameter names drift across tools
(`query` vs `search_keywords`, `limit` vs `max_results`).

---

## 1 — Connection Surfaces (How You Connect In)

Six ways to reach the same ToolUniverse instance. Pick by deployment context.

- **Python SDK** — `from tooluniverse import ToolUniverse` (in-process).
  Embed in scripts, notebooks, agent frameworks.
- **MCP stdio** — `tooluniverse` / `tooluniverse-smcp-stdio` (JSON-RPC
  stdio). Claude Desktop, Claude Code, MCP host integrations.
- **MCP HTTP** — `tooluniverse-mcp` / `tooluniverse-smcp-server`
  (streamable-http). Remote or containerised MCP hosts.
- **REST API** — `tooluniverse-http-api` (FastAPI HTTP+JSON).
  Language-agnostic services, curl, web clients.
- **CLI (`tu`)** — `tu` (shell). Humans, shell scripts, CI.
- **HTTP client lib** — `from tooluniverse import ToolUniverseClient`
  (HTTP wrapper). Python apps talking to a remote REST server.
- **smolagents** — `tooluniverse.smolagent_tool.SmolagentsTool`
  (adapter). Wire TU tools into the smolagents agent framework.

All console scripts come from `pyproject.toml [project.scripts]`.

### 1.1 — Python SDK (in-process)

`src/tooluniverse/execute_function.py` defines the `ToolUniverse` class. Public
surface, grouped:

#### Lifecycle

- `ToolUniverse(tool_files=..., profile=..., workspace=..., hooks=...)`
- `load_tools(categories=None, exclude_tools=None, python_files=None)`
  — glob filtering supported
- `load_profile()`, `refresh_tools()`, `clear_tools()`, `clear_cache()`,
  `init_tool()`, `close()`

#### Discovery

- `list_built_in_tools()`, `get_available_tools()`, `find_tools_by_pattern(pat)`
- `tool_specification(name)` — full JSON schema
- `get_tool_by_name(name)`, `get_tool_description(name)`, `get_required_parameters(name)`

#### Execution

- `run_one_function(function_call_json, stream_callback=None, use_cache=False, validate=True)`
- `run(fcall_str, return_message=False, ...)` — accepts string or dict
- `check_function_call(fc)` — validate without executing

#### Inspection / state

- `prepare_tool_prompts()`, `filter_tools()`, `select_tools()`, `export_tool_names()`
- `get_cache_stats()`, `toggle_hooks()`

Outside-codebase quickstart:

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools(categories=["uniprot", "ChEMBL"])
spec = tu.tool_specification("UniProt_get_entry_by_accession")
result = tu.run_one_function({
    "name": "UniProt_get_entry_by_accession",
    "arguments": {"accession": "P05067"},
})

# Equivalent attribute-access form (ToolProxy under the hood)
tu.tools.UniProt_get_entry_by_accession(accession="P05067")

# Batch (parallel within the worker pool)
tu.run([
    {"name": "UniProt_get_entry_by_accession", "arguments": {"accession": "P05067"}},
    {"name": "ChEMBL_get_molecule",            "arguments": {"chembl_id": "CHEMBL25"}},
])

# Register your own Python function as a tool (extension point)
tu.register_custom_tool("my_local_op", my_python_function)

tu.close()
```

### 1.2 — MCP servers

`src/tooluniverse/smcp_server.py`:

| Console script             | Function                          | Transport       | Default          |
|----------------------------|-----------------------------------|-----------------|------------------|
| `tooluniverse`             | `run_default_stdio_server` (1016) | stdio + compact | stdin/stdout     |
| `tooluniverse-smcp-stdio`  | `run_stdio_server` (190)          | stdio           | stdin/stdout     |
| `tooluniverse-smcp`        | `run_smcp_server` (628)           | http/stdio/sse  | `0.0.0.0:7000`   |
| `tooluniverse-smcp-server` | `run_http_server` (53)            | streamable-http | `127.0.0.1:8000` |
| `tooluniverse-mcp`         | `run_http_server` (alias)         | streamable-http | `127.0.0.1:8000` |

Flags: `--compact-mode`, `--transport {stdio,http,sse}`, `--host`, `--port`,
`--categories`, `--load`, `--workspace` / `--global`.

Beyond the standard MCP `tools/list`, `tools/call`, `resources/list`,
`prompts/list` methods, the SMCP server adds an **async task family** for
long-running tools: `tasks/get`, `tasks/list`, `tasks/cancel`, `tasks/result`
(see `src/tooluniverse/smcp.py:806-827`). Outside agents can fire-and-poll
instead of blocking on multi-minute calls.

In **compact mode** (default for `tooluniverse`) only the 4 proxy tools
(`list_tools`, `grep_tools`, `get_tool_info`, `execute_tool`) are exposed at
the MCP protocol level — backend tools stay loaded and reachable via
`execute_tool`. A 5th, `find_tools`, is registered when the `tool_finder`
category is included.

Manifest: `server.json` (`io.github.mims-harvard/tooluniverse`, runtime `uvx`,
default args `tooluniverse-smcp-stdio --compact-mode`).

Connect from Claude Desktop / Claude Code:

```json
{ "mcpServers": {
  "tooluniverse": { "command": "uvx",
    "args": ["tooluniverse-smcp-stdio", "--compact-mode"] } } }
```

```bash
claude mcp add tooluniverse
```

### 1.3 — HTTP REST API

`src/tooluniverse/http_api_server.py` is a FastAPI app that introspects
`ToolUniverse` and exposes **every public method** through one generic POST.

| Method | Route          | Purpose                                              |
|--------|----------------|------------------------------------------------------|
| GET    | `/`            | server info                                          |
| GET    | `/health`      | tools count + status                                 |
| GET    | `/api/methods` | list every callable method with its signature        |
| POST   | `/api/call`    | `{method: str, kwargs: dict}` — call any TU method   |
| POST   | `/api/reset`   | re-initialise the ToolUniverse instance              |

Run: `tooluniverse-http-api --host 0.0.0.0 --port 8080`.

```bash
curl -X POST http://localhost:8080/api/call \
  -H 'Content-Type: application/json' \
  -d '{"method":"run_one_function","kwargs":{"function_call_json":{
        "name":"UniProt_get_entry_by_accession",
        "arguments":{"accession":"P05067"}}}}'
```

### 1.4 — `ToolUniverseClient` (Python over HTTP)

`src/tooluniverse/http_client.py` mirrors **every** ToolUniverse method through
`__getattr__` magic — no manual updates required.

```python
from tooluniverse import ToolUniverseClient
c = ToolUniverseClient("http://localhost:8080")
c.load_tools(tool_type=["uniprot"])
c.run_one_function({"name": "UniProt_get_entry_by_accession",
                    "arguments": {"accession": "P05067"}})
c.list_available_methods(); c.health_check(); c.reset_server({})
```

### 1.5 — CLI (`tu`)

`src/tooluniverse/cli.py`. Mirrors compact-mode MCP plus operational commands.

| Subcommand  | Purpose                                                          |
|-------------|------------------------------------------------------------------|
| `tu list`   | list tools — modes: names / categories / by_category / summary   |
| `tu grep`   | text or regex search (`--field`, `--mode`)                       |
| `tu info`   | parameter schema — `--detail brief/description/full`             |
| `tu find`   | natural-language semantic search                                 |
| `tu run`    | execute a tool — `tu run NAME k=v ...` or JSON                   |
| `tu test`   | run tool with example inputs                                     |
| `tu status` | tool count, health, API keys                                     |
| `tu health` | check / refresh tool health cache                                |
| `tu build`  | rebuild static lazy registry                                     |
| `tu serve`  | shortcut for `tooluniverse` (MCP stdio)                          |

Global flags: `--version`, `--quiet`, `--verbose`/`-v`, `--json`, `--raw`.

Other console scripts (operational):
`generate-mcp-tools`, `tu-datastore`, `tooluniverse-doctor`,
`tooluniverse-expert-feedback`, `tooluniverse-expert-feedback-web`.

---

## 2 — The Discovery Layer in Depth

Three finder strategies live behind `find_tools` / `grep_tools`. Pick by
constraint, not preference.

| Finder                     | Algorithm                                          | When                                   |
|----------------------------|----------------------------------------------------|----------------------------------------|
| `ToolFinderKeyword`        | BM25 + TF-IDF, stemming, phrase bonuses            | exact terms, no GPU, reproducible      |
| `ToolFinderEmbedding`      | `ToolRAG-T1-GTE-Qwen2-1.5B` + cosine, FAISS, MPS   | natural-language paraphrase, GPU OK    |
| `ToolFinderLLM`            | keyword pre-filter (top 50) → LLM JSON reasoning   | multi-tool composition, multi-hop      |

Cache: `~/.cache/tooluniverse/embeddings/*.pt`, MD5 cache-busting on tool list
change. Static lazy registry at `src/tooluniverse/_lazy_registry_static.py`
maps tool type → module so imports happen on first use, not at startup.

Docs already in repo:

- `docs/dev_docs/Embedding_Search.md` — embedding pipeline
- `docs/dev_docs/Tool_Registration_Chain.md` — 6 links from JSON → MCP

---

## 3 — Built-in Capability Classes

ToolUniverse isn't only API passthroughs. Several tool classes execute logic
in-process. An outside agent should reach for these when it needs to *compute*,
not just *look up*.

### Agentic tools (LLMs-as-tools)

`src/tooluniverse/agentic_tool.py`. `AgenticTool` is a generic LLM wrapper with
a provider fallback chain (Claude CLI → OpenRouter → Ollama). 23 registered
agentic tools in `src/tooluniverse/data/agentic_tools.json` (e.g.
`ScientificTextSummarizer`, `MedicalLiteratureReviewer`, `HypothesisGenerator`,
`ExperimentalDesignScorer`, `NoveltySignificanceReviewer`).

`SmolagentsTool` (`smolagent_tool.py`) wraps any TU tool as a
`smolagents.Tool` subclass for the smolagents framework.

### Sandboxed Python execution

`src/tooluniverse/python_executor_tool.py` — `BasePythonExecutor`. AST-checked
sandbox with safe builtins (`print`, `len`, `range`, `zip`) and allowed
modules (`math`, `sympy`, `numpy`, `scipy`, `matplotlib`). For symbolic math,
ad-hoc statistics, plotting.

### Cheminformatics / sequence

| Tool                  | Capability                                                       |
|-----------------------|------------------------------------------------------------------|
| `ChemComputeTool`     | Synthetic Accessibility score via RDKit                          |
| `RDKitCheminfoTool`   | pharmacophore features (HBD/HBA/aromatic/...), MMP analysis      |
| `SequenceAnalyzeTool` | GC%, reverse complement, MW, UniProt fetch by accession          |

### Statistical / analytical

| Tool                  | Capability                                                       |
|-----------------------|------------------------------------------------------------------|
| `MetaAnalysisTool`    | fixed/random-effects (DerSimonian-Laird), Q, I²                  |
| `FAERSAnalyticsTool`  | ROR / PRR / IC / EBGM disproportionality, demographic stratify   |
| `MetaboAnalystTool`   | metabolite mapping, pathway/biomarker enrichment                 |
| `DataQualityTool`     | tabular profiling, missingness, outliers                         |
| `GraphQLTool`         | generic GraphQL builder + executor + null-strip                  |
| `WikidataSparqlTool`  | generic SPARQL                                                   |

### Visualization

| Tool                | Capability                                                                |
|---------------------|---------------------------------------------------------------------------|
| `VisualizationTool` | base — HTML or base64 PNG envelope                                        |
| `ToolGraphWebUI`    | Flask + D3.js over `tool_composition_graph.json` (nodes/edges/search)     |

Cached graph files at repo root: `tool_composition_graph.{json,pkl}`,
`tool_composition_graph_cache.pkl`, `tool_relationship_graph.json`,
`TOOL_MANIFEST.json` (~616 KB).

---

## 4 — Skills Layer (~134 skills)

Skills are higher-level orchestration playbooks that sit *above* the tools.
They're in `skills/` and follow `SKILL.md` frontmatter conventions.

### Routing / meta (11)

| Skill                              | Purpose                                                          |
|------------------------------------|------------------------------------------------------------------|
| `tooluniverse`                     | Top-level router; dispatches to specialized skills               |
| `tu-llm`                           | LLM-powered tool discovery for multi-step queries                |
| `tooluniverse-deep-research`       | Iterative cross-database research agent                          |
| `deep-review`                      | Publication-quality typeset review w/ verified bibliography      |
| `setup-tooluniverse`               | Install + configure (MCP / CLI / SDK)                            |
| `create-tooluniverse-skill`        | TDD methodology to build new skills                              |
| `tooluniverse-install-skills`      | Auto-install missing research skills                             |
| `tooluniverse-custom-tool`         | Add custom local tools                                           |
| `tooluniverse-claude-code-plugin`  | Install ToolUniverse plugin for Claude Code                      |
| `tooluniverse-sdk`                 | Build AI scientist systems via Python SDK                        |
| `evals`                            | (orphan — no SKILL.md)                                           |

### Development (`devtu-*`, 10)

`devtu-auto-discover-apis`, `devtu-benchmark-harness`,
`devtu-code-optimization`, `devtu-create-tool`, `devtu-docs-quality`,
`devtu-fix-tool`, `devtu-github`, `devtu-optimize-descriptions`,
`devtu-optimize-skills`, `devtu-self-evolve`.

### Domain research (`tooluniverse-*`, ~112)

- **Disease & clinical** (19) — `disease-research`,
  `rare-disease-diagnosis`, `vaccine-design`, `epidemiological-analysis`
- **Drug research** (18) — `drug-research`, `admet-prediction`,
  `drug-repurposing`, `pharmacovigilance`
- **Genomics & variants** (25) — `acmg-variant-classification`,
  `gwas-trait-to-gene`, `polygenic-risk-score`
- **Cancer & oncology** (2) — `cancer-classification`,
  `precision-oncology`
- **Protein & structure** (11) — `antibody-engineering`,
  `binder-discovery`, `protein-structure-prediction`
- **Cell & expression** (5) — `single-cell`, `crispr-screen-analysis`,
  `stem-cell-organoid`
- **Omics & pathways** (14) — `metabolomics`, `proteomics-analysis`,
  `spatial-transcriptomics`, `rnaseq-deseq2`
- **Other** (18) — `literature-deep-research`, `dataset-discovery`,
  `image-analysis`, `statistical-modeling`

### Non-domain (1)

- `company-research` — FBI/SEC-style company briefs (job-application use).

**Orphans (no SKILL.md):** `evals`, `tooluniverse-computational-biophysics-workspace`,
`tooluniverse-drug-drug-interaction-workspace`,
`tooluniverse-organic-chemistry-workspace`.

The `tooluniverse` router skill is the canonical entry point: it parses
intent, matches keywords against the routing table, and either invokes a
specialized skill or falls back to general strategies in
`skills/tooluniverse/references/general-strategies.md`.

---

## 5 — State Awareness

What the outside codebase can know about a running ToolUniverse instance.

| Question                             | Surface                                                        |
|--------------------------------------|----------------------------------------------------------------|
| How many tools are loaded right now? | `tu status` / `GET /health` / `tu.get_available_tools()`       |
| What categories exist?               | `tu list --mode categories` / `list_tools` MCP                 |
| What's the schema of tool X?         | `tu info X` / `get_tool_info` MCP / `tu.tool_specification(X)` |
| Which tools are healthy?             | `tu health` / `tu list --filter-healthy`                       |
| Which API keys are configured?       | `tu status` / `tooluniverse-doctor`                            |
| What does the tool graph look like?  | `tool_composition_graph.json` / `ToolGraphWebUI`               |
| Has the embedding cache been built?  | `~/.cache/tooluniverse/embeddings/*.pt`                        |
| What's in MEMORY.md?                 | conversation-scoped — not exposed via TU                       |

---

## 6 — Credentials (env vars an outside codebase must set)

Tools auto-skip when keys are missing; set what you need.

**Databases / data:** `USPTO_API_KEY`, `NCBI_API_KEY`, `SEMANTIC_SCHOLAR_API_KEY`,
`OMIM_API_KEY`, `UMLS_API_KEY`, `DISGENET_API_KEY`, `ONCOKB_API_TOKEN`,
`ADDGENE_API_KEY`, `BIOGRID_API_KEY` / `BIOGRID_ACCESS_KEY`,
`FDA_API_KEY`, `FDC_API_KEY`, `CLUE_API_KEY`, `MCULE_API_KEY`.

**LLMs:** `OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY` (+ `AZURE_OPENAI_ENDPOINT`,
`AZURE_OPENAI_DEPLOYMENT`, `OPENAI_API_VERSION`), `GEMINI_API_KEY`,
`OPENROUTER_API_KEY`, `NVIDIA_API_KEY`, `HF_TOKEN`.

**Specialised:** WHO ICD (`ICD_CLIENT_ID`, `ICD_CLIENT_SECRET`),
BRENDA (`BRENDA_EMAIL`, `BRENDA_PASSWORD`), `ESM_API_KEY`,
expert-feedback (`EXPERT_FEEDBACK_API_HOST`, `EXPERT_FEEDBACK_API_PORT`).

**Local inference:** `OLLAMA_SERVER_URL`, `VLLM_SERVER_URL`.

**Behaviour:** `TOOLUNIVERSE_CACHE_ENABLED`, `TOOLUNIVERSE_CACHE_PERSIST`,
`TOOLUNIVERSE_CACHE_MEMORY_SIZE`, `TOOLUNIVERSE_LAZY_LOADING`,
`TOOLUNIVERSE_COERCE_TYPES`, `TOOLUNIVERSE_STRICT_VALIDATION`,
`TOOLUNIVERSE_STDIO_MODE`, `TOOLUNIVERSE_LOG_LEVEL`,
`TOOLUNIVERSE_LLM_DEFAULT_PROVIDER`, `TOOLUNIVERSE_LLM_TEMPERATURE`,
`TOOLUNIVERSE_PROFILE`, `TOOLUNIVERSE_HOME`.

Set in shell, `.tooluniverse/.env`, or `.tooluniverse/profile.yaml`.

---

## 7 — Canonical Iterative Workflow

How an outside agent searches *everything* and pulls it together:

1. **Discover** — start broad. `find_tools(query)` for natural
   language; `grep_tools(pattern)` for known terms; `tu-llm` to plan
   multi-tool compositions.
2. **Inspect** — `get_tool_info(name)` for every candidate. Never guess
   parameters.
3. **Execute** — `execute_tool(name, args)`. Use cache
   (`TOOLUNIVERSE_CACHE_ENABLED=true`) for repeats.
4. **Cross-reference** — chain entities (gene → pathway → disease → drug
   → trial) across databases. Discover gaps; query intermediates.
5. **Iterate** — when results are thin, reformulate and re-run discovery.
   The LLM finder is good at proposing the next hop.
6. **Compute** — when you need numbers, use `python_executor_tool`,
   `MetaAnalysisTool`, `FAERSAnalyticsTool`, `RDKitCheminfoTool`,
   `SequenceAnalyzeTool`. Don't estimate.
7. **Synthesise** — combine all outputs; trace every claim back to a
   tool call ID; grade evidence (VERIFIED / NOVEL / GAP / NEGATIVE).
8. **Render** — `VisualizationTool` for figures; `ToolGraphWebUI` for
   interactive exploration; `deep-review` skill for typeset PDFs.

Minimal Python sketch of the loop:

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse(); tu.load_tools()

def step(name, **args):
    schema = tu.tool_specification(name)
    return tu.run_one_function({"name": name, "arguments": args}, use_cache=True)

# 1. discover
hits = step("Tool_Finder_LLM",
            description="cross-reference TP53 variants to drug response in TCGA",
            limit=8)

# 2. inspect + execute the suggested chain
gwas = step("OpenTargets_get_target_gene_ontology_by_ensemblID",
            ensemblId="ENSG00000141510")
trials = step("ClinicalTrials_search_studies", query="TP53 inhibitor", max_results=10)
faers  = step("FAERS_count_reactions_by_drug_event", medicinalproduct="nutlin")

# 3. compute locally
mw = step("SequenceAnalyzeTool", sequence="...")  # local, no API
tu.close()
```

---

## 8 — Map of Maps

If you only remember one thing, remember the file map:

| Need                          | Read                                                          |
|-------------------------------|---------------------------------------------------------------|
| Python class API              | `src/tooluniverse/execute_function.py`                        |
| MCP entry points              | `src/tooluniverse/smcp_server.py`                             |
| MCP tool registration         | `mcp_tool_registry.py` + `mcp_tool_registration_en.md`        |
| Compact-mode proxy tools      | `src/tooluniverse/smcp.py`                                    |
| HTTP REST                     | `src/tooluniverse/http_api_server.py`                         |
| HTTP client                   | `src/tooluniverse/http_client.py`                             |
| CLI (`tu`)                    | `src/tooluniverse/cli.py`                                     |
| Discovery: keyword / NL / LLM | `tool_finder_{keyword,embedding,llm}.py`                      |
| Lazy startup registry         | `src/tooluniverse/_lazy_registry_static.py`                   |
| Tool registration chain       | `docs/dev_docs/Tool_Registration_Chain.md`                    |
| Embedding pipeline            | `docs/dev_docs/Embedding_Search.md`                           |
| MCP tutorial                  | `docs/dev_docs/MCP_Server_Tutorial.md`                        |
| Adding new tools              | `docs/dev_docs/Adding_Tools_Tutorial.md` (+ Quick_Reference)  |
| Skills inventory              | `skills/` (134 SKILL.md files)                                |
| Tool graph UI                 | `src/tooluniverse/tool_graph_web_ui.py`                       |
| Agentic tools registry        | `src/tooluniverse/data/agentic_tools.json`                    |
| Tool composition graph data   | `tool_composition_graph.{json,pkl}` (repo root)               |
| Manifest                      | `server.json`, `TOOL_MANIFEST.json`                           |
