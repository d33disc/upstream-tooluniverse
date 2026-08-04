# Phase 1: Protected Sync Baseline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-03
**Phase:** 1-protected-sync-baseline
**Areas discussed:** Baseline depth

---

## Baseline Depth

### Overall coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Comprehensive offline baseline | Targeted high-risk suites, broader offline tests, catalog loading, and representative Python/CLI/MCP/REST probes | ✓ |
| Targeted baseline | Synchronization-sensitive tests and representative probes only | |
| Smoke baseline | Package import, catalog load, and one discovery/execution check | |

**User's choice:** Comprehensive offline baseline
**Notes:** The user later expanded this with configured live-provider gating.

### Existing failures

| Option | Description | Selected |
|--------|-------------|----------|
| Record and fingerprint | Preserve known failures as baseline debt | |
| Require fully green | Fix every offline failure before synchronization | ✓ |
| Triage by relevance | Fix sync-sensitive failures and record unrelated failures | |

**User's choice:** Require a fully green baseline
**Notes:** Existing failures cannot be carried forward as accepted debt.

### Live providers

| Option | Description | Selected |
|--------|-------------|----------|
| Offline gate only | Live checks are informational | |
| Configured live gate | Every provider with available configuration must pass | ✓ |
| Selected live probes | Require only a named provider subset | |

**User's choice:** Configured live gate
**Notes:** Persistent failures block after bounded retries.

### Runtime matrix

| Option | Description | Selected |
|--------|-------------|----------|
| Python 3.12 local plus supported-version CI | Comprehensive local run on the primary runtime and CI proof for Python 3.10+ | ✓ |
| Every supported Python locally | Run the complete suite locally on every supported version | |
| Python 3.12 only | Use one controlled runtime | |

**User's choice:** Python 3.12 locally plus supported-version CI
**Notes:** Current CI only lists Python 3.12, so planning must close the declared-support gap.

### Surface behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Discovery-to-execution chain | Search/list, schema inspection, deterministic execution, and structured result/error on each surface | ✓ |
| Discovery only | Test listing, search, and schema inspection | |
| Execution only | Run one known tool through each surface | |
| Expanded matrix | Several categories and success/error paths on every surface | |

**User's choice:** Discovery-to-execution chain
**Notes:** Apply to Python, CLI, MCP stdio/HTTP, and REST.

### Probe tool set

| Option | Description | Selected |
|--------|-------------|----------|
| Stable local and fork-specific tools | Deterministic credential-free tools plus representative custom tools | ✓ |
| Stable local tools only | Maximize repeatability | ✓ |
| Scientific remote tools | Exercise real external scientific APIs | ✓ |
| Catalog-driven sample | Select tools across major categories | ✓ |

**User's choice:** All options as a combined tiered matrix
**Notes:** Deterministic local coverage, fork-specific tools, configured remote providers, and catalog sampling are all required.

### Output comparison

| Option | Description | Selected |
|--------|-------------|----------|
| Schema and invariant comparison | Normalize volatile fields and enforce stable structural/semantic contracts | ✓ |
| Exact snapshots | Require byte-for-byte output | |
| Test-only comparison | Preserve only pass/fail | |
| Per-tool rules | Define custom comparison logic for every selected tool | |

**User's choice:** Schema and invariant comparison
**Notes:** Normalize timestamps, IDs, and unstable remote ordering without hiding contract drift.

### Transient live failures

| Option | Description | Selected |
|--------|-------------|----------|
| Bounded retry, then block | Retry transient failures and block with diagnostics if they persist | ✓ |
| Fail immediately | Block on the first failure | |
| Quarantine | Make persistent transient failures non-blocking | |
| Provider-specific policy | Define separate retry policy for every provider | |

**User's choice:** Bounded retry, then block
**Notes:** Retry policy must remain finite and diagnostics must be retained.

---

## the agent's Discretion

- Exact representative tools, catalog sample size, retry counts/backoff, artifact format, and execution ordering within the locked coverage rules.

## Deferred Ideas

None.
