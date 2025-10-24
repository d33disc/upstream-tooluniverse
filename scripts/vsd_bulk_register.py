#!/usr/bin/env python3
import json, re
from pathlib import Path
from tooluniverse.vsd_tool import VerifiedSourceRegisterTool

VSD_HOME = Path.home() / ".tooluniverse" / "vsd"
CATALOG = VSD_HOME / "catalog" / "vsd_catalog_candidates.json"

def looks_api_like(ep: str) -> bool:
    if not ep: return False
    e = ep.lower()
    return e.startswith("http") and ("api." in e or "/api/" in e or "graphql" in e or e.endswith(".json"))

def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_")
    return s[:60] if s else "src"

def main():
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))
    builder = VerifiedSourceRegisterTool(tool_config={})

    count = 0
    for m in rows:
        ep = m.get("endpoint")
        if not looks_api_like(ep):
            continue

        dom = (m.get("domain") or "unknown").lower()
        label = m.get("label") or dom
        # Make a mostly-unique, repeatable name
        base = f"vsd_{slugify(dom)}_{slugify(label)}"
        tool_name = base if len(base) <= 80 else base[:80]

        cand = {
            "domain": dom,
            "label": label,
            "endpoint": ep,
            "license": m.get("license", "unknown"),
            "score": float(m.get("trust", 0.7)),      # just carry through
            "registry": m.get("registry", "catalog"),
        }

        out = builder.run({
            "candidate": cand,
            "tool_name": tool_name,
            "description": f"Auto-generated VSD tool for {label}",
            # parameter_overrides optional; we keep the generic schema
        })

        if not out.get("registered"):
            print(" failed:", tool_name, out)
            continue

        count += 1
        if count % 50 == 0:
            print(f"…registered {count} tools so far")

    print(f" Done. Registered ~{count} tools. See {VSD_HOME/'generated_tools.json'}")

if __name__ == "__main__":
    main()
