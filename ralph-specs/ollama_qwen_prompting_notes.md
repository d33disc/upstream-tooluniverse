# Ollama + Qwen3.5 Tool-Calling Prompting Notes

Durable research notes for tuning the local-agent system prompt used by
`ralph-specs/ollama_agent.py` (model `qwen3.5:35b-a3b-q8_0` via Ollama's
OpenAI-compatible `/v1/chat/completions`, native structured `tool_calls`).

Retrieved: 2026-06-03T20:42:03.000Z (all web sources fetched within this window).

Cross-refs: [[ollama_worker.system.md]] [[ollama_agent.py]] [[OLLAMA_HARNESS_RECIPE.md]]

---

## Sources (primary first)

- S1 Ollama API tool-calling docs — <https://github.com/ollama/ollama/blob/main/docs/api.md>
- S2 Ollama capability docs (tool calling) — <https://docs.ollama.com/capabilities/tool-calling>
- S3 Qwen function-calling guide (readthedocs) — <https://qwen.readthedocs.io/en/latest/framework/function_call.html>
- S4 Qwen3.5-9B model card (HuggingFace) — <https://huggingface.co/Qwen/Qwen3.5-9B>
- S5 Vendor LLM param quick-reference (Qwen3) — <https://muxup.com/2025q2/recommended-llm-parameter-quick-reference>
- S6 Ollama issue #14493 (Qwen3.5 tool-calling bugs) — <https://github.com/ollama/ollama/issues/14493>
- S7 PromptQuorum: local agents that actually work — <https://www.promptquorum.com/power-local-llm/autonomous-local-agents-actually-work>
- S8 Qwen-Agent repo — <https://github.com/QwenLM/Qwen-Agent>

---

## Key facts (with provenance)

### Sampling / generation params

- Qwen3.5 model card recommends, NON-thinking/instruct general tasks:
  `temperature=0.7, top_p=0.8, top_k=20, min_p=0.0, presence_penalty=1.5, repetition_penalty=1.0`. (S4, S5)
- Thinking-mode general: `temperature=1.0, top_p=0.95, top_k=20, presence_penalty=1.5`;
  precise/coding thinking: `temperature=0.6, top_p=0.95, top_k=20, presence_penalty=0.0`. (S4)
- Qwen explicitly warns: **avoid greedy decoding**; tune `presence_penalty` in 0-2 to stop endless
  repetition (too high → language mixing / quality drop). (S4, S5)
- Community / agent guidance: for deterministic tool calls set `temperature=0` (or near-0) to reduce
  hallucinated arguments. (S7) — This CONFLICTS with the model card's "avoid greedy decoding."
  Practical reconcile: low-but-nonzero temp (0.1-0.2, as the current harness uses 0.1) keeps
  determinism while avoiding pure greedy degeneracy.

### Thinking mode

- Qwen3.5 is thinking-by-default; emits `<think>...</think>` before the answer. (S4)
- Qwen3.5 does NOT support the `/think` `/no_think` soft switches that Qwen3 had — control thinking
  via `chat_template_kwargs={"enable_thinking": False}` / `extra_body`. (S4)
- For reasoning models, do NOT use stopword-based ReAct templates ("Thought:/Action:/Observation:")
  because the model may emit those stopwords inside its thinking, corrupting parsing. Prefer NATIVE
  structured tool calls. (S3)
- Multi-turn history should EXCLUDE prior thinking content — only keep final outputs + tool_calls.
  (S4; default in Qwen's Jinja template.)

### Ollama renderer bugs affecting Qwen3.5 (issue #14493)

- **think-block / tool-call render bug:** assistant message with thinking + tool_calls but no text
  content can render an unclosed `<think>` block, corrupting every later turn. (S6)
- **presence/repetition penalties silently ignored** by the Ollama Go runner — params accepted but
  discarded. So you CANNOT rely on `presence_penalty=1.5` actually applying via Ollama; mitigate
  repetition through prompt + loop guards instead. (S6)
- **missing generation prompt** after a tool-call message can break the round-trip loop. (S6)
- Affected v0.17.1 → master at time of report; "no user-side workaround" beyond code fixes — so
  PIN/track Ollama version and prefer the qwen3-coder tool-parser path where possible. (S6)

### Failure modes + mitigations

- Small/weak models emit prose instead of structured `tool_calls`; reliability is a property of the
  MODEL, not the harness. `qwen2.5-coder:32b` returns calls as plain text — unusable; `qwen3.5:35b-a3b`
  emits real `tool_calls`. (S7 + [[OLLAMA_HARNESS_RECIPE.md]])
- With small models, multi-tool-in-one-response breaks; recommended pattern: call only the FIRST tool
  and drop the rest before the next turn. (S2 secondary / general practice)
- Cap plan horizon to ~5-8 steps; beyond that agents drift, re-read files, repeat searches. (S7)
- Surface tool errors explicitly back into the conversation so the model proposes a corrective step;
  don't silently retry. (S7)
- Add explicit "only call a tool when you need external data you don't already have" to suppress
  gratuitous tool calls. (S7)
- Qwen docs: generation is NOT guaranteed to follow the protocol even with correct templates — write
  defensive parsing for malformed tool calls. (S3)

### Tool definition

- Provide rich `description` per tool + per parameter; type annotations + Google-style docstrings (the
  Python SDK auto-derives schema from them). The description is what the model reads to choose/fill a
  tool. (S2)
- Hermes-style tool format is recommended for Qwen3 family to maximize function-calling performance
  (`--tool-call-parser hermes` in vLLM; qwen3_coder parser as alternative). (S3, S4)
- Loop until `tool_calls` is empty; append each `tool`-role result (with `tool_call_id`) before the
  next request. (S1, S2) — matches current harness's `finish` sentinel tool.

---

## Conflicts noted

- Temperature: model card says avoid greedy (implying >0 sampling); agent practitioners say temp=0
  for determinism. Harness uses 0.1 — a sane middle. Keep low; don't go to exactly 0 if degeneracy
  appears, don't go above ~0.3 for tool work.
- presence_penalty=1.5 is the card's anti-repeat lever but Ollama's Go runner ignores it (S6), so the
  prompt must carry the anti-repeat / anti-loop burden instead.

---

## Deliverable: candidate rules (ranked, tagged by locus)

Tags: [PROMPT] = system-prompt text the optimization loop tunes;
[SAMPLING] = API param in ollama_agent.py; [HARNESS] = loop/code change.

Qwen3.5-via-Ollama specific (highest value):

1. [SAMPLING][HARNESS] Disable thinking in the agentic loop (`enable_thinking=False`) AND verify the
   rendered prompt contains no stray/unclosed `<think>` — non-thinking is more reliable for plain
   function invocation (S4) and dodges the Ollama unclosed-`<think>` multi-turn corruption bug (S6).
   Don't assume Ollama's `/v1` honors the kwarg; confirm by inspecting a turn.
2. [PROMPT] Forbid ReAct/stopword templates ("Thought:/Action:/Observation:"); instruct the model to
   emit a NATIVE structured tool call, never describe the call in prose. (S3 + harness)
3. [HARNESS] Strip prior `<think>` content from multi-turn history; keep only final outputs +
   tool_calls + tool results. (S4)
4. [SAMPLING] temperature 0.1-0.2 (current 0.1 OK); top_p=0.8, top_k=20. Low-but-nonzero, NOT 0 and
   NOT >0.3 — with thinking off and short JSON outputs, greedy-degeneracy barely applies, so low
   determinism is coherent. (S4 reconciled with S7)
5. [SAMPLING] Do NOT rely on presence_penalty/repetition_penalty via Ollama — the Go runner silently
   ignores them (S6). Carry anti-repeat via #1, #6, low temp instead, not this knob.
6. [PROMPT][HARNESS] One tool call per turn: instruct "call exactly one tool, then wait for its
   result"; if the model returns several, execute only the first and drop the rest. (S2 + S6 round-trip
   fragility)
7. [PROMPT] "Only call a tool when you need data/effect you don't already have" — suppresses
   gratuitous calls that waste steps. (S7)
8. [PROMPT] Define a single explicit finish/stop convention (the harness `finish` tool + a single
   `STATUS:` line) and forbid trailing prose after it, so loop termination is unambiguous. (S1/S2 loop;
   harness)

Generic agent guards (include, ranked lower):

1. [HARNESS] Cap steps to ~5-8; break on empty/repeated output to stop drift-loops. (S7)
2. [PROMPT][HARNESS] Surface tool errors verbatim back to the model and ask for a corrective step;
    never silent-retry. (S7)
3. [PROMPT] Rich per-tool and per-parameter descriptions; literal arg names — the description is what
    the model reads to fill the call. (S2)
4. [PROMPT] Anti-narration: "use tools to actually act; never print code and assume it ran; report
    only real tool output" — already in v1, keep. (harness v1 + S7)
5. [PROMPT] What NOT to include: no chain-of-thought scaffolding, no "first think step by step" (Qwen
    thinks natively; redundant CoT inflates tokens and risks stopword leakage), no multi-tool batch
    instructions. (S3, S4)
