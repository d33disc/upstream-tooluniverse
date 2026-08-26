---
phase: 02-upstream-main-integration
plan: 06
subsystem: governance
tags: [checkpoint, corrective-commit, evidence-publication, traceability, phase-close]

# Dependency graph
requires:
  - phase: 02-upstream-main-integration (02-04)
    provides: findings.json (29 landed_dropped_or_altered candidates, forensically traced), preservation-reclass.json
  - phase: 02-upstream-main-integration (02-05)
    provides: probes/ evidence, corrected --symlinks gate (self_healed_downstream tier), PRES-02 restored to Complete
provides:
  - "One corrective commit on docs/gsd-codebase-map: d08ae18d, restoring tests/unit/test_agentic_tool_env_vars.py::test_openrouter_primary_falls_back_to_claude_cli"
  - "Immutable evidence bundle at evidence/a4d3d95a096a14ce4d147faa20334d24f8db9f9a/ (the refs/audit/remerge OID), checksum-verified two ways"
  - "02-FINDINGS.md Corrective-commit decision + Success Criteria Evidence sections"
  - "ROADMAP.md Phase 2 marked 5/5 plans; REQUIREMENTS.md SYNC-01/SYNC-02/PRES-02 Complete"
affects: [Phase 3 (SYNC-03, depends on Phase 2 closing cleanly), any future re-audit of this merge]

# Actuals
actuals:
  tokens: null
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Human checkpoint handled by the orchestrating session directly (AskUserQuestion), not delegated to a subagent -- gsd-executor has no AskUserQuestion tool, and D-06's one-way reversibility means the decision must be made by the human, not inferred"
    - "publish_evidence()/verify_checksums() from capture_sync_baseline.py reused verbatim for the bundle, matching Phase 1's evidence/<oid>/ convention exactly"

key-files:
  created:
    - .planning/phases/02-upstream-main-integration/evidence/a4d3d95a096a14ce4d147faa20334d24f8db9f9a/ (14 files + SHA256SUMS)
  modified:
    - tests/unit/test_agentic_tool_env_vars.py (restored 1 test method)
    - .planning/phases/02-upstream-main-integration/02-FINDINGS.md (Corrective-commit decision + Success Criteria Evidence sections)
    - .planning/ROADMAP.md (Phase 2 Plans line + per-plan outcomes)
    - .planning/REQUIREMENTS.md (already Complete via 02-05's correction; unchanged here)

key-decisions:
  - "Reviewer decision (human, via AskUserQuestion): approve-subset -- exactly 1 of 29 candidates approved (the missing OpenRouter->Claude CLI fallback regression test); the other 28 rejected as false positives on individually traced evidence, not on aggregate pin-match statistics alone."
  - "All 3 flagged assumptions (A1 union treatment of JSON tool-definition arrays, A2 corrected preservation.json class distribution, A3 base-crossing join treatment) accepted as resolved on measured evidence; none overturned."
  - "The corrective commit was authored by hand against the current tests/unit/test_agentic_tool_env_vars.py content, restored verbatim from the re-derived tree's remerge_blob, and re-verified against present-day agentic_tool.py/llm_clients.py (OpenRouterClient, ClaudeCliClient, _is_available/_current_api_type/_current_model_id all confirmed unchanged) before landing -- not merged or cherry-picked from refs/audit/remerge."
  - "3 full-suite pytest failures (identical 'RuntimeError: no running event loop' in ToolCallable.__call__) were investigated and confirmed pre-existing and unrelated (execute_function.py last touched by 4b2c1c38, before this phase's work) rather than silently accepted or blocking; flagged as a separate follow-up task instead."

requirements-completed: [SYNC-01, SYNC-02, PRES-02]

coverage:
  - id: D1
    description: "Human decision checkpoint resolves before any source-tree write, per D-06's one-way-reversibility gate"
    requirement: "PRES-02"
    verification:
      - kind: manual
        ref: "02-FINDINGS.md '## Corrective-commit decision' section, ISO-8601 ms stamped; git status --porcelain -- src/ tests/ pyproject.toml uv.lock was empty at decision time (verified before recording)"
        status: pass
    human_judgment: true
  - id: D2
    description: "Exactly the approved corrective commit exists, individually attributable, full targeted test suite plus ruff both green, union sweep still holds"
    requirement: "PRES-02"
    verification:
      - kind: integration
        ref: "commit d08ae18d; targeted suite (test_registry_integrity, test_sync_baseline_git, test_audit_upstream_merge, test_probe_custom_tools) 0 failures; ruff check/format clean; union.json net_removed_fork_entries=0, duplicate_name_files=0"
        status: pass
    human_judgment: false
  - id: D3
    description: "Immutable evidence bundle published and independently verified"
    requirement: "SYNC-01, SYNC-02, PRES-02"
    verification:
      - kind: integration
        ref: "verify_checksums() -> True; shasum -a 256 -c SHA256SUMS from inside evidence/a4d3d95a.../ -> all OK, exit 0"
        status: pass
    human_judgment: false

duration: ~1h10min (checkpoint framing + 1 corrective commit + evidence publish + traceability, following directly from 02-05's post-blocker correction in the same session)
completed: 2026-08-06
status: complete
---

# Phase 2 Plan 06: Corrective-commit Decision, Evidence Publication, Traceability Summary

**The human-gated checkpoint resolved to approve-subset: exactly 1 of 29 forensically-traced candidates landed as a corrective commit (a missing regression test for a live fallback code path), the other 28 confirmed false positives. The immutable evidence bundle published and double-verified. Phase 2 closes: SYNC-01, SYNC-02, and PRES-02 all Complete.**

## Performance

- **Duration:** ~1h10min
- **Tasks:** 3 of 3 complete
- **Files modified:** 1 source test file, 3 planning docs, 1 new 14-file evidence bundle

## Accomplishments

- **Task 1 (checkpoint:decision):** Presented the reviewer with the real, forensically-traced candidate list (not the boilerplate 02-04 originally produced) via `AskUserQuestion` -- exactly 1 genuine gap out of 29, with the other 28's individual traced causes. Reviewer approved the 1 candidate and accepted all 3 flagged assumptions. Decision recorded verbatim in `02-FINDINGS.md` with an ISO-8601 ms stamp, `git status --porcelain -- src/ tests/ pyproject.toml uv.lock` confirmed empty at that moment.
- **Task 2:** Restored `test_openrouter_primary_falls_back_to_claude_cli` to `tests/unit/test_agentic_tool_env_vars.py`, authored against present-day file content (not merged from the stage), re-verifying every referenced symbol (`OpenRouterClient`, `ClaudeCliClient`, `_is_available`, `_current_api_type`, `_current_model_id`) still exists unchanged in `agentic_tool.py`/`llm_clients.py`. `ruff format`/`ruff check` clean. Committed alone: `d08ae18d`.
- **Task 3:** Published `evidence/staging/` to the immutable `evidence/a4d3d95a096a14ce4d147faa20334d24f8db9f9a/` (the full `refs/audit/remerge` OID) via `publish_evidence()`, verified with `verify_checksums()` and independently with `shasum -a 256 -c SHA256SUMS`. Added a **Success Criteria Evidence** table to `02-FINDINGS.md` mapping each of the 4 ROADMAP criteria and SYNC-01/SYNC-02/PRES-02 to the exact command whose live output backs it, plus the 3 unresolved edge-coverage rows named explicitly. `ROADMAP.md` updated to `5 plans` with per-plan one-line outcomes.
- **Full default pytest suite run** (not strictly required by every acceptance path, but the plan's own verify block calls for it): 3 pre-existing failures found, investigated, and confirmed unrelated to this phase's work via `git log` (the implicated file, `execute_function.py`, was last touched before this phase began) -- flagged as a separate follow-up task rather than silently accepted or treated as blocking.

## Task Commits

1. **Task 1: Checkpoint decision recorded** - `87cba00a` (docs)
2. **Task 2: Corrective commit landed** - `d08ae18d` (test)
3. **Task 3: Evidence bundle published, traceability updated** - `fa8ebd8f` (docs)

## Files Created/Modified

- `tests/unit/test_agentic_tool_env_vars.py` - restored 1 test method
- `.planning/phases/02-upstream-main-integration/02-FINDINGS.md` - `## Corrective-commit decision`, `## Success Criteria Evidence` sections appended
- `.planning/ROADMAP.md` - Phase 2 `**Plans**: 5 plans executed`, per-plan outcomes
- `.planning/REQUIREMENTS.md` - unchanged this plan (SYNC-01/SYNC-02/PRES-02 already Complete)
- `.planning/phases/02-upstream-main-integration/evidence/a4d3d95a096a14ce4d147faa20334d24f8db9f9a/` - 13 evidence JSON files + `SHA256SUMS`, immutable

## Decisions Made

- See `key-decisions` in frontmatter. The load-bearing one: the checkpoint was handled directly by the orchestrating session via `AskUserQuestion`, not delegated to a subagent, because `gsd-executor` has no human-interaction tool and D-06 explicitly requires a human decision before any source write.

## Deviations from Plan

None requiring correction within this plan's own scope. The 3 unrelated pytest failures discovered during the plan's own verification step were investigated (not silently passed over) and routed to a separate follow-up task rather than treated as this plan's problem to fix -- consistent with the phase's repeated pattern of tracing anomalies to a root cause before deciding whether they are in scope.

## User Setup Required

None.

## Next Phase Readiness

**Phase 2 is complete.** SYNC-01, SYNC-02, and PRES-02 are all `[x]` Complete in `REQUIREMENTS.md` with traceable evidence. Phase 3 (SYNC-03, historical PR #161 ancestry) can proceed; Phase 1's evidence already answers `pr161_ancestor: true` for its own scope, but SYNC-03's closure remains Phase 3's requirement per this plan's explicit prohibition against resolving it here.

---

*Phase: 02-upstream-main-integration*
*Completed: 2026-08-06*
