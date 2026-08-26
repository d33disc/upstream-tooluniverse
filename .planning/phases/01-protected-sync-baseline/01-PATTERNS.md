# Phase 1: Protected Sync Baseline - Pattern Map

**Mapped:** 2026-08-03
**Files/artifact shapes analyzed:** 12
**Existing analogs selected:** 5
**Analogs found:** 10 / 12 (two preservation-specific shapes have no functional analog)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/capture_sync_baseline.py` | utility / orchestration service | batch, subprocess request-response, file-I/O | `scripts/tool_health_check.py` | role + flow match |
| `tests/unit/test_sync_baseline_git.py` | test | file-I/O, batch transform | `tests/unit/test_http_retry_after_cap.py` for unit-test structure only | role match; no Git inventory analog |
| `tests/unit/test_sync_baseline_normalize.py` | test | transform, bounded event/retry flow | `tests/unit/test_http_retry_after_cap.py` | role + flow match |
| `tests/integration/test_sync_baseline_surfaces.py` | integration test | request-response plus stdio streaming | `tests/integration/test_stdio_mode.py`; `tests/integration/test_http_api_server.py` | composite role + flow match |
| `.github/workflows/tests.yml` | config / CI workflow | event-driven batch | `.github/workflows/tests.yml` | exact, in-place extension |
| `evidence/<full-fork-sha>/baseline.json` | generated root manifest / model | batch aggregation, file-I/O | `TOOL_HEALTH_REPORT.json` writer in `scripts/tool_health_check.py` | role match |
| `evidence/<full-fork-sha>/git.json` | generated evidence model | subprocess-to-JSON transform, file-I/O | none | no functional analog |
| `evidence/<full-fork-sha>/preservation.json` | generated inventory model | Git/filesystem metadata transform, file-I/O | none | no functional analog |
| `evidence/<full-fork-sha>/environment.json` | generated evidence model | environment-to-redacted-JSON transform | report serialization in `scripts/tool_health_check.py` | partial flow match |
| `evidence/<full-fork-sha>/tests/*` | generated JUnit/log artifacts | batch subprocess output | test invocation/artifact steps in `.github/workflows/tests.yml` | role match |
| `evidence/<full-fork-sha>/probes/*.json` | generated probe model | request-response normalization, file-I/O | HTTP response assertions plus health report serialization | composite flow match |
| `evidence/<full-fork-sha>/SHA256SUMS` | generated integrity manifest | file-I/O transform | report-writing boundary in `scripts/tool_health_check.py` | partial flow match |

The evidence paths are output contracts, not additional hand-authored modules. Keep their schemas in the single orchestrator unless implementation pressure proves a separate module necessary.

## Pattern Assignments

### `scripts/capture_sync_baseline.py` (utility/orchestrator; batch + subprocess + file-I/O)

**Primary analog:** `scripts/tool_health_check.py`

**Imports pattern** (`scripts/tool_health_check.py:16-25`):

```python
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
```

Use stdlib imports first and `Path` for bounded artifact paths. Phase 1 does not need the analog's random sampling or concurrency; its selection must be SHA-derived and deterministic.

**Argv-array subprocess and bounded result pattern** (`scripts/tool_health_check.py:67-97`):

```python
def _test_once(name: str) -> tuple[str, str]:
    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "tooluniverse.cli", "test", name, "--json"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        elapsed = f"{time.time() - t0:.1f}s"
        if proc.returncode == 0:
            return "live", f"passed ({elapsed})"
        raw = (proc.stdout or proc.stderr).strip()
        # parse structured output, then return bounded diagnostics
    except subprocess.TimeoutExpired:
        return "broken", f"timeout after {TIMEOUT}s"
```

Copy the argv-array, `cwd`, captured-stream, explicit-timeout, and structured-return shape. Do not use `shell=True`. For baseline evidence, retain stdout and stderr separately, redact before persistence, use `time.monotonic()` for durations, and record the exact argv as an array.

**Retry seam** (`scripts/tool_health_check.py:100-115`):

```python
def _test_tool(name, _run=_test_once, _sleep=time.sleep) -> tuple[str, str, str]:
    status, detail = _run(name)
    attempt = 0
    while status == "broken" and _is_transient(detail) and attempt < RETRIES:
        attempt += 1
        _sleep(RETRY_BACKOFF * attempt)
        status, detail = _run(name)
    if attempt and status == "live":
        detail = f"{detail} [recovered after {attempt} retry(s)]"
    return name, status, detail
```

Preserve dependency injection for `_run` and `_sleep`, but intentionally change the analog's linear delay to the locked fixed interval: three total attempts and `2.0` seconds between attempts. Retry only classified transient failures.

**JSON report boundary** (`scripts/tool_health_check.py:183-200`):

```python
live = sum(1 for r in results.values() if r.get("status") == "live")
broken = sum(1 for r in results.values() if r.get("status") == "broken")

REPORT_PATH.write_text(
    json.dumps(
        {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary": {"live": live, "broken": broken},
            "tools": results,
        },
        indent=2,
    )
)
```

Copy the single structured serialization boundary, but sort keys, add a trailing newline, write into a temporary sibling tree, validate it, then publish the bounded artifact set. Generate `SHA256SUMS` last and exclude it from its own checksum input.

**Error/validation rule:** fail closed on a nonzero required command, malformed JSON, schema/invariant mismatch, unexpected skip, dirty isolated worktree, unresolved preservation classification, or persistent configured-provider failure. Exceptions should become typed stage outcomes with sanitized diagnostics, not be silently swallowed as `_load_prev` does at lines 58-64.

---

### `tests/unit/test_sync_baseline_git.py` (test; temporary Git/filesystem I/O)

**Closest structural analog:** `tests/unit/test_http_retry_after_cap.py`

**Small fake and observable side-effect pattern** (`tests/unit/test_http_retry_after_cap.py:14-30`):

```python
class _FakeSession:
    def __init__(self, retry_after):
        self.calls = 0
        self.retry_after = retry_after

    def request(self, *args, **kwargs):
        self.calls += 1
        resp = MagicMock()
        if self.calls == 1:
            resp.status_code = 429
            resp.headers = {"Retry-After": self.retry_after}
        else:
            resp.status_code = 200
            resp.headers = {}
        return resp
```

Use the same principle—minimal fixtures with directly observable calls/state—but create real temporary Git repositories under `tmp_path` rather than mocking Git semantics. A helper should invoke `git` through argv arrays and configure only repository-local identity.

**Focused assertion style** (`tests/unit/test_http_retry_after_cap.py:33-45`):

```python
@pytest.mark.unit
def test_oversized_retry_after_is_capped(monkeypatch):
    slept = []
    monkeypatch.setattr(hu.time, "sleep", lambda s: slept.append(s))

    resp = hu.request_with_retry(
        _FakeSession("3600"), "GET", "http://example", max_retry_after_seconds=30.0
    )

    assert resp.status_code == 200
    assert slept, "should have slept once before the retry"
    assert slept[0] <= 31.0
```

Mirror the marker, one-behavior-per-test, injected boundary, and explicit invariant assertions. Cover full OIDs/divergence; staged, unstaged, untracked, rename, and mode records; NUL-safe unusual paths; relative/absolute, in-root/out-of-root, tracked, and broken symlinks; link text without traversal; and original-checkout non-mutation.

**No Git-specific analog exists:** do not invent a project-local Git abstraction. Use `subprocess.run([...], check=True, capture_output=True)` and assert authoritative Git output against the produced JSON records.

---

### `tests/unit/test_sync_baseline_normalize.py` (test; transform + retry policy)

**Analog:** `tests/unit/test_http_retry_after_cap.py`

**Injected clock/sleep pattern** (`tests/unit/test_http_retry_after_cap.py:48-58`):

```python
@pytest.mark.unit
def test_small_retry_after_is_honoured_unchanged(monkeypatch):
    slept = []
    monkeypatch.setattr(hu.time, "sleep", lambda s: slept.append(s))

    hu.request_with_retry(
        _FakeSession("2"), "GET", "http://example", max_retry_after_seconds=30.0
    )

    assert 2.0 <= slept[0] <= 2.5
```

Use injected sleep/run functions so retry tests are instantaneous and verify exact attempt counts and the fixed `2.0`-second sequence. Parameterize transient vs permanent classifications where it improves clarity.

Normalization tests should prove that only allowlisted JSON paths change, maps become deterministically ordered, arrays remain ordered unless their contract declares otherwise, structured success/error envelopes retain required keys/types, and redaction prevents credential values from reaching JSON/JUnit/log diagnostics. Add deterministic SHA sampling and checksum ordering cases here.

---

### `tests/integration/test_sync_baseline_surfaces.py` (integration test; request-response + stdio streaming)

**Stdio analog:** `tests/integration/test_stdio_mode.py`

**Process environment and deadline reader** (`tests/integration/test_stdio_mode.py:22-54`):

```python
_SRC_PATH = str(Path(__file__).parent.parent.parent / "src")
_PYTHON = sys.executable
_SUBPROCESS_ENV = {**os.environ, "PYTHONUNBUFFERED": "1"}

def _read_json_line(process, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            return None
        ready, _, _ = _select.select([process.stdout], [], [], 2.0)
        if not ready:
            continue
        line = process.stdout.readline()
        if not line:
            continue
        try:
            return json.loads(line.strip())
        except json.JSONDecodeError:
            continue
    return None
```

Copy the current-interpreter, unbuffered child, and bounded-read ideas. Prefer `time.monotonic()` and capture stderr rather than discarding it, with redaction before evidence persistence.

**Protocol sequence and cleanup** (`tests/integration/test_stdio_mode.py:86-163`):

```python
process = subprocess.Popen(
    [_PYTHON, "-c", "...run_stdio_server()"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    bufsize=1,
    env=_SUBPROCESS_ENV,
)
try:
    # initialize, notifications/initialized, then tools/list
    response_data = _read_json_line(process, timeout=60)
    assert "result" in response_data
    assert "tools" in response_data["result"]
finally:
    process.terminate()
    process.wait(timeout=5)
```

Retain `try/finally` teardown and actual protocol messages. Strengthen the baseline test: no fixed startup sleep, no `pytest.skip` on timeout, terminate then kill on bounded teardown failure, and perform `grep_tools`/`list_tools` → `get_tool_info` → `execute_tool` using the inspected arguments.

**REST analog:** `tests/integration/test_http_api_server.py`

**Isolated client fixture** (`tests/integration/test_http_api_server.py:9-19`):

```python
import pytest
from fastapi.testclient import TestClient
from tooluniverse.http_api_server import app, _tu_manager

@pytest.fixture
def client():
    _tu_manager.reset()
    return TestClient(app)
```

Use this for the fast in-process REST contract portion. The process-level baseline probe must additionally launch Uvicorn on an allocated loopback port with startup/operation/teardown deadlines.

**Structured success and error assertions** (`tests/integration/test_http_api_server.py:85-113`):

```python
response = client.post(
    "/api/call",
    json={"method": "get_available_tools", "kwargs": {"name_only": True}},
)
assert response.status_code == 200
data = response.json()
assert data["success"] is True
assert isinstance(data["result"], list)

response = client.post(
    "/api/call",
    json={"method": "non_existent_method", "kwargs": {}},
)
data = response.json()
assert data["success"] is False
assert "error" in data
```

Extend this established envelope check into one chained discovery → `tool_specification` → `run_one_function` probe for `DegreesOfUnsaturation_calculate`, plus an intentional structured-error probe.

**MCP HTTP gap:** there is no existing real streamable-HTTP end-to-end analog. Use the installed MCP/FastMCP client session; do not copy REST/raw-POST mechanics into MCP HTTP.

---

### `.github/workflows/tests.yml` (CI config; event-driven batch)

**Exact in-place analog:** `.github/workflows/tests.yml`

**Matrix/setup pattern** (`.github/workflows/tests.yml:9-24`):

```yaml
jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12']

    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

Extend the existing matrix to the declared stable range (`3.10` through `3.14`) while keeping Python 3.12 as the primary comprehensive lane. Avoid multiplying every expensive job across every interpreter when a targeted compatibility lane proves the contract.

**Existing test selection/artifact pattern** (`.github/workflows/tests.yml:59-67`, `87-92`):

```yaml
- name: Run core tests (unit + integration)
  timeout-minutes: 15
  run: |
    pytest tests/unit/ tests/integration/ -v \
      --cov=tooluniverse \
      --cov-report=xml \
      -m "not slow and not require_api_keys and not network and not require_gpu"

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results-${{ matrix.python-version }}
    path: coverage.xml
```

Keep explicit timeouts and version-keyed artifact names. For baseline lanes, clear repository `addopts`, restate strict markers/config/timeouts, emit JUnit XML, and ensure the required offline suites are not hidden behind the current optional network step.

## Evidence Artifact Assignments

All artifact shapes are emitted by `scripts/capture_sync_baseline.py`; they should share canonical JSON writing (`sort_keys=True`, `indent=2`, trailing newline), stable schema/version fields, full fork/upstream OIDs, and explicit gate status.

| Artifact | Pattern to apply |
|---|---|
| `baseline.json` | Aggregate named stage outcomes like the summary/results split at `scripts/tool_health_check.py:183-200`; include a hard overall gate derived from all required stages. |
| `git.json` | Record argv arrays and parsed NUL-safe Git facts. Preserve raw machine evidence in a JSON-safe representation; never parse human-formatted output. |
| `preservation.json` | Emit one record per delta path, retaining modes/OIDs/rename endpoints/classification. For symlinks store mode, blob/link text, and lexical target metadata separately without traversal. |
| `environment.json` | Store versions and credential variable names/booleans only. Never serialize values, lengths, hashes, headers, query strings, `.env` contents, or a full environment dump. |
| `tests/*` | Use pytest JUnit plus concise command metadata and bounded sanitized stdout/stderr. Collection-only output is not execution evidence. |
| `probes/*.json` | Use a common stage schema (`discover`, `inspect`, `execute`, `assert`) across Python, CLI, MCP stdio/HTTP, REST, provider, and catalog probes. Store raw sanitized and normalized values only when safe. |
| `SHA256SUMS` | Sort relative artifact paths, hash file bytes after final validation, write last, and verify before declaring the baseline green. Checksums provide integrity detection, not authenticity. |

## Shared Patterns

### Subprocess safety and lifecycle

**Sources:** `scripts/tool_health_check.py:67-97`; `tests/integration/test_stdio_mode.py:86-163`

- Always pass argv arrays and explicit `cwd`; never use `shell=True`.
- Set per-operation and global deadlines.
- Capture stdout/stderr separately, sanitize before writing, and retain return code/duration.
- Wrap child servers in `try/finally`; terminate and use a bounded wait, then kill if necessary.
- Bind HTTP servers to loopback only.

### Deterministic structured evidence

**Source:** `scripts/tool_health_check.py:183-200`

- One writer owns JSON formatting and path containment.
- Preserve structure by default; normalize only allowlisted volatile paths.
- Sort maps; sort arrays only when their tool contract says ordering is irrelevant.
- Generate into a temporary tree outside the isolated worktree, validate, publish the bounded set, then checksum.

### Retry policy

**Sources:** `scripts/tool_health_check.py:34-55,100-115`; `tests/unit/test_http_retry_after_cap.py:33-58`

- Inject runner/sleep dependencies for tests.
- Use three total attempts with a fixed `2.0`-second interval.
- Retry only timeout, connection, 408, 429, 500, 502, 503, 504, or explicit `retryable=true` outcomes.
- Do not retry credentials/auth, validation, schema, missing-tool, unsupported-operation, or domain-invariant failures.
- Record each attempt and whether recovery occurred; persistent configured-provider failure blocks.

### Surface contract

**Sources:** `tests/integration/test_stdio_mode.py:111-163`; `tests/integration/test_http_api_server.py:74-113`

Every transport follows the same semantic sequence: discover the selected tool, inspect its exact required schema, execute exactly those inspected arguments, then assert a normalized structured envelope and domain invariants. Use `DegreesOfUnsaturation_calculate` with `{"operation": "calculate", "formula": "C6H6"}` as the credential-free deterministic reference.

### Test conventions

**Sources:** `tests/unit/test_http_retry_after_cap.py:33-58`; `tests/integration/test_stdio_mode.py:57-59`; `.github/workflows/tests.yml:59-67`

- Use `pytest.mark.unit` / `integration` / `stdio` consistently and run with strict markers.
- Prefer small explicit helpers and one contract per test.
- Use `tmp_path` for repositories/artifacts and `monkeypatch` for clock/environment seams.
- Required baseline timeouts/failures are assertions, never skips.
- Clear implicit `pytest.ini` selection when proving comprehensive lanes.

### Credentials and diagnostics

No current analog provides a complete secret-safe evidence pipeline. The new code must capture only credential names and configured booleans at source, pass values only through process environment, and sanitize bounded diagnostics before persistence. Do not read or copy `.tooluniverse/.env.1password`.

### Authentication

No application auth/guard pattern applies: this is local/CI developer tooling. Provider authentication remains owned by existing adapters and environment configuration; the baseline only detects configuration and invokes selected probes.

## No Analog Found

| File / Capability | Role | Data Flow | Reason / planner direction |
|---|---|---|---|
| `tests/unit/test_sync_baseline_git.py` and the `git.json` / `preservation.json` collectors | test + generated inventory model | Git/filesystem metadata to JSON | No repository code currently parses porcelain-v2/raw NUL records or inventories symlinks without traversal. Follow RESEARCH.md's Git-object specification and test with real temporary repositories. |
| MCP streamable-HTTP portion of `tests/integration/test_sync_baseline_surfaces.py` | integration test | session-based request-response | Existing coverage explicitly lacks a true transport session. Use installed MCP/FastMCP clients, not raw HTTP or the REST `TestClient` pattern. |
| Secret-safe evidence redaction | utility / validation | transform | Existing health reporting bounds diagnostics but does not establish credential-safe redaction. Implement an allowlist/value-free capture boundary and adversarial tests from RESEARCH.md. |

## Metadata

**Analog search scope:** `scripts/`, `tests/unit/`, `tests/integration/`, `.github/workflows/`

**Selected analogs (5):**

1. `scripts/tool_health_check.py` — subprocess orchestration, transient classification, retry seam, JSON report.
2. `tests/unit/test_http_retry_after_cap.py` — focused unit style, injected sleep, bounded retry assertions.
3. `tests/integration/test_stdio_mode.py` — real stdio child process, JSON-RPC lifecycle, teardown.
4. `tests/integration/test_http_api_server.py` — REST fixture, method discovery, structured success/error envelopes.
5. `.github/workflows/tests.yml` — current Python matrix, test lane, and version-keyed artifact conventions.

**Pattern extraction date:** 2026-08-03

**Planner caution:** copy the stable structural patterns above, not known weaknesses in the analogs. In particular, replace fixed sleeps, timeout skips, discarded stderr, nondeterministic random sampling, broad exception swallowing, and linear backoff with the locked fail-closed deterministic behavior.
