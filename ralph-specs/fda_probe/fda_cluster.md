# FDA Cluster Probe — findings (Phase 1.5)

Authored 2026-06-04T14:00:00.000Z. Cross-refs: [[OVERNIGHT_PLAN]]
[[project_ollama_agentic_harness]] [[feedback_recon_durable_data]]
Raw data: `fda_probe_results.json`, `repro_results.json`, `fda_broken.txt`.
Method: authoritative `tu test <name> --json` reproduced on all 82 broken FDA tools,
6 workers (health check used 16 workers / 15s timeout / no retry). One row per tool.

## Headline: the plan's premise is FALSIFIED

The overnight plan assumed "80 FDA tools, likely ONE root cause; one schema/URL fix
greens all 80." **There is no shared code bug. Zero of 82 tools have a code/schema/URL
defect.** The cluster is two *methodology* problems, not a tool problem.

## Verdict tally (per tool, n=82)

| Verdict                  | Count | Class | Ours to fix? |
|--------------------------|-------|-------|--------------|
| PASS on reproduce        | 66    | false-positive | health-check methodology |
| NOT_FOUND (test-drift)   | 13    | C     | yes — fix `test_examples` |
| VALIDATION (bad example) | 1     | C     | yes — fix `test_examples` |
| FDAGSRS HTTP 404/500     | 2     | B     | no — external API (1 stale query, 1 transient) |
| CODE_BUG (EXCEPTION)     | 0     | A     | — none exist |

## Two real root causes

### Root cause 1 — health-check has no transient resilience (66 tools, 80%)

CONFIRMED (read `scripts/tool_health_check.py`): each tool is tested **once, 16 workers,
15s timeout, no retry** — any timeout or transient error flips it straight to "broken."
On reproduction at 6 workers all 66 **pass on reproduce** (what I proved: a single clean
pass; I did not separately measure why they failed at 16:27Z). Whether that run tripped
on openFDA rate-limiting under 16-way concurrency or a one-time upstream outage is NOT
confirmed — but either trigger becomes a permanent "broken" flag because the harness
never retries. Fix belongs to the health-check harness (retry transient HTTP/timeout
before flagging), not to any tool source.

### Root cause 2 — stale / malformed `test_examples` (16 tools)

`tu test` fails a tool if **any** of its examples fail. Each of the 13 NOT_FOUND tools
passes example 1 and fails example 2 — the 2nd canned query string (a snippet of label
section text, e.g. `"reduces hepatic glucose production"`, `"Pharmacodynamics In a"`) no
longer matches any live FDA label, so openFDA correctly returns `NOT_FOUND`. The code is
correct; the test data is stale.

- `FDA_get_drug_names_by_clinical_studies` ex.2 omits the required `indication` param —
  malformed example, not a schema bug.
- `FDAGSRS_get_structure` ex.3 → HTTP 404 (stale substance query); `FDAGSRS_search_substances`
  ex.3 → HTTP 500 (transient, `retryable=true`). External GSRS service, not our code.

## Implication for the harness plan

- **No class-A pilot target exists in the FDA cluster.** The single-biggest-win hypothesis
  is dead. Do not point the worker at FDA expecting code fixes.
- The FDA "fix" is two diffs, both small and both authored by the foreman, not the worker:
  1. Regenerate the 14 stale `test_examples` from live openFDA data (deterministic script).
  2. Add retry-on-transient to the health-check harness before flagging broken.
- **Re-triage the full 535 before any worker pilot.** If 80% of the FDA cluster were
  phantoms, the real broken count is likely far below 535 — but that extrapolation is
  unverified until measured. A retry-aware re-triage IS the corrected health report, so
  actions 1 and 2 below are one job. This is the highest-ROI next step: it tells us
  whether a class-A (real code bug) target population even exists before we build a worker
  to fix it.

## Next actions (smallest first)

1. **Retry-aware re-triage of all 535** (one job = corrected health report + real class
   distribution). Use `fda_probe.py`'s exact-reason classifier, NOT `triage_sweep.py`
   (which misbuckets NOT_FOUND into OTHER_FAIL).
2. Regenerate the 14 stale FDA `test_examples` from live data → those tools go green.
