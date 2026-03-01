---
name: devtu-create-tool
description: Create new scientific tools for ToolUniverse framework with proper structure, validation, and testing. Use when users need to add tools to ToolUniverse, implement new API integrations, create tool wrappers for scientific databases/services, expand ToolUniverse capabilities, or follow ToolUniverse contribution guidelines. Supports creating tool classes, JSON configurations, validation, error handling, and test examples. IMPORTANT: Before creating a new tool, verify no equivalent tool exists — use mcp__tooluniverse__grep_tools and mcp__tooluniverse__find_tools first.
---

# ToolUniverse Tool Creator

Create new scientific tools for the ToolUniverse framework following established best practices.

**BEFORE CREATING**: Always verify no equivalent tool exists:
```
mcp__tooluniverse__grep_tools(pattern="[api_or_database_name]")
mcp__tooluniverse__find_tools(query="[intended functionality]", limit=10)
```
Creating a duplicate tool wastes effort and adds maintenance burden. If a similar tool exists, use `devtu-fix-tool` instead.

---

## Workflow (Phase-Based)

### Phase 1: Create the Tool Class

File: `src/tooluniverse/my_api_tool.py`

```python
from typing import Dict, Any
from tooluniverse.tool import BaseTool
from tooluniverse.tool_utils import register_tool
import requests

@register_tool("MyAPITool")
class MyAPITool(BaseTool):
    """Tool for MyAPI database."""

    BASE_URL = "https://api.example.com/v1"

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.parameter = tool_config.get("parameter", {})
        self.required = self.parameter.get("required", [])

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        operation = arguments.get("operation")
        if not operation:
            return {"status": "error", "error": "Missing: operation"}
        if operation == "search":
            return self._search(arguments)
        elif operation == "get_item":
            return self._get_item(arguments)
        return {"status": "error", "error": f"Unknown operation: {operation}"}

    def _search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        query = arguments.get("query")
        if not query:
            return {"status": "error", "error": "Missing: query"}
        try:
            response = requests.get(
                f"{self.BASE_URL}/search",
                params={"q": query, "limit": arguments.get("limit", 20)},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return {"status": "success", "data": data.get("results", []), "count": data.get("count", 0)}
        except requests.exceptions.Timeout:
            return {"status": "error", "error": "Timeout after 30s"}
        except requests.exceptions.HTTPError as e:
            return {"status": "error", "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_item(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        item_id = arguments.get("item_id")
        if not item_id:
            return {"status": "error", "error": "Missing: item_id"}
        try:
            response = requests.get(f"{self.BASE_URL}/items/{item_id}", timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
```

**Key rules:**
- Inherit from `BaseTool`, decorate with `@register_tool("ClassName")`
- `run()` must never raise — always return `{"status": "error", "error": "..."}` on failure
- Set `timeout=30` on all HTTP requests
- Catch specific exceptions: `Timeout`, `HTTPError`, `ConnectionError`

For async/polling, offline/computational, GraphQL, and caching patterns see [references/advanced-patterns.md](references/advanced-patterns.md).

---

### Phase 2: Create the JSON Config

File: `src/tooluniverse/data/my_api_tools.json`

```json
[
  {
    "name": "MyAPI_search",
    "class": "MyAPITool",
    "description": "Search MyAPI database. Returns up to 100 items with IDs and names. Supports partial text matching. Example: query='protein' finds all protein-related records.",
    "parameter": {
      "type": "object",
      "required": ["operation"],
      "properties": {
        "operation": {"const": "search", "description": "Operation type (fixed)"},
        "query": {"type": "string", "description": "Search term"},
        "limit": {"type": ["integer", "null"], "description": "Max results (1-100)", "minimum": 1, "maximum": 100}
      }
    },
    "return_schema": {
      "type": "object",
      "properties": {
        "status": {"type": "string", "enum": ["success", "error"]},
        "data": {"type": "array", "items": {"type": "object", "additionalProperties": true}},
        "count": {"type": "integer"},
        "error": {"type": "string"}
      },
      "required": ["status"]
    },
    "test_examples": [
      {"operation": "search", "query": "protein"}
    ]
  }
]
```

**JSON conventions:**
- `"class"` (or `"type"`) must match the `@register_tool` name exactly (case-sensitive)
- Tool name ≤55 chars for MCP compatibility. Template: `{API}_{action}_{target}`
- Description: 150-250 chars; include what it returns, data source, input format, example
- `test_examples`: use REAL IDs from API docs — never placeholders like `"TEST123"` or `"example_id"`
- All optional parameters and all mutually exclusive parameters must be nullable: `"type": ["string", "null"]`
- Avoid giant `enum` lists in schema; document allowed values in `description` instead
- Do not add `examples` blocks inside `parameter` or `return_schema` — they bloat configs

For full JSON config templates see [references/templates.md](references/templates.md).

---

### Phase 3: Register in default_config.py

**This step is the #1 cause of tools silently not loading.**

Edit `src/tooluniverse/default_config.py`:

```python
TOOLS_CONFIGS = {
    # ... existing entries ...
    "my_api": os.path.join(current_dir, "data", "my_api_tools.json"),
}
```

Verify:
```bash
grep "my_api" src/tooluniverse/default_config.py
```

---

### Phase 4: Generate Wrappers and Verify Registration

```bash
# Generate wrappers (auto-creates src/tooluniverse/tools/MyAPI_*.py)
PYTHONPATH=src python3 -m tooluniverse.generate_tools --force

# Verify all 3 registration steps passed
python3 -c "
import sys; sys.path.insert(0, 'src')
from tooluniverse.tool_registry import get_tool_registry
import tooluniverse.my_api_tool
assert 'MyAPITool' in get_tool_registry(), 'Step 1 FAILED: class not registered'
from tooluniverse.default_config import TOOLS_CONFIGS
assert 'my_api' in TOOLS_CONFIGS, 'Step 2 FAILED: not in default_config'
from tooluniverse import ToolUniverse
tu = ToolUniverse(); tu.load_tools()
assert hasattr(tu.tools, 'MyAPI_search'), 'Step 3 FAILED: wrapper not generated'
print('All 3 registration steps OK')
"
```

---

### Phase 5: Write Tests

File: `tests/tools/test_my_api_tool.py`

**Level 1 — Direct class (tests implementation logic):**
```python
import json
from tooluniverse.my_api_tool import MyAPITool

def test_direct_search():
    with open("src/tooluniverse/data/my_api_tools.json") as f:
        config = next(t for t in json.load(f) if t["name"] == "MyAPI_search")
    tool = MyAPITool(config)
    result = tool.run({"operation": "search", "query": "protein"})
    assert result["status"] in ("success", "error")  # API may be unavailable in CI
    if result["status"] == "success":
        assert "data" in result
```

**Level 2 — ToolUniverse interface (tests registration):**
```python
import pytest
from tooluniverse import ToolUniverse

@pytest.fixture(scope="module")
def tu():
    tu = ToolUniverse()
    tu.load_tools()
    return tu

def test_tool_registered(tu):
    assert hasattr(tu.tools, "MyAPI_search")

def test_missing_required_param(tu):
    result = tu.run_tool("MyAPI_search", {"operation": "search"})  # missing query
    assert result["status"] == "error"
```

**Level 3 — Real API (optional, skip in CI):**
```python
@pytest.mark.skipif(not os.environ.get("RUN_REAL_API"), reason="real API test")
def test_real_search(tu):
    result = tu.run_tool("MyAPI_search", {"operation": "search", "query": "TP53"})
    assert result["status"] == "success"
    assert "data" in result
```

---

### Phase 6: Final Validation (MANDATORY)

```bash
# Validate JSON syntax
python3 -m json.tool src/tooluniverse/data/my_api_tools.json

# Check Python syntax
python3 -m py_compile src/tooluniverse/my_api_tool.py

# Run unit tests
pytest tests/tools/test_my_api_tool.py -v

# MANDATORY: test_new_tools.py validates test_examples against return_schema
python scripts/test_new_tools.py MyAPI_search -v
python scripts/test_new_tools.py MyAPI -v  # all tools in category

# Check tool name lengths
python scripts/check_tool_name_lengths.py --test-shortening
```

**Common `test_new_tools.py` failures:**

| Failure | Cause | Fix |
|---------|-------|-----|
| 404 ERROR | Invalid ID in `test_examples` | Use real IDs from API docs |
| Schema Mismatch | Response doesn't match `return_schema` | Update schema or fix response format |
| Exception raised | Code bug or missing dependency | Check error message, fix `run()` |

---

## Known Gotchas

### 1. Mutually Exclusive / Optional Parameters Must Be Nullable

When a parameter is optional OR mutually exclusive with another (user provides one OR the other), passing `None` for the unused one triggers schema validation failure: `"None is not of type 'integer'"`.

**Wrong:**
```json
"id":   {"type": "integer"},
"name": {"type": "string"}
```

**Correct:**
```json
"id":   {"type": ["integer", "null"]},
"name": {"type": ["string", "null"]}
```

This affects 60% of new tools in 2026. Always check: if a param isn't in `"required"`, make it nullable.

### 2. Schema Validates the `data` Field, Not the Full Response

`return_schema` (and `test_new_tools.py`) validates the structure of the tool's response dict. If your tool wraps upstream data in an envelope (`{"status": ..., "data": ...}`), your schema must reflect the envelope shape — not just the inner upstream payload.

```json
"return_schema": {
  "type": "object",
  "properties": {
    "status": {"type": "string"},
    "data": {"type": "array", "items": {"type": "object"}},
    "error": {"type": "string"}
  }
}
```

### 3. Missing `default_config.py` Entry Silently Drops All Tools

Tools don't produce an error if Step 3 is skipped — they simply never appear. Always verify with `grep "my_category" src/tooluniverse/default_config.py`.

### 4. Never Raise Exceptions in `run()`

Any uncaught exception causes the entire MCP tool call to fail (no graceful error). Always wrap the body of `run()` in try/except and return `{"status": "error", "error": str(e)}`.

### 5. `test_examples` Must Use Real IDs

`test_new_tools.py` actually executes the tool with each `test_examples` entry. Fake IDs like `"XXXXX"` will produce 404 errors. Look up a real identifier from the API documentation.

### 6. `"class"` vs `"type"` Field in JSON

Some older configs use `"type"` to reference the Python class; newer ones use `"class"`. Either is valid but must match the `@register_tool("ClassName")` string exactly (case-sensitive).

### 7. Auto-Generated Wrappers Must Not Be Edited

Files in `src/tooluniverse/tools/MyAPI_*.py` are regenerated on every `tu build` / `load_tools()`. Manual edits are overwritten.

### 8. Optional API Keys: Use Env Vars, Never Parameters

For APIs that work without a key but have better rate limits with one, use `optional_api_keys` in the JSON config and read the key from `os.environ` inside `__init__`. Never add `api_key` as a tool parameter.

```json
{"name": "PubMed_search", "optional_api_keys": ["NCBI_API_KEY"], ...}
```

```python
self.api_key = os.environ.get("NCBI_API_KEY", "")
```

---

## Complete Workflow Checklist

1. `grep_tools` / `find_tools` — confirm no duplicate exists
2. Create `src/tooluniverse/my_api_tool.py` with `@register_tool`
3. Create `src/tooluniverse/data/my_api_tools.json` with real `test_examples` and `return_schema`
4. Add entry to `src/tooluniverse/default_config.py`
5. Run `PYTHONPATH=src python3 -m tooluniverse.generate_tools --force`
6. Verify all 3 registration steps (class / config / wrappers)
7. Write and run Level 1 tests (direct class)
8. Write and run Level 2 tests (ToolUniverse interface)
9. Run `python scripts/test_new_tools.py MyAPI -v` — fix all failures
10. Run `python scripts/check_tool_name_lengths.py --test-shortening`
11. Create `examples/my_api_examples.py`

---

## Success Criteria

- All 3 registration steps verified
- Level 1 and Level 2 tests passing
- `test_new_tools.py` passes with 0 failures (mandatory)
- Tool names are ≤55 characters
- `test_examples` use real IDs
- Standard `{"status": ..., "data": ...}` response format
- No raised exceptions in `run()`
- All HTTP requests have `timeout=30`

---

## Quick Command Reference

```bash
# Validate JSON
python3 -m json.tool src/tooluniverse/data/your_tools.json

# Check Python syntax
python3 -m py_compile src/tooluniverse/your_tool.py

# Verify registration in default_config
grep "your_category" src/tooluniverse/default_config.py

# Generate wrappers
PYTHONPATH=src python3 -m tooluniverse.generate_tools --force

# List generated wrappers
ls src/tooluniverse/tools/YourCategory_*.py

# Run unit tests
pytest tests/tools/test_your_tool.py -v

# MANDATORY: final validation
python scripts/test_new_tools.py your_tool_name -v
```

---

## Reference

| Topic | File |
|-------|------|
| Full JSON config templates (search, detail, paginated) | [references/templates.md](references/templates.md) |
| Offline/computational tools, GraphQL, caching, batch, pagination patterns | [references/advanced-patterns.md](references/advanced-patterns.md) |
| Tool improvement and maintenance checklist (phases 1-7) | [references/implementation-guide.md](references/implementation-guide.md) |
| Quick HTTP/schema/validation snippets | [references/quick-reference.md](references/quick-reference.md) |
| Tool improvement checklist | [references/tool-improvement-checklist.md](references/tool-improvement-checklist.md) |
