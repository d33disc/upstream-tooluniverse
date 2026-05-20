# ToolUniverse Tool Registration Chain

How a tool goes from "JSON definition" to "callable via MCP." Six links.
Break any one and the tool silently doesn't load.

Last verified: 2026-04-18

## The 6 links

```
JSON definition ──> Python class ──> Lazy registry ──> Category config ──> Wrapper stub ──> __init__.py
    (Link 1)          (Link 2)        (Link 3)          (Link 4)           (Link 5)         (Link 6)
```

An AI adding tools must create or update ALL 6. The order matters —
each link references the previous one.

## Link 1: JSON tool definition

**File:** `src/tooluniverse/data/<category>_tools.json`

This is the source of truth. Defines name, type, description,
parameters, return schema, required API keys, and test examples.

```json
[
  {
    "type": "MyToolType",
    "name": "my_tool_name",
    "description": "One sentence. What it does, not how.",
    "parameter": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "What to search for"
        },
        "limit": {
          "type": "integer",
          "description": "Max results",
          "default": 10
        }
      },
      "required": ["query"]
    },
    "required_api_keys": ["MY_API_KEY"],
    "return_schema": {
      "type": "object",
      "properties": {
        "status": {"type": "string"},
        "data": {"type": "object"}
      }
    },
    "test_examples": [
      {"query": "test input", "limit": 1}
    ]
  }
]
```

**Rules:**

- File is a JSON array (even for one tool)
- `type` must exactly match the `@register_tool` decorator string (Link 2)
- `name` must be a valid Python identifier (used as function name in Link 5)
- `required` inside `parameter` lists mandatory params
- `required_api_keys` lists env vars checked at init time
- `test_examples` are dicts of arguments (no `name` key — just the args)
- Multiple tools can share one JSON file (same category)

## Link 2: Python implementation

**File:** `src/tooluniverse/<module_name>.py`

A class decorated with `@register_tool` that implements `run()`.

```python
"""
<module_name>.py — one-line summary.

Metadata
--------
name:          <module_name>
version:       1.0.0
owner:         ToolUniverse
last_reviewed: 2026-04-18
"""

import os
import requests
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool("MyToolType")
class MyToolClass(BaseTool):
    """One-line docstring matching the JSON description."""

    def __init__(self, tool_config: dict, api_key: str | None = None) -> None:
        super().__init__(tool_config)
        self.api_key = api_key or os.environ.get("MY_API_KEY")
        if not self.api_key:
            raise ValueError("MY_API_KEY environment variable is required.")

    def run(self, arguments: dict | None = None) -> dict:
        arguments = arguments or {}
        query = arguments.get("query")
        if not query:
            return self.tool_error(
                "Missing required parameter 'query'.",
                error_type="ValidationError",
                suggestion="Provide a search query string.",
            )

        # ... do the work ...

        return {"status": "success", "data": {"results": []}}
```

**Rules:**

- `@register_tool("MyToolType")` string must EXACTLY match `"type"` in the JSON
- Must inherit from `BaseTool`
- `__init__` must accept `tool_config` as first arg
- `run` must accept `arguments` dict, return a dict
- Use `self.tool_error()` for structured errors (inherited from BaseTool)
- Module name (filename without .py) is what Link 3 references
- One class per module is cleanest, but multiple are allowed

## Link 3: Lazy registry

**File:** `src/tooluniverse/_lazy_registry_static.py`

A dict mapping type strings to module names. This is how ToolUniverse
knows which Python file to import when it encounters a tool type.

```python
TOOL_REGISTRY = {
    # ... hundreds of existing entries, alphabetically sorted ...
    "MyToolType": "my_module_name",
    # ...
}
```

**Rules:**

- Key = the `@register_tool("...")` string = the JSON `"type"` field
- Value = the Python module name (filename without `.py`, relative to `src/tooluniverse/`)
- Entries are alphabetically sorted by key
- If this line is missing, the tool SILENTLY fails to load. No error, no warning. It just doesn't appear.

**This is the link most commonly broken.** It was the only bug in the
USPTO tools — 4 entries were missing, so 4 tools existed in code but
were invisible to MCP.

## Link 4: Category registration

**File:** `src/tooluniverse/default_config.py`

Maps a category name to the JSON file path. This tells ToolUniverse
where to find the tool definitions at startup.

```python
DEFAULT_CATEGORY_MAP = {
    # ... existing entries ...
    "my_category": os.path.join(current_dir, "data", "my_category_tools.json"),
    # ...
}
```

**Rules:**

- Key = category name (used for filtering in `list_tools`, `grep_tools`)
- Value = absolute path to the JSON file from Link 1
- If this line is missing, the JSON file is never read and the tools never load
- Multiple JSON files can exist under different categories
- Remote tools in `data/remote_tools/` are auto-scanned — they DON'T need an entry here

## Link 5: Wrapper stub

**File:** `src/tooluniverse/tools/<tool_name>.py`

A thin Python function that the MCP server exposes. Every tool needs
one. The pattern is identical for all tools — only the name, params,
and docstring change.

```python
"""
my_tool_name

One sentence description matching the JSON.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def my_tool_name(
    query: str,
    limit: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    One sentence description matching the JSON.

    Parameters
    ----------
    query : str
        What to search for
    limit : int
        Max results (default 10)
    """
    _args = {k: v for k, v in {
        "query": query,
        "limit": limit,
    }.items() if v is not None}
    return get_shared_client().run_one_function(
        {
            "name": "my_tool_name",
            "arguments": _args,
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["my_tool_name"]
```

**Rules:**

- Filename = tool name from JSON (exact match, including case)
- Function name = tool name from JSON (exact match)
- Function params mirror the JSON `parameter.properties`
- Required JSON params become required function args (no default)
- Optional JSON params get defaults matching the JSON `default` values
- All params are stripped of None before passing to `run_one_function`
- `stream_callback`, `use_cache`, `validate` are keyword-only (after `*`)
- `__all__` must export the function name
- `_shared_client.get_shared_client()` returns a singleton ToolUniverse instance

## Link 6: `__init__.py` import

**File:** `src/tooluniverse/tools/__init__.py`

Import the stub and add to `__all__`. Two places to edit.

```python
# Near the top, with other imports (alphabetical by module name):
from .my_tool_name import my_tool_name

# In the __all__ list (alphabetical):
__all__ = [
    # ...
    "my_tool_name",
    # ...
]
```

**Rules:**

- Import from the stub module (Link 5)
- Add to `__all__`
- Both alphabetically sorted
- If missing, the MCP server can't discover the function

## Verification

After completing all 6 links, verify end-to-end:

```python
# Quick test — does it load and accept (bad) input?
python3 -c "
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()
result = tu.run({'name': 'my_tool_name', 'arguments': {}})
print(result)
# Should print a validation error (missing required param), NOT 'tool not found'
"
```

If you get a validation error, all 6 links are working. If you get
"tool not found" or silence, one of the links is broken — check them
in reverse order (Link 6 first, then 5, 4, 3, 2, 1).

## Debugging silent failures

| Symptom | Broken link | Fix |
|---------|------------|-----|
| `grep_tools` finds nothing | Link 3 or 4 | Add lazy registry entry and/or default_config category |
| `grep_tools` finds it but `execute_tool` fails with "unknown type" | Link 3 | Add type->module mapping to lazy registry |
| `execute_tool` fails with import error | Link 2 | Fix the Python module (syntax, missing dependency) |
| Tool loads in Python but not via MCP | Link 5 or 6 | Create wrapper stub and add to `__init__.py` |
| Tool loads but wrong params | Link 1 | Fix the JSON parameter schema |
| Tool loads but returns wrong data | Link 2 | Fix the `run()` method |

## Real example: adding `USPTO_get_patent_claims`

**Link 1:** `src/tooluniverse/data/patent_claims_tools.json`

```json
[{
  "type": "PatentClaimsTool",
  "name": "USPTO_get_patent_claims",
  "description": "Extract the full text of every claim from a granted US patent...",
  "parameter": {
    "type": "object",
    "properties": {
      "applicationNumberText": {"type": "string", "description": "..."},
      "patent_number": {"type": "string", "description": "..."}
    },
    "required": []
  },
  "required_api_keys": ["USPTO_API_KEY"]
}]
```

**Link 2:** `src/tooluniverse/patent_claims_tool.py`

```python
@register_tool("PatentClaimsTool")
class PatentClaimsTool(BaseTool):
    def __init__(self, tool_config, api_key=None):
        super().__init__(tool_config)
        # ...
    def run(self, arguments):
        # Download grant XML, parse <claim> elements
        # ...
```

**Link 3:** `src/tooluniverse/_lazy_registry_static.py`

```python
"PatentClaimsTool": "patent_claims_tool",
```

**Link 4:** `src/tooluniverse/default_config.py`

```python
"patent_claims": os.path.join(current_dir, "data", "patent_claims_tools.json"),
```

**Link 5:** `src/tooluniverse/tools/USPTO_get_patent_claims.py`

```python
def USPTO_get_patent_claims(
    applicationNumberText=None, patent_number=None, *,
    stream_callback=None, use_cache=False, validate=True,
):
    _args = {k: v for k, v in {
        "applicationNumberText": applicationNumberText,
        "patent_number": patent_number,
    }.items() if v is not None}
    return get_shared_client().run_one_function(
        {"name": "USPTO_get_patent_claims", "arguments": _args},
        stream_callback=stream_callback, use_cache=use_cache, validate=validate,
    )
```

**Link 6:** `src/tooluniverse/tools/__init__.py`

```python
from .USPTO_get_patent_claims import USPTO_get_patent_claims
# ...
__all__ = [
    # ...
    "USPTO_get_patent_claims",
    # ...
]
```

## Remote tools (Tier 1 downloaders)

Remote tools skip Links 2-3. They use the generic `RemoteTool` type
which is already registered. Instead they need:

- Link 1: JSON in `src/tooluniverse/data/remote_tools/` with `remote_info` field
- Link 4: Auto-scanned from `data/remote_tools/` directory (no config entry needed)
- Links 5-6: NOT needed (remote tools aren't exposed as Python stubs)

The `remote_info` field specifies the MCP server URL and transport.
The remote MCP server must be running separately.

## Composite tools (tools that call other tools)

Tools like `USPTO_patent_deep_lookup` call other tools internally.
Use lazy imports inside methods to avoid circular dependencies:

```python
def _fetch_claims(self, app_number):
    from .patent_claims_tool import PatentClaimsTool  # lazy import
    tool = PatentClaimsTool({"name": "..."}, api_key=self.api_key)
    return tool.run({"applicationNumberText": app_number})
```

## `.tool_metadata.json`

`src/tooluniverse/tools/.tool_metadata.json` is a hash map
(tool_name -> content_hash) used for cache invalidation of generated
stubs. It's updated automatically when stubs are regenerated. If a
tool name is missing from this file, the stub may be stale.

## File naming conventions

| What | Pattern | Example |
|------|---------|---------|
| JSON config | `<category>_tools.json` | `patent_claims_tools.json` |
| Implementation | `<module_name>.py` | `patent_claims_tool.py` |
| Wrapper stub | `<tool_name>.py` | `USPTO_get_patent_claims.py` |
| Tests | `test_<module_name>.py` | `test_patent_claims_tool.py` |

Note: JSON file and implementation module have DIFFERENT names.
The JSON file is named after the category. The module is named after
the tool type. The stub is named after the tool name. Keep them
straight.
