---
phase: 02-upstream-main-integration
plan: 05
subsystem: testing
tags: [pytest, tooluniverse-sdk, cli-probing, symlink-verification, evidence-bundle]

# Dependency graph
requires:
  - phase: 01-protected-sync-baseline
    provides: preservation.json (120 symlink-carrying path records, PR #161 repair commit 8a759b14)
  - phase: 02-upstream-main-integration (02-03/02-04)
    provides: the re-merge stage (refs/audit/remerge, stage_merge_oid a4d3d95a) and its findings.json/preservation-reclass.json
provides:
  - scripts/probe_custom_tools.py -- parameterized discover/inspect/execute probe harness (Python + tu CLI) plus a --symlinks verification mode
  - tests/unit/test_probe_custom_tools.py -- pure unit coverage of assert_probe_contract, including the T-02-17 empty-as-success regression guard
  - execution-time evidence that 3 of 120 preservation-recorded symlinks do NOT verify as preserved in the re-merge stage (a genuine, unresolved gate failure, not a false negative)
affects: [02-06 (human decision checkpoint), any future PRES-02 closure work, Phase 3 SYNC-03]

# Actuals (#2632)
actuals:
  tokens: 12252
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "importlib.util.spec_from_file_location module loading (no scripts/__init__.py) to reuse capture_sync_baseline.py helpers without duplicating them"
    - "subprocess dispatch boundary keyed on interpreter identity (_module_matches_interpreter) so the probe runs in-process when already inside the stage's venv and out-of-process otherwise, with the same assert_probe_contract consuming both shapes"
    - "resource_timeout as a first-class gate_reason alongside missing-credential gating, so a slow-but-legitimate first-use embedding load cannot masquerade as a registration failure"

key-files:
  created:
    - scripts/probe_custom_tools.py
    - tests/unit/test_probe_custom_tools.py
    - .planning/phases/02-upstream-main-integration/evidence/staging/probes/*.json
    - .planning/phases/02-upstream-main-integration/evidence/staging/probes/SHA256SUMS
  modified:
    - .planning/REQUIREMENTS.md (PRES-02 reverted from prematurely-marked Complete back to Pending)

key-decisions:
  - "The 3 plugin/skills/*-workspace symlinks verdict 'retargeted' against preservation.json's phase1_target, and this verdict was left standing rather than reconciled away -- the plan's own acceptance criteria treat any non-'preserved' verdict on this set as a hard gate failure requiring human resolution, not a finding to record and continue past."
  - "PRES-02 reverted from Complete to Pending in REQUIREMENTS.md. It was marked complete by 02-03 (source-layer conflict resolution), before 02-05 -- the plan whose explicit job is to prove the plugin-asset half of PRES-02 by execution-time symlink verification -- had run. That verification now shows the requirement does not currently hold for 3 of 120 records."
  - "Tool_RAG's per-surface probe timeout raised to 480s and wrapped in explicit subprocess.TimeoutExpired handling on both the Python and CLI probe paths, after live-testing showed first-use CPU embedding inference over the full ~2,300-tool catalog can exceed 480s; either surface hitting that ceiling is recorded as gated with gate_reason='resource_timeout', never as a crash or a fail."
  - "_rerun_registry_integrity calls subprocess.run directly with an explicit cwd=stage_path, not capture_sync_baseline.py's _run_command (which has no cwd parameter and silently inherits the caller's), and passes --no-cov so pytest.ini's coverage-report footer cannot be mistaken for the pass/fail summary line."

patterns-established:
  - "Parameterized probe harness generalizes capture_sync_baseline.py's single-fixed-tool probe into a PROBE_SAMPLE-driven suite without touching the original file, reusable for any future stage-verification plan."

requirements-completed: []

coverage:
  - id: D1
    description: "6-tool PROBE_SAMPLE (2 fork-only USPTO, 2 finder tool_definition-class, 1 offline control, Tool_RAG) completes discover -> inspect -> execute through both Python core and tu CLI inside the re-merge stage"
    requirement: "PRES-02"
    verification:
      - kind: integration
        ref: "scripts/probe_custom_tools.py --stage <stage> --json; evidence/staging/probes/summary.json (failed:0, passed:3, gated:3, sample:6)"
        status: pass
    human_judgment: false
  - id: D2
    description: "assert_probe_contract's six verdict outcomes have unit coverage, including a named T-02-17 empty-as-success regression guard"
    verification:
      - kind: unit
        ref: "tests/unit/test_probe_custom_tools.py -- test_assert_probe_contract_verdicts, test_empty_list_result_with_no_gating_signal_is_rejected_not_passed, test_empty_dict_result_with_no_gating_signal_is_also_rejected, test_none_result_with_no_gating_signal_is_rejected"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every preservation.json symlink record verifies preserved in the re-merge stage, and the registration-chain gate is green after the probe run"
    requirement: "PRES-02"
    verification:
      - kind: integration
        ref: "scripts/probe_custom_tools.py --stage <stage> --symlinks --json; evidence/staging/probes/symlinks.json"
        status: fail
    human_judgment: true
    rationale: "3 of 120 records (plugin/skills/*-workspace, Phase 1's PR #161 hard-gated set) verdict 'retargeted', not 'preserved'. This is a genuine gate failure requiring a human decision between two remedies (re-pin fork_oid past repair commit 8a759b14 and rebuild the stage, or amend the gate's comparand) -- not something further automation can resolve within this plan's scope. registry_integrity_at_probe_time is green (exit_code 0) and the remaining 117 records are unaffected."

duration: ~3h (includes ~10min Tool_RAG live-timeout characterization + a stalled 10min foreground re-run superseded by the already-verified background result)
completed: 2026-08-06
status: blocked
---

# Phase 2 Plan 05: Probe Custom Tools and Verify Preserved Symlinks Summary

**Parameterized discover/inspect/execute probe harness proves 6 preservation-linked tools load and run in the re-merge stage (3 pass, 3 credential/timeout-gated, 0 fail) -- but the companion `--symlinks` mode's hard gate trips: 3 of Phase 1's PR #161-repaired `plugin/skills/*-workspace` links verdict "retargeted" against `preservation.json`, because the stage is deliberately built from a pre-repair fork commit. Plan is BLOCKED pending a human decision on the remedy.**

## Performance

- **Duration:** ~3h (dominated by live-testing Tool_RAG's real embedding-inference timeout behavior against the stage, twice, plus forensic tracing of the symlink divergence's git lineage)
- **Tasks:** 2 of 3 complete (Task 1, Task 2 done and committed; Task 3's code and artifacts are committed, but its hard-gate acceptance criteria are NOT met)
- **Files modified:** 11 (2 source files, 8 evidence artifacts, 1 requirements doc)

## Accomplishments

- `scripts/probe_custom_tools.py`: a standalone, parameterized probe harness reusing `scripts/capture_sync_baseline.py`'s helpers (`_run_command`, `normalize_probe_result`, `inspect_symlink`, `_contains_secret`, `run_git`) via `importlib.util.spec_from_file_location`. Runs both the Python SDK surface and the `tu` CLI surface against the re-merge stage's own `.venv`, never the main checkout's environment.
- `assert_probe_contract`: a pure, ToolUniverse-import-free function classifying each probe into `pass` / `gated` / `fail`, with an explicit `fail` (not `pass`) for an empty result carrying no gating signal -- the T-02-17 regression this repository has a recorded history of.
- Live-verified against the real stage: `DegreesOfUnsaturation_calculate` (offline control) passes on both surfaces; `USPTO_get_patent_assignment` / `USPTO_get_patent_transactions` gate cleanly on `USPTO_API_KEY`; `Tool_Finder_Keyword` / `Tool_Finder_LLM` pass; `Tool_RAG` gates on `resource_timeout` on both surfaces (first-use CPU embedding inference over the ~2,300-tool catalog exceeds the 480s budget -- expected per this plan's own `credential_expectation` field).
- `tests/unit/test_probe_custom_tools.py`: 21 tests, zero `tooluniverse` imports, covering all six `assert_probe_contract` verdict paths plus `PROBE_SAMPLE` shape invariants -- passes clean under `pytest.ini`'s default selection.
- `--symlinks` mode added and run for real against the stage: reads all 120 `preservation.json` symlink-carrying records, classifies each via `inspect_symlink` (lstat/readlink only, no traversal), and re-runs `tests/unit/test_registry_integrity.py` inside the stage to close the loop (green: `4 passed, 2 warnings`).
- **The hard gate tripped, as designed, and was left standing.** 3 of 120 records -- the `plugin/skills/*-workspace` links Phase 1 repaired from authoritative PR #161 evidence -- verdict `retargeted`. `main()` returns 1.

## Task Commits

Each task was committed atomically:

1. **Task 1: Parameterized custom-tool probe harness running inside the re-merge stage** - `942b7979` (feat)
2. **Task 2: Unit coverage for the probe contract, including the empty-as-success rejection** - `0f074df7` (test)
3. **Task 3: Verify preserved plugin symlinks and the registration chain hold in the stage** - `f5a4ee16` (feat) -- code and artifacts committed; **acceptance criteria NOT met** (see Blocker below)

**No plan-completion metadata commit was made.** This plan is not complete; see Blocker.

## Files Created/Modified

- `scripts/probe_custom_tools.py` - `PROBE_SAMPLE`, `probe_tool_python`, `probe_tool_cli`, `assert_probe_contract`, `run_probe_suite`, `run_symlink_verification`, `main`
- `tests/unit/test_probe_custom_tools.py` - unit coverage for `assert_probe_contract` and `PROBE_SAMPLE`
- `.planning/phases/02-upstream-main-integration/evidence/staging/probes/*.json` - one file per sampled tool, `summary.json`, `symlinks.json`
- `.planning/phases/02-upstream-main-integration/evidence/staging/probes/SHA256SUMS` - checksums for everything under `probes/` (verifies clean: `shasum -a 256 -c SHA256SUMS` exits 0)
- `.planning/REQUIREMENTS.md` - `PRES-02` reverted from `[x]` Complete to `[ ]` Pending, with an inline note pointing here

## Decisions Made

- **Left the "retargeted" verdict standing rather than reconciling it to "preserved."** An earlier draft of this script computed `landed_link_text` / `pin_link_text` evidence fields alongside the verdict; those fields are informational only and never feed `_classify_symlink_verdict`'s return value. The plan's own acceptance criteria are explicit that any non-`preserved` verdict on this set is a hard gate failure requiring the resolution to be fixed upstream and re-run, not something this plan may launder into a pass.
- **Reverted `PRES-02` to Pending in `.planning/REQUIREMENTS.md`.** It had been marked Complete by plan 02-03 (source-layer conflict *resolution*, i.e. choosing how conflicts merge), which is a different concern from this plan's execution-time *verification* that the resolved state actually holds. Leaving a false "Complete" marker in place while this plan's own fresh evidence contradicts it would be worse than correcting it.
- **`Tool_RAG` given a 480s per-surface timeout, with `resource_timeout` as an explicit third gate reason** alongside missing-credential gating. Confirmed via direct testing that a single `run_one_function` call for `Tool_RAG` can exceed 600s on first use (CPU-only SentenceTransformer inference over the full catalog); both `probe_tool_python` and `probe_tool_cli` now catch `subprocess.TimeoutExpired` and return a gated result instead of crashing the suite.
- **`_rerun_registry_integrity` uses `subprocess.run(..., cwd=stage_path)` directly**, not `capture_sync_baseline.py`'s `_run_command` (which has no `cwd` parameter and silently inherits the caller's), and passes `--no-cov` -- `pytest.ini`'s coverage-report footer ("N files skipped due to complete coverage.") was otherwise the actual last stdout line and got mistaken for the pass/fail summary.
- **Only the last non-empty stdout line is parsed as JSON** in `probe_tool_python`'s subprocess dispatch, because the stage's own `tooluniverse` logger writes info-level lines to stdout before the JSON payload.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `probe_tool_python`'s subprocess dispatch parsed the wrong stdout line as JSON**
- **Found during:** Task 1, live-testing against the real stage
- **Issue:** The stage subprocess prints `tooluniverse`'s own info-level log lines to stdout before the JSON payload; naive `json.loads(stdout)` failed.
- **Fix:** Parse only the last non-empty line of stdout as JSON.
- **Files modified:** `scripts/probe_custom_tools.py`
- **Committed in:** `942b7979`

**2. [Rule 1 - Bug] `Tool_RAG` probes crashed the whole suite on timeout instead of gating**
- **Found during:** Task 1, live-testing
- **Issue:** Both the Python-surface and CLI-surface `Tool_RAG` calls can exceed 480s on first use (full-catalog CPU embedding inference); the original code had no timeout handling and an uncaught `subprocess.TimeoutExpired` crashed `run_probe_suite`.
- **Fix:** Wrapped both `probe_tool_python` and `probe_tool_cli` in `try`/`except subprocess.TimeoutExpired`, returning a `gate_reason: "resource_timeout"` result; raised `Tool_RAG`'s per-tool timeout to 480s.
- **Files modified:** `scripts/probe_custom_tools.py`
- **Committed in:** `942b7979`

**3. [Rule 1 - Bug] `_rerun_registry_integrity` could silently collect the wrong test file**
- **Found during:** Task 3
- **Issue:** Using `capture_sync_baseline.py`'s `_run_command` (no `cwd` parameter) would run pytest from the main checkout's cwd while pointing at the stage's interpreter -- `pytest.ini`'s `pythonpath = src` and relative test-path resolution would then silently resolve against the wrong tree.
- **Fix:** Call `subprocess.run` directly with an explicit `cwd=stage_path`.
- **Files modified:** `scripts/probe_custom_tools.py`
- **Committed in:** `f5a4ee16`

**4. [Rule 1 - Bug] Registry-integrity summary line extraction picked up the coverage footer, not the pass/fail line**
- **Found during:** Task 3
- **Issue:** `pytest.ini`'s default `addopts` include a coverage report; its footer ("N files skipped due to complete coverage.") was the actual last stdout line, not the "N passed" summary.
- **Fix:** Added `--no-cov` to the pytest invocation and replaced naive `lines[-1]` extraction with a regex (`\b\d+\s+(passed|failed|error)\b`) searched in reverse.
- **Files modified:** `scripts/probe_custom_tools.py`
- **Committed in:** `f5a4ee16`

---

**Total deviations:** 4 auto-fixed (all Rule 1, bugs discovered via live testing against the real stage rather than only unit-testing the pure contract logic).
**Impact on plan:** All four were necessary for the probe harness to run correctly and honestly against the real stage; none represent scope creep.

## Issues Encountered — BLOCKER (plan not complete)

**Task 3's hard-gate acceptance criterion is not met.** `jq -e '[.links[] | .verdict] | map(. == "preserved") | all' probes/symlinks.json` is **false**. All 3 gated links (`plugin/skills/tooluniverse-computational-biophysics-workspace`, `plugin/skills/tooluniverse-drug-drug-interaction-workspace`, `plugin/skills/tooluniverse-organic-chemistry-workspace`) verdict `retargeted`.

**What was found, concretely:**
- Each link is still genuinely a symlink in the stage (`stage_is_symlink: true` for all 3 -- no destructive overwrite by a regular file or directory).
- Each link's on-disk target carries a spurious `-workspace` suffix, e.g. `plugin/skills/tooluniverse-computational-biophysics-workspace -> ../../skills/tooluniverse-computational-biophysics-workspace` (dangling -- that target directory does not exist in the stage).
- `preservation.json`'s recorded `phase1_target` for the same path is `../../skills/tooluniverse-computational-biophysics` (no `-workspace` suffix), which does exist and is a real directory in the stage.

**Root cause (git lineage, verified via `git show <oid>:<path>` and `git merge-base --is-ancestor`):**
- The re-merge stage is deliberately built from `e0755067`, the pre-merge fork parent (`02-CONTEXT.md` D-05).
- The link's broken, self-referential target is inherited unchanged from `e0755067` -- `git status` classifies these 3 paths as fork-only `A` (add), with no upstream counterpart, so the merge auto-resolves them identically to the fork's pre-merge state on every re-derivation. This is not something plan 02-03's conflict-resolution choices could have affected.
- The repair, commit `8a759b14` ("fix(01-01): repair authoritative plugin skill links"), landed downstream of both `e0755067` and the original landed merge `f81448f2`. Verified: `git merge-base --is-ancestor 8a759b14 21945440` → true (it *is* an ancestor of the Phase 1 pin); `git merge-base --is-ancestor 8a759b14 e0755067` → false; `git merge-base --is-ancestor 8a759b14 f81448f2` → false.
- `f81448f2` (the original landed merge) has the identical broken target -- confirmed byte-for-byte via `git show`. This is corroborated independently by plan 02-04's `findings.json` / `preservation-reclass.json`, which record no disagreement for this path (landed and the re-derived stage tree agree with each other, both pre-repair).
- **This is not novel merge damage introduced by this integration effort.** But it also does not satisfy this plan's gate, which requires matching the *repaired* Phase 1 pin, not the pre-repair fork parent -- those are two different authoritative states, and the stage's deliberate construction from `e0755067` (chosen for legitimate review-instrument reasons, `02-CONTEXT.md` D-05/D-06) never had a path to include the later repair.

**This is a Rule 4 architectural decision, not something this plan can auto-resolve within its own scope** (the hard prohibitions explicitly forbid mutating the stage or reaching outside this plan's declared file list). Two remedies were identified and are presented for human decision in `.planning/phases/02-upstream-main-integration/evidence/staging/probes/symlinks.json`'s `scope_note`:

- **(a)** Re-pin `fork_oid` to a commit that is a descendant of `8a759b14` and rebuild the re-merge stage, so the stage's own tree carries the repair; or
- **(b)** Amend this plan's gate to compare the stage against the fork parent's recorded pre-repair state (or against `f81448f2`) rather than against the Phase 1 pin's `preservation.json`, on the basis that the repair is a downstream, self-healed correction outside this specific stage's review window.

Neither remedy was applied. The verdict, the evidence, and both options are recorded in the committed artifact rather than silently worked around.

**registry_integrity_at_probe_time is green** (`exit_code: 0`, `"4 passed, 2 warnings in 2.86s"`) -- the catalog's registration chain is unaffected; this is purely a symlink-target discrepancy on 3 of 120 records.

**A benign false positive in the credential-string grep:** the acceptance-criteria grep pattern matches `sk-` inside `tooluniverse-polygenic-risk-score` (`ri`**`sk-`**`score`). Manually confirmed this is a path/tool name, not a credential.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**This plan is BLOCKED, not complete.** `02-06-PLAN.md` depends on both `02-04` and `02-05`; do not proceed past 02-06's checkpoint without a human decision on the remedy above. `.planning/REQUIREMENTS.md`'s `PRES-02` has been reverted to Pending to reflect this accurately. `STATE.md`'s plan counter was intentionally NOT advanced and `ROADMAP.md` / `requirements mark-complete` were intentionally NOT run, so the pipeline does not silently advance past an unmet gate.

Everything else in this plan's scope is genuinely done and reusable once the blocker resolves: the probe harness, its test coverage, and the symlink-verification mode all work correctly and need no further code changes -- only a decision on which authoritative state the gate should compare against.

---

## Self-Check: PASSED

All 6 created/modified files confirmed present on disk; all 3 task commits (`942b7979`, `0f074df7`, `f5a4ee16`) confirmed present in `git log --oneline --all`.

---

*Phase: 02-upstream-main-integration*
*Completed: 2026-08-06 (blocked)*
