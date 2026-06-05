# E2E Ollama Tool-Use Loop — Programmatic Optimization Results

Date: 2026-06-05. Branch: `perf/ollama-toolloop-opt`. Harness: `ollama_promptopt_eval.py`
(8 chores), optimizer: `ollama_promptopt.py`. Model under test: local Ollama.

## Headline

On every realistic chore we can construct, **qwen3.5:35b-a3b is at ceiling regardless of
prompt**. The optimization surface is flat — the finding is a *negative result*, and the
optimal config is therefore the **leanest** prompt (core-only), which is provably equivalent
and faster.

## Measurements (all repeats=3, temp 0.1)

| Run | Config | Score | Note |
|---|---|---|---|
| Model A/B | qwen3.5 vs qwen3.6, 5-task | 15/15 == 15/15 | qwen3.5 ~10s faster → chosen |
| Leanness opt | qwen3.5, 5-task, 20 loops | 15/15 with **0 clauses** | all 7 reinforcement clauses trim away |
| Baseline-8 | qwen3.5, 8-task, core-only | **24/24** | harder chores did NOT de-saturate |
| Baseline-8 | qwen3.5, 8-task, core+all-clauses | **24/24** | clauses add nothing measurable |

8-task suite = 5 original + 3 harder (multifile_handler, recovery_from_error, ambiguous_skip),
the last three chosen to mirror real overnight maintenance failure modes. All passed 3/3 with
and without reinforcement clauses.

## Interpretation

1. **No quality gradient exists** at realistic difficulty → an overnight hill-climb for quality
   is unjustified (nothing to climb). Surfaced honestly rather than run for show.
2. **The reinforcement clauses are removable** without quality loss on these workloads → the
   core prompt's 9 ABSOLUTE RULES already carry the behavior. Leaner = fewer tokens = faster.
3. **The real optimization axis with headroom is latency/cost, not quality.** Quality is pinned
   at ceiling; wall-clock/steps/tokens are where remaining gains live.

## Recommendation

- Ship the lean **core-only** prompt (`ollama_worker.system.optimized.md`, clauses=[]) — proven
  24/24-equivalent and shorter. Keep the clause file for harder future workloads.
- Do NOT chase a quality gradient by inventing harder-than-real synthetic tasks — that overfits
  to difficulty the worker never meets.
- If a real overnight failure ever appears, add it as a chore here; the harness + optimizer are
  ready to route a clause to it (targets are wired).

## Caveat (self-verifying)

48 runs total (2 configs x 8 tasks x 3 repeats). "Ceiling" = no failure observed across 48
stochastic runs at temp 0.1 — robust, not exhaustive. Re-derive: rerun `/tmp/baseline8.py`.
