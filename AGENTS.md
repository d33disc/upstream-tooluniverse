# AGENTS.md — ToolUniverse

You're an AI agent working in this repo. Read this first.

ToolUniverse is a scientific research platform exposing **2,500+ tools** plus
**150+ orchestration skills**. It is reachable through multiple transports —
every transport routes through the same core class. Use `tu status` for the
current runtime inventory; `TOOL_MANIFEST.json` is a dated health snapshot, not
the authoritative count of loadable tools.

## How to interact (5 connection surfaces)

- **Embedded in Python** — `from tooluniverse import ToolUniverse`
- **Claude Desktop / Claude Code** — MCP stdio → `tooluniverse` (or
  `tooluniverse-smcp-stdio`)
- **Remote / containerised MCP** — streamable-http → `tooluniverse-mcp`
  or `tooluniverse-smcp-server`
- **Language-agnostic / curl** — REST → `tooluniverse-http-api` (FastAPI)
- **Shell scripts / humans** — CLI → `tu` (`tu list`, `tu grep`,
  `tu find`, `tu info`, `tu run`)

For **MCP host registration** in another project: `claude mcp add tooluniverse`
(or add `~/code/ToolUniverse`'s `server.json` config to your MCP host).

## How to find tools (the 5 discovery primitives)

Every surface exposes the same 5 primitives. Always discover → inspect →
execute; never guess parameter names.

1. `grep_tools` — BM25 keyword/regex match (deterministic, no GPU)
2. `find_tools` — embedding semantic search (natural language)
3. `list_tools` — browse / paginate by category
4. `get_tool_info` — **always call this before `execute_tool`** to get the
   exact parameter schema (names vary across tools)
5. `execute_tool` — run any backend tool

Higher-level reasoning over multi-tool compositions: `Tool_Finder_LLM` /
`/tu-llm` skill.

## Where the full map lives

Read **[`docs/dev_docs/Interaction_Surfaces.md`](docs/dev_docs/Interaction_Surfaces.md)**
for the comprehensive integration map: every entry point, the discovery layer
in depth, built-in compute/visualisation tools, skills, credentials, and the
canonical iterative workflow.

Also useful:

- `docs/dev_docs/Adding_Tools_Tutorial.md` (+ `src/tooluniverse/_lazy_registry_static.py`)
  — how a tool gets from JSON definition to MCP-callable
- `docs/dev_docs/Embedding_Search.md` — how `find_tools` indexes tools
- `docs/dev_docs/MCP_Server_Tutorial.md` — MCP setup walkthrough
- `server.json` — machine-readable MCP manifest
- `pyproject.toml` `[project.scripts]` — every console entry point

## Conventions

- The default `tooluniverse` console script runs in **compact mode**: the MCP
  layer exposes the 4 proxy tools (`list_tools`, `grep_tools`,
  `get_tool_info`, `execute_tool`) plus `find_tools` when search is enabled
  (the default). Backend tools stay loaded and reachable via `execute_tool`.
  To suppress `find_tools`, exclude the `tool_finder`
  category at startup.
- Credentials are env-var-based; tools auto-skip when their key is missing.
  Run `tu status` to see what's configured.
- Set `TOOLUNIVERSE_CACHE_ENABLED=true` for repeatable lookups.

## Blind-agent research protocol

For agents that do NOT know the catalog, use the compact MCP entry
(`tooluniverse-discover`): it exposes only list_tools, grep_tools,
get_tool_info, execute_tool plus find_tools (semantic), keeping context lean.

1. **Semantic sweep FIRST, before any docs**: call find_tools with the
   research question in natural language. This converts the 2,722-tool space
   into a shortlist of 5-10 candidates in one call. Run one sweep per
   research facet. get_tool_info then fills in only what is relevant.
2. **Breadth backstop**: grep_tools(keywords, field=description) if the sweep
   missed something; list_tools(category=...) only within a suspected
   category. Never enumerate the full catalog.
3. **Depth**: get_tool_info on each candidate; read the test_examples
   (live-verified usage). Return schemas are hardened, so output shape is
   predictable before the first call.
4. **Plan, then execute**: one tool per subtask; argument names copied
   exactly from get_tool_info. Parse {status, data, error_details};
   error_details.retriable decides whether to retry.
5. **Evidence rule**: tu is transport, never authority. Cite the underlying
   API (api.uspto.gov, UniProt, IntAct, ...) in every report.

Meta-rules: three calls per tool max (sweep -> info -> execute). Respect
vendor limits (USPTO per-URI quota, NIM job latency, TDC Dataverse outages);
chain outputs between tools (search result IDs feed get-by-id tools).
