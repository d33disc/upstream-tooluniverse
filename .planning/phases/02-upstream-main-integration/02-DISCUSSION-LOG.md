# Phase 2: Upstream Main Integration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-06
**Phase:** 2-upstream-main-integration
**Areas discussed:** Baseline comparison target, Integration stance

---

## Framing finding (pre-discussion)

Before any gray area was presented, codebase scouting established that `upstream/main` = `56adcfd9` is already an ancestor of the fork (`124 0` divergence, merge-base = upstream head), arriving via merge `f81448f2`. Verified against the live remote with `git ls-remote upstream main`, not a possibly-stale local ref. This reframed Phase 2 from "perform the merge" to "audit the merge that already landed" and was presented to the user before area selection.

## Area selection

Four gray areas were offered: Integration stance, Baseline comparison target, Canonical-def proof, Custom-tool probe scope. The user initially selected **Baseline comparison target** only, then after that area completed chose to explore further and added **Integration stance**. Canonical-def proof and Custom-tool probe scope were left to planner discretion (recorded in CONTEXT.md `### Claude's Discretion`).

---

## Baseline comparison target

### Q1 — Which revision is Phase 2's authoritative comparison baseline?

| Option | Description | Selected |
|--------|-------------|----------|
| Pin to 21945440 (recommended) | Treat Phase 1's captured evidence as authoritative; delta to HEAD is `.planning/` docs only | ✓ |
| Re-capture at current HEAD | Re-run the full baseline capture at `ef786704` | |
| Pin, but re-verify tree equality | Pin, and make tree-equality a re-runnable plan check | |

**User's choice:** Pin to 21945440
**Notes:** Evidence gathered before asking: `git diff --name-only 21945440 ef786704 | grep -v '^\.planning/'` returned empty — the two commits in between (`a8cba82d`, `ef786704`) touch only planning documentation.

### Q2 — Re-pin policy when the working commit drifts?

| Option | Description | Selected |
|--------|-------------|----------|
| Source-tree equality gate (recommended) | Pin holds while runtime tree is unchanged; first `src/`/`tests/`/definitions/config commit invalidates it | ✓ |
| Hard pin — freeze the commit | Execute against `21945440` in isolation regardless of branch drift | |
| Re-capture on any drift | Any commit at all invalidates the pin | |

**User's choice:** Source-tree equality gate
**Notes:** Motivated by the known concurrent-session hazard on this repository, plus the fact that GSD itself commits to `.planning/` at every workflow step — a whole-commit rule would re-run the green gate repeatedly.

### Q3 — Which Phase 1 evidence artifacts form the binding comparison surface?

| Option | Description | Selected |
|--------|-------------|----------|
| preservation.json (recommended) | 1,392 paths / 87 blockers — direct instrument for criterion 3 | ✓ |
| Surface probes (recommended) | Five probe JSONs — direct instrument for criterion 4 | |
| catalog.json + test results | Catalog and four test-result JSONs | |
| environment.json + ci.json | Runtime environment facts and CI matrix state | ✓ |

**User's choice:** preservation.json + environment.json/ci.json (multi-select)
**Notes:** Departed from the recommendation by excluding the surface probes, which left criterion 4 without a binding instrument. Surfaced as an explicit tension and resolved in Q4 rather than written into CONTEXT.md unaddressed.

### Q4 — How is criterion 4 satisfied with probes excluded?

| Option | Description | Selected |
|--------|-------------|----------|
| Fresh probes, not baseline-diffed | Phase 2 runs its own load/execute checks on preservation-flagged at-risk tools; pass on their own terms | ✓ |
| Defer execution proof to Phase 5 | Prove preservation structurally; leave execution to SURF-01 | |
| Add probes back to the comparison surface | Reverse the exclusion and diff under D-07 normalization | |

**User's choice:** Fresh probes, not baseline-diffed
**Notes:** Keeps the comparison surface as selected in Q3 while still producing direct criterion-4 evidence, targeted at the assets actually in question rather than Phase 1's broader sample.

---

## Integration stance

### Q1 — How is criterion 1's "isolated integration stage" satisfied?

| Option | Description | Selected |
|--------|-------------|----------|
| Audit in place on isolated worktree | Classify all 1,392 preservation paths in a detached worktree; take landed resolutions as given | |
| Re-merge on a clean stage | Branch from `e0755067`, re-merge `56adcfd9`, resolve deliberately, diff against what landed | ✓ |
| Audit in place, re-merge only conflicted files | Hybrid — re-derive only the paths where a resolution decision was made | |

**User's choice:** Re-merge on a clean stage
**Notes:** The expensive option, chosen deliberately. It is the only one that independently re-derives resolutions rather than inspecting their output.

### Q2 — Standing of the re-merge when it disagrees with what landed?

| Option | Description | Selected |
|--------|-------------|----------|
| Review instrument — findings only | Throwaway branch, never merged; real losses get targeted corrective commits | ✓ |
| Authoritative — re-merge replaces the landed merge | Rewrites history atop `e0755067`, discards four post-merge commits | |
| Findings only, but block on unresolved disagreement | Same as chosen, but any unclassifiable disagreement blocks the phase | |

**User's choice:** Review instrument — findings only
**Notes:** Evidence presented before asking: `git diff-tree --cc f81448f2 --name-only` lists 22 hand-resolved files, including `_lazy_registry_static.py`, `default_config.py`, `literature_search_tools.json`, `uspto_tools.json`. The authoritative option was rejected on blast radius given concurrent sessions.

### Q3 — Scope of the re-merge and its comparison?

| Option | Description | Selected |
|--------|-------------|----------|
| Full re-merge, focused comparison | Complete merge; concentrate line-level comparison on conflicted files | |
| Re-derive the 22 known files only | Trust `diff-tree --cc` as the definitive conflict set | |
| Full re-merge, full-tree comparison | Complete merge plus whole-tree diff against what landed | ✓ |

**User's choice:** Full re-merge, full-tree comparison
**Notes:** Widest net. Catches a post-merge amendment or a change that entered outside conflict resolution — cases the `--cc` record cannot show, since that record is itself the artifact under audit.

### Q4 — Resolution rule for shared definitions and structural files?

| Option | Description | Selected |
|--------|-------------|----------|
| Upstream-canonical + fork-additive (recommended) | Upstream wins for shared definitions; fork-only retained; structural files take the union | ✓ |
| Upstream-canonical, fork wins on conflict | Fork version wins where it encodes deliberate divergence | |
| Union everything, flag every collision | No automatic precedence; every same-name collision is a finding | |

**User's choice:** Upstream-canonical + fork-additive
**Notes:** PROJECT.md's stated policy applied literally, which makes criterion 2 mechanically checkable — a net-removed fork-only entry is by definition a finding.

---

## Claude's Discretion

- **Canonical-def proof artifact** — the resolution rule (D-08) and comparison scope (D-07) are locked; the evidence format demonstrating criterion 2 is the planner's call.
- **Custom-tool probe sample** — the approach (D-04) is locked; the specific fork-only tools are the planner's call, provided the selection is recorded and covers what `preservation.json` flags.
- **Volatile-value normalization** — carried forward from Phase 1's D-07.

## Deferred Ideas

- **PR #161 integration status** — already answered by Phase 1 evidence (`pr161_ancestor: true`, merge OID `16af425c`); belongs to Phase 3 / SYNC-03. Recorded in CONTEXT.md canonical refs so Phase 3 finds it without re-deriving.
- **Catalog and test-level regression certification** — considered for the binding comparison surface and excluded; Phase 5 / TEST-01 owns it.
- **Full cross-surface certification** — Phase 5 / SURF-01.
- **Roadmap phrasing** — Phase 2's entry reads as "perform the integration" while the work is an audit. Boundary and success criteria are unchanged and met; no roadmap edit proposed.
