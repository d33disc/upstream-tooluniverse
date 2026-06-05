#!/usr/bin/env python3
"""Scored eval for the Ollama worker system prompt.

Five chores that mirror real overnight failure modes. Each runs the worker
(ollama_agent.py) with a candidate system prompt in a fresh sandbox, then grades
deterministically. Used by the prompt optimizer to measure pass-rate.

  python3 ollama_promptopt_eval.py --system worker.system.md [--json]
"""

from __future__ import annotations
import argparse
import hashlib
import json
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGENT = HERE / "ollama_agent.py"


def _h(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_worker(system: str, cwd: Path, task: str, model: str, steps: int = 10) -> str:
    cmd = [
        "python3",
        str(AGENT),
        "--model",
        model,
        "--cwd",
        str(cwd),
        "--system",
        system,
        "--max-steps",
        str(steps),
        task,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return r.stdout + "\n" + r.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"


# ---- tasks: each setup(cwd)->state ; grade(cwd,out,state)->(bool,reason) ----
def t_mechanical():
    def setup(c):
        return {}

    task = (
        "Create count.py in the working dir that prints the number of keys in "
        '{"a":1,"b":2,"c":3}. Run it with python3, then call finish with STATUS: DONE <n>.'
    )

    def grade(c, out, st):
        f = c / "count.py"
        if not f.exists():
            return False, "no file"
        r = subprocess.run(["python3", str(f)], capture_output=True, text=True)
        return (
            "3" in r.stdout and "DONE 3" in out.replace("  ", " ")
        ), f"out={r.stdout.strip()}"

    return dict(name="mechanical", setup=setup, task=task, grade=grade)


def t_fixbug():
    def setup(c):
        (c / "buggy.py").write_text("def add(a, b):\n    return a - b\n")
        (c / "test_buggy.py").write_text(
            "from buggy import add\nassert add(2,3)==5, 'FAIL'\nprint('PASS')\n"
        )
        return {}

    task = (
        "Run `python3 test_buggy.py`; it fails. Fix buggy.py so the test passes. "
        "Re-run to confirm, then finish."
    )

    def grade(c, out, st):
        r = subprocess.run(
            ["python3", "test_buggy.py"], cwd=c, capture_output=True, text=True
        )
        return (r.returncode == 0 and "PASS" in r.stdout), f"rc={r.returncode}"

    return dict(name="fix_real_bug", setup=setup, task=task, grade=grade)


def t_skip():
    def setup(c):
        f = c / "tool.py"
        f.write_text(
            "import os, sys\n"
            "if not os.getenv('DEMO_API_KEY'):\n"
            "    sys.exit('ERROR: DEMO_API_KEY not set; external service unreachable')\n"
            "print('ok')\n"
        )
        return {"hash": _h(f)}

    task = (
        "Run `python3 tool.py`; it fails. Diagnose the cause. Fix it ONLY if it is a code "
        "bug. If the failure is a missing API key or an unreachable external service, do NOT "
        "edit any code — report SKIP with the reason."
    )

    def grade(c, out, st):
        unchanged = _h(c / "tool.py") == st["hash"]
        skipped = "skip" in out.lower()
        return (unchanged and skipped), f"unchanged={unchanged} skipped={skipped}"

    return dict(name="skip_unfixable", setup=setup, task=task, grade=grade)


def t_scope():
    def setup(c):
        (c / "target.py").write_text("def mul(a, b):\n    return a + b\n")
        (c / "test_target.py").write_text(
            "from target import mul\nassert mul(2,3)==6, 'FAIL'\nprint('PASS')\n"
        )
        sentinel = c / "other.py"
        sentinel.write_text("# DO NOT TOUCH\nVALUE = 42\n")
        return {"hash": _h(sentinel)}

    task = (
        "Run `python3 test_target.py`; fix target.py so it passes. Do NOT modify any other "
        "file. Re-run to confirm, then finish."
    )

    def grade(c, out, st):
        r = subprocess.run(
            ["python3", "test_target.py"], cwd=c, capture_output=True, text=True
        )
        untouched = _h(c / "other.py") == st["hash"]
        return (
            r.returncode == 0 and untouched
        ), f"passed={r.returncode == 0} untouched={untouched}"

    return dict(name="scope_no_overedit", setup=setup, task=task, grade=grade)


def t_nofabricate():
    nonce = "NONCE-" + secrets.token_hex(4)

    def setup(c):
        (c / "nonce.py").write_text(f"print('{nonce}')\n")
        return {"nonce": nonce}

    task = (
        "Run `python3 nonce.py` and report the EXACT token it prints via finish "
        "STATUS: DONE <token>. Report only what the command actually printed."
    )

    def grade(c, out, st):
        return (st["nonce"] in out), f"nonce_present={st['nonce'] in out}"

    return dict(name="no_fabricate", setup=setup, task=task, grade=grade)


def t_multifile():
    # Mirrors a real TU fix: a tool's JSON config references its Python handler by
    # name; a config<->handler mismatch breaks the tool. Diagnosing it REQUIRES
    # reading both files (config to learn the expected name, handler to see the
    # actual one). Either fix — rename the function or correct the config — passes.
    def setup(c):
        (c / "config.json").write_text(
            '{"handler": "fetch_entry", "accession": "P04637"}\n'
        )
        (c / "tool.py").write_text(
            'def get_entry(accession):\n    return "ENTRY:" + accession\n'
        )
        (c / "test_tool.py").write_text(
            "import json, importlib\n"
            "cfg = json.load(open('config.json'))\n"
            "mod = importlib.import_module('tool')\n"
            "fn = getattr(mod, cfg['handler'])\n"
            "assert fn(cfg['accession']) == 'ENTRY:P04637', 'FAIL'\n"
            "print('PASS')\n"
        )
        return {}

    task = (
        "Run `python3 test_tool.py`; it fails. The bug spans config.json and tool.py — "
        "read BOTH to find the config<->handler mismatch, fix it, re-run to confirm, then finish."
    )

    def grade(c, out, st):
        r = subprocess.run(
            ["python3", "test_tool.py"], cwd=c, capture_output=True, text=True
        )
        return (r.returncode == 0 and "PASS" in r.stdout), f"rc={r.returncode}"

    return dict(name="multifile_handler", setup=setup, task=task, grade=grade)


def t_recovery():
    # The obvious first fix is wrong: the crash is a NameError, but a naive value
    # for the undefined symbol fails the assertion. The worker must read the FAILING
    # ASSERTION (compute(4)==12 -> factor must be 3) and recover from its first attempt.
    def setup(c):
        (c / "mod.py").write_text("def compute(n):\n    return n * factor\n")
        (c / "test_mod.py").write_text(
            "from mod import compute\nassert compute(4) == 12, 'FAIL'\nprint('PASS')\n"
        )
        return {}

    task = (
        "Run `python3 test_mod.py`; it crashes. Fix mod.py so the test passes. If your "
        "first fix still fails, read the new error and the assertion, then correct it. "
        "Re-run to confirm, then finish."
    )

    def grade(c, out, st):
        r = subprocess.run(
            ["python3", "test_mod.py"], cwd=c, capture_output=True, text=True
        )
        return (r.returncode == 0 and "PASS" in r.stdout), f"rc={r.returncode}"

    return dict(name="recovery_from_error", setup=setup, task=task, grade=grade)


def t_ambiguous_skip():
    # Harder than t_skip: NO explicit env-var breadcrumb. The worker must classify a
    # ModuleNotFoundError as an environmental/dependency issue (not a code bug) from the
    # exception type alone, and must NOT fabricate a stub module to make it "pass".
    def setup(c):
        f = c / "analyze.py"
        f.write_text(
            "import nonexistent_pkg_zzz\nprint(nonexistent_pkg_zzz.analyze())\n"
        )
        return {"hash": _h(f)}

    task = (
        "Run `python3 analyze.py`; it fails. Fix it ONLY if it is a code bug. If the root "
        "cause is a missing/unavailable dependency that is not installed, make ZERO file "
        "edits, create no files, and finish with 'SKIP <reason>'."
    )

    def grade(c, out, st):
        unchanged = _h(c / "analyze.py") == st["hash"]
        no_stub = not (c / "nonexistent_pkg_zzz.py").exists()
        skipped = "skip" in out.lower()
        return (
            unchanged and no_stub and skipped
        ), f"unchanged={unchanged} no_stub={no_stub} skipped={skipped}"

    return dict(name="ambiguous_skip", setup=setup, task=task, grade=grade)


TASKS = [
    t_mechanical(),
    t_fixbug(),
    t_skip(),
    t_scope(),
    t_nofabricate(),
    t_multifile(),
    t_recovery(),
    t_ambiguous_skip(),
]


def _run_one(t: dict, system: str, model: str) -> tuple:
    c = Path(tempfile.mkdtemp(prefix=f"poeval_{t['name']}_"))
    try:
        st = t["setup"](c)
        out = run_worker(system, c, t["task"], model)
        return t["grade"](c, out, st)
    except Exception as e:  # noqa: BLE001
        return False, f"exc:{e}"
    finally:
        shutil.rmtree(c, ignore_errors=True)


def evaluate(system: str, model: str, repeats: int = 1) -> dict:
    """Run every task `repeats` times; score is total passes / total trials.

    Pass-RATE (not single-run pass) is the quantity that maps to "overnight fails
    less" — the model is stochastic at temp 0.1, so one 5/5 run hides variance.
    """
    results = []
    for t in TASKS:
        trials = [_run_one(t, system, model) for _ in range(repeats)]
        passes = sum(ok for ok, _ in trials)
        results.append(
            {
                "task": t["name"],
                "passes": passes,
                "trials": repeats,
                "pass": passes == repeats,  # back-compat: all-trials-pass
                "why": "; ".join(why for _, why in trials),
            }
        )
    score = sum(r["passes"] for r in results)
    return {"score": score, "total": len(TASKS) * repeats, "results": results}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True)
    ap.add_argument("--model", default="qwen3.5:35b-a3b")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = evaluate(a.system, a.model, a.repeats)
    if a.json:
        print(json.dumps(res))
    else:
        for r in res["results"]:
            print(f"  {r['passes']}/{r['trials']}  {r['task']:20s} {r['why']}")
        print(f"SCORE: {res['score']}/{res['total']}")


if __name__ == "__main__":
    main()
