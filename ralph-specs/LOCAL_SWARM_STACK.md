# Local Agent-Swarm Inference Stack — M1 Max 64GB (Metal, arm64)

> Researched + **empirically probed on this exact rig** 2026-06-05. Hardware: Apple M1 Max,
> 64 GB unified memory, 10 cores, 400 GB/s memory bandwidth, 32-core GPU. No CUDA.
> Cross-refs: [[MODEL_SELECTION.md]] [[ollama_agent.py]] [[OVERNIGHT_PLAN.md]]
> [[project_ollama_agentic_harness]]

## TL;DR (the one decision that matters)

On Apple Silicon, **decode is memory-bandwidth-bound, not compute-bound** — so "continuous
batching" does NOT multiply tasks/hour the way it does on an A100. I measured this directly:
firing 1 vs 6 concurrent requests at `qwen3-coder:30b` on Ollama held **aggregate throughput
flat (~62 -> ~72 tok/s, 1.16x)** while per-stream collapsed 61.7 -> 12.0 tok/s. Ollama
time-slices one weight copy; it does not batch on Metal.

**Therefore the concurrency lever on this box is NOT slots-per-copy — it is COPIES.**
You have ~40 GB free after one 24 GB MoE model. The realistic ceiling is **2 full model
copies of a 24 GB MoE running truly in parallel (~2x tasks/hour), or 1 hard-tier copy + a
small 7-9 GB triage copy.** Past that you exhaust bandwidth and RAM, not slots.

Keep the **Ollama swarm you already have** (`ollama_agent.py`). It is the correct, lowest-risk
runtime. Switch to an MLX-batching server only if independent benchmarks later prove >2x Metal
batching — today they don't (see below).

---

## Runtime comparison (Apple Silicon, late 2025 / 2026)

Legend: "true CB" = continuous batching with concurrent slots sharing ONE weight copy and
gaining aggregate throughput on Metal.

| Runtime | (a) True CB on Metal? | (b) OpenAI `/v1` + `tool_calls`? | (c) Realistic concurrency on M1 64GB | (d) Setup |
|---------|----------------------|----------------------------------|--------------------------------------|-----------|
| **Ollama** (current) | **No.** `OLLAMA_NUM_PARALLEL` time-slices one copy; aggregate flat (measured 1.16x @ 6). | **Yes — verified on our rig.** Hermes/Qwen template parses to `tool_calls`. | Scale by COPIES not slots. ~2x via 2 model instances. | `brew install ollama` (have it) |
| **llama.cpp `llama-server`** | Partial. `-cb --parallel N` interleaves slots; real Metal aggregate gain is small/sublinear (bandwidth bound), better prefill batching than decode. | Yes — `/v1/chat/completions`, tool_calls via grammar/template (model-dependent). | Marginally better batching than Ollama; same bandwidth ceiling >27B. | `brew install llama.cpp` (stable 9430, bottled) |
| **MLX / `mlx_lm.server`** | No native CB in stock server (queues). Fastest *single-stream* (~25-130 tok/s by model). | Yes — OpenAI server; tool_calls depends on model chat template. | Best per-stream speed; use for 1 fast copy, not for batching. | `pip install mlx-lm` (have `mlx_lm.server`) |
| **MLX batching servers — `omlx`, `vllm-mlx`** | **Closest thing to true CB on Metal**, but gains are MODEST: independent benchmark shows **omlx ~1.29-1.40x @ concurrency 1->4** (only backend that batched at all). Vendor READMEs claim up to 3.4x — treat as unverified marketing. | Yes — both expose `/v1/chat/completions` + multi-parser tool_calls + MCP. | ~1.3-1.4x per copy (independent) — real but small. Worth piloting only if you want >2 effective workers without a 2nd full copy. | `brew tap jundot/omlx && brew install omlx` · or `pip install vllm-mlx` |
| **LM Studio** | **No.** 0.3.x loads ONE model per server; "for concurrency use Ollama or separate instances." | Yes — `/v1/chat/completions` tool use for tool-tuned models. | Single-request; not a swarm backend. GUI/dev convenience only. | have `lms` CLI |
| **vLLM (upstream)** | **CUDA-class CB is N/A on Mac.** Upstream macOS = **CPU-only, experimental** — unusable for this. | Yes (CPU path). | Effectively no — too slow on CPU. | skip on Mac |
| **vllm-metal** (official plugin, vLLM org) | Plugs vLLM scheduler over an MLX+PyTorch Metal backend; v0.2.0 (Apr 2026) claims big TTFT/throughput jumps. Independent batching gains on Metal still unproven vs the modest MLX numbers above. | Yes — vLLM OpenAI server. | Promising but bleeding-edge; not yet a reason to leave Ollama. | `pip install vllm-metal` (plugin) |

**Three different "vLLM on Mac" — do not conflate:** (1) **vLLM upstream** = CPU-only experimental;
(2) **vllm-metal** = official vLLM-org plugin, MLX/PyTorch Metal backend; (3) **vllm-mlx** =
third-party (waybarrios), MLX-native, "Works with Claude Code." Only (2)/(3) are GPU-real.

**Why batching barely helps here (the physics the task asked for):**
Decode tok/s ≈ memory_bandwidth ÷ bytes_read_per_token. M1 Max = 400 GB/s. You are already near
saturation reading weights, so adding concurrent streams shares the SAME bandwidth — aggregate is
flat. On an A100 (1.5-3 TB/s + huge compute slack) batching gives 3-4x; on Metal it gives ~1.0-1.4x.
**MoE rescues single-stream speed** (A3B reads only ~3B active params/token ≈ 10x fewer bytes ->
~62-130 tok/s) but the batching ceiling is unchanged.

---

## Recommended stack

```
┌──────────────────────── Frontier orchestrator (Claude / human) ────────────────────────┐
│  reviews diffs, assigns tasks, never blocks on local compute                            │
└───────────────┬─────────────────────────────────────────────┬───────────────────────────┘
                │ work queue (file/SQLite + flock, or redis)   │
        ┌───────▼────────┐                            ┌────────▼─────────┐
        │ HARD tier      │  Ollama instance :11434    │ FAST/triage tier │  Ollama :11435
        │ qwen3.6:35b-a3b│  24 GB Q4_K_M              │ qwen3.5:9b       │  7.4 GB
        │ 1 copy         │  ~62 tok/s, PASSES gate    │ 1-2 copies       │  parallel triage
        └────────────────┘                            └──────────────────┘
        free RAM after both copies: ~64 - 24 - 8 - OS(~8) ≈ 24 GB headroom for KV + 2nd fast copy
```

- **Runtime:** **Ollama** (keep). Reason: the only runtime where structured `tool_calls` is
  *empirically verified* on our rig (the MODEL_SELECTION.md hard gate), trivial multi-instance
  scaling, zero migration risk. Batching alternatives buy ≤1.4x — not worth leaving a proven
  tool-call path for an unproven one mid-flight.

- **Concurrency setting & REALISTIC ceiling:**
  `OLLAMA_NUM_PARALLEL=2` per instance (lets short triage calls overlap without starving the
  hard worker), but **drive throughput by running 2-3 Ollama INSTANCES on different ports**, one
  model loaded each. **Ceiling on this exact box ≈ 2 concurrent hard-tier agents (2x tasks/hour)
  OR 1 hard + 2 fast triage agents.** Derivation, re-derivable:
  - ceiling_copies = (RAM − OS − KV) ÷ model_size = (64 − ~8 − ~8) ÷ 24 ≈ **2** hard copies, or
    1 hard (24) + 2 fast (2×7.4) = ~39 GB, leaving ~17 GB for KV/OS.
  - Throughput does NOT rise within a copy (measured flat) -> only copies add tasks/hour.

- **Models (fit 64 GB, strong tool-calling — gate-verified where noted):**

  | Tier | Model | Disk | Active | Native tool-calling | Status |
  |------|-------|------|--------|---------------------|--------|
  | **Hard** | `qwen3.6:35b-a3b` | 24 GB | ~3B (MoE) | Yes, Hermes JSON | **PASS** (gate-proven, MODEL_SELECTION.md) |
  | Hard alt | `qwen3-coder:30b` (A3B) | 18 GB | ~3.3B | Yes, XML `<tool_call>` | RISKY — drops tag >5 tools; have it installed |
  | Hard alt | `devstral-small-2:24b` | 15 GB | dense 24B | Yes, cleanest OpenAI-style | PASS but dense=slower |
  | **Fast/triage** | `qwen3.5:9b` (have it) | 7.4 GB | dense | Qwen template | **probe gate before trusting** — small models drop params |
  | Fast alt | `qwen3-4b` / `qwen3-coder` small | ~3-5 GB | — | Qwen | probe gate first |

  Caveat surfaced by the rig: small models emit malformed `tool_calls` more often — **run the
  one-line gate probe** (does it return structured `tool_calls` not prose) on any fast-tier
  candidate before putting it in 24/7 rotation. `qwen3.6:35b-a3b` is the proven hard-tier anchor.

  Arch note: qwen3.5/3.6 `:35b-a3b` are MoE (A3B) — good single-stream + some batching headroom.
  If a future tag uses GatedDeltaNet/recurrent attention, batching efficiency drops (independent
  benchmark flagged this) — prefer standard-attention MoE for the swarm.

---

## Copy-paste setup

```bash
# --- runtime: already installed; pin a hard worker + a fast triage worker on separate ports ---
ollama pull qwen3.6:35b-a3b          # hard tier (have it)
ollama pull qwen3.5:9b               # fast/triage tier (have it)

# Instance A — hard worker (default port 11434)
OLLAMA_NUM_PARALLEL=2 OLLAMA_MAX_LOADED_MODELS=1 ollama serve   # if not already running

# Instance B — fast triage worker on a second port (own model copy = real parallelism)
OLLAMA_HOST=127.0.0.1:11435 OLLAMA_NUM_PARALLEL=4 \
  OLLAMA_MAX_LOADED_MODELS=1 ollama serve &

# point hard agents at :11434/v1, triage agents at :11435/v1 (OpenAI-compatible, tool_calls)

# --- work queue + fan-out helpers (Homebrew) ---
brew install redis        # durable work queue if you want cross-process claim/ack + retries
brew install util-linux   # provides `flock` for cheap file-lock task claiming (no redis needed)
# GNU `parallel` already installed — fan tasks across the 2 ports:
#   parallel -j2 --joblog /tmp/swarm.log 'python ollama_agent.py --task {} --port 11434' :::: tasks.txt

# --- OPTIONAL pilot: MLX batching server, ONLY if you later want >2 effective workers/copy ---
brew tap jundot/omlx https://github.com/jundot/omlx && brew install omlx   # ~1.3-1.4x measured CB
# or: pip install vllm-mlx && vllm-mlx serve mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit --port 8000
# Probe the tool_call gate on it BEFORE trusting; gains are modest on Metal.

# --- the gate probe (run on ANY new model/runtime before 24/7 use) ---
# Confirms structured tool_calls (not prose). Reuse ollama_agent.py's tool-call assertion.
```

### Homebrew tools that materially help

| Tool | Role in the swarm |
|------|-------------------|
| `parallel` (have it) | fan N tasks across the 2-3 Ollama ports; `--joblog` + `--halt soon,fail=1` |
| `flock` (`brew install util-linux`) | atomic task-claim on a shared file queue — zero-infra, no daemon |
| `redis` (`brew install redis`) | durable queue with claim/ack/retry + dead-letter if you outgrow flock |
| `llama.cpp` (`brew install llama.cpp`) | drop-in `llama-server -cb --parallel N` if you want to A/B Metal batching |

---

## Reasoning recap (why this beats the alternatives)

1. **Measured, not assumed:** Ollama aggregate throughput is flat under concurrency on THIS box
   (1.16x @ 6 streams). Independent third-party benchmark agrees only `omlx` batches at all
   (~1.3-1.4x). Vendor READMEs claiming 3.4x are unverified marketing.
2. **Bandwidth is the wall:** 400 GB/s shared across streams -> batching is sublinear on Metal,
   unlike CUDA. Real concurrency comes from independent weight COPIES, bounded by 64 GB RAM.
3. **Tool-calling is a per-model binary gate** already proven on Ollama for `qwen3.6:35b-a3b`.
   Don't trade a proven path for a ≤1.4x batching gain on an unproven runtime.
4. **MoE (A3B) is the right model class:** ~3B active params -> fast single-stream AND fits two
   copies in 64 GB -> doubles tasks/hour the only way that works here.

## Sources (accessed 2026-06-05)

- Ollama parallelism/`OLLAMA_NUM_PARALLEL`: <https://docs.ollama.com/faq> ·
  <https://www.glukhov.org/llm-performance/ollama/how-ollama-handles-parallel-requests/>
- llama.cpp batching `-cb`/`--parallel`: <https://github.com/ggml-org/llama.cpp/discussions/4130> ·
  Apple Silicon tuning <https://medium.com/@michael.hannecke/tuning-llama-server-on-apple-silicon-9b3e778ab100>
- MLX / mlx-lm server: <https://github.com/ml-explore/mlx-lm> ·
  five-backend independent benchmark (omlx only true CB, 1.29-1.40x): <https://jaesolshin.com/posts/apple-silicon-llm-backends/>
- omlx (continuous batching, brew): <https://github.com/jundot/omlx>
- vllm-mlx (third-party, Claude Code): <https://github.com/waybarrios/vllm-mlx>
- vllm-metal (official plugin): <https://github.com/vllm-project/vllm-metal> ·
  <https://www.docker.com/blog/docker-model-runner-vllm-metal-macos/>
- LM Studio tool use + single-model caveat: <https://lmstudio.ai/docs/developer/openai-compat/tools> ·
  <https://github.com/lmstudio-ai/lms/issues/259>
- Qwen3-Coder-30B-A3B tool-calling/agentic: <https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct>
- M1 Max 400 GB/s bandwidth: <https://www.apple.com/newsroom/2021/10/introducing-m1-pro-and-m1-max-the-most-powerful-chips-apple-has-ever-built/>

---

## Empirical tool_calls gate — multi-arm probe (2026-06-05)

The per-model tool_calls gate, measured on this rig (identical get_weather probe):

| Arm | Runtime | Model | tool_calls | latency | note |
|-----|---------|-------|-----------|---------|------|
| A | MLX (mlx_lm.server :8081) | Qwen3-4B-Instruct-2507-4bit | PASS | 2.4s | clean structured call; FAST |
| B | Ollama :11434 | qwen3.5:35b-a3b | PASS | 13.0s | hard-tier reference |
| C | Ollama :11434 | qwen3-coder:30b | PASS | 12.5s | also gate-PASS |

Decision: **MLX earns the fast/triage lane.** mlx_lm 0.31.3 returns OpenAI structured
tool_calls for Qwen3-Instruct. This unlocks a TRUE concurrent tiered fleet — different
runtimes on different ports run as separate processes/model copies:
  - hard tier:  Ollama qwen3.5:35b-a3b (:11434), serial, deep fixes
  - fast tier:  MLX Qwen3-4B-Instruct-2507-4bit (:8081), quick triage/classification
Memory: 23GB + ~2.5GB = ~26GB resident — fits with room. Both share one GPU but the 4B is light.
Clean MLX env: /tmp/mlxenv (uv, mlx_lm 0.31.3). Model cached. Chat Playground venv is BROKEN
(orphaned python3.13) — do not reuse; the uv env replaces it.
