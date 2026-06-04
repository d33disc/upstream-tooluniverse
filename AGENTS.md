# AGENTS.md — ToolUniverse

You're an AI agent working in this repo. Read this first.

ToolUniverse is a scientific research platform exposing **~2,300 tools across
~500 categories** (494 cataloged in `TOOL_MANIFEST.json`, 2026-03-28) plus
**136 orchestration skills**. It is reachable through
multiple transports — every transport routes through the same core class.

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
5. `execute_tool` — run any of the ~2,300 backend tools

Higher-level reasoning over multi-tool compositions: `Tool_Finder_LLM` /
`/tu-llm` skill.

## Where the full map lives

Read **[`docs/dev_docs/Interaction_Surfaces.md`](docs/dev_docs/Interaction_Surfaces.md)**
for the comprehensive integration map: every entry point with file:line refs,
the discovery layer in depth, built-in compute/visualisation tools, the 134
skills inventory, credentials inventory, and the canonical iterative workflow.

Also useful:

- `docs/dev_docs/Adding_Tools_Tutorial.md` (+ `src/tooluniverse/_lazy_registry_static.py`)
  — how a tool gets from JSON definition to MCP-callable
- `docs/dev_docs/Interaction_Surfaces.md` 2 — how `find_tools` indexes tools
- `docs/dev_docs/MCP_Server_Tutorial.md` — MCP setup walkthrough
- `docs/dev_docs/Adding_Tools_Tutorial.md` — adding new tools
- `server.json` — machine-readable MCP manifest
- `pyproject.toml` `[project.scripts]` — every console entry point

## Conventions

- The default `tooluniverse` console script runs in **compact mode**: the MCP
  layer exposes the 4 proxy tools (`list_tools`, `grep_tools`,
  `get_tool_info`, `execute_tool`) plus `find_tools` when search is enabled
  (the default). The full ~2,300 tools stay loaded and reachable via
  `execute_tool`. To suppress `find_tools`, exclude the `tool_finder`
  category at startup.
- Credentials are env-var-based; tools auto-skip when their key is missing.
  Run `tu status` to see what's configured.
- Set `TOOLUNIVERSE_CACHE_ENABLED=true` for repeatable lookups.
