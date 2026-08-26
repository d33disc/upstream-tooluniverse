# Phase 2: Upstream Main Integration - Research

**Researched:** 2026-08-06
**Domain:** Git merge audit/reconciliation on a large (~450K LOC) configuration-driven Python monorepo with a generated tool-registration chain
**Confidence:** HIGH (git facts independently re-verified this session; codebase mechanics read from source, not inferred)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Baseline Comparison Target**

- **D-01:** Phase 2's authoritative comparison baseline is Phase 1's captured evidence at `21945440c9f2a15537ba878500a800d9e330eab0`. The delta from that OID to current HEAD is `.planning/`-only (re-verified this session, see Verification below).
- **D-02:** Re-pin policy is a **source-tree equality gate**: the pin holds as long as no commit touches `src/`, `tests/`, tool definitions, or config. First such commit invalidates it.
- **D-03:** Phase 2's binding comparison surface is **`preservation.json` + `environment.json` + `ci.json`**. Surface probe JSONs and catalog/test-result JSONs are explicitly EXCLUDED from the binding diff (Phase 5 / TEST-01 owns those).
- **D-04:** Criterion 4 is satisfied by **fresh, non-baseline-diffed probes** against the custom tools `preservation.json` flags as at-risk. They must pass on their own terms, not be compared to Phase 1's probe JSONs.

**Integration Stance**

- **D-05:** Satisfy criterion 1 via a **clean re-merge**: branch from pre-merge fork parent `e0755067`, merge upstream `56adcfd9`, resolve every conflict deliberately under PROJECT.md's rules. This independently re-derives resolutions rather than trusting the landed merge's output.
- **D-06:** The re-merge is a **review instrument, not a replacement**. Throwaway branch, never merged. Each disagreement with what `f81448f2` produced is a recorded finding: "landed merge is correct" or "landed merge dropped/altered fork behavior." Only the second kind is a corrective-commit candidate.
- **D-06a:** Findings must be **re-validated against the pinned tree** before earning a corrective commit. 31 commits separate `f81448f2` from pinned `21945440` (verified again this session at current HEAD `fe4af922`: `f81448f2..fe4af922` = 34 commits, `f81448f2..21945440` = 31 commits — the 31-commit figure in CONTEXT.md is against the pin, still correct). A finding already fixed downstream is "self-healed" — no corrective commit.
- **D-06b:** Corrective commits land on **`docs/gsd-codebase-map`** (verified: this is the current branch of the main checkout at `/Users/davis/code/ToolUniverse`).
- **D-07:** Scope is a **full re-merge with full-tree comparison** — not only the 22 files `git diff-tree --cc` reports as hand-resolved.
- **D-08:** Resolution rule is **upstream-canonical plus fork-additive**: shared definitions -> upstream wins; fork-only definitions -> retained; structural files (`default_config.py`, `_lazy_registry_static.py`) -> union of both sides' entries. A net-removed fork-only entry is by definition a finding.

### Claude's Discretion

- **Canonical-def proof artifact** — evidence format demonstrating criterion 2 held (per-file diff of `src/tooluniverse/data/*.json` against upstream's copies, line-level accounting for structural files, artifact layout).
- **Custom-tool probe sample** — specific fork-only tools selected for criterion-4 probes, provided the selection is recorded and covers what `preservation.json` flags.
- **Volatile-value normalization** — carried forward from Phase 1's D-07 (normalize timestamps/generated IDs/unstable ordering; keep structural/semantic drift visible).

### Deferred Ideas (OUT OF SCOPE for this phase)

- **PR #161 integration status** — already answered by Phase 1 evidence (`pr161_ancestor: true`, merge OID `16af425c053c306a658c96e254b4c4114338dd11`). Belongs to Phase 3 / SYNC-03.
- **Catalog and test-level regression certification** (`catalog.json`, `tests/*.json`) — Phase 5 / TEST-01.
- **Full cross-surface certification** (Python/CLI/MCP stdio+HTTP/REST) — Phase 5 / SURF-01. Phase 2 runs only targeted criterion-4 probes.
- **Roadmap phrasing** — Phase 2's roadmap entry reads "perform the integration" while the actual work is an audit of an already-landed merge. No roadmap edit proposed; boundary and criteria are unchanged and met by the above.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SYNC-01 | Maintainer can integrate the selected upstream main revision on an isolated synchronization branch without incorporating unrelated local changes | D-05's re-merge branches from `e0755067` (pre-existing-worktree-changes-free) via `git worktree add --detach`, reusing `create_isolated_worktree()` from `scripts/capture_sync_baseline.py:749`. Containment at HEAD is already proven (see Verified Git Facts); the re-merge stage re-establishes it as a reviewable instrument. |
| SYNC-02 | Shared canonical tool definitions follow upstream while structural conflicts retain both upstream additions and fork-specific behavior | D-08's resolution rule mapped onto concrete files below (`default_config.py` = hand dict union; `_lazy_registry_static.py` = regenerate, don't hand-merge; `data/literature_search_tools.json` / `data/uspto_tools.json` = entry-level union by `name` key, not line-based). See Pitfall 1 and Pattern 2. |
| PRES-02 | Fork-specific code, tools, plugin assets, and registration contracts remain present and functional after the upstream-main integration | D-04's fresh probes against `preservation.json`-flagged custom tools; `tests/unit/test_registry_integrity.py` (one of the 22 hand-resolved files) already asserts every JSON `type` maps to a known lazy-registry class and every referenced tool name is defined — reuse it as a mechanical PRES-02 check. |

</phase_requirements>

## Summary

Phase 2 is not a merge — it is an audit of a merge that already landed. `git ls-remote upstream main` and local ancestry checks (re-verified this session, not trusted from a prior document) confirm `upstream/main` (`56adcfd9`) is an ancestor of current HEAD, having entered through merge commit `f81448f2` with parents `e0755067` (pre-merge fork) and `56adcfd9` (upstream). The work is: independently re-derive that merge's conflict resolutions on a throwaway branch, diff the resulting tree against what `f81448f2` actually produced, classify every disagreement, and correct only the disagreements that represent real loss and have not already been fixed by one of the 31 (soon-checked-to-current-HEAD: 34) commits that landed afterward.

The technical substance the planner needs is concentrated in two places. First, the merge's 22 hand-resolved files (`git diff-tree --cc f81448f2 --name-only`, re-verified this session at exactly 22) split into three risk tiers: a **generated** file (`_lazy_registry_static.py`) that should never be hand-merged — it should be regenerated via `tu build` (wraps `tooluniverse.generate_lazy_registry.main()`, `src/tooluniverse/cli.py:1722`) after the underlying source tree is resolved; a **hand-maintained structural dict** (`default_config.py`, category-name -> JSON-file-path) where D-08's "union" is a straightforward key union with near-zero collision risk; and two **JSON tool-definition arrays** (`data/literature_search_tools.json`, `data/uspto_tools.json`) where D-08's "union" must be entry-level by the `name` field, not trusted to Git's line-based merge driver, because both sides can independently add/reorder list entries in ways that produce syntactically valid but semantically wrong JSON (duplicate `name` values, or a silently dropped fork-only entry that never triggers a conflict marker). Second, `preservation.json` (1,392 paths, 87 blockers, all currently `class: other_review_required`) is the literal join key for criterion 3 — its `path`/`status`/`class`/`must_survive` fields must carry through to Phase 2's findings artifact unchanged so the two can be joined mechanically, per the existing Integration Points note in CONTEXT.md.

**Primary recommendation:** Reuse `scripts/capture_sync_baseline.py`'s `create_isolated_worktree()` and `run_git()` for the re-merge stage; resolve `default_config.py` and the two flagged JSON arrays by entry-level union keyed on `name`/dict-key (never trust Git's line merge for JSON arrays); regenerate `_lazy_registry_static.py` with `tu build` rather than hand-merging it; and drive PRES-02's mechanical check off the existing `tests/unit/test_registry_integrity.py`, which already asserts ghost-reference-free registration.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Re-merge execution (D-05) | Local Git / filesystem (isolated worktree) | — | Not an application-tier concern; a detached `git worktree` outside the working checkout, per `create_isolated_worktree()`. |
| Shared tool-definition resolution (SYNC-02) | Database / Storage (`src/tooluniverse/data/*.json` as the package's config/data layer) | API / Backend (`default_config.py` category map consumed by `ToolUniverse.load_tools()`) | JSON definitions are the canonical data layer; `default_config.py` is the backend-tier index into it. Both must resolve together — a JSON file present but not indexed in `default_config.py` is invisible to the catalog. |
| Registration-chain regeneration (`_lazy_registry_static.py`) | API / Backend (build-time codegen inside the package) | — | Not runtime application logic; a generated artifact consumed by `tool_registry.py`'s lazy loader at process start. |
| Custom tool execution proof (PRES-02, D-04) | API / Backend (`ToolUniverse.run_one_function()`) | — | All five transports converge here (`ARCHITECTURE.md`); fresh probes should call through this one path, not a transport-specific shortcut. |
| Findings artifact / classification join | Database / Storage (evidence JSON on disk, no live service) | — | A comparison instrument, not a running service; lives beside Phase 1's evidence tree. |

## Standard Stack

This phase installs no new application dependencies of its own. Its "stack" is repository tooling already present and pinned by the project (verified live in this session, not assumed):

### Core

| Tool | Version (verified live) | Purpose | Why Standard |
|------|--------------------------|---------|---------------|
| git | 2.55.0 | Worktree isolation, merge re-derivation, `diff-tree`, provenance | Already the project's sync mechanism (Phase 1's `capture_sync_baseline.py`) |
| uv | 0.12.1 (Homebrew) | Dependency sync/lock for the re-merge worktree | PROJECT.md: "do not introduce another package manager" |
| pytest | 8.4.2 (`.venv/bin/python -m pytest`) | Targeted regression + `test_registry_integrity.py` | Project's only test runner (`pytest.ini`) |
| ruff | 0.16.1 | Format/lint check on any corrective commit | PROJECT.md/CLAUDE.md: upstream uses `ruff format`; do not apply a global `~/.ruff.toml` |
| gh | 2.97.0 | Read PR/CI state if a corrective commit needs verification | Already used by Phase 1's evidence capture |

### Supporting

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `tu build` (`src/tooluniverse/cli.py:1715` `cmd_build`) | Regenerates `_lazy_registry_static.py` (Step 1: `tooluniverse.generate_lazy_registry.main()`) and coding-API wrappers (Step 2) | After the re-merge tree's Python tool adapters and JSON definitions are resolved — never hand-merge the generated registry file |
| `python3 src/tooluniverse/generate_lazy_registry.py` | Direct invocation of the same regeneration, if `tu` is not on PATH inside the isolated worktree | Equivalent to `tu build` Step 1 only |
| `jq` | Query `preservation.json` (523KB, 1,392 entries) and the git-facts JSON files without loading them into an agent's context wholesale | Any inspection of Phase 1 evidence |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Full re-merge (D-05, locked) | `git rerere` replay of the original merge's recorded resolutions | Rejected by the user's own decision (D-05 Q1) — replaying `f81448f2`'s resolutions would take them on faith, defeating the audit's purpose. Not offered as an alternative here; recorded only because a planner might otherwise reach for it. |
| Entry-level JSON union (this research) | Trust Git's textual merge driver on `data/*.json` | Git's line-based 3-way merge on a JSON array can silently produce two entries with the same `name` (duplicate) or auto-resolve a conflict by picking one side's insertion point without conflict markers, if the two sides inserted at different array positions. Neither failure mode raises a merge conflict — see Pitfall 1. |

**Installation:** Not applicable — no new packages. If the re-merge worktree needs a fresh environment: `uv sync` inside the isolated worktree (existing `uv.lock`, do not regenerate it unless upstream's `pyproject.toml` changes force a resolution — see Verified Git Facts, `pyproject.toml` is one of upstream's dependency-version changes).

**Version verification:** All versions above were captured live via `--version` in this repository's environment on 2026-08-06 — not looked up in a registry, since none of these are Python/npm packages this research is recommending; they are already-installed system/project tooling.

## Package Legitimacy Audit

**Not applicable in the standard sense.** This phase does not add new PyPI/npm/crates dependencies of its own; RESEARCH.md is not recommending any package the planner should `pip install`/`uv add`. However, the merge under audit itself changed `pyproject.toml` dependencies (upstream's `56adcfd9` vs the pre-merge fork `e0755067`, diffed live this session):

| Dependency change (fork -> merged) | Source | Verdict | Disposition |
|---|---|---|---|
| `mcp[cli]>=1.9.3` -> `mcp[cli]>=1.29.0,<2.0.0` | upstream `56adcfd9` | Already-installed upstream dependency, not researcher-recommended | Out of Phase 2's audit scope (dependency correctness is not one of the four success criteria) — note for Phase 5 / COMP-01 if install/test issues surface |
| `fastmcp>=2.12.3,<4.0.0` -> `fastmcp>=3.4.5,<4.0.0` | upstream `56adcfd9` | Same | Same |
| `google-generativeai>=0.7.2` removed | upstream `56adcfd9` | Same | Same |
| `openpyxl>=3.1.0`, `freesasa>=2.2.0`, `sphinx-reredirects>=0.1.5` added | upstream `56adcfd9` | Same | Same |

None of these are `[ASSUMED]` package names requiring a `checkpoint:human-verify` — they arrived through the upstream project's own release process (a public, long-lived, widely-used fork of `mims-harvard/ToolUniverse`), not through this research's own web-search-derived recommendation. **If** the planner's re-merge stage runs `uv sync` inside the isolated worktree and it fails to resolve, that is a Phase 2 finding to record (does not block criteria 1-4, which are about code content, not dependency resolution), and Phase 5 / COMP-01 is the correct owner of full install/compat certification.

## Architecture Patterns

### System Architecture Diagram — Re-merge Audit Flow

```text
┌───────────────────────────────────────────────────────────────────┐
│ Main checkout: /Users/davis/code/ToolUniverse, branch docs/gsd-... │
│  HEAD = fe4af922... (pinned comparison OID: 21945440...)          │
└───────────────────────────────┬───────────────────────────────────┘
                                 │  create_isolated_worktree(repo, "e0755067", worktree_dir)
                                 │  = git worktree add --detach <dir> e0755067
                                 ▼
┌───────────────────────────────────────────────────────────────────┐
│ Isolated detached worktree at pre-merge fork parent e0755067       │
│  (does NOT contain unrelated pre-existing dirty-worktree changes)  │
└───────────────────────────────┬───────────────────────────────────┘
                                 │  git merge 56adcfd9 (upstream/main)
                                 │  resolve every conflict per D-08:
                                 │   - shared def in data/*.json  -> upstream wins
                                 │   - fork-only def in data/*.json -> keep
                                 │   - default_config.py           -> key union
                                 │   - _lazy_registry_static.py    -> regenerate (tu build)
                                 ▼
┌───────────────────────────────────────────────────────────────────┐
│ Re-merge result tree (throwaway; NEVER merged into any branch)     │
└───────────┬───────────────────────────────────────────┬───────────┘
            │ full-tree diff vs f81448f2's tree (D-07)  │ fresh criterion-4
            ▼                                            │ probes against
┌───────────────────────────────┐                        │ preservation.json-
│ Disagreement list              │                        │ flagged custom tools
│  classify each: correct /      │                        │ (D-04, no baseline diff)
│  landed-merge-dropped-fork     │                        ▼
└───────────┬─────────────────┘                ┌───────────────────────┐
            │ D-06a: re-check against pinned    │ pass/fail per tool,   │
            │ tree (21945440). Present there?   │ own terms             │
            │  -> self-healed, no commit        └───────────────────────┘
            │  Absent there?
            ▼
┌───────────────────────────────┐
│ Corrective commit candidates   │──▶ land on docs/gsd-codebase-map (D-06b)
│ (real, unhealed loss only)     │
└─────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────────┐
│ Findings artifact: joins preservation.json's 1,392 path/status/    │
│ class/must_survive entries -> survived / superseded / lost         │
│ (criterion 3)                                                      │
└───────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure (new artifacts this phase produces)

```text
.planning/phases/02-upstream-main-integration/
├── 02-RESEARCH.md          # this file
├── 02-PLAN.md              # planner's output
├── evidence/                # follows Phase 1's evidence/<full-OID>/ convention
│   └── <re-merge-result-OID or descriptive dir>/
│       ├── remerge-diff.json       # D-07 full-tree diff, classified
│       ├── remerge-findings.json   # disagreement classification (D-06a applied)
│       ├── preservation-reclass.json  # joins preservation.json paths -> survived/superseded/lost
│       ├── probes/<tool>.json      # D-04 fresh, non-diffed criterion-4 probes
│       └── SHA256SUMS              # tamper-evident checksums, Phase 1's convention
```

### Pattern 1: Isolated worktree for a throwaway re-merge

**What:** Reuse `create_isolated_worktree(repo, fork_oid, worktree_dir)` from `scripts/capture_sync_baseline.py:749` rather than reimplementing `git worktree` invocation. It refuses to nest inside the original checkout (`target == root or root in target.parents` guard) and refuses to overwrite a non-empty target.
**When to use:** D-05's re-merge stage. This function already exists, is tested (`tests/unit/test_sync_baseline_git.py`), and takes an argv-only Git subprocess boundary (no shell interpolation).
**Example:**
```python
# Source: scripts/capture_sync_baseline.py:749-761 (read this session)
def create_isolated_worktree(
    repo: Path | str, fork_oid: str, worktree_dir: Path | str
) -> Path:
    """Create a detached worktree at *fork_oid* without touching the checkout."""
    root = Path(repo).resolve()
    target = Path(worktree_dir).resolve()
    if target == root or root in target.parents:
        raise ValueError("isolated worktree must not be inside the original checkout")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(target)
    run_git(["worktree", "add", "--detach", str(target), _oid(root, fork_oid)], root)
    return target
```
Call with `fork_oid="e0755067ebe7cc5374f033c5c28160980c5eddfa"` — the verified pre-merge fork parent.

### Pattern 2: Entry-level union for JSON tool-definition arrays

**What:** `src/tooluniverse/data/*.json` files are JSON arrays of tool-definition objects keyed by a `"name"` field (verified live this session for `literature_search_tools.json` — 6 agentic-tool entries — and `uspto_tools.json` — 8 patent-tool entries). D-08's "structural files take the union" rule, applied literally to these two files (the only two data/*.json files in the 22 hand-resolved set), means: parse both sides' arrays, index by `name`, then for each name present on both sides take upstream's object outright (per D-08's shared-definition rule) and for each name present only on the fork side keep it. Do NOT rely on Git's line-based 3-way merge to do this — a line merge on a JSON array only resolves cleanly when both sides touch disjoint line ranges; independent insertions at overlapping array positions can auto-resolve to a technically-valid but semantically-wrong result (duplicate names, or one side's insertion silently discarded) without ever raising a conflict marker.
**When to use:** Any of the 22 hand-resolved files that is a `data/*.json` array (currently 2: `literature_search_tools.json`, `uspto_tools.json`) plus the same check should be applied to any other `data/*.json` file the full-tree diff (D-07) surfaces as touched by both sides, even if it did not raise a Git conflict in the original merge.
**Example:**
```python
# Not sourced from repo code — a merge-safety pattern to apply, not existing
# tooling. Verify by reading each file's actual shape before writing this.
import json

fork_entries = {t["name"]: t for t in json.load(open(fork_path))}
upstream_entries = {t["name"]: t for t in json.load(open(upstream_path))}

merged = dict(fork_entries)          # start fork-additive
merged.update(upstream_entries)      # shared names: upstream wins (D-08)
result = list(merged.values())       # order is not semantically load-bearing
# but SHOULD be normalized (e.g. sorted by name) for a stable, diffable
# corrective commit — see Claude's Discretion: volatile-value normalization
```

### Pattern 3: Regenerate, don't hand-merge, generated registry files

**What:** `src/tooluniverse/_lazy_registry_static.py` declares itself `"""STATIC LAZY REGISTRY - GENERATED FILE. Do not edit manually. generated by generate_lazy_registry.py"""` (verified by reading the file, line 1-5) and is produced by AST discovery over the source tree (`build_lazy_registry()` in `tool_registry.py`, invoked by `generate_lazy_registry.py`). Phase 1's own preservation classifier (`classify_preservation_path()` in `capture_sync_baseline.py:853-884`) already tags this file `generated_asset`, distinct from `custom_code`.
**When to use:** After the re-merge worktree's Python tool-adapter files and `data/*.json` definitions are fully resolved, run `tu build` (or `python3 -m tooluniverse.generate_lazy_registry` equivalent) inside that worktree and let it overwrite `_lazy_registry_static.py` wholesale rather than manually resolving its Git conflict markers. Compare the regenerated file's key set against `f81448f2`'s version as the criterion-2 check for this specific file (a name present in the merged commit's version but absent from the regenerated one is a finding — either a class failed AST discovery or a source file was lost).
**Anti-pattern:** Hand-resolving conflict markers inside `_lazy_registry_static.py` line-by-line. It is dict-literal `json.dumps(..., sort_keys=True)` output; manual editing risks silent typos in module-name strings that only surface as an `ImportError` the first time that specific tool is invoked (lazy loading defers the failure past load time).

### Anti-Patterns to Avoid

- **Trusting `git diff-tree --cc`'s file list as the complete conflict surface:** D-07 already rejects this (locked decision), but it is worth stating why: `--cc` reports only paths where Git itself detected and recorded a conflict. A file that both sides modified in a way Git's merge driver auto-resolved (no conflict marker, e.g. two non-overlapping edits to the same JSON array) never appears in that list, yet can still contain a silently-dropped fork-only entry. Full-tree comparison (D-07) is the only way to catch it.
- **Comparing the re-merge to the pinned baseline (`21945440`) instead of to `f81448f2`:** D-06/D-07 specify the re-merge is compared against what `f81448f2` produced immediately post-merge, not the current pinned tree. The pinned tree only enters via D-06a's *second* check (has a finding already self-healed downstream?). Conflating these two comparisons will misattribute 31 commits' worth of legitimate post-merge repair work as "landed merge dropped fork behavior."
- **Re-running Phase 1's probe suite and diffing it against the captured `probes/*.json`:** D-03 explicitly excludes probe JSONs from the binding comparison surface, and D-04 explicitly requires criterion-4 probes to pass on their own terms rather than be diffed. A plan that re-introduces a probe diff silently expands scope beyond what CONTEXT.md locked.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Detached worktree isolation for the re-merge | A new `git worktree add` wrapper | `create_isolated_worktree()`, `scripts/capture_sync_baseline.py:749` | Already exists, already tested (`tests/unit/test_sync_baseline_git.py`), already guards against nesting inside the working checkout |
| Argv-only Git subprocess invocation | Shell-interpolated `git` calls or a new subprocess wrapper | `run_git()`, `scripts/capture_sync_baseline.py:634` | Established pattern (Phase 1's own "patterns-established"): argv-only, checked exit status, explicit `cwd`, byte-safe decode |
| Preservation-path classification for the findings artifact | A new taxonomy of path classes | `classify_preservation_path()`, `scripts/capture_sync_baseline.py:853` | The exact function that produced `preservation.json`'s `class` field — reusing it keeps the findings artifact joinable on identical semantics, not a re-interpretation |
| Detecting whether a JSON `type` field maps to a live registry class, or a referenced tool name is a ghost | A new registry-consistency checker | `tests/unit/test_registry_integrity.py` | Already collects every defined tool `name` from `data/*.json` and every referenced name from configs/skills/rules and asserts no ghost references; already validates JSON `type` -> lazy-registry class mapping |
| Regenerating the lazy tool registry after source changes | Hand-editing `_lazy_registry_static.py`'s conflict markers | `tu build` (`cmd_build`, `src/tooluniverse/cli.py:1705`) wrapping `tooluniverse.generate_lazy_registry.main()` | It is declared GENERATED in its own docstring; AST-discovers tool classes from source, so it is correct-by-construction once the source tree is resolved |
| Evidence-bundle tamper-evidence | A new checksum scheme | Phase 1's `SHA256SUMS` + `verify_checksums()` pattern (`scripts/capture_sync_baseline.py:1372`) and `evidence/<full-OID>/` directory convention | Already established, already the pattern CONTEXT.md's Reusable Assets section names as the one to follow |

**Key insight:** Almost everything this phase needs already exists in `scripts/capture_sync_baseline.py` and `tests/unit/test_registry_integrity.py` from Phase 1's own build-out. The planner's job is largely composition (call these existing functions against a new fork_oid / new comparison target) rather than new implementation. The one genuinely new piece of logic is the entry-level JSON-array union (Pattern 2), because Phase 1 never needed it — Phase 1 only *classified and inventoried* fork-vs-upstream deltas; it never had to *merge* two conflicting tool-definition arrays.

## Common Pitfalls

### Pitfall 1: Git's line-based merge silently mis-resolving a JSON tool-definition array

**What goes wrong:** Two sides independently add or reorder entries in a `data/*.json` array. If the insertions land at different array positions, Git's default 3-way text merge can resolve without a conflict marker, producing output that is valid JSON but has lost one side's entry, duplicated a `name`, or interleaved objects in a way that breaks nothing structurally but is wrong content.
**Why it happens:** Git's merge driver operates on text lines, not JSON semantics. A JSON array has no inherent line-alignment guarantee across two independently-edited copies.
**How to avoid:** For every `data/*.json` file the full-tree diff (D-07) shows touched on both sides — not just the 2 pre-flagged ones — parse both versions, union by `name` per D-08, and treat the result as authoritative regardless of what Git's automatic merge produced. Verify by counting: `len(merged) == len(set(fork_names) | set(upstream_names))` should hold exactly (no accidental duplicates, no accidental drops).
**Warning signs:** A `data/*.json` file where `json.load()` succeeds but two objects share the same `name`, or where a name known to exist in `preservation.json`'s inventory (fork-only, `class: custom_code`) is absent from the merged file.

### Pitfall 2: Comparing the wrong pair of trees

**What goes wrong:** Conflating "re-merge vs. `f81448f2`" (the actual audit comparison, D-07) with "re-merge vs. pinned baseline `21945440`" (D-06a's self-heal check, a *different* comparison against a *later* tree that already contains 31 commits of post-merge repair).
**Why it happens:** Both are legitimate comparisons in this phase and use similar tooling (`git diff`), making it easy to run the wrong one, especially since the pinned tree is what's checked out in the main working directory and is thus the "obvious" default.
**How to avoid:** Two explicit, separately-named comparison steps: (1) full-tree diff of the re-merge result against `f81448f2` itself (`git diff f81448f2 <remerge-branch>`) to produce the raw disagreement list; (2) for each disagreement classified as "landed merge dropped fork behavior," a second, separate check against `21945440` (`git show 21945440:<path>` or `git diff 21945440 <remerge-branch> -- <path>`) to determine self-healed status.
**Warning signs:** A finding classified as "landed merge dropped fork behavior" for a path that a `git log -- <path>` between `f81448f2` and `21945440` shows was touched by one of the 8 Phase 1 `fix(01-*)`/`ci(01)` commits or `4b2c1c38` — strong signal it was already repaired and should be self-healed, not re-fixed.

### Pitfall 3: Treating `_lazy_registry_static.py`'s merge conflict as a normal source conflict

**What goes wrong:** Hand-resolving conflict markers in a 722-line generated dict literal, introducing a typo in a module-name string value that Python's lazy import machinery won't catch until that specific tool name is actually invoked (see `ARCHITECTURE.md`'s "Lazy import failures are recorded per tool by `mark_tool_unavailable()`" — a broken entry degrades to a silent per-tool exclusion, not an import-time crash).
**Why it happens:** It looks like ordinary Python source in a diff/merge tool; nothing in Git's conflict UI flags it as generated.
**How to avoid:** Check the file's own header comment before resolving any conflict in it — every generated file in this codebase self-declares (`"""...GENERATED FILE. Do not edit manually..."""`). Regenerate via `tu build` after the source tree is settled instead.
**Warning signs:** A tool that appears correctly in `default_config.py`'s category map and has a valid `data/*.json` entry, but fails discovery/execution with an import error only at call time, not at catalog-load time.

### Pitfall 4: Assuming `preservation.json`'s `class: other_review_required` / `blocking: true` marks a defect

**What goes wrong:** Treating all 87 `blockers` entries (all `status: A` or `M`, all classified `other_review_required`, `must_survive: "fork delta retained pending staged synchronization"`) as problems to fix in Phase 2.
**Why it happens:** The word "blocking" sounds like a failure state.
**How to avoid:** Per Phase 1's own design, `blocking: true` on the whole `preservation.json` document meant "synchronization must not proceed until every one of these paths is classified" — it is a completeness gate for Phase 1's inventory, not a per-path defect flag. Phase 2's job (per criterion 3 and D-03) is to re-classify each of the 1,392 `paths` entries — most currently generic `other_review_required` — into survived / superseded-by-upstream / lost, using the same `path`/`status`/`class`/`must_survive` fields as the join key.
**Warning signs:** A findings artifact that reports "87 blockers found" as if that number itself is the phase's central metric, rather than reporting the reclassification outcome across all 1,392 paths.

## Code Examples

### Verifying containment and the merge commit's parentage (re-run before planning; do not trust a stale doc)

```bash
# Source: verified live this session, 2026-08-06, in /Users/davis/code/ToolUniverse
git ls-remote upstream main
# 56adcfd9c299078d0c40fde642b0be006510ccf3	refs/heads/main

git rev-list --left-right --count HEAD...upstream/main
# 127	0   (current HEAD; was 122 0 at pinned OID 21945440 per git.json — grows as fork commits land, upstream side stays 0)

git merge-base HEAD upstream/main
# 56adcfd9c299078d0c40fde642b0be006510ccf3   (merge-base == upstream head: full containment)

git log -1 --format='%H %P' f81448f2047a6f35bd552956a0d9990019a39eb1
# f81448f2047a6f35bd552956a0d9990019a39eb1 e0755067ebe7cc5374f033c5c28160980c5eddfa 56adcfd9c299078d0c40fde642b0be006510ccf3
# (merge commit, first parent = pre-merge fork, second parent = upstream)
```

### Verifying D-01/D-02's source-tree equality gate (re-runnable check, not a one-time fact)

```bash
# Source: verified live this session; returns EMPTY (gate holds) as of current HEAD fe4af922
git diff --name-only 21945440 HEAD | grep -v '^\.planning/'
# (no output — pin still valid; if this produces output, D-02 says re-capture the baseline before proceeding)
```

### Enumerating the 22 hand-resolved files (re-derive; don't hardcode the list from CONTEXT.md)

```bash
# Source: verified live this session
git diff-tree --cc f81448f2047a6f35bd552956a0d9990019a39eb1 --name-only | tail -n +2
# .gitignore
# pyproject.toml
# src/tooluniverse/_lazy_registry_static.py
# src/tooluniverse/agentic_tool.py
# src/tooluniverse/base_tool.py
# src/tooluniverse/brenda_tool.py
# src/tooluniverse/cli.py
# src/tooluniverse/data/literature_search_tools.json
# src/tooluniverse/data/uspto_tools.json
# src/tooluniverse/default_config.py
# src/tooluniverse/llm_clients.py
# src/tooluniverse/sabdab_tool.py
# src/tooluniverse/smcp.py
# src/tooluniverse/therasabdab_tool.py
# src/tooluniverse/tool_discovery_tools.py
# src/tooluniverse/tool_finder_embedding.py
# src/tooluniverse/unified_guideline_tools.py
# tests/integration/test_compose_tool.py
# tests/integration/test_tool_integration.py
# tests/tools/test_brenda_tool.py
# tests/unit/test_registry_integrity.py
# tests/unit/test_tool_composition.py
# (22 files, first line is the commit SHA itself, not a file)
```

### Querying `preservation.json` without loading 523KB into agent context (use `jq`, per shell-discipline)

```bash
# Source: pattern verified this session against the actual evidence file
EVID=".planning/phases/01-protected-sync-baseline/evidence/21945440c9f2a15537ba878500a800d9e330eab0"
jq '.paths | group_by(.class) | map({class: .[0].class, count: length})' "$EVID/preservation.json"
# custom_code: 512, documentation: 425, plugin_asset: 240, planning: 64, test: 45,
# other_review_required: 84, workflow: 5, skill: 8, generated_asset: 5, tool_definition: 4
# (sums to 1392, matches the top-level count)

jq '.paths[] | select(.path | startswith("src/tooluniverse/data/") and endswith(".json"))' \
  "$EVID/preservation.json" | jq -s 'length'
# 128  (data/*.json files the fork modified relative to upstream at the pinned OID)
```

### Regenerating the lazy registry after resolving the source tree

```bash
# Source: src/tooluniverse/cli.py:1705-1730 (cmd_build, read this session)
tu build
# Regenerating lazy registry...    (writes src/tooluniverse/_lazy_registry_static.py in place)
# Regenerating coding-API wrappers...  (writes to .tooluniverse/coding_api/ by default, --output to override)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Treat the roadmap phrasing "perform the upstream integration" literally | Treat it as "audit the integration that already landed" (established during `/gsd-discuss-phase`, "Framing finding (pre-discussion)" in `02-DISCUSSION-LOG.md`) | 2026-08-06, before any CONTEXT.md decision was written | Every plan task in Phase 2 must be an audit/reconciliation task, not a "run the merge" task — a plan that opens with "merge upstream/main into the working branch" is planning the wrong phase |

**Deprecated/outdated:** None specific to this phase's technical domain — this is a one-time audit exercise, not a evolving library/framework.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Entry-level union by `name` field (Pattern 2) is the correct interpretation of D-08's "structural files take the union of both sides' entries" as applied to `data/literature_search_tools.json` and `data/uspto_tools.json`. D-08's own text names `default_config.py` and `_lazy_registry_static.py` as "structural files"; the two JSON data files are grouped with them in CONTEXT.md's canonical-refs paragraph ("The ones that matter most against criterion 2") but D-08's decision text does not explicitly classify JSON data files as "structural" vs. ordinary shared-definition files. | Pattern 2, Pitfall 1 | If the planner instead applies pure "shared definition -> upstream wins outright" (D-08's other branch) to these two files, any fork-only entries inside them (e.g., a fork-added USPTO tool) could be silently dropped rather than unioned. Low risk of silent failure because `preservation.json`'s 128 modified `data/*.json` entries and `tests/unit/test_registry_integrity.py`'s ghost-reference check would likely surface a dropped tool name — but the corrective action ("union" vs "upstream wins") differs, so this should be confirmed with the user or resolved explicitly in the plan rather than left ambiguous. |
| A2 | "At-risk" custom tools for D-04's fresh probes should be drawn from `preservation.json`'s `custom_code`/`tool_definition`/`plugin_asset` classes generally, since no explicit `at_risk` boolean field exists in the schema (verified this session: the only keys present on path entries are `must_survive, new_mode, status, old_mode, symlink, path, new_oid, class, old_oid`). | Don't Hand-Roll, Assumptions | This is explicitly Claude's Discretion per CONTEXT.md, not a locked decision — the planner should pick a specific, recorded sample rather than defer further, but the exact selection criteria (e.g., "all 22 hand-resolved files' associated tools" vs. "a stratified sample across the 512 custom_code entries") is not dictated by any research finding here. |

## Open Questions

1. **Does `pyproject.toml`'s hand-resolved status (one of the 22 files) require re-derivation for this phase, or is it in-scope only if it affects tool registration?**
   - What we know: `pyproject.toml` diffs between the pre-merge fork and upstream show dependency version bumps (`mcp`, `fastmcp`) and additions (`openpyxl`, `freesasa`, `sphinx-reredirects`) — none of which are tool-definition or registration-chain concerns.
   - What's unclear: Whether D-07's "full-tree comparison" implies re-deriving `pyproject.toml`'s merge resolution with the same rigor as the JSON tool files, or whether it's out of scope because it doesn't touch criteria 2/3/4 (which are about tool definitions, preservation, and execution, not dependency declarations).
   - Recommendation: Include `pyproject.toml` in the full-tree diff mechanically (D-07 says full-tree, not "tool-files-only"), but do not treat a dependency-version disagreement as a criterion-2 finding unless it changes the runtime tool catalog; route dependency-resolution concerns to Phase 5 / COMP-01 per PROJECT.md's phase boundaries.

2. **Does the re-merge worktree need a working Python environment (for `tu build` and the criterion-4 probes) via `uv sync`, and does that risk drifting from the main checkout's `.venv`?**
   - What we know: `uv.lock` is committed and the project mandates using it (PROJECT.md constraint). The isolated worktree is a separate filesystem location from the main checkout's `.venv`.
   - What's unclear: Whether the planner should point the isolated worktree at the main checkout's existing `.venv` (fast, but conflates two Python environments across two working trees) or run a fresh `uv sync` inside the worktree (slower, cleaner isolation, matches the "isolated integration stage" spirit of criterion 1).
   - Recommendation: Fresh `uv sync` inside the isolated worktree — consistent with D-05's "isolated" framing and avoids any risk of the main checkout's environment being mutated by an audit exercise on a throwaway branch.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| git | All of D-05/D-06/D-07 (worktree, merge, diff-tree) | Yes | 2.55.0 | — |
| gh (GitHub CLI) | Optional CI/PR verification if a corrective commit needs it | Yes | 2.97.0 | Skip; not required by any of the four success criteria directly |
| uv | Re-merge worktree environment sync | Yes | 0.12.1 (Homebrew) | — |
| Python (project `.venv`) | `tu build`, pytest, criterion-4 probes | Yes | 3.14.6 system / `.venv` pytest 8.4.2 | — |
| ruff | Formatting check on any corrective commit | Yes | 0.16.1 | — |
| jq | Inspecting `preservation.json` and other evidence JSON without loading full files into context | Yes | present (`/opt/homebrew/bin/jq`) | — |

**Missing dependencies with no fallback:** None identified.

**Missing dependencies with fallback:** None identified — full toolchain is present in this environment.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4.2 (`.venv/bin/python -m pytest`), configured by `pytest.ini` |
| Config file | `pytest.ini` (repo root) — default run excludes `tests/tools`, `tests/examples`, `tests/api` and markers `slow`, `require_api_keys`, `network` |
| Quick run command | `.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -q` |
| Full suite command | `.venv/bin/python -m pytest` (respects `pytest.ini` default excludes; broader/tool suites need explicit `--ignore` removal or explicit path, per PROJECT.md's "explicitly select affected suites") |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|--------------------|-------------|
| SYNC-01 | Re-merge branch does not include unrelated pre-existing worktree changes | scripted check | `git diff --stat <remerge-branch> e0755067 -- . ':!<expected-merge-touched-paths>'` should show only paths the merge itself would touch, not the dirty-worktree paths Phase 1 recorded as pre-existing | N/A — new check, no existing test file |
| SYNC-01 | Isolated worktree creation is correct and non-destructive | unit | `.venv/bin/python -m pytest tests/unit/test_sync_baseline_git.py -q` | Yes — existing Phase 1 test covers `create_isolated_worktree` |
| SYNC-02 | Shared tool definitions match upstream; fork-only definitions retained; no net-removed fork-only entry | scripted diff + assertion | Entry-level union check per Pattern 2: `len(merged) == len(set(fork_names) | set(upstream_names))` for each touched `data/*.json` | N/A — new check, Wave 0 gap |
| SYNC-02 | No ghost tool-name references after regeneration | unit | `.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -q` | Yes — one of the 22 hand-resolved files, already covers this |
| PRES-02 | Preservation-flagged custom tools still load and execute | integration (fresh probes, D-04) | Per-tool: `tu info <ToolName>` (schema loads) then `tu run <ToolName> <minimal-args>` or `ToolUniverse.run_one_function()` equivalent, on the re-merge worktree | N/A — new probes, Wave 0 gap; selection is Claude's Discretion (see Assumptions A2) |
| PRES-02 | Registration chain (JSON -> registry -> lazy registry -> discovery -> execution) stable after regeneration | unit | `.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -q` | Yes |

### Sampling Rate

- **Per task commit:** Quick run — `tests/unit/test_registry_integrity.py` plus any unit test file touched by a corrective commit (e.g., `tests/unit/test_sync_baseline_git.py` if the worktree helper is extended).
- **Per wave merge:** Full suite as configured by `pytest.ini` default (`unit` + `integration` minus `slow`/`network`/`require_api_keys`), run inside the re-merge worktree before any finding is promoted to "verified."
- **Phase gate:** Before `/gsd-verify-work`, all four success criteria must have artifact evidence: (1) re-merge branch diff-stat proving containment, (2) entry-level union check + `test_registry_integrity.py` green, (3) findings artifact fully joined against all 1,392 `preservation.json` paths with no entry left unclassified, (4) fresh probe results for the selected custom-tool sample, all passing on their own terms.

### Wave 0 Gaps

- [ ] A scripted entry-level JSON union checker (Pattern 2) — does not exist yet; needed before SYNC-02 can be mechanically verified for `data/literature_search_tools.json` and `data/uspto_tools.json` (and any other `data/*.json` the full-tree diff surfaces).
- [ ] A findings-classification script that joins the re-merge full-tree diff against `f81448f2`'s tree, then against the pinned baseline (D-06a's two-step check) — does not exist yet; this is the phase's central new artifact.
- [ ] Fresh, non-diffed criterion-4 probe harness for the planner-selected custom-tool sample — Phase 1's `run_python_probe`/`run_cli_probe`/etc. in `capture_sync_baseline.py` are close analogues but were built for *baseline capture*, not *targeted fresh probing against a specific tool list*; likely reusable with a narrower tool filter rather than built from scratch.
- [ ] No framework install needed — pytest, ruff, uv, git, jq all present.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | This phase touches no auth surface; it is a repository/CI-local audit exercise |
| V3 Session Management | No | Same |
| V4 Access Control | No | Same |
| V5 Input Validation | Yes (narrow) | JSON tool-definition parsing (`json.load()` on `data/*.json` during the entry-level union, Pattern 2) — use `json.load()`/`json.loads()` only, never `eval()`; if any tool-definition schema needs re-validation post-merge, reuse the existing JSON-schema validation path in `src/tooluniverse/base_tool.py` (per `ARCHITECTURE.md`'s Cross-Cutting Concerns), not a hand-rolled validator |
| V6 Cryptography | No new crypto | No cryptographic operation is introduced; Phase 1's `SHA256SUMS` tamper-evidence pattern is checksumming (integrity), not confidentiality, and is reused unchanged (`shasum -a 256 -c` verification, as Phase 1's own verification did) |

### Known Threat Patterns for this domain

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| A merge silently reintroduces a previously-patched vulnerability (e.g., upstream's version of a shared file reverts a fork-only security fix that D-08 would otherwise discard as "just a diff") | Tampering (unintentional, via merge policy) | D-06's findings-only posture already catches this *if* the fork-only fix is recorded in `preservation.json` under a relevant class (most likely `custom_code`); the corrective-commit path exists precisely for this case. No new mitigation needed beyond executing D-06/D-06a faithfully — but the planner should be aware this is a real risk category, not purely a "did we drop a feature" question. |
| A hand-merged JSON tool-definition file introduces a duplicate `name` that changes which tool definition wins at runtime (last-registered-wins or first-registered-wins depending on load order) | Tampering | Pattern 2's exact-count assertion (`len(merged) == len(set(fork_names) \| set(upstream_names))`) catches duplicates deterministically before any corrective commit lands. |
| `tu build`'s regeneration is run against an unresolved/partial source tree (e.g., before all conflicts are settled), producing a `_lazy_registry_static.py` that reflects an inconsistent intermediate state | Tampering / Denial of Service (tools silently unavailable) | Sequence the re-merge stage strictly: resolve all source-file and JSON conflicts first, run `tu build` last, verify with `tests/unit/test_registry_integrity.py` before treating the worktree as a stable comparison point. |

Out of scope per PROJECT.md's explicit "Broad security/performance remediation" exclusion: `CONCERNS.md`'s catalogued items (pickle deserialization, SSRF in `file_download_tool.py`/`url_tool.py`, generic HTTP method exposure) are pre-existing and unrelated to the merge under audit — do not fold them into this phase's scope even if encountered while reading merge-touched files.

## Sources

### Primary (HIGH confidence — read/executed live this session)

- `/Users/davis/code/ToolUniverse` git repository (branch `docs/gsd-codebase-map`, HEAD `fe4af922`) — `git ls-remote`, `git rev-list --left-right --count`, `git merge-base`, `git log -1 --format='%H %P'`, `git diff-tree --cc`, `git diff --name-only` all executed live this session
- `.planning/phases/02-upstream-main-integration/02-CONTEXT.md` — all 8 locked decisions (D-01 through D-08), Claude's Discretion, Deferred Ideas
- `.planning/phases/02-upstream-main-integration/02-DISCUSSION-LOG.md` — alternatives considered, the "Framing finding" that reframed the phase
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/PROJECT.md` — requirement IDs, phase status, milestone constraints
- `.planning/phases/01-protected-sync-baseline/01-VERIFICATION.md` — Phase 1's pass status, known state inconsistencies (stale STATE.md metadata, `ci.json` head lag)
- `.planning/phases/01-protected-sync-baseline/evidence/21945440.../preservation.json`, `git.json`, `ci.json`, `stages.json`, `environment.json` — read/queried live via `python3`/`jq` this session
- `scripts/capture_sync_baseline.py` — read in full for `create_isolated_worktree`, `run_git`, `classify_preservation_path`, `collect_preservation_inventory` this session
- `src/tooluniverse/default_config.py`, `src/tooluniverse/_lazy_registry_static.py`, `src/tooluniverse/data/literature_search_tools.json`, `src/tooluniverse/data/uspto_tools.json`, `src/tooluniverse/generate_lazy_registry.py`, `src/tooluniverse/cli.py` (`cmd_build`), `tests/unit/test_registry_integrity.py` — read live this session
- `.planning/codebase/ARCHITECTURE.md`, `STRUCTURE.md`, `CONVENTIONS.md`, `CONCERNS.md` — read live this session
- `pyproject.toml`, `pytest.ini` — read live this session; `pyproject.toml` diffed against `e0755067`/`f81448f2` live this session

### Secondary (MEDIUM confidence)

- None — this phase's research is entirely a first-party codebase/git audit; no external documentation lookups were required or performed.

### Tertiary (LOW confidence)

- None.

## Metadata

**Confidence breakdown:**
- Standard stack (git/uv/pytest/ruff/gh): HIGH — versions verified live via `--version` in this exact environment
- Architecture / registration-chain mechanics: HIGH — read directly from source (`default_config.py`, `_lazy_registry_static.py`, `generate_lazy_registry.py`, `cli.py`), not inferred
- Merge-conflict resolution patterns (entry-level JSON union): HIGH confidence in the *mechanism* (verified file shapes, verified Git's line-merge limitation is a well-known general Git behavior), MEDIUM confidence in whether it is D-08's *intended* scope for these two specific files (flagged as Assumption A1 — recommend confirming with user or making explicit in the plan)
- Pitfalls: HIGH — each is grounded in a concretely verified file/mechanism in this repository, not a generic list

**Research date:** 2026-08-06
**Valid until:** This research is tied to specific commit OIDs (`f81448f2`, `e0755067`, `56adcfd9`, pinned baseline `21945440`) and is valid as long as D-01/D-02's source-tree equality gate holds. Re-verify the gate (`git diff --name-only 21945440 HEAD | grep -v '^\.planning/'` returns empty) before using this research if more than a few days have passed or if any `src/`/`tests/`/config commit has landed.
