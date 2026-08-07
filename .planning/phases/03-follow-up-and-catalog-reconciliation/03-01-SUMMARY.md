---
phase: 03-follow-up-and-catalog-reconciliation
plan: 01
subsystem: testing
tags: [pytest, git, jq, sha256, ast, tdd]

# Dependency graph
requires:
  - phase: 02-upstream-main-integration
    provides: the landed merge (f81448f2) with PR #161 folded in -- this plan re-derives ancestry against 16af425c... live at every run rather than trusting that landing
provides:
  - scripts/audit_registration_chain.py -- single-tool tracer for the six-link registration chain (definition, implementation, category, lazy-registry metadata, generated module, tests), built as pure functions (check_link_*, classify_chain, load_definitions, load_live_categories, audit_names) that Wave 2 (03-02) calls unchanged across ~2,900 names
  - assert_discovery_contract -- pure pass/gated/fail verdict over the CAT-02 discovery surface, mirroring scripts/probe_custom_tools.py's assert_probe_contract split
  - Re-derived, checksummed SYNC-03 evidence (PR #161 ancestry against the live HEAD, never a copied Phase 1 value)
  - A read-only SHA-256 fingerprint of the pre-existing ~2,662-file dirty working tree (D-06), so every later Phase 3 task can prove it neither swept that state into a commit nor reverted it
  - tests/unit/test_audit_registration_chain.py -- unit coverage that TDD-drove out two real bugs in the Task 1 script before Wave 2 scales the same functions
affects: [03-02 (full-catalog registration-chain audit), 03-03 (discovery smoke sample), 03-04 (regeneration guard + evidence publication)]

# Actuals (#2632)
actuals:
  tokens: 53198
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "importlib.util.spec_from_file_location module loading (no scripts/__init__.py) to reuse capture_sync_baseline.py's publish_evidence/verify_checksums/_canonical_json/_contains_secret and audit_upstream_merge.py's extract_definition_names without duplicating them"
    - "Two-stage verdict classification (classify_chain), mirroring audit_upstream_merge.py's classify_finding: primary link-boolean pass, then an archived/gated recheck before finalizing"
    - "assert_*_contract split: gather facts from a live SDK call (probe_discovery), then hand the pass/gated/fail conclusion to a pure, independently-testable function (assert_discovery_contract) -- the same split scripts/probe_custom_tools.py already established for assert_probe_contract, now duplicated for the discovery stage"
    - "Whole-process os.execv re-exec (_ensure_capable_interpreter) into .venv/bin/python when the ambient interpreter cannot import tooluniverse, chosen over probe_custom_tools.py's per-call subprocess dispatch because Wave 2 will call these functions ~2,900 times"

key-files:
  created:
    - scripts/audit_registration_chain.py
    - tests/unit/test_audit_registration_chain.py
    - .planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/tracer/git.json
    - .planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/tracer/worktree_fingerprint.json
    - .planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/tracer/chain_tracer.json
    - .planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/tracer/SHA256SUMS
  modified: []

key-decisions:
  - "_ensure_capable_interpreter re-execs the whole process into .venv/bin/python (once, sentinel-guarded) when the ambient interpreter can't import tooluniverse -- the plan's own literal verify command invokes the script via ambient python3, which has none of tooluniverse's dependencies."
  - "Moved the evidence-directory shutil.rmtree cleanup to the very top of main(), before ancestry derivation or fingerprinting, with a repo-root-boundary guard -- a second run's fingerprint was otherwise seeing the first run's leftover evidence files as new dirty paths, breaking the byte-identical rerun guarantee the plan's acceptance criteria require."
  - "classify_chain([], gated) now returns 'broken' via an explicit empty-links guard, rather than falling through to Python's vacuous all([]) == True -- found by writing the parametrize table Task 2 required, not by inspection; this repository has a recorded history of exactly this empty-as-success shape (T-02-17)."
  - "Extracted assert_discovery_contract out of probe_discovery. Task 1's own action text specified 'an empty result with no gating signal is a failure, not a pass,' but probe_discovery only ever returned raw booleans -- no function anywhere actually drew that conclusion. Writing Task 2's required named empty-result-rejection test (which must run without importing tooluniverse) surfaced that the behavior was specified but never built; completing it stayed inside the same script Task 1 already declared, mirroring the assert_probe_contract precedent Task 2's own read_first pointed at."
  - "Both fixes regenerate chain_tracer.json (additive discovery.verdict/discovery.reason fields) and the sibling evidence files, committed together with the test file in Task 2's commit rather than split across two commits -- the script and its evidence must move together to stay internally consistent."

patterns-established:
  - "Six link-check functions + classify_chain's two-stage verdict, all pure and unit-testable without tooluniverse -- the exact surface Wave 2 (03-02) scales across the full catalog unchanged."
  - "load_live_categories's whole-body regex-with-lookback (_CATEGORY_ENTRY_RE + a 5-line 'Archived at:' marker window) handles single-line, three-physical-line os.path.join(...), and commented-archived default_config.py entries uniformly -- verified against the real file's oxo/interpro_entry/uniprot_proteomes categories, not just synthetic fixtures."

requirements-completed: [SYNC-03, CAT-01, CAT-02]

coverage:
  - id: D1
    description: "PR #161 (16af425c...) ancestry re-derived live against the executing HEAD and recorded with its exit code, never copied from Phase 1's evidence or from research prose"
    requirement: "SYNC-03"
    verification:
      - kind: integration
        ref: "scripts/audit_registration_chain.py --tool DegreesOfUnsaturation_calculate --out <dir> --json; git.json: pr161_ancestor==true, exit_code==0, head_oid matches live `git rev-parse HEAD`"
        status: pass
    human_judgment: false
  - id: D2
    description: "DegreesOfUnsaturation_calculate (credential-free tracer) proven intact across all six registration links, each with concrete resolving evidence"
    requirement: "CAT-01"
    verification:
      - kind: integration
        ref: "chain_tracer.json: verdict==intact, links length==6, every links[].ok==true with non-empty evidence"
        status: pass
    human_judgment: false
  - id: D3
    description: "The same tracer tool is found via the grep_tools path and returns a real parameter schema from get_tool_info, not a gated error object"
    requirement: "CAT-02"
    verification:
      - kind: integration
        ref: "chain_tracer.json: discovery.grep_found==true, discovery.schema_has_parameters==true, discovery.gated==false, discovery.verdict==pass"
        status: pass
    human_judgment: false
  - id: D4
    description: "The pre-existing ~2,662-file dirty working tree is fingerprinted before other Phase 3 work and proven unchanged (neither committed nor reverted) after both tasks"
    verification:
      - kind: other
        ref: "worktree_fingerprint.json count/digest/by_prefix; post-commit set-diff between its recorded paths and live `git status --porcelain` shows only this task's own committed paths as the delta, zero unexplained entries either direction"
        status: pass
    human_judgment: false
  - id: D5
    description: "Pure link-verdict, category-parsing, and discovery-contract logic has unit coverage proving all four classify_chain verdicts, the three load_live_categories entry forms, the credential-gated downgrade, the empty-discovery-result rejection, and audit_names's empty/single/ordering contracts -- without importing tooluniverse"
    requirement: "CAT-01"
    verification:
      - kind: unit
        ref: "tests/unit/test_audit_registration_chain.py (16 tests, 0 skipped); named nodes test_credential_gated_downgrade_missing_link_yields_gated_with_key_names and test_empty_discovery_result_with_no_gating_signal_is_rejected_not_passed"
        status: pass
      - kind: unit
        ref: "tests/unit/test_registry_integrity.py -q (4 passed) -- pre-existing registry gate unaffected"
        status: pass
    human_judgment: false

duration: unknown -- session spanned a context-compaction boundary before Task 1's commit, so the true start time was not captured; the measurable window from Task 1's commit to Task 2's commit is 21 minutes, which excludes all of Task 1's own implementation and debugging time
completed: 2026-08-07
status: complete
---

# Phase 3 Plan 01: Registration-Chain Tracer, Ancestry Re-derivation, and Dirty-Tree Fingerprint Summary

**Single-tool tracer proves the whole Phase 3 spine end to end -- PR #161 ancestry re-derived live, all six registration links intact for `DegreesOfUnsaturation_calculate`, and its discoverability via `grep_tools`/`get_tool_info` confirmed -- before Wave 2 scales the same pure functions across ~2,900 names. TDD unit coverage (Task 2) caught two real gaps in Task 1's own script: a vacuous-truth bug in `classify_chain` on an empty links list, and a discovery-stage pass/fail conclusion the spec called for but that had never actually been built.**

## Performance

- **Duration:** Not reliably known end-to-end (session spanned a context-compaction boundary before Task 1's commit). Measured window: Task 1 commit to Task 2 commit was 21 minutes; the plan document itself was created the prior evening (2026-08-06T21:30:45-04:00).
- **Task 1 committed:** 2026-08-07T08:41:38-04:00
- **Task 2 committed:** 2026-08-07T09:02:45-04:00
- **Tasks:** 2 of 2 complete
- **Files modified:** 6 (1 script, 1 test file, 4 evidence artifacts)

## Accomplishments

- `scripts/audit_registration_chain.py`: a standalone tracer CLI reusing `capture_sync_baseline.py`'s evidence-publishing convention and `audit_upstream_merge.py`'s AST definition extractor via `importlib.util`, never reimplementing either.
- `derive_pr161_ancestry` and `fingerprint_worktree`: SYNC-03's live ancestry re-derivation and D-06's read-only dirty-tree fingerprint, both re-verified byte-identical (modulo their own timestamp fields) across repeated runs at the same commit.
- All six registration links (`check_link_definition` through `check_link_tests`) plus `classify_chain`'s two-stage verdict, proven `intact` end to end for `DegreesOfUnsaturation_calculate` -- and confirmed discoverable via `find_tools_by_pattern` and `tool_specification`.
- `tests/unit/test_audit_registration_chain.py`: 16 tests, zero `tooluniverse` imports, exercising `classify_chain`, `load_live_categories`, `load_definitions`, `audit_names`, and the newly extracted `assert_discovery_contract` by hand-built fixtures and a `tmp_path` mini repository.
- Two real bugs caught by writing those tests before trusting Task 1's script further -- see Deviations below.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end single-tool registration-chain proof, ancestry re-derivation, and dirty-tree fingerprint** - `3f2f1ee0` (feat)
2. **Task 2: Unit coverage for the pure link-verdict and category-parsing logic** - `cd3bb0d0` (test)

_Task 2 is `tdd="true"`; both fixes it drove out (see Deviations) landed inside its own commit alongside the test file, since the regenerated evidence and the fixed script must move together to stay internally consistent._

## Files Created/Modified

- `scripts/audit_registration_chain.py` - `derive_pr161_ancestry`, `fingerprint_worktree`, `load_definitions`, `load_live_categories`, `check_link_definition`/`_implementation`/`_category`/`_lazy_metadata`/`_generated_module`/`_tests`, `classify_chain`, `audit_names`, `assert_discovery_contract`, `probe_discovery`, `_ensure_capable_interpreter`, `main`
- `tests/unit/test_audit_registration_chain.py` - unit coverage for `classify_chain`, `load_live_categories`, `load_definitions`, `audit_names`, `assert_discovery_contract`
- `.planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/tracer/{git.json,chain_tracer.json,worktree_fingerprint.json,SHA256SUMS}` - the tracer's checksummed evidence bundle, regenerated after Task 2's script fixes and re-verified

## Decisions Made

See `key-decisions` in the frontmatter above -- the interpreter re-exec, the determinism fix, and the two TDD-driven script fixes (`classify_chain`'s empty-links guard, `assert_discovery_contract`'s extraction) are the substantive decisions this plan made beyond following the plan text directly. Two of them (the interpreter re-exec necessity, and how to resolve the "empty-result rejection" test's referent between `classify_chain` and the discovery stage) were checked against a second-opinion review before implementation rather than resolved by inspection alone.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Ambient `python3` cannot import `tooluniverse`**

- **Found during:** Task 1, running the plan's own literal verify command
- **Issue:** The verify command invokes the script via ambient `python3` (a pyenv shim), which has neither `tooluniverse` nor any of its dependencies installed.
- **Fix:** `_ensure_capable_interpreter` re-execs the whole process into `.venv/bin/python` once (sentinel-guarded against a loop), mirroring `scripts/probe_custom_tools.py`'s `_module_matches_interpreter` idiom.
- **Files modified:** `scripts/audit_registration_chain.py`
- **Verification:** Running the script via ambient `python3` transparently re-execs and completes, including `tooluniverse`'s own log lines proving the real package loaded.
- **Committed in:** `3f2f1ee0` (Task 1 commit)

**2. [Rule 1 - Bug] `worktree_fingerprint.json` was not byte-identical across repeated runs**

- **Found during:** Task 1, running the script twice per the plan's own determinism acceptance criterion
- **Issue:** `shutil.rmtree(out_dir)` ran near the end of `main()`, just before `publish_evidence`. A second run's fingerprint therefore saw the first run's still-on-disk evidence files as new dirty paths.
- **Fix:** Moved the cleanup to the very top of `main()`, before ancestry derivation or fingerprinting, with a guard refusing to delete anything that is not a strict subdirectory of the repository root.
- **Files modified:** `scripts/audit_registration_chain.py`
- **Verification:** Two runs at an unchanged commit now produce byte-identical `chain_tracer.json`; `git.json`/`worktree_fingerprint.json` match modulo their own timestamp fields.
- **Committed in:** `3f2f1ee0` (Task 1 commit)

**3. [Rule 1 - Bug] `classify_chain([], gated)` returned `"intact"`**

- **Found during:** Task 2, writing the required `pytest.mark.parametrize` table covering all four verdicts
- **Issue:** An empty `links` list satisfies Python's `all(...)` vacuously, so a chain with zero link records silently classified as `intact` rather than as a failure -- the same empty-as-success shape this repository has a recorded history of (T-02-17 in `probe_custom_tools.py`), now found in the verdict function itself.
- **Fix:** Added an explicit `if not links: return "broken"` guard at the top of `classify_chain`.
- **Files modified:** `scripts/audit_registration_chain.py`
- **Verification:** `test_classify_chain_verdicts[empty_links_list_yields_broken_not_vacuous_intact]` passes; re-ran Task 1's full literal verify chain afterward to confirm the real 6-link tracer still verdicts `intact` (the guard does not over-fire on a genuine full link set).
- **Committed in:** `cd3bb0d0` (Task 2 commit)

**4. [Rule 2 - Missing Critical] `probe_discovery` never drew a pass/gated/fail conclusion**

- **Found during:** Task 2, writing the required named "empty-result rejection" test, which per the plan must run without importing `tooluniverse`
- **Issue:** Task 1's own action text specified this behavior explicitly ("an empty result with no gating signal is a failure, not a pass"), but `probe_discovery` only ever returned raw `grep_found`/`schema_has_parameters`/`gated` booleans -- no function anywhere actually classified them into a verdict, so the specified behavior had no testable surface and, more importantly, was never actually enforced.
- **Fix:** Extracted `assert_discovery_contract`, a pure function mirroring `scripts/probe_custom_tools.py`'s `assert_probe_contract` split (gather facts from the live SDK call in `probe_discovery`; hand the pass/gated/fail conclusion to a pure, independently-testable function). `probe_discovery` now calls it and merges `verdict`/`reason` into its result -- additive to `chain_tracer.json`'s `discovery` object.
- **Files modified:** `scripts/audit_registration_chain.py`; regenerated all 4 files under `evidence/staging/tracer/` since `chain_tracer.json`'s schema gained fields
- **Verification:** `test_empty_discovery_result_with_no_gating_signal_is_rejected_not_passed` plus two companion tests pass; re-ran Task 1's full literal verify chain and determinism check afterward -- all green, `discovery.verdict == "pass"` for the real tracer tool, checksums verify.
- **Committed in:** `cd3bb0d0` (Task 2 commit)

---

**Total deviations:** 4 auto-fixed (2 in Task 1's commit: an environment/interpreter issue and a determinism bug; 2 in Task 2's commit: both TDD-driven completions of behavior Task 1's own spec called for but had not built).
**Impact on plan:** All four were necessary for the script to be correct and for the plan's own acceptance criteria to hold. None introduced a new file outside the plan's declared `files_modified` list -- all four landed inside `scripts/audit_registration_chain.py`, already declared, or its already-declared sibling evidence files. No scope creep.

## Issues Encountered

None beyond the four deviations above. Two design forks were checked against a second-opinion review before implementation rather than resolved by inspection alone: (1) whether the interpreter-mismatch problem was real and how to resolve it -- confirmed empirically (`ModuleNotFoundError` under ambient `python3`) before building `_ensure_capable_interpreter`; (2) whether Task 2's "empty-result rejection" behavior item referred to `classify_chain`'s empty-links case or `probe_discovery`'s discovery-stage conclusion -- resolved by locating `probe_custom_tools.py`'s `assert_probe_contract`/`test_empty_list_result_with_no_gating_signal_is_rejected_not_passed` precedent, which settled it as the latter (both were ultimately built, since both were genuine gaps).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 03-02 (full-catalog registration-chain audit) can import `load_definitions`, `load_live_categories`, the six `check_link_*` functions, `classify_chain`, and `audit_names` from `scripts/audit_registration_chain.py` unchanged and call them across the full ~2,900-name catalog -- none of Task 2's fixes altered these functions' signatures, only `classify_chain`'s behavior on a degenerate input `audit_names` never actually produces (it always builds exactly six link records). `assert_discovery_contract` is available for 03-03's discovery smoke sample if it needs the same pass/gated/fail split. No blockers.

---
_Phase: 03-follow-up-and-catalog-reconciliation_
_Completed: 2026-08-07_
