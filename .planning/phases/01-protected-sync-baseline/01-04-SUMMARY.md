---
phase: 01-protected-sync-baseline
plan: 04
status: complete
completed: 2026-08-04
commit: 3a0ab1f0
---

# Plan 01-04 Summary

Implemented the hosted compatibility and exact-head CI evidence contract.

## Delivered

- Expanded `.github/workflows/tests.yml` to exactly Python 3.10–3.14 compatibility jobs with stable display names and a Python 3.12-only comprehensive lane.
- Added version-keyed JUnit artifact collection and bounded step timeouts while retaining uv and existing Actions conventions.
- Added `EXPECTED_CI_JOB_NAMES`, `validate_ci_jobs`, and `collect_ci_evidence` to enforce one exact full-SHA Actions run, successful completion, and the approved five-job set using read-only argv-based `gh` calls.
- Extended capture mode validation to mutually exclusive disposable and final contracts; final mode publishes evidence beneath the captured fork OID and writes result metadata.
- Added unit coverage for workflow shape, stale/ambiguous/failed CI evidence, exact-head matching, argv calls, and all mode rejection cases.

## Verification

- `uv run ruff check scripts/capture_sync_baseline.py tests/unit/test_sync_baseline_ci.py`
- `uv run pytest -o addopts='' tests/unit/test_sync_baseline_ci.py tests/unit/test_sync_baseline_git.py -q --strict-markers --strict-config --timeout=60` (17 passed)
- Parsed workflow YAML and confirmed the five-version matrix.

## Deviations

- No new dependencies, remote mutations, pushes, or pull requests were introduced.
- Existing optional network test step is disabled explicitly; the required offline suites run in the Python 3.12 comprehensive lane.
