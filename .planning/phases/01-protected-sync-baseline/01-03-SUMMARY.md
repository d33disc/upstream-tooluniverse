---
phase: 01-protected-sync-baseline
plan: 03
subsystem: surface-certification
tags: [python, cli, mcp, rest, integration, lifecycle]
requires: [BASE-02]
provides:
  - "Real discover-inspect-execute-assert probes for Python, CLI, MCP stdio, MCP streamable HTTP, and REST"
  - "Schema-derived C6H6 deterministic reference evidence and structured invalid-operation outcomes"
affects: [baseline-evidence, upstream-sync]
tech-stack: [Python stdlib, MCP client, FastMCP, Uvicorn, pytest]
key-files:
  created: [tests/integration/test_sync_baseline_surfaces.py]
  modified: [scripts/capture_sync_baseline.py]
key-decisions:
  - "MCP stdio uses JSON-RPC lifecycle messages and MCP HTTP uses initialized streamablehttp_client sessions; no raw HTTP approximation is used."
  - "REST probes call the loopback /api/call route and child/server lifecycles are bounded and cleaned up in finally blocks."
requirements-completed: [BASE-02]
status: complete
---

# Phase 1 Plan 3 Summary

The shared surface contract is now proven against the same deterministic
`DegreesOfUnsaturation_calculate` tool. Each runner discovers the tool,
inspects its schema, derives the required `operation=calculate` and
`formula=C6H6` arguments, executes, and asserts DoU `4.0` with `is_integer`
true. The matrix also records an intentional invalid-operation response as a
structured error for every surface.

## Task commits

1. `6dec1ba4` — `feat(01-03): certify five real connection surfaces`
2. `2023cc6f` — `test(01-03): enforce structured surface errors`

## Validation

- `uv run pytest -o addopts='' tests/integration/test_sync_baseline_surfaces.py -q --strict-markers --strict-config --timeout=120` — 7 passed.
- Structured-error matrix test — passed.
- `uv run ruff check scripts/capture_sync_baseline.py tests/integration/test_sync_baseline_surfaces.py` — passed.

## Deviations

- The existing workspace profile preloads the full catalog even when the SMCP
  process receives `--include-tools`; compact mode still exposes only the four
  proxy tools, so the probe verifies the proxy handshake and inspected tool
  execution rather than assuming filtered server load.
- `.planning/config.json` and `ralph-specs/fleet/results/` were pre-existing
  untracked user content and remain untouched.

