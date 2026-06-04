# Overnight Local Tool-Fixer — the long plan

Authored 2026-06-03T22:05:00.000Z. Cross-refs: [[project_ollama_agentic_harness]]
[[MODEL_SELECTION.md]] [[ollama_agent.py]] [[ollama_qwen_prompting_notes.md]]
[[OLLAMA_HARNESS_RECIPE.md]] [[project_ralph_health_check]] [[feedback_recon_durable_data]]

## North star

A FREE, local, unattended Ollama worker that fixes genuinely-broken ToolUniverse tools and
produces diffs trustworthy enough that Claude (foreman) merges most of them UNEDITED — so the
maintenance workload stops burning Claude/Max quota.

**The one metric that matters: deflection rate `d`** = (worker diffs accepted unedited) / (total).
Everything below exists to raise `d` while driving the **false-fix rate toward zero** (a worker that
fabricates a green test or "fixes" a missing-key tool is worse than useless).

**The predictive test (Chris's insight, the spine of this plan):** the only eval that predicts
overnight quality is running the chosen model on REAL broken tools and judging whether the diffs are
trustworthy. Toy chores saturate at 15/15 for every competent model — they measure nothing here.

## Definition of DONE (Chris, 2026-06-03T22:20:00.000Z) — non-negotiable

Complete = real bug(s) **found**, **fixed via TDD** (reproduce as a failing test → fix → green;
red-green-refactor), **tested with 100% coverage of the changed code (non-negotiable, measured by
`coverage.py` — a fix without full coverage of its lines/branches is NOT done)**, **lint + type clean
/ error-free**, and **squash-merged to `main` via PR** (feature branch → PR → squash; never
direct-to-main, never upstream). The codebase is **operational and ready for Chris to use at end of
session** — not a branch awaiting review, but merged and green on `main`. "Reviewed diff on a branch"
is a checkpoint, NOT done.

Coverage gate detail: run `coverage run -m pytest <test>` + `coverage report --include=<changed files>`;
require 100% on every line and branch of the code the fix touches. The foreman-authored frozen test is
what drives coverage — the worker fixes source until that test passes AND covers every changed line.

## Anti-gaming: separation of test authorship (Chris, 2026-06-03T22:30:00.000Z)

The entity that writes the test MUST NOT be the entity that writes the fix. Claude (foreman) authors
the **failing test first** (red) — that test IS the spec / answer key. The worker receives it
**read-only** and may edit ONLY the tool source file(s), NEVER the test. Enforcement, defense in depth:

1. Harness path-guard: deny any `write_file` whose path is the frozen test (or any `test_*`/`*_test`).
2. Hash the test file before/after the worker runs; if it changed → reject the attempt outright
   (same sentinel pattern as the eval's `t_scope`).
3. Verification re-runs CLAUDE's untouched test independently; the worker's "it passes" claim is never
   trusted on its own word.

This closes both gaming vectors at once: (a) worker editing the test to pass, (b) worker fabricating a
green result. A fix is real only when an unmodified, foreman-authored test goes green on re-run.

## Scope rule: OUR code only (Chris, 2026-06-03T22:50:00.000Z)

Fix only bugs in code WE control (ToolUniverse source: parsing, schema, param handling, logic, URL
construction). Failures caused by things OUTSIDE our code are NOT ours to fix — skip + document:

- External API down / rate-limited / timeout (e.g. the FDA cluster — proven transient, passes on retry).
- Missing API key / credential / unauthorized.
- Third-party service removed or endpoint gone.

The one nuance that IS ours: if an external API **changed its response format** and our parser breaks
on valid data, fixing our parser is in scope. Decision test: "if the external service is healthy and
authenticated, does our code still fail?" Yes → ours, fix it. No → not ours, skip.

This maps to triage classes: CODE_BUG = ours (fix); MISSING_KEY / NETWORK_TRANSIENT / PASS_NOW = not
ours (skip). Network-free tool types (ComposeTool, PackageTool, DatasetTool) that fail are almost
always ours — the cleanest class-A targets.

## Method (per working-method: MVP-spine-first)

Stand up the crudest end-to-end loop on ONE real tool. Dial it. Then scale. Never perfect a stage
while the pipeline doesn't yet run end-to-end. Validate on real tools BEFORE turning it loose.

---

## Phase 0 — Foundations  [DONE this session, one item open]

- Hardened harness `ollama_agent.py` (sampling top_p/top_k, strip-`<think>`, one-tool-per-turn). ✓
- Model selected + gate-probed: `qwen3.6:35b-a3b` (PASS; SWE-bench 73.4%; fixes incumbent
  `tool_call` regression). Fallback `devstral-small-2:24b`. ✓ (see MODEL_SELECTION.md)
- Eval rig `ollama_promptopt_eval.py` with `--repeats` (pass-RATE). ✓ — but SATURATED; toy only.
- OPEN: confirm 3.6 eval 15/15 on hardened harness (running), then set 3.6 as the default model in
  the harness + recipe + memory.

## Phase 1 — Build the REAL discriminating eval (the heart)

Re-triage the 535 "broken" into three classes by REPRODUCING each (the FDA cluster was a
false-positive that actually returned data — never trust the health flag, reproduce):

- **(A) Code/schema-fixable** — param drift, wrong `return_schema`, bad URL/parsing. Worker SHOULD fix.
- **(B) Missing-key / credential / unreachable** — worker MUST make zero edits + emit `SKIP <reason>`.
- **(C) False-positive / test-drift / transient** — API works; the test example is stale. Worker should
  fix the TEST example or SKIP — never "fix" working code.

Deliverable: a **golden set** of ~6–8 real broken tools spanning A/B/C with a known-correct outcome
each (the answer key). This golden set IS the real eval. Output: durable `golden_set.json` +
`triage_real.md`. Cheap recon — Ollama or Claude-light, capture raw errors to disk first.

## Phase 1.5 — FDA cluster probe (highest ROI, do early)

80 of the broken tools are FDA-family — likely ONE root cause. Reproduce 3–4, find the shared
failure. If one schema/URL fix greens all 80, that single diff is the biggest single win available
and a perfect first real pilot. Capture findings to `fda_cluster.md`.

## Phase 2 — Pilot the spine on ONE real fixable tool (MVP, end-to-end)

Crudest full loop: pick 1 class-A tool → fresh git worktree (isolation) → hand the worker the tool
source + reproduction + failing test → worker fixes → re-run the tool's `test_examples` → if green,
commit to a branch → STOP. Claude reviews the diff by hand. First real `d` data point. Goal here is
ONLY "does the spine run end-to-end and is the diff sane," not coverage.

## Phase 3 — Dial against the real eval (vindicates prompt-opt, now with signal)

Run the chosen model on the full golden set. Score: fixed-correctly / skipped-correctly /
**false-fixes** (the kill metric). Now the prompt optimizer has real signal — tune
`ollama_worker.system.md` against the golden set, not the toy eval. A/B qwen3.6 vs devstral here if
the golden set discriminates. Target: false-fix rate = 0, then maximize correct-fix + correct-skip.

## Phase 4 — The overnight loop (scale, with guardrails)

Queue = re-triaged fixable list. Per tool: fresh worktree → reproduce → fix → **verify green before
commit** → commit to branch → next. Guardrails (make wrong states impossible):

- SKIP on class-B (missing key) — never edit code.
- Hard caps: max-steps, per-tool timeout, **diff-size cap**, scope = only the named file(s).
- Mandatory: tool test passes + lint clean BEFORE commit; unverifiable → SKIP, don't commit.
- Never touch `main`; never push upstream (mims-harvard); per-tool or per-batch branch only.
- Durable timestamped log per attempt (tool, class, action, verify result, diff path). GIGO.
- First run = small batch (~10 tools), not all 297.

## Phase 5 — Morning verification + deflection measurement (Claude = foreman)

Claude reviews the batch: accept→PR / edit / reject. Record `d`. Failures feed back into prompt +
triage. Raise batch size as `d` climbs. This is the token-savings proof, measured not assumed.

## Phase 6 — Productionize / generalize

Cron the overnight run. Apply the FDA root-cause fix across all 80. Escalation tier: tools the local
model can't fix get queued for a paid tier (Qwen/Codex), still off Claude. Parameterize the harvester
for reuse. Roadmap only after `d` is proven on real batches.

---

## Risk register

| Risk | Mitigation |
|------|-----------|
| Worker fabricates a green test | Claude re-runs verification independently; never trust worker's claim |
| Worker fixes the TEST to game the check | Golden set includes this trap; verify vs real API behavior, not just exit code |
| Missing-key tool wrongly "fixed" | Class-B triage first; prompt to SKIP; golden set scores false-fixes |
| Diff too broad / scope creep | diff-size cap + only-named-file scope rule + lint gate |
| Old Ollama 0.24.0 | Upgrade only if a needed model fails to run; 3.6 runs fine today |
| 24/7 thermals on M1 Max | Batch + cap concurrency; not all 297 at once |

## What is DONE vs NEXT

DONE: harness hardened; model chosen+gated; eval rig (saturated→known limitation); research durable.
NEXT (smallest first step): Phase 1.5 FDA probe + Phase 1 golden set → Phase 2 one-tool pilot.
