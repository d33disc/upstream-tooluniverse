# Phase 3: Follow-up and Catalog Reconciliation - Context

**Gathered:** 2026-08-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish whether historical PR #161 is already represented by the integrated upstream revision (and integrate it separately if not), then restore and certify a coherent, complete, loadable six-link registration chain across every synchronized and preserved tool. This phase does not perform new feature development, does not refactor the execution core, and does not certify cross-surface behavior beyond catalog loading and discovery (that is Phase 5 / SURF-01).

**User declined to work through phase-specific gray areas in this discussion** ("nothing particular") and asked Claude to proceed on discretion. The decisions below are Claude's implementation calls, made from the codebase evidence already gathered this session (Phase 1/2 evidence, CONCERNS.md tech-debt entries, live git checks) rather than from user preference statements -- treat them as defaults the planner may revisit, not as user-stated requirements.

</domain>

<decisions>
## Implementation Decisions

### PR #161 Handling (SYNC-03)

- **D-01:** Treat SYNC-03 as **verify-and-record, not a separate merge/integration stage**. Phase 1's `git.json` already records `pr161_ancestor: true` with merge OID `16af425c053c306a658c96e254b4c4114338dd11`. Re-verified live against current HEAD in this discussion: `git merge-base --is-ancestor 16af425c... HEAD` still returns true, so nothing that landed since Phase 1 (including all of Phase 2's corrective commits) invalidated the ancestry. Since the commit is already an ancestor, there is no separate stage to merge -- SYNC-03 is satisfied by re-deriving and publishing this proof, following the same "verify, don't assume" discipline Phase 2's D-06a established. -- **Reversibility:** reversible -- if the re-verification had failed, the phase would pivot to an actual integration stage; it did not.
- **D-02:** If re-verification at planning/execution time contradicts this (ancestry no longer holds, e.g. a history rewrite), **stop and treat it as a planning-time finding**, not something to silently work around -- this would be a significant, unexpected state change worth surfacing before any further Phase 3 work.

### Registration-Chain Audit Scope (CAT-01)

- **D-03:** Audit is **two-tiered, not an from-scratch manual pass over all ~2,300 tools**. Tier 1: every tool touched by Phase 2's actual merge -- the 22 `git diff-tree --cc f81448f2` hand-resolved files plus the 213 both-sides `data/*.json` files from the union sweep -- gets explicit six-link verification (JSON definition -> implementation -> catalog config -> lazy metadata -> generated module -> tests). Tier 2: a full mechanical pass via `tests/unit/test_registry_integrity.py`-style automated checks across the *entire* catalog, since this is cheap to run and is exactly the backstop CONCERNS.md's "Generated and hand-maintained registries coexist" tech-debt entry calls for -- catches drift outside Phase 2's explicit touch-set without requiring manual per-tool inspection of the full catalog. -- **Reversibility:** reversible -- the tiering can be widened if Tier 2 surfaces problems concentrated outside Tier 1's scope.
- **D-04:** `tests/unit/test_registry_integrity.py` (already exercised repeatedly this session, always green post-Phase-2) is the canonical mechanical check -- extend it rather than writing a parallel registry-integrity script, matching the pattern Phase 1 and Phase 2 both established (extend existing test modules, don't fork new ones).

### Duplicate/Stale Registry Handling (CAT-02)

- **D-05:** **Regeneration is mechanical and auto-run; only genuine name collisions need review.** PROJECT.md states hand-edited partial registries are "not a valid synchronized state" and regeneration (`tu build` / `generate_lazy_registry.py`) is the expected, low-risk mechanism -- auto-run it and treat a clean regeneration as self-resolving for stale entries. A **duplicate public name across two different tool definitions** is a different, higher-risk class (an actual naming collision, not staleness) and follows Phase 2's D-06 pattern: recorded as a finding, resolved only after review, never silently reconciled. -- **Reversibility:** reversible for regeneration (it is a deterministic build step); the review gate for genuine collisions is what keeps it that way.

### The Concurrent Uncommitted Regeneration

- **D-06:** **Investigate before building on it or ignoring it.** `src/tooluniverse/tools/*.py` (2,660 files) and `.tool_metadata.json` are modified and uncommitted in this shared checkout, with an mtime (~2026-08-06T17:32) that predates this session's own Phase 2 work -- another concurrent session's in-progress output, not this session's. A sample diff (`ACC_list_guidelines.py`) shows type-hint cleanup (`int | Any` -> `int`) consistent with exactly the kind of registration/codegen regeneration CAT-01/CAT-02 cover. **Do not silently commit, revert, or build on this state.** The Phase 3 researcher must first determine: is this session still active, is its output correct and complete, and does it supersede or conflict with Phase 3's planned regeneration work? Record the finding and route it to a human decision if the other session's status can't be determined mechanically (e.g., no matching commit ever lands and the working tree sits dirty across multiple Phase 3 planning sessions). -- **Reversibility:** the investigation itself is free; touching the files before investigating would not be (this is exactly the shared-workspace hazard this session hit and worked around earlier in Phase 2).

### Claude's Discretion

- Exact evidence-artifact format for the six-link chain proof (per-tool table vs. aggregate pass/fail counts vs. both) -- follow Phase 1/2's established `evidence/<oid>/` + `SHA256SUMS` convention.
- Whether Tier 1's audit and Tier 2's mechanical pass run as one combined script or two -- whichever keeps the artifact schema joinable, per Phase 2's `join_preservation` precedent (findings.json's verdict as the primary signal, not re-derived comparisons).
- Ordering of PR #161 verification vs. the registration-chain audit -- SYNC-03's re-verification is cheap and has no dependency on CAT-01/CAT-02, so it can run first, last, or in parallel; the researcher/planner may sequence for convenience.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

ROADMAP.md carries no `Canonical refs:` line for Phase 3, so this list was assembled during this discussion.

### Scope and requirements

- `.planning/PROJECT.md` -- milestone constraints, "hand-edited partial registries are not a valid synchronized state" (governs D-05), staged integration sequence (Phase 1 baseline -> Phase 2 upstream merge -> Phase 3 PR #161 evaluation).
- `.planning/REQUIREMENTS.md` -- Phase 3 requirements SYNC-03, CAT-01, CAT-02.
- `.planning/ROADMAP.md` -- Phase 3 boundary, goal, and the four observable success criteria.
- `.planning/phases/02-upstream-main-integration/02-CONTEXT.md` -- Phase 2 decisions carried forward: D-06/D-06a (findings-only posture, pin recheck before corrective commit), D-06b (corrective commits land on `docs/gsd-codebase-map`), the deferred note that PR #161 belongs here.
- `.planning/phases/02-upstream-main-integration/02-FINDINGS.md` -- the 22 hand-resolved files and 213 both-sides `data/*.json` files that define Tier 1's audit scope (D-03).

### PR #161 evidence

- `.planning/phases/01-protected-sync-baseline/evidence/21945440c9f2a15537ba878500a800d9e330eab0/git.json` -- `pr161_ancestor: true`, `pr161_merge_oid: 16af425c053c306a658c96e254b4c4114338dd11`. Re-verified live against current HEAD during this discussion (2026-08-07); still true.

### Registration chain and catalog architecture

- `.planning/codebase/CONCERNS.md` section "Generated and hand-maintained registries coexist" -- names the exact tech-debt this phase closes: `src/tooluniverse/tool_registry.py`, `_lazy_registry_static.py`, `generate_lazy_registry.py`, `generate_coding_api.py`, `src/tooluniverse/data/`, `src/tooluniverse/tools/__init__.py` must stay synchronized or a tool "can exist in configuration but be undiscoverable, import under the wrong name, or expose stale schemas on one transport."
- `.planning/codebase/ARCHITECTURE.md` -- shared-core execution paths; every transport converges on `ToolUniverse` in `src/tooluniverse/execute_function.py`.
- `.planning/codebase/STRUCTURE.md` -- directory layout: `src/tooluniverse/data/` (JSON definitions), `src/tooluniverse/tools/` (generated per-tool modules).
- `tests/unit/test_registry_integrity.py` -- the canonical mechanical registration-chain check (D-04); extend, do not fork.
- `docs/dev_docs/Interaction_Surfaces.md` section 2 -- the discovery layer (`grep_tools`, `find_tools`, `list_tools`, `get_tool_info`, `execute_tool`) CAT-02's success criteria are phrased against.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `scripts/audit_upstream_merge.py` (Phase 2) already has `extract_definition_names` (AST-based top-level/class-level definition extraction) and `classify_finding`'s two-stage verdict pattern (primary comparison + pin/self-heal recheck) -- directly reusable for Tier 1's per-tool six-link verification rather than writing a new AST walker.
- `scripts/forensic_trace_findings.py` (Phase 2, this session) demonstrates the "diff definitions, then check if the stage-only name is actually absent from HEAD or just renamed/still referenced" pattern -- the same false-positive-avoidance discipline applies to distinguishing a genuinely stale registry entry from a renamed one.
- `tests/unit/test_registry_integrity.py` already runs green and fast (`4 passed` in ~3s against the re-merge stage in Phase 2); it is the right base to extend for CAT-01's mechanical pass.
- Phase 1/2's `evidence/<full-OID>/` + sorted `SHA256SUMS` convention (via `capture_sync_baseline.py`'s `publish_evidence`/`verify_checksums`) is directly reusable for Phase 3's audit artifact.

### Established Patterns

- Findings-first, human-gated corrective commits (Phase 2 D-06/D-06a/D-06b) -- this session's 02-06 checkpoint demonstrated the pattern end-to-end (1 approved out of 29 candidates, 28 traced to false positives) and should be Phase 3's default posture for anything beyond mechanical regeneration.
- `git log --oneline <ref>..HEAD -- <path>` to confirm whether a file was touched by *this* phase's work before treating an anomaly as in-scope or pre-existing (used this session to correctly route a pre-existing `execute_function.py` async-context bug to a separate follow-up task instead of blocking Phase 2's close).
- Shared-workspace concurrency hazard: `.planning/` and all Git state live in `/Users/davis/code/ToolUniverse`, shared by concurrent Claude sessions that auto-commit each other's edits. Verify `git status` and current branch before any staging or commit; never assume an untouched-but-modified file is safe to revert or claim.

### Integration Points

- The registration-chain audit connects `src/tooluniverse/data/*.json` (definitions) through `src/tooluniverse/tools/*.py` (generated modules) and `.tool_metadata.json` (generated hashes) to `_lazy_registry_static.py` (the lazy loader) -- CAT-01's six links span this whole chain, and the concurrent uncommitted regeneration (D-06) sits directly in the middle of it.
- CAT-02's `grep_tools`/`get_tool_info` surface is the discovery layer described in `docs/dev_docs/Interaction_Surfaces.md` section 2 -- certifying it means running the actual discovery primitives against the post-Phase-2 catalog, not just checking file presence.

</code_context>

<specifics>
## Specific Ideas

No specific requirements were stated in this discussion -- the user declined the offered gray areas and delegated implementation choices to Claude's discretion (see `<domain>` note above). The decisions in this document are Claude's calls, grounded in codebase evidence, not user preferences -- the planner should treat them as a starting point open to revision, not a locked spec.

</specifics>

<deferred>
## Deferred Ideas

- **Full cross-surface certification** (Python, CLI, MCP stdio/HTTP, REST) -- Phase 3 only certifies catalog loading and discovery (`grep_tools`/`get_tool_info`). Full surface certification is Phase 5 / SURF-01, per ROADMAP.md.
- **Execution-core refactoring** -- CONCERNS.md's "Monolithic execution core" and "Broad exception suppression" tech-debt entries are real but out of this milestone's scope per PROJECT.md ("Broad refactoring of the monolithic execution core or registry architecture -- high-risk structural work needs a separate milestone").
- **The pre-existing `execute_function.py` async-context bug** (`RuntimeError: no running event loop` in `ToolCallable.__call__`, discovered during Phase 2's close-out) -- already routed to a standalone follow-up task (`task_43fff30b`), not folded into Phase 3. It is adjacent to CAT-01's registration-chain concern but is a runtime-dispatch bug, not a registration/discovery gap.

</deferred>

---

*Phase: 3-follow-up-and-catalog-reconciliation*
*Context gathered: 2026-08-07*
