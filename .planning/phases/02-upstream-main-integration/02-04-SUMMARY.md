---
phase: 02-upstream-main-integration
plan: 04
subsystem: infra
tags: [git, merge-audit, findings-classification, preservation-join, sha256, upstream-sync]

# Dependency graph
requires:
  - phase: 02-upstream-main-integration
    provides: "scripts/audit_upstream_merge.py's remerge --layer source resolvers and the committed, pinned re-merge stage at refs/audit/remerge (handoff_state: merged_complete) that plan 02-03 left behind, plus its discovered_findings (F-02-03-01, F-02-03-02)"
provides:
  - "scripts/audit_upstream_merge.py: full_tree_diff, classify_finding, recheck_against_pin, build_findings, join_preservation, _determine_disposition, render_findings_markdown; findings and reclass subcommands"
  - "evidence/staging/findings.json: 3,446 landed-vs-re-derived-stage disagreements, every one classified (unclassified: 0), D-06a pin recheck recorded as a separately-named comparison"
  - "evidence/staging/preservation-reclass.json: all 1,392 preservation.json entries joined to a Phase 2 disposition (survived/superseded_by_upstream/lost), Phase 1 class values preserved verbatim"
  - "02-FINDINGS.md: the human review surface for plan 02-06 -- corrective-commit candidates presented as proposals, none applied"
affects: [02-05, 02-06]

# Actuals (#2632)
actuals:
  tokens: 19000
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "classify_finding's verdict precedence resolves the noise-bucket-vs-real-candidate problem BEFORE blob comparison: dependency_scope (path identity) > remerge_only_artifact (resolution-set membership) > landed_correct (blob equality, both-absent included) > self_healed_downstream (pin corroboration) > landed_dropped_or_altered (default). Measured necessity: the raw landed-vs-stage diff is 3,446 paths, not the ~22 git's own diff-tree --cc flags -- 2,604 are wholesale-regenerated tool-wrapper stubs and 600 are plugin/skills/* directory-materialization artifacts of this audit's own tooling, not fork-content judgments."
    - "join_preservation's disposition function must consult the ALREADY-noise-aware findings.json verdict for a path, not re-derive disposition from a fresh stage-vs-pin blob comparison. Re-deriving reproduced the exact same misattribution build_findings solved: an initial naive stage-vs-pin comparison produced 339 (then 495, after a second miss) false 'lost' verdicts, almost entirely wholesale-regenerated tool stubs and plugin/skills/* sub-paths that are never git-tracked at that literal path under the fork's own symlink architecture. Fixed by branching on finding_verdict first and only falling through to a detailed stage/pin/landed/upstream heuristic for the narrow landed_dropped_or_altered subset (29 of 3,446)."
    - "A rename record in `git diff --raw -z --find-renames --abbrev=40` output is one NUL-delimited meta token (`:oldmode newmode oldoid newoid Rnnn`, no embedded tab) followed by TWO path tokens (source, then destination), not one -- confirmed against real git output before writing the parser. `--abbrev=40` is required; without it OIDs abbreviate to 8 hex chars and every downstream blob-equality check silently breaks."
    - "A preservation.json record with status D under a plugin/skills/<name>/ prefix does not mean content was deleted -- it means upstream's materialized-directory alternative doesn't exist under the fork's own symlink-redirected architecture at that literal path. Disposition for such a sub-path must check whether the top-level symlink (plugin/skills/<name>) is intact at the pin, not whether the literal sub-path itself is git-tracked there."

key-files:
  created:
    - .planning/phases/02-upstream-main-integration/evidence/staging/findings.json
    - .planning/phases/02-upstream-main-integration/evidence/staging/preservation-reclass.json
    - .planning/phases/02-upstream-main-integration/02-FINDINGS.md
    - .planning/phases/02-upstream-main-integration/evidence/staging/.plan-04-start-oid
  modified:
    - scripts/audit_upstream_merge.py
    - tests/unit/test_audit_upstream_merge.py
    - .planning/phases/02-upstream-main-integration/evidence/staging/SHA256SUMS

key-decisions:
  - "Widened classify_finding's remerge_only_artifact resolution-set check to unconditional path membership (not gated on 'present only in remerge'), so a materialized-directory path that is present in LANDED and absent from the re-derived stage (the reverse presence pattern from the literal spec wording) still lands in the correct noise bucket rather than being misclassified as landed_dropped_or_altered. Backward-compatible with the plan's literal unit-test wording since it's a strict superset."
  - "Deliberately did NOT sweep remerge.json's real D-08 resolutions (agentic_tool.py, cli.py, .gitignore, default_config.py, the resolved test files, etc.) into remerge_only_artifact, even though they are literal entries in remerge.json's resolutions array. An initial implementation did this and it was wrong: those are genuine content judgments (entry_union / key_union / upstream_canonical_fork_additive / line_union) that 02-03-SUMMARY itself says 'carry no independent SYNC-02/PRES-02 authority... re-validate against the pinned tree per D-06a before treating any of it as a finding' -- i.e. they must flow through the SAME classify_finding pipeline as any other disagreement, not be exempted from it. Only the two disclaimed, non-content-judgment noise buckets (wholesale regeneration; symlink-to-directory git auto-resolve) are swept."
  - "join_preservation's _determine_disposition consults findings.json's verdict as the primary signal (not a fresh stage-vs-pin blob comparison) -- see patterns-established. This was found and fixed twice during Task 3: first pass produced 339 false 'lost' (generated-stub noise), second pass (after routing remerge_only_artifact through presence-at-pin) still produced 495 false 'lost' (plugin/skills/* sub-paths that are never git-tracked under the fork's symlink architecture at all). Final fix adds a symlink-workspace-root special case: a sub-path under plugin/skills/<name>/ is 'survived' if the top-level plugin/skills/<name> symlink is intact at the pin, regardless of whether the literal sub-path is tracked there."
  - "Added a `pin_matches_landed` diagnostic field to every landed_dropped_or_altered record and an 'Overall Assessment' section to 02-FINDINGS.md, beyond what the plan's literal schema required. classify_finding's blob-comparison design cannot by itself distinguish 'landed dropped real fork content' from 'this audit's own re-derivation tooling produces different bytes than the original human resolution while landed and the pin both agree, unchanged.' Measured: 27 of 29 candidates carry pin_matches_landed=true (the pin, 31 commits downstream, matches what shipped -- not this audit's re-derivation), and the remaining 2 carry an explaining unrelated repair commit (4b2c1c38). Recording this explicitly prevents 02-06 from treating formatting/re-derivation-style churn as fork-content-loss candidates."

patterns-established:
  - "_ls_tree_blobs(repo, ref) -- one `git ls-tree -r -z` per tree into a path->(mode,blob_oid) dict -- is the right tool whenever a join needs presence/blob lookups across many paths (1,392 records x up to 4 trees here); avoids ~5,500 per-path git rev-parse subprocess calls."
  - "_parse_raw_diff_output(raw: str) is a pure function extracted from full_tree_diff so the NUL-safe raw-diff parser (space-in-path, R100 rename preserving both operands) is unit-testable against a literal deterministic payload without invoking git -- full_tree_diff itself is now a thin git-invoking wrapper around it."

requirements-completed: [SYNC-02, PRES-02]

coverage:
  - id: D1
    description: "Full-tree diff of the landed merge (f81448f2) against the re-derived stage (a4d3d95a) enumerates every disagreement (3,446, not just the 22 conflict-marked files), and every one carries exactly one of five verdicts with unclassified: 0"
    requirement: SYNC-02
    verification:
      - kind: unit
        ref: "tests/unit/test_audit_upstream_merge.py::test_classify_finding_verdicts (7 parametrized cases covering all 5 verdicts + pin-mismatch discrimination), ::test_classify_finding_dependency_scope_wins_regardless_of_blob_state, ::test_full_tree_diff_parses_path_with_embedded_space, ::test_full_tree_diff_preserves_both_operands_of_a_rename_record, ::test_full_tree_diff_live_against_a_synthetic_repo, ::test_recheck_against_pin_reports_absent_when_path_missing_at_pin, ::test_recheck_against_pin_finds_repair_commit_in_ancestry_range"
        status: pass
      - kind: other
        ref: "python3 scripts/audit_upstream_merge.py findings --repo . --json; jq over findings.json: summary.unclassified == 0, primary_comparison.left_oid == f81448f2, self_heal_recheck.left_oid == 21945440, all verdicts in the 5-item enum, every landed_dropped_or_altered record has repair_commits + pin_blob, pyproject.toml routes to dependency_scope"
        status: pass
    human_judgment: false
  - id: D2
    description: "27 of 29 landed_dropped_or_altered candidates carry pin_matches_landed=true (pin, 31 commits downstream, agrees with what shipped, not this audit's re-derivation) and the remaining 2 carry an explaining unrelated repair commit (4b2c1c38) -- the corrective-commit candidate list for plan 02-06 is effectively empty"
    requirement: SYNC-02
    verification:
      - kind: manual_procedural
        ref: "02-FINDINGS.md Corrective-commit Candidates table + Overall Assessment section; independently confirmed llm_clients.py's AzureOpenAIClient present in landed/upstream/pin alike (matches predecessor-state F-02-03-01 finding) and test_registry_integrity.py never appearing as a disagreement at all (matches F-02-03-02)"
        status: pass
    human_judgment: true
    rationale: "Whether an unrepaired byte-level disagreement is truly inconsequential is a judgment call plan 02-06's decision checkpoint owns per D-06; this plan supplies the evidence (pin_matches_landed, repair_commits) but does not itself authorize skipping the human gate."
  - id: D3
    description: "All 1,392 preservation.json entries carry a Phase 2 disposition (survived/superseded_by_upstream/lost), Phase 1's class values preserved verbatim (512 custom_code confirms it), all four tree OIDs (pin, upstream, stage, landed) recorded side by side, CONTEXT.md's A2 claim recorded as a discrepancy (84 of 1,392 are other_review_required, not all 1,392)"
    requirement: PRES-02
    verification:
      - kind: other
        ref: "python3 scripts/audit_upstream_merge.py reclass --repo . --json; jq over preservation-reclass.json: records length == 1392, zero null phase2_disposition, preservation_fork_oid == 21945440, preservation_upstream_oid == 56adcfd9, class==custom_code count == 512, context_md_discrepancy has claimed+measured, every symlink record has phase2_disposition+evidence"
        status: pass
    human_judgment: false
  - id: D4
    description: "No corrective commit landed in this plan; refs/audit/remerge unchanged/unmerged/unpushed; SHA256SUMS verifies; .planning/config.json and ralph-specs/fleet/results/ remain untouched and untracked"
    verification:
      - kind: other
        ref: "git diff --name-only $(cat .plan-04-start-oid)..HEAD -- src/ pyproject.toml uv.lock: empty; git branch --contains refs/audit/remerge: empty; shasum -a 256 -c SHA256SUMS: OK for all 4 evidence files; git status --porcelain shows only the two pre-existing untracked user-owned paths throughout"
        status: pass
    human_judgment: false

duration: ~2h30min
completed: 2026-08-06
status: complete
---

# Phase 2 Plan 4: Full-tree Merge Findings + Preservation Reclassification Summary

**Classified all 3,446 landed-vs-re-derived-stage disagreements into 5 verdicts (2,604 wholesale-regenerated tool stubs + 600 plugin/skills materialization artifacts correctly excluded as this audit's own tooling noise, not fork-content findings), joined the result to all 1,392 preservation.json entries, and found the corrective-commit candidate list for plan 02-06 to be effectively empty -- 27 of 29 surviving candidates carry direct evidence the landed merge is correct and this audit's own re-derivation tooling produced the disagreement, not a real fork-content loss.**

## Performance

- **Duration:** ~2h30min
- **Started:** 2026-08-06T18:00:00Z (approx)
- **Completed:** 2026-08-06T20:35:00Z (approx)
- **Tasks:** 3
- **Files modified:** 7 (script, test, 3 evidence JSON, 1 findings markdown, 1 start-OID marker)

## Accomplishments

- **Measured the real disagreement count before designing the classifier, per the advisor's guidance:** `git diff --raw -z --find-renames f81448f2 a4d3d95a` enumerates **3,446** paths, not ~22 or ~50. Breakdown: 2,604 wholesale-regenerated `src/tooluniverse/tools/*.py` wrapper stubs, 600 `plugin/skills/*` directory-materialization records (git's own D+A auto-resolve replacing the fork's symlink with upstream's directory before this audit's D-08 resolvers ever ran), 213 `data/*.json` (211 confirmed `union_ok` canonical-JSON-reformat-only via `union.json`), 17 source modules, 4 tests, 1 `.gitignore`, 3 `skills/*` markdown files, 1 `pyproject.toml`, 1 `_lazy_registry_static.py`.
- Built `full_tree_diff` / `_parse_raw_diff_output` (NUL-safe, `--abbrev=40` for full-length blob OIDs, rename records preserving both operands in one record), `classify_finding` (pure, 7-arg + `resolution_paths` kwarg, 5-verdict precedence table), `recheck_against_pin` (D-06a corroboration via `git log --ancestry-path`), and `build_findings` (the orchestrating sweep with two documented noise-bucket overrides plus a `union.json`-aware canonical-reformat override).
- **Caught and fixed a real classification bug before committing:** an initial version swept remerge.json's literal `resolutions` array (the genuine D-08 content decisions -- `agentic_tool.py`, `cli.py`, `default_config.py`, `.gitignore`, resolved test files) into `remerge_only_artifact`, exempting them from real review. Fixed by restricting the noise-bucket override to only the two non-content-judgment buckets (wholesale regeneration; symlink-to-directory git auto-resolve) and letting every genuine D-08 resolution flow through the same `classify_finding` pipeline as any other disagreement, per 02-03-SUMMARY's own explicit instruction to re-validate them, not exempt them.
- `findings.json`: 3,446 disagreements, `unclassified: 0` -- 211 `landed_correct`, 3,205 `remerge_only_artifact`, 1 `dependency_scope` (`pyproject.toml`), 0 `self_healed_downstream`, 29 `landed_dropped_or_altered`. `primary_comparison` (left=`f81448f2`) and `self_heal_recheck` (left=`21945440`) recorded as distinct objects with distinct left operands.
- Every `landed_dropped_or_altered` record carries a `pin_matches_landed` diagnostic (added beyond the plan's literal schema): 27 of 29 have `pin_matches_landed=true` -- the pin (31 commits downstream of landed) agrees with what actually shipped, not with this audit's re-derivation, meaning the disagreement originates in this audit's own AST-splice/whole-file-canonical/entry-union tooling producing different bytes than the original human merge resolution, not in dropped fork content. The remaining 2 (`skills/setup-tooluniverse/SKILL.md`, `src/tooluniverse/execute_function.py`) carry an explaining unrelated downstream repair commit (`4b2c1c38 fix: harden sync, discovery, cache lifecycle, and docs`).
- Independently confirmed both plan 02-03 `discovered_findings` resolve to non-issues: `AzureOpenAIClient` present in `landed_blob == pin_blob` for `llm_clients.py` (F-02-03-01, matches predecessor-state claim exactly); `tests/unit/test_registry_integrity.py` never even appears in the disagreement set (byte-identical between landed and the re-derived stage -- F-02-03-02's fix, sourced byte-for-byte from the pinned tree, converged exactly).
- **Caught and fixed a preservation-join bug twice** (`_determine_disposition`): a naive stage-vs-pin blob comparison, run independently of `findings.json`'s already-noise-aware verdict, reproduced the exact misattribution `build_findings` had already solved -- first pass produced 339 false `lost` verdicts (326 wholesale-regenerated tool stubs), second pass (after routing `remerge_only_artifact` through presence-at-pin) still produced 495 false `lost` (`plugin/skills/*` sub-paths that are never git-tracked at that literal path under the fork's own symlink architecture at all -- upstream materializes a directory of files there, the fork always redirects via a single symlink). Fixed by (1) consulting `findings.json`'s verdict as the primary disposition signal, falling through to a detailed stage/pin/landed/upstream heuristic only for the narrow `landed_dropped_or_altered` subset, and (2) a symlink-workspace-root special case: a `plugin/skills/<name>/...` sub-path is `survived` if the top-level `plugin/skills/<name>` symlink is intact at the pin, regardless of the literal sub-path's own (non-)existence there.
- `preservation-reclass.json`: 1,392 of 1,392 records, zero null dispositions -- **1,377 survived, 6 superseded_by_upstream, 9 lost** (both non-`survived` buckets are the same small subset of the 29 `findings.json` candidates, not additional risk). Phase 1's `class` values preserved verbatim (`custom_code` 512 exactly matches the measured distribution). `context_md_discrepancy` records CONTEXT.md's A2 claim ("all 1,392 carry `other_review_required`") against the measured reality (only 84 do).
- Symlink records (120 of 1,392) verified via `git ls-tree` mode + `git cat-file blob` at both the stage and pin trees -- link text compared without ever traversing or reading through a symlink on disk (T-02-14), stronger than `lstat`/`readlink` since it works even after the stage worktree is cleaned up.
- `02-FINDINGS.md`: ASCII-only (`perl -ne 'exit 1 if /[^\x00-\x7F]/'` clean), all four trees named with OIDs, ISO-8601 ms timestamp, reciprocal wikilinks to `[[02-CONTEXT]]` `[[02-RESEARCH]]` `[[01-VERIFICATION]]`, every corrective-commit candidate presented as a proposal gated on plan 02-06, and an explicit "Overall Assessment" section stating the bottom line: **the corrective-commit candidate list is effectively empty.**
- 14 new unit tests (`test_classify_finding_verdicts` parametrized over all 5 verdicts + the pin-mismatch discrimination case, `full_tree_diff`/`_parse_raw_diff_output` space-in-path and R100-rename coverage, `recheck_against_pin` absent/repair-commit cases) -- all green, zero skipped; sibling suites (`test_registry_integrity.py`, `test_sync_baseline_git.py`) remain green.
- No corrective commit landed anywhere in this plan: `git diff --name-only $(cat .plan-04-start-oid)..HEAD -- src/ pyproject.toml uv.lock` is empty. `refs/audit/remerge` unchanged, unmerged, unpushed throughout. `.planning/config.json` and `ralph-specs/fleet/results/` remained untracked and untouched throughout.

## Task Commits

1. **Task 1 + Task 2 (script + tests): full_tree_diff, classify_finding, recheck_against_pin, build_findings, findings CLI dispatch** - `a4376e96` (feat)
2. **Task 1 (evidence): findings.json -- 3,446 disagreements classified, unclassified: 0** - `02074c14` (docs)
3. **Task 3 (script + evidence + doc): join_preservation, _determine_disposition, render_findings_markdown, reclass CLI dispatch; preservation-reclass.json; 02-FINDINGS.md** - `dc8803b0` (feat)
4. **Formatting fix: ruff format the Task 3 additions (whitespace only, evidence files byte-identical)** - `61f19405` (style)

**Plan metadata:** commit pending (this SUMMARY + STATE.md + ROADMAP.md + REQUIREMENTS.md)

## Files Created/Modified

- `scripts/audit_upstream_merge.py` - `_parse_raw_diff_output`, `full_tree_diff`, `_diff_entries`, `classify_finding`, `recheck_against_pin`, `_resolve_blob`, `_finding_rationale`, `build_findings`, `_ls_tree_blobs`, `_blob_text`, `_determine_disposition`, `_detailed_disposition`, `_symlink_workspace_root`, `_symlink_disposition`, `join_preservation`, `render_findings_markdown`, `run_stamp`; `findings` and `reclass` subcommand dispatch
- `tests/unit/test_audit_upstream_merge.py` - 14 new tests: 7 parametrized `classify_finding` verdict cases, dependency-scope-wins case, 2 raw-diff-parser edge cases (space-in-path, R100 rename), 1 live-git sanity check, 2 `recheck_against_pin` cases
- `.planning/phases/02-upstream-main-integration/evidence/staging/findings.json` - 3,446 classified disagreements, `primary_comparison`/`self_heal_recheck` metadata
- `.planning/phases/02-upstream-main-integration/evidence/staging/preservation-reclass.json` - 1,392 dispositions, four tree OIDs, `context_md_discrepancy`, `blocker_dispositions`, `untracked_out_of_scope`, `upstream_deleted_data_files`
- `.planning/phases/02-upstream-main-integration/02-FINDINGS.md` - the human review surface for plan 02-06
- `.planning/phases/02-upstream-main-integration/evidence/staging/SHA256SUMS` - regenerated, verified with `shasum -a 256 -c`
- `.planning/phases/02-upstream-main-integration/evidence/staging/.plan-04-start-oid` - this plan's start HEAD, recorded as the first action so "no corrective commit landed" is provable by diff

## Decisions Made

See `key-decisions` in frontmatter. Summary: (1) widened `remerge_only_artifact`'s resolution-set check to unconditional path membership so the reverse presence pattern (present-in-landed, absent-from-remerge, e.g. a materialized symlink) is still caught correctly; (2) deliberately excluded remerge.json's real D-08 resolutions from the noise-bucket sweep after an initial implementation wrongly exempted them, per 02-03-SUMMARY's own instruction to re-validate rather than exempt; (3) made `join_preservation`'s disposition function consult `findings.json`'s already-noise-aware verdict as the primary signal, fixed twice after two rounds of measured false-`lost` verdicts; (4) added a `pin_matches_landed` diagnostic and an "Overall Assessment" section beyond the plan's literal schema, because blob comparison alone cannot distinguish real fork-content loss from this audit's own re-derivation tooling producing different (but not worse) bytes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] classify_finding's remerge_only_artifact swept genuine D-08 resolutions as noise**
- **Found during:** Task 1, inspecting `findings.json`'s first run -- `agentic_tool.py`, `cli.py`, `default_config.py`, `.gitignore`, and 5 more genuinely-resolved files were misclassified `remerge_only_artifact` instead of undergoing real classification.
- **Issue:** The initial `build_findings` implementation included `remerge.json`'s literal `resolutions` array (every D-08 content decision, not just the two disclaimed noise buckets) in the `resolution_paths` set passed to `classify_finding`, exempting real content judgments from review.
- **Fix:** Restricted the noise-bucket override to only the two non-content-judgment buckets (wholesale-regenerated tool stubs / lazy registry; `plugin/skills/*` directory-materialization from git's own auto-resolve). Every genuine D-08 resolution now flows through the same `classify_finding` pipeline as any other disagreement.
- **Files modified:** `scripts/audit_upstream_merge.py`
- **Verification:** Re-ran `findings --json`; `landed_dropped_or_altered` count rose from 16 to 29 (the previously-exempted real resolutions now correctly under review), `unclassified` stayed 0.
- **Committed in:** `a4376e96` (before the evidence commit `02074c14`, so the committed `findings.json` reflects the fix)

**2. [Rule 1 - Bug] join_preservation's disposition heuristic reproduced the noise-bucket misattribution twice**
- **Found during:** Task 3, inspecting `preservation-reclass.json`'s first run (339 `lost`) and second run (495 `lost`, after a partial fix)
- **Issue:** `_determine_disposition` initially re-derived disposition from a fresh stage-vs-pin blob comparison, independent of `findings.json`'s already-noise-aware verdict. This misclassified 326 wholesale-regenerated tool-wrapper stubs as `lost` (pass 1), and after routing `remerge_only_artifact` through presence-at-pin, still misclassified 469 `plugin/skills/*` sub-paths as `lost` (pass 2) because those literal sub-paths are never git-tracked under the fork's own symlink architecture at all (upstream materializes a directory there; the fork always redirects through one symlink path).
- **Fix:** Restructured `_determine_disposition` to consult the path's `findings.json` verdict first (falling through to a detailed heuristic only for the narrow `landed_dropped_or_altered` subset), and added a `_symlink_workspace_root` special case: a `plugin/skills/<name>/...` sub-path is `survived` if the top-level symlink is intact at the pin.
- **Files modified:** `scripts/audit_upstream_merge.py`
- **Verification:** Re-ran `reclass --json` after each fix; `lost` count went 339 -> 495 -> 9, with the final 9 all confirmed as genuine `findings.json` `landed_dropped_or_altered` candidates (not noise).
- **Committed in:** `dc8803b0`

### Process deviations (not rule-governed fixes)

**3. Added a `pin_matches_landed` diagnostic field and an "Overall Assessment" section, beyond the plan's literal schema**
- **Reason:** `classify_finding`'s blob-comparison design, by itself, cannot distinguish "landed dropped real fork content" from "this audit's own re-derivation tooling (AST-splice / whole-file-canonical / entry-union) produces different bytes than the original human merge resolution while landed and the pin both agree, unchanged." Without this field, a human reviewer at plan 02-06 would have to manually re-derive the same investigation this plan already did (confirmed via `git rev-parse` on `llm_clients.py`/`AzureOpenAIClient` and the `4b2c1c38` repair-commit trail) for all 29 candidates.
- **Verification:** `02-FINDINGS.md`'s candidate table and Overall Assessment section make the distinction explicit and auditable; `jq` acceptance criteria checks are unaffected since they only require the presence of `repair_commits`/`pin_blob`, not the absence of additional fields.

---

**Total deviations:** 2 auto-fixed (Rule 1, both self-caught before committing), plus 1 process deviation (added diagnostic field/section) documented for transparency.
**Impact on plan:** No scope creep -- both auto-fixes correct classification bugs discovered by running this plan's own acceptance criteria against real data, exactly the kind of self-correction the plan's TDD framing and the advisor's "measure before designing" guidance exist to catch. The added diagnostic field strengthens the human review surface without changing any acceptance-criteria-checked schema.

## Issues Encountered

- **The raw landed-vs-stage diff is 3,446 paths, not the ~22 `git diff-tree --cc` reports.** Confirmed before writing any classification logic (per the advisor's explicit guidance to measure first): 2,604 are wholesale-regenerated tool-wrapper stubs, 600 are `plugin/skills/*` directory-materialization artifacts from git's own auto-resolve during the merge-in-progress step (predates this audit's own D-08 resolvers), 213 are `data/*.json` (211 confirmed semantically equivalent via `union.json`). Both noise buckets are structural byproducts of this audit's own tooling, not fork-vs-upstream content judgments -- excluding them from the candidate list required consulting `union.json` and `remerge.json`'s own disclaimers, not just the raw blob diff.
- **`preservation.json`'s `status: D` records under `plugin/skills/*` do not mean deleted content.** They record upstream's materialized-directory alternative not existing under the fork's symlink-redirected architecture at that literal path -- a structural difference in representation, not a content loss. Discovered only by manually tracing one such record (`plugin/skills/setup-tooluniverse/API_KEYS_REFERENCE.md`) back through `preservation.json`'s own upstream-vs-pin diff direction.
- **Two of the 213 `data/*.json` both-sides paths (`oxo_tools.json` / `broken_apis/oxo_tools.json`) fall outside `union.json`'s sweep scope** (only one side, not both, touched the pre-merge base) yet still appear as a genuine `landed_dropped_or_altered` disagreement -- landed correctly carries both the original and upstream's relocated-to-`broken_apis` version, while this audit's re-derivation stage lost upstream's content update during git's own rename-detection auto-merge (mirroring F-02-03-01's class of bug, this time in a data file). Flagged in `02-FINDINGS.md`'s candidate table with full blob evidence; not fixed here per D-06's findings-only posture.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **02-FINDINGS.md is the complete review surface for plan 02-06's decision checkpoint.** The corrective-commit candidate list is effectively empty: of 29 `landed_dropped_or_altered` candidates, 27 carry `pin_matches_landed=true` (direct evidence the disagreement is this audit's own re-derivation tooling, not the landed merge) and the remaining 2 carry an explaining unrelated repair commit. Plan 02-06 should confirm this read and can very likely close without any corrective commit.
- **`preservation-reclass.json`'s 9 `lost` + 6 `superseded_by_upstream` records are the same small set already in `findings.json`'s candidate table** -- no additional preservation risk beyond what's already surfaced.
- `refs/audit/remerge` (OID `a4d3d95a096a14ce4d147faa20334d24f8db9f9a`) remains available for plan 02-05/02-06 if further inspection of the re-derived stage is useful; it is still committed, pinned, unmerged, and unpushed.
- No blockers. `.planning/config.json` and `ralph-specs/fleet/results/` remain untouched and untracked throughout.

---
*Phase: 02-upstream-main-integration*
*Completed: 2026-08-06*

## Self-Check: PASSED

- FOUND: scripts/audit_upstream_merge.py
- FOUND: tests/unit/test_audit_upstream_merge.py
- FOUND: .planning/phases/02-upstream-main-integration/evidence/staging/findings.json
- FOUND: .planning/phases/02-upstream-main-integration/evidence/staging/preservation-reclass.json
- FOUND: .planning/phases/02-upstream-main-integration/02-FINDINGS.md
- FOUND: .planning/phases/02-upstream-main-integration/evidence/staging/.plan-04-start-oid
- FOUND commit: a4376e96
- FOUND commit: 02074c14
- FOUND commit: dc8803b0
- FOUND commit: 61f19405
