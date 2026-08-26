---
phase: 02-upstream-main-integration
plan: 03
subsystem: infra
tags: [git, merge-audit, re-merge, ast, definition-level-resolution, sha256, upstream-sync]

# Dependency graph
requires:
  - phase: 02-upstream-main-integration
    provides: "scripts/audit_upstream_merge.py's remerge --layer data-config resolvers and the merge-in-progress stage at ${TMPDIR}/tu-remerge-audit-e0755067 that plan 02-02 left behind (MERGE_HEAD present, data/config layer resolved, source layer open)"
provides:
  - "scripts/audit_upstream_merge.py: extract_definition_names(), resolve_source_module_conflict(), resolve_source_layer(), resolve_generated_conflict(), REMERGE_REF; remerge --layer source dispatch"
  - "A committed, pinned re-merge stage at refs/audit/remerge (two parents: e0755067 fork, 56adcfd9 upstream), never merged into any branch, with a regenerated _lazy_registry_static.py and a green tests/unit/test_registry_integrity.py inside the stage's own fresh .venv"
  - "evidence/staging/remerge.json: full resolutions array (151), deviation_out_of_scope_resolutions, discovered_findings (2), lazy_registry delta, registry_integrity result -- the complete re-derived-merge evidence bundle for plan 02-04"
affects: [02-04, 02-05, 02-06]

# Actuals (#2632)
actuals:
  tokens: 82000
  tasks: 3
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Definition-level D-08 resolution built on ast.parse indexing (top-level + one-level-deep class-member), not hunk-by-hunk text merging: base is upstream's file verbatim, fork-only module-level definitions appended at file end, fork-only class-level members spliced onto the end of the corresponding shared class body (never a whole-class replace) -- verified byte-parseable and definition-name-set-exact against all 16 real source-module conflicts and 3 real test-file conflicts, zero fork_only_dropped."
    - "remerge --layer source resumes from the *persisted* unresolved_by_class in remerge.json, not a live `git diff --diff-filter=U` re-derivation -- by the time this CLI path runs, some paths may already be resolved and staged (no longer `U`), which would make a live re-derivation see nothing left to do on a second invocation. resolve_source_module_conflict reads fork_oid/upstream_oid content directly (never the working tree), so re-running it against an already-resolved path is idempotent and safe."
    - "git pathspec `*` crosses `/` without `:(glob)` magic: Task 1's own `src/tooluniverse/*.py` gate silently includes `src/tooluniverse/tools/*.py` (the generated per-tool wrapper stubs), discovered by running the plan's literal verify command before assuming the 16-file source_modules bucket was the whole gate."
    - "A path that never appears in `git diff --diff-filter=U` is not proof the auto-merge got it right: llm_clients.py cleanly auto-merged with zero conflict markers yet silently dropped upstream's entire AzureOpenAIClient class. Confirmed only by checking whether resolve_source_module_conflict's own fork/upstream/merged definition-set accounting held for every source file the resolved tree imports from, not just the ones git flagged."
    - "git blame on the CURRENT pinned tree is a legitimate way to check whether a test-file fix pre-dates or post-dates the historical merge commit -- attributes content to f81448f2 itself vs. a later repair commit, which is exactly the D-06a self-healed-downstream distinction the phase needs."

key-files:
  created: []
  modified:
    - scripts/audit_upstream_merge.py
    - tests/unit/test_audit_upstream_merge.py
    - .planning/phases/02-upstream-main-integration/evidence/staging/remerge.json
    - .planning/phases/02-upstream-main-integration/evidence/staging/SHA256SUMS
    - (inside the throwaway stage only, never the main checkout) src/tooluniverse/llm_clients.py, src/tooluniverse/_lazy_registry_static.py, tests/unit/test_registry_integrity.py, 16 source modules, 3 test files, 7 generated tool stubs, and 141 out-of-declared-scope paths (symlink_workspaces/packaging/ci_docs)

key-decisions:
  - "Resolved 16 source_modules + 3 tests (19 files), not the plan's literally-named 11 modules + 5 tests (16 files). The plan's list came from CONTEXT.md's `git diff-tree --cc f81448f2` output, which 02-02-SUMMARY already proved undercounts real conflicts 13x (combined-diff pruning hides any path resolved by taking one side wholesale). The measured live conflict set (`git -C <stage> diff --name-only --diff-filter=U`, cross-checked against remerge.json's persisted unresolved_by_class) is ground truth; Task 1's own acceptance criterion ('no unmerged tooluniverse/*.py files') is only satisfiable by resolving all 16, and 02-02-SUMMARY's own 'Next Phase Readiness' section had already flagged this exact correction for this plan to apply."
  - "Resolved 7 additional 'generated' paths (src/tooluniverse/tools/*.py per-tool wrapper stubs) inside Task 1, not deferred entirely to Task 3, because git's pathspec `*` crosses `/` without `:(glob)` magic -- Task 1's own literal verify command (`diff --name-only --diff-filter=U -- 'src/tooluniverse/*.py' ':!...'`) includes them, so they had to be conflict-free before Task 1's gate could pass. Given the same deferred_to_regeneration treatment as _lazy_registry_static.py (fork content as placeholder, true content from Task 3's generate_tools.main() run), not the D-08 definition-level algorithm."
  - "Resolved 141 further out-of-plan-declared-scope conflicts (symlink_workspaces 114, packaging 9, ci_docs 11) under explicit, uniform, recorded mechanical rules distinct from Task 1/2's D-08 resolutions array, because git refuses `git commit` while ANY path in the working tree is unmerged -- Task 2's own acceptance criterion ('git status --porcelain produces no output') is mechanically unreachable otherwise, regardless of the predecessor state's framing of those classes as out of scope. symlink_workspaces: git had already auto-resolved every path at the D+A level (materializing upstream's directory), leaving only the fork's `~HEAD` symlink-object marker unmerged; `git rm` on the marker accepts git's own already-staged resolution without opening, reading, or writing through any plugin/skills/* symlink -- honoring the hard prohibition's literal text. packaging/ci_docs: D-08's literal wording ('a definition present on both sides, upstream's version wins outright') applied at whole-file granularity, treating the path itself as the shared 'definition' identity for content that is not AST-decomposable. Recorded under a separate deviation_out_of_scope_resolutions key so it never pollutes Task 1/2's own resolution counts, and explicitly disclaimed: this is a review instrument (D-06), re-validated against the pinned tree before any corrective commit (D-06a) -- these 141 resolutions carry no independent SYNC-02/PRES-02 authority on their own."
  - "Fixed llm_clients.py despite it never appearing in conflicts_raw at all. git's own 3-way auto-merge silently dropped upstream's entire AzureOpenAIClient class with zero conflict markers -- discovered only because Task 3's generate_tools.main() run failed on the resulting ImportError from agentic_tool.py (resolved to upstream's canonical body in Task 1, which imports AzureOpenAIClient). Applied resolve_source_module_conflict() directly to this file despite the absent conflict flag; recorded as discovered finding F-02-03-01 (high severity), carried to 02-04 as a landed_dropped_or_altered / T-02-07 candidate."
  - "Patched tests/unit/test_registry_integrity.py with a 2-line api_keys_catalog.json scan-exclusion neither fork@e0755067 nor upstream@56adcfd9 had pre-merge (verified via git show on both OIDs), sourced byte-identical from the current pinned tree. git blame attributes the exclusion in the pinned tree to f81448f2 itself -- original content the human resolver authored during the historical merge's own conflict resolution, not derivable from either input side under D-08. Recorded as discovered finding F-02-03-02 (medium severity); this is squarely D-06a self-healed-downstream territory, applied here only so Task 3's hard gate measures the real registration chain rather than a known, already-fixed test-scope gap."
  - "ruff format applied only to files where the splice itself needed it (agentic_tool.py: missing blank line between two spliced methods) or where I introduced new code (scripts/audit_upstream_merge.py, tests/unit/test_audit_upstream_merge.py in the main checkout). Did NOT run ruff format/check --fix broadly across all 19 resolved source-layer files: measured that tool_finder_embedding.py's ruff-format-check failures and every file's ruff-check import-sort/typing-modernization findings are 100% pre-existing in upstream's own file (verified against git show <upstream_oid>:<path> directly), unrelated to this plan's resolution work, and out of scope per CLAUDE.md's explicit scope-boundary rule -- reformatting them would inject unrelated churn into plan 02-04's full-tree diff against f81448f2."

patterns-established:
  - "resolve_source_module_conflict()'s two-pass algorithm (module-level append + class-level splice into a shared class, both anchored to upstream's line numbers, classes processed in descending end_lineno order so earlier insertion points stay valid) generalizes cleanly to any Python module or test file -- no rule change was needed between production modules (16) and test files (3), only the vocabulary of what counts as a \"definition\" (functions/classes vs. test functions/fixtures)."
  - "resolve_generated_conflict() is now the second file to use the deferred_to_regeneration pattern (after _lazy_registry_static.py in plan 02-02) -- any future GENERATED-file conflict in this audit should reach for this same helper rather than reintroducing hand-resolution."

requirements-completed: [SYNC-02, PRES-02]

coverage:
  - id: D1
    description: "All 16 real source-module conflicts and 3 real test-file conflicts resolved definition-by-definition under D-08's upstream_canonical_fork_additive rule; every file parses; zero fork_only_dropped"
    requirement: SYNC-02
    verification:
      - kind: unit
        ref: "tests/unit/test_audit_upstream_merge.py::test_extract_definition_names_includes_module_and_class_level, ::test_resolve_source_module_conflict_shared_def_takes_upstream_body, ::test_resolve_source_module_conflict_fork_only_module_level_retained, ::test_resolve_source_module_conflict_fork_only_class_member_spliced, ::test_resolve_source_module_conflict_stages_the_file, ::test_resolve_generated_conflict_stages_fork_content_as_placeholder"
        status: pass
      - kind: other
        ref: "python3 scripts/audit_upstream_merge.py remerge --repo . --layer source --json; jq -e over remerge.json (19 upstream_canonical_fork_additive resolutions, all fork_only_dropped empty, all resolved_name_set_matches_expected true); git -C <stage> diff --name-only --diff-filter=U -- 'src/tooluniverse/*.py' ':!src/tooluniverse/_lazy_registry_static.py' empty"
        status: pass
    human_judgment: false
  - id: D2
    description: "Stage committed with the same two parents as f81448f2, pinned at refs/audit/remerge outside refs/heads/, contained by no branch"
    verification:
      - kind: other
        ref: "git -C <stage> status --porcelain empty; git rev-list --parents -n 1 refs/audit/remerge == a4d3d95a e0755067 56adcfd9; git branch --contains refs/audit/remerge empty"
        status: pass
    human_judgment: false
  - id: D3
    description: "_lazy_registry_static.py and every src/tooluniverse/tools/*.py wrapper regenerated inside the stage's own fresh uv-synced environment, strictly after every source conflict settled; full key-set delta recorded, not gated on"
    requirement: PRES-02
    verification:
      - kind: other
        ref: "uv sync inside stage succeeded; generate_lazy_registry.main() + generate_tools.main(output_dir=None) run from stage's .venv; lazy_registry delta recorded (713 regenerated, 712 landed, 0 missing_vs_landed, 1 added_vs_landed, 0 module_target_diffs)"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/unit/test_registry_integrity.py green inside the stage's own fresh environment -- hard gate"
    requirement: PRES-02
    verification:
      - kind: other
        ref: "<stage>/.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -q --no-cov: 4 passed, exit 0"
        status: pass
    human_judgment: false

duration: 3h40min
completed: 2026-08-06
status: complete
---

# Phase 2 Plan 3: Source-Layer Conflict Resolution + Registry Regeneration Summary

**Resolved all 19 real (not 16 plan-named) source/test-layer conflicts under D-08's definition-level rule, committed and pinned the re-merge stage, then discovered and fixed two genuine merge-correctness bugs -- a silent git auto-merge data loss in `llm_clients.py` and a test-scope gap -- before regenerating the lazy registry and every tool wrapper stub to a green `test_registry_integrity.py`.**

## Performance

- **Duration:** ~3h40min
- **Started:** 2026-08-06T16:50:00Z (approx, resuming plan 02-02's handoff)
- **Completed:** 2026-08-06T20:30:00Z (approx)
- **Tasks:** 3
- **Files modified (main checkout):** 4 (script, test, remerge.json, SHA256SUMS)
- **Files touched (inside the throwaway stage only):** ~2,630 (19 D-08-resolved + 7 generated stubs + 141 out-of-scope mechanical resolutions + 2 discovered-finding fixes + ~2,602 regenerated tool wrapper files)

## Accomplishments

- **Task 1's real scope was 16 files, not 11.** CONTEXT.md's `git diff-tree --cc f81448f2` list (the plan's literal source for its 11 named modules) undercounts real conflicts the same way 02-02-SUMMARY already proved for the whole merge (13x, 285 vs 22). Verified the ground truth directly against the live stage (`git -C <stage> diff --name-only --diff-filter=U`) and cross-checked it matched remerge.json's persisted `unresolved_by_class.source_modules` exactly: `agentic_tool.py`, `cli.py`, `compound_gene_disease_tool.py`, `compound_variant_tool.py`, `ctd_tool.py`, `gtex_v2_tool.py`, `gwas_tool.py`, `msigdb_tool.py`, `package_tool.py`, `reactome_content_tool.py`, `sabdab_tool.py`, `semantic_scholar_tool.py`, `therasabdab_tool.py`, `tool_finder_embedding.py`, `unified_guideline_tools.py`, `uniprot_tool.py`. Only 6 of these overlap the plan's named 11; `base_tool.py`, `brenda_tool.py`, `llm_clients.py`, `smcp.py`, `tool_discovery_tools.py` were never conflicted at all in the re-derived merge.
- **Task 2's real test scope was 3 files, not 5.** `tests/integration/test_tool_integration.py`, `tests/test_claude_code_plugin.py`, `tests/unit/test_agentic_tool_env_vars.py` -- only the first overlaps the plan's named 5. `tests/unit/test_registry_integrity.py` (the plan's own emphasized "simultaneously a merge input and the acceptance gate" file) was **not conflicted at all**: it merged cleanly with zero markers, needing no D-08 resolution -- stronger than a resolved-with-zero-fork-only-entries outcome, since git's own three-way merge found no divergence to reconcile between fork's and upstream's versions.
- Built `extract_definition_names()` / `_index_module()` (AST indexing, top-level + one-level-deep class members) and `resolve_source_module_conflict()` (D-08's definition-level rule: base is upstream's file verbatim, fork-only module-level definitions appended at file end, fork-only class-level members spliced onto the end of the corresponding shared class body). Surveyed all 16 real module conflicts before implementing: every fork-only definition was either module-level or a member of a class present on **both** sides -- no whole-fork-only-class case existed, simplifying the splice logic to two passes with no recursive class handling needed.
- Ran the resolver against all 19 real files: zero `fork_only_dropped`, every resolved file's definition-name set exactly matches `fork_only_retained | shared_taken_from_upstream | upstream_only_added`, every file parses with `ast.parse`.
- **Task 1's own literal verify command surfaced a fifth undercounted class.** `git diff --name-only --diff-filter=U -- 'src/tooluniverse/*.py' ':!src/tooluniverse/_lazy_registry_static.py'` still returned 7 files after resolving the 16 source_modules -- git's pathspec `*` crosses `/` without `:(glob)` magic, so the gate also covers `src/tooluniverse/tools/*.py` (the classified-separately "generated" bucket). Built `resolve_generated_conflict()`, the same `deferred_to_regeneration` treatment as `_lazy_registry_static.py`, and cleared all 7.
- **141 further out-of-declared-scope conflicts blocked Task 2's commit mechanically, not just by task-boundary framing.** Git refuses `git commit` while any path is unmerged, and `symlink_workspaces` (114), `packaging` (9), and `ci_docs` (11) were still conflicted. Resolved under explicit, uniform, recorded mechanical rules kept structurally separate from the D-08 `resolutions` array (see `deviation_out_of_scope_resolutions` in `remerge.json`): symlinks via index-only `git rm` of the fork's `~HEAD` marker (git had already auto-resolved the real path with `D`+`A`, materializing upstream's directory -- confirmed via `git status --porcelain -- 'plugin/skills/'` showing 528 `A` / 114 `D` before this plan touched anything, so no symlink was opened, read, or written through); packaging/ci_docs via D-08's literal wording applied at whole-file granularity (upstream wins for the 19 present-on-both-sides files; the one upstream-only file, `skills/tooluniverse/REFERENCE.md`, restored from upstream since fork had no content to lose there).
- Committed the stage (`git -C <stage> commit --no-edit`): two parents `e0755067`/`56adcfd9`, matching `f81448f2`'s parentage. Pinned at `refs/audit/remerge`; `git branch --contains` empty throughout.
- **Discovered and fixed two genuine bugs before Task 3's regeneration could succeed**, both recorded as `discovered_findings` in `remerge.json` (not silently absorbed):
  - **F-02-03-01 (high):** `llm_clients.py` was never in `conflicts_raw` at all -- git's own clean 3-way auto-merge (during plan 02-02's `git merge --no-commit`) silently dropped upstream's entire `AzureOpenAIClient` class (49 lines), with zero conflict markers to flag it. Surfaced only when `generate_tools.main()` raised `ImportError: cannot import name 'AzureOpenAIClient'` from `agentic_tool.py` (resolved to upstream's canonical body in Task 1, which imports it). Fixed by applying `resolve_source_module_conflict()` directly to this file despite the absent conflict flag -- confirmed both fork and upstream's pre-merge class lists, confirmed the auto-merged result was missing exactly the upstream-only class. This is a genuine git auto-merge data-loss bug, not a mistake in either side's source or in this plan's own resolution work, and is exactly the class of finding this phase exists to catch (T-02-07).
  - **F-02-03-02 (medium):** Task 3's hard gate initially failed -- `test_json_type_fields_exist_in_lazy_registry` found 3 unknown `type` values (`api_key`, `endpoint`, `secret`) sourced from `api_keys_catalog.json` (a credential-metadata catalog the test's unconditional `data/*.json` scan wasn't meant to include). Verified neither fork@e0755067 nor upstream@56adcfd9's pre-merge test file has the exclusion; `git blame` on the current pinned tree attributes the 2-line guard to `f81448f2` itself -- original content the human resolver authored during the historical merge's own conflict resolution, outside what D-08's definition-level rule can mechanically derive. Applied the identical fix, byte-for-byte from the pinned tree; squarely D-06a self-healed-downstream territory.
- Fresh `uv sync` inside the stage (never the main checkout's `.venv`, per OQ2). Regenerated `_lazy_registry_static.py` via `generate_lazy_registry.main()` and all tool wrapper stubs via `generate_tools.main(output_dir=None)` (2,602 files -- every wrapper, not just the 7 that were conflicted, since the fresh worktree has no prior `.tool_metadata.json` to diff against; flagged in `remerge.json` so plan 02-04 treats `src/tooluniverse/tools/*.py` as generated, not individually diffable, matching `_lazy_registry_static.py`'s own treatment).
- Full-tree sanity check beyond the plan's own gate: `import tooluniverse; ToolUniverse().load_tools()` succeeds inside the stage (2,601 tools loaded), and `ast.parse` over every `.py` file under `src/tooluniverse/` returns zero syntax errors.
- `lazy_registry` delta: 713 regenerated keys vs. 712 landed (`f81448f2`), 0 `missing_vs_landed`, 1 `added_vs_landed` (`CTDBackendUnavailable`, a new exception class AST-discovered in the resolved `ctd_tool.py`), 0 `module_target_diffs` -- a clean result.
- `tests/unit/test_registry_integrity.py`: 4 passed, exit 0 -- hard gate satisfied.
- Amended the stage commit (`git -C <stage> add -A && commit --amend --no-edit`) to include the regenerated tree; re-pointed `refs/audit/remerge` to the amended OID `a4d3d95a096a14ce4d147faa20334d24f8db9f9a`; `handoff_state` set to `merged_complete`.
- 6 new unit tests for the source-layer resolver (53 total in `test_audit_upstream_merge.py`, up from 47), all passing; full `tests/unit/test_audit_upstream_merge.py` suite green.

## Task Commits

Main checkout (`docs/gsd-codebase-map`):

1. **Tasks 1-2 (script + tests): source-layer resolver, generated-stub resolver, `--layer source` CLI dispatch** - `7627c785` (feat)
2. **Tasks 1-3 (evidence): remerge.json + SHA256SUMS -- full resolutions, deviations, findings, lazy_registry delta, registry_integrity result** - `8be4f83c` (docs)

Inside the stage (never merged, never pushed, not on any branch):

3. **Re-derived merge commit, amended with the regenerated registry** - `a4d3d95a096a14ce4d147faa20334d24f8db9f9a` (pinned at `refs/audit/remerge`; original pre-regeneration commit was `bd81c6999de276cbed8960e8db7ba1a81d7310c2`, superseded by the amend)

## Files Created/Modified

- `scripts/audit_upstream_merge.py` - `_decorated_span`, `_segment`, `_index_module`, `extract_definition_names`, `_insert_class_members`, `resolve_source_module_conflict`, `resolve_source_layer`, `resolve_generated_conflict`, `REMERGE_REF`; `remerge --layer source` CLI dispatch (resumes from persisted `unresolved_by_class`, merges new resolutions into the existing array)
- `tests/unit/test_audit_upstream_merge.py` - 6 new tests: `extract_definition_names` module+class-level coverage, shared-definition-takes-upstream, fork-only-module-level-retained, fork-only-class-member-spliced-into-shared-class, working-tree staging, generated-stub placeholder
- `.planning/phases/02-upstream-main-integration/evidence/staging/remerge.json` - full resolution table (151 entries: 125 data-config + 19 source/test + 7 generated), `deviation_out_of_scope_resolutions` (141 entries across 3 mechanical-rule buckets), `discovered_findings` (2), `lazy_registry` delta, `registry_integrity` result, `env_sync`, `generated_tool_wrappers`, `stage_merge_oid`, `handoff_state: merged_complete`
- `.planning/phases/02-upstream-main-integration/evidence/staging/SHA256SUMS` - regenerated, verified with `shasum -a 256 -c`
- Inside the throwaway stage only (never the main checkout): `src/tooluniverse/llm_clients.py`, `src/tooluniverse/_lazy_registry_static.py`, `tests/unit/test_registry_integrity.py`, the 16 resolved source modules, 3 resolved test files, 7 regenerated-placeholder-then-true tool stubs, and 141 out-of-scope mechanically-resolved paths, plus ~2,602 regenerated tool wrapper files from Task 3

## Decisions Made

See `key-decisions` in frontmatter. Summary: (1) resolved the real 16+3 file scope, not the plan's literally-named 11+5, per 02-02-SUMMARY's own flagged correction; (2) resolved 7 additional "generated" stub conflicts inside Task 1 because git's pathspec matching pulled them into Task 1's own gate; (3) resolved 141 further out-of-declared-scope conflicts under explicit mechanical rules, structurally separated from the D-08 resolutions array, because git's commit precondition made Task 2 otherwise unreachable; (4) fixed a genuine git auto-merge data-loss bug in `llm_clients.py` that was never even flagged as conflicted; (5) fixed a test-scope gap in `test_registry_integrity.py` using content verified byte-identical to the pinned tree's own already-landed fix; (6) scoped `ruff format` to only the bytes this plan's own resolution work touched, leaving pre-existing upstream-canonical formatting/lint findings untouched per CLAUDE.md's scope-boundary rule.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Resolved 16 source modules + 3 tests, not the plan's literally-named 11 + 5**
- **Found during:** Task 1, before any resolution work, by running the plan's own literal verify command against the live stage
- **Issue:** Plan text named 11 modules and 5 tests sourced from CONTEXT.md's `git diff-tree --cc f81448f2` output. Measured (`git -C <stage> diff --name-only --diff-filter=U`, cross-checked against remerge.json's persisted `unresolved_by_class`) that the real conflict set is 16 source modules (only 6 overlap the named 11) and 3 tests (only 1 overlaps the named 5) -- 02-02-SUMMARY had already flagged this exact correction under "Next Phase Readiness."
- **Fix:** Resolved all 16 + 3 real files under D-08; Task 1's own primary acceptance criterion (`git diff --diff-filter=U` over the pathspec produces no output) is only satisfiable this way.
- **Files modified:** `scripts/audit_upstream_merge.py`, stage files
- **Verification:** Task 1/2's automated `<verify>` diff-emptiness checks pass; the plan's secondary `length == 11` / `length == 5` jq counts do not (16/3 actual) -- documented here as the expected, correct divergence, not a bug in this plan's execution.
- **Committed in:** `7627c785`, `8be4f83c`

**2. [Rule 3 - Blocking issue] Resolved 7 additional generated-stub conflicts inside Task 1's scope**
- **Found during:** Task 1, running the plan's own literal automated verify command
- **Issue:** `git diff --name-only --diff-filter=U -- 'src/tooluniverse/*.py' ':!src/tooluniverse/_lazy_registry_static.py'` still returned 7 files after resolving all 16 source_modules. Git's pathspec `*` crosses `/` without `:(glob)` magic, so this gate also matches `src/tooluniverse/tools/*.py`.
- **Fix:** `resolve_generated_conflict()`, the same `deferred_to_regeneration` treatment `_lazy_registry_static.py` already uses -- fork content as placeholder, true content from Task 3's `generate_tools.main()` regeneration.
- **Files modified:** `scripts/audit_upstream_merge.py`, stage files
- **Verification:** Task 1's literal verify command now returns empty.
- **Committed in:** `7627c785`, `8be4f83c`

**3. [Rule 3 - Blocking issue] Resolved 141 out-of-declared-scope conflicts to reach Task 2's commit**
- **Found during:** Task 2, attempting `git -C <stage> commit --dry-run`
- **Issue:** `symlink_workspaces` (114), `packaging` (9), and `ci_docs` (11) remained conflicted. Git refuses to commit with any unmerged path present, so Task 2's commit step was unreachable regardless of the predecessor state's framing of those classes as out of this plan's scope.
- **Fix:** Resolved under explicit, uniform, non-content-judgment mechanical rules, recorded separately from the D-08 `resolutions` array (`deviation_out_of_scope_resolutions`): symlinks via index-only `git rm` of the already-superseded `~HEAD` marker (git had already auto-resolved the real path); packaging/ci_docs via D-08's literal wording at whole-file granularity.
- **Files modified:** stage files only
- **Verification:** `git -C <stage> commit --dry-run` succeeds cleanly before the real commit; `git -C <stage> status --porcelain` empty post-commit.
- **Committed in:** `8be4f83c` (evidence record); stage commit `a4d3d95a`

**4. [Rule 1 - Bug] Fixed a silent git auto-merge data-loss bug in llm_clients.py**
- **Found during:** Task 3, `generate_tools.main()` raising `ImportError: cannot import name 'AzureOpenAIClient'`
- **Issue:** `llm_clients.py` was never in `conflicts_raw` -- git's own clean auto-merge silently dropped upstream's entire `AzureOpenAIClient` class.
- **Fix:** Applied `resolve_source_module_conflict()` directly to this file despite the absent conflict flag; verified `resolved_name_set_matches_expected: true`, `fork_only_dropped: []`.
- **Files modified:** stage's `src/tooluniverse/llm_clients.py` only (main checkout untouched)
- **Verification:** `ast.parse` clean; `generate_tools.main()` completes; recorded as `discovered_findings[F-02-03-01]`, carried to `02-04`
- **Committed in:** `8be4f83c` (evidence record); stage commit `a4d3d95a`

**5. [Rule 1 - Bug] Fixed a test-scope gap blocking Task 3's hard gate**
- **Found during:** Task 3, `test_json_type_fields_exist_in_lazy_registry` failing on `api_key`/`endpoint`/`secret`
- **Issue:** `test_registry_integrity.py`'s unconditional `data/*.json` scan includes `api_keys_catalog.json` (credential metadata, not tool definitions); neither fork nor upstream's pre-merge test file excludes it.
- **Fix:** Applied the identical 2-line exclusion, byte-for-byte from the current pinned tree (`git blame` attributes it to `f81448f2` itself -- D-06a self-healed-downstream).
- **Files modified:** stage's `tests/unit/test_registry_integrity.py` only (main checkout untouched)
- **Verification:** `pytest tests/unit/test_registry_integrity.py -q --no-cov`: 4 passed, exit 0
- **Committed in:** `8be4f83c` (evidence record); stage commit `a4d3d95a`

### Process deviations (not rule-governed fixes)

**6. Task boundaries collapsed to 2 main-checkout commits, not 3**
- **Reason:** Mirrors 02-02's own precedent exactly. Tasks 1 and 2's script contributions (`resolve_source_module_conflict`, `resolve_source_layer`, the `--layer source` CLI dispatch) are one coherent, jointly-tested unit -- Task 2's test-file resolution literally cannot run without Task 1's resolver existing. Task 3 contributed no new script code (only ran existing tooling: `uv sync`, `generate_lazy_registry.main()`, `generate_tools.main()`) but did substantially extend `remerge.json`'s evidence. Two commits -- one `feat` for the script+tests, one `docs` for the complete evidence bundle after all three tasks' work landed -- keep each commit independently reviewable and revertible as a unit.
- **Verification:** Each task's own `<verify>` block (where mechanically satisfiable given the scope corrections above) was run to green against the live stage before any commit.

---

**Total deviations:** 5 auto-fixed under Rules 1/3, plus 1 process deviation (commit granularity) documented for transparency.
**Impact on plan:** No scope creep beyond what was mechanically required to satisfy the plan's own acceptance criteria and hard gates. Deviations 1-3 correct the plan's under-scoped file lists to measured reality (already flagged by 02-02-SUMMARY) and resolve conflicts git itself requires resolved before any commit can land. Deviations 4-5 fix genuine correctness bugs discovered only by attempting the actual regeneration/registration-chain proof this plan exists to produce -- exactly the failure mode this phase audits for.

## Issues Encountered

- **`llm_clients.py` never appeared as conflicted, yet silently lost content.** This is the most significant finding of this plan: proof that "not in `git diff --diff-filter=U`" is not sufficient evidence a merge preserved everything. Flagged prominently for plan `02-04`, whose findings work should not assume `conflicts_raw`/`conflicts_landed` (both git-diff-derived) are a complete map of where content was lost.
- **`test_registry_integrity.py`'s scan-exclusion fix originated inside the historical merge's own conflict resolution, not either input side.** `git blame` attributing it to `f81448f2` itself confirms D-06a's own premise -- that the landed merge sometimes contains genuine, correct, de novo human judgment a mechanical D-08 re-derivation cannot reproduce -- is not hypothetical; this plan hit a real instance of it.
- **`generate_tools.main(output_dir=None)` regenerates the entire `src/tooluniverse/tools/` tree (2,602 files) on a fresh worktree**, not just the 7 that were conflicted, because there is no prior `.tool_metadata.json` to diff against. This produces a large footprint inside the stage; flagged in `remerge.json`'s `generated_tool_wrappers` note so plan `02-04` treats this directory as generated (compared by presence/behavior, not line diff) rather than surfacing ~2,600 individual "findings."

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Stage handoff for plan 02-04:** `refs/audit/remerge` (OID `a4d3d95a096a14ce4d147faa20334d24f8db9f9a`) is a committed, pinned, fully-resolved, regenerated re-merge stage -- `handoff_state: merged_complete`. The stage worktree itself (`${TMPDIR}/tu-remerge-audit-e0755067`) still exists on disk with its own fresh `.venv`; plan 02-04 can diff `refs/audit/remerge`'s tree against `f81448f2` directly via `git show`/`git diff` without needing the worktree, but the worktree remains available if a live environment check is useful.
- **Findings queue for plan 02-04:** `remerge.json`'s `discovered_findings` (2: `F-02-03-01` high, `F-02-03-02` medium) and the `fork_only_dropped` fields across all 151 `resolutions` entries (all empty -- zero data loss detected in the D-08-governed layers) are the primary inputs. `deviation_out_of_scope_resolutions` (141 entries, 3 buckets) is explicitly disclaimed as carrying no independent SYNC-02/PRES-02 authority -- re-validate against the pinned tree per D-06a before treating any of it as a finding.
- No blockers. `.planning/config.json` and `ralph-specs/fleet/results/` remain untouched and untracked throughout. Main checkout `.venv` unchanged (all environment operations ran inside the stage's own fresh `uv sync`).

---
*Phase: 02-upstream-main-integration*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: scripts/audit_upstream_merge.py
- FOUND: tests/unit/test_audit_upstream_merge.py
- FOUND: .planning/phases/02-upstream-main-integration/evidence/staging/remerge.json
- FOUND: .planning/phases/02-upstream-main-integration/evidence/staging/SHA256SUMS
- FOUND: .planning/phases/02-upstream-main-integration/02-02-SUMMARY.md
- FOUND commit: 7627c785
- FOUND commit: 8be4f83c
- FOUND ref: refs/audit/remerge -> a4d3d95a096a14ce4d147faa20334d24f8db9f9a
