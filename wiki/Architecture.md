# Architecture

## MCP Server (Compact Mode)

ToolUniverse runs as a single MCP stdio server exposing 5 proxy tools:

| Tool | Purpose |
|------|---------|
| `grep_tools` | Keyword search (fast, exact match) |
| `find_tools` | Natural language / embedding search |
| `list_tools` | Browse tools by category |
| `get_tool_info` | Get exact parameter schema for a tool |
| `execute_tool` | Run any tool with arguments |

All 1,200+ underlying tools are accessed through `execute_tool` after
discovering them via `grep_tools` or `find_tools` and inspecting their
schema via `get_tool_info`.

## Tool Registry

- **1,200+ tools** covering literature, proteins, drugs, clinical trials,
  genomics, pathways, ontologies, and datasets
- **Lazy loading** (`TOOLUNIVERSE_LAZY_LOADING=true`) -- tools load on
  first use, keeping startup fast
- **Two-tier cache** -- in-memory LRU (configurable size) backed by
  optional persistent disk cache for offline support

## Skills (Research Workflows)

The `skills/` directory contains 70+ research workflow definitions.
Each skill is a structured Markdown file that guides Claude through
a multi-step scientific investigation (literature review, drug safety
analysis, variant interpretation, etc.).

## Claude Code Integration (`claude/`)

The `claude/` directory provides:

- **`commands/`** -- slash commands (e.g., `/tooluniverse`)
- **`rules/`** -- query reference and protocol rules loaded as context
- **`scripts/`** -- wrapper scripts for MCP startup
- **`tooluniverse-hooks.json`** -- pre/post hooks for tool execution

## Data Flow

```text
User query
  → Claude Code (with skills + rules context)
    → MCP stdio server (compact mode)
      → grep_tools / find_tools  (discover)
      → get_tool_info             (inspect)
      → execute_tool              (execute)
        → upstream API (PubMed, UniProt, ChEMBL, ...)
      → SummarizationHook (auto-summarize large outputs)
    → Claude synthesizes results
  → User
```
