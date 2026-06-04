#!/usr/bin/env python3
"""Phase 1.5 FDA cluster probe. Runs the authoritative `tu test --json` on each
broken FDA tool, parses per-example failures, buckets by exact root cause.
Writes durable JSON. Reproduce, never trust the health flag."""
import json, subprocess, sys, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = str(ROOT / ".venv" / "bin" / "python")
NAMES = (ROOT/"ralph-specs/fda_probe/fda_broken.txt").read_text().split()

def reason(fail_str: str) -> str:
    s = fail_str.lower()
    if "not_found" in s or "no matches found" in s: return "NOT_FOUND(test-drift)"
    if "not found even after loading" in s or "toolunavailable" in s: return "TOOL_UNREGISTERED"
    if "required property" in s or "validation" in s: return "VALIDATION(bad-example)"
    if "exception" in s or "traceback" in s or "keyerror" in s or "nonetype" in s: return "EXCEPTION(code-bug)"
    if "timeout" in s or "429" in s or "503" in s or "connection" in s: return "NETWORK"
    if "missing key" in s: return "MISSING_KEY(schema)"
    if "result is none" in s: return "RETURNED_NONE"
    if "empty" in s: return "EMPTY"
    return "OTHER"

def probe(name: str) -> dict:
    try:
        r = subprocess.run([PY,"-m","tooluniverse.cli","test",name,"--json"],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as e:
        return {"tool":name,"verdict":"PROBE_ERROR","err":str(e)}
    # the JSON summary is the last json object on stdout
    out = r.stdout.strip()
    try:
        m = re.search(r'\{.*\}\s*$', out, re.S)
        summ = json.loads(m.group(0)) if m else json.loads(out)
    except Exception:
        return {"tool":name,"verdict":"UNPARSEABLE","raw":out[-400:]+r.stderr[-200:]}
    total=summ.get("total"); passed=summ.get("passed"); failed=summ.get("failed")
    reasons=[]
    for t in summ.get("tests",[]):
        if not t.get("passed"):
            fs = " ".join(t.get("failures",[]))
            reasons.append(reason(fs))
    return {"tool":name,"total":total,"passed":passed,"failed":failed,
            "reasons":reasons, "verdict": "PASS" if failed==0 else (reasons[0] if reasons else "FAIL")}

rows=[]
with ThreadPoolExecutor(max_workers=6) as ex:
    futs={ex.submit(probe,n):n for n in NAMES}
    for i,f in enumerate(as_completed(futs),1):
        rows.append(f.result())
        if i%20==0: print(f"  {i}/{len(NAMES)}",flush=True)

rows.sort(key=lambda r:r["tool"])
(Path(ROOT)/"ralph-specs/fda_probe/fda_probe_results.json").write_text(json.dumps(rows,indent=2))

# tally by primary verdict
tally={}
for r in rows:
    tally[r["verdict"]]=tally.get(r["verdict"],0)+1
print("\n=== PRIMARY VERDICT TALLY (per tool) ===")
for k in sorted(tally,key=lambda x:-tally[x]):
    print(f"  {k:24s} {tally[k]}")
# tally every failing-example reason
rt={}
for r in rows:
    for x in r.get("reasons",[]): rt[x]=rt.get(x,0)+1
print("\n=== ALL FAILING-EXAMPLE REASONS ===")
for k in sorted(rt,key=lambda x:-rt[x]):
    print(f"  {k:24s} {rt[k]}")
# tools that PASS on reproduce (false positives)
fp=[r["tool"] for r in rows if r["verdict"]=="PASS"]
print(f"\nFALSE-POSITIVE (pass on reproduce): {len(fp)}")
print(f"wrote fda_probe_results.json")
