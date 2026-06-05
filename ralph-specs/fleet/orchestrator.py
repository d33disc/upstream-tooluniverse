#!/usr/bin/env python3
"""Fleet orchestrator: run local-LLM workers on queued tasks in DISPOSABLE git
worktrees, verify, and surface diffs for review.

Safety contract (non-negotiable for unattended operation):
  - each worker runs in its own throwaway worktree off a base ref (isolation)
  - NEVER commits to main, NEVER pushes, NEVER auto-merges
  - the merge gate is human/orchestrator DIFF REVIEW, not the worker's own test —
    a worker's green test does NOT prove the fix correct (green-but-wrong is real)
  - halts after N consecutive verify failures (runaway guard)

  python3 orchestrator.py --repo /path/to/repo --k 1 [--max-steps 15]
Reads queue.jsonl ({id, base, task, verify_cmd}); writes results/<id>.json.

Caveat: the worker's run_shell is path-confined for file tools but shell commands
are NOT sandboxed — true unattended use needs sandbox-exec/container. Worktree +
diff review is the gate for trusted/local tasks.
"""

from __future__ import annotations
import argparse
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGENT = HERE.parent / "ollama_agent.py"
WORKER_SYS = HERE.parent / "ollama_worker.system.md"
WT_ROOT = Path("/tmp/fleet")


def sh(cmd, cwd=None, timeout=900):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def run_task(repo: Path, t: dict, model: str, max_steps: int) -> dict:
    wid = t["id"]
    wt = WT_ROOT / f"wt-{wid}"
    branch = f"fleet/{wid}"
    base = t.get("base", "main")
    # idempotent teardown of any prior run, then a fresh isolated worktree
    sh(["git", "worktree", "remove", "--force", str(wt)], cwd=repo)
    sh(["git", "branch", "-D", branch], cwd=repo)
    rc, _, err = sh(["git", "worktree", "add", "-b", branch, str(wt), base], cwd=repo)
    if rc != 0:
        return {"id": wid, "error": f"worktree add failed: {err.strip()}"}

    # the worker fixes autonomously, confined to its worktree
    t0 = time.time()
    rc, out, err = sh(
        [
            "python3",
            str(AGENT),
            "--model",
            model,
            "--cwd",
            str(wt),
            "--system",
            str(WORKER_SYS),
            "--max-steps",
            str(max_steps),
            t["task"],
        ],
    )
    dur = round(time.time() - t0, 1)

    # the worker's OWN verify (necessary, NOT sufficient — see gate note above)
    vrc = None
    vout = ""
    if t.get("verify_cmd"):
        vrc, vout, _ = sh(["bash", "-lc", t["verify_cmd"]], cwd=wt, timeout=300)

    # stage everything (incl. new files) and capture the diff for REVIEW
    sh(["git", "add", "-A"], cwd=wt)
    _, diff, _ = sh(["git", "diff", "--cached"], cwd=wt)

    return {
        "id": wid,
        "task": t["task"],
        "duration_s": dur,
        "worker_tail": out[-500:],
        "verify_rc": vrc,
        "verify_pass": (vrc == 0) if vrc is not None else None,
        "verify_out": vout[-400:],
        "diff": diff,
        "diff_bytes": len(diff),
        "worktree": str(wt),
        "branch": branch,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument(
        "--k",
        type=int,
        default=1,
        help="orchestration concurrency (GPU serializes inference)",
    )
    ap.add_argument("--model", default="qwen3.5:35b-a3b")
    ap.add_argument("--max-steps", type=int, default=15)
    ap.add_argument(
        "--halt", type=int, default=3, help="halt after N consecutive verify fails"
    )
    a = ap.parse_args()

    repo = Path(a.repo).resolve()
    WT_ROOT.mkdir(parents=True, exist_ok=True)
    (HERE / "results").mkdir(exist_ok=True)
    tasks = [
        json.loads(line)
        for line in (HERE / "queue.jsonl").read_text().splitlines()
        if line.strip()
    ]
    print(
        f"fleet: {len(tasks)} task(s), K={a.k}, model={a.model}, repo={repo}",
        flush=True,
    )

    consecutive_fail = 0
    with ThreadPoolExecutor(max_workers=a.k) as ex:
        futs = {ex.submit(run_task, repo, t, a.model, a.max_steps): t for t in tasks}
        for fut in as_completed(futs):
            res = fut.result()
            (HERE / "results" / f"{res['id']}.json").write_text(
                json.dumps(res, indent=2)
            )
            vp = res.get("verify_pass")
            mark = "PASS" if vp else ("FAIL" if vp is False else "n/a")
            print(
                f"  [{res['id']}] verify={mark}  {res.get('duration_s', '?')}s  "
                f"diff={res.get('diff_bytes', 0)}b  -> results/{res['id']}.json",
                flush=True,
            )
            consecutive_fail = consecutive_fail + 1 if vp is False else 0
            if consecutive_fail >= a.halt:
                print(f"HALT: {a.halt} consecutive verify failures", flush=True)
                break

    print(
        "\nDONE. Nothing merged or pushed. Review each diff in results/, then KEEP "
        "(commit+PR the branch) or DISCARD (git worktree remove --force <wt>).",
        flush=True,
    )


if __name__ == "__main__":
    main()
