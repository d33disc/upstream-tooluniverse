---
phase: 01-protected-sync-baseline
plan: 01
subsystem: testing
tags: [git, worktree, symlinks, preservation, pytest]
requires: []
provides:
  - "Isolated full-OID Git provenance and worktree snapshot capture"
  - "Object-based preservation and non-traversing symlink inventory"
  - "Authoritatively repaired PR #161 plugin workspace links"
affects: [upstream-sync, baseline-evidence, embeddings]
actuals:
  tokens: 1250
  tasks: 3
  commits: 3
tech-stack:
  added: []
  patterns: [argv-only Git subprocesses, NUL-safe status/diff parsing, detached worktree isolation]
key-files:
  created: [scripts/capture_sync_baseline.py, tests/unit/test_sync_baseline_git.py]
  modified:
    - plugin/skills/tooluniverse-computational-biophysics-workspace
    - plugin/skills/tooluniverse-organic-chemistry-workspace
    - plugin/skills/tooluniverse-drug-drug-interaction-workspace
key-decisions:
  - "Use upstream/main as the frozen authoritative revision and require PR #161 merge ancestry before link repair."
  - "Treat output and user-owned untracked paths as outside the mutable isolated worktree."
patterns-established:
  - "Git evidence uses full OIDs, porcelain/raw NUL records, explicit cwd, and checked subprocess exit status."
  - "Symlinks are inspected with lstat/readlink and never traversed during inventory."
requirements-completed: [BASE-01, PRES-01]
coverage:
  - id: D1
    description: "Capture exact Git topology and preserve original checkout state through detached worktree isolation."
    requirement: BASE-01
    verification:
      - kind: unit
        ref: "tests/unit/test_sync_baseline_git.py -k provenance or isolation or worktree"
        status: pass
    human_judgment: false
  - id: D2
    description: "Inventory preservation deltas and repair the three authoritative plugin skill links."
    requirement: PRES-01
    verification:
      - kind: unit
        ref: "tests/unit/test_sync_baseline_git.py"
        status: pass
      - kind: other
        ref: "readlink plugin/skills/*-workspace and tracked-target checks"
        status: pass
    human_judgment: false
duration: 12min
completed: 2026-08-04
status: complete
---

# Phase 1 Plan 1 Summary

**Protected Git provenance, preservation inventory, and authoritative plugin-link repair are implemented and tested.**

## Accomplishments

- Added disposable-only `capture_sync_baseline.py` with full-OID provenance, divergence, staged/unstaged/untracked state, detached worktree isolation, and fail-closed parser validation.
- Added object-based preservation classification and symlink metadata inspection that records link text and lexical safety without dereferencing targets.
- Proved PR #161 ancestry and repaired exactly three tracked plugin workspace links to existing in-repository skill directories.

## Task Commits

1. Task 1 — `2e4ab126` (`feat(01-01): capture isolated git provenance`)
2. Task 2 — `0540c27c` (`feat(01-01): inventory preservation deltas safely`)
3. Task 3 — `8a759b14` (`fix(01-01): repair authoritative plugin skill links`)

## Validation

- `uv run pytest -o addopts='' tests/unit/test_sync_baseline_git.py -q --strict-markers --strict-config --timeout=60` — 7 passed.
- `uv run ruff check scripts/capture_sync_baseline.py tests/unit/test_sync_baseline_git.py` — passed.
- All three repaired links resolve to tracked directories under `skills/` and no target content was created or copied.

## Deviations

### Auto-fixed Issues

1. **[Rule 3 — Blocking] Temporary repositories without an `upstream` remote** — snapshot capture records absent remote metadata as unavailable for isolated fixture tests.
2. **[Rule 1 — Bug] Git raw `-z` diff records use NUL-separated metadata/path tokens** — preservation parsing accepts both tab and NUL layouts while retaining path bytes.

No dependencies were added and the unrelated `ralph-specs/fleet/results/` files were not opened or modified.

## Next Phase Readiness

The next plan can add normalization, provider manifests, retry policy, and evidence publication on top of the protected Git and preservation primitives. The disposable parser reserves final-publication flags for Plan 01-04.
