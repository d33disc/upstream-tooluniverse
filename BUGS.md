# ToolUniverse — Open Bugs & Test Failures

> Generated: 2026-02-24
> Repo: `mims-harvard/ToolUniverse`, branch `local`
> Test command: `python -m pytest tests/ --ignore=tests/integration --ignore=tests/test_database_setup --ignore=tests/unit --ignore=tests/examples`
> Result: **494 passed, 35 failed, 6 errors**

---

## 1. Test Failures

### 1.1 `tests/tools/test_simbad_tool.py` — 11 failures

**Root cause:** The tests were written against an old response format. The SIMBAD tool now returns a structured `{"status": "...", "data": {...}}` envelope, but the tests check for top-level `"error"` and `"success"` keys that no longer exist at that level.

**Two failure patterns:**

**Pattern A — wrong key for errors (8 tests):**
```python
# Test does:
assert "error" in result          # FAILS

# Tool actually returns:
{"status": "error", "data": {"error": "object_name parameter is required ..."}}
# Fix: assert result["status"] == "error"  OR  assert "error" in result["data"]
```

Affected tests:
- `test_query_by_name_missing_object_name`
- `test_query_by_coordinates_missing_ra`
- `test_query_by_coordinates_missing_dec`
- `test_query_by_identifier_missing_identifier`
- `test_execute_query_timeout`, `test_execute_query_network_error`
- `test_execute_query_not_found`, `test_execute_query_empty_result`
- `test_run_missing_adql_query`, `test_run_timeout`, `test_run_network_error`

**Pattern B — missing `success` key (7 tests):**
```python
# Test does:
assert result["success"] is True   # KeyError: 'success'

# Tool actually returns:
{"status": "success", "data": {...}}
# Fix: assert result["status"] == "success"
```

Affected tests:
- `test_execute_query_success`, `test_execute_query_with_metadata_lines`
- `test_execute_query_with_max_results`, `test_execute_query_parses_multiple_fields`
- `test_run_success_json`, `test_run_success_votable`, `test_run_default_format`
- `test_run_json_parse_error`

**Files to fix:**
- `tests/tools/test_simbad_tool.py` — update all assertions to use `result["status"]` and `result["data"]`

---

### 1.2 `tests/tools/test_umls_tool.py` — 2 failures

**Root cause:** The UMLS API response no longer contains `"ICD"` or `"SNOMED"` in the `rootSource` field of returned results (API behavior change or wrong assertion).

```
FAILED test_icd_search_codes
  assert any("ICD" in r.get("rootSource", "") for r in results)  →  False

FAILED test_snomed_search_concepts
  assert any("SNOMED" in r.get("rootSource", "") for r in results)  →  False
```

**Files to fix:**
- `tests/tools/test_umls_tool.py` — check what the UMLS API actually returns in `rootSource` and update the assertions accordingly. The API may use `"ICD10CM"` or `"SNOMEDCT_US"` as the source string rather than `"ICD"` / `"SNOMED"`.

---

### 1.3 `tests/tools/test_genomics_tools.py` — 6 errors (setup crash)

**Root cause:** Hardcoded absolute path pointing to the wrong directory. The path references `ToolUniverse` (old clone) but the current repo is `ToolUniverse-local`.

```python
# test_genomics_tools.py:32
config_path = '/Users/shgao/logs/25.05.28tooluniverse/ToolUniverse/src/tooluniverse/data/genomics_tools.json'
# FileNotFoundError — path does not exist
```

**Fix:**
- `tests/tools/test_genomics_tools.py` — replace the hardcoded path with a path relative to the repo root, e.g.:
```python
import tooluniverse
config_path = Path(tooluniverse.__file__).parent / "data" / "genomics_tools.json"
```

---

### 1.4 `tests/examples/test_local_tools_tooluniverse_integration.py` — syntax error (collection crash)

**Root cause:** `except` block placed after `finally`, which is invalid Python syntax. The file never runs.

```python
# Line 115-121
    finally:
        if 'tu' in locals():
            tu.close()

    except Exception as e:        # ← SyntaxError: except after finally
        print(f"❌ ToolUniverse initialization failed: {e}")
        return False
```

**Fix:**
- `tests/examples/test_local_tools_tooluniverse_integration.py:115-121` — restructure to `try/except/finally` (except must come before finally).

---

## 2. Unfixed Architectural Bugs

These are design-level issues that require a process restart to work around. They were found during a robustness audit but not fixed because they require larger refactors.

---

### Bug A — Static lazy registry is stale after adding new built-in tools

**Severity:** High
**File:** `src/tooluniverse/_lazy_registry_static.py`, `src/tooluniverse/tool_registry.py:354–366`

When a new `.py` tool class is added to `src/tooluniverse/tools/`, the static lazy registry (`_lazy_registry_static.py`) must be manually regenerated. If it isn't, the new tool's class cannot be found at execution time even if its JSON config loads correctly. The AST fallback is only reached if the static file is completely absent — not if it is merely incomplete.

**Workaround:** Regenerate the static registry (run `build_optimizer.py`) after adding any new built-in tool file.
**Proper fix:** Compare the static file's tool list against files on disk at startup and fall back to AST discovery for any missing entries.

---

### Bug B — Entry-point plugins are discovered only once per process

**Severity:** Medium
**File:** `src/tooluniverse/tool_registry.py:438–553`

`_discover_entry_point_plugins()` uses a global `_discovered_plugin_names` set that is never cleared. If a new plugin package is installed via `pip install` while the server is running, the new entry point is silently skipped on subsequent calls.

**Workaround:** Restart the server after installing a new plugin package.
**Proper fix:** Clear `_discovered_plugin_names` when a forced re-scan is needed, or expose a `force=True` parameter on `_discover_entry_point_plugins()`.

---

### Bug C — Editing an existing workspace Python tool file has no effect without restart

**Severity:** Medium
**File:** `src/tooluniverse/execute_function.py:1298–1305`

User Python tool files in `.tooluniverse/tools/` are loaded into `sys.modules` under a name derived from the file path hash. On subsequent `load_tools()` / `refresh_tools()` calls, the code checks `if module_name in sys.modules` and skips re-import. This means edits to an existing file are invisible until the process restarts.

Note: adding a *new* file works fine because the module name is new.

**Workaround:** Restart the server (or temporarily rename the file to bust the hash).
**Proper fix:** Compare the file's `mtime` or content hash to the cached module and call `importlib.reload()` when the file changed.

---

### Bug D — Lazy module cache (`_lazy_cache`) never invalidated

**Severity:** Medium
**File:** `src/tooluniverse/tool_registry.py:165–173`

`lazy_import_tool()` caches imported modules in the module-global `_lazy_cache` dict. Once cached, the module is returned on every subsequent call with no check for whether the source file has changed. Editing a built-in tool module in `src/tooluniverse/tools/` requires a restart.

**Workaround:** Restart the server.
**Proper fix:** Add an `mtime`-based invalidation check, or expose a `clear_lazy_cache()` helper for dev environments.

---

## 3. Summary Table

| # | Location | Type | Severity | Needs restart? | Status |
|---|---|---|---|---|---|
| 1.1 | `tests/tools/test_simbad_tool.py` | Wrong response format in tests | — | — | **Unfixed** |
| 1.2 | `tests/tools/test_umls_tool.py` | API `rootSource` assertion stale | — | — | **Unfixed** |
| 1.3 | `tests/tools/test_genomics_tools.py` | Hardcoded absolute path | — | — | **Unfixed** |
| 1.4 | `tests/examples/test_local_tools_tooluniverse_integration.py` | `except` after `finally` syntax error | — | — | **Unfixed** |
| A | `tool_registry.py` / `_lazy_registry_static.py` | Static registry not updated for new tools | High | Yes | **Unfixed** |
| B | `tool_registry.py` | Plugin entry points only scanned once | Medium | Yes | **Unfixed** |
| C | `execute_function.py` | Edited workspace `.py` files not reloaded | Medium | Yes | **Unfixed** |
| D | `tool_registry.py` | `_lazy_cache` never invalidated | Medium | Yes | **Unfixed** |
