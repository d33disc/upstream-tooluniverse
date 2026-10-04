"""Structural 3-way merge for conflicted tool-config JSON files.

Reads stages :1 (base) :2 (ours) :3 (theirs) from the index. Tool lists are keyed by
"name"; dicts merge per key, recursively. A leaf changed differently on both sides is a
real conflict: recorded, and the file is left unresolved for a human.
Usage: python json3way.py [--policy] [--write] <file>...
  --policy  resolve double-rewritten return_schema to theirs (whole), union
            test_examples, other leaf clashes to theirs; every call is logged
  --write   write resolved files, git add them, and dump the log to
            $SYNC_DIR/decisions.json (default: $TMPDIR) for schema_ab.py
"""

import json
import os
import subprocess
import sys
import tempfile

SYNC_DIR = os.environ.get("SYNC_DIR", tempfile.gettempdir())

MISSING = object()
conflicts: list[str] = []


def stage(n: int, path: str):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else MISSING


def is_tool_list(v) -> bool:
    return isinstance(v, list) and all(isinstance(t, dict) and "name" in t for t in v)


def merge(base, ours, theirs, where: str):
    if ours == theirs:
        return ours
    if ours == base:
        return theirs
    if theirs == base:
        return ours
    if all(isinstance(x, dict) for x in (ours, theirs)) and (
        base is MISSING or isinstance(base, dict)
    ):
        return merge_dict(base if base is not MISSING else {}, ours, theirs, where)
    if all(is_tool_list(x) for x in (ours, theirs)) and (
        base is MISSING or is_tool_list(base)
    ):
        return merge_tools(base if base is not MISSING else [], ours, theirs, where)
    if POLICY:
        decisions.append(
            {"where": where, "rule": "leaf->theirs", "ours": ours, "theirs": theirs}
        )
        return theirs
    conflicts.append(where)
    return ours


decisions: list[dict] = []


def resolve_key(k, b, o, t, where):
    """Policy for one tool key changed on both sides; None = no policy, recurse."""
    if o == t or o == b or t == b or o is MISSING or t is MISSING:
        return None
    if k == "return_schema":
        decisions.append(
            {"where": where, "rule": "schema->theirs", "ours": o, "theirs": t}
        )
        return t
    if k == "test_examples" and isinstance(o, list) and isinstance(t, list):
        return t + [x for x in o if x not in t]
    return None


POLICY = "--policy" in sys.argv


def merge_dict(base, ours, theirs, where):
    out = {}
    for k in list(ours) + [k for k in theirs if k not in ours]:
        b, o, t = base.get(k, MISSING), ours.get(k, MISSING), theirs.get(k, MISSING)
        r = resolve_key(k, b, o, t, f"{where}.{k}") if POLICY else None
        if r is not None:
            out[k] = r
            continue
        v = merge(b, o, t, f"{where}.{k}")
        if v is not MISSING:
            out[k] = v
    return out


def merge_tools(base, ours, theirs, where):
    b = {t["name"]: t for t in base}
    o = {t["name"]: t for t in ours}
    t_ = {t["name"]: t for t in theirs}
    order = [t["name"] for t in ours] + [n for n in t_ if n not in o]
    out = []
    for n in order:
        v = merge(
            b.get(n, MISSING), o.get(n, MISSING), t_.get(n, MISSING), f"{where}[{n}]"
        )
        if v is not MISSING:
            out.append(v)
    return out


def main() -> None:
    write = "--write" in sys.argv
    clean = dirty = 0
    for path in [a for a in sys.argv[1:] if not a.startswith("--")]:
        before = len(conflicts)
        merged = merge(stage(1, path), stage(2, path), stage(3, path), path)
        if len(conflicts) == before:
            clean += 1
            if write:
                raw = subprocess.run(
                    ["git", "show", f":3:{path}"], capture_output=True, text=True
                ).stdout
                second = raw.split("\n")[1] if "\n" in raw else "  "
                indent = len(second) - len(second.lstrip(" ")) or 2
                with open(path, "w") as f:
                    f.write(json.dumps(merged, indent=indent, ensure_ascii=False))
                    if raw.endswith("\n"):
                        f.write("\n")
                subprocess.run(["git", "add", path], check=True)
        else:
            dirty += 1
    print(f"clean={clean} conflicted={dirty}")
    for c in conflicts:
        print("CONFLICT", c)
    for d in decisions:
        print("DECIDED", d["rule"], d["where"])
    if write:
        with open(os.path.join(SYNC_DIR, "decisions.json"), "w") as f:
            json.dump(decisions, f, indent=1)


main()
