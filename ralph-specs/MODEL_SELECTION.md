# Optimal Local Agentic-Coding Model — selection record

Research + empirical probe for the Ollama worker (`ollama_agent.py`). Hardware: Apple M1 Max,
64 GB RAM, 10 cores. Goal: best LOCAL model for unattended 24/7 agentic code-maintenance
(reproduce→diagnose→edit→run→verify→finish) that reliably emits **structured OpenAI `tool_calls`**
over Ollama `/v1/chat/completions`.

Researched: 2026-06-03T21:40:00.000Z (web-grounded; BFCL tool-calling + SWE-bench Verified).
Cross-refs: [[ollama_agent.py]] [[ollama_qwen_prompting_notes.md]] [[OLLAMA_HARNESS_RECIPE.md]]
[[project_ollama_agentic_harness]]

## The #1 hard gate

Structured `tool_calls` emission over Ollama `/v1` is a MODEL property — proven the hard way:
`qwen2.5-coder:32b` FAILS (returns calls as prose), `qwen3.5:35b-a3b` PASSES. Any candidate must
be probed on OUR rig before trusting it for 24/7 runs. Leaderboards rank average quality; this is
a binary capability our pipeline requires.

## Ranked shortlist (sorted by the gate, then SWE-bench)

| Rank | `ollama pull` tag | Disk Q4 | Arch | SWE-bench Verified | Gate (structured tool_calls on Ollama) |
|------|-------------------|---------|------|--------------------|----------------------------------------|
| 1 | `qwen3.6:35b-a3b` | 24 GB | MoE 36B / 3B active | 73.4% | PASS — release explicitly fixes 3.5-line tool-call drops; Hermes JSON |
| 2 | `devstral-small-2:24b` | 15 GB | Dense 24B | 65.8–68.0% | PASS — cleanest OpenAI-style tool_calls; dense = slower |
| 3 | `qwen3-coder:30b` (a3b) | 19 GB | MoE 30.5B / 3.3B active | ~22–52%* | RISKY — XML calls, drops `<tool_call>` tag, prose-in-content above ~5 tools |
| 4 | `gpt-oss:20b` | ~14 GB | MoE 21B / 3.6B active | ~34% | FAIL on Ollama — harmony parser 500s |
| 5 | `glm-4.7-flash` | ~18 GB | MoE 30B / 3.6B active | 59.2% | FAIL via Ollama GGUF — vendor says don't use Ollama (template) |

\* Qwen3-Coder-30B SWE-bench numbers vary wildly by harness; gate-risk dominates regardless.

## TOP PICK: `qwen3.6:35b-a3b` (24 GB Q4_K_M)

Direct successor to our proven `qwen3.5:35b-a3b` — same MoE/3B-active/Hermes-template family, so
lowest-risk path to the gate, PLUS release notes target the exact tool-call edge cases the 3.5 line
stumbled on (InsiderLLM May 2026: "handles nested JSON, missing-parameter errors, and the choice
NOT to call a tool better than the 2.5 line"). 73.4% SWE-bench, fast (3B active), 40 GB headroom.
Pull plain `:35b-a3b` (NOT IQ3 — corrupts function-call JSON; NOT the mxfp8 coding variant).

RUNNER-UP: `devstral-small-2:24b` — safety net if 3.6 regresses on our harness; smallest, cleanest
tool_calls; only demerit is dense (no few-active-params speedup).

## Known Ollama tool-calling bugs by model

- gpt-oss 20b/120b: harmony parser parse failures / 500s on elaborate JSON. Ongoing.
- GLM-4.7-Flash GGUF: vendor says don't run with Ollama (template mismatch).
- Qwen3-Coder-30B: XML output, dropped `<tool_call>` after text, prose-in-content above ~5 tools
  (QwenLM/Qwen3-Coder #475, block/goose #6883). Our harness has 4 tools — under threshold.
- Qwen3.5:35b-a3b (incumbent): documented regression — thinking-only output, malformed `<tool_call>`,
  dropped actions (zeroclaw #3079). This is precisely what 3.6 fixes → reason to upgrade.
- General Qwen on Ollama: use IQ4/Q6, NOT IQ3 (corrupts function-call JSON).

## Cloud-only / won't fit 64 GB — do NOT pull

Qwen3-Coder-Next 80B-A3B (52 GB Q4, over budget), Qwen3-Coder-480B, Kimi-K2 1T, DeepSeek-V3.1 671B,
GLM-4.7/5.1 357B — all cloud-only at usable quants.

## Empirical results on OUR rig (the deciding evidence)

| Model | single-tool gate probe | eval rate (K=3, multi-step) | decision |
|-------|------------------------|------------------------------|----------|
| qwen3.5:35b-a3b (incumbent) | PASS | 15/15 | superseded |
| qwen3-coder:30b | PASS (clean, no XML leak) | 15/15 | rejected — gate-risk under load; no edge |
| qwen3.6:35b-a3b | PASS (clean) | 15/15 | **ADOPTED** — default in harness/eval/promptopt |

**Decision 2026-06-03T22:35:00.000Z:** adopt `qwen3.6:35b-a3b`. The toy eval saturates at 15/15 for
all three competent models (no discrimination — known limitation), so the choice rests on external
evidence (SWE-bench 73.4%, release fixes the 3.5-line tool-call regression) plus our gate probe.
Runs on the existing Ollama 0.24.0 server (no upgrade). Set as default in `ollama_agent.py`,
`ollama_promptopt_eval.py`, `ollama_promptopt.py`. Fallback remains `devstral-small-2:24b`.
The real discriminator (real broken tools) is deferred to OVERNIGHT_PLAN.md Phase 1/2.

Sources: ollama.com/library/{qwen3.6:35b-a3b, devstral-small-2, qwen3-coder:30b}; InsiderLLM
function-calling guide; QwenLM/Qwen3-Coder #475; block/goose #6883; Ollama #11781/#11800;
Unsloth GLM-4.7-Flash; BFCL v3/v4 (Gorilla, pricepertoken).
