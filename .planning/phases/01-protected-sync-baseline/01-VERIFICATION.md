---
phase: 01-protected-sync-baseline
verified: 2026-08-04T19:35:00-04:00
status: passed
score: 5/5
overrides_applied: 0
---

# Phase 1: Protected Sync Baseline — Verification

## Goal-backward verdict

The baseline implementation, pre-sync evidence, and exact-head hosted CI are now
validated. All five approved compatibility jobs passed in Test Suite run
`30941714134`, whose `headSha` exactly matches the open PR and local head
`a8cba82d0bc2fef35aaf802bec5ea129ca21aa01`.

## Must-have truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | Maintainers can name exact fork/upstream revisions, merge-base, divergence, and worktree state. | VERIFIED | `evidence/21945440c9f2a15537ba878500a800d9e330eab0/git.json` records full OIDs, merge-base, divergence, branch, staged/unstaged/untracked state, and PR #161 ancestry. |
| 2 | A reproducible pre-sync result set exists for tests, catalog loading, discovery, and representative execution across supported surfaces. | VERIFIED | `baseline.json` is green for all required stages; targeted/broad test summaries and Python, CLI, MCP stdio/HTTP, and REST probe artifacts are present. |
| 3 | Preservation inventory covers custom code, tools, plugins, generated assets, symlink targets, and user-owned untracked metadata without reading contents. | VERIFIED | `preservation.json` is substantive (16k+ lines), records preservation classes and symlink metadata; `git.json` records untracked paths; repaired plugin links are tracked and in-root. |
| 4 | Exact-head hosted CI has exactly five successful Python 3.10–3.14 jobs before the baseline is green. | VERIFIED | Run `30941714134` completed successfully at exact head `a8cba82...`; jobs 3.10, 3.11, 3.12, 3.13, and 3.14 each completed successfully. |
| 5 | The final evidence directory is immutable, complete, and checksummed. | VERIFIED (for captured fork head) | Evidence contains required provenance, preservation, environment, CI, tests, probes, and `SHA256SUMS`; `shasum -a 256 -c` passes for every listed artifact. |

## Requirements coverage

| Requirement | Status | Evidence |
|---|---|---|
| BASE-01 | SATISFIED | Git provenance/isolation artifacts and unit coverage are present. |
| BASE-02 | SATISFIED | Local and surface evidence is green; exact-head hosted CI is green in run `30941714134`. |
| PRES-01 | SATISFIED | Preservation inventory and symlink repair evidence are present and checksummed. |

No Phase 1 requirements are orphaned; all three are declared by the phase plans and
mapped in `REQUIREMENTS.md`.

## Artifact and wiring checks

- `scripts/capture_sync_baseline.py` contains the Git snapshot, preservation,
  normalization, provider, surface, capture-mode, and CI validation entry points.
- `tests/unit/test_sync_baseline_git.py`, `tests/unit/test_sync_baseline_normalize.py`,
  `tests/unit/test_sync_baseline_ci.py`, and
  `tests/integration/test_sync_baseline_surfaces.py` exercise those contracts.
- `.github/workflows/tests.yml` defines the five approved compatibility jobs and the
  comprehensive Python 3.12 lane.
- Evidence `baseline.json` names every required stage and marks each green, but its
  `ci.json` is tied to the prior certified head, not the current PR head.

## Behavioral spot-checks

| Check | Result |
|---|---|
| `jq` required-stage assertion on `baseline.json` | PASS — all 17 required stages green |
| `shasum -a 256 -c SHA256SUMS` | PASS |
| `gh pr view 62` exact head/state | PASS — open draft PR, head `a8cba82...` |
| `gh run view 30941714134` exact-head Test Suite | PASS — exact `headSha`, five successful jobs |

## Anti-pattern scan

No unreferenced `TBD`, `FIXME`, or `XXX` markers were found in the phase's changed
implementation artifacts. The only non-phase files in the worktree are preserved
untracked user content (`.planning/config.json` and `ralph-specs/fleet/results/`); they
were not opened, modified, or included in the evidence payload.

## State inconsistencies and follow-up

- The committed evidence bundle's `ci.json` still records the earlier certified head
  `21945440...`; the newer exact-head run `30941714134` is independently verified
  above but is not yet materialized into that bundle. This is a traceability warning,
  not a failed runtime gate.
- `.planning/STATE.md` has contradictory progress metadata: `status: complete` and
  “Plan: 5 of 5” coexist with `completed_plans: 2` and a “Phase ... EXECUTING” label.
  `.planning/ROADMAP.md` and `REQUIREMENTS.md` correctly mark Phase 1 complete.
- `01-05-SUMMARY.md` still says `commit: pending`; the phase report itself remains
  intentionally uncommitted for the parent agent to include or amend.

Phase 1 may proceed to Phase 2 after the parent decides whether to refresh the
checksummed `ci.json` linkage and reconcile the stale STATE metadata.
