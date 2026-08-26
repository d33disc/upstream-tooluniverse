# Coding Conventions

**Analysis Date:** 2026-08-03

## Naming Patterns

**Files:**
- Use lowercase `snake_case.py` for Python modules, with domain or transport suffixes such as `src/tooluniverse/base_tool.py`, `src/tooluniverse/http_api_server.py`, and `src/tooluniverse/result_cache_manager.py`.
- Name concrete scientific integrations `<service>_tool.py`, as in `src/tooluniverse/web_search_tool.py` and `src/tooluniverse/semantic_scholar_tool.py`; place reusable foundations in unsuffixed or `base_*.py` modules such as `src/tooluniverse/exceptions.py` and `src/tooluniverse/base_rest_tool.py`.
- Name tests `test_<behavior_or_component>.py`; mirror broad test scope with directories such as `tests/unit/`, `tests/integration/`, `tests/tools/`, and `tests/api/`.

**Functions:**
- Use lowercase `snake_case` for functions and methods, as in `BaseTool.validate_parameters()` in `src/tooluniverse/base_tool.py` and `ToolUniverse.run_one_function()` in `src/tooluniverse/execute_function.py`.
- Prefix non-public helpers with `_`, including `_normalize_key()` in `src/tooluniverse/base_tool.py`, `_cleanup_all_cache_managers()` in `src/tooluniverse/cache/result_cache_manager.py`, and `_render_list()` in `src/tooluniverse/cli.py`.
- Name command handlers `cmd_<command>` in `src/tooluniverse/cli.py`; name test functions `test_<subject>_<expected_behavior>` following `tests/README.md`.

**Variables:**
- Use lowercase `snake_case` for locals, parameters, attributes, and module state, as shown by `tool_config`, `persistent_path`, and `cache_key` in `src/tooluniverse/base_tool.py` and `src/tooluniverse/cache/result_cache_manager.py`.
- Use leading underscores for internal attributes and module constants that are not public, such as `_cached_version_hash` in `src/tooluniverse/base_tool.py`, `_worker_thread` in `src/tooluniverse/cache/result_cache_manager.py`, and `_TRUTHY_VALUES` in `src/tooluniverse/execute_function.py`.
- Use uppercase `UPPER_SNAKE_CASE` for public constants and configuration switches, including `LAZY_LOADING_ENABLED` in `src/tooluniverse/execute_function.py` and `STATIC_CACHE_VERSION` in `src/tooluniverse/base_tool.py`.

**Types:**
- Use `PascalCase` for classes, exceptions, and dataclasses: `BaseTool` in `src/tooluniverse/base_tool.py`, `ToolUniverse` and `_BatchJob` in `src/tooluniverse/execute_function.py`, and `ToolValidationError` in `src/tooluniverse/exceptions.py`.
- Give concrete tools a `Tool` suffix and tool-specific failures an `Error` suffix, following `WebSearchTool` in `src/tooluniverse/web_search_tool.py` and the hierarchy in `src/tooluniverse/exceptions.py`.
- Use modern built-in generics in newly typed code (`list[str]`, `dict[str, Any]`, `str | None`) as demonstrated in `src/tooluniverse/base_tool.py` and `src/tooluniverse/cli.py`; existing core modules also use `typing.Dict`, `List`, and `Optional` in `src/tooluniverse/execute_function.py`, so match the surrounding module rather than rewriting unrelated annotations.

## Code Style

**Formatting:**
- Run Ruff's Black-compatible formatter configured by `[tool.ruff]` in `pyproject.toml`; the repository line length is 88 and generated/docs/example trees are excluded there.
- Use four-space indentation, trailing commas for multiline calls and collections, and one expression or argument per line when Ruff expands a construct; representative formatted code is in `src/tooluniverse/cache/result_cache_manager.py`.
- Keep source UTF-8 and favor double-quoted strings in Ruff-formatted code, while preserving a surrounding module's established quoting when making a small change; both styles remain in older files such as `src/tooluniverse/execute_function.py`.

**Linting:**
- Run `ruff check <touched paths>` and `ruff format --check <touched paths>` before submitting; Ruff settings live in `pyproject.toml`, and CI invokes Ruff in `.github/workflows/tests.yml` and `.github/workflows/lint-typecheck.yml`.
- Respect ignored Ruff rules `E203`, `E402`, `E501`, `F401`, and `F541` from `pyproject.toml`; do not use those ignores as a reason to add unused imports or disorder imports in new code.
- Add a narrow `# noqa: <CODE>` only when the exception is intentional and local, following `# noqa: BLE001` in `src/tooluniverse/execute_function.py`.
- Add type annotations to public and reusable code where practical. Mypy configuration is in `pyproject.toml`; strict untyped-definition and return checks apply specifically to `src/tooluniverse/base_tool.py`, `src/tooluniverse/gwas_tool.py`, and `src/tooluniverse/semantic_scholar_tool.py`.

## Import Organization

**Order:**
1. Import standard-library modules first, preferably grouped as in `src/tooluniverse/cache/result_cache_manager.py` (`atexit`, `logging`, `os`, threading/time utilities, dataclasses, then typing).
2. Import third-party packages next, such as `jsonschema` in `src/tooluniverse/base_tool.py`, `pytest` in `tests/conftest.py`, or `fastapi` in `src/tooluniverse/http_api_server.py`.
3. Import local package modules last with relative imports inside `src/tooluniverse/`, as in `src/tooluniverse/execute_function.py`; tests use absolute `tooluniverse.*` imports, as in `tests/unit/test_cache_manager.py`.
4. Keep conditional or expensive imports inside functions only when they implement an explicit compatibility, optional-dependency, or lazy-loading boundary, as shown by `importlib.resources` in `BaseTool.get_default_config_file()` in `src/tooluniverse/base_tool.py`.

**Path Aliases:**
- No Python path aliases are configured. The package uses the `src/` layout declared in `pyproject.toml`, and `pytest.ini` sets `pythonpath = src`.
- Do not add per-test `sys.path` manipulation in new tests; shared source-path setup already exists in `tests/conftest.py`. Some legacy tests such as `tests/unit/test_parameter_validation.py` retain local path insertion.

## Error Handling

**Patterns:**
- Raise structured subclasses from `src/tooluniverse/exceptions.py` when callers need exception semantics. Choose the narrow type (`ToolValidationError`, `ToolAuthError`, `ToolRateLimitError`, `ToolUnavailableError`, `ToolConfigError`, `ToolDependencyError`, or `ToolServerError`) and populate actionable recovery details.
- Return the standard structured error mapping from `tool_error()` in `src/tooluniverse/base_tool.py` for tool execution paths whose public contract returns data rather than raising. Preserve `status`, `error`, `error_type`, and optional `suggestion`.
- Catch specific exceptions at boundaries where recovery is known, as in JSON/schema handling in `src/tooluniverse/cli.py`. A broad `except Exception` is acceptable only at process, cleanup, plugin, network, or persistence isolation boundaries; log or translate it as done in `src/tooluniverse/cache/result_cache_manager.py` and `src/tooluniverse/http_api_server.py`.
- Never silently turn a failure into an ambiguous `None`, empty string, or empty list. `tool_error()` in `src/tooluniverse/base_tool.py` documents the required distinction between failures and legitimate empty results.
- Keep cleanup idempotent and exception-safe around threads, caches, and optional resources, following `ResultCacheManager.close()` patterns in `src/tooluniverse/cache/result_cache_manager.py` and session cleanup in `tests/conftest.py`.

## Logging

**Framework:** Python `logging`, wrapped by package helpers where appropriate.

**Patterns:**
- Create module loggers with `logging.getLogger(__name__)` for conventional modules, as in `src/tooluniverse/cache/result_cache_manager.py`.
- In core execution code, use `debug`, `info`, `warning`, and `error` imported from `src/tooluniverse/logging_config.py`, as demonstrated by `src/tooluniverse/execute_function.py`.
- Log recoverable infrastructure failures with context and parameterized messages, such as `logger.warning("Persistent cache delete failed: %s", exc)` in `src/tooluniverse/cache/result_cache_manager.py`; do not print secrets or full credential-bearing requests.
- Keep stdout machine-readable for CLI and MCP transports. Route diagnostics to logging or stderr following the rendering/status separation in `src/tooluniverse/cli.py` and the stdout-pollution tests in `tests/tools/test_tu_cli.py`.

## Comments

**When to Comment:**
- Explain invariants, compatibility constraints, non-obvious fallbacks, and the reason for deliberate behavior. Examples include dependency rationale in `pyproject.toml`, lazy-loading rationale in `src/tooluniverse/execute_function.py`, and cache-expiry logic in `src/tooluniverse/cache/result_cache_manager.py`.
- Use short section dividers only in long modules where they improve navigation, as in `src/tooluniverse/cache/result_cache_manager.py` and `tests/conftest.py`.
- Do not narrate straightforward assignments or restate a clear function name. Prefer extracting a well-named helper such as `_unknown_keys()` in `src/tooluniverse/base_tool.py`.

**JSDoc/TSDoc:**
- Not applicable; production code is Python. Use Python docstrings for public modules, classes, functions, fixtures, and tests, following `src/tooluniverse/exceptions.py`, `src/tooluniverse/base_tool.py`, and `tests/README.md`.
- Use concise one-line docstrings for simple helpers and expanded `Args`/`Returns` documentation for public methods with non-obvious contracts, as in `BaseTool.run()` in `src/tooluniverse/base_tool.py`.

## Function Design

**Size:** Keep helpers focused on one operation and extract parsing, rendering, validation, or persistence details from public orchestration methods. `src/tooluniverse/cli.py` separates `_render_*` helpers from `cmd_*` handlers, while `src/tooluniverse/cache/result_cache_manager.py` separates public cache operations from persistence helpers. Large orchestration methods remain in `src/tooluniverse/execute_function.py`; extend them through focused helpers rather than adding another responsibility inline.

**Parameters:** Use keyword-only parameters for calls with several same-typed or optional values, as in `ResultCacheManager.get()` and `ResultCacheManager.set()` in `src/tooluniverse/cache/result_cache_manager.py`. Accept a tool's external arguments as a dictionary where required by the common `BaseTool.run(arguments=...)` contract in `src/tooluniverse/base_tool.py`, and validate against the tool schema before executing.

**Return Values:** Preserve transport and tool contracts. Tool failures return the structured mapping defined by `tool_error()` in `src/tooluniverse/base_tool.py`; typed internal helpers return explicit values or `Optional[...]`, as in `ResultCacheManager.get()` in `src/tooluniverse/cache/result_cache_manager.py`; HTTP endpoints return Pydantic-compatible response data from `src/tooluniverse/http_api_server.py`.

## Module Design

**Exports:** Define implementation next to its domain behavior under `src/tooluniverse/`, then expose stable package-level symbols selectively through `src/tooluniverse/__init__.py`. Keep private implementation classes and helpers underscore-prefixed, as with `_BatchJob` in `src/tooluniverse/execute_function.py`.

**Barrel Files:** `src/tooluniverse/__init__.py` is the package facade for high-level imports such as `from tooluniverse import ToolUniverse`; do not create nested barrel modules merely to shorten imports. Tool discovery uses registries in `src/tooluniverse/tool_registry.py` and generated metadata in `src/tooluniverse/_lazy_registry_static.py`, so register new tools through the documented registry/build path rather than hand-maintaining broad wildcard exports.

---

*Convention analysis: 2026-08-03*
