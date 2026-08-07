---
phase: 03-follow-up-and-catalog-reconciliation
plan: 03
subsystem: testing
tags: [pytest, git, jq, sha256, tdd, discovery]

# Dependency graph
requires:
  - phase: 02-upstream-main-integration
    provides: "union.json (both-sides union artifact recording fork_oid/upstream_oid/merged_oid and per-file name counts) -- this plan re-derives the new-upstream pool's actual names from those OIDs via git show, since union.json itself carries only counts"
  - phase: 03-follow-up-and-catalog-reconciliation
    provides: "plan 03-01's worktree_fingerprint.json (dirty-tree precondition baseline) and its capture_sync_baseline.py-reuse idiom (publish_evidence/verify_checksums via importlib.util)"
provides:
  - scripts/smoke_discovery_sample.py -- select_sample, probe_grep_tools, probe_get_tool_info, classify_discovery, run_discovery_suite, main; a mechanically-selected, gated-aware discovery smoke suite
  - evidence/staging/discovery/{discovery.json,SHA256SUMS} -- CAT-02's discoverability evidence: 11 sampled tools (5 preserved-custom, 5 new-upstream, 1 offline control), all passing, against catalog_size=2658
  - tests/unit/test_smoke_discovery_sample.py -- 11 tests covering all 6 classify_discovery outcomes plus select_sample's gated-exclusion, emptied-pool, and cap/determinism behavior
affects: [03-04 (regeneration guard + evidence publication; inherits the gated:[] live-evidence limitation and the two probe_discovery divergences documented below)]

# Actuals (#2632)
actuals:
  tokens: 14977
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "importlib.util.spec_from_file_location module loading (no scripts/__init__.py) to reuse capture_sync_baseline.py's publish_evidence/verify_checksums/_canonical_json/_contains_secret without duplicating them -- same idiom as scripts/audit_registration_chain.py and tests/unit/test_sync_baseline_git.py"
    - "Cap-then-gate sample selection: pools are capped at POOL_CAP in flat, globally sorted order FIRST, then any capped name present in the gated mapping is removed into a separate list -- never backfilled with the next-sorted name, so an accident of which credentials happen to be configured cannot silently reshape the sample (T-03-19)"
    - "classify_discovery checks gating before found/schema, mirroring assert_discovery_contract (03-01) and assert_probe_contract (Phase 2) -- a gated tool is structurally never 'found' (excluded from all_tool_dict at load_tools() time), so gating must be ruled out first or its absence reads as catalog damage"
    - "Real tmp_path git repositories (git init -b main, repo-local user.email/user.name, real commits) as unit-test fixtures for functions that shell out to git show -- same house pattern as tests/unit/test_sync_baseline_git.py's repo() helper; a mocked git response would not exercise the real code path"

key-files:
  created:
    - scripts/smoke_discovery_sample.py
    - tests/unit/test_smoke_discovery_sample.py
    - .planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/discovery/discovery.json
    - .planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/discovery/SHA256SUMS
  modified: []

key-decisions:
  - "Pool 1 uses a flat, globally-sorted cap-5 across both hand-resolved files combined, not a per-file allocation -- even though this excludes uspto_tools.json's pair entirely (both sort after the 6 literature-agent names). The plan's literal text says 'cap each of pools 1 and 2 at five names, taken in sorted order'; a per-file or round-robin split would have guaranteed USPTO representation and produced a non-empty gated array, but that is fitting the method to a preferred result -- exactly what T-03-19 exists to prevent. The consequence (USPTO's pair, gated on USPTO_API_KEY, not represented in this run) is written into discovery.json's exclusions array rather than engineered around."
  - "union.json records only per-file name counts and mostly-empty anomaly lists, not literal per-side name sets, contrary to the plan's read_first description ('the files array and per-file name sets that define the new-upstream pool'). The new-upstream pool is instead re-derived from the exact git blobs those counts were computed from (fork_oid/upstream_oid, both recorded in union.json itself) via git show <oid>:<path>, restricted to verdict==union_ok files where merged_name_count==upstream_name_count (a conservative soundness filter skipping files where the fork also added names) and excluding src/tooluniverse/data/broken_apis/. Validated against the real repository before writing select_sample: this derivation reproduces the correct name sets on a spot-checked file."
  - "probe_grep_tools checks exact-name membership in find_tools_by_pattern's returned matches, not just non-empty match count -- diverging from scripts/audit_registration_chain.py's probe_discovery, which treats bool(matches) as 'found'. find_tools_by_pattern does an unanchored re.search over tool names, so a shorter name that is a substring of another real tool's name would produce a false-positive 'found' under the bool(matches) check. This is a deliberate improvement over the reused pattern, not an oversight -- worth reconciling if 03-04 scales probe_discovery itself, so the two scripts don't silently diverge in the opposite direction."
  - "run_discovery_suite loads the full catalog once, unfiltered (load_tools() with no include_tools filter), and reuses one ToolUniverse instance across the whole sample -- required by the plan's action text ('call load_tools() with no filter so the sample is exercised against the real loadable catalog') and different from probe_discovery's per-tool filtered load. This is what makes catalog_size=2658 a meaningful, real number rather than an artifact of a filtered load."
  - "Investigated and ruled out (empirically, not by inspection) a suspected AgenticTool gating blind spot: execute_function.py gates AgenticTool-type tools via a separate AgenticTool.has_any_api_keys() check that does not populate _excluded_api_key_tools, which select_sample relies on exclusively. A live unfiltered load in this environment confirmed all 5 pool-1 literature-agent candidates (AgenticTool/ComposeTool) resolve with real schemas despite no LLM keys in the ambient shell -- .tooluniverse/env.py resolves them from .env.1password at ToolUniverse() construction time. The blind spot is real in principle (a future environment with zero LLM keys resolvable by any path would see these AgenticTool names silently classify as fail rather than gated) but did not fire here; noted in discovery.json's environment-dependency exclusion."

patterns-established:
  - "classify_discovery(grep_result, info_result, gated_keys) as a three-argument pure verdict function, one layer more granular than 03-01's assert_discovery_contract(single merged dict) -- because the plan specified probe_grep_tools and probe_get_tool_info as two separate probes rather than one probe_discovery, the verdict function takes their two outputs separately plus the gated-mapping lookup as a third argument."
  - "select_sample(repo_root, excluded_api_key_tools, union_json_path=None) -- the union_json_path parameter defaults to the real Phase 2 evidence path but is overridable, so unit tests point it at a tmp_path fixture instead of replicating a deep, hash-named evidence directory structure."

requirements-completed: [CAT-02]

coverage:
  - id: D1
    description: "A sample spanning preserved-custom and new-upstream tools is found by grep_tools and returns a real parameter schema from get_tool_info against the live loaded post-Phase-2 catalog (catalog_size=2658)"
    requirement: "CAT-02"
    verification:
      - kind: integration
        ref: ".venv/bin/python scripts/smoke_discovery_sample.py --out <dir> --json; discovery.json: failed==0, sample spans preserved-custom/new-upstream/offline-control pools, catalog_size==2658 (>1000)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A tool whose required_api_keys are unmet is excluded from the schema-inspection sample and recorded separately as gated with its missing key names, never counted as a discovery failure. This run's live mechanical sample drew zero gated names (pool 1's cap-5 excluded the only gated candidates, uspto_tools.json's pair) -- discovery.json's gated array is [] for this run, and the exclusion mechanism itself is proven by unit tests exercising the identical code path (classify_discovery and select_sample do not distinguish a live-catalog gated name from a fixture one), not by this run's live evidence"
    requirement: "CAT-02"
    verification:
      - kind: unit
        ref: "tests/unit/test_smoke_discovery_sample.py::test_select_sample_gated_exclusion_removes_names_without_backfill; ::test_classify_discovery_verdict_table[info-gated-error-object-is-gated]; ::test_classify_discovery_verdict_table[gated-mapping-hit-is-gated-even-when-grep-empty]; ::test_select_sample_records_emptied_pool_without_substituting"
        status: pass
    human_judgment: false
  - id: D3
    description: "The credential-free offline control (DegreesOfUnsaturation_calculate) passes outright, so a red sample cannot be blamed on the environment"
    requirement: "CAT-02"
    verification:
      - kind: integration
        ref: "discovery.json: results[] where name==DegreesOfUnsaturation_calculate has verdict==pass"
        status: pass
    human_judgment: false
  - id: D4
    description: "The sample is selected mechanically from Phase 2's own recorded artifacts plus one offline control, and the selection rule and every exclusion (deferred transport surfaces -> Phase 5/SURF-01, the credential-gated population, both pool-2 anomaly filters, pool 1's USPTO exclusion) are written into discovery.json so a reviewer can see what was covered and what was not"
    requirement: "CAT-02"
    verification:
      - kind: integration
        ref: "discovery.json: exclusions array (5 entries) names CLI/MCP stdio/MCP HTTP/REST/Phase 5/SURF-01 and the credential-gated population; every sample[] record carries non-empty name/pool/selection_rule/source_path"
        status: pass
      - kind: unit
        ref: "tests/unit/test_smoke_discovery_sample.py::test_select_sample_caps_pools_sorts_and_is_deterministic"
        status: pass
    human_judgment: false
  - id: D5
    description: "Pure selection and verdict logic (classify_discovery's 6 outcomes; select_sample's gated-exclusion, emptied-pool, and cap/sort/determinism behavior) has unit coverage that runs without importing tooluniverse or instantiating ToolUniverse"
    requirement: "CAT-02"
    verification:
      - kind: unit
        ref: "tests/unit/test_smoke_discovery_sample.py (11 tests, 0 skipped); named nodes test_classify_discovery_empty_result_with_no_gating_signal_is_fail_never_pass and test_select_sample_gated_exclusion_removes_names_without_backfill"
        status: pass
      - kind: unit
        ref: "tests/unit/test_registry_integrity.py -q (9 passed, 1 xfail unrelated pre-existing D-05 collision) -- pre-existing registry gate unaffected"
        status: pass
    human_judgment: false

duration: 5min (Task 1 commit to Task 2 commit; excludes design/research time before Task 1's commit, which spanned this session's own context-compaction boundary)
completed: 2026-08-07
status: complete
---

# Phase 3 Plan 03: Discovery Smoke Suite over a Mechanical, Gated-Aware Sample Summary

**A mechanically-selected 11-tool sample (5 preserved-custom, 5 new-upstream, 1 offline control) is proven discoverable via the live `grep_tools`/`get_tool_info` primitives against the real loaded catalog (`catalog_size=2658`), with gated-tool handling proven by dedicated unit tests rather than by this run's live evidence, since the mechanical sample happened to draw zero of this environment's 86 gated tools.**

## Performance

- **Duration:** 5 min measured (Task 1 commit `10:38:31-04:00` to Task 2 commit `10:43:31-04:00`); design, research, and implementation time before Task 1's commit is not reliably measurable (session spanned a context-compaction boundary).
- **Task 1 committed:** 2026-08-07T10:38:31-04:00
- **Task 2 committed:** 2026-08-07T10:43:31-04:00
- **Tasks:** 2 of 2 complete
- **Files modified:** 4 (1 script, 1 test file, 2 evidence artifacts)

## Accomplishments

- `scripts/smoke_discovery_sample.py`: a standalone CLI reusing `capture_sync_baseline.py`'s evidence-publishing convention via `importlib.util`, exposing `select_sample`, `probe_grep_tools`, `probe_get_tool_info`, `classify_discovery`, and `run_discovery_suite`, all pure except the last.
- A real, unfiltered `ToolUniverse.load_tools()` proved `catalog_size=2658`, and all 11 mechanically-selected sample names (5 preserved-custom from `literature_search_tools.json`, 5 new-upstream re-derived from `union.json`'s git blobs, 1 offline control) are found by `grep_tools` and return a non-empty parameter schema from `get_tool_info` -- `failed==0`.
- `tests/unit/test_smoke_discovery_sample.py`: 11 tests, zero `tooluniverse` imports, zero `ToolUniverse` instantiation, exercising `classify_discovery`'s 6 outcomes and `select_sample`'s gated-exclusion/emptied-pool/determinism behavior against hand-built fixtures and a real `tmp_path` mini git repository.
- **Important caveat carried forward to 03-04:** this run's live `discovery.json` has `gated: []`. Pool 1's flat cap-5 across both hand-resolved files excluded `uspto_tools.json`'s pair (the only gated candidates in the candidate pool, on `USPTO_API_KEY`) because both literature-agent names sort earlier. The gated-exclusion *mechanism* is fully proven -- by `test_select_sample_gated_exclusion_removes_names_without_backfill` and the two gated `classify_discovery` parametrize cases, which exercise the identical code path a live gated name would -- but CAT-02's gated-handling truth is demonstrated by unit fixtures here, not by this run's live probe. See Decisions Made.

## Task Commits

Each task was committed atomically:

1. **Task 1: Discovery smoke suite over a mechanically selected, gated-aware representative sample** - `d8322582` (feat)
2. **Task 2: Unit coverage for the sample-selection and discovery-verdict logic** - `9d5d1b63` (test)

## Files Created/Modified

- `scripts/smoke_discovery_sample.py` - `select_sample`, `probe_grep_tools`, `probe_get_tool_info`, `classify_discovery`, `run_discovery_suite`, `_collect_secrets`, `main`; CLI flags `--out`, `--json`, `--tool`
- `tests/unit/test_smoke_discovery_sample.py` - unit coverage for `classify_discovery` (6 outcomes) and `select_sample` (gated-exclusion, emptied-pool, cap/sort/determinism)
- `.planning/phases/03-follow-up-and-catalog-reconciliation/evidence/staging/discovery/{discovery.json,SHA256SUMS}` - the discovery smoke suite's checksummed evidence bundle

## Decisions Made

See `key-decisions` in the frontmatter above for the five substantive decisions: the pool-1 flat-cap-5 choice and its USPTO consequence, the union.json-name-list gap and its git-show-based resolution, the exact-name-membership divergence from `probe_discovery`, the single-unfiltered-load requirement, and the AgenticTool gating blind spot that was investigated and empirically ruled out for this environment. The first was checked against a second-opinion review before implementation, specifically to guard against T-03-19 (a hand-picked sample fitted to a preferred result) -- the review's discriminator: both a flat cap-5 and a round-robin-across-files cap-5 satisfy every automated acceptance criterion identically (the pool-diversity and `gated`-shape checks hold either way), so when the literal acceptance criteria do not discriminate between two readings, the plan's plain text wins over a reading chosen because it produces a preferred artifact shape.

## Deviations from Plan

### Auto-fixed Issues

**1. [Precondition wording] Tracer fingerprint precondition treated as explained rather than literal**

- **Found during:** Pre-Task-1 precondition check (`git status --porcelain` path set vs. `worktree_fingerprint.json`'s recorded `paths`)
- **Issue:** The live path set (2,662 paths) did not literally match the recorded fingerprint (2,668 paths). Root-caused via explicit set-difference to exactly 6 self-referential paths: plan 03-01's own committed outputs (`tracer/{SHA256SUMS,chain_tracer.json,git.json,worktree_fingerprint.json}`, `scripts/audit_registration_chain.py`, `tests/unit/test_audit_registration_chain.py`), which the fingerprint necessarily captured *before* its own sibling files existed on disk. The forbidden zone (`src/tooluniverse/tools/`, `.tool_metadata.json`, `_lazy_registry_static.py`) was verified byte-identical between the recorded fingerprint and the live tree in both set-difference directions -- zero unexplained additions, zero unexplained removals.
- **Fix:** Per explicit instruction, stopped before Task 1 and reported the mismatch rather than reconciling it. The launching session independently confirmed the identical 6-path delta from its own post-03-01 diff and instructed treating the current 2,662-path set as ground truth for both tasks' preconditions and acceptance criteria, since the literal "matches the fingerprint" wording is stale relative to what actually needs proving (the forbidden zone is unchanged) -- not something to fix in code, since the fingerprint is intentionally a point-in-time artifact from an earlier plan.
- **Files modified:** None (a precondition-interpretation decision, not a code fix). Re-verified after each task: the only new paths beyond the 2,662-path baseline were this plan's own committed outputs, and `git diff --name-only -- .../evidence/staging/tracer/` showed no change from this plan at either checkpoint.
- **Verification:** `git status --porcelain | wc -l` was 2,662 immediately before Task 1, 2,664 after Task 1 (script + evidence dir, both this plan's own), 2,663 after staging Task 2 (test file, also this plan's own) -- see Issues Encountered for the full accounting.
- **Committed in:** N/A (precondition handling; no commit required beyond the tasks' own).

---

**Total deviations:** 1 (a precondition-interpretation clarification, explicitly authorized by the launching session; not a code bug). The `gated: []` live-evidence caveat above is not counted as a deviation -- it is a true, in-spec outcome of the plan's own literal `<sample_selection_rule>` text, disclosed in `discovery.json`'s `exclusions` array exactly as the plan requires ("if removing gated names empties a pool, record that fact explicitly rather than substituting silently" -- here no pool was emptied, but the same disclosure discipline applies to the gated array coming back empty overall).
**Impact on plan:** No code changes were needed to reconcile the precondition; both tasks executed exactly as planned once the precondition's explanation was accepted. No scope creep.

## Issues Encountered

None beyond the precondition-interpretation deviation above. `git status --porcelain | wc -l` accounting across the plan: 2,662 (baseline, confirmed against the coordinator-approved ground truth before any write) -> 2,664 (after Task 1's script + evidence directory were written but before commit) -> 2,662 clean baseline again immediately after Task 1's commit reduced the untracked count by exactly the 2 committed paths -> 2,663 (after Task 2's test file was written) -> 2,662 again after Task 2's commit. At every checkpoint the delta from baseline was exactly this plan's own in-progress or just-committed output, with zero unexplained paths in either direction.

One design question was investigated empirically before implementation rather than assumed from reading the plan text alone: whether `execute_function.py`'s separate `AgenticTool` credential-gating path (which does not populate `_excluded_api_key_tools`) would cause pool 1's literature-agent candidates to misclassify as `fail` instead of `gated` or `pass` in this environment. A live unfiltered `load_tools()` run confirmed all 5 candidates resolve with real schemas -- `.tooluniverse/env.py` resolves LLM keys from `.env.1password` at `ToolUniverse()` construction even though the ambient shell exports none -- so the theoretical risk did not materialize here. Recorded as a decision above rather than an issue, since no code change was required.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 03-04 can regenerate the bundle-wide checksum set over `evidence/staging/discovery/` (and its siblings `tracer/`, `chain/`) unchanged -- this plan's `discovery.json` schema (`catalog_size`, `sample`, `gated`, `emptied_pools`, `results`, `passed`/`gated_count`/`failed`, `exclusions`) is stable and self-describing. Two things 03-04 should carry forward explicitly rather than rediscover:

1. **`gated: []` in this run's live evidence** is a true, documented, in-spec outcome (see Accomplishments and Decisions Made), not a gap in the mechanism -- the mechanism itself is unit-proven. If 03-04 or a later plan wants live evidence of a gated tool specifically, `scripts/smoke_discovery_sample.py --tool USPTO_get_patent_assignment --out <a-different-dir>` demonstrates it directly (do not point `--tool` at the committed `discovery/` directory -- it replaces the full bundle rather than merging into it).
2. **`probe_grep_tools`'s exact-name-membership check** diverges from `scripts/audit_registration_chain.py`'s `probe_discovery` (`bool(matches)`). If 03-04 consolidates or scales either function, reconcile toward the exact-membership version -- it is the correct one, since `find_tools_by_pattern`'s unanchored `re.search` can return non-empty matches for a name that is not itself in the catalog.

No blockers.

---
*Phase: 03-follow-up-and-catalog-reconciliation*
*Completed: 2026-08-07*
