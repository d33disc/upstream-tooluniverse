---
name: devtu-auto-discover-apis
description: Automatically discover life science APIs online, create ToolUniverse tools, validate them, and prepare integration PRs. Performs gap analysis to identify missing tool categories, web searches for APIs, automated tool creation using devtu-create-tool patterns, validation with devtu-fix-tool, and git workflow management. Use when expanding ToolUniverse coverage, adding new API integrations, or systematically discovering scientific resources.
---

# Automated Life Science API Discovery & Tool Creation

Discover, create, validate, and integrate life science APIs into ToolUniverse through systematic workflows with human review checkpoints.

## When to Use This Skill

Use this skill when:
- Expanding ToolUniverse coverage in underrepresented domains
- Systematically discovering new life science APIs and databases
- Building a batch of tools from multiple APIs at once
- Identifying gaps in current ToolUniverse tool coverage
- Automating the tool creation pipeline from discovery to PR
- Adding emerging APIs from recent publications or releases

**Triggers**: "find new APIs", "expand tool coverage", "discover missing tools", "add APIs for [domain]"

---

## Four-Phase Workflow

```
Phase 1          Phase 2          Phase 3          Phase 4
Gap Analysis  →  Tool Creation →  Validation    →  Integration
     ↓                ↓               ↓                ↓
Coverage         .py + .json     Validation       Git branch
Report           files           report           + PR ready
(15-30 min)      (30-60 min)     (10-20 min)      (5-10 min)
```

**Human approval gates** are required at:
1. After gap analysis — approve focus areas before creating tools
2. After tool creation — review generated code before validating
3. After validation — confirm results before pushing to git
4. Before PR submission — final review of PR description

---

## Phase 1: Discovery & Gap Analysis

### Step 1.1: Analyze Current Coverage

Load ToolUniverse and list all tools. Categorize each tool by domain using keyword matching:

- **Genomics**: sequence, genome, gene, variant, SNP
- **Proteomics**: protein, structure, PDB, fold, domain
- **Drug Discovery**: drug, compound, molecule, ligand, ADMET
- **Clinical**: disease, patient, trial, phenotype, diagnosis
- **Omics**: expression, transcriptome, metabolome, proteome
- **Imaging**: microscopy, imaging, scan, radiology
- **Literature**: pubmed, citation, publication, article
- **Pathways**: pathway, network, interaction, signaling
- **Systems Biology**: model, simulation, flux, dynamics

Count tools per category and produce a coverage matrix.

### Step 1.2: Identify Gap Domains

Classify gaps by severity:
- **Critical Gap**: fewer than 5 tools (or zero)
- **Moderate Gap**: 5–15 tools but missing key subcategories
- **Emerging Gap**: new technologies not yet represented

Common gap areas as of 2026: single-cell genomics, metabolomics databases, patient registries for rare diseases, somatic/germline variant databases beyond ClinVar, microbial and metagenomic genomics, multi-omics integration platforms, synthetic biology parts/circuits, toxicology, agricultural genomics.

Prioritize gap domains by: research impact, complementarity with existing tools, documentation quality, accessibility (public or simple auth), and active maintenance.

### Step 1.3: Search for APIs in Gap Domains

For each gap domain, run web searches using multiple query patterns:

1. Direct API search: "[domain] API REST JSON", "[domain] database API documentation"
2. Database discovery: "[domain] public database", "list of [domain] databases"
3. Recency filter: "[domain] API 2025 OR 2026"
4. Academic sources: "[domain] database" site:nar.oxfordjournals.org

For each discovered API, extract:
- Base URL and version
- Available endpoints
- Authentication method
- Parameter schemas
- Example requests/responses
- Rate limits and terms of service

### Step 1.4: Score and Prioritize APIs

Score each API candidate on 0–100 points across eight criteria. See [references/tools.md](references/tools.md#api-scoring-matrix) for the full scoring table.

Prioritization thresholds:
- **High Priority (≥70 points)**: Implement immediately
- **Medium Priority (50–69)**: Implement if time permits
- **Low Priority (<50)**: Document for future consideration

### Step 1.5: Generate Discovery Report

Produce a `discovery_report.md` with:
- Executive summary (total APIs found, high-priority count, gap domains addressed)
- Coverage matrix table
- Prioritized API candidates (one section per API: domain, score, base URL, auth, endpoints, rationale, example operations)
- Implementation roadmap by batch

---

## Phase 2: Tool Creation

### Step 2.1: Design Tool Architecture

Prefer the **multi-operation pattern**: one Python class handles all operations for an API, each endpoint gets its own JSON wrapper, and operations are routed via an `operation` parameter. This is future-proof even if the API currently has only one endpoint.

File naming:
- Python: `src/tooluniverse/[api_name]_tool.py`
- JSON: `src/tooluniverse/data/[api_name]_tools.json`
- Config key: `[api_category]` (lowercase, underscores)

### Step 2.2: Implement the Python Tool Class

Write a class that inherits from `BaseTool`, is decorated with `@register_tool("ClassName")`, and implements a `run(arguments)` method that:
- Reads the `operation` parameter and routes to a private handler method
- Returns `{"status": "success", "data": ...}` on success
- Returns `{"status": "error", "error": "..."}` on failure — never raises exceptions
- Sets a timeout (30 seconds) on all HTTP requests
- Handles specific exceptions: `Timeout`, `HTTPError`, `ConnectionError`, and generic `Exception`

For authentication, support these patterns:
- **Public**: no special handling
- **Optional API key**: read from environment variable, include in headers only when set; mention in description as "Rate limits: X req/sec without key, Y req/sec with ENV_VAR_NAME"
- **Required API key**: read from environment variable, raise `ValueError` in `__init__` if absent; set `required_api_keys` in JSON config

See [references/tools.md](references/tools.md#python-class-template) for a full annotated template.

### Step 2.3: Write the JSON Configuration

Each operation needs a JSON entry with:
- `name`: tool name, 55 characters maximum (MCP compatibility)
- `class`: Python class name
- `description`: 150–250 characters covering what it does, return format, input format, a concrete example, and special notes
- `parameter`: JSON Schema object with `required` list and `properties`; use `"const"` for the fixed `operation` value
- `return_schema`: must use `oneOf` with exactly two schemas — a success schema containing a top-level `data` field, and an error schema containing an `error` field
- `test_examples`: list of real parameter objects with no placeholder values (no "TEST", "DUMMY", "EXAMPLE", "your_", etc.)

See [references/tools.md](references/tools.md#json-config-template) for a full annotated template.

### Step 2.4: Find Real Test Examples

Use the "List then Get" strategy:
1. Identify the API's list endpoint
2. Call it and extract a real ID from the response
3. Confirm the ID works in the detail endpoint
4. Use that ID in `test_examples`

If no list endpoint exists, search the API's own documentation, GitHub issues, playground/sandbox, or tutorial articles for sample identifiers.

### Step 2.5: Register in default_config.py

Add an entry to `src/tooluniverse/default_config.py`:

```python
TOOLS_CONFIGS = {
    # ... existing entries ...
    "[api_category]": os.path.join(current_dir, "data", "[api_name]_tools.json"),
}
```

This step is the most commonly forgotten. Tools will silently not load if this entry is missing.

---

## Phase 3: Validation

### Step 3.1: Verify return_schema Structure

For each tool in the JSON file, confirm:
- `return_schema` has a top-level `oneOf` key
- `oneOf` contains exactly two schemas
- The first (success) schema has a `data` field in `properties`
- The second (error) schema has an `error` field and lists it in `required`

### Step 3.2: Check test_examples for Placeholders

Scan all string values in `test_examples` for any of these patterns (case-insensitive): `test`, `dummy`, `placeholder`, `example`, `sample`, `xxx`, `temp`, `fake`, `mock`, `your_`.

If any are found, replace them with real values from the API before proceeding.

### Step 3.3: Verify Three-Step Tool Registration

Run these checks in order:
1. Import the tool module and confirm the class appears in `get_tool_registry()`
2. Check that `TOOLS_CONFIGS` in `default_config.py` contains the API category key
3. Instantiate `ToolUniverse()`, call `load_tools()`, and confirm the expected wrapper attributes exist

All three must pass. A failure at step 1 means the `@register_tool` decorator is missing or broken. A failure at step 2 means `default_config.py` was not updated. A failure at step 3 means the JSON file has errors or the class name doesn't match.

### Step 3.4: Run Integration Tests

Execute `python scripts/test_new_tools.py [api_name] -v` and verify 100% pass rate.

Common failure modes and fixes:
- **404**: Invalid test example ID — find a real one using the "List then Get" strategy
- **Schema mismatch**: Call the API directly, inspect the raw response, update `return_schema` to match
- **Timeout**: Increase timeout or add retry; document API latency in description
- **Parameter error**: Compare parameter names against API documentation; rename fields as needed

### Step 3.5: Generate Validation Report

Write `validation_report.md` including:
- Summary counts (total tools, passed, failed, schema issues)
- Tool loading checklist (3 steps)
- Schema validation status per tool
- Test example status
- Integration test results per tool (status, response time)
- devtu compliance checklist (6 items: loading, API verification, error pattern check, schema validation, real test examples, parameter verification)

---

## Phase 4: Integration

### Step 4.1: Create a Feature Branch

Create a branch named `feature/add-[api-name]-tools` from the current main branch. Verify the working tree is clean before proceeding.

### Step 4.2: Stage and Commit Tool Files

Stage exactly these files (no others):
- `src/tooluniverse/[api_name]_tool.py`
- `src/tooluniverse/data/[api_name]_tools.json`
- `src/tooluniverse/default_config.py`

Write a commit message that summarizes the API name, domain, number of tools added, validation results, and a list of tool names and their purposes.

### Step 4.3: Write the PR Description

The PR description should cover:
- What was added and why (gap domain addressed)
- API information: base URL, documentation URL, auth method, rate limits, license
- Table of tools added (tool name, operation, description)
- Validation results summary (pass counts, schema status, test example status)
- Files changed
- Discovery score and rationale
- Usage examples in plain language (not Python SDK code)
- Checklist: all tests passing, real test examples, no placeholders, names ≤55 chars, default_config.py updated

See [references/tools.md](references/tools.md#pr-description-template) for a full template.

### Step 4.4: Push and Open PR

Push the branch with `-u` flag to set the upstream. Create the PR using `gh pr create` with the prepared description. Provide the PR URL to the human reviewer.

---

## Output Artifacts

| Artifact | Phase | Description |
|---|---|---|
| `discovery_report.md` | 1 | Gap analysis, scored API candidates, roadmap |
| `[api_name]_tool.py` | 2 | Python tool class per API |
| `[api_name]_tools.json` | 2 | Tool configurations per API |
| `validation_report.md` | 3 | Schema, test, and loading results |
| PR description | 4 | Comprehensive PR for human review |

---

## Known Gotchas

### Missing default_config.py Entry
Tools are silently absent from ToolUniverse if the category key is not added. Always check this as the first debugging step when a tool does not appear.

### Placeholder test_examples
The patterns "test", "example", "dummy", "placeholder" cause automated checks to fail and give agents misleading examples. Use the "List then Get" strategy to find real identifiers even when the API documentation does not provide them.

### Non-nullable Optional Parameters
If two parameters are mutually exclusive (provide one or the other), both must have nullable types: `{"type": ["string", "null"]}`. Non-nullable mutually exclusive parameters cause validation errors for roughly 60% of new tools in 2026.

### return_schema Missing oneOf
Omitting the `oneOf` structure or having a success schema without a top-level `data` field causes schema validation to fail. The data wrapper is required even when the API returns a flat object — wrap it: `{"data": flat_object}`.

### Tool Name Length
Names longer than 55 characters break MCP compatibility. Count characters before finalizing JSON configs.

### OAuth Complexity
APIs requiring interactive OAuth flows cannot be fully automated. Document the manual setup steps, store tokens in environment variables, and implement token refresh logic. Consider whether the integration complexity is worth the benefit.

### API Documentation Drift
Endpoint parameters and response shapes often differ from documentation. Always test against the live API and update schemas based on actual responses rather than documented ones.

### Rate Limits During Validation
If testing hits rate limits (HTTP 429), reduce the number of test examples, add an optional API key to get higher limits, or implement exponential backoff. Document rate limits in the tool description.

### _TOOL_ERRORS Persistence in Tests
The `_TOOL_ERRORS` global in `tool_registry.py` persists across test instances in a process. Tests that select `tool_names[0]` can unexpectedly fail if that tool was marked unavailable by a prior test. Use `get_tool_errors()` to filter out unavailable tools when selecting test subjects.

---

## Processing Patterns

### Batch Processing
Process multiple related APIs together: discover all → create all → validate all → submit one PR. Best when APIs share a domain or similar structure.

### Iterative Single-API
Process one API at a time through all four phases before starting the next. Better for complex authentication, novel patterns, or when early failures need investigation before continuing.

### Discovery-Only Mode
Run Phase 1 only to survey the landscape and generate a report. Use to plan a long-term roadmap without committing to implementation immediately.

### Validation-Only Mode
Run Phase 3 only against existing tool files. Use for auditing tool quality, reviewing incoming PRs, or running health checks after upstream API changes.

---

## Abbreviated Tool Reference

| Tool | Purpose |
|---|---|
| `mcp__tooluniverse__grep_tools` | Search tools by name pattern before creating to avoid duplicates |
| `mcp__tooluniverse__find_tools` | Semantic search for tools by intended function |
| `mcp__tooluniverse__list_tools` | Enumerate all tools for gap analysis |
| `mcp__tooluniverse__get_tool_info` | Inspect existing tool schemas and descriptions |
| `mcp__tooluniverse__execute_tool` | Run a tool to verify it works with real parameters |

For full parameter schemas and examples, see [references/tools.md](references/tools.md).

---

## Related Skills

- **`devtu-create-tool`**: Manual single-tool creation; this skill automates it at scale
- **`devtu-fix-tool`**: Diagnose and repair failing tools; use after validation failures
- **`devtu-optimize-descriptions`**: Polish tool descriptions after integration

---

## References

- [references/tools.md](references/tools.md) — API scoring matrix, full Python and JSON templates, PR description template
- [README.md](README.md) — Overview, use cases, quick start
- [example_usage.py](example_usage.py) — Python SDK usage examples
