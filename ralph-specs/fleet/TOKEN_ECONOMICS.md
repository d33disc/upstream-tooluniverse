# Fleet vs Direct — Token Economics (measured)

The question: does offloading work to the free local fleet consume fewer or more **frontier**
(billed, quota-capped, context-limited) tokens than the frontier doing the work directly?

Answer: **for bulk/repetitive/context-busting work, far fewer — measured 18.8× on a 20-tool
triage, scaling higher with N.** For small one-off edits, MORE (the spec+review overhead exceeds
the generation offloaded). The fleet is a fixed-cost-high, marginal-cost-low machine.

## The experiment

Classify 20 real broken ToolUniverse tools (from `TOOL_HEALTH_REPORT.json`) into failure
categories. Two cost models, identical task:

- **DIRECT** — the frontier reads each tool's full config+detail (input) and emits a
  classification (output). Proxy: measured config+detail char size ÷ 4, + ~40 out/tool.
- **FLEET** — a local model (MLX Qwen3-4B, fast lane) reads+classifies each for FREE; the
  frontier writes ONE spec and reads back a compact `tool: category` report.

Harness + full per-tool logs: `/tmp/fleet_triage/triage.py`, `triage_log.jsonl`, `summary.json`.

## Measured result (N=20, fast lane, 20.9s wall)

| | DIRECT (frontier) | FLEET (frontier) | FLEET (local, FREE) |
|---|---|---|---|
| tokens | **8,099** | **430** | 8,771 |
| breakdown | 7,299 read configs + 800 classify | 200 spec + 230 read report | the whole job |

**Frontier ratio: 18.8× fewer tokens** with the fleet. The 8,771 tokens of actual reading+
reasoning were absorbed by free local compute; the frontier paid only to *specify* and *skim*.

Triage was also USEFUL once fed the right field (`detail`, not `error`): 18/20 = `timeout`,
1 schema, 1 unknown — i.e. most "broken" tools are transient timeouts, not code bugs (a real
maintenance signal, consistent with the known phantom-failure pattern). NB: a first run that
fed the wrong field returned 15/20 "unknown" — **fleet quality is bounded by input quality**,
not just model capability. Garbage in → unknown out. The token *cost* was identical either way.

## Scaling projection (the real argument)

The frontier spec is fixed; the report scales sub-linearly vs config-reading. Extrapolating the
535 broken tools (or the ~387 manifest figure):

| N tools | DIRECT frontier | FLEET frontier | ratio | DIRECT context impact |
|---|---|---|---|---|
| 20 | 8.1k | 0.43k | 19× | trivial |
| 387 | ~157k | ~5k (200 spec + ~4.8k report) | ~31× | ~140k INPUT floods a 200k window |
| 535 | ~217k | ~6.6k | ~33× | exceeds a single context window |

**The win compounds, and the deeper win is the context window, not the token count.** Direct
triage of 387 tools would pull ~140k tokens of configs into the frontier's working memory —
most of a session's context, spent on reading. The fleet keeps the frontier at ~5k: it never
loads the configs, only the verdicts. Context is the binding constraint on long sessions; the
fleet protects it.

## The crossover

```
Fleet frontier cost ≈ spec(~200, fixed) + report(scales with N, ~12 tok/item, skimmable/sampleable)
Direct frontier cost ≈ Σ read_inputs (OUTPUT-heavy if generating; INPUT-heavy if reading) + Σ reason

Fleet WINS when  Σ(per-task generation or ingestion)  ≫  spec + report
  → large N, long per-task generation, or context-busting inputs.
Fleet LOSES when the task is a small one-off (a 30-line file): writing it directly (~670 frontier
  tokens) beats spec+diff-read+review (~1,340). Measured earlier this session on the validators.
```

## Honest caveats

- Local tokens are free but not instant: 20 tools = 20.9s; 387 ≈ ~7 min on one fast lane. Wall-clock,
  not tokens, is the fleet's real budget — which is the point ("burn local compute all day").
- Fleet quality = input quality × model capability. Thin inputs or a weak model → low-value output
  the frontier must still pay to review. Feed rich inputs; escalate hard cases to the hard lane.
- The frontier still pays a REVIEW tax (sampled, not full) and a REWORK tax on rejects. Both are
  small vs generation, but nonzero — folded into the report-read estimate above.

## Verdict

Wrong tool for a handful of small edits (just do those directly). Right tool — by a large,
measured margin — for the scale jobs it was built for: triage 535 tools, regenerate fixtures
across hundreds of configs, sweep-and-classify. There the fleet is ~30× cheaper in frontier
tokens AND the only option that fits in a context window.
