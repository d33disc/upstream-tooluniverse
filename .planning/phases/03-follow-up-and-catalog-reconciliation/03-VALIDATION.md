---
phase: 03
slug: follow-up-and-catalog-reconciliation
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-07T00:48:45.990Z
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `03-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4.2 — `.venv/bin/python -m pytest` `[VERIFIED: .venv/bin/python -m pytest --version, this session — supersedes RESEARCH.md's ambient-shell "9.0.2", which resolved a different, non-project interpreter]` |
| **Config file** | `pytest.ini` (repo root) — default `addopts` excludes markers `slow`, `require_api_keys`, `network` |
| **Quick run command** | `.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -x` |
| **Full suite command** | `.venv/bin/python -m pytest` (respects `pytest.ini` default excludes) |
| **Estimated runtime** | ~13 seconds quick (measured this session, coverage instrumentation included) / full suite not re-measured this session — Phase 2 observed ~180s under the same `pytest.ini` config; confirm at wave-merge gate |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -x`.
- **After every plan wave:** Run `.venv/bin/python -m pytest` (full default suite).
- **Before `/gsd-verify-work`:** Full suite must be green AND all four phase success criteria must have artifact evidence:
  1. PR #161 ancestry OID pair + `git merge-base --is-ancestor` exit code, published per Phase 1/2's `evidence/<oid>/` convention.
  2. Six-link chain audit covering both Tier 1 (Phase 2's touched-file scope) and Tier 2 (full catalog) with zero unresolved findings.
  3. `grep_tools`/`get_tool_info` smoke results for the representative sample (credential-gated names excluded per the researched constraint).
  4. Duplicate/stale-name check green across the full, `broken_apis/`-aware catalog.
- **Max feedback latency:** ~13 seconds (quick) / ~180 seconds (full wave gate, carried forward from Phase 2's measurement — same file, same config).

---

## Requirements → Test Map

Seeded from research. Task IDs are filled in by `/gsd-plan-phase` once PLAN.md files exist;
this table is the authoritative source for what each requirement must prove.

| Req ID | Behavior | Test Type | Automated Command | File Exists |
|--------|----------|-----------|-------------------|-------------|
| SYNC-03 | PR #161 (`16af425c...`) remains an ancestor of HEAD | scripted check (git, not pytest) | `git merge-base --is-ancestor 16af425c053c306a658c96e254b4c4114338dd11 HEAD` — re-run against the HEAD active at execution time, not this research's HEAD (D-02) | ❌ W0 — evidence-script pattern, follow Phase 1/2's `capture_sync_baseline.py`/`git.json` convention |
| CAT-01 | JSON `name` references resolve + JSON `type` fields resolve to a known Python class (links 1 & 4, partial) | unit | `.venv/bin/python -m pytest tests/unit/test_registry_integrity.py -x` | ✅ already covers 2 of 6 links |
| CAT-01 | Every JSON-defined tool name has a corresponding `tools/<Name>.py` file (link 5) | unit | new test fn in `test_registry_integrity.py` | ❌ W0 |
| CAT-01 | Every JSON-defined tool name is imported in `tools/__init__.py` (link 5) | unit | new test fn in `test_registry_integrity.py` | ❌ W0 |
| CAT-02 | No tool name is defined in more than one *live* (non-archived) `data/*.json` file | unit | new duplicate-name test — recursive `data/**/*.json` glob + `default_config.py` category cross-reference (Pitfall 3, catches the live `OxO_*` case) | ❌ W0 |
| CAT-02 | `grep_tools`/`get_tool_info` surface a representative sample of new-upstream and preserved-custom tools | smoke | script reusing `tu grep`/`tu info` (or `ToolUniverse` discovery primitives) against a representative sample that **excludes** tools with unmet `required_api_keys` | ❌ W0 |

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| *(pending — populated from PLAN.md task IDs)* | — | — | — | — | — | — | — | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New test function(s) in `tests/unit/test_registry_integrity.py` covering: (a) every JSON-defined tool name has a corresponding `tools/<Name>.py` file, (b) every JSON-defined tool name is imported in `tools/__init__.py`, (c) no tool name is defined in more than one *live* (non-archived) `data/*.json` file.
- [ ] A duplicate-name check that is `broken_apis/`-aware (recursive glob + `default_config.py` category cross-reference), per Pitfall 3.
- [ ] A smoke test/script exercising `grep_tools` and `get_tool_info` against a representative sample of both new-upstream and preserved-custom tool names, for CAT-02's discoverability criterion. The representative sample must exclude tools with unmet `required_api_keys`.
- [ ] A regeneration-output diff guard (`tools/__init__.py` name-set vs. current HEAD's name-set) per D-06's root-cause finding — any name-count *decrease* is a hard-stop finding, not a self-resolving case. Needed before any Tier-1/Tier-2 regeneration step can be trusted.
- [x] Framework install: none — pytest, ruff, uv, git all present and working (`.venv/bin/python -m pytest` verified passing this session).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Disposition of the concurrent dirty `src/tooluniverse/tools/*.py` + `.tool_metadata.json` state (D-06) | CAT-01, CAT-02 | Requires a maintainer decision on provenance (RESEARCH.md Open Question 1) before any automated regeneration step can safely run — research confirmed the state is stale and a regression, but could not determine which command produced it without mutating state, which was explicitly forbidden | Read RESEARCH.md § "Concurrent State Investigation (D-06)"; decide discard (`git restore`) vs. further investigation before Phase 3's own regeneration step begins |
| Whether the `OxO_*` duplicate (Pitfall 3) is hygiene debt or a genuine D-05 collision | CAT-02 | Two defensible dispositions exist (RESEARCH.md Assumption A3); D-05's own posture requires human review for genuine collisions | Read RESEARCH.md § Pitfall 3; confirm `default_config.py`'s commented-out `oxo` category line is intentional, then decide delete-orphan vs. formal collision review |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---

Related: [[03-RESEARCH]] · [[03-CONTEXT]] · [[reference_tu_usage_cheatsheet]] · [[feedback_tu_root_cause_discipline]] · [[feedback_shared_workspace_concurrency_hazard]]
