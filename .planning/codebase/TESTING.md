# Testing Patterns

**Analysis Date:** 2026-08-03

## Test Framework

**Runner:**
- Pytest 7.0 or newer, declared in the `dev` extra in `pyproject.toml`.
- Config: `pytest.ini`; database-subsystem overrides live in `tests/test_database_setup/pytest.ini`.
- Plugins used by the suite are declared in `pyproject.toml`: `pytest-cov`, `pytest-timeout`, `pytest-mock`, `pytest-asyncio`, `pytest-xdist`, `pytest-html`, and `requests-mock`.

**Assertion Library:**
- Use pytest's plain `assert` rewriting for new tests, as in `tests/unit/test_cache_manager.py` and `tests/tools/test_web_search_tool.py`.
- Use `pytest.raises`, `pytest.approx`, and fixture assertions where suitable. `unittest.TestCase` assertions remain in legacy-style suites such as `tests/unit/test_parameter_validation.py`, but are not the preferred pattern for new tests.

**Run Commands:**
```bash
pytest                                                        # Default fast unit + integration selection from pytest.ini
pytest tests/unit/test_cache_manager.py -q                    # Smallest relevant file
pytest -m unit                                                # Tests marked as isolated unit tests
pytest tests/integration -m "not network and not slow"         # Integration subset without external network
pytest --cov=tooluniverse --cov-report=html                    # Coverage report for the configured suite
pytest tests/unit tests/integration -n auto --cov=tooluniverse # CI-style parallel core suite
```

`pytest.ini` excludes `slow`, `require_api_keys`, and `network` tests by default and ignores `tests/tools/`, `tests/examples/`, and `tests/api/`. Pass those paths explicitly when validating those areas.

## Test File Organization

**Location:**
- Put fast isolated tests in `tests/unit/`, multi-component and transport tests in `tests/integration/`, individual scientific backend tests in `tests/tools/`, credential/service tests in `tests/api/`, and datastore tests in `tests/test_database_setup/`, following `tests/README.md`.
- Keep shared root fixtures in `tests/conftest.py`; keep subtree-specific fixtures in a local `conftest.py`, as in `tests/test_database_setup/conftest.py` and `tests/examples/conftest.py`.
- Some legacy component tests remain directly under `tests/`, such as `tests/test_scientific_calculator_tools.py`; place new tests in the scoped directories above.

**Naming:**
- Name files `test_<component_or_behavior>.py`, test functions `test_<what>_<expected_behavior>`, and optional suite classes `Test<Area>` as described in `tests/README.md`.
- Give every new test a concise behavior docstring and a category marker. `tests/conftest.py` emits quality warnings when docstrings, recognized markers, or meaningful names are absent.

**Structure:**
```text
tests/
├── conftest.py                       # Cross-suite environment and cache fixtures
├── unit/test_<behavior>.py           # Fast, isolated behavior and regression tests
├── integration/test_<workflow>.py    # Multi-module, protocol, and server tests
├── tools/test_<service>_tool.py      # Concrete scientific tool tests
├── api/test_<api_behavior>.py        # External API/auth tests
├── test_database_setup/              # SQLite/vector/search subsystem suite
└── examples/test_<example>.py        # Executable example validation
```

## Test Structure

**Suite Organization:**
```python
import pytest

from tooluniverse.web_search_tool import WebSearchTool


@pytest.mark.unit
def test_web_search_returns_clean_empty_results_on_backend_failure(monkeypatch):
    """A backend failure remains distinguishable from a malformed result."""
    tool = WebSearchTool({"name": "web_search", "parameter": {"type": "object"}})

    def always_fail(*args, **kwargs):
        raise RuntimeError("simulated search failure")

    monkeypatch.setattr(tool, "_search_with_ddgs", always_fail)
    result = tool.run({"query": "test query", "backend": "auto"})

    assert result["status"] == "success"
    assert result["data"]["all_providers_failed"] is True
```

This pattern is adapted from `tests/tools/test_web_search_tool.py`.

**Patterns:**
- Arrange inputs and collaborators, act once through the public behavior, then assert the observable result. The sections may be implicit for short tests such as `tests/unit/test_cache_manager.py`.
- Use `@pytest.mark.unit` for isolated tests and `@pytest.mark.integration` for composed behavior; add orthogonal markers such as `mcp`, `hooks`, `stdio`, `slow`, or `require_api_keys` from `pytest.ini` when they control selection.
- Use `@pytest.mark.parametrize` for equivalent input/output cases, as in `tests/tools/test_web_search_tool.py`, instead of duplicating test bodies.
- Use fixtures for setup and guaranteed teardown. Yield-based cache fixtures in `tests/conftest.py` close managers after assertions; integration suite classes such as `tests/integration/test_hooks_integration.py` use `setup_method`/`teardown_method` when class-scoped state is clearer.
- Keep unit tests deterministic: use `tmp_path`, fixed vectors, fixed environment flags, and local fakes. Examples live in `tests/conftest.py`, `tests/test_database_setup/conftest.py`, and `tests/unit/test_batch_concurrency.py`.

## Mocking

**Framework:** Pytest `monkeypatch`, `pytest-mock`, `unittest.mock`, and `requests-mock`, all available through the dev dependencies in `pyproject.toml`.

**Patterns:**
```python
@pytest.mark.unit
def test_fallback_uses_second_provider(monkeypatch):
    tool = _new_tool()

    monkeypatch.setattr(tool, "_search_with_ddgs", lambda **kwargs: (_ for _ in ()).throw(RuntimeError("failed")))
    monkeypatch.setattr(tool, "_search_with_duckduckgo_html", lambda **kwargs: [{"title": "Fallback"}])

    result = tool.run({"query": "example", "backend": "auto"})
    assert result["data"]["backend_used"] == "duckduckgo_html"
```

The production-facing variant of this pattern is in `tests/tools/test_web_search_tool.py`; object patching with call assertions is also used in `tests/integration/test_hooks_integration.py`.

**What to Mock:**
- Mock network clients, SDK calls, clocks/sleeps, process boundaries, and optional model/service integrations in unit tests. Patch the symbol where the code under test looks it up, as `tests/tools/test_web_search_tool.py` patches `tooluniverse.web_search_tool.BaseMCPClient`.
- Use `monkeypatch.setenv` for configuration and `tmp_path` for filesystem/database behavior, following fixtures in `tests/conftest.py`.
- Prefer small behavior-rich fakes when protocol shape matters, such as the `FakeMCPClient` in `tests/tools/test_web_search_tool.py`, and use `AsyncMock` for awaited collaborators as in `tests/integration/test_mcp_protocol.py`.

**What NOT to Mock:**
- Do not mock the pure calculation, parsing, validation, or normalization logic being asserted; feed it representative values, following `tests/unit/test_parameter_validation.py` and `tests/unit/test_opentargets_target_diseases_score.py`.
- Do not replace all collaborating ToolUniverse components in an integration test. Exercise the real in-process composition and mock only the external service, costly model, or nondeterministic boundary, as in `tests/integration/test_hooks_integration.py`.
- Do not make unmarked network calls from unit tests. The `disable_network` fixture in `tests/conftest.py` can enforce the boundary, and actual network tests belong behind `network`, `integration`, or `require_api_keys` markers from `pytest.ini`.

## Fixtures and Factories

**Test Data:**
```python
@pytest.fixture
def memory_cache_manager():
    """Create an in-memory-only cache manager."""
    manager = ResultCacheManager(
        memory_size=4,
        persistent_path=None,
        enabled=True,
        persistence_enabled=False,
        singleflight=False,
    )
    yield manager
    manager.close()
```

This is the shared lifecycle pattern used in `tests/conftest.py`.

**Location:**
- Put broadly reusable runtime, environment, cache, and ToolUniverse fixtures in `tests/conftest.py`.
- Put subsystem fixtures beside their tests, such as SQLite stores, deterministic embeddings, and search engines in `tests/test_database_setup/conftest.py`.
- Keep one-off factories private in the test module, such as `_new_tool()` in `tests/tools/test_web_search_tool.py`; introduce a shared helper under `tests/helpers/` only when multiple suites use the same construction logic.
- Prefer pytest built-ins (`tmp_path`, `monkeypatch`, `capsys`, `caplog`) over hand-rolled temporary directories or output capture. Existing older imports of `TemporaryDirectory` in `tests/conftest.py` do not establish a new-test convention.

## Coverage

**Requirements:** No numeric minimum is enforced in `pytest.ini` or `pyproject.toml`. The default command always collects package coverage with `--cov=tooluniverse --cov-report=term-missing:skip-covered`, and `.github/workflows/tests.yml` uploads `coverage.xml` to Codecov without failing CI on upload errors.

**View Coverage:**
```bash
pytest --cov=tooluniverse --cov-report=term-missing
pytest --cov=tooluniverse --cov-report=html
open htmlcov/index.html
```

For a targeted change, run its test file first, then use the configured default or the core CI command from `.github/workflows/tests.yml` when the touched behavior crosses modules.

## Test Types

**Unit Tests:**
- Scope one class, function, parser, schema, or regression at a time under `tests/unit/`; keep tests fast, deterministic, and free of external services per `tests/README.md`.
- Use real lightweight objects and isolate only boundaries. Examples include cache lifecycle assertions in `tests/unit/test_cache_manager.py`, validation cases in `tests/unit/test_parameter_validation.py`, and concurrency limits in `tests/unit/test_batch_concurrency.py`.

**Integration Tests:**
- Exercise interactions among ToolUniverse, transports, hooks, caches, workspaces, and generated tool registries under `tests/integration/`.
- Mark them `integration` and add a capability marker where useful. Keep network or credentials independently marked so the default selector in `pytest.ini` remains offline-safe; examples include `tests/integration/test_mcp_protocol.py` and `tests/integration/test_http_api_server.py`.
- API and datastore integration have dedicated suites at `tests/api/` and `tests/test_database_setup/`; their selection rules are documented in `pytest.ini` and `tests/test_database_setup/pytest.ini`.

**E2E Tests:**
- No browser E2E framework is used. End-to-end behavior is covered with pytest workflow tests such as `tests/integration/test_dms_pipeline_e2e_kras.py`, database pipeline coverage in `tests/test_database_setup/test_pipeline_e2e.py`, executable examples under `tests/examples/`, and the shell scenario `tests/e2e_claude_code.sh`.
- Treat E2E tests as explicit, potentially slow validation; mark service-dependent cases and do not add them to the default fast path in `pytest.ini` without evidence that they are deterministic and offline.

## Common Patterns

**Async Testing:**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_mcp_tools_list_request():
    server = SMCP(name="Test Server", tool_categories=["uniprot"], search_enabled=True)

    tools = await server.get_tools()

    assert isinstance(tools, (list, dict))
    assert len(tools) > 0
```

Use `pytest.mark.asyncio` and directly await the public coroutine, following `tests/integration/test_mcp_protocol.py`. The event-loop fixture scope is `function` in `pytest.ini`; avoid sharing async loop state between tests.

**Error Testing:**
```python
@pytest.mark.unit
def test_invalid_value_raises_clear_error():
    with pytest.raises(ValueError, match="expected detail"):
        parse_invalid_value()
```

Use `pytest.raises(..., match=...)` when exceptions are the contract, as in `tests/tools/test_tu_cli.py`. When a tool or HTTP boundary intentionally returns structured errors, assert the full observable shape (`status`, `error_type`, message/detail, and HTTP status where applicable) rather than expecting an exception; examples live in `tests/tools/test_web_search_tool.py` and `tests/integration/test_http_api_server.py`.

---

*Testing analysis: 2026-08-03*
