# ToolUniverse — agent guidance

2,722 scientific tools (life science, literature, patents, clinical, chemistry)
across 605 categories. All tools are reachable through every transport; the
difference between surfaces is how much context the agent spends discovering.

## Entry points

- tooluniverse-discover (MCP, compact mode): THE entry for agents blind to the
  catalog. Exposes 4 proxy tools (list_tools, grep_tools, get_tool_info,
  execute_tool) plus find_tools (semantic). Everything else is reachable via
  execute_tool.
- tooluniverse (MCP, full mode): all tools exposed directly. Only use when the
  agent already knows the catalog — 2,722 schemas flood the context.
- tu CLI: same primitives, any shell (tu find, tu grep --field description,
  tu info, tu run <tool> '<json args>' --raw).
- REST: http://127.0.0.1:8011/api/call (list methods via /api/methods).

## Blind-agent research protocol

1. **Semantic sweep FIRST, before any docs**: call find_tools with the
   research question in natural language. This converts the 2,722-tool space
   into a shortlist of 5-10 candidates in one call. Run one sweep per
   research facet. get_tool_info then fills in only what is relevant.
2. **Breadth backstop**: grep_tools(keywords, field=description) if the sweep
   missed something; list_tools(category=...) only within a suspected
   category. Never enumerate the full catalog.
3. **Depth**: get_tool_info on each candidate. Read the test_examples — they
   are live-verified usage and teach the argument shape fastest. Return
   schemas are hardened (required keys live-derived), so output shape is
   predictable before the first call.
4. **Plan, then execute**: one tool per subtask. execute_tool(name, args)
   with argument names copied exactly from get_tool_info. Parse
   {status, data, error_details}; error_details.retriable tells you whether
   to retry.
5. **Evidence rule**: tu is transport, never authority. Cite the underlying
   API (api.uspto.gov, UniProt, IntAct, ...) in every report. Errors are real
   signal now — read them.

Meta-rules: three calls per tool max (sweep -> info -> execute). Respect
vendor limits (USPTO per-URI quota, NIM job latency, TDC Dataverse outages) —
note and move on, do not hammer. Chain outputs between tools (search result
IDs feed get-by-id tools).
