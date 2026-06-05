#!/usr/bin/env python3
"""Programmatic system-prompt optimizer for the Ollama worker.

Hill-climbs over reinforcement clauses (promptopt_clauses.json) added to the core
prompt (ollama_worker.system.md), scoring each variant with the eval harness, to
maximize pass-rate / minimize overnight failures. Writes the best variant.

  python3 ollama_promptopt.py --loops 20 [--model ...]
Outputs: ollama_worker.system.optimized.md  +  promptopt_report.md
"""

from __future__ import annotations
import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ollama_promptopt_eval import evaluate, TASKS  # noqa: E402

CORE = HERE / "ollama_worker.system.md"
CLAUSES = HERE / "promptopt_clauses.json"
OUT = HERE / "ollama_worker.system.optimized.md"
REPORT = HERE / "promptopt_report.md"


def compose(core: str, clauses: list, ids: set) -> str:
    extra = [c for c in clauses if c["id"] in ids]
    if not extra:
        return core
    return (
        core
        + "\n\nADDITIONAL DIRECTIVES:\n"
        + "\n".join("- " + c["text"] for c in extra)
    )


def write_tmp(text: str) -> str:
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
    f.write(text)
    f.close()
    return f.name


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--loops", type=int, default=20)
    ap.add_argument("--model", default="qwen3.5:35b-a3b")
    # repeats>=3: the worker is stochastic at temp 0.1, so single-run scores swap on
    # rerun and the hill-climb would chase noise. Pass-RATE over repeats is the signal
    # (see ollama_promptopt_eval.evaluate docstring). Default 1 was the latent bug.
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args()

    core = CORE.read_text()
    clauses = json.loads(CLAUSES.read_text())["clauses"]
    by_id = {c["id"]: c for c in clauses}

    cur = set(by_id)  # start with all reinforcement ON
    best = {"score": -1, "ids": set(), "text": core}
    history = []

    for it in range(1, a.loops + 1):
        text = compose(core, clauses, cur)
        path = write_tmp(text)
        res = evaluate(path, a.model, a.repeats)
        score = res["score"]
        failed = [r["task"] for r in res["results"] if not r["pass"]]
        history.append(
            {
                "iter": it,
                "score": score,
                "total": res["total"],
                "clauses": sorted(cur),
                "failed": failed,
            }
        )
        print(
            f"[loop {it}/{a.loops}] score={score}/{res['total']} "
            f"clauses={len(cur)} failed={failed}",
            flush=True,
        )

        better = score > best["score"] or (
            score == best["score"] and len(text) < len(best["text"])
        )
        if better:
            best = {"score": score, "ids": set(cur), "text": text}

        # ---- targeted hill-climb mutation ----
        if failed:
            # ensure a clause targeting a failed task is included
            add = [
                c
                for c in clauses
                if c["id"] not in cur and set(c["targets"]) & set(failed)
            ]
            if add:
                cur = set(cur) | {add[0]["id"]}
                continue
        # all pass (or nothing to add): try trimming for leanness — drop one, keep best by tracking
        if cur:
            cur = set(cur)
            cur.discard(sorted(cur)[it % len(cur)])

    # persist best
    OUT.write_text(best["text"])
    lines = [
        "# Prompt optimization report",
        "",
        f"- model: {a.model}",
        f"- loops: {a.loops}",
        f"- BEST score: {best['score']}/{len(TASKS) * a.repeats}",
        f"- repeats: {a.repeats}",
        f"- best clauses: {sorted(best['ids'])}",
        f"- output: {OUT.name}",
        "",
        "## progression",
        "",
    ]
    for h in history:
        lines.append(
            f"- loop {h['iter']:2d}: {h['score']}/{h['total']}  "
            f"failed={h['failed']}  clauses={h['clauses']}"
        )
    REPORT.write_text("\n".join(lines))
    print(
        f"\nBEST {best['score']} clauses={sorted(best['ids'])} -> wrote {OUT.name} + {REPORT.name}"
    )


if __name__ == "__main__":
    main()
