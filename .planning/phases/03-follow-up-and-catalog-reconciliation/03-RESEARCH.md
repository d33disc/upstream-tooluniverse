# Phase 3: Follow-up and Catalog Reconciliation - Research

**Researched:** 2026-08-06T20:31:44.000Z (Wed)
**Domain:** Internal registry/codegen reconciliation (git ancestry verification, generated-vs-source drift, catalog integrity) — no external library research applies
**Confidence:** HIGH (all load-bearing claims verified this session by reading source, running read-only git commands, or diffing tracked files against the working tree)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Treat SYNC-03 as verify-and-record, not a separate merge/integration stage. Phase 1's `git.json` already records `pr161_ancestor: true` with merge OID `16af425c053c306a658c96e254b4c4114338dd11`. Re-verified live against current HEAD in this discussion: `git merge-base --is-ancestor 16af425c... HEAD` still returns true, so nothing that landed since Phase 1 (including all of Phase 2's corrective commits) invalidated the ancestry. SYNC-03 is satisfied by re-deriving and publishing this proof. Reversibility: reversible — if re-verification had failed, the phase would pivot to an actual integration stage; it did not.
- **D-02:** If re-verification at planning/execution time contradicts this (ancestry no longer holds, e.g. a history rewrite), stop and treat it as a planning-time finding, not something to silently work around.
- **D-03:** Audit is two-tiered, not a from-scratch manual pass over all ~2,300 tools. Tier 1: every tool touched by Phase 2's actual merge — the 22 `git diff-tree --cc f81448f2` hand-resolved files plus the 213 both-sides `data/*.json` files from the union sweep — gets explicit six-link verification (JSON definition -> implementation -> catalog config -> lazy metadata -> generated module -> tests). Tier 2: a full mechanical pass via `tests/unit/test_registry_integrity.py`-style automated checks across the entire catalog. Reversibility: reversible — tiering can be widened if Tier 2 surfaces problems concentrated outside Tier 1's scope.
- **D-04:** `tests/unit/test_registry_integrity.py` (already exercised repeatedly this session, always green post-Phase-2) is the canonical mechanical check — extend it rather than writing a parallel registry-integrity script.
- **D-05:** Regeneration is mechanical and auto-run; only genuine name collisions need review. PROJECT.md states hand-edited partial registries are "not a valid synchronized state" and regeneration (`tu build` / `generate_lazy_registry.py`) is the expected, low-risk mechanism — auto-run it and treat a clean regeneration as self-resolving for stale entries. A duplicate public name across two different tool definitions is a different, higher-risk class (an actual naming collision) and follows Phase 2's D-06 pattern: recorded as a finding, resolved only after review, never silently reconciled. Reversibility: reversible for regeneration (deterministic build step); the review gate for genuine collisions is what keeps it that way.
- **D-06:** Investigate the concurrent uncommitted regeneration before building on it or ignoring it. `src/tooluniverse/tools/*.py` (2,660 files) and `.tool_metadata.json` are modified and uncommitted, with an mtime predating this session's own Phase 2 work — another concurrent session's in-progress output. Do not silently commit, revert, or build on this state. Reversibility: the investigation itself is free; touching the files before investigating would not be.

**Research note on D-05 (not part of the verbatim CONTEXT.md block above):** this research found mechanically-verified evidence that qualifies "regeneration is mechanical and auto-run" — see "Concurrent State Investigation" and "Root cause" below. Regeneration on THIS machine is not credential-neutral; "auto-run" needs a precondition (diff-before-commit guard), not a literal one-shot `tu build`.

### Claude's Discretion

- Exact evidence-artifact format for the six-link chain proof (per-tool table vs. aggregate pass/fail counts vs. both) — follow Phase 1/2's established `evidence/<oid>/` + `SHA256SUMS` convention.
- Whether Tier 1's audit and Tier 2's mechanical pass run as one combined script or two — whichever keeps the artifact schema joinable, per Phase 2's `join_preservation` precedent (findings.json's verdict as the primary signal, not re-derived comparisons).
- Ordering of PR #161 verification vs. the registration-chain audit — SYNC-03's re-verification is cheap and has no dependency on CAT-01/CAT-02, so it can run first, last, or in parallel.

### Deferred Ideas (OUT OF SCOPE)

- **Full cross-surface certification** (Python, CLI, MCP stdio/HTTP, REST) — Phase 3 only certifies catalog loading and discovery (`grep_tools`/`get_tool_info`). Full surface certification is Phase 5 / SURF-01.
- **Execution-core refactoring** — CONCERNS.md's "Monolithic execution core" and "Broad exception suppression" tech-debt entries are out of this milestone's scope per PROJECT.md.
- **The pre-existing `execute_function.py` async-context bug** (`RuntimeError: no running event loop` in `ToolCallable.__call__`) — already routed to standalone follow-up task `task_43fff30b`, not folded into Phase 3.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| SYNC-03 | Maintainer can determine whether historical PR #161 is already represented by the selected upstream revision and, when needed, integrate it as a separate verified stage | Re-verified live: `git merge-base --is-ancestor 16af425c053c306a658c96e254b4c4114338dd11 HEAD` returns true against current HEAD `20a03aaea22d29b09336001480264ee162f5430b` `[VERIFIED: git merge-base, this session]`. D-01's verify-and-record posture holds; no integration stage needed. See "PR #161 Verification" below. |
| CAT-01 | Every synchronized or preserved tool has a consistent six-link registration chain from canonical JSON definition through implementation, catalog configuration, lazy metadata, generated public module, and tests | Six links mapped to concrete files this session (see "Architecture Patterns"). Existing `tests/unit/test_registry_integrity.py` covers 2 of 6 links (JSON name/type <-> lazy-registry class). A concrete, currently-committed drift example (`OxO_*` orphaned/duplicate definition) and the credential-gated codegen hazard (below) both give the planner real, verified test cases to extend the mechanical pass against. |
| CAT-02 | The synchronized loadable catalog exposes new upstream and preserved custom tools through `grep_tools` and `get_tool_info` without stale or duplicate registry entries | Found a live, currently-committed duplicate-name case (`OxO_get_ontology_mappings` / `OxO_search_ontology_mappings` defined in both `src/tooluniverse/data/oxo_tools.json` and `src/tooluniverse/data/broken_apis/oxo_tools.json`) — exactly the D-05 "genuine collision, needs review" class, verified live in the current catalog, not hypothetical. See "Common Pitfalls". **Additional constraint found this session:** `grep_tools`/`get_tool_info` read the same credential-gated `all_tool_dict` collection the codegen scripts do (verified at source level, see "Root cause"), so the ~80+ tools gated by missing API keys on this machine cannot have their schema inspected via `get_tool_info` here — the plan's "representative tool" sample for this criterion must exclude credential-gated tools or explicitly scope around them. |
</phase_requirements>

## Summary

This phase has almost no external-library research surface — it is entirely about reconciling this repository's own generated-vs-source state after Phase 2's merge. The two things that matter are (1) re-confirming a single git-ancestry fact for SYNC-03, and (2) auditing/repairing the six-link tool registration chain for CAT-01/CAT-02 using the test infrastructure and audit scripts Phase 1/2 already built.

The highest-value finding of this research session is **not** in either of those — it is in the mandatory concurrent-state investigation (D-06). Direct evidence (reading `generate_coding_api.py`, `generate_tools.py`, and `execute_function.py`'s `load_tools()`, plus diffing the dirty working tree against HEAD) shows that **both of this repo's tool-wrapper generator scripts call `ToolUniverse().load_tools()` with no override, and `load_tools()` silently excludes any tool whose `required_api_keys` are not satisfied in the running shell's environment.** On this machine, at least 8 specialty API-key families (Addgene, AlphaGenome, BRENDA, BioGRID, CLUE, ClusPro, DisGeNET, ESM — none of whose keys exist in `.tooluniverse/.env.1password`, and there is no `.env.local` at all) are unmet, and the dirty, uncommitted `tools/__init__.py` in the working tree is missing at least 80 tools that are present in the currently-committed HEAD as a direct, reproducible consequence. This means **D-05's "regeneration is mechanical and auto-run" is not safe to execute verbatim on this machine** — running `tu build` (or `generate_coding_api.py`/`generate_tools.py` directly) without first loading every available credential would regress the catalog, and even with every available credential loaded, 8+ tool families whose keys this project does not currently hold would still be dropped from the generated module tree if committed. The planner needs to build a precondition and a diff-before-commit gate around D-05, not treat regeneration as a pure formatting step.

**Primary recommendation:** Do not commit or build on the dirty working tree. Treat regeneration as credential-environment-sensitive, not purely mechanical: before any regeneration step, diff its `tools/__init__.py` tool count against the currently-committed count, and treat any *reduction* as a hard-stop finding requiring human review (not an auto-apply), while treating *additions/renames consistent with Phase 2's merged JSON changes* as the expected self-resolving case D-05 describes.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| PR #161 ancestry verification | Database / Storage (git object graph) | — | Pure git history query; no application-tier code involved. |
| Six-link registration chain audit | API / Backend (package internals) | Database / Storage (JSON definitions as source-of-truth) | The chain spans JSON config -> Python implementation -> catalog config -> generated code -> tests, all inside the `tooluniverse` package; no browser/CDN tier exists in this project. |
| Catalog regeneration (`tu build`) | API / Backend | — | Runs entirely in-process (`ToolUniverse.load_tools()` + codegen scripts); output lands in package source tree. |
| Discovery certification (`grep_tools`/`get_tool_info`) | API / Backend | CLI / MCP surface (thin wrappers) | Discovery primitives execute inside `ToolUniverse`; CLI/MCP/HTTP surfaces are transport-only per `docs/dev_docs/Interaction_Surfaces.md` and are explicitly out of scope for Phase 3 (deferred to SURF-01). |

## Concurrent State Investigation (D-06) — Required Findings

**Status: STALE, not active. Output is INCOMPLETE relative to current HEAD. Direct conflict with Phase 3's planned regeneration step identified and characterized. Root cause identified and reproducible.**

### Is the other session still active?

No, with high confidence. Evidence gathered read-only this session (2026-08-06T20:31:44Z, main checkout `/Users/davis/code/ToolUniverse`, branch `docs/gsd-codebase-map`):

- Newest mtime among all 2,661 modified `src/tooluniverse/tools/*.py`/`.tool_metadata.json` files is `2026-08-06T17:54:56` (`_lazy_registry_static.py`); the bulk cluster is `17:22:42`-`17:32:30`. At the time of this check (`20:31:44`), that is **~2h37m of no further writes** to any file in that set `[VERIFIED: stat -f %m, this session]`.
- No `lsof` handles open under `src/tooluniverse/tools/` `[VERIFIED: lsof +D, this session]`.
- No `.pid`/`.lock` files at repo root `[VERIFIED: ls, this session]`.
- This session's own commits (Phase 2 close-out, `d08ae18d` through `20a03aae`, latest at `2026-08-06T20:14:31-04:00`) landed entirely on top of / after the dirty files' mtimes, and none of them touched or reverted the dirty `tools/*.py` set — confirming the dirty state has persisted, untouched, across at least 6 of this session's own commits `[VERIFIED: git reflog, git log, this session]`.
- Several `claude` CLI processes are running on the machine (`ps aux`), but none show a working directory or command line tied to `/Users/davis/code/ToolUniverse`'s main checkout specifically (all visible invocations reference other session/plugin state) `[VERIFIED: ps aux, this session — inconclusive on cwd but no positive evidence of an active writer]`.

**Conclusion: the regeneration that produced this dirty state ran once, ~3 hours before this research, and stopped. Nothing is currently writing to these files.**

### Is its output correct and complete?

**No.** Diffing the working tree's `tools/__init__.py` (2,659 imports) against the currently-committed HEAD's `tools/__init__.py` (2,737 imports) shows:

- **80 tool imports present in HEAD are missing from the dirty working tree.** A full sample check of the first 30 (all of them) confirms every one of them has `required_api_keys` set in its `src/tooluniverse/data/*.json` definition, e.g.: `Addgene_get_plasmid -> ['ADDGENE_API_KEY']`, `BRENDA_get_enzyme_info -> ['BRENDA_EMAIL','BRENDA_PASSWORD']`, `DisGeNET_search_disease -> ['DISGENET_API_KEY']`, `ESM_fold_protein -> ['ESM_API_KEY']`, `BioGRID_get_interactions -> ['BIOGRID_ACCESS_KEY']`, `CLUE_search_compounds -> ['CLUE_API_KEY']`, `AlphaGenome_predict_interval -> ['ALPHA_GENOME_API_KEY']`, `ClusPro_submit_peptide_docking -> ['CLUSPRO_USERNAME','CLUSPRO_API_SECRET']` `[VERIFIED: src/tooluniverse/data/{addgene,brenda,disgenet,esm,biogrid,clue,alphagenome,cluspro}_tools.json, this session]`.
- None of these 8 key families are present in `.tooluniverse/.env.1password` and there is no `.tooluniverse/.env.local` file in the repo at all `[VERIFIED: grep against both files, this session]`.
- 2 tools (`SEC_EDGAR_get_company_submissions`, `SEC_EDGAR_search_filings`) appear in the working tree's `__init__.py` but not HEAD's — but the `.py` files themselves are tracked at HEAD (`git ls-tree HEAD` resolves a blob), meaning this is HEAD's `__init__.py` under-including an already-defined, already-generated, key-less tool, not the working tree over-including something invalid. This is a **separate, pre-existing drift already present in the committed baseline**, unrelated to the concurrent session — a legitimate CAT-01 finding in its own right.
- The `src/tooluniverse/_lazy_registry_static.py` diff is exactly one line (a trailing-comma formatting difference from a different `ruff`/formatter version) — cosmetic only, `[VERIFIED: git diff, this session]`.

**Conclusion: the dirty output is a regression relative to HEAD for the reason below, and must not be trusted as a drop-in replacement.**

### Root cause (verified mechanically, exact source read — not inferred from documentation)

Both of the repo's two tool-wrapper generator scripts call `tu.load_tools()` with default arguments and then iterate `tu.all_tool_dict`/`tu.all_tools` — i.e., **the generated file tree is a function of which tools loaded successfully given the running shell's credentials, not purely a function of `data/*.json`:**

- `src/tooluniverse/generate_coding_api.py::main()`, line 269-270: `tu = ToolUniverse(); tu.load_tools()` `[VERIFIED: src/tooluniverse/generate_coding_api.py:269-270, this session]`.
- `src/tooluniverse/generate_tools.py::main()`, line 614-615: `tu = ToolUniverse(); tu.load_tools()` `[VERIFIED: src/tooluniverse/generate_tools.py:614-615, this session]`.
- `ToolUniverse.load_tools()` (`src/tooluniverse/execute_function.py:895-936`) has no parameter to force-include tools whose keys are missing — its filtering parameters (`exclude_tools`, `exclude_categories`, `include_tools`, `include_tool_types`, `exclude_tool_types`) are all selection controls, not a credential-bypass `[VERIFIED: src/tooluniverse/execute_function.py:895-936 signature, this session]`.
- **The exclusion mechanism itself was read directly, not assumed from CLAUDE.md's prose.** Inside the tool-loading loop, before a tool is appended to the list that becomes `self.all_tools`:

  ```python
  # Source: src/tooluniverse/execute_function.py:1289-1300, read verbatim this session
              # Check API key requirements
              if "required_api_keys" in each:
                  all_keys_available, missing_keys = self._check_api_key_requirements(
                      each
                  )
                  if not all_keys_available:
                      all_missing_keys.update(missing_keys)
                      self._excluded_api_key_tools[tool_name] = list(missing_keys)
                      self.logger.debug(
                          f"Skipping tool '{tool_name}' due to missing API keys: {', '.join(missing_keys)}"
                      )
                      continue
  ```

  and, at the end of the same method:

  ```python
  # Source: src/tooluniverse/execute_function.py:1339, read verbatim this session
          self.all_tools = dedup_all_tools
  ```

  The `continue` at line 1300 fires *before* the tool is appended to `dedup_all_tools`/`tool_name_list` (the append happens earlier in the loop, lines 1263-1270, only for tools that survive this check), and `dedup_all_tools` is assigned directly to `self.all_tools` at line 1339 with no re-inclusion step. This is the exact collection both generator scripts iterate (via `tu.all_tool_dict`/`tu.all_tools`) — **the mechanism is confirmed at the source-code level, not inferred from correlation or from documentation** `[VERIFIED: src/tooluniverse/execute_function.py:1263-1270, 1289-1300, 1339, this session]`.

**Same mechanism also gates `grep_tools`/`get_tool_info` (CAT-02 discoverability, not just codegen):**

```python
# Source: src/tooluniverse/tool_discovery_tools.py:99, 114, 281, 311, 429, 581, 813 — read this session
# every discovery primitive iterates self.tooluniverse.all_tool_dict directly
```

`[VERIFIED: src/tooluniverse/tool_discovery_tools.py, grep + read this session]`. This means the same ~80+ credential-gated tools identified above are, on this machine, excluded from `grep_tools`/`get_tool_info`'s underlying data source exactly as they are from codegen — **not a separate, independent risk, but the same root cause surfacing in two different places CAT-01 and CAT-02 both care about.**

The codebase already has partial, documented mitigation for the *discovery-layer* symptom (not the codegen symptom): a fix tagged `Fix-R13D-1` makes `grep_tools`'s name-substring fallback and `GetToolInfoTool._not_found_error` check `_excluded_api_key_tools` and return `"requires API key(s) not set: ..."` instead of a bare, misleading `"not found"` when a gated tool is queried by exact/near-exact name `[VERIFIED: src/tooluniverse/tool_discovery_tools.py:220-228, 742-760, this session — comments explicitly document this was "confirmed live" as a real bug: 'tu grep uspto returned 0 matches with no hint that USPTO tools exist but are gated']`. This softens but does not remove the CAT-02 gap: `get_tool_info` for a gated tool returns `{"name": tool_name, "error": "requires API key(s) not set: ..."}` — a helpful error, but **not the tool's schema** `[VERIFIED: src/tooluniverse/tool_discovery_tools.py:808-819, this session]`. CAT-02's success criterion ("inspect their exact schemas with `get_tool_info`") is genuinely unsatisfiable for these tools on this specific machine, with a graceful rather than silent failure mode.

**Planning implication for CAT-02:** when the plan selects "representative upstream and custom tools" to certify via `grep_tools`/`get_tool_info`, it must exclude (or separately caveat) any tool whose `required_api_keys` are unmet in the execution environment — sampling one of the ~80+ gated tools would make the phase's own success-criteria check fail for a reason unrelated to catalog integrity.

**There are also two separate, diverged generator implementations** (`generate_coding_api.py`, docstring "Run via `tu build`"; and `generate_tools.py`, docstring "Minimal tools generator — one tool, one file", mtime `2026-08-03T17:58`) `[VERIFIED: diff of both files, this session]`. Only `generate_tools.py` is wired to the public `tu build` CLI subcommand (`cli.py::cmd_build`, calling `tooluniverse.generate_tools.main(output_dir=...)`), and `tu build`'s **default output directory is `.tooluniverse/coding_api/` — a workspace-local directory, not `src/tooluniverse/tools/`** `[VERIFIED: src/tooluniverse/cli.py:1705-1741, this session]`. This means the dirty `src/tooluniverse/tools/*.py` state was **not** produced by a bare `tu build` invocation; it required either an explicit `--output src/tooluniverse/tools` override or a direct call to `generate_coding_api.py` (or an older/different codepath). Which script and invocation actually produced the dirty state could not be determined mechanically from the working-tree diff alone — this is an open question for the planner/human (see Open Questions).

### Does it conflict with or supersede Phase 3's planned work?

**Yes, directly.** CAT-01/CAT-02 explicitly require "no missing... names" and "no stale or duplicate registry entries" in the six-link chain, and D-05 calls regeneration "mechanical and auto-run." The concurrent dirty state is direct counter-evidence that on this machine, mechanical regeneration silently drops real tools. If Phase 3's regeneration step is executed without first (a) discarding or backing up the existing dirty state, and (b) adding a tool-count/name-set regression check, it risks either inheriting this 80-tool regression or masking it by committing over it.

**Recommendation for the planner:** Add an explicit Wave-0/Tier-2 task: "Diff any regeneration output's `tools/__init__.py` import set against the current HEAD's import set before considering it a candidate for commit; any name present in HEAD but absent from the regenerated output is a blocking finding, not a self-resolving staleness case." Do not touch, stash, revert, or commit the existing dirty `src/tooluniverse/tools/*.py`/`.tool_metadata.json` state as part of research — it remains exactly as found, for the planner/human to decide whether to discard (`git restore` — a decision, not a research action) or investigate further before Phase 3 begins its own regeneration pass.

## PR #161 Verification (SYNC-03)

Re-run live this session, read-only, against current HEAD (not the pin used in Phase 1):

```
$ git rev-parse HEAD
20a03aaea22d29b09336001480264ee162f5430b
$ git merge-base --is-ancestor 16af425c053c306a658c96e254b4c4114338dd11 HEAD; echo $?
0   # true — 16af425c is an ancestor of current HEAD
```

`[VERIFIED: git merge-base --is-ancestor, this session, exit 0]`. This confirms D-01/D-02: SYNC-03 remains a verify-and-record requirement, not an integration stage. The planner should have the phase's plan reproduce this exact command against the HEAD it will actually operate from (not assume this research's HEAD stays current — the phase may execute after further commits) and publish the OID pair + exit code into the evidence bundle per Phase 1/2's convention.

## Architecture Patterns

### Six-Link Registration Chain — concrete file mapping

```
                       ┌────────────────────────────────────────┐
                       │  src/tooluniverse/data/*.json           │  Link 1: canonical definition
                       │  ("name", "type", "required_api_keys")  │  (source of truth)
                       └───────────────┬──────────────────────────┘
                                       │ "type" field
                                       ▼
                       ┌────────────────────────────────────────┐
                       │  src/tooluniverse/<domain>_tool.py       │  Link 2: implementation
                       │  (the Tool subclass named by "type")     │  (hand-written)
                       └───────────────┬──────────────────────────┘
                                       │ category registration
                                       ▼
                       ┌────────────────────────────────────────┐
                       │  src/tooluniverse/default_config.py      │  Link 3: catalog config
                       │  (category -> data/*.json path map)      │  (hand-written; can be
                       └───────────────┬──────────────────────────┘   commented out — see
                                       │                                Common Pitfalls)
                                       ▼
                       ┌────────────────────────────────────────┐
                       │  _lazy_registry_static.py (type->module) │  Link 4: lazy metadata
                       │  .tool_metadata.json (per-tool hash)     │  (BOTH generated;
                       └───────────────┬──────────────────────────┘   see two generators below)
                                       │
                                       ▼
                       ┌────────────────────────────────────────┐
                       │  src/tooluniverse/tools/<Name>.py         │  Link 5: generated module
                       │  src/tooluniverse/tools/__init__.py       │  (generated; CREDENTIAL-
                       └───────────────┬──────────────────────────┘   GATED — see pitfalls)
                                       │
                                       ▼
                       ┌────────────────────────────────────────┐
                       │  tests/unit/, tests/tools/, etc.         │  Link 6: tests
                       └────────────────────────────────────────┘

  Generators (both call tu.load_tools() with defaults -> both credential-gated):
    generate_lazy_registry.py  -> Link 4 (_lazy_registry_static.py)
    generate_coding_api.py     -> Link 5, writes directly to src/tooluniverse/tools/
    generate_tools.py          -> Link 5, writes to `tu build`'s output_dir
                                   (default: .tooluniverse/coding_api/, NOT src tree)
```

### Recommended audit script structure (Tier 1 + Tier 2)

Following D-04 (extend `test_registry_integrity.py`, don't fork) and the Claude's-discretion note about keeping Tier 1/Tier 2 artifacts joinable via a shared `verdict` field (Phase 2's `join_preservation` precedent):

```
src/tooluniverse/data/*.json  ──┐
                                 ├─► shared "defined_names" set (already exists:
tests/unit/test_registry_       │    _load_defined_tool_names(), excludes
integrity.py::_load_defined_    │    api_keys_catalog.json)
tool_names()                    │
                                 ▼
                     ┌───────────────────────────┐
                     │ NEW: per-tool six-link      │  Tier 1 — scoped to the 22 hand-
                     │ check function              │  resolved + 213 both-sides files
                     │ (name -> {defined, has_     │  from 02-FINDINGS.md's disagreement
                     │  category, has_module_file, │  classification table
                     │  in_init, has_test})        │
                     └───────────────┬───────────────┘
                                     │ same function, full name set
                                     ▼
                     ┌───────────────────────────┐
                     │ Tier 2 — same check, run    │  Cheap (per D-03's own reasoning);
                     │ across ALL defined names    │  catches drift outside Phase 2's
                     └───────────────────────────┘  explicit touch-set
```

### Reusable assets (verified present this session)

- `scripts/audit_upstream_merge.py::extract_definition_names` (AST-based top-level/class-level definition extraction) — reusable for confirming a `<domain>_tool.py` implementation module actually defines the class a JSON `"type"` field names.
- `scripts/audit_upstream_merge.py::classify_finding` — two-stage verdict pattern (primary comparison + pin/self-heal recheck); reusable for Tier 1's per-tool verdicts.
- `scripts/forensic_trace_findings.py` — "diff definitions, then check if a stage-only name is actually absent from HEAD or just renamed/still referenced" pattern; same discipline applies to distinguishing a genuinely stale registry entry from a renamed one.
- `scripts/capture_sync_baseline.py::publish_evidence` / `verify_checksums` — the `evidence/<full-OID>/` + sorted `SHA256SUMS` convention Phase 1/2 evidence bundles already use (see `.planning/phases/01-protected-sync-baseline/evidence/` and `.planning/phases/02-upstream-main-integration/evidence/`).
- `tests/unit/test_registry_integrity.py` — canonical mechanical check (D-04). Currently covers **2 of the 6 links**: (a) JSON `name` references (`required_tools` arrays, `claude/rules/*.md` mentions) resolve to a real JSON-defined name, and (b) JSON `type` fields resolve to a known Python class via `_lazy_registry_static.py` / `tool_registry.py`. It does **not** currently check: module-file existence in `tools/`, `tools/__init__.py` completeness, `.tool_metadata.json` hash freshness, or duplicate names across `data/*.json` files. These are the concrete gaps Tier 2 needs to close.
- `tests/unit/test_lazy_load_cache_consistency.py` — adjacent but orthogonal (runtime instance-caching correctness, not registration-chain completeness); useful pattern reference for safely picking a "known-good" tool name in new tests (`_SAFE_TOOL_NAMES`, `_SKIP_KEYWORDS` to avoid GPU/model-loading crashes).

## Common Pitfalls

### Pitfall 1: Treating regeneration as credential-neutral

**What goes wrong:** Running `tu build` (or either generator script directly) on a machine without every specialty API key configured silently shrinks `tools/__init__.py` and the generated module tree, because both generators build their file list from `tu.load_tools()`'s runtime-loaded set, not from `data/*.json` directly.
**Why it happens:** `ToolUniverse.load_tools()` is designed for *execution* (where credential gating is the correct, documented behavior — CLAUDE.md's Mental Model 4), but both codegen scripts reuse it unmodified for *catalog generation*, where every defined tool should get a wrapper regardless of whether it can currently execute.
**How to avoid:** Before trusting or committing any regeneration output, diff its `tools/__init__.py` import set against the current HEAD's import set. Any name present in HEAD but absent from the new output is a regression requiring investigation (was this tool intentionally removed from `data/*.json`, or did codegen just not have the key?) — never assume it self-resolves.
**Warning signs:** A regeneration reduces the `tools/__init__.py` docstring's tool count (`Type-safe Python interface to N scientific tools`) rather than increasing/holding steady after a merge that only added tools.

### Pitfall 2: Assuming `tu build` and `generate_coding_api.py` are the same generator

**What goes wrong:** They are two separately-maintained, currently-diverged scripts (confirmed via `diff`) that both produce `tools/<Name>.py` + `tools/__init__.py`-shaped output but are not guaranteed to produce byte-identical output. `tu build` is wired to `generate_tools.py` and defaults to writing outside the source tree (`.tooluniverse/coding_api/`); only an explicit `--output` override or a direct call to `generate_coding_api.py` writes into `src/tooluniverse/tools/`.
**Why it happens:** CONCERNS.md's tech-debt entry names `generate_coding_api.py` specifically; `generate_tools.py` is newer (mtime 2026-08-03) and wasn't necessarily in scope when that entry was written.
**How to avoid:** Before extending or invoking either script, confirm with the maintainer (or a `checkpoint:human-verify`) which one is canonical for regenerating the committed `src/tooluniverse/tools/` tree going forward, and consider whether the second script should be deprecated/removed as part of CAT-01's cleanup — leaving both live is itself a duplicate-registry-generator hazard.
**Warning signs:** Regeneration output differs depending on which script/CLI path was used to produce it.

### Pitfall 3: Orphaned/duplicate JSON definitions look like registration-chain gaps but are actually catalog hygiene debt

**What goes wrong:** `OxO_get_ontology_mappings` / `OxO_search_ontology_mappings` are defined with identical names in **both** `src/tooluniverse/data/oxo_tools.json` (mtime `2026-03-30`) and `src/tooluniverse/data/broken_apis/oxo_tools.json` (mtime `2026-08-03`) `[VERIFIED: src/tooluniverse/data/oxo_tools.json and src/tooluniverse/data/broken_apis/oxo_tools.json, this session — both files' "name" fields read directly]`. The top-level copy's category registration in `default_config.py` is commented out (`# "oxo": os.path.join(current_dir, "data", "oxo_tools.json"),` at `default_config.py:765`) with a comment explaining EBI retired the OxO service `[VERIFIED: src/tooluniverse/data/default_config.py:763-765, this session]` — so it is not currently loaded twice at runtime — but the orphaned top-level file is still present on disk, uncategorized, and would be picked up by any glob-based "all defined tool names" check (like `_load_defined_tool_names()`) as if it were live.
**Why it happens:** "Archiving" a broken API meant copying its JSON into `broken_apis/` and commenting out its category line, but the original top-level file was never deleted.
**How to avoid:** Tier 2's mechanical check must cross-reference `default_config.py`'s category map (what's actually loadable) against `data/*.json` (what's merely present on disk), not just check for JSON-internal name uniqueness. A tool name that is duplicate-defined but only one copy is ever loaded is a hygiene/cleanup finding (delete the orphan), not a runtime collision — but a mechanical check that only compares JSON files against each other will flag it as a duplicate-name collision (D-05's higher-risk class) unless it also checks live category wiring. Both framings are defensible; the planner should pick one and say so explicitly, since this is exactly the kind of "genuine collision, needs review" case D-05 anticipates.
**Warning signs:** Any tool name appearing in more than one `data/*.json` file; `grep -rl "<ToolName>" src/tooluniverse/data/*.json` returning more than one path.

### Pitfall 4: `test_registry_integrity.py`'s `RULES_DIR` looks like a typo but isn't

`RULES_DIR = REPO / "claude" / "rules"` (no leading dot) is correct — this repo has a real top-level `claude/rules/` directory distinct from `.claude/rules/` (which does not exist) `[VERIFIED: ls -d claude/rules exits 0; ls -d .claude/rules fails, this session]`. Don't "fix" this path when extending the test file.

## Code Examples

### Verified: PR #161 ancestry check (reusable exactly as-is for the phase's evidence artifact)

```bash
# Source: this session, read-only, against /Users/davis/code/ToolUniverse main checkout
git rev-parse HEAD
git merge-base --is-ancestor 16af425c053c306a658c96e254b4c4114338dd11 HEAD
echo "exit: $?"   # 0 = true = already an ancestor, SYNC-03 satisfied by verify-and-record
```

### Verified: full-catalog defined-name extraction (already in the codebase, reuse don't reimplement)

```python
# Source: tests/unit/test_registry_integrity.py:34-50, read this session
def _load_defined_tool_names() -> set[str]:
    """All tool names from ``name`` fields in data/*.json."""
    names: set[str] = set()
    for jf in DATA_DIR.glob("*.json"):
        if jf.name == "api_keys_catalog.json":
            continue
        try:
            data = json.loads(jf.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        items = (
            data if isinstance(data, list) else [data] if isinstance(data, dict) else []
        )
        for item in items:
            if isinstance(item, dict) and "name" in item:
                names.add(item["name"])
    return names
```

Note: this glob is **not recursive** — it will not pick up `data/broken_apis/*.json`. Any Tier 2 duplicate-name check that wants to catch the OxO case (Pitfall 3) needs an explicit `data/**/*.json` walk or an explicit second pass over `broken_apis/`, plus a decision about whether archived/broken definitions count toward "duplicate" at all.

### Verified: category-vs-disk cross-reference precedent (comment convention already used for archived APIs)

```python
# Source: src/tooluniverse/default_config.py:762-765, read this session
    # EBI OxO - Ontology cross-reference mappings across biomedical databases
    # Archived at: src/tooluniverse/data/broken_apis/oxo_tools.json
    # EBI retired the OxO service (all endpoints hang); use OLS (ols_* tools) instead.
    # "oxo": os.path.join(current_dir, "data", "oxo_tools.json"),
```

This is the existing convention for "intentionally disabled category" — three other categories (`pathway_commons`, `soilgrids`, plus `hmdb` referenced from `metabolite_tool.py`) follow the same pattern `[VERIFIED: grep "broken_apis" src/tooluniverse/*.py, this session — 4 matches]`. A Tier 2 check should treat any category whose `default_config.py` line is commented out with a `# Archived at:` marker as intentionally excluded, not stale.

## Runtime State Inventory

This is not a rename/refactor/migration phase in the conventional sense, but the concurrent dirty working-tree state functions identically to the hazard this section exists to catch — it is fully covered above under "Concurrent State Investigation (D-06)." No additional categories apply:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — this phase touches no external datastores (no DB, no vector index rebuild; `find_tools`' embedding regeneration is explicitly Phase 4 / EMBD-01) | none |
| Live service config | None — no external services (n8n, Datadog, etc.) are in scope for this repo/phase | none |
| OS-registered state | None | none |
| Secrets/env vars | The 8 credential families named above (`ADDGENE_API_KEY`, `BRENDA_EMAIL`/`BRENDA_PASSWORD`, `CLUE_API_KEY`, `DISGENET_API_KEY`, `ESM_API_KEY`, `BIOGRID_ACCESS_KEY`, `ALPHA_GENOME_API_KEY`, `CLUSPRO_USERNAME`/`CLUSPRO_API_SECRET`) are absent from both `.env.local` (file doesn't exist) and `.env.1password` on this machine. This is a **precondition to check**, not something Phase 3 should attempt to fix (obtaining these keys is out of scope) — see Open Questions. | Planner must NOT gate regeneration success on these keys being present; must instead design the diff-and-flag guard described above. |
| Build artifacts | `src/tooluniverse/tools/*.py` (2,660 files) + `.tool_metadata.json`, uncommitted and stale as characterized above | Do not build on top of; human/planner decision needed on whether to discard (`git restore`) before Phase 3's own regeneration runs, or to first fully diagnose which command produced it (open question). |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | No `claude` CLI process currently has its working directory inside `/Users/davis/code/ToolUniverse`'s main checkout running a regeneration script. `ps aux` output does not expose per-process cwd directly, so this is inferred from command-line arguments and absence of file-lock/lsof evidence, not a direct cwd read. | Concurrent State Investigation | If wrong, a process could resume writing to the dirty files mid-Phase-3, corrupting an in-progress audit. Low likelihood given the 2h37m-and-counting mtime gap, but not a mechanically-certain proof. |
| A2 | The dirty `src/tooluniverse/tools/*.py` state was produced by a direct call to `generate_coding_api.py` (or `tu build --output src/tooluniverse/tools`) rather than some other, undiscovered code path, since bare `tu build` defaults to `.tooluniverse/coding_api/`. | Concurrent State Investigation, Pitfall 2 | If wrong, there may be a third generation path not yet identified, which would need its own credential-gating audit. Doesn't change the recommended mitigation (diff-before-commit), only the root-cause narrative. |
| A3 | Treating the `OxO_*` duplicate as "hygiene debt, not a live runtime collision" (because `default_config.py`'s `oxo` category line is commented out) is the correct disposition, rather than "duplicate name, needs D-05 review checkpoint." | Common Pitfalls, Pitfall 3 | If the planner disagrees and treats it as a genuine collision requiring a `checkpoint:human-verify`, that's the more conservative (safer) choice — flagging this as an assumption mainly so the planner makes the call deliberately rather than by omission. |

**If this table is empty:** N/A — see above.

## Open Questions

1. **Which command produced the dirty `src/tooluniverse/tools/` regeneration, and by whom?**
   - What we know: mtime cluster `17:22:42`-`17:54:56` on 2026-08-06, predates this session's Phase 2 close-out commits; not producible by a bare `tu build` (wrong default output dir); consistent with `generate_coding_api.py` run directly or `tu build --output src/tooluniverse/tools`.
   - What's unclear: whether this was an intentional maintenance run by another operator/session, an accidental invocation, or leftover from an earlier phase of this same project's history.
   - Recommendation: surface to the human maintainer before Phase 3 execution begins (D-06's own instruction) — this research task cannot resolve it further without mutating state, which is explicitly forbidden.

2. **Should `generate_coding_api.py` and `generate_tools.py` be reconciled/deduplicated as part of CAT-01, or is that out of scope (ARCH-01 territory)?**
   - What we know: REQUIREMENTS.md's v2 backlog has `ARCH-01`: "Maintainers can evolve registry and generated metadata from one canonical manifest without parallel hand-maintained representations" — explicitly deferred beyond this milestone.
   - What's unclear: whether having *two divergent generator scripts* (not just parallel generated-vs-hand-maintained registries) is squarely inside CAT-01's "consistent six-link registration chain" mandate for *this* milestone, or is itself the kind of "broad refactoring... needs a separate milestone" PROJECT.md excludes.
   - Recommendation: the planner should scope this narrowly — CAT-01 needs the chain to be *consistent*, which can be satisfied by picking one generator as canonical for this phase's audit and evidence artifact, without necessarily deleting or merging the other. Flag the duplication as a finding either way.

3. **Does the currently-committed HEAD's `tools/__init__.py` already have MORE drift than the two examples found here (SEC_EDGAR under-inclusion, OxO duplication)?**
   - What we know: a rough (noisy) comparison of all `data/*.json` `"name"+"type"` entries against HEAD's `__init__.py` import list showed roughly 130 names present in JSON but absent from `__init__.py`, before excluding `skill:`-prefixed entries (not Python tools) and other likely-synthetic `get_*_info` coding-API helper names not sourced from `data/*.json` at all.
   - What's unclear: the true baseline drift count, since a rigorous count requires cross-referencing against `default_config.py`'s live category map (to exclude intentionally-archived categories like `broken_apis/`) rather than a flat JSON-file glob.
   - Recommendation: this is precisely what Tier 2's mechanical pass should compute authoritatively — treat this research's rough count as a lower-bound sanity check, not the final number.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| git | PR #161 ancestry check, all diffing | Yes | (system git) | — |
| Python | test/audit scripts | Yes | 3.14.6 (pyenv/miniforge active interpreter) | `pyproject.toml` declares `requires-python = ">=3.10"`; project's declared/tested runtime floor is unaffected |
| pytest | Tier 2 mechanical pass, existing `test_registry_integrity.py` | Yes | 9.0.2 | — |
| ruff | formatting verification (relevant to Pitfall re: `_lazy_registry_static.py`'s cosmetic diff) | Yes | 0.16.1 | — |
| uv | dependency/lockfile management (not expected to be touched this phase) | Yes | 0.12.1 | — |
| `tu` CLI | regeneration (`tu build`), discovery certification (`tu grep`/`tu info`) | Yes | matches installed package (`pyproject.toml` declares `version = "1.4.0"`, newer than CLAUDE.md's stale "1.1.11" ground-truth note) | — |
| ADDGENE_API_KEY, BRENDA_EMAIL/PASSWORD, CLUE_API_KEY, DISGENET_API_KEY, ESM_API_KEY, BIOGRID_ACCESS_KEY, ALPHA_GENOME_API_KEY, CLUSPRO_USERNAME/SECRET | Full-fidelity regeneration (all defined tools present in generated output) | No | — | None available on this machine; see "Root cause" above. The fallback is architectural, not a credential fetch: gate regeneration output on a name-set diff against HEAD rather than requiring these keys. |

**Missing dependencies with no fallback:** none blocking — the 8 credential families above have no fallback *credential*, but the phase does not need them if the diff-before-commit guard (this research's primary recommendation) is adopted instead of "auto-run regeneration and trust it."

**Missing dependencies with fallback:** the 8 credential families (fallback: architectural guard, not key acquisition).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 `[VERIFIED: pytest --version, this session]` |
| Config file | `pytest.ini` (repo root) `[VERIFIED: read this session]` |
| Quick run command | `pytest tests/unit/test_registry_integrity.py -x` |
| Full suite command | `pytest` (default `addopts` already excludes `slow`, `require_api_keys`, `network` — see below) |

Default `addopts` (from `pytest.ini`, read this session): `-ra -q --strict-markers --strict-config --maxfail=5 --disable-warnings --cov=tooluniverse --cov-report=term-missing:skip-covered -m "not slow and not require_api_keys and not network"`. This means: **the default test run will not exercise credential-gated tool loading paths either** — a Tier 2 test asserting "every JSON-defined tool has a generated module" is a static/structural check (file existence, name-set comparison) and does NOT need `require_api_keys`/`network` markers; it should run in the default fast lane. A test that actually calls `tu.load_tools()` and asserts on `len(tu.all_tools)`, by contrast, would be environment-sensitive per this research's central finding and should be marked accordingly (or explicitly documented as "credential-environment-dependent, expected count varies").

### Phase Requirement -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| SYNC-03 | PR #161 already an ancestor of HEAD | shell/git assertion (not pytest) | `git merge-base --is-ancestor 16af425c053c306a658c96e254b4c4114338dd11 HEAD` | N/A — evidence-script pattern, not a test file; follow Phase 1/2's `capture_sync_baseline.py`/`git.json` precedent |
| CAT-01 | Every tool has a consistent six-link chain (module file exists, importable, in `__init__.py`, has a test reference) | unit (structural, no network) | `pytest tests/unit/test_registry_integrity.py -x` (extend with new test functions per "Architecture Patterns" above) | Partial — 2 of 6 links covered; ❌ Wave 0 for the remaining 4 |
| CAT-02 | No duplicate/stale names in the loadable catalog; `grep_tools`/`get_tool_info` surface new+preserved tools correctly | unit (structural) + smoke (actual `grep_tools`/`get_tool_info` calls against representative names) | new test in `test_registry_integrity.py` for duplicates; a smoke script reusing the existing `tu grep`/`tu info` CLI or `ToolUniverse` discovery primitives for a representative sample | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/unit/test_registry_integrity.py -x` (fast, no network/API keys required)
- **Per wave merge:** `pytest` (full default suite; ~3s baseline observed for the registry-integrity module alone in Phase 2, per 02-CONTEXT.md's reused-pattern note)
- **Phase gate:** full suite green (excluding the known pre-existing, already-routed-to-follow-up `RuntimeError: no running event loop` failures — see PROJECT.md/STATE.md task `task_43fff30b`) before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] New test function(s) in `tests/unit/test_registry_integrity.py` covering: (a) every JSON-defined tool name has a corresponding `tools/<Name>.py` file, (b) every JSON-defined tool name is imported in `tools/__init__.py`, (c) no tool name is defined in more than one *live* (non-archived) `data/*.json` file.
- [ ] A duplicate-name check that is `broken_apis/`-aware (recursive glob + `default_config.py` category cross-reference), per Pitfall 3.
- [ ] A smoke test/script exercising `grep_tools` and `get_tool_info` against a representative sample of both new-upstream and preserved-custom tool names, for CAT-02's discoverability criterion (not currently covered by any existing test found this session). **The representative sample must exclude tools with unmet `required_api_keys`** — verified this session that `grep_tools`/`get_tool_info` read the same credential-gated `all_tool_dict` the codegen scripts do, so a gated tool would fail `get_tool_info`'s schema-inspection check for a credential reason, not a catalog-integrity reason.
- [ ] Framework install: none — pytest and all tooling already present and working.

## Security Domain

`security_enforcement` is not explicitly set in `.planning/config.json` (file is present but minimal/untracked, only contains `workflow._auto_chain_active: false` `[VERIFIED: read this session]`), so per the absent-defaults-to-enabled convention this section is included, scoped honestly to what actually applies.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|-------------------|
| V2 Authentication | No | This phase touches no auth surface — it's internal package/catalog reconciliation |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Marginal | The registration-chain audit is itself a form of input validation over `data/*.json` — malformed/duplicate entries are exactly what CAT-01/CAT-02 exist to catch. No new validation library is needed; extend the existing JSON-schema-shaped checks in `test_registry_integrity.py`. |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Silent catalog regression (credential-gated codegen dropping real tools without any error) | Tampering / (unintentional, not adversarial, but the effect is indistinguishable from a supply-chain drop) | The diff-before-commit guard recommended throughout this document; treat any generated-artifact name-count *decrease* as a hard-stop. |
| Duplicate public tool names resolving unpredictably at runtime (whichever `data/*.json` file loads last wins, silently) | Tampering | D-05's existing posture (flag genuine collisions for human review) is the correct standard mitigation; Tier 2's duplicate-name check operationalizes it. |

## Sources

### Primary (HIGH confidence — read directly this session)

- `src/tooluniverse/execute_function.py` (lines 895-936 `load_tools` signature/docstring; lines 1263-1300, 1339 the exact API-key exclusion mechanism, quoted verbatim; lines 389, 970, 1290-1296, 2419, 3170, 3352, 3892 `_excluded_api_key_tools` usage sites)
- `src/tooluniverse/tool_discovery_tools.py` (lines 99-114, 220-228, 281-311, 429, 581, 735-819 — `grep_tools`/`get_tool_info` reading `all_tool_dict`, and the `Fix-R13D-1` graceful-degradation comments for gated tools, quoted verbatim)
- `src/tooluniverse/generate_coding_api.py` (full file header + `main()`, lines 1-40, 255-290)
- `src/tooluniverse/generate_tools.py` (header, `main()` at line 592, `load_tools()` call at 614-615)
- `src/tooluniverse/cli.py` (`cmd_build`, lines 1705-1741)
- `src/tooluniverse/default_config.py` (lines 755-770, `oxo` category comment block)
- `src/tooluniverse/data/oxo_tools.json`, `src/tooluniverse/data/broken_apis/oxo_tools.json` (full `name` field extraction)
- `src/tooluniverse/data/{addgene,brenda,disgenet,esm,biogrid,clue,alphagenome,cluspro}_tools.json` (`required_api_keys` fields)
- `tests/unit/test_registry_integrity.py` (full file, 198 lines)
- `tests/unit/test_lazy_load_cache_consistency.py` (header + first 50 lines)
- `pytest.ini` (full file)
- `.planning/phases/03-follow-up-and-catalog-reconciliation/03-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`
- `.planning/phases/02-upstream-main-integration/02-FINDINGS.md` (first 60 lines — disagreement classification table, OxO row)
- Live git/shell commands this session: `git status`, `git diff`, `git log`, `git reflog`, `git worktree list`, `git merge-base --is-ancestor`, `stat`, `lsof`, `ps aux`, `pytest --version`, `ruff --version`, `uv --version`

### Secondary (MEDIUM confidence)

- `.claude/CLAUDE.md`'s Mental Model 4 (Credential Flow) description of per-tool API-key gating — used only as the initial documented-behavior pointer; the actual exclusion mechanism (which collection is filtered, at which line, and that codegen/discovery both consume that same collection) was independently confirmed by reading `execute_function.py` and `tool_discovery_tools.py` directly this session and is filed under Primary above, not this doc.

### Tertiary (LOW confidence)

- None — no claim in this document rests solely on training-data/WebSearch knowledge; this phase's domain is entirely this repository's own code, all of which was read directly.

## Metadata

**Confidence breakdown:**

- SYNC-03 / PR #161 ancestry: HIGH — re-verified live, single deterministic git command, exit code checked.
- CAT-01 / six-link chain mapping: HIGH — every link traced to a specific file/line read this session; existing test coverage gap identified by reading the actual test file, not inferred.
- CAT-02 / duplicate-and-stale findings: HIGH — the OxO duplicate and the credential-gated codegen regression are both live, currently-reproducible facts on this exact checkout, not hypothetical risk.
- Concurrent state investigation (D-06): HIGH on "stale, not active", "output incomplete relative to HEAD", and root cause (the exact exclusion mechanism was read verbatim at `execute_function.py:1263-1300,1339`, not inferred from documentation or correlation alone); MEDIUM on "which exact command produced it" (flagged as Open Question / Assumption A2).
- CAT-02 discoverability gap for gated tools: HIGH — `grep_tools`/`get_tool_info` reading the same `all_tool_dict` collection was confirmed by reading `tool_discovery_tools.py` directly, including the codebase's own prior `Fix-R13D-1` bug-fix comments corroborating the same failure mode was already found and partially mitigated once before.

**Research date:** 2026-08-06
**Valid until:** This research is tied to a specific git state (`HEAD=20a03aaea22d29b09336001480264ee162f5430b`, dirty working tree as characterized above). Re-verify the PR #161 ancestry check and the dirty-file mtime/lsof checks at the start of Phase 3 execution if any time has passed — both are cheap, and D-02 explicitly requires treating a changed ancestry result as a new finding, not something to silently trust from this document.
