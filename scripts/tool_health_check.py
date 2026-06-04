#!/usr/bin/env python3
"""Nightly tool health check for ToolUniverse CI.

Reads the previous TOOL_HEALTH_REPORT.json for smart filtering, then runs
`python -m tooluniverse.cli test <tool>` for:
  - all broken/unknown tools from the previous run
  - a 10 % random sample of passing tools (regression coverage)

Transient failures (timeout, 5xx, 429, connection errors) are retried before a
tool is flagged broken — a single network blip must not condemn a working tool.
Concurrency, timeout, and retry count are env-tunable (see constants below).

Writes a new TOOL_HEALTH_REPORT.json with per-tool status and a summary.
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

TIMEOUT = int(os.getenv("TU_HEALTH_TIMEOUT", "15"))
MAX_WORKERS = int(os.getenv("TU_HEALTH_WORKERS", "8"))
RETRIES = int(os.getenv("TU_HEALTH_RETRIES", "2"))
RETRY_BACKOFF = float(os.getenv("TU_HEALTH_BACKOFF", "2.0"))
SAMPLE_RATE = 0.10
REPORT_PATH = Path("TOOL_HEALTH_REPORT.json")

# Substrings marking a failure as transient (retriable) rather than a real defect.
# Anything not matched here (NOT_FOUND, validation, code exceptions) is permanent.
_TRANSIENT_MARKERS = (
    "timeout",
    "timed out",
    "connection",
    "connectionerror",
    "rate limit",
    "429",
    "500",
    "502",
    "503",
    "504",
    "temporarily",
    "read timed out",
)


def _is_transient(detail: str) -> bool:
    """True if a failure detail looks like a retriable network blip, not a real bug."""
    low = detail.lower()
    return any(marker in low for marker in _TRANSIENT_MARKERS)


def _load_prev() -> dict[str, dict]:
    if REPORT_PATH.exists():
        try:
            return json.loads(REPORT_PATH.read_text()).get("tools", {})
        except Exception:
            pass
    return {}


def _test_once(name: str) -> tuple[str, str]:
    """Run the tool's test examples exactly once; return (status, detail)."""
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
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list) and parsed:
                parsed = parsed[0]
            detail = str(
                parsed.get("error") or (parsed.get("failures") or ["test failed"])[0]
                if isinstance(parsed, dict)
                else raw
            )[:120]
        except Exception:
            detail = raw[:120] or "test failed"
        return "broken", f"{detail} ({elapsed})"
    except subprocess.TimeoutExpired:
        return "broken", f"timeout after {TIMEOUT}s"
    except Exception as exc:
        elapsed = f"{time.time() - t0:.1f}s"
        return "broken", f"{type(exc).__name__}: {str(exc)[:80]} ({elapsed})"


def _test_tool(name, _run=_test_once, _sleep=time.sleep) -> tuple[str, str, str]:
    """Test a tool, retrying transient failures before flagging it broken.

    A live result or a permanent failure (NOT_FOUND, validation, code bug) returns
    immediately. A transient failure (timeout, 5xx, 429, connection) is retried up
    to RETRIES times with linear backoff — a network blip must not condemn a tool.
    """
    status, detail = _run(name)
    attempt = 0
    while status == "broken" and _is_transient(detail) and attempt < RETRIES:
        attempt += 1
        _sleep(RETRY_BACKOFF * attempt)
        status, detail = _run(name)
    if attempt and status == "live":
        detail = f"{detail} [recovered after {attempt} retry(s)]"
    return name, status, detail


def _select(all_tools: list[str], prev: dict[str, dict]) -> list[str]:
    priority: list[str] = []
    passing: list[str] = []
    for name in all_tools:
        status = prev.get(name, {}).get("status", "unknown")
        if status == "live":
            passing.append(name)
        else:
            priority.append(name)

    k = min(len(passing), max(0, int(len(passing) * SAMPLE_RATE)))
    sample = random.sample(passing, k)
    print(
        f"Testing {len(priority) + len(sample)} tools: "
        f"{len(priority)} broken/unknown + {len(sample)} sampled "
        f"from {len(passing)} passing",
        file=sys.stderr,
        flush=True,
    )
    return priority + sample


def main() -> None:
    os.environ.setdefault("TOOLUNIVERSE_STDIO_MODE", "1")
    os.environ.setdefault("TOOLUNIVERSE_LIGHT_IMPORT", "1")

    prev = _load_prev()

    print("Loading ToolUniverse…", file=sys.stderr, flush=True)
    from tooluniverse import ToolUniverse  # noqa: PLC0415

    tu = ToolUniverse()
    tu._auto_load_tools_if_empty()

    testable = [
        n
        for n, d in tu.all_tool_dict.items()
        if isinstance(d, dict) and d.get("test_examples")
    ]
    print(f"Testable tools: {len(testable)}", file=sys.stderr, flush=True)

    to_test = _select(testable, prev)
    results: dict[str, dict] = dict(prev)

    t_start = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_test_tool, name): name for name in to_test}
        for future in as_completed(futures):
            name, status, detail = future.result()
            results[name] = {
                "status": status,
                "detail": detail,
                "tested": time.strftime("%Y-%m-%d"),
                "tested_epoch": time.time(),
            }
            done += 1
            if done % 50 == 0 or done == len(to_test):
                elapsed = time.time() - t_start
                print(
                    f"  [{done}/{len(to_test)}] {elapsed:.0f}s elapsed",
                    file=sys.stderr,
                    flush=True,
                )

    live = sum(1 for r in results.values() if r.get("status") == "live")
    broken = sum(1 for r in results.values() if r.get("status") == "broken")

    REPORT_PATH.write_text(
        json.dumps(
            {
                "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "summary": {
                    "live": live,
                    "broken": broken,
                    "total_tested": done,
                    "total_known": len(results),
                },
                "tools": results,
            },
            indent=2,
        )
    )
    total_elapsed = time.time() - t_start
    print(
        f"Report written: {live} live, {broken} broken "
        f"(tested {done}/{len(testable)}, {total_elapsed:.0f}s)",
        flush=True,
    )


if __name__ == "__main__":
    main()
