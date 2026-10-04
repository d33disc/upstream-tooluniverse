"""Evidence for return_schema decisions made by json3way.py --policy.

For each tool whose schema the merge took from upstream ("theirs"):
  1. live A/B: run the tool on its test_examples, validate the payload (the `tu test`
     rule: success-envelope data, or a bare list) against theirs AND ours;
  2. junk probe: does each schema accept {} / [] / "x" / null / 0 / [{}]?
  3. contract check: is the tool named in tests/? Then its schema is a tested
     contract -- never flip it without running those tests (2026-10-03: 6 FAERS
     flips broke 3 upstream tests).

Flip candidate = live both_pass AND only ours rejects junk AND not named in tests/.
Prints the tally and candidates; writes $SYNC_DIR/ab_results.jsonl. Never edits files.
Usage: SYNC_DIR=... python scripts/upstream_sync/schema_ab.py [--workers 8]
"""

import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import tempfile

import jsonschema

from tooluniverse import ToolUniverse

SYNC_DIR = os.environ.get("SYNC_DIR", tempfile.gettempdir())
JUNK = {"{}": {}, "[]": [], '"x"': "x", "null": None, "0": 0, "[{}]": [{}]}


def validates(schema, payload) -> bool:
    try:
        jsonschema.validate(payload, schema)
        return True
    except jsonschema.ValidationError:
        return False


def live_verdict(tu, tool, theirs, ours) -> str:
    examples = (tu.all_tool_dict.get(tool) or {}).get("test_examples") or []
    ran = []
    for args in examples[:2]:
        try:
            result = tu.run_one_function({"name": tool, "arguments": args})
        except Exception:  # noqa: BLE001 - an exception is simply "no evidence"
            continue
        envelope = isinstance(result, dict) and result.get("status") == "success"
        if envelope or (isinstance(result, list) and result):
            payload = result.get("data") if envelope else result
            ran.append((validates(theirs, payload), validates(ours, payload)))
    if not ran:
        return "no_live_result"
    t_ok, o_ok = all(t for t, _ in ran), all(o for _, o in ran)
    return {
        (True, True): "both_pass",
        (True, False): "theirs_only",
        (False, True): "ours_only",
        (False, False): "both_fail",
    }[(t_ok, o_ok)]


def named_in_tests(tool: str) -> bool:
    r = subprocess.run(["git", "grep", "-q", "-w", tool, "--", "tests"], check=False)
    return r.returncode == 0


def main() -> None:
    workers = (
        int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    )
    decisions = [
        d
        for d in json.load(open(os.path.join(SYNC_DIR, "decisions.json")))
        if d["rule"] == "schema->theirs"
    ]
    tu = ToolUniverse()
    tu.load_tools()

    def assess(d):
        tool = re.search(r"\[(.+?)\]\.return_schema$", d["where"]).group(1)
        weak = sorted(
            k
            for k, v in JUNK.items()
            if validates(d["theirs"], v) and not validates(d["ours"], v)
        )
        return {
            "tool": tool,
            "live": live_verdict(tu, tool, d["theirs"], d["ours"]),
            "theirs_only_accepts_junk": weak,
            "tested_contract": named_in_tests(tool),
        }

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(assess, decisions))
    with open(os.path.join(SYNC_DIR, "ab_results.jsonl"), "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)

    tally: dict = {}
    for r in rows:
        tally[r["live"]] = tally.get(r["live"], 0) + 1
    print("live:", json.dumps(tally))
    flip = [
        r["tool"]
        for r in rows
        if r["live"] == "both_pass"
        and r["theirs_only_accepts_junk"]
        and not r["tested_contract"]
    ]
    print(f"flip-to-ours candidates ({len(flip)}):", " ".join(sorted(flip)))
    print(
        "ours_only (strong flip evidence):",
        " ".join(r["tool"] for r in rows if r["live"] == "ours_only") or "-",
    )
    print(
        "both_fail (merged schema wrong, review):",
        " ".join(r["tool"] for r in rows if r["live"] == "both_fail") or "-",
    )


if __name__ == "__main__":
    main()
