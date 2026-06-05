#!/usr/bin/env python3
"""Minimal dependency-free agentic executor for local Ollama models.

Why this exists: Ollama (qwen3.5:35b-a3b) returns *structured* OpenAI tool_calls,
but the off-the-shelf CLIs don't execute them over a custom endpoint. This closes
the loop: call -> if tool_calls: execute (confined to --cwd) -> feed results -> repeat.

Usage:
  python3 ollama_agent.py --model qwen3.5:35b-a3b-q8_0 --cwd /path \
      --system worker.system.md --max-steps 12 "the task"
"""

from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# Env-gated profiling: OLLAMA_PROFILE=1 prints per-call latency to stderr (no behavior change).
_PROFILE = os.getenv("OLLAMA_PROFILE")
# Env-gated multi-tool turns: OLLAMA_MULTITOOL=1 lifts the one-tool-per-turn cap to batch
# independent actions (fewer round-trips). Default OFF — the cap is #14493 insurance; only
# lift it if the 8-task suite confirms quality holds.
_MULTITOOL = os.getenv("OLLAMA_MULTITOOL")

OLLAMA = "http://localhost:11434/v1/chat/completions"

# Reasoning suppression. On Ollama's /v1 OpenAI-compat endpoint, `think=false` and
# `enable_thinking` are IGNORED; only `reasoning_effort` is honored (probed 2026-06-05).
# "none" halves completion tokens (~89->42) and ~2-3x's per-call latency. Off by default
# until the 8-task suite confirms it holds 24/24; set OLLAMA_REASONING_EFFORT=none to A/B.
_REASONING_EFFORT = os.getenv("OLLAMA_REASONING_EFFORT")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file (path relative to the working dir).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file's contents (path relative to the working dir).",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command in the working dir. Returns stdout, stderr, exit code.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": "Call when done. Provide the final status line.",
            "parameters": {
                "type": "object",
                "properties": {"status": {"type": "string"}},
                "required": ["status"],
            },
        },
    },
]


def _safe(cwd: Path, p: str) -> Path:
    """Confine a path to the working dir."""
    full = (cwd / p).resolve()
    if cwd.resolve() not in full.parents and full != cwd.resolve():
        raise ValueError(f"path escapes working dir: {p}")
    return full


def execute(name: str, args: dict, cwd: Path) -> str:
    try:
        if name == "write_file":
            f = _safe(cwd, args["path"])
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(args["content"])
            return f"wrote {f} ({len(args['content'])} bytes)"
        if name == "read_file":
            return _safe(cwd, args["path"]).read_text()[:4000]
        if name == "run_shell":
            r = subprocess.run(
                args["command"],
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return f"exit={r.returncode}\nSTDOUT:\n{r.stdout[:3000]}\nSTDERR:\n{r.stderr[:1500]}"
        if name == "finish":
            return "FINISH:" + args.get("status", "")
        return f"unknown tool {name}"
    except Exception as e:  # noqa: BLE001
        return f"ERROR: {e}"


import re

_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)


def strip_think(text: str) -> str:
    """Drop reasoning blocks from assistant content before it re-enters history.

    Defensive against Ollama bug #14493 (an unclosed <think> in a tool-call turn
    corrupts every later turn). Probed empirically: qwen3.5:35b-a3b via /v1 emits
    no <think> on tool turns today — so this is insurance, not a measured fix.
    """
    text = _THINK.sub("", text)
    return text.split("<think>")[0].strip()  # drop any unclosed trailing block


def call(model: str, messages: list, base_url: str = OLLAMA) -> dict:
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "stream": False,
            # Doc-grounded sampling for tool work (ollama_qwen_prompting_notes.md):
            # low-but-nonzero temp + Qwen3.5 card's top_p/top_k. presence_penalty is
            # omitted on purpose — Ollama's Go runner silently ignores it (bug #14493).
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 20,
            **({"reasoning_effort": _REASONING_EFFORT} if _REASONING_EFFORT else {}),
        }
    ).encode()
    req = urllib.request.Request(
        base_url, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["choices"][0]["message"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3.5:35b-a3b")
    ap.add_argument(
        "--base-url",
        default=OLLAMA,
        help="OpenAI /v1/chat/completions endpoint (Ollama :11434 or MLX :8081)",
    )
    ap.add_argument("--cwd", required=True)
    ap.add_argument("--system", help="path to system-prompt file")
    ap.add_argument("--max-steps", type=int, default=12)
    ap.add_argument("task")
    a = ap.parse_args()
    cwd = Path(a.cwd)
    cwd.mkdir(parents=True, exist_ok=True)
    sysprompt = (
        Path(a.system).read_text() if a.system else "You are a careful coding worker."
    )
    messages = [
        {"role": "system", "content": sysprompt},
        {"role": "user", "content": a.task},
    ]

    for step in range(1, a.max_steps + 1):
        _t = time.time()
        msg = call(a.model, messages, a.base_url)
        if _PROFILE:
            print(
                f"[profile] step={step} call={time.time() - _t:.1f}s "
                f"ctx_msgs={len(messages)}",
                file=sys.stderr,
                flush=True,
            )
        calls = msg.get("tool_calls") or []
        if not calls:
            print(f"[step {step}] (no tool call) {msg.get('content', '')[:500]}")
            break
        if not _MULTITOOL:
            calls = calls[:1]  # one tool per turn — round-trip safety (bug #14493)
        messages.append(
            {
                "role": "assistant",
                "content": strip_think(msg.get("content") or ""),
                "tool_calls": calls,
            }
        )
        for tc in calls:
            fn = tc["function"]["name"]
            raw = tc["function"].get("arguments") or "{}"
            args = json.loads(raw) if isinstance(raw, str) else raw
            result = execute(fn, args, cwd)
            print(f"[step {step}] {fn}({json.dumps(args)[:120]}) -> {result[:200]}")
            messages.append(
                {"role": "tool", "tool_call_id": tc.get("id", fn), "content": result}
            )
            if fn == "finish":
                print("DONE:", args.get("status"))
                return
    print("(max steps reached)")


if __name__ == "__main__":
    main()
