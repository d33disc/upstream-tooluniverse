# Requirements: ToolUniverse

**Defined:** 2026-08-03
**Core Value:** Synchronize the fork with upstream without losing custom behavior or allowing its tested, documented, and searchable tool catalog to drift.

## v1 Requirements

Requirements for the upstream synchronization milestone. Each maps to exactly one roadmap phase.

### Baseline and Preservation

- [ ] **BASE-01**: Maintainer can identify the exact fork revision, upstream revision, divergence, worktree state, and staged integration targets before synchronization begins
- [ ] **BASE-02**: Maintainer has a reproducible pre-sync baseline for relevant tests, catalog loading, and representative discovery/execution behavior
- [ ] **PRES-01**: Maintainer has an explicit inventory of fork-specific code, tools, plugins, generated assets, and symlinks that must survive synchronization

### Upstream Integration

- [ ] **SYNC-01**: Maintainer can integrate the selected `mims-harvard/ToolUniverse` main revision on an isolated synchronization branch without incorporating unrelated local changes
- [ ] **SYNC-02**: Shared canonical tool definitions follow upstream while structural conflicts retain both upstream additions and fork-specific behavior
- [ ] **PRES-02**: Fork-specific code, tools, plugin assets, and registration contracts remain present and functional after the upstream-main integration
- [ ] **SYNC-03**: Maintainer can determine whether historical PR #161 is already represented by the selected upstream revision and, when needed, integrate it as a separate verified stage

### Catalog Integrity

- [ ] **CAT-01**: Every synchronized or preserved tool has a consistent six-link registration chain from canonical JSON definition through implementation, catalog configuration, lazy metadata, generated public module, and tests
- [ ] **CAT-02**: The synchronized loadable catalog exposes new upstream and preserved custom tools through `grep_tools` and `get_tool_info` without stale or duplicate registry entries

### Documentation and Embeddings

- [ ] **DOC-01**: User-facing and developer documentation accurately describes the synchronized tool/skill inventory, public entry points, and any changed behavior
- [ ] **EMBD-01**: `find_tools` uses embeddings regenerated from the synchronized loadable catalog and returns relevant results for representative upstream and custom-tool queries

### Release Certification

- [ ] **COMP-01**: The synchronized package remains installable and testable on declared Python 3.10+ runtimes, with Python 3.12 as the primary CI/container runtime
- [ ] **TEST-01**: Targeted and broader offline test suites pass at the same or better level than the recorded baseline, including affected tool/API suites excluded by default pytest selection
- [ ] **SURF-01**: Users can discover, inspect, and execute representative tools through Python, CLI, MCP stdio/HTTP, and REST with behavior routed through the shared core
- [ ] **REL-01**: Maintainer can audit the final synchronization diff and provenance to confirm custom code is preserved and generated catalog, documentation, lockfile, and embedding artifacts are current

## v2 Requirements

Deferred beyond this synchronization milestone.

### Hardening

- **HARD-01**: Operators can authorize discovery, network, filesystem, code-execution, and management capabilities independently
- **HARD-02**: Operators can apply uniform execution deadlines, response-size limits, and resource policies across tools
- **HARD-03**: Release automation can enforce catalog-wide provider health and compatibility gates, including credentialed live services

### Architecture

- **ARCH-01**: Maintainers can evolve registry and generated metadata from one canonical manifest without parallel hand-maintained representations
- **ARCH-02**: Maintainers can change invocation, batching, caching, and registry loading through smaller behavior-preserving services behind the `ToolUniverse` facade

## Out of Scope

| Feature | Reason |
|---------|--------|
| New scientific tool families unrelated to upstream synchronization | Expands scope and makes regressions harder to attribute |
| Broad security/performance remediation | Important concerns, but not necessary to prove this synchronization correct |
| Raising the minimum Python version above 3.10 | Conflicts with the declared compatibility contract |
| Replacing `uv` or introducing another root package manager | The repository already has a canonical lock and workflow |
| Live validation of every external provider | Credentials, rate limits, and provider availability make this unsuitable as the synchronization gate |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BASE-01 | Phase 1 | Pending |
| BASE-02 | Phase 1 | Pending |
| PRES-01 | Phase 1 | Pending |
| SYNC-01 | Phase 2 | Pending |
| SYNC-02 | Phase 2 | Pending |
| PRES-02 | Phase 2 | Pending |
| SYNC-03 | Phase 3 | Pending |
| CAT-01 | Phase 3 | Pending |
| CAT-02 | Phase 3 | Pending |
| DOC-01 | Phase 4 | Pending |
| EMBD-01 | Phase 4 | Pending |
| COMP-01 | Phase 5 | Pending |
| TEST-01 | Phase 5 | Pending |
| SURF-01 | Phase 5 | Pending |
| REL-01 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-08-03*
*Last updated: 2026-08-03 after initial roadmap creation*
