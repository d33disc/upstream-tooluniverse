---
phase: 03-follow-up-and-catalog-reconciliation
plan: 02
subsystem: testing
tags: [pytest, git, jq, sha256, regex, audit]

# Dependency graph
requires:
  - phase: 03-follow-up-and-catalog-reconciliation (plan 03-01)
    provides: scripts/audit_registration_chain.py's six check_link_* functions, classify_chain, audit_names, load_definitions, and load_live_categories -- reused unchanged; also worktree_fingerprint.json, the dirty-tree baseline every task's precondition in this plan checks against.
provides:
  - tier1_scope, run_full_audit, find_duplicate_names, and a --tier1/--tier2/--duplicates chain-mode CLI in scripts/audit_registration_chain.py, composable across independent invocations into one evidence directory
  - Four new tests in tests/unit/test_registry_integrity.py gating links 5 and 6 (generated module + tools/__init__.py import) against a reviewed, checked-in drift baseline that cannot go stale
  - tests/unit/registration_chain_baseline.json -- the 323-name pre-existing registration-chain gap, mechanically derived from Task 1's own Tier 2 audit
  - test_no_duplicate_names_across_live_categories -- a strict xfail gate naming the two genuine live D-05 collisions (UniProt_get_proteome, OpenMeteo_get_air_quality) and routing them to plan 03-04's review
  - Two-tier (Phase-2-touched-set + full-catalog) registration-chain audit evidence and an archived-vs-live duplicate classification, both under evidence/staging/chain/
affects: [03-03 (discovery smoke sample, concurrent wave 2), 03-04 (regeneration guard, evidence publication, and the D-05 human review gate for the two live collisions this plan surfaced)]

# Actuals (#2632)
actuals:
  tokens: 15711
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Two-tier audit on classify_chain's one shared verdict schema (intact/gated/archived/broken), joined by tool name -- Tier 1 (Phase 2's touched set) is provably a subset of Tier 2 (full catalog) rather than a separately re-derived comparison"
    - "Chain-mode CLI composability: --tier1/--tier2/--duplicates are independently runnable into one evidence directory across separate invocations spanning two tasks (and two commits), via _load_existing_chain_evidence's read-existing-then-republish pattern -- publish_evidence itself requires an empty target directory"
    - "Archived-vs-live duplicate classification by live-category COUNT (>=2 => collision), not by presence/absence of a second copy alone -- generalizes correctly across both the 'one live + one uncategorized' shape (HMDB_*) and the 'zero live (archived) + one uncategorized' shape (OxO_*)"
    - "Committed-tree-only reads (git show HEAD:/git ls-tree HEAD) for every link-5/6 and duplicate-classification check, never the working tree -- this checkout carries ~2,662 pre-existing uncommitted files from a concurrent session's regeneration"

key-files:
  created:
    - tests/unit/registration_chain_baseline.json
    - .planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/chain/registration_chain.json
    - .planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/chain/duplicates.json
    - .planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/chain/SHA256SUMS
  modified:
    - scripts/audit_registration_chain.py
    - tests/unit/test_registry_integrity.py

key-decisions:
  - "tier1_scope resolves names via a RECURSIVE load_definitions lookup, not non-recursive, after discovering one of Phase 2's own 213 union.json scope paths (data/packages/machine_learning_tools.json) is nested one level under data/ -- a non-recursive glob would have silently dropped ~20 genuinely-in-scope names from Tier 1's audit."
  - "find_duplicate_names and the test's _load_live_collisions both classify by 'live_count >= 2 => live_collision', not the plan's literal 'only one file's category is live => archived_duplicate' prose. The OxO_* pair has ZERO live categories among its two defining files (broken_apis/oxo_tools.json is never referenced by default_config.py at all, live or commented) -- a literal '== 1' rule would misclassify it as a collision, contradicting the plan's own measured 5-archived/2-live expected split. The '>= 2' generalization was checked against a second-opinion review before implementation and verified to reproduce the plan's exact expected counts."
  - "registration_chain.json composes across independent --tier1/--tier2 (Task 1) and --duplicates (Task 3) CLI invocations, spanning two separate commits, via a read-existing-evidence-then-republish pattern (_load_existing_chain_evidence) -- publish_evidence itself requires an empty output directory. Confirmed byte-identical to Task 1's committed version after Task 3's run (cmp against `git show 2eecf64e:...`), so the read-merge-republish round-trip introduced no unexplained dirty path."
  - "registration_chain_baseline.json's 323-name count is Task 1's actual, mechanically-derived Tier 2 link-5 failure count, not the 279 estimated during planning -- per the plan's own explicit instruction not to force it to the planning-time figure. The 44-name gap is fully explained: names defined only under recursively-nested data/ subdirectories (data/broken_apis/, data/packages/, data/remote_tools/, etc.) that a non-recursive scan cannot see; spot-checked run_scvi_integration (data/remote_tools/scvi_tools.json, no module file at HEAD) as a genuine case, not a bug in the check."

patterns-established:
  - "Two-tier verdict-schema join (established here, reusable for any future catalog-wide vs. touched-set audit split)"
  - "Read-existing-evidence-then-republish for composing independently-runnable CLI flags into one append-only evidence directory across separate commits"
  - "Test-local re-derivation of a small piece of audit logic (_load_live_collisions' ~50-line default_config.py re-parse) rather than importing a phase-scoped script into the canonical registry-integrity test module, so the standing gate never depends on scripts/ or .planning/ paths that later phases may move or clean"

requirements-completed: [CAT-01, CAT-02]

coverage:
  - id: D1
    description: "Two-tier full-catalog six-link audit: Tier 1 over every tool Phase 2's merge touched (22 hand-resolved paths + 213 union.json both-sides paths, 1,314 records), Tier 2 mechanically over the whole catalog (2,790 records), both on classify_chain's one shared verdict field with every Tier 1 name provably present in Tier 2"
    requirement: "CAT-01"
    verification:
      - kind: integration
        ref: "scripts/audit_registration_chain.py --tier1 --tier2 --out evidence/staging/chain --json; registration_chain.json: head_oid matches HEAD, tier1.scope.union_files==213, tier1.scope.hand_resolved_files==22, tier1.records>100, tier2.records>2000, every verdict in {intact,gated,archived,broken}, every tier1 name present in tier2, exclusions.count==126; two runs at one commit byte-identical (cmp); SHA256SUMS verifies"
        status: pass
    human_judgment: false
  - id: D2
    description: "The canonical registry gate (tests/unit/test_registry_integrity.py) extended to links 5 and 6 -- generated module existence and tools/__init__.py import -- against a reviewed, checked-in 323-name baseline that hard-fails on new drift and cannot silently accumulate stale entries"
    requirement: "CAT-01"
    verification:
      - kind: unit
        ref: "tests/unit/test_registry_integrity.py::TestRegistryIntegrity::{test_generated_module_exists_for_defined_names,test_defined_names_imported_in_tools_init,test_no_new_registration_chain_drift,test_baseline_has_no_stale_entries} -- 8/8 passed, 0 skipped; stale-entry gate proven to have teeth (invented name appended -> failure listing it -> restored -> green)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Archived-aware duplicate-name classification: all 7 duplicated names at HEAD mechanically split into 5 archived_duplicate (hygiene debt, at most one copy ever loadable) and 2 live_collision (UniProt_get_proteome, OpenMeteo_get_air_quality -- genuine simultaneous-load collisions), matching the plan's own measured set without any hard-coded name list"
    requirement: "CAT-02"
    verification:
      - kind: integration
        ref: "scripts/audit_registration_chain.py --duplicates --out evidence/staging/chain --json; duplicates.json: records==7, live_collision names sort to [OpenMeteo_get_air_quality,UniProt_get_proteome], archived_duplicate count==5; a --tier1-only run into a clean directory leaves no duplicates.json behind; SHA256SUMS covers both registration_chain.json and duplicates.json"
        status: pass
    human_judgment: false
  - id: D4
    description: "The two genuine live collisions are held open as a loud, strict xfail finding routed to plan 03-04's D-05 review gate -- never silently reconciled, renamed, or resolved by this plan"
    requirement: "CAT-02"
    verification:
      - kind: unit
        ref: "tests/unit/test_registry_integrity.py::TestRegistryIntegrity::test_no_duplicate_names_across_live_categories -- reported xfail with both collision names in the reason (pytest -rx); --runxfail forces it to a real FAILED (exit 1) listing both names and their defining paths, proving the marker is strict, not a disabled test"
        status: pass
    human_judgment: false

duration: ~39min (approximate start 09:18 EDT from the earliest working artifact; measurable commit-to-commit window Task 1 to Task 3 is 15min1s)
completed: 2026-08-07
status: complete
---

# Phase 3 Plan 02: Two-Tier Catalog Audit, Registration-Chain Gate, and Duplicate-Name Classifier Summary

**Scaled plan 03-01's six-link tracer to the full ~2,900-name catalog on one joinable verdict schema, extended the canonical registry gate to links 5/6 against a reviewed 323-name drift baseline, and shipped a mechanical archived-vs-live duplicate-name classifier that holds the two genuine collisions open as a strict xfail routed to human review rather than resolving them.**

## Performance

- **Duration:** ~39 min end to end; the precisely measurable window (Task 1 commit to Task 3 commit) is 15 min 1 s
- **Task 1 committed:** 2026-08-07T09:41:47-04:00
- **Task 2 committed:** 2026-08-07T09:49:37-04:00
- **Task 3 committed:** 2026-08-07T09:56:48-04:00
- **Tasks:** 3 of 3 complete
- **Files modified:** 6 distinct files across 3 commits (2 scripts/tests files touched repeatedly, 1 baseline JSON, 3 evidence artifacts)

## Accomplishments

- `scripts/audit_registration_chain.py`: `tier1_scope` (scope derived from Phase 2's own `git diff-tree --cc` output and `union.json`, never a hand-typed list), `run_full_audit` (both tiers on one verdict schema), `find_duplicate_names` (mechanical archived-vs-live classification), and a `--tier1`/`--tier2`/`--duplicates` chain-mode CLI that composes into one evidence directory across independent invocations.
- Tier 1 (1,314 records, Phase 2's touched set) and Tier 2 (2,790 records, full catalog) both verified `intact`/`gated`/`archived`/`broken` on `classify_chain`'s unchanged verdict schema; every Tier 1 name provably present in Tier 2; two runs at one commit produce a byte-identical `registration_chain.json`.
- `tests/unit/test_registry_integrity.py` extended in place (no second registry-integrity module, per D-04) with four new tests gating links 5/6 against `tests/unit/registration_chain_baseline.json`'s 323 reviewed names, plus a fifth strict-`xfail` test naming the two live D-05 collisions.
- All 7 duplicated names at HEAD mechanically classified: 5 `archived_duplicate` (3 HMDB_*, 2 OxO_*), 2 `live_collision` (`UniProt_get_proteome`, `OpenMeteo_get_air_quality`) -- matching the plan's own measured set with zero hard-coded names.
- Nothing under `src/tooluniverse/` was modified; the pre-existing ~2,662-file dirty working tree is byte-for-byte unchanged (verified before and after every task against plan 03-01's `worktree_fingerprint.json`).

## Task Commits

Each task was committed atomically:

1. **Task 1: Two-tier full-catalog six-link audit on one joinable verdict field** - `2eecf64e` (feat)
2. **Task 2: Extend the canonical registry gate to links 5 and 6 against a reviewed drift baseline** - `078172d6` (test)
3. **Task 3: Archived-aware duplicate-name check separating live collisions from hygiene debt** - `fb52e2d0` (feat)

## Files Created/Modified

- `scripts/audit_registration_chain.py` - `tier1_scope`, `run_full_audit`, `find_duplicate_names`, `_verdict_summary`, `_collect_secrets`, `_load_existing_chain_evidence`, `_run_chain_mode`, `_colon_excluded_count`; CLI flags `--tier1`, `--tier2`, `--duplicates`
- `tests/unit/test_registry_integrity.py` - new helpers (`_load_defined_tool_names_recursive`, `_load_committed_tools_module_names`, `_load_committed_tools_init_imports`, `_load_registration_chain_baseline_names`, `_load_currently_drifting_names`, `_load_live_collisions`) and five new tests
- `tests/unit/registration_chain_baseline.json` - `generated_at_oid`, `rationale`, `names` (323 entries)
- `.planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/chain/{registration_chain.json,duplicates.json,SHA256SUMS}` - the two-tier audit and duplicate-classification evidence bundle

## Decisions Made

See `key-decisions` in the frontmatter above. Two are worth restating: (1) `tier1_scope` had to resolve names recursively, not non-recursively, once a nested Phase-2-scope path (`data/packages/machine_learning_tools.json`) was found empirically; (2) the duplicate classifier's `>= 2 live categories` threshold, not the plan's literal `== 1`, was required to correctly handle the OxO_* pair's zero-live-category shape -- checked against a second-opinion review before implementation, then verified to reproduce the plan's own measured 5/2 split exactly.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's literal duplicate-classification rule misclassifies the zero-live-category case**

- **Found during:** Task 3, reading `default_config.py` to confirm the OxO_* category resolution before writing `find_duplicate_names`
- **Issue:** The plan's `<behavior>` and `<action>` text both describe the archived-vs-collision split as "only one file's category is live => archived_duplicate." `broken_apis/oxo_tools.json` has no `default_config.py` category entry at all (not even commented), so the OxO_* pair has ZERO live categories among its two defining files, not one. A literal `== 1` implementation would classify OxO_* as a collision (2 != 1), producing 4 archived_duplicate + 3 live_collision -- contradicting the plan's own measured "5 archived / 2 live" table one paragraph later in the same plan.
- **Fix:** Implemented `live_count >= 2 => live_collision, else archived_duplicate` in both `find_duplicate_names` (script) and `_load_live_collisions` (test helper) -- the natural generalization ("a collision requires two *simultaneously loadable* copies") that correctly covers both the one-live (HMDB_*) and zero-live (OxO_*) shapes.
- **Files modified:** `scripts/audit_registration_chain.py`, `tests/unit/test_registry_integrity.py`
- **Verification:** `duplicates.json` reproduces the plan's exact expected split (5 archived_duplicate, 2 live_collision, matching names) with zero hard-coded names in the classifier.
- **Committed in:** `fb52e2d0` (Task 3 commit)

**2. [Rule 1 - Bug] `ruff format` corrupted the baseline JSON with a trailing comma**

- **Found during:** Task 2, immediately after the stale-entry teeth check (append-invented-name, run test, restore)
- **Issue:** I gratuitously ran `ruff format` on `tests/unit/registration_chain_baseline.json` (a `.json` file the plan never asked to be ruff-formatted -- only the two `.py` files require it). Some formatting side effect reindented the file to 4 spaces and left a trailing comma before the closing `]`, an invalid-JSON state that failed all four link-5/6 tests with a `JSONDecodeError`.
- **Fix:** Regenerated the baseline file cleanly from the same Python computation used originally (sorted 323 names, `generated_at_oid`, `rationale`, 2-space canonical JSON) via a fresh Write, and stopped invoking any formatter on `.json` files for the remainder of the plan.
- **Files modified:** `tests/unit/registration_chain_baseline.json` (content restored to the correct 323-name, valid-JSON state; no `git restore`/`checkout` used)
- **Verification:** File re-parses as valid JSON; shape criteria re-verified (`jq` check); full test suite green again (8/8, then 9/9 after Task 3).
- **Committed in:** `078172d6` (Task 2 commit) -- caught and fixed before that commit, so the corrupted intermediate state was never committed.

---

**Total deviations:** 2 auto-fixed (both Rule 1 - Bug: one a plan-prose edge case, one a self-inflicted tooling mistake caught immediately by the very next verification step).
**Impact on plan:** Both were necessary for correctness. Deviation 1 was required for the classifier to match the plan's own stated expected results. Deviation 2 was a self-correction of an out-of-scope action (formatting a JSON file the plan never asked to be formatted) that never reached a commit. No scope creep beyond the plan's three declared tasks.

## Plan-text imprecisions noted, not corrected

Two places where this plan's own prose does not exactly match the mechanically-correct result, satisfied in substance per the plan's own escape-hatch language ("or each `broken` record otherwise records that..."):

- **Task 1 acceptance criteria, the `broken` record link-5-provenance jq expression:** `length == [...] | length` has a jq operator-precedence defect (`|` binds looser than `==`) and is not runnable as literally written. It is not in the `<verify>` block. Substance verified directly instead: every `generated_module` link's evidence string (pass or fail) contains "at HEAD," confirming link 5 is always read from the committed tree.
- **Task 3 acceptance criteria, "each archived_duplicate record has exactly one live category key":** true for the 3 HMDB_* records (one live category, "metabolite"), false for the 2 OxO_* records (zero live categories -- see Deviation 1 above). Not in the `<verify>` block. The mechanical `>= 2` classification rule is correct per the plan's own measured-set table; this specific prose sentence undershoots the zero-live edge case it describes.

## Issues Encountered

The dirty-tree fingerprint precondition initially appeared to mismatch at session start: `git status --porcelain`'s live path set (2,662 paths) was a strict subset of plan 03-01's recorded `worktree_fingerprint.json` (2,668 paths), missing exactly 6 paths. Investigation (git log/git ls-files) confirmed all 6 are plan 03-01's own script/test/evidence outputs, committed in `3f2f1ee0`/`cd3bb0d0` after the fingerprint was captured mid-plan -- fully explained, not a real drift. Checked against a second opinion before proceeding (the literal "must match exactly" reading is also permanently unsatisfiable once those commits landed, which would make the plan unexecutable by construction). Froze the resulting 2,662-path set as the working invariant and re-verified it exactly before and after every task.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 03-04 has two concrete, evidence-backed items to act on: (1) the two `live_collision` findings (`UniProt_get_proteome`, `OpenMeteo_get_air_quality`) need a D-05 human decision (rename, remove one, or accept) -- `duplicates.json` carries both defining paths and category keys for that review, and `test_no_duplicate_names_across_live_categories`'s `xfail(strict=True)` will itself fail the build the moment that decision lands and the marker becomes obsolete; (2) the 323-name `registration_chain_baseline.json` gap is available for triage (regenerate a module, or remove a stale definition) with `registration_chain.json`'s full six-link evidence per name. Plan 03-03 (discovery smoke sample) ran concurrently in this wave and is unaffected by anything in this plan. No blockers.

---
*Phase: 03-follow-up-and-catalog-reconciliation*
*Completed: 2026-08-07*
