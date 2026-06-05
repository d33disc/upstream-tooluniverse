# Local-LLM Fleet — Portable Playbook

A **fixed-cost-high, marginal-cost-low** machine for autonomous codebase maintenance:
free local models do the bulk drafting in isolated git worktrees; a frontier model
(you) reviews every diff and merges. Built for ToolUniverse, but the core is
project-agnostic — see [Porting](#porting) to template it elsewhere.

> One-line thesis: **spend free local tokens to save scarce frontier tokens and
> protect the frontier's context window — a win that grows with batch size.**

## Architecture

```
queue.jsonl ──> orchestrator.py ──> per task: disposable git worktree
                  │                    └─ worker (ollama_agent.py) drafts autonomously
                  │                    └─ verify_cmd runs (necessary, NOT sufficient)
                  │                    └─ diff captured → results/<id>.json
                  └─ routes each task by `lane` to a tiered backend:
                       hard lane  Ollama 35B  :11434   (deep, reliable, ~45s/task)
                       fast lane  MLX 4B      :8081    (bulk/triage, ~5s/task, ~75% first-pass)
                  NEVER merges / pushes / touches main.  Halts after N consecutive fails.

YOU (frontier) ──> review each diff ──> KEEP (commit+PR) or DISCARD.  ← the only merge gate
```

Files (all in `ralph-specs/`):

- `fleet/orchestrator.py` — queue runner; worktree isolation; lane routing; halt guard.
- `fleet/queue.jsonl` — the work: `{id, lane, base, task, verify_cmd}` per line.
- `ollama_agent.py` — the worker: a dependency-free ReAct loop (`--base-url`, `--model`,
  `--cwd`, `--system`). Tools: write_file/read_file/run_shell/finish, path-confined.
- `ollama_worker.system.md` — the worker's system prompt (9 ABSOLUTE RULES).
- `LOCAL_SWARM_STACK.md` — runtime/model selection + the empirical tool_calls gate.
- `TOKEN_ECONOMICS.md` — when fleet beats direct (the measured crossover).

## The non-negotiable gate

**"The worker's test passed" is NEVER the merge criterion.** Proven necessary here: a worker's
CAS validator passed green but was subtly wrong (`\d{1,6}` vs canonical `\d{2,7}`, false-accepting
malformed input) — only diff review caught it. The verifier catches *broken* output (e.g. the 4B
emitting literal `\n`); the human reviewer catches *green-but-wrong*. You need both.

Corollary: **precise specs prevent green-but-wrong.** When the task spec named the exact bad
input to reject, the worker produced correct code. Review feedback → tighter specs → fewer rejects.

## Capacity math (recompute per machine)

Apple Silicon decode is **memory-bandwidth-bound**, so continuous batching does NOT multiply
throughput. Width comes from **model COPIES, not concurrent slots**:

```
hard_copies ≈ (RAM − OS≈8GB − KV≈8GB) ÷ model_GB     # e.g. (64−16)/24 ≈ 2 on an M1 Max/64GB
true parallelism = separate processes on separate PORTS, not OLLAMA_NUM_PARALLEL
```

Verify on any box: a concurrency sweep (req/s flat as concurrency rises ⇒ one effective lane/copy).

## Setup

```bash
# hard lane (Ollama) — verify the model passes the tool_calls gate first
ollama pull qwen3.5:35b-a3b
# fast lane (MLX, Apple Silicon) — clean env via uv
uv venv /tmp/mlxenv --python 3.12
uv pip install -p /tmp/mlxenv/bin/python mlx-lm huggingface_hub
/tmp/mlxenv/bin/python -m mlx_lm.server --model mlx-community/Qwen3-4B-Instruct-2507-4bit --port 8081 &
# probe tool_calls before trusting any model: send /v1/chat/completions with a tools array,
# require a structured tool_calls response. This is a per-model BINARY gate.
```

## Run

```bash
# edit queue.jsonl, then:
python3 ralph-specs/fleet/orchestrator.py --repo "$PWD" --k 2 --max-steps 15
# review each results/<id>.json diff, then keep (commit+PR) or discard (git worktree remove).
```

Task line: `{"id":"slug","lane":"hard|fast","base":"main","task":"...precise spec...","verify_cmd":"..."}`

## When to use it (token economics)

Fleet is fixed-cost-high, marginal-cost-low. It LOSES on small one-off edits (spec+review
overhead exceeds the generation it offloads) and WINS on large/repetitive/context-busting jobs
(it converts expensive frontier OUTPUT into free local tokens + cheap sampled review, and keeps
the frontier context clean). Measured crossover in `TOKEN_ECONOMICS.md`.

## Porting

The core is project-agnostic. To template into another repo or system-wide:

1. Copy `ralph-specs/ollama_agent.py`, `ollama_worker.system.md`, `fleet/orchestrator.py`.
2. Edit `LANES` in `orchestrator.py` (ports/models) — the only runtime coupling.
3. Write a project `queue.jsonl` with `verify_cmd`s that gate YOUR repo (tests, lint, build).
4. Keep the gate discipline verbatim: disposable worktree · never main/push/merge · halt-on-N.
5. For unattended all-day runs, add a sandbox (sandbox-exec/container) around `run_shell` —
   file tools are path-confined but shell is not.

Nothing in steps 1–2 is ToolUniverse-specific; step 3 is where a project plugs in.

```
```
