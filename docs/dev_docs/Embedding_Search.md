# ToolUniverse Embedding Search -- How It Works

How `find_tools` turns a natural language query into a ranked list of
tools using HuggingFace sentence embeddings.

## The pipeline

```
"extract patent claims"          <-- your query (natural language)
        |
        v
   SentenceTransformer.encode()  <-- encode query to 1536-dim vector
        |
        v
   cosine similarity against     <-- compare to precomputed tool vectors
   2,300 tool embeddings
        |
        v
   torch.topk(scores, k)        <-- pick top-k highest scores
        |
        v
   ["USPTO_get_patent_claims",   <-- ranked tool names
    "USPTO_patent_deep_lookup",
    ...]
```

## What gets embedded

NOT just the tool name. Each tool's embedding is computed from its
full JSON specification serialized to a string:

```python
all_tools_str = [json.dumps(each) for each in tu.prepare_tool_prompts(filtered_tools)]
```

`prepare_tool_prompts` returns the tool's name, description, parameter
schema, and return schema -- everything an agent needs to decide if a
tool is relevant. This means the embedding captures semantic meaning
from parameter names, descriptions, and type information, not just the
tool name.

## The model

```
mims-harvard/ToolRAG-T1-GTE-Qwen2-1.5B
```

A 1.5B parameter sentence transformer fine-tuned for tool retrieval.
Hosted on HuggingFace, downloaded and cached locally on first use.
Runs on MPS (Apple Silicon), CUDA, or CPU.

- Max sequence length: 4,096 tokens
- Output dimension: 1,536 (normalized L2)
- Similarity metric: cosine (via `model.similarity()`)

## Caching

Embeddings are cached to disk so they don't need to be recomputed
every session.

**Cache location:**

```
~/.cache/tooluniverse/embeddings/
```

**Cache key:** MD5 hash of the serialized tool list. If any tool's
JSON definition changes (name, description, parameters), the hash
changes and embeddings auto-regenerate on next query.

**Cache filename pattern:**

```
ToolRAG-T1-GTE-Qwen2-1.5Btool_embedding_<md5>.pt
```

**Staleness:** Adding, removing, or modifying any tool invalidates
the cache. The rebuild takes 2-5 minutes on M1 Max (MPS), encoding
~2,300 tool descriptions through a 1.5B model.

## How to call it

### Via MCP (Claude Code / agents)

The embedding search is exposed as `find_tools` in ToolUniverse's
compact mode MCP interface:

```python
mcp__tooluniverse__find_tools(
    query="extract patent claims from USPTO",
    limit=10
)
```

This calls `Tool_Finder` internally, which is backed by
`ToolFinderEmbedding.run()`.

### Via Python SDK

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

# Option 1: Through the standard run interface
result = tu.run({
    "name": "Tool_Finder",
    "arguments": {
        "description": "extract patent claims from USPTO",
        "limit": 10
    }
})

# Option 2: Direct access to the embedding finder
finder = tu.tool_finder  # ToolFinderEmbedding instance
tool_names = finder.rag_infer("extract patent claims", top_k=10)
```

### Via standalone (no ToolUniverse)

If you want just the embedding similarity without ToolUniverse's
orchestration:

```python
import torch
from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer("mims-harvard/ToolRAG-T1-GTE-Qwen2-1.5B")
model.max_seq_length = 4096

# Load cached embeddings
cache_path = "~/.cache/tooluniverse/embeddings/ToolRAG-T1-GTE-Qwen2-1.5Btool_embedding_<md5>.pt"
tool_embeddings = torch.load(cache_path, weights_only=False)

# You also need the tool name list (same order as embeddings).
# Rebuild it from ToolUniverse or cache it alongside the .pt file.
tu = ToolUniverse()
tu.load_tools()
exclude = ["Tool_RAG", "Tool_Finder", "Finish", "CallAgent"]
tool_names = [t["name"] for t in tu.all_tools if t["name"] not in exclude]

# Query
query_embedding = model.encode(
    ["find patents by inventor name"],
    normalize_embeddings=True,
    convert_to_tensor=True,
)

# Cosine similarity (embeddings are L2-normalized, so dot product = cosine)
scores = model.similarity(query_embedding, tool_embeddings)
top_k = torch.topk(scores, 10).indices.tolist()[0]
results = [tool_names[i] for i in top_k]
print(results)
```

## How another codebase would integrate

### Option A: Use ToolUniverse as a dependency

```python
pip install tooluniverse[embedding]
```

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

# Search for tools by natural language
result = tu.run({
    "name": "Tool_Finder",
    "arguments": {"description": "analyze protein structure stability", "limit": 5}
})
# Returns tool specifications with full parameter schemas
```

This is the intended integration path. ToolUniverse handles model
loading, caching, device placement, and cache invalidation.

### Option B: Use the MCP server

Run ToolUniverse as an MCP server and call `find_tools` over HTTP.
Another Claude Code session or any MCP client can query it:

```python
# From any MCP client:
mcp__tooluniverse__find_tools(
    query="predict drug-drug interactions",
    limit=5
)
```

The MCP server handles everything -- model loading, embedding cache,
similarity search. The client just sends a string and gets back tool
specs.

### Option C: Use the cached embeddings directly

If you want to run similarity search without ToolUniverse:

1. Install `sentence-transformers` and `torch`
2. Load the same HF model: `mims-harvard/ToolRAG-T1-GTE-Qwen2-1.5B`
3. Load the cached `.pt` file from `~/.cache/tooluniverse/embeddings/`
4. Maintain your own tool name list (same order as the embedding rows)
5. Encode your query and compute cosine similarity

This is fragile -- you must keep the tool name list synchronized with
the embedding tensor. Option A or B is better.

## Key implementation details

### Auto-refresh

`ToolFinderEmbedding._maybe_refresh_embeddings()` runs before every
query. It compares the current tool list against the indexed list. If
tools were added or removed since last rebuild, it regenerates
embeddings automatically. No manual cache invalidation needed.

### Device handling

The model and embeddings are placed on the same device:

- CUDA if available (fastest)
- MPS on Apple Silicon (used on this machine)
- CPU fallback

Both query embedding and tool embeddings must be on the same device
for similarity computation. The code handles cross-device moves
automatically.

### Exclusions

These tool names are excluded from embedding search results:
`Tool_RAG`, `Tool_Finder`, `Finish`, `CallAgent`. These are internal
orchestration tools that agents shouldn't discover through search.

### Embedding vs keyword search

ToolUniverse has TWO search tools:

| Tool | Method | When to use |
|------|--------|-------------|
| `find_tools` (Tool_Finder) | Embedding similarity | Natural language queries, fuzzy matching, "find tools that do X" |
| `grep_tools` (Tool_Finder_Keyword) | Text pattern matching | Known tool names, exact keywords, regex patterns |

Embedding search understands semantics ("analyze protein folding"
finds AlphaFold tools even though "folding" isn't in the tool name).
Keyword search is faster and deterministic but requires you to know
the right words.

## Source files

| File | Role |
|------|------|
| `src/tooluniverse/tool_finder_embedding.py` | Core class: model loading, embedding generation, similarity search |
| `src/tooluniverse/data/finder_tools.json` | Tool_Finder JSON definition (type: ToolFinderEmbedding) |
| `src/tooluniverse/data/compact_mode_tools.json` | MCP compact mode config that exposes `find_tools` |
| `~/.cache/tooluniverse/embeddings/*.pt` | Cached embedding tensors |
