#!/usr/bin/env python3
import sys, json, argparse, requests
from pathlib import Path

from tooluniverse.vsd_tool import VerifiedSourceDiscoveryTool, VerifiedSourceRegisterTool

def looks_api_like(endpoint: str) -> bool:
    e = (endpoint or "").lower()
    # purely structural (no domain/topic keywords)
    return ("api." in e) or ("/api/" in e) or e.endswith(".json") or ("graphql" in e)

def pick_best_api_candidate(cands):
    # Prefer endpoints that look like APIs; otherwise fallback to first
    apis = [c for c in cands if looks_api_like(c.get("endpoint",""))]
    return (apis[0] if apis else (cands[0] if cands else None))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("query", type=str)
    p.add_argument("--limit", type=int, default=5)
    args = p.parse_args()

    print(f"\n[1] Running discovery for: {args.query}\n")
    discovery = VerifiedSourceDiscoveryTool(tool_config={})
    disc_out = discovery.run({"query": args.query, "limit": args.limit})
    print("Discovery candidates:\n", json.dumps(disc_out, indent=2))

    cands = disc_out.get("candidates", [])
    cand = pick_best_api_candidate(cands)
    if not cand:
        print("No suitable candidate found.")
        sys.exit(1)

    print(f"\n[2] Chosen candidate: {cand.get('domain')} ({cand.get('endpoint')})\n")

    print("[3] Registering as a tool...")
    registrar = VerifiedSourceRegisterTool(tool_config={})
    tool_name = f"{(cand.get('domain') or 'vsd').replace('.', '_')}_test"
    build_out = registrar.run({
        "candidate": cand,
        "tool_name": tool_name,
        "description": f"Auto-generated test tool for {cand.get('label') or cand.get('domain')}"
    })
    print(json.dumps(build_out, indent=2))

    # Inspect registry
    reg_path = Path(build_out["config_path"])
    spec = None
    tools = json.loads(reg_path.read_text(encoding="utf-8"))
    for t in tools:
        if t["name"] == tool_name:
            spec = t; break

    print("\n[4] Tool spec:\n", json.dumps(spec, indent=2))

    # [5] Live call (basic GET) — no special cases, no api-specific keys here.
    base_url = spec.get("fields", {}).get("base_url")
    if not (base_url and base_url.startswith("http")):
        print("\n[5] Skipping live call (no HTTP base_url).")
        return

    print("\n[5] Live call preview:")
    try:
        r = requests.get(base_url, timeout=20)
        print("Status:", r.status_code)
        print("URL:", r.url)
        ctype = (r.headers.get("Content-Type") or "").lower()
        if "json" in ctype:
            print(json.dumps(r.json(), indent=2)[:4000])
        else:
            print((r.text or "")[:1000])
    except Exception as e:
        print("Live call failed:", e)

if __name__ == "__main__":
    main()
