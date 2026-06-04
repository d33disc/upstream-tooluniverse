# Agentic Ollama Harness — proven recipe (e2e live 2026-06-03T20:30:00.000Z)

FREE local agentic worker for ToolUniverse maintenance. Verified end-to-end: the model wrote a
file and executed it; artifact independently confirmed on disk.

## The working stack

- **Model:** `qwen3.5:35b-a3b-q8_0` (Ollama). MoE, ~3B active params → FAST despite 38GB. FREE, local.
  - CRITICAL: it emits **structured OpenAI `tool_calls`**. `qwen2.5-coder:32b` does NOT (returns the
    call as plain text) — do not use it for agentic work.
- **Harness:** `ralph-specs/ollama_agent.py` — dependency-free ReAct loop. Calls Ollama's
  `/v1/chat/completions` with tools, executes returned tool_calls (write_file/read_file/run_shell/
  finish) confined to `--cwd`, feeds results back, repeats. We built this because the off-the-shelf
  `qwen`/`codex` CLIs did NOT execute Ollama tool_calls over a custom OpenAI base-url (model narrated).
- **System prompt:** `ralph-specs/ollama_worker.system.md` (weak-model-tuned: act-don't-narrate,
  reproduce→verify, skip-when-unsure, status line).

## Run it

```bash
python3 ralph-specs/ollama_agent.py \
  --model qwen3.5:35b-a3b-q8_0 \
  --cwd <work_dir> \
  --system ralph-specs/ollama_worker.system.md \
  --max-steps 12 \
  "the task"
```

Precondition: `ollama serve` running (check `curl -s localhost:11434/api/tags`).

## What didn't work (so future-me doesn't retry)

- `ollama run <model>` plain = text completion, no tool execution.
- `qwen --auth-type openai --openai-base-url localhost:11434/v1` = model emitted tool intentions but
  the CLI did not execute them over the custom endpoint; file never created.
- `qwen2.5-coder:32b` via /v1 returns tool calls as TEXT content, not structured `tool_calls`.

## Next: wire into the overnight loop

Point `ollama_agent.py` at broken tools from `TOOL_HEALTH_REPORT.json`, branch-isolated, one tool
per invocation, loop overnight. Claude verifies the diffs in the morning (see token-savings model).
