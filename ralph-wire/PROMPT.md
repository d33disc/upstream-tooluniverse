# Ralph Wire: Health Cache → Tool Finder Integration

You are Ralph. You are a self-coding agent. Your job is to wire the tool health cache into the tool finder so broken tools are filtered out BEFORE recommendation. Work through the task list. Each iteration: pick ONE task, implement it, test it, commit it, exit. If a test fails, fix it in the same iteration. If you can't fix it, revert and document why.

## Context

- `src/tooluniverse/tool_health.py` — existing health cache at `~/.tooluniverse/health.json`
  - `ToolHealthCache().is_live(tool_name)` → True/False/None
  - `ToolHealthCache().warn(tool_name)` → warning string or None
  - `ToolHealthCache().check(tool_name)` → full record dict or None
- Health cache already imported via `tu health --import-manifest TOOL_MANIFEST.json`
- 1,660 live tools, 387 broken tools in cache

## Task List

Work through these in order. Mark each done by committing with the task number.

### Task 1: Annotate results in ToolFinderKeyword.find_tools()

File: `src/tooluniverse/tool_finder_keyword.py`

After keyword search returns results, annotate each tool with its health status. Do NOT filter — just add `_health` and `_health_warning` fields. Tools are being actively fixed, so never hide them permanently.

```python
try:
    from tooluniverse.tool_health import ToolHealthCache
    _cache = ToolHealthCache()
    for tool in results:
        name = tool.get("name", "")
        status = _cache.is_live(name)
        if status is False:
            tool["_health"] = "broken"
            tool["_health_warning"] = _cache.warn(name)
        elif status is True:
            tool["_health"] = "live"
        # None = unknown, don't annotate
except Exception:
    pass  # health cache is optional
```

Test: `python -m tooluniverse.cli grep "PubMed" --json` — results should include `_health` field.

### Task 2: Annotate results in ToolFinderLLM.find_tools()

File: `src/tooluniverse/tool_finder_llm.py`

Same annotation pattern as Task 1. After LLM returns tool recommendations, annotate with health status. Never filter.

### Task 3: Annotate results in SMCP find_tools()

File: `src/tooluniverse/smcp.py`

The MCP `find_tools` at ~line 1145. After `_perform_tool_search`, annotate results with health status. The LLM calling the MCP tool sees the warning and can decide whether to use a broken tool or find an alternative.

### Task 4: Sort healthy tools first

In all 3 finders (Tasks 1-3), after annotating, sort results so live tools appear before broken ones. This is soft prioritization — broken tools still appear, just lower in the list. The LLM naturally picks from the top.

```python
results.sort(key=lambda t: 0 if t.get("_health") != "broken" else 1)
```

### Task 5: Add `--filter-healthy` flag to CLI grep/find/list

File: `src/tooluniverse/cli.py`

Add optional `--filter-healthy` flag that DOES hard-filter broken tools. Default OFF. This is for when the user explicitly wants only working tools. Without the flag, broken tools still appear (annotated).

### Task 6: End-to-end integration test

Write and run a test that:

1. Searches for "adverse event drug safety" tools
2. Verifies known-broken tools (CTD, SIDER) appear WITH `_health: "broken"` warning
3. Verifies known-live tools (FAERS) appear WITH `_health: "live"`
4. Verifies live tools sort before broken ones
5. With `--filter-healthy` flag: broken tools are excluded

```bash
# Without flag: all tools appear, annotated
python -m tooluniverse.cli find "adverse event drug safety" --json

# With flag: only healthy tools
python -m tooluniverse.cli find "adverse event drug safety" --filter-healthy --json
```

### Task 7: Refresh stale health records

Instead of marking dead tools in JSON configs (too permanent), add logic to `tool_health.py`:

- When a tool's health record is older than 7 days, the annotation says `_health: "stale"` instead of `"broken"`
- This signals "was broken, might be fixed now, re-test with `tu health <tool> --refresh`"
- Actively being fixed tools naturally transition from broken → stale → live

### Task 8: GitHub Action for nightly health check

Create `.github/workflows/tool-health.yml` that:

1. Runs nightly at 3am UTC on a cron schedule
2. Installs the repo with `uv pip install -e .`
3. Runs `python -m tooluniverse.cli test <tool>` for every tool with test_examples (use a simple Python loop, 15s timeout per tool)
4. Generates `TOOL_HEALTH_REPORT.json` with pass/fail/timeout counts and per-tool status
5. Commits the report to the repo on a `health-report` branch
6. Opens or updates a single PR with the latest report

This gives a daily, committed, reviewable snapshot of what works. The PR diff shows what changed since yesterday.

Keep the action under 60 minutes (GitHub free tier limit). With ~2,000 tools at 15s max each = worst case 8 hours. So: run only tools that were broken or stale last time (skip known-pass), plus a random 10% sample of passing tools for regression. Target: <30 min.

## Implementation Rules

- Import lazily: `from tooluniverse.tool_health import ToolHealthCache` inside functions, not at module top
- Cache the ToolHealthCache instance — don't create a new one per call
- If health cache doesn't exist or fails to load, silently pass through (no blocking)
- Use `--config pyproject.toml` for ruff. Only touch files you changed.
- NEVER push to upstream. Only commit to feature branch.
- Each task = one atomic commit: `git commit -m "wire(task-N): description"`
- Test EACH change before committing. If test fails, fix or revert.
