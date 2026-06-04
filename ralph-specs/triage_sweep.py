#!/usr/bin/env python3
"""Re-triage the 'broken' tools by REPRODUCING each (the health flag lies —
FDA cluster passes on retry). Buckets every broken tool into a class and captures
the real error, to durable JSONL. Class-A (genuine code/schema bug) is the target.

  .venv/bin/python ralph-specs/triage_sweep.py
Writes: ralph-specs/triage_real.jsonl  (one row per tool) + prints a class tally.
"""

from __future__ import annotations
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "TOOL_HEALTH_REPORT.json"
OUT = ROOT / "ralph-specs" / "triage_real.jsonl"
PY = str(ROOT / ".venv" / "bin" / "python")
WORKERS = (
    6  # low — these are live network tests; high concurrency caused the false fails
)


def classify(name: str) -> dict:
    """Run the same test the health check runs; reproduce twice to catch transients."""
    last = ""
    for attempt in (1, 2):
        r = subprocess.run(
            [PY, "-m", "tooluniverse.cli", "test", name],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=90,
        )
        out = r.stdout + r.stderr
        if "passed" in out and "✓" in out:
            cls = "PASS_NOW" if attempt == 2 else "PASS"
            return {"tool": name, "cls": cls, "attempt": attempt, "err": ""}
        last = out
    low = last.lower()
    # bucket the genuine failures
    if any(
        k in low
        for k in (
            "api key",
            "apikey",
            "credential",
            "unauthorized",
            "401",
            "403",
            "not set",
            "missing key",
        )
    ):
        cls = "MISSING_KEY"
    elif any(
        k in low
        for k in (
            "timeout",
            "timed out",
            "connection",
            "rate limit",
            "429",
            "503",
            "502",
            "temporarily",
        )
    ):
        cls = "NETWORK_TRANSIENT"
    elif any(
        k in low
        for k in (
            "keyerror",
            "typeerror",
            "validationerror",
            "attributeerror",
            "schema",
            "nonetype",
            "traceback",
            "indexerror",
        )
    ):
        cls = "CODE_BUG"  # class-A candidate
    else:
        cls = "OTHER_FAIL"
    # keep the last few lines of the error, durable + greppable
    tail = "\n".join(l for l in last.strip().splitlines() if l.strip())[-1500:]
    return {"tool": name, "cls": cls, "attempt": 2, "err": tail}


def main() -> None:
    rep = json.loads(REPORT.read_text())
    broken = sorted(n for n, v in rep["tools"].items() if v.get("status") == "broken")
    print(f"re-triaging {len(broken)} broken tools, {WORKERS} workers...", flush=True)
    rows = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(classify, n): n for n in broken}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:  # noqa: BLE001
                row = {"tool": futs[f], "cls": "ERROR", "attempt": 0, "err": str(e)}
            rows.append(row)
            if i % 25 == 0:
                print(f"  {i}/{len(broken)}", flush=True)
    OUT.write_text("\n".join(json.dumps(r) for r in rows))
    tally: dict[str, int] = {}
    for r in rows:
        tally[r["cls"]] = tally.get(r["cls"], 0) + 1
    print("\n=== CLASS TALLY ===")
    for k in sorted(tally, key=lambda x: -tally[x]):
        print(f"  {k:18s} {tally[k]}")
    code = [r["tool"] for r in rows if r["cls"] == "CODE_BUG"]
    print(f"\nCODE_BUG (class-A, the real targets): {len(code)}")
    for t in code[:40]:
        print("  -", t)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
