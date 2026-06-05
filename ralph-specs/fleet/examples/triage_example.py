#!/usr/bin/env python3
"""Fleet triage experiment — classify N broken ToolUniverse tools on a local lane,
logging EVERY token so we can compare frontier-token cost of fleet-vs-direct.

Direct-cost proxy: the frontier would have to READ each tool's full config+error
(input tokens) and emit a classification (output). We log config+error char size
to estimate that without consuming the orchestrator's context.

Fleet cost: local model does the reading+classifying for FREE (we log its usage);
the frontier only writes one spec + reads the compact report at the end.

Logs: triage_log.jsonl (per-tool) + summary.json. Nothing touches the repo.
"""

import json
import time
import urllib.request
from pathlib import Path

REPO = Path("/Users/davis/code/ToolUniverse")
HEALTH = REPO / "TOOL_HEALTH_REPORT.json"
DATA = REPO / "src/tooluniverse/data"
OUT = Path("/tmp/fleet_triage")
OUT.mkdir(parents=True, exist_ok=True)
N = 20
LANES = [
    (
        "fast-mlx",
        "http://localhost:8081/v1/chat/completions",
        "mlx-community/Qwen3-4B-Instruct-2507-4bit",
    ),
    ("hard-ollama", "http://localhost:11434/v1/chat/completions", "qwen3.5:35b-a3b"),
]
CATEGORIES = "missing_api_key, network_or_external_unreachable, schema_or_config_error, real_code_bug, timeout, unknown"


def pick_lane():
    for name, url, model in LANES:
        try:
            base = url.rsplit("/v1/", 1)[0]
            urllib.request.urlopen(base + "/v1/models", timeout=3)
            return name, url, model
        except Exception:
            continue
    raise SystemExit("no lane reachable (start MLX :8081 or Ollama :11434)")


def build_config_index():
    idx = {}
    for f in DATA.glob("*.json"):
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        if isinstance(data, list):
            for cfg in data:
                if isinstance(cfg, dict) and "name" in cfg:
                    idx[cfg["name"]] = cfg
    return idx


def classify(url, model, tool, error, cfg_snippet):
    prompt = (
        f"A ToolUniverse tool failed its health check. Classify the failure into EXACTLY one "
        f"category from: {CATEGORIES}.\n\n"
        f"Tool: {tool}\nError: {error}\nConfig (truncated): {cfg_snippet}\n\n"
        f'Respond with ONLY JSON: {{"category": "<one category>", "reason": "<max 10 words>"}}'
    )
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": 0.0,
            "max_tokens": 120,
        }
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    t = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.loads(r.read())
    dt = time.time() - t
    msg = resp["choices"][0]["message"].get("content") or ""
    usage = resp.get("usage", {})
    cat, reason = "unknown", ""
    try:
        s = msg[msg.index("{") : msg.rindex("}") + 1]
        parsed = json.loads(s)
        cat, reason = parsed.get("category", "unknown"), parsed.get("reason", "")
    except Exception:
        reason = msg[:60]
    return dt, usage, cat, reason


def main():
    lane, url, model = pick_lane()
    health = json.loads(HEALTH.read_text())
    tools = health.get("tools", {})
    broken = [
        (n, m)
        for n, m in tools.items()
        if isinstance(m, dict) and m.get("status") != "live"
    ][:N]
    idx = build_config_index()

    print(f"lane={lane} model={model}  triaging {len(broken)} broken tools", flush=True)
    log_path = OUT / "triage_log.jsonl"
    log_path.write_text("")
    records = []
    t_all = time.time()
    for i, (tool, meta) in enumerate(broken, 1):
        error = str(
            meta.get("detail") or meta.get("error") or meta.get("status") or ""
        )[:400]
        cfg = idx.get(tool, {})
        cfg_full = json.dumps(cfg)
        cfg_snip = cfg_full[:1200]
        # what DIRECT frontier would ingest: full config + error
        input_chars = len(cfg_full) + len(error)
        try:
            dt, usage, cat, reason = classify(url, model, tool, error, cfg_snip)
        except Exception as e:
            dt, usage, cat, reason = 0.0, {}, "ERROR", str(e)[:80]
        rec = {
            "i": i,
            "tool": tool,
            "lane": lane,
            "input_chars": input_chars,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "wall_s": round(dt, 2),
            "category": cat,
            "reason": reason,
        }
        records.append(rec)
        with log_path.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(
            f"  [{i:2d}/{len(broken)}] {cat:32s} {tool[:40]}  ({usage.get('completion_tokens', 0)}tok {dt:.1f}s)",
            flush=True,
        )

    wall_total = time.time() - t_all
    # the compact report the FRONTIER reads back = tool->category lines
    report = "\n".join(f"{r['tool']}: {r['category']}" for r in records)
    (OUT / "triage_report.txt").write_text(report)

    direct_in = sum(r["input_chars"] for r in records) / 4  # ~4 chars/token
    direct_out = len(records) * 40  # ~40 tok per classification I'd emit
    fleet_local = sum(
        r["prompt_tokens"] + r["completion_tokens"] for r in records
    )  # FREE
    spec_tokens = 200  # one triage spec I write once
    report_tokens = len(report) / 4  # what I read back

    summary = {
        "n": len(records),
        "lane": lane,
        "model": model,
        "wall_total_s": round(wall_total, 1),
        "DIRECT_frontier_tokens": round(direct_in + direct_out),
        "DIRECT_breakdown": {
            "read_configs_in": round(direct_in),
            "classify_out": direct_out,
        },
        "FLEET_frontier_tokens": round(spec_tokens + report_tokens),
        "FLEET_breakdown": {
            "spec_out": spec_tokens,
            "read_report_in": round(report_tokens),
        },
        "FLEET_local_tokens_FREE": fleet_local,
        "frontier_ratio_direct_over_fleet": round(
            (direct_in + direct_out) / max(1, spec_tokens + report_tokens), 1
        ),
        "categories": {
            c: sum(1 for r in records if r["category"] == c)
            for c in {r["category"] for r in records}
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n=== SUMMARY ===", flush=True)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
