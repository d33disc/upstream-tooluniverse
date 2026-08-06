---
phase: 02-upstream-main-integration
plan: 02
subsystem: infra
tags: [git, merge-audit, re-merge, ast, toml, evidence-bundle, sha256, upstream-sync]

# Dependency graph
requires:
  - phase: 02-upstream-main-integration
    provides: "scripts/audit_upstream_merge.py's run_git import boundary, classify_union()/tool_names()/derive_both_sides_paths()/search_relocated_names()/write_staging_artifact() from plan 02-01, reused unmodified"
provides:
  - "scripts/audit_upstream_merge.py `remerge` subcommand: create_remerge_stage(), resolve_data_json_conflict(), union_default_config_keys(), resolve_pyproject_conflict(), resolve_gitignore_conflict(), resolve_data_config_layer(), classify_unresolved_path()/classify_unresolved_paths()"
  - "A detached, merge-in-progress isolated stage at ${TMPDIR}/tu-remerge-audit-e0755067, data/config layer fully resolved under D-08, source layer left open"
  - "evidence/staging/remerge.json: conflicts_raw (285) vs conflicts_landed (22) recorded side-by-side, unresolved_by_class breakdown for plan 02-03"
affects: [02-03, 02-04, 02-05, 02-06]

# Actuals (#2632)
actuals:
  tokens: 12000
  tasks: 3
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "git merge --no-commit --no-ff run via a thin subprocess wrapper (not run_git) because a merge conflict's exit code 1 is this operation's expected, successful outcome, not a subprocess failure -- run_git's raise-on-nonzero contract would misclassify it"
    - "MERGE_HEAD probed via `git -C <worktree> rev-parse --absolute-git-dir` + join, never `<worktree>/.git/MERGE_HEAD` -- a linked worktree's .git is a file pointing elsewhere, and MERGE_HEAD lives under the shared repo's .git/worktrees/<name>/"
    - "ast.literal_eval applied per-key only (never over the whole dict node) when parsing a hand-maintained Python dict literal whose values are function calls (os.path.join(...)) -- literal_eval on the whole structure would raise on exactly the file it needs to read; values are kept as ast.get_source_segment() text and re-spliced, never evaluated"
    - "TOML conflict resolution as upstream-canonical-plus-fork-additive: split both sides into header-delimited blocks, take upstream's file verbatim, append any table whose header text is absent from upstream -- verified byte-for-byte to match how `f81448f2` itself resolved pyproject.toml's [tool.mypy] block, except this resolver additionally preserves fork's comments those diff-tree --cc pruning made invisible upstream"
    - "conflicts_raw vs conflicts_landed recorded side-by-side, never reconciled: git diff-tree --cc <merge-commit> prunes any path whose final content is TREESAME to one parent, so it undercounts real conflicts whenever the original resolver took one side wholesale -- classify_unresolved_paths() buckets the gap (source_modules/tests/generated/symlink_workspaces/packaging/ci_docs) instead of leaving it undifferentiated"

key-files:
  created: []
  modified:
    - scripts/audit_upstream_merge.py
    - tests/unit/test_audit_upstream_merge.py
    - .planning/phases/02-upstream-main-integration/evidence/staging/remerge.json
    - .planning/phases/02-upstream-main-integration/evidence/staging/SHA256SUMS

key-decisions:
  - "pyproject.toml resolved as upstream-file-plus-fork-only-tables, not upstream wholesale, after measuring that the fork's [tool.mypy] and [[tool.mypy.overrides]] tables are absent from upstream's file but survived in the landed merge f81448f2 -- taking upstream wholesale would have been a Rule-1 data-loss bug the plan's literal 'take upstream's dependency declarations' wording did not anticipate."
  - "The raw re-derived conflict set (conflicts_raw, 285 paths) is recorded verbatim alongside conflicts_landed (22, from git diff-tree --cc f81448f2) without reconciliation, per D-07. The gap is explained: diff-tree --cc prunes any path whose final content is TREESAME to a parent, hiding every conflict the original resolution settled by taking one side wholesale (confirmed identical parents/merge-base to f81448f2 via git log -1 --format=%P and git merge-base)."
  - "unresolved_paths (160, after data/config resolution) is additionally classified via classify_unresolved_paths() into 6 buckets, because the plan's own acceptance criterion ('every entry is a src/tooluniverse/*.py, tests/**, or _lazy_registry_static.py path') does not literally hold against the measured data -- 134 of the 160 entries are outside that pattern (symlink_workspaces 114, packaging 9, ci_docs 11, generated 7). Recorded as an explicit, reviewable classification rather than silently reconciled to fit the plan's wording."
  - "src/tooluniverse/data/*.json conflicts in the real re-merge numbered 121 (119 entry_union + 2 upstream_deleted), not the 2 files (literature_search_tools.json, uspto_tools.json) CONTEXT.md names -- resolve_data_config_layer() was already written generically over conflicts_raw, so no code change was needed to cover the larger scope; only the evidence record and this SUMMARY needed to say so honestly."

patterns-established:
  - "Stage idempotency: _existing_stage()/_describe_existing_stage() detect a stage a prior invocation already created (by HEAD == fork_oid) and skip re-calling create_remerge_stage(), so `remerge` can be re-run to continue rather than only from a fresh stage."
  - "_guard_evidence_not_merge_in_progress() refuses --stage-only from overwriting an existing remerge.json whose handoff_state is already merge_in_progress -- both flags write the same evidence file, and a later --stage-only re-run would otherwise desynchronize the JSON from the stage's real on-disk state without touching the stage itself."

requirements-completed: [SYNC-01, SYNC-02]

coverage:
  - id: D1
    description: "Isolated detached worktree at fork parent e0755067, outside the main checkout, containing none of Phase 1's recorded pre-existing dirty/untracked paths"
    requirement: SYNC-01
    verification:
      - kind: unit
        ref: "tests/unit/test_audit_upstream_merge.py::test_create_remerge_stage_refuses_nested_target, ::test_create_remerge_stage_refuses_non_empty_target, ::test_create_remerge_stage_leaves_repo_untouched, ::test_create_remerge_stage_stage_head_equals_fork_oid, ::test_create_remerge_stage_excludes_preexisting_paths"
        status: pass
      - kind: other
        ref: "python3 scripts/audit_upstream_merge.py remerge --repo . --stage-only --json; jq -e over remerge.json (stage_head, stage_status, repo_head_before==after, excluded_preexisting all absent); git -C <stage> status --porcelain empty"
        status: pass
    human_judgment: false
  - id: D2
    description: "Data/config-layer conflicts (data/*.json entry_union, default_config.py key_union, pyproject.toml upstream_canonical_deps, .gitignore line_union) resolved under recorded D-08 rules; _lazy_registry_static.py cleared without hand-resolution"
    requirement: SYNC-02
    verification:
      - kind: unit
        ref: "tests/unit/test_audit_upstream_merge.py::test_resolve_data_json_conflict_prefers_upstream_on_shared_name, ::test_resolve_data_json_conflict_byte_identical_regardless_of_array_order, ::test_resolve_data_json_conflict_raises_on_non_list_side, ::test_resolve_data_json_conflict_upstream_deletion_records_relocation, ::test_union_default_config_keys_returns_key_union, ::test_union_default_config_keys_shared_key_takes_upstream_value_and_records_collision, ::test_union_default_config_keys_rejects_non_dict_literal_assignment, ::test_union_default_config_keys_handles_call_node_values"
        status: pass
      - kind: other
        ref: "python3 scripts/audit_upstream_merge.py remerge --repo . --layer data-config --json; jq -e over remerge.json (handoff_state, conflicts_raw>0, every resolution has rule/decision/rationale, all entry_union verdicts union_ok, default_config.key_union_ok); git -C <stage> diff --name-only --diff-filter=U over data/config paths empty"
        status: pass
    human_judgment: false
  - id: D3
    description: "Stage left in a documented merge-in-progress handoff state, never committed, never aborted; source layer (160 paths, classified) open for plan 02-03"
    verification:
      - kind: other
        ref: "git -C <stage> rev-parse MERGE_HEAD succeeds; git -C <stage> rev-parse HEAD still equals e0755067; jq -r '.handoff_state' remerge.json == merge_in_progress"
        status: pass
    human_judgment: false

duration: 62min
completed: 2026-08-06
status: complete
---

# Phase 2 Plan 2: Isolated Re-Merge Stage + Data/Config Conflict Resolution Summary

**Built a detached, merge-in-progress `e0755067` + `56adcfd9` re-merge stage outside the main checkout, resolved all 121 conflicted `data/*.json` files plus `default_config.py`/`pyproject.toml`/`.gitignore` under D-08, and discovered the raw conflict set is 285 paths -- 13x the 22 `git diff-tree --cc` reports for the landed merge.**

## Performance

- **Duration:** ~62 min
- **Started:** 2026-08-06T16:00:00Z (approx)
- **Completed:** 2026-08-06T17:02:00Z
- **Tasks:** 3
- **Files modified:** 4 (script, test, remerge.json, SHA256SUMS)

## Accomplishments

- `create_remerge_stage()` builds an isolated detached worktree at `e0755067` by calling `create_isolated_worktree()` from `scripts/capture_sync_baseline.py` unmodified -- its nesting and non-empty-target guards make SYNC-01's isolation mechanical. Verified live: stage lands at `${TMPDIR}/tu-remerge-audit-e0755067`, `stage_head` equals the full `e0755067` OID, `stage_status` is empty, and all 7 of Phase 1's recorded pre-existing dirty/untracked paths are absent from it.
- `git merge --no-commit --no-ff 56adcfd9` run inside the stage via a thin subprocess wrapper (a conflict's exit code 1 is expected success, not a `run_git`-raisable failure). `conflicts_raw` (285 paths, git's real re-derived conflict set) is recorded verbatim alongside `conflicts_landed` (22, from `git diff-tree --cc f81448f2`) without reconciliation, per D-07.
- **Major finding:** the 285-vs-22 gap is not noise. `git diff-tree --cc` prunes any path whose final content is TREESAME to one parent -- it hides every conflict the original merge resolved by taking one side wholesale. This is confirmed structurally (same parents, same merge-base as `f81448f2`, verified via `git log -1 --format=%P` and `git merge-base`), not a re-run artifact. `classify_unresolved_paths()` buckets the still-open 160 paths (after data/config resolution) into `source_modules` (16), `tests` (3), `generated` (7 -- `src/tooluniverse/tools/*.py` per-tool wrapper stubs, `AA` add/add conflicts from independent regeneration on both sides), `symlink_workspaces` (114 -- `plugin/skills/*~HEAD`, git's materialized symlink-conflict artifacts), `packaging` (9 -- `uv.lock`, `plugin/**`), and `ci_docs` (11 -- `.github/**`, `docs/**`, `skills/**`).
- `resolve_data_json_conflict()` resolved **121** `data/*.json` conflicts (119 `entry_union`, all `union_ok`; 2 `upstream_deleted` -- `pathway_commons_tools.json`/`soilgrids_tools.json`, both relocated under `broken_apis/`, matching plan 02-01's earlier finding). The plan's own read_first materials named only 2 conflicted JSON files; the resolver was already written generically over `conflicts_raw`, so it correctly handled the larger real scope with no code change.
- `union_default_config_keys()` resolved `default_config.py`: 532 fork keys, 618 upstream keys, 524 shared, 626 merged (`fork_keys | upstream_keys`, verified `key_union_ok: true`), zero value collisions. Keys parsed via per-key `ast.literal_eval`; values (all `os.path.join(...)` calls) kept as source text via `ast.get_source_segment()` and re-spliced, never evaluated -- `ast.literal_eval` on the whole dict node would raise on this exact file.
- `resolve_pyproject_conflict()` resolved `pyproject.toml` as upstream-file-plus-fork-only-tables. **Secondary finding:** this preserved two fork comments (`# Default: lenient...`, `# Strict overrides...`) inside `[tool.mypy]` that the landed merge `f81448f2` dropped -- confirmed by diffing this resolution against `git show f81448f2:pyproject.toml`. Recorded as an observation only; no corrective action taken (D-06a requires re-validation against the pinned tree before any fix, which is plan 02-04's job).
- `resolve_gitignore_conflict()` unioned 32 upstream-only lines onto fork's, fork order first, to keep the fork's negation pattern (`!IMPLEMENTATION_PLAN.md`) semantically safe.
- `_lazy_registry_static.py`'s conflict cleared with fork content as a placeholder, marked `deferred_to_regeneration` -- never hand-resolved.
- Stage left in a documented `merge_in_progress` handoff state: `MERGE_HEAD` present (probed via `git -C <stage> rev-parse --absolute-git-dir` + join, since a linked worktree's `.git` is a file, not `<stage>/.git/MERGE_HEAD`), `HEAD` still at `e0755067`, never committed, never aborted.
- 27 new unit tests (47 total, up from 20), all passing. `test_registry_integrity.py` and `test_sync_baseline_git.py` remain green (11 tests). Full `tests/unit/` suite run in background: exit code 0.

## Task Commits

1. **Task 1 + Task 2 (combined): remerge stage creation + data/config conflict resolvers** - `f15922f4` (feat)
2. **Task 3 (folded into commit 1): unit coverage for resolvers** - tests landed in the same commit as the implementation (see Deviations)
3. **Evidence publication: remerge.json + SHA256SUMS** - `4ada59f5` (docs)

## Files Created/Modified

- `scripts/audit_upstream_merge.py` - `create_remerge_stage`, `default_stage_path`, `_check_excluded_preexisting`, `_existing_stage`, `_describe_existing_stage`, `read_text_at`, `_merge_in_progress`, `_start_or_continue_merge`, `resolve_data_json_conflict`, `_parse_default_tool_files`, `union_default_config_keys`, `render_default_config_source`, `_toml_blocks`, `resolve_pyproject_conflict`, `resolve_gitignore_conflict`, `resolve_data_config_layer`, `classify_unresolved_path`, `classify_unresolved_paths`, `_guard_evidence_not_merge_in_progress`, `_run_remerge`; `remerge` subcommand with `--stage-only`, `--layer data-config`, `--worktree` flags
- `tests/unit/test_audit_upstream_merge.py` - 27 new tests: 5 for `create_remerge_stage`'s isolation/containment behavior, 4 for `resolve_data_json_conflict` (shared-name preference, order-insensitive byte-identity, non-list rejection, upstream-deletion relocation), 4 for `union_default_config_keys` (key union, value-collision-takes-upstream, non-dict-literal rejection, `os.path.join(...)` call-node values), 14 parametrized for `classify_unresolved_path`'s six buckets
- `.planning/phases/02-upstream-main-integration/evidence/staging/remerge.json` - the live run's provenance, conflicts_raw/conflicts_landed, all 125 resolutions, default_config summary, unresolved_paths + unresolved_by_class
- `.planning/phases/02-upstream-main-integration/evidence/staging/SHA256SUMS` - regenerated, verified with `shasum -a 256 -c`

## Decisions Made

See `key-decisions` in frontmatter. Summary: (1) `pyproject.toml` resolved as upstream-plus-fork-additive-tables rather than upstream-wholesale, after measuring that wholesale replacement would have dropped a fork-only `[tool.mypy]` table; (2) `conflicts_raw` (285) recorded verbatim alongside `conflicts_landed` (22) without reconciliation, with the gap explained rather than hidden; (3) `unresolved_paths` classified into 6 buckets because the plan's literal acceptance-criterion pattern does not hold against the measured 160-path reality; (4) the `data/*.json` resolver's already-generic design correctly covered 121 real conflicts against the plan's anticipated 2, with no code change required.

## Deviations from Plan

### Auto-fixed / Clarified Issues

**1. [Rule 1 - Bug avoidance] `pyproject.toml` resolved as upstream-plus-fork-additive-tables, not upstream wholesale**
- **Found during:** Task 2, before writing `resolve_pyproject_conflict`
- **Issue:** The plan's action text says "Take upstream's dependency declarations" for `pyproject.toml`, which read as license to take upstream's file wholesale. Measured (`git show f81448f2:pyproject.toml | grep -n tool.mypy`) that the fork's `[tool.mypy]`/`[[tool.mypy.overrides]]` tables are absent from upstream's file but survived verbatim in the landed merge `f81448f2` -- a wholesale upstream copy would have been a genuine, self-inflicted data-loss bug of exactly the kind this phase audits for.
- **Fix:** `resolve_pyproject_conflict()` splits both sides into TOML-header-delimited blocks, takes upstream's file verbatim (including `[project]` `dependencies`/`optional-dependencies`), and appends any table whose header text is absent from upstream, in fork's original order.
- **Files modified:** `scripts/audit_upstream_merge.py`
- **Verification:** Diffed the resolver's output against `git show f81448f2:pyproject.toml` directly -- structurally identical except the resolver additionally preserves two fork comments the landed merge dropped (see Issues Encountered).
- **Committed in:** `f15922f4`

**2. [Rule 2 - Missing critical evidence structure] `unresolved_by_class` bucketing added**
- **Found during:** Task 2, after the first live `--layer data-config` run measured 160 remaining unresolved paths, not the ~16 the plan's acceptance criteria anticipated
- **Issue:** The plan's Task 2 acceptance criteria state "every entry [of `unresolved_paths`] is a `src/tooluniverse/*.py`, `tests/**`, or `_lazy_registry_static.py` path." Measured against the real re-merge, 134 of 160 unresolved paths fall outside that pattern (symlink workspace conflicts, generated per-tool wrapper stubs, `uv.lock`, CI/docs files). Leaving `unresolved_paths` as an undifferentiated 160-item list would silently violate the criterion's stated intent without making the mismatch reviewable.
- **Fix:** Added `classify_unresolved_path()`/`classify_unresolved_paths()`, bucketing every unresolved path into `source_modules`/`tests`/`generated`/`symlink_workspaces`/`packaging`/`ci_docs`, recorded in `remerge.json` under `unresolved_by_class` alongside the flat `unresolved_paths` list (which still satisfies the criterion's "length > 0" half).
- **Files modified:** `scripts/audit_upstream_merge.py`
- **Verification:** 14 parametrized unit tests over the classifier; zero paths in the real run fell into the `other` catch-all bucket.
- **Committed in:** `f15922f4`

**3. [Process, not a rule-governed fix] Tasks 1, 2, and 3 landed as a single implementation commit, not three**
- **Reason:** Task 2's resolvers directly extend Task 1's stage-creation helpers in the same module and were designed, implemented, and verified together as one coherent unit before either was independently committable in a working state (Task 2's `--layer data-config` CLI path requires Task 1's stage-detection/creation plumbing to exist). Task 3 is unit coverage for Task 2's resolvers, authored in the same pass as the resolvers themselves. Splitting the diff after the fact via partial-hunk staging would have been artificial -- it would not have produced a Task 1 commit that builds and passes tests independently of Task 2's code already being present in the file. The two commits that did land (`f15922f4` for code+tests, `4ada59f5` for evidence) are each independently reviewable and revertible as units; the loss is per-task commit granularity within `f15922f4`, not code correctness or test coverage.
- **Verification:** Both Task 1's and Task 2's `<verify>` blocks were run to green independently against the live repository (see Task Commits and the `coverage` block above) before either commit was made.

---

**Total deviations:** 2 auto-fixed under Rules 1/2, plus 1 process deviation (commit granularity) documented for transparency.
**Impact on plan:** No scope creep. Both auto-fixes are corrections that keep the plan's own stated intent (fork-additive resolution; an honestly-scoped source-layer handoff) intact against what the plan's prose slightly underspecified. The commit-granularity deviation reduces reviewability slightly but not correctness -- every task's `<verify>` block was independently run to green.

## Issues Encountered

- **`git diff-tree --cc f81448f2 --name-only` undercounts real conflicts by 13x (285 vs 22).** Root cause: combined-diff pruning skips any path whose final content is TREESAME to a parent, which happens whenever a conflict was resolved by taking one side wholesale rather than blending content. This is a finding about the *audit method* itself (D-07's own stated purpose), not a defect in this plan's re-merge. Flagged prominently for plan 02-04, which owns the comparison/findings work: any future phase relying on `diff-tree --cc` to enumerate conflicts will undercount the same way.
- **`pyproject.toml`'s landed resolution (`f81448f2`) dropped two fork comments** inside the `[tool.mypy]` block that this plan's independently re-derived resolution preserves. Recorded as an observation, no corrective action taken here -- D-06a requires re-validation against the pinned tree (`21945440`) before any finding earns a fix, and that comparison is plan 02-04's job, not this plan's.
- **Stale evidence file from an earlier exploratory run required a manual reset.** Before committing, an earlier interactive `--layer data-config` invocation (run to validate the resolver design against real data) had already partially resolved the stage and wrote a `merge_in_progress` `remerge.json`. The stage worktree was removed (`git worktree remove --force`, reversible per this plan's own `<reversibility>` contract -- nothing was ever committed or merged) and a fresh stage was built for the final, official run whose evidence is what's committed. This also exercised `_guard_evidence_not_merge_in_progress()` in practice, confirming it correctly refuses to let a stale `--stage-only` re-run clobber a merge-in-progress evidence record.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Stage handoff for plan 02-03:** `${TMPDIR}/tu-remerge-audit-e0755067` is a live, merge-in-progress detached worktree. `HEAD` is `e0755067`, `MERGE_HEAD` is `56adcfd9`, data/config layer resolved and staged, 160 source-layer paths (classified in `remerge.json`'s `unresolved_by_class`) still conflicted. Never abort, never commit -- plan 02-03 owns both.
- **Scope correction for plan 02-03:** the plan's own text scoped 02-03 to "11 conflicted Python adapter/core modules and 5 conflicted test files" (16 total). The measured reality is `source_modules` (16) + `tests` (3) = 19 files matching that description, **plus** `generated` (7, `src/tooluniverse/tools/*.py` -- almost certainly resolvable the same way as `_lazy_registry_static.py`, i.e. regenerate via `tu build` rather than hand-merge), `symlink_workspaces` (114, git-materialized `~HEAD` conflict artifacts on `plugin/skills/*` symlinks -- this plan's prohibitions already forbid traversing/writing through those symlinks), `packaging` (9, `uv.lock`/`plugin/**`), and `ci_docs` (11, `.github/**`/`docs/**`/`skills/**`). Plan 02-03 (or whoever plans it) should read `remerge.json`'s `unresolved_by_class` before assuming a 16-file scope.
- **`resolve_data_config_layer()` is idempotent-safe to re-run** against the same stage (via `_existing_stage()`/`_merge_in_progress()` detection) if 02-03 needs to re-invoke `remerge --layer data-config` for any reason, though it should be a no-op given the layer is already fully resolved and staged.
- No blockers. `.planning/config.json` and `ralph-specs/fleet/results/` remain untouched and untracked throughout.

---
*Phase: 02-upstream-main-integration*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: scripts/audit_upstream_merge.py
- FOUND: tests/unit/test_audit_upstream_merge.py
- FOUND: .planning/phases/02-upstream-main-integration/evidence/staging/remerge.json
- FOUND: .planning/phases/02-upstream-main-integration/evidence/staging/SHA256SUMS
- FOUND: .planning/phases/02-upstream-main-integration/02-02-SUMMARY.md
- FOUND commit: f15922f4
- FOUND commit: 4ada59f5
