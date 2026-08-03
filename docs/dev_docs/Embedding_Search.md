# ToolUniverse embedding search

`find_tools` turns a natural-language request into a ranked list of tools. It
embeds the query and compares it with cached embeddings of the tools currently
loaded by `ToolUniverse`.

## Pipeline

```text
natural-language query
        │
        ▼
embedding encoder
        │
        ▼
cosine similarity against cached tool-description tensors
        │
        ▼
top-k tool specifications
```

Each document embedding represents the full prepared tool specification: name,
description, parameter schema, and return schema. Search is therefore not
limited to words in the tool name.

The default local encoder is:

```text
mims-harvard/ToolRAG-T1-GTE-Qwen2-1.5B
```

It produces 1,536-dimensional, L2-normalized vectors and runs on CUDA, Apple
Silicon MPS, or CPU. The model is downloaded from Hugging Face on first use.

## Install

The embedding finder needs the optional embedding dependencies:

```bash
uv pip install 'tooluniverse[embedding]'
```

## Cache and automatic updates

Tool embeddings are stored under ToolUniverse's cross-platform user cache:

| Platform | Default cache root |
|---|---|
| macOS | `~/Library/Caches/ToolUniverse` |
| Linux | `$XDG_CACHE_HOME/tooluniverse` or `~/.cache/tooluniverse` |
| Windows | `%LOCALAPPDATA%\ToolUniverse\Cache` |

Embedding tensors live in `<user_cache_dir>/embeddings/`. Set
`TOOLUNIVERSE_TMPDIR` to override the ToolUniverse user-cache root.

The filename contains the encoder name and a hash:

```text
ToolRAG-T1-GTE-Qwen2-1.5Btool_embedding_<hash>.pt
```

The hash covers the prepared tool specifications and settings that affect
document vectors: embedding backend, `trust_remote_code`, and document prompt.
A new process therefore selects or builds the matching cache whenever the tool
catalog or embedding configuration changes. During a running process,
`_maybe_refresh_embeddings()` also rebuilds when the loaded set of tool names
changes.

There is normally no manual update step. Load the current tools and issue an
embedding query; ToolUniverse either reuses the matching tensor or generates a
new one. Old cache files may coexist safely because their hashes differ.

To inspect the resolved cache directory:

```python
from pathlib import Path
from tooluniverse.utils import get_user_cache_dir

cache_dir = Path(get_user_cache_dir()) / "embeddings"
print(cache_dir)
print(*sorted(cache_dir.glob("*tool_embedding_*.pt")), sep="\n")
```

## Query through ToolUniverse

### MCP compact mode

Call the compact-mode proxy:

```python
find_tools(
    query="extract patent claims from USPTO",
    limit=10,
)
```

The MCP proxy invokes the configured `Tool_Finder` embedding tool and returns
tool specifications suitable for a subsequent `get_tool_info` call.

### Python SDK

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

result = tu.run({
    "name": "Tool_Finder",
    "arguments": {
        "description": "extract patent claims from USPTO",
        "limit": 10,
    },
})
```

ToolUniverse handles model loading, device placement, cache selection, and
refresh. Prefer this interface over loading a `.pt` file directly: a tensor is
only meaningful with the exact ordered tool list and encoder configuration that
produced it.

## Encoder choices

The `embedding_model` argument can select a configured encoder:

| Value | Backend | Notes |
|---|---|---|
| `default` | local | Fine-tuned ToolRAG-T1 model |
| `gte-qwen2-7b` | local | Larger instruction-tuned encoder; GPU recommended |
| `e5-mistral-7b` | local | Larger instruction-tuned encoder; GPU recommended |
| `openai-3-large` | hosted | OpenAI/Azure credentials required |
| `openai-3-small` | hosted | OpenAI/Azure credentials required |

Hosted models use ToolUniverse's shared embedding provider. If a hosted encoder
is requested without usable credentials, the finder falls back to its local
model and logs a warning.

Example:

```python
result = tu.run({
    "name": "Tool_Finder",
    "arguments": {
        "description": "find tools for protein stability analysis",
        "limit": 5,
        "embedding_model": "gte-qwen2-7b",
    },
})
```

## Finder strategies

ToolUniverse provides three complementary discovery strategies:

| Tool | Method | Best for |
|---|---|---|
| `Tool_Finder` / MCP `find_tools` | embedding cosine similarity | Natural-language and semantic matching |
| `Tool_Finder_Keyword` / MCP `grep_tools` | BM25/TF-IDF keyword ranking | Exact terms, names, and deterministic local search |
| `Tool_Finder_LLM` | LLM reasoning over candidates | Multi-tool and multi-hop planning |

The configured embedding finder excludes internal orchestration tools from its
results: `Tool_RAG`, `Tool_Finder`, `Finish`, `CallAgent`, `Tool_Finder_LLM`,
and `Tool_Finder_Keyword`.

## Implementation map

| File | Role |
|---|---|
| `src/tooluniverse/tool_finder_embedding.py` | Model selection, encoding, cache, and similarity |
| `src/tooluniverse/data/finder_tools.json` | Finder schemas, default model, and exclusions |
| `src/tooluniverse/data/compact_mode_tools.json` | MCP compact-mode proxy definitions |
| `src/tooluniverse/utils.py` | Cross-platform user-cache resolution |
