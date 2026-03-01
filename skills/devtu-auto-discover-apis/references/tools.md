# devtu-auto-discover-apis Reference

Detailed parameter tables, templates, and scoring matrices for the devtu-auto-discover-apis skill.
For the workflow steps, see [SKILL.md](../SKILL.md).

---

## API Scoring Matrix

Score each discovered API on the following criteria (0–100 points total):

| Criterion | Max Points | Scoring Guide |
|---|---|---|
| Documentation Quality | 20 | OpenAPI/Swagger spec = 20; detailed prose docs = 15; basic docs = 10; poor/absent = 5 |
| API Stability | 15 | Versioned + stable SLA = 15; versioned = 10; unversioned = 5 |
| Authentication | 15 | Public or API-key = 15; OAuth = 10; complex/proprietary = 5 |
| Coverage | 15 | Comprehensive endpoints = 15; good = 10; limited = 5 |
| Maintenance | 10 | Updated within 6 months = 10; 6–18 months = 6; stale = 2 |
| Community | 10 | High citations or GitHub stars = 10; moderate = 6; unknown = 2 |
| License | 10 | Open or academic-use = 10; free commercial = 7; restricted = 3 |
| Rate Limits | 5 | Generous (>100 req/min) = 5; moderate = 3; restrictive = 1 |

Prioritization: High (≥70), Medium (50–69), Low (<50).

---

## Python Class Template

```python
from typing import Dict, Any
from tooluniverse.tool import BaseTool
from tooluniverse.tool_utils import register_tool
import requests
import os


@register_tool("[APIName]Tool")
class [APIName]Tool(BaseTool):
    """Tool for [API Name] — [one-line description]."""

    BASE_URL = "[API base URL without trailing slash]"

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.parameter = tool_config.get("parameter", {})
        self.required = self.parameter.get("required", [])
        # Optional key: omit the check if the key is required
        self.api_key = os.environ.get("[API_KEY_ENV_VAR]", "")

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route to the correct operation handler."""
        operation = arguments.get("operation")
        if not operation:
            return {"status": "error", "error": "Missing required parameter: operation"}

        if operation == "operation1":
            return self._operation1(arguments)
        elif operation == "operation2":
            return self._operation2(arguments)
        else:
            return {"status": "error", "error": f"Unknown operation: {operation}"}

    def _operation1(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch [resource] by [identifier]."""
        param1 = arguments.get("param1")
        if not param1:
            return {"status": "error", "error": "Missing required parameter: param1"}

        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.get(
                f"{self.BASE_URL}/endpoint",
                params={"param1": param1},
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "status": "success",
                "data": data.get("results", []),
                "metadata": {
                    "total": data.get("total", 0),
                    "source": "[API Name]",
                },
            }

        except requests.exceptions.Timeout:
            return {"status": "error", "error": "API timeout after 30 seconds"}
        except requests.exceptions.HTTPError as e:
            return {
                "status": "error",
                "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}",
            }
        except requests.exceptions.ConnectionError:
            return {"status": "error", "error": "Cannot connect to [API Name] API"}
        except Exception as e:
            return {"status": "error", "error": f"Unexpected error: {str(e)}"}
```

### Key Rules for the Python Class

- Never raise exceptions inside `run()` or handler methods. Always return an error dict.
- Always set `timeout=30` (or higher for slow APIs) on every HTTP call.
- Wrap the raw API response in a `data` key in the success return.
- For required API keys, raise `ValueError` in `__init__` and set `required_api_keys` in JSON.
- For optional API keys, read with a default of `""` and include them in headers only when non-empty.

### Async Polling Pattern

For job-based APIs (submit → poll → retrieve):

```python
def _submit_job(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    import time

    # Submit
    submit_resp = requests.post(
        f"{self.BASE_URL}/jobs",
        json={"data": arguments.get("data")},
        timeout=30,
    )
    submit_resp.raise_for_status()
    job_id = submit_resp.json().get("job_id")

    # Poll with a timeout ceiling
    for _ in range(60):  # 2 minutes maximum
        status_resp = requests.get(f"{self.BASE_URL}/jobs/{job_id}", timeout=30)
        result = status_resp.json()
        if result.get("status") == "completed":
            return {"status": "success", "data": result.get("results")}
        if result.get("status") == "failed":
            return {"status": "error", "error": result.get("error")}
        time.sleep(2)

    return {"status": "error", "error": "Job timeout after 2 minutes"}
```

### Pagination Pattern

```python
def _list_all(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    all_results = []
    page = 1

    while True:
        response = requests.get(
            f"{self.BASE_URL}/items",
            params={"page": page, "limit": 100},
            timeout=30,
        )
        data = response.json()
        results = data.get("results", [])
        if not results:
            break
        all_results.extend(results)
        if len(results) < 100:
            break
        page += 1

    return {
        "status": "success",
        "data": all_results,
        "metadata": {"total_pages": page, "total_items": len(all_results)},
    }
```

---

## JSON Config Template

```json
[
  {
    "name": "[APIName]_operation1",
    "class": "[APIName]Tool",
    "description": "[What it does]. Returns [data format]. [Input format and constraints]. Example: [concrete example with real values]. [Special notes or rate limit info].",
    "parameter": {
      "type": "object",
      "required": ["operation", "param1"],
      "properties": {
        "operation": {
          "const": "operation1",
          "description": "Operation identifier (fixed)"
        },
        "param1": {
          "type": "string",
          "description": "Description with format, constraints, and an example value"
        },
        "optional_param": {
          "type": ["string", "null"],
          "description": "Optional filter; omit or pass null to use default",
          "default": null
        }
      }
    },
    "return_schema": {
      "oneOf": [
        {
          "type": "object",
          "properties": {
            "status": {"type": "string", "const": "success"},
            "data": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "id": {"type": "string"},
                  "name": {"type": "string"}
                }
              }
            },
            "metadata": {
              "type": "object",
              "properties": {
                "total": {"type": "integer"},
                "source": {"type": "string"}
              }
            }
          },
          "required": ["status", "data"]
        },
        {
          "type": "object",
          "properties": {
            "status": {"type": "string", "const": "error"},
            "error": {"type": "string"}
          },
          "required": ["status", "error"]
        }
      ]
    },
    "test_examples": [
      {
        "operation": "operation1",
        "param1": "REAL_VALUE_FROM_API"
      }
    ]
  }
]
```

### JSON Config Rules

| Field | Constraint | Notes |
|---|---|---|
| `name` | ≤55 characters | MCP compatibility limit |
| `description` | 150–250 characters | Cover: what, return format, input, example, special notes |
| `return_schema` | Must use `oneOf` | Two schemas: success (with `data`) and error (with `error`) |
| `test_examples` | Real values only | No: TEST, DUMMY, PLACEHOLDER, EXAMPLE, your_, sample_, xxx |
| Mutually exclusive params | `{"type": ["string", "null"]}` | Required to avoid validation errors |

---

## Authentication Configuration

### Public API
No special configuration. Do not add auth headers or environment variable references.

### Optional API Key

In the Python class `__init__`:
```python
self.api_key = os.environ.get("MYAPI_KEY", "")
```

In the request:
```python
headers = {}
if self.api_key:
    headers["Authorization"] = f"Bearer {self.api_key}"
```

In the JSON config description field, append:
```
Rate limits: 3 req/sec without key, 10 req/sec with MYAPI_KEY.
```

### Required API Key

In the Python class `__init__`:
```python
self.api_key = os.environ.get("MYAPI_KEY")
if not self.api_key:
    raise ValueError("MYAPI_KEY environment variable is required")
```

In the JSON config, add at the top level:
```json
"required_api_keys": ["MYAPI_KEY"]
```

### OAuth (Complex)

Document the manual setup in the skill README. Store tokens in environment variables. Implement token refresh logic in the tool class. Consider whether the complexity is worth the benefit before proceeding.

---

## PR Description Template

```markdown
## Add [API Name] tools for [domain]

### Summary
- Adds X tools integrating [API Name] for [domain] research
- Addresses critical/moderate gap: [domain] had only N tools before
- API: [one-line description of what the API provides]

### API Details
| Field | Value |
|---|---|
| Base URL | [URL] |
| Documentation | [URL] |
| Authentication | [public / API key (optional) / API key (required)] |
| Rate Limits | [e.g., 10 req/sec] |
| License | [open / academic / commercial] |
| Discovery Score | [N]/100 |

### Tools Added
| Tool Name | Operation | Description |
|---|---|---|
| [APIName]_operation1 | operation1 | [Brief description] |
| [APIName]_operation2 | operation2 | [Brief description] |

### Validation Results
- All tests passing: X/X (100%)
- Schema validation: all tools have oneOf with data wrapper
- Test examples: real IDs verified against live API
- devtu compliance checklist: complete

### Files Changed
- `src/tooluniverse/[api_name]_tool.py`
- `src/tooluniverse/data/[api_name]_tools.json`
- `src/tooluniverse/default_config.py`

### Checklist
- [ ] All tests passing
- [ ] Schema validation complete
- [ ] Real test examples (no placeholders)
- [ ] Tool names ≤55 characters
- [ ] default_config.py updated
- [ ] Error handling comprehensive
- [ ] Authentication documented

### Discovery Context
[Brief note on why this API was prioritized — discovery score rationale, gap it fills]
```

---

## ToolUniverse MCP Tool Parameters

### mcp__tooluniverse__grep_tools

| Parameter | Type | Description |
|---|---|---|
| `pattern` | string | Text or regex to match against tool names or descriptions |
| `field` | string (optional) | Restrict to: `name`, `description`, `type`, or `category` |
| `search_mode` | string (optional) | `text` (default) or `regex` |
| `limit` | integer (optional) | Max results to return (default 100) |
| `categories` | array (optional) | Filter by category list |

### mcp__tooluniverse__find_tools

| Parameter | Type | Description |
|---|---|---|
| `query` | string | Natural-language description of the desired functionality |
| `limit` | integer (optional) | Max results (default 10) |
| `categories` | array (optional) | Filter by category list |
| `use_advanced_search` | boolean (optional) | Use AI-powered search (default true) |
| `search_method` | string (optional) | `auto`, `llm`, `embedding`, or `keyword` |

### mcp__tooluniverse__list_tools

| Parameter | Type | Description |
|---|---|---|
| `mode` | string (optional) | `names` (default), `basic`, `categories`, `by_category`, `summary`, `custom` |
| `categories` | array (optional) | Filter by category list |
| `group_by_category` | boolean (optional) | Group results by category |
| `limit` | integer (optional) | Max entries to return |
| `offset` | integer (optional) | Pagination offset |

### mcp__tooluniverse__get_tool_info

| Parameter | Type | Description |
|---|---|---|
| `tool_names` | string or array | Single tool name or list of tool names |
| `detail_level` | string (optional) | `description` (text only) or `full` (includes parameter schema) |

### mcp__tooluniverse__execute_tool

| Parameter | Type | Description |
|---|---|---|
| `tool_name` | string | Name of the tool to execute |
| `arguments` | object or string (optional) | Tool arguments as a JSON object or JSON string |

---

## Validation Checklist

Use this checklist before moving from Phase 3 to Phase 4.

**Schema**
- [ ] `return_schema` has `oneOf` at the top level
- [ ] `oneOf[0]` (success) has `data` in `properties` and `status` in `required`
- [ ] `oneOf[1]` (error) has `error` in `properties` and `error` in `required`
- [ ] All mutually exclusive params use nullable types

**test_examples**
- [ ] No string values matching: test, dummy, placeholder, example, sample, xxx, temp, fake, mock, your_
- [ ] At least one example per tool
- [ ] Examples verified against live API (returned 200 OK)

**Tool Loading**
- [ ] `@register_tool("ClassName")` present on class
- [ ] Class name in `get_tool_registry()` after import
- [ ] Category key present in `TOOLS_CONFIGS` in `default_config.py`
- [ ] `ToolUniverse().load_tools()` produces expected wrapper attributes

**API Behavior**
- [ ] `run()` never raises exceptions (all paths return dicts)
- [ ] All HTTP calls have `timeout` set
- [ ] Specific exceptions caught: Timeout, HTTPError, ConnectionError
- [ ] Tool names are 55 characters or fewer

**devtu Compliance**
1. [ ] Tool loading verified (3-step registration)
2. [ ] API behavior verified against documentation
3. [ ] No error patterns detected (exceptions in run, missing data wrapper)
4. [ ] Schema validation passing
5. [ ] Test examples use real identifiers
6. [ ] All parameter names match API requirements
