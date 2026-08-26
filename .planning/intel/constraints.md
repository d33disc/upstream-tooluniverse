# Constraints

## Patent Tier 1 implementation scope
- source: docs/superpowers/plans/2026-04-17-patent-tools-tier1.md
- type: protocol
- content:
  DATA_e28df000_START
  | Field         | Value                                                        |
  |---------------|--------------------------------------------------------------|
  | Goal          | 6 USPTO patent tools + 1 base class for FTO analysis         |
  | Architecture  | JSON-config tools, XML parser, DSAPITool base, batch pipeline |
  | Tech Stack    | Python 3.12, httpx, lxml, ToolUniverse tool framework        |
  DATA_e28df000_END

## USPTO provider policy
- source: docs/superpowers/specs/2026-04-17-patent-tools-tier1-design.md
- type: protocol
- content:
  DATA_34e06313_START
  **PatentsView is dead.** The API migrated to ODP on 2026-03-20. All
  PatentsView endpoints return 404. Do not build against it.
  DATA_34e06313_END

## USPTO assignment endpoint
- source: docs/superpowers/specs/2026-04-17-patent-tools-tier1-design.md
- type: api-contract
- content:
  DATA_a6273d4e_START
  **Assignment endpoint is singular.** `/assignment` returns 200.
  `/assignments` returns 403. The Swagger docs are misleading.
  DATA_a6273d4e_END

## USPTO claims extraction
- source: docs/superpowers/specs/2026-04-17-patent-tools-tier1-design.md
- type: protocol
- content:
  DATA_0239b3b6_START
  **No dedicated claims endpoint.** ODP does not expose patent claims as
  structured data. The workaround is to download grant XML via
  `associated-documents` and parse the `<claims>` element.
  DATA_0239b3b6_END

## USPTO deep-lookup rate limiting
- source: docs/superpowers/specs/2026-04-17-patent-tools-tier1-design.md
- type: nfr
- content:
  DATA_1c717b66_START
  Includes rate limiting (burst=1, 4 req/s
  default) and structured multi-patent output for FTO analysis.
  DATA_1c717b66_END

## DSAPITool base contract
- source: docs/superpowers/specs/2026-04-17-patent-tools-tier1-design.md
- type: api-contract
- content:
  DATA_315678d7_START
  Abstract base class for Office Action DSAPI endpoints. Handles:

  - POST request construction with Lucene query syntax
  - Pagination (offset/limit)
  - Response normalization
  - Error handling for the DSAPI-specific error format
  DATA_315678d7_END

## Two-phase upstream merge
- source: docs/superpowers/plans/2026-04-17-upstream-sync.md
- type: protocol
- content:
  DATA_52ab2042_START
  **Architecture:** Two-phase staged merge on a feature branch. Phase 1 merges upstream/main. Phase 2 merges PR #161's branch. Each phase resolves conflicts, runs tests, and commits before proceeding.
  DATA_52ab2042_END

## Canonical upstream conflict resolution
- source: docs/superpowers/plans/2026-04-17-upstream-sync.md
- type: protocol
- content:
  DATA_63cba8c5_START
  The resolution strategy is: take upstream's version for canonical tool definitions (`--theirs`), manually merge structural files where we have custom additions.
  DATA_63cba8c5_END

## Preserve custom code during upstream sync
- source: docs/superpowers/specs/2026-04-17-upstream-sync-design.md
- type: protocol
- content:
  DATA_5173903d_START
  For all conflicts: keep our custom code, layer in upstream additions. Never drop our
  lines.
  DATA_5173903d_END

## Upstream-sync success criteria
- source: docs/superpowers/specs/2026-04-17-upstream-sync-design.md
- type: nfr
- content:
  DATA_cf648a05_START
  1. All 4 conflict files resolved with both sides' content preserved
  2. `pytest` passes (same or better than current pass rate)
  3. New upstream tools load correctly (`grep_tools`, `get_tool_info` spot checks)
  4. Plugin directory present and structurally intact
  5. Our custom code unchanged (git diff confirms no regressions)
  DATA_cf648a05_END

## Six-link tool registration chain
- source: docs/dev_docs/Tool_Registration_Chain.md
- type: protocol
- content:
  DATA_b4def736_START
  An AI adding tools must create or update ALL 6. The order matters —
  each link references the previous one.
  DATA_b4def736_END

## Tool-definition JSON contract
- source: docs/dev_docs/Tool_Registration_Chain.md
- type: schema
- content:
  DATA_1625c97e_START
  This is the source of truth. Defines name, type, description,
  parameters, return schema, required API keys, and test examples.
  DATA_1625c97e_END

## Python tool implementation contract
- source: docs/dev_docs/Tool_Registration_Chain.md
- type: api-contract
- content:
  DATA_1bf2b96c_START
  - `@register_tool("MyToolType")` string must EXACTLY match `"type"` in the JSON
  - `__init__` must accept `tool_config` as first arg
  - `run` must accept `arguments` dict, return a dict
  DATA_1bf2b96c_END

## Registration naming contract
- source: docs/dev_docs/Tool_Registration_Chain.md
- type: protocol
- content:
  DATA_862359f1_START
  The JSON file is named after the category. The module is named after
  the tool type. The stub is named after the tool name. Keep them
  straight.
  DATA_862359f1_END

## USPTO ODP authentication
- source: docs/dev_docs/USPTO_ODP_API_Reference.md
- type: api-contract
- content:
  DATA_26df0632_START
  All requests require an API key in the `X-API-KEY` header.
  DATA_26df0632_END

## USPTO ODP rate limits
- source: docs/dev_docs/USPTO_ODP_API_Reference.md
- type: nfr
- content:
  DATA_4db23fc7_START
  | Quota              | Limit                   |
  |--------------------|-------------------------|
  | Metadata per week  | 5,000,000 requests      |
  | Documents per week | 1,200,000 requests      |
  | Burst              | 1 concurrent request    |
  | Sustained rate     | 4-15 requests/second    |
  | Reset              | Sunday 00:00 UTC        |
  DATA_4db23fc7_END

## USPTO application response wrapper
- source: docs/dev_docs/USPTO_ODP_API_Reference.md
- type: schema
- content:
  DATA_c1c55d96_START
  All application endpoints return a `patentFileWrapperDataBag` wrapper.
  DATA_c1c55d96_END

## USPTO response-type discrepancies
- source: docs/dev_docs/USPTO_ODP_API_Reference.md
- type: schema
- content:
  DATA_f41ac7a6_START
  1. **frameNumber / reelNumber**: Swagger shows `string`, but the API returns
     `integer`. Parse accordingly.

  2. **correspondenceAddress**: Swagger shows an `array`, but the API returns a
     single `object`. Do not iterate over it.
  DATA_f41ac7a6_END

## Transcriptformer input schema
- source: docs/tools/remote/transcriptformer.md
- type: schema
- content:
  DATA_28dd393c_START
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `disease` | string | Yes | Disease/dataset identifier (e.g., "follicular_lymphoma") |
  | `state` | string | Yes | Disease state context ("normal", "disease_name", etc.) |
  | `cell_type` | string | Yes | Cell type context for embeddings |
  | `gene_names` | List[str] | Yes | Gene identifiers (symbols or Ensembl IDs) |
  DATA_28dd393c_END

## Transcriptformer output schema
- source: docs/tools/remote/transcriptformer.md
- type: schema
- content:
  DATA_daf9645f_START
  The tool returns a JSON object with the following structure:
  DATA_daf9645f_END

## Transcriptformer MCP transport
- source: docs/tools/remote/transcriptformer.md
- type: protocol
- content:
  DATA_b13b2853_START
  - **Host**: `0.0.0.0` (accepts connections from any IP)
  - **Port**: `7002` (configured to avoid conflicts with other tools)
  - **Transport**: `streamable-http`
  - **Mode**: Stateless HTTP for scalability
  DATA_b13b2853_END
