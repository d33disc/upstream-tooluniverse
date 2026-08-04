# Phase 1: Protected Sync Baseline - Context

**Gathered:** 2026-08-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish a reproducible, fully green pre-sync baseline and an auditable preservation reference before any upstream integration begins. This phase records the current fork, proves its supported behavior, and identifies protected custom assets; it does not merge upstream changes.

</domain>

<decisions>
## Implementation Decisions

### Baseline Depth
- **D-01:** The pre-sync baseline must be comprehensive: targeted high-risk suites, the broader offline suite, catalog loading, and representative Python, CLI, MCP stdio/HTTP, and REST probes.
- **D-02:** The baseline must be fully green before synchronization. Existing failures are not accepted as baseline debt; they must be diagnosed and fixed before upstream integration.
- **D-03:** Every live provider that is currently configured must pass its selected checks. Transient timeouts and rate limits receive bounded retries with fixed backoff; a persistent configured-provider failure blocks synchronization and retains diagnostics.
- **D-04:** Run the comprehensive baseline locally on Python 3.12. CI must prove compatibility across the full declared Python 3.10+ support range; the current Python-3.12-only CI matrix is insufficient for this decision.
- **D-05:** Each public surface must prove the complete discovery-to-execution chain: list or search, inspect the exact schema, execute a deterministic tool, and return a structured success or error.
- **D-06:** Use a tiered probe matrix covering deterministic credential-free local tools, representative fork-specific tools, configured remote scientific providers, and a catalog-driven sample across major categories.
- **D-07:** Compare normalized schemas and semantic invariants rather than volatile byte-for-byte output. Normalize timestamps, generated IDs, and unstable remote ordering while enforcing status, required keys, types, documented ordering guarantees, and domain invariants.

### the agent's Discretion
- Select the exact representative tools and category sample, provided every tier in D-06 is present and the choices are recorded.
- Choose bounded retry counts and backoff intervals that keep live checks finite and reproducible.
- Choose the baseline artifact layout and machine-readable formats, provided exact revisions, commands, environment facts, outcomes, and diagnostics remain auditable.
- Order targeted and broad checks to fail quickly without reducing the required coverage.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and preservation
- `.planning/PROJECT.md` — milestone constraints, protected architecture, staged integration policy, and preservation rules.
- `.planning/REQUIREMENTS.md` — Phase 1 requirements BASE-01, BASE-02, and PRES-01.
- `.planning/ROADMAP.md` — Phase 1 boundary, goal, and observable success criteria.
- `docs/superpowers/specs/2026-04-17-upstream-sync-design.md` — historical sync design, conflict strategy, protected paths, and rollback intent.
- `docs/superpowers/plans/2026-04-17-upstream-sync.md` — historical integration plan and known conflict inventory; treat revision counts and branch names as dated evidence to re-verify.

### Test and runtime contracts
- `pyproject.toml` — declared Python >=3.10 compatibility, dependencies, and Ruff configuration.
- `pytest.ini` — default offline selection and suites excluded from default pytest collection.
- `tests/README.md` — test taxonomy, markers, commands, and API-key/network conventions.
- `.github/workflows/tests.yml` — current CI test jobs and Python matrix, which currently covers only Python 3.12.

### Public surfaces and architecture
- `docs/dev_docs/Interaction_Surfaces.md` — Python, CLI, MCP, and REST entry points and discovery workflow.
- `.planning/codebase/ARCHITECTURE.md` — shared-core execution paths and architectural constraints.
- `.planning/codebase/STACK.md` — supported runtime, package manager, test stack, and semantic-search dependencies.
- `.planning/codebase/CONVENTIONS.md` — validation commands and repository coding/testing conventions.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Existing pytest unit, integration, tool, example, and API suites provide the baseline test layers; default pytest intentionally omits several of these.
- `ToolUniverse`, `tu`, MCP server entry points, and the REST API already expose the discovery, schema-inspection, execution, and structured-error behavior needed for surface probes.
- Existing Git remotes (`origin` and `upstream`), the GSD codebase map, and Git history provide inputs for revision and preservation inventories.

### Established Patterns
- Use `uv` and the committed `uv.lock`; do not introduce another environment or package manager.
- Public transports route through the shared `ToolUniverse` core and must be tested as surfaces over the same execution behavior.
- Credential-dependent tests use markers and environment configuration; secrets remain external and must never enter artifacts.
- Optional scientific dependencies and provider availability are isolated, but a provider explicitly configured for this baseline is part of the green gate.

### Integration Points
- Phase 1 planning should connect baseline commands to `pytest.ini`, `.github/workflows/tests.yml`, CLI/MCP/REST entry points, and a machine-readable evidence directory chosen by the planner.
- Preservation inventory must include tracked fork-only changes and account for symlinked plugin skills without traversing or rewriting their targets.
- The existing untracked `ralph-specs/fleet/results/` content remains user-owned and untouched unless separately classified during preservation inventory work.

</code_context>

<specifics>
## Specific Ideas

- “Fully green” means no accepted pre-existing offline failures.
- Configured live providers are blocking after bounded retries; missing credentials for an unconfigured provider do not make that provider configured.
- Surface probes must exercise the workflow users actually follow: discover, inspect, then execute.
- Volatile remote values may be normalized, but structural or semantic drift must remain visible.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-protected-sync-baseline*
*Context gathered: 2026-08-03*
