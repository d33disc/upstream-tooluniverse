"""Health-check retry/transient policy (fix/health-check-retry-transient).

The nightly health check (`scripts/tool_health_check.py`) tested each tool once
with no retry, so a single transient network failure (timeout, 5xx, 429) flipped a
working tool to "broken" permanently — the FDA-cluster false-positive root cause.

These tests pin the corrected behavior:
  - transient failures are retried before flagging broken
  - permanent failures (NOT_FOUND, validation, code bugs) are NOT retried
  - after exhausting retries a still-failing tool is reported broken

The single-attempt runner is injected so no network or subprocess is touched.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "tool_health_check.py"
_spec = importlib.util.spec_from_file_location("tool_health_check", _SCRIPT)
assert _spec and _spec.loader
thc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(thc)


def _seq(*results):
    """A single-attempt runner that yields canned (status, detail) per call,
    recording how many times it was invoked."""
    calls = {"n": 0}

    def run(_name: str) -> tuple[str, str]:
        i = min(calls["n"], len(results) - 1)
        calls["n"] += 1
        return results[i]

    run.calls = calls  # type: ignore[attr-defined]
    return run


# ── transient classification ────────────────────────────────────────────────


def test_is_transient_true_for_timeout():
    assert thc._is_transient("timeout after 15s") is True


def test_is_transient_true_for_5xx_and_429():
    assert thc._is_transient("FDA GSRS HTTP 503") is True
    assert thc._is_transient("HTTP 429 Too Many Requests") is True
    assert thc._is_transient("ConnectionError: connection reset") is True


def test_is_transient_false_for_not_found():
    assert thc._is_transient("tool returned error: NOT_FOUND No matches found") is False


def test_is_transient_false_for_validation():
    assert thc._is_transient("'indication' is a required property") is False


# ── retry policy ──────────────────────────────────────────────────────────────


def test_retries_transient_then_succeeds():
    run = _seq(("broken", "timeout after 15s"), ("live", "passed (1.2s)"))
    name, status, _ = thc._test_tool("X", _run=run, _sleep=lambda *_: None)
    assert status == "live"
    assert run.calls["n"] == 2  # one retry after the transient


def test_does_not_retry_permanent_failure():
    run = _seq(("broken", "tool returned error: NOT_FOUND No matches found"))
    name, status, _ = thc._test_tool("X", _run=run, _sleep=lambda *_: None)
    assert status == "broken"
    assert run.calls["n"] == 1  # permanent failure: no retry


def test_gives_up_after_max_retries():
    run = _seq(("broken", "FDA GSRS HTTP 503"))  # always transient
    name, status, _ = thc._test_tool("X", _run=run, _sleep=lambda *_: None)
    assert status == "broken"
    assert run.calls["n"] == thc.RETRIES + 1  # initial attempt + RETRIES
