---
phase: 02
slug: upstream-main-integration
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-06T11:59:50.017Z
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `02-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4.2 — `.venv/bin/python -m pytest` |
| **Config file** | `pytest.ini` (repo root) — default run excludes `tests/tools`, `tests/examples`, `tests/api` and markers `slow`, `require_api_keys`, `network` |
| **Quick run command** | `.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -q` |
| **Full suite command** | `.venv/bin/python -m pytest` (respects `pytest.ini` default excludes; broader tool/API suites require explicit paths per PROJECT.md's "explicitly select affected suites") |
| **Estimated runtime** | ~5 seconds quick / ~180 seconds full |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -q`, plus any unit test file touched by a corrective commit (e.g. `tests/unit/test_sync_baseline_git.py` when the worktree helper is extended).
- **After every plan wave:** Run `.venv/bin/python -m pytest` inside the re-merge worktree before any finding is promoted to "verified".
- **Before `/gsd-verify-work`:** Full suite must be green AND all four phase success criteria must have artifact evidence:
  1. Re-merge branch diff-stat proving containment (no unrelated pre-existing worktree changes).
  2. Entry-level JSON union check passing + `test_registry_integrity.py` green.
  3. Findings artifact fully joined against all 1,392 `preservation.json` paths, with zero entries left unclassified.
  4. Fresh probe results for the selected custom-tool sample, all passing on their own terms.
- **Max feedback latency:** 5 seconds (quick) / 180 seconds (full wave gate).

---

## Requirements → Test Map

Seeded from research. Task IDs are filled in by `/gsd-plan-phase` once PLAN.md files exist;
this table is the authoritative source for what each requirement must prove.

| Req ID | Behavior | Test Type | Automated Command | File Exists |
|--------|----------|-----------|-------------------|-------------|
| SYNC-01 | Re-merge branch excludes unrelated pre-existing worktree changes | scripted check | `git diff --stat <remerge-branch> e0755067 -- .` shows only merge-touched paths, not the dirty-worktree paths Phase 1 recorded as pre-existing | ❌ W0 — new check |
| SYNC-01 | Isolated worktree creation is correct and non-destructive | unit | `.venv/bin/python -m pytest tests/unit/test_sync_baseline_git.py -q` | ✅ Phase 1 covers `create_isolated_worktree` |
| SYNC-02 | Shared tool definitions match upstream; fork-only definitions retained; no net-removed fork-only entry | scripted diff + assertion | Entry-level union per touched `data/*.json`: `len(merged) == len(set(fork_names) \| set(upstream_names))` | ❌ W0 — new check |
| SYNC-02 | No ghost tool-name references after regeneration | unit | `.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -q` | ✅ already covers this |
| PRES-02 | Preservation-flagged custom tools still load and execute | integration (fresh probes, D-04) | Per tool: `tu info <ToolName>` then `tu run <ToolName> <minimal-args>` (or `run_one_function()` equivalent) on the re-merge worktree | ❌ W0 — new probes; sample selection is Claude's Discretion (Assumption A2) |
| PRES-02 | Registration chain (JSON → registry → lazy registry → discovery → execution) stable after regeneration | unit | `.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -q` | ✅ |

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| *(pending — populated from PLAN.md task IDs)* | — | — | — | — | — | — | — | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] **Entry-level JSON union checker** (research Pattern 2) — does not exist. Required before SYNC-02 can be mechanically verified for `data/literature_search_tools.json`, `data/uspto_tools.json`, and any other `data/*.json` the full-tree diff surfaces. Git's line-based merge can mis-resolve overlapping array insertions *without* emitting a conflict marker, so a clean merge is not evidence of a correct merge.
- [ ] **Findings-classification script** — joins the re-merge full-tree diff against `f81448f2`'s tree, then against the pinned baseline (D-06a's two-step check). This is the phase's central new artifact.
- [ ] **Fresh criterion-4 probe harness** for the planner-selected custom-tool sample. Phase 1's `run_python_probe` / `run_cli_probe` in `scripts/capture_sync_baseline.py` are close analogues built for *baseline capture*, not *targeted fresh probing against a specific tool list* — likely reusable with a narrower tool filter rather than rebuilt.
- [x] No framework install needed — pytest, ruff, uv, git, jq all present.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Maintainer can *account for* every preserved asset | PRES-02 | "Account for" is a review judgment over the findings artifact, not a boolean a script can assert; the script proves completeness of the join, a human confirms each classification is right | Read the findings artifact; confirm every one of the 1,392 `preservation.json` paths carries a classification and that the 87 blocker paths each have an explicit disposition |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---

Related: [[02-RESEARCH]] · [[02-CONTEXT]] · [[01-VERIFICATION]] · [[reference_tu_usage_cheatsheet]] · [[feedback_tu_root_cause_discipline]]
