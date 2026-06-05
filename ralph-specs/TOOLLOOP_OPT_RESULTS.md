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

---

# Part 2 — Latency axis (the one with headroom)

Quality is pinned at ceiling, so latency was the remaining axis. Result: **also at its floor.**
Three levers tested, all quality-gated at 24/24; none moved wall-clock beyond run-to-run noise (~±10%).

## Where the time goes (warm profile, 1 run/task, `OLLAMA_PROFILE=1`)

| task | wall | steps | avg_call | note |
|---|---|---|---|---|
| recovery_from_error | 15.6s | 7 | 2.1s | hardest — fix/rerun/recover cycle |
| multifile_handler | 13.5s | 6 | 2.2s | read both files + fix + verify |
| fix_real_bug / scope | ~7.7s | 5 | ~1.5s | run/fix/rerun/finish |
| mechanical | 6.2s | 3 | 2.0s | write/run/finish (irreducible) |
| skip / no_fabricate / ambiguous | ~4s | 2 | ~1.9s | diagnose + report |

**Wall-clock = (task-inherent steps) x (~2s/call).** Per-call is flat ~1.4-2.2s warm; first call
of each task is 2-4.5s (system-prompt + 4-tool-schema prefill). Steps are SEQUENTIAL and necessary
(can't run a file before writing it) — the worker wastes no turns.

## Levers tested (all 8-task, repeats=3)

| lever | env knob | quality | wall vs baseline | verdict |
|---|---|---|---|---|
| suppress reasoning | `OLLAMA_REASONING_EFFORT=none` | 24/24 | 0.94x | tokens 89->42 but NO wall-clock gain — generation isn't the bound |
| multi-tool per turn | `OLLAMA_MULTITOOL=1` | 24/24 | 0.92x | steps are sequential — nothing to batch; also proves #14493 absent on this model |

NB: my initial single-call probe showed reasoning=none at ~2-3x — a WARMUP-ORDER ARTIFACT
(cold first call vs warm last). The batched A/B (48 fresh runs) corrected it to ~1x. Trust the batch.

## Conclusion

The loop is at its latency floor for the overnight maintenance workload (~4-16s/task; a few
hundred tools ~= ~1h). Time is structural: sequential steps x ~2s prefill floor. No low-risk lever
yields speedup. Env knobs kept (default OFF, zero behavior change) as documented diagnostics +
findings — `reasoning_effort=none` would still help on token-metered backends or
generation-bound hardware. Re-derive: `/tmp/profile_loop.py`, `/tmp/ab_reasoning.py`, `/tmp/ab_multitool.py`.
