# ToolUniverse

## What This Is

ToolUniverse is a Python 3.10+ scientific research platform that exposes a large, configuration-driven tool catalog through Python, CLI, MCP, and REST interfaces. This milestone synchronizes the fork with `mims-harvard/ToolUniverse` while preserving fork-specific code and ensuring that tests, documentation, generated catalog artifacts, and semantic-search embeddings describe the synchronized runtime.

## Core Value

Synchronize the fork with upstream without losing custom behavior or allowing its tested, documented, and searchable tool catalog to drift.

## Requirements

### Validated

- ✓ Users can discover, inspect, and execute scientific tools through a shared `ToolUniverse` core exposed by Python, CLI, MCP, and REST — existing v1.4.0 codebase
- ✓ Tool definitions remain schema-first and tool implementations load lazily through configuration and registry metadata — existing v1.4.0 codebase
- ✓ Core local and stdio operation works without external-service credentials, while integrations activate from environment configuration — existing v1.4.0 codebase

### Active

- [ ] Establish an auditable upstream/fork baseline and preservation inventory before integration
- [ ] Integrate upstream main and the identified follow-up change set in separate, verifiable stages
- [ ] Preserve custom code, plugin assets, tool contracts, and Python 3.10+ compatibility while resolving conflicts
- [ ] Regenerate and validate every derived catalog/registration artifact affected by the synchronization
- [ ] Refresh documentation and semantic-search embeddings from the synchronized loadable catalog
- [ ] Certify tests and representative behavior across the supported connection surfaces before declaring the fork synchronized

### Out of Scope

- Unrelated feature development — this milestone is limited to synchronization and the repairs required to preserve existing behavior
- Broad refactoring of the monolithic execution core or registry architecture — high-risk structural work needs a separate milestone
- Resolving every known security, performance, or provider-health concern — only regressions or blockers introduced/exposed by synchronization are included
- Guaranteeing live success for every credentialed external provider — offline contracts and selected configured smoke checks are the release gate
- Adopting Python features that raise the declared runtime floor above 3.10 — compatibility is part of the synchronization contract

## Context

- The fork has a shared orchestration core in `src/tooluniverse/execute_function.py`; Python, CLI, MCP, and REST transports must continue routing through it.
- Public tools are defined through a multi-link registration chain spanning JSON definitions, Python adapters, default catalog configuration, lazy registry metadata, generated tool modules, and tests.
- Upstream synchronization guidance calls for staged integration: upstream main first, then the historical PR #161 follow-up only if it is not already represented by the selected upstream revision.
- Canonical upstream tool definitions should be preferred when they supersede fork copies, but fork-only tools and additions must remain present; structural files require a deliberate combined resolution.
- The repository uses `uv`, `pytest`, and Ruff. Default pytest excludes several tool/API/example suites, so synchronization certification must explicitly select affected suites.
- Semantic search is computed from the tools actually loaded by `ToolUniverse`; dated manifests are snapshots, not authoritative inventory.
- The current worktree is dirty on `docs/gsd-codebase-map`. Synchronization execution must isolate and preserve pre-existing changes before any merge.
- Plugin skill entries include symlinks. Sync and generation work must preserve link targets and avoid destructive recursive writes through them.

## Constraints

- **Compatibility**: Preserve `requires-python = ">=3.10"`; Python 3.12 is the primary CI/container validation runtime — downstream users rely on the declared floor.
- **Integration sequence**: Establish a protected baseline, merge upstream main, then evaluate/integrate PR #161 as a separate stage — each stage must be independently reviewable and testable.
- **Conflict resolution**: Preserve all fork-specific behavior and additions; use upstream canonical definitions where they supersede shared copies and manually combine structural files — dropping custom lines is unacceptable.
- **Architecture**: Keep execution routed through `ToolUniverse` and retain lazy imports, schema-first calls, optional-dependency isolation, and structured errors — transport-specific execution would create drift.
- **Registration**: Maintain the complete six-link registration chain and regenerate derived files with existing repository workflows — hand-edited partial registries are not a valid synchronized state.
- **Validation**: Compare test results with the captured pre-sync baseline, run targeted affected suites before broader offline tests, and explicitly cover affected tool/API suites excluded by default.
- **Documentation**: Update authored and generated documentation when catalog, navigation, shared references, or public behavior changes; run the smallest relevant checks before a complete docs build when needed.
- **Embeddings**: Rebuild semantic-search artifacts from the synchronized loadable catalog and verify `find_tools` behavior — stale snapshots must not drive the index.
- **Dependencies**: Use the existing `uv.lock` and `uv` workflow; do not introduce another package manager or add dependencies unless upstream integration requires and justifies them.
- **Secrets and network**: Keep credentials environment-based and do not read or commit populated secret files; live checks remain explicitly marked and scoped.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat the loadable runtime catalog as authoritative | `TOOL_MANIFEST.json` is dated and can diverge from what users can execute | — Pending |
| Use a protected, staged synchronization rather than one combined merge | Separates conflict resolution and regression attribution between upstream main and the follow-up change set | — Pending |
| Preserve custom additions while accepting upstream canonical replacements for shared definitions | Balances fork value with upstream correctness and minimizes long-term drift | — Pending |
| Gate completion on tests, docs, embeddings, and representative surface checks | A clean Git merge alone does not prove the scientific platform remains usable | — Pending |

---
*Last updated: 2026-08-03 after initial roadmap creation from ingested project context*
