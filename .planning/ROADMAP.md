# Roadmap: ToolUniverse

## Overview

This milestone moves from a protected, measurable fork baseline to a staged upstream integration, then reconciles the catalog's generated registration artifacts, documentation, and semantic-search embeddings before certifying compatibility and behavior across ToolUniverse's public connection surfaces. Each boundary is independently auditable so upstream adoption cannot silently erase custom work or leave derived artifacts stale.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Protected Sync Baseline** - Establish exact revisions, measurable behavior, and the fork-specific preservation contract
- [ ] **Phase 2: Upstream Main Integration** - Integrate upstream main while retaining custom behavior and resolving conflicts deliberately
- [ ] **Phase 3: Follow-up and Catalog Reconciliation** - Resolve PR #161 status and restore a coherent, fully registered runtime catalog
- [ ] **Phase 4: Documentation and Semantic Index** - Align documentation and embeddings with the synchronized loadable catalog
- [ ] **Phase 5: Cross-Surface Certification** - Prove runtime compatibility, regression safety, and representative behavior on every supported surface

## Phase Details

### Phase 1: Protected Sync Baseline

**Goal**: Maintainers can begin synchronization from an isolated, reproducible baseline with every custom asset explicitly protected
**Depends on**: Nothing (first phase)
**Requirements**: BASE-01, BASE-02, PRES-01
**Success Criteria** (what must be TRUE):

  1. Maintainer can name the exact fork and upstream revisions, review their divergence, and distinguish pre-existing worktree changes from synchronization work.
  2. Maintainer can rerun the recorded test, catalog-load, discovery, and representative execution checks and reproduce the pre-sync result set.
  3. Maintainer can inspect a preservation inventory covering custom code, tool definitions, plugins, generated assets, and symlink targets before resolving any conflict.

**Plans**: 5/5 plans executed

Plans:
**Wave 1**

- [x] 01-01-PLAN.md — Capture immutable Git provenance, inventory protected assets, and repair three plugin links from authoritative PR #161 evidence.

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02-PLAN.md — Normalize evidence, map configured providers, bound retries, and publish tamper-evident artifacts.

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 01-03-PLAN.md — Certify discover → inspect → execute across Python, CLI, MCP stdio/HTTP, and REST.

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 01-04-PLAN.md — Define Python 3.10–3.14 hosted CI and fail-closed exact-head evidence collection.

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 01-05-PLAN.md — Pass the remote-availability checkpoint and publish the exact-commit fully green baseline.

### Phase 2: Upstream Main Integration

**Goal**: The fork contains the selected upstream-main revision without losing its custom capabilities
**Depends on**: Phase 1
**Requirements**: SYNC-01, SYNC-02, PRES-02
**Success Criteria** (what must be TRUE):

  1. Maintainer can inspect an isolated integration stage that contains the selected upstream-main revision and excludes unrelated pre-existing worktree changes.
  2. Shared canonical tool definitions match upstream while fork-only definitions and additions remain available in deliberately combined structural files.
  3. Maintainer can compare the result with the Phase 1 preservation inventory and account for every custom code, tool, plugin, registration, and symlink asset.
  4. Representative preserved custom tools still load and execute after the upstream-main integration.

**Plans**: 1/6 plans executed

Plans:
**Wave 1**

- [x] 02-01-PLAN.md -- Entry-level tool-name union sweep over all 213 both-sides `data/*.json` files, with checksummed evidence (tracer slice).

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-02-PLAN.md -- Isolated re-merge stage at `e0755067`; merge started and the data/config layer resolved under D-08.

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 02-03-PLAN.md -- Source-layer resolution (11 modules, 5 test files), stage commit pinned at `refs/audit/remerge`, lazy-registry regeneration.

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 02-04-PLAN.md -- Full-tree diff against `f81448f2`, finding classification with D-06a pin recheck, 1,392-path preservation join.
- [ ] 02-05-PLAN.md -- Fresh criterion-4 probes for the recorded custom-tool sample plus symlink preservation checks.

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 02-06-PLAN.md -- Corrective-commit decision checkpoint, evidence publication, traceability update.

### Phase 3: Follow-up and Catalog Reconciliation

**Goal**: The final integrated source has one coherent, complete, and loadable catalog after resolving the historical follow-up change set
**Depends on**: Phase 2
**Requirements**: SYNC-03, CAT-01, CAT-02
**Success Criteria** (what must be TRUE):

  1. Maintainer can see whether PR #161 is already contained by upstream; if not, its separate integration result and validation are reviewable without replaying upstream main.
  2. Every new upstream and preserved custom tool traverses the full six-link registration chain without missing, stale, or mismatched names and types.
  3. Users can locate representative upstream and custom tools with `grep_tools` and inspect their exact schemas with `get_tool_info`.
  4. The runtime catalog loads without duplicate public names or stale generated registry references.

**Plans**: TBD

### Phase 4: Documentation and Semantic Index

**Goal**: Users encounter documentation and semantic discovery results that accurately represent the synchronized runtime catalog
**Depends on**: Phase 3
**Requirements**: DOC-01, EMBD-01
**Success Criteria** (what must be TRUE):

  1. Users can follow current documentation for the Python, CLI, MCP, and REST entry points without encountering stale tool counts, schemas, names, or generated references.
  2. Users can distinguish the authoritative loadable inventory from dated health snapshots in the updated documentation.
  3. Users can run `find_tools` queries for representative upstream and custom capabilities and receive relevant results from embeddings built from the synchronized catalog.
  4. Maintainers can reproduce the documentation and embedding outputs with the repository's existing generation and validation workflows.

**Plans**: TBD

### Phase 5: Cross-Surface Certification

**Goal**: Maintainers can release the synchronized fork with evidence that supported runtimes and public connection surfaces remain correct
**Depends on**: Phase 4
**Requirements**: COMP-01, TEST-01, SURF-01, REL-01
**Success Criteria** (what must be TRUE):

  1. Users can install and exercise the synchronized package under the declared Python 3.10+ contract, with the Python 3.12 CI/container path passing.
  2. Maintainers can compare targeted and broader offline test results with the Phase 1 baseline and see the same or better pass level, including explicitly selected affected tool/API suites.
  3. Users can discover, inspect, and execute representative tools through Python, CLI, MCP stdio/HTTP, and REST with consistent shared-core behavior.
  4. Maintainers can audit the final diff and integration provenance and account for preserved custom code plus current registry, documentation, lockfile, and embedding artifacts.

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Protected Sync Baseline | 5/5 | Complete | 2026-08-04 |
| 2. Upstream Main Integration | 1/6 | In Progress|  |
| 3. Follow-up and Catalog Reconciliation | 0/TBD | Not started | - |
| 4. Documentation and Semantic Index | 0/TBD | Not started | - |
| 5. Cross-Surface Certification | 0/TBD | Not started | - |
