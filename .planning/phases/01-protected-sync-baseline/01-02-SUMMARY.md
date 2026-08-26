---
phase: 01-protected-sync-baseline
plan: 02
subsystem: baseline-evidence
tags: [normalization, providers, retry, checksums, redaction]
requires: [BASE-01, PRES-01]
provides:
  - "Conservative volatile-path normalization and typed invariant validation"
  - "Value-free configured-provider manifest, four-tier catalog sampling, and bounded retry policy"
  - "Canonical, redacted, checksummed evidence publication and verification"
affects: [upstream-sync, embeddings, baseline-evidence]
tech-stack:
  added: []
  patterns: [stdlib-only evidence contract, exact-path allowlists, fixed retry budget]
key-files:
  created: [tests/unit/test_sync_baseline_normalize.py]
  modified: [scripts/capture_sync_baseline.py]
key-decisions:
  - "Only explicit volatile paths are replaced; mappings are sorted while ordered arrays remain ordered."
  - "Configured credentials project to names and booleans only; persistent transient failures exhaust exactly three attempts."
  - "Evidence is published from a temporary sibling tree and covered by sorted SHA256SUMS entries."
requirements-completed: [BASE-02]
coverage:
  - id: D-03
    requirement: BASE-02
    verification: "Retry unit tests assert three total attempts and two fixed 2.0-second sleeps; permanent failures do not retry."
  - id: D-06
    requirement: BASE-02
    verification: "Provider manifest and SHA-256 seeded category sampling tests prove value-free mappings and repeatability."
  - id: D-07
    requirement: BASE-02
    verification: "Normalization/invariant tests preserve schema, ordering, undeclared fields, and DoU=4.0/is_integer=true."
status: complete
---

# Phase 1 Plan 2 Summary

The baseline evidence contract is now deterministic, secret-safe, and tamper-evident. The implementation is intentionally independent of provider SDKs and uses only the standard library.

## Accomplishments

- Added conservative recursive normalization with exact volatile-path allowlists, stable mapping order, explicit unordered-array identity sorting, JSON-serializability checks, structured status/schema validation, and domain invariant checks.
- Added the `DegreesOfUnsaturation_calculate` C6H6 reference contract, enforcing `degrees_of_unsaturation == 4.0` and `is_integer is True`.
- Added value-free provider projection from `ToolUniverseConfig.CREDENTIAL_SPECS`, configured-family mapping requirements, SHA-256 seeded category sampling, and the four-tier evidence metadata contract.
- Added fixed three-attempt retry semantics for timeout/connection/408/429/500/502/503/504 failures with injected 2.0-second sleeps and bounded sanitized diagnostics.
- Added canonical JSON publication from a temporary sibling tree, secret-canary scanning, required-stage green gating, path containment checks, sorted SHA256SUMS generation, and post-publication verification.

## Task Commits

1. Task 1 — `bfb03a23` (`feat(01-02): add deterministic normalization tracer`)
2. Task 2 — `60daa84f` (`feat(01-02): enforce provider tiers and retry evidence`)
3. Task 3 — `5626510a` (`feat(01-02): publish bounded checksummed evidence`)

## Validation

- `uv run pytest -o addopts='' tests/unit/test_sync_baseline_normalize.py -q --strict-markers --strict-config --timeout=60` — 8 passed.
- `uv run ruff check scripts/capture_sync_baseline.py tests/unit/test_sync_baseline_normalize.py` — passed.
- Checksum verification passes for an untouched bundle and rejects a tampered artifact.

## Deviations

No dependencies were added. The unrelated `.planning/config.json` and `ralph-specs/fleet/results/` remain untouched.

## Next Phase Readiness

Plan 01-03 can consume the normalization, provider, retry, and publication contracts to exercise all Python, CLI, MCP, and REST surfaces.
