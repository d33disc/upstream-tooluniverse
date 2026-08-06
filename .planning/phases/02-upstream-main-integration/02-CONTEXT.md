# Phase 2: Upstream Main Integration - Context

**Gathered:** 2026-08-06
**Status:** Ready for planning

<domain>
## Phase Boundary

The fork contains the selected upstream-main revision (`56adcfd9`) without losing its custom capabilities.

**Reframing established during this discussion — downstream agents must start here.** Git containment is already satisfied: `git ls-remote upstream main` returns `56adcfd9c299078d0c40fde642b0be006510ccf3`, unchanged since Phase 1 froze it, and that commit is an ancestor of the fork (`git rev-list --left-right --count HEAD...upstream/main` = `124 0`; merge-base equals the upstream head). It entered through merge `f81448f2` ("merge: sync with upstream mims-harvard/ToolUniverse"), whose parents are fork commit `e0755067` and upstream `56adcfd9`.

Therefore Phase 2 is **not** "perform the merge." It is **audit and reconcile the merge that already landed**. Success criterion 1 (containment in an isolated integration stage) is satisfied at the Git level and re-established as an isolated stage by the re-merge below. Criteria 2, 3, and 4 are **not** satisfied by containment and are the actual work: `rev-list` cannot see whether `f81448f2` clobbered a fork-only tool definition, dropped fork lines from the structural files, or left a custom tool unloadable. Those conflict resolutions were never reviewed under this milestone — Phase 1's CONTEXT.md states explicitly that Phase 1 "does not merge upstream changes."

**Not in this phase:** PR #161 resolution. Phase 1 evidence already records `pr161_ancestor: true` with merge OID `16af425c053c306a658c96e254b4c4114338dd11`, which answers SYNC-03 — a Phase 3 requirement. Record and carry forward; do not resolve here.

</domain>

<decisions>
## Implementation Decisions

### Baseline Comparison Target

- **D-01:** Pin Phase 2's authoritative comparison baseline to Phase 1's captured evidence at `21945440c9f2a15537ba878500a800d9e330eab0`. Justified by measurement, not convenience: the delta from that OID to current HEAD `ef786704` is two commits (`a8cba82d` publish evidence, `ef786704` record verification) and `git diff --name-only` between them returns files under `.planning/` exclusively — no source, test, tool-definition, or config file differs. The measured runtime tree is provably identical, so re-running the comprehensive green gate would re-derive a known result. — **Reversibility:** reversible — re-capturing at a different OID costs only the gate runtime.

- **D-02:** Re-pin policy is a **source-tree equality gate**. The pin to `21945440` stays valid for as long as the runtime tree is unchanged: drift confined to `.planning/`, docs, or other non-runtime paths preserves it. The first commit touching `src/`, `tests/`, tool definitions, or config invalidates the pin and forces a fresh baseline capture. Checkable with a path-scoped diff, and it is the same reasoning that justified D-01. This matters because concurrent sessions commit to this repository and GSD itself writes to `.planning/` at every workflow step.

- **D-03:** Phase 2's **binding comparison surface** — the Phase 1 artifacts a Phase 2 result must be diffed against — is `preservation.json` plus `environment.json` and `ci.json`. The surface probe JSONs and the catalog/test-result JSONs are deliberately **excluded** from the binding diff (see D-04 for how criterion 4 is met instead; catalog and test-level regression certification is Phase 5's TEST-01 charter).

- **D-04:** Criterion 4 (representative preserved custom tools still load and execute) is satisfied by **fresh probes that are not diffed against Phase 1's probe JSONs**. Phase 2 runs its own load-and-execute checks against the custom tools that `preservation.json` flags as at-risk, and they must pass on their own terms. This keeps the comparison surface exactly as scoped in D-03 while targeting execution proof at the assets actually in question rather than Phase 1's broader representative sample.

### Integration Stance

- **D-05:** Satisfy criterion 1's "isolated integration stage" by performing a **clean re-merge**: branch from the pre-merge fork parent `e0755067`, merge upstream `56adcfd9`, and resolve every conflict deliberately under the PROJECT.md rules. This independently re-derives the resolutions rather than inspecting their output, which is the only way to review decisions that were made outside this milestone. Chosen over auditing the landed merge in place, which would have taken `f81448f2`'s individual resolutions on faith. — **Reversibility:** reversible — the re-merge branch is throwaway by D-06.

- **D-06:** The re-merge is a **review instrument, not a replacement**. It lives on a throwaway branch and is never merged. Each disagreement with what `f81448f2` actually produced becomes a recorded finding classified as either "landed merge is correct" or "landed merge dropped or altered fork behavior"; only the second kind is a candidate for a corrective commit. This preserves the fork history and makes every correction individually reviewable and attributable. Explicitly rejected: making the re-merge authoritative, which would rewrite history atop `e0755067` and discard everything that landed after `f81448f2` — unacceptable blast radius on a repository with concurrent sessions. — **Reversibility:** one-way — the rejected alternative would have been history-rewriting; this decision is what keeps the phase reversible, and reversing it later means re-litigating the corrective commits already landed under it.

- **D-06a:** **Findings must be re-validated against the pinned tree before earning a corrective commit.** D-07's comparison is re-merge-tree vs `f81448f2`-tree — both immediately-post-merge trees — but **31 commits** separate `f81448f2` from the pinned baseline `21945440` (verified: `git merge-base --is-ancestor f81448f2 ef786704` → true; `git log --oneline --ancestry-path f81448f2..ef786704` → 31 commits). Several are post-merge repair work, notably `4b2c1c38` ("fix: harden sync, discovery, cache lifecycle, and docs") and eight Phase 1 `fix(01-*)` / `ci(01)` commits. A fork-only entry that `f81448f2` dropped may therefore already have been restored downstream. So: any finding classified as "landed merge dropped or altered fork behavior" is re-checked against the pinned tree; if the pinned tree already has it, the finding is recorded as **self-healed downstream** and no corrective commit is made. Without this, a corrective commit could re-add something already present or revert a later deliberate change. This keeps D-06's findings-only posture intact and makes the corrective set genuinely minimal.

- **D-06b:** Corrective commits from D-06 land on **`docs/gsd-codebase-map`** — the branch carrying the pin, Phase 1's evidence, and `git.json`. Naming it explicitly because two branches are live and concurrent sessions commit to this repository; "the current branch" is not a safe referent here.

- **D-07:** Scope is a **full re-merge with full-tree comparison**. Perform the complete merge so Git's own conflict set is re-derived independently rather than trusted from `f81448f2`'s record, then diff the whole resulting tree against `f81448f2`'s result — not only the conflicted paths. `git diff-tree --cc f81448f2 --name-only` reports 22 files carrying hand-resolved content, but that record is itself the artifact under audit; a full-tree comparison also catches a post-merge amendment or a change that entered outside conflict resolution.

- **D-08:** Resolution rule when re-deriving is **upstream-canonical plus fork-additive**, applying PROJECT.md's stated policy literally: for a definition present on both sides, upstream's version wins outright; a definition present only in the fork is retained; structural files (`default_config.py`, `_lazy_registry_static.py`) take the union of both sides' entries. This makes criterion 2 mechanically checkable — a re-merge that ever produces a net-removed fork-only entry is by definition a finding.

### Claude's Discretion

Two gray areas were surfaced and deliberately left to the researcher and planner, because the governing rules above already constrain them:

- **Canonical-def proof artifact** — D-08 fixes the resolution rule and D-07 fixes the comparison scope; the planner chooses the evidence format that demonstrates criterion 2 held (per-file diff of `src/tooluniverse/data/*.json` against upstream's copies, line-level accounting for the structural files, and the artifact layout that records it).
- **Custom-tool probe sample** — D-04 fixes the approach (fresh, non-diffed, targeted at `preservation.json` at-risk assets); the planner selects the specific fork-only tools, provided the selection is recorded and covers the assets the preservation inventory actually flags.

Also at the planner's discretion, consistent with Phase 1's D-07: normalize volatile values (timestamps, generated IDs, unstable remote ordering) when comparing, while keeping structural and semantic drift visible.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

ROADMAP.md carries no `Canonical refs:` line for Phase 2, so this list was assembled during discussion. The Phase 1 evidence files are the highest-value entries — no downstream agent will find them otherwise, and the entire Phase 2 audit hangs off `preservation.json`.

### Scope and preservation contract

- `.planning/PROJECT.md` — milestone constraints, protected architecture, staged integration policy, and the conflict-resolution rule D-08 applies ("dropping custom lines is unacceptable").
- `.planning/REQUIREMENTS.md` — Phase 2 requirements SYNC-01, SYNC-02, PRES-02.
- `.planning/ROADMAP.md` — Phase 2 boundary, goal, and the four observable success criteria.
- `.planning/phases/01-protected-sync-baseline/01-CONTEXT.md` — Phase 1 decisions carried forward, notably D-02 (fully green, no accepted debt), D-06 (tiered probe matrix), D-07 (normalized comparison).

### Phase 1 evidence — the binding comparison surface

All under `.planning/phases/01-protected-sync-baseline/evidence/21945440c9f2a15537ba878500a800d9e330eab0/`:

- `preservation.json` — **the central instrument.** 1,392 inventoried paths, 87 blockers, `blocking: true`. Every entry currently carries `class: other_review_required` with `must_survive: "fork delta retained pending staged synchronization"`. Phase 2's core output is re-classifying each as survived, superseded-by-upstream, or lost (criterion 3).
- `git.json` — frozen provenance: `head`, `merge_base`, `divergence`, `upstream_local_oid`/`upstream_remote_oid`, plus `pr161_ancestor: true` and `pr161_merge_oid` (carry to Phase 3 for SYNC-03).
- `environment.json`, `ci.json` — binding comparison surface per D-03.
- `stages.json` — the sixteen green gate stages Phase 1 certified.
- `SHA256SUMS` — tamper-evident checksum set over the evidence tree; D-01's pin keeps it meaningful.
- `probes/{python,cli,mcp_stdio,mcp_http,rest}.json`, `catalog.json`, `tests/{targeted,broad_offline,excluded_suites,summary}.json` — **context only, deliberately excluded from the binding diff** per D-03. Read for reference; do not treat a difference against them as a Phase 2 finding.

### Merge under audit — concrete Git facts

- Merge commit `f81448f2047a6f35bd552956a0d9990019a39eb1`, parents `e0755067ebe7cc5374f033c5c28160980c5eddfa` (fork) and `56adcfd9c299078d0c40fde642b0be006510ccf3` (upstream). Verified an ancestor of the pinned baseline on `docs/gsd-codebase-map`, with 31 commits in between — see D-06a, which depends on that gap.
- `git diff-tree --cc f81448f2 --name-only` reports 22 hand-resolved files. The ones that matter most against criterion 2: `src/tooluniverse/_lazy_registry_static.py`, `src/tooluniverse/default_config.py`, `src/tooluniverse/data/literature_search_tools.json`, `src/tooluniverse/data/uspto_tools.json`. The rest span `pyproject.toml`, `.gitignore`, nine adapter/core modules (`agentic_tool.py`, `base_tool.py`, `brenda_tool.py`, `cli.py`, `llm_clients.py`, `sabdab_tool.py`, `smcp.py`, `therasabdab_tool.py`, `tool_discovery_tools.py`, `tool_finder_embedding.py`, `unified_guideline_tools.py`) and five test files.

### Architecture and registration contracts

- `.planning/codebase/ARCHITECTURE.md` — shared-core execution paths; every transport converges on `ToolUniverse` in `src/tooluniverse/execute_function.py`.
- `.planning/codebase/STRUCTURE.md` — directory layout, notably `src/tooluniverse/data/` (JSON definitions), `src/tooluniverse/tools/` (generated per-tool modules), and the `plugin/skills/` symlinked workspaces.
- `.planning/codebase/CONVENTIONS.md` — validation commands and repository conventions.
- `docs/dev_docs/Interaction_Surfaces.md` — the discover → inspect → execute workflow the criterion-4 probes must exercise.
- `docs/superpowers/specs/2026-04-17-upstream-sync-design.md` — historical sync design, conflict strategy, protected paths, rollback intent. Treat revision counts and branch names as dated evidence to re-verify.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `scripts/capture_sync_baseline.py` (created by Phase 1 plan 01-01) already implements argv-only Git subprocesses, NUL-safe status/diff parsing, and detached-worktree isolation — the re-merge stage in D-05 should reuse this rather than reimplementing Git invocation.
- `tests/unit/test_sync_baseline_git.py` covers provenance, isolation, and worktree behavior; extend it rather than starting a parallel test module.
- Phase 1's evidence directory convention (`evidence/<full-OID>/` with sorted `SHA256SUMS`) is an established, tamper-evident layout that Phase 2's findings artifact can follow.
- Both Git remotes are configured and current: `origin` → `d33disc/upstream-tooluniverse`, `upstream` → `mims-harvard/ToolUniverse`.

### Established Patterns

- Git evidence uses full OIDs, porcelain/raw NUL records, explicit `cwd`, and checked subprocess exit status (Phase 1 `patterns-established`).
- Symlinks are inspected with `lstat`/`readlink` and **never traversed** during inventory. Three `plugin/skills/*-workspace` links were repaired in Phase 1 from authoritative PR #161 evidence; the re-merge must not destructively write through them.
- Use `uv` and the committed `uv.lock`; do not introduce another environment or package manager.
- Public transports route through the shared `ToolUniverse` core, so criterion-4 probes test surfaces over one execution path.

### Integration Points

- The re-merge stage (D-05) branches from `e0755067` in an isolated worktree — the same isolation mechanism Phase 1 established, not a checkout of the working branch.
- The findings artifact connects `preservation.json`'s 1,392 path entries to per-path classifications; its schema should keep the original `path` / `status` / `class` / `must_survive` fields so the two can be joined mechanically.
- **Concurrency hazard.** `.planning/` and all Git state live in `/Users/davis/code/ToolUniverse`, which concurrent Claude sessions share; they auto-commit each other's edits and interleave checkouts. Verify `git status` and the current branch immediately before any staging or commit. Untracked paths currently present and user-owned: `.planning/config.json` and `ralph-specs/fleet/results/` — leave both untouched.

</code_context>

<specifics>
## Specific Ideas

- "Isolated integration stage" is satisfied by a re-merge performed for review, not by a merge that gets shipped. The stage is an instrument; the fork history stays as it is.
- A finding is a **disagreement between the re-derived resolution and what landed** — not merely a difference from upstream. Upstream superseding a shared definition is the expected, correct outcome under D-08, not a defect.
- A net-removed fork-only entry is by definition a finding. That is the single mechanical check that makes criterion 2 falsifiable.
- Phase 1's "fully green, no accepted debt" posture (D-02) governs corrective commits: a real loss gets fixed, not recorded and carried.
- The delta justifying the D-01 pin should be re-derived, not trusted from this document — `git diff --name-only 21945440 <phase-2-start-OID> | grep -v '^\.planning/'` returning empty is the check.

</specifics>

<deferred>
## Deferred Ideas

- **PR #161 integration status** — already answered by Phase 1 evidence (`pr161_ancestor: true`, merge OID `16af425c053c306a658c96e254b4c4114338dd11`). Belongs to Phase 3 / SYNC-03; recorded in canonical refs so Phase 3 finds it immediately rather than re-deriving it.
- **Catalog and test-level regression certification** — `catalog.json` and the four `tests/*.json` result files were considered for Phase 2's binding comparison surface and excluded (D-03). Phase 5 owns this under TEST-01.
- **Full cross-surface certification** — Phase 2 runs targeted criterion-4 probes only (D-04). Certifying discover → inspect → execute across Python, CLI, MCP stdio/HTTP, and REST is Phase 5 / SURF-01.
- **Roadmap phrasing** — Phase 2's roadmap entry reads as "perform the integration" while the work is now an audit of an already-landed merge. The phase boundary and its four success criteria are unchanged and fully met by the decisions above; no roadmap edit is proposed or needed.

</deferred>

---

*Phase: 2-upstream-main-integration*
*Context gathered: 2026-08-06*
