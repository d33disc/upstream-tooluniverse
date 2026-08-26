---
phase: 01
slug: protected-sync-baseline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-03
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4.2 locally; project minimum 7.0 |
| **Config file** | `pytest.ini`; database override `tests/test_database_setup/pytest.ini` |
| **Quick run command** | `uv run pytest -o addopts='' tests/unit/test_sync_baseline_git.py tests/unit/test_sync_baseline_normalize.py -q --strict-markers --timeout=60` |
| **Full suite command** | `uv run python scripts/capture_sync_baseline.py --output-dir <caller-supplied-path>` |
| **Estimated runtime** | Quick lane <30 seconds; full gate is environment/provider dependent and must record elapsed time |

---

## Sampling Rate

- **After every task commit:** Run the smallest new baseline unit test file plus the smallest affected existing test file.
- **After every plan wave:** Run the targeted high-risk lane and verify its JUnit output.
- **Before `$gsd-verify-work`:** The complete Python 3.12 local baseline, configured live-provider lane, checksum validation, and Python 3.10+ CI matrix must be green.
- **Max feedback latency:** 30 seconds for per-task checks; longer lanes run at wave/phase boundaries.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-W0-01 | TBD | 0 | BASE-01, PRES-01 | T-01 path/symlink escape | Git data is parsed without shell interpolation or symlink traversal | unit | `uv run pytest -o addopts='' tests/unit/test_sync_baseline_git.py -q --strict-markers --timeout=60` | ❌ W0 | ⬜ pending |
| 01-W0-02 | TBD | 0 | BASE-02 | T-02 secret leakage / over-normalization | Evidence contains no credential values and retains required structural invariants | unit | `uv run pytest -o addopts='' tests/unit/test_sync_baseline_normalize.py -q --strict-markers --timeout=60` | ❌ W0 | ⬜ pending |
| 01-W0-03 | TBD | 0 | BASE-02 | T-03 transport/session drift | Python, CLI, MCP stdio/HTTP, and REST complete discover → inspect → execute with structured outcomes | integration | `uv run pytest -o addopts='' tests/integration/test_sync_baseline_surfaces.py -q --strict-markers --timeout=60` | ❌ W0 | ⬜ pending |
| 01-GATE-01 | TBD | final | BASE-01, BASE-02, PRES-01 | T-04 evidence tampering | All required lanes are green and `SHA256SUMS` validates every committed evidence file | integration | `uv run python scripts/capture_sync_baseline.py --output-dir <caller-supplied-path>` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_sync_baseline_git.py` — exact revisions, divergence, worktree-state separation, preservation classes, and safe symlink inventory for BASE-01/PRES-01.
- [ ] `tests/unit/test_sync_baseline_normalize.py` — redaction, volatile-path normalization, invariant checks, deterministic sampling, and bounded retry behavior for BASE-02.
- [ ] `tests/integration/test_sync_baseline_surfaces.py` — real five-surface discovery-to-execution contract for BASE-02.
- [ ] Configured-provider manifest test — every configured credential family maps to a bounded live probe before network execution.
- [ ] `scripts/capture_sync_baseline.py` — fail-closed evidence orchestrator using existing Git, uv, pytest, and Python standard library only.
- [ ] CI matrix expansion — prove the full declared Python 3.10+ range instead of Python 3.12 alone.
- [ ] Broken-symlink gate — resolve or explicitly classify each tracked dangling plugin-skill link before sign-off.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Supported Python matrix is green | BASE-02 | Hosted runner versions are a GitHub CI result | Inspect the synchronization commit's required test workflow and confirm every declared Python 3.10+ matrix job succeeded. |
| Configured providers are intentionally selected | BASE-02 | Credential availability is environment-specific and values must remain secret | Review the value-free provider manifest, confirm each configured credential family has a selected probe, then verify all probes passed after bounded retries. |
| Broken symlink disposition is intentional | PRES-01 | Missing targets may reflect omitted assets or deliberate removal | Review all tracked mode-120000 entries reported as broken; restore targets or record an explicit removal decision before approving. |

---

## Validation Sign-Off

- [ ] Every planned task has an automated verification command or an explicit Wave 0 dependency.
- [ ] No three consecutive tasks lack automated verification.
- [ ] Wave 0 creates every currently missing test/orchestrator artifact.
- [ ] No watch-mode flags are used.
- [ ] Per-task feedback latency remains below 30 seconds.
- [ ] All deterministic offline tests are green; no pre-existing failure waiver exists.
- [ ] Every configured live-provider probe is green after bounded retry.
- [ ] Python 3.10+ CI compatibility is green.
- [ ] Evidence checksums validate and a secret scan finds no credential values.
- [ ] `nyquist_compliant: true` and `wave_0_complete: true` are set only after these checks pass.

**Approval:** pending
