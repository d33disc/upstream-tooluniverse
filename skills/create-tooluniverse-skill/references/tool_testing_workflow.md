# Tool Testing Workflow

**CRITICAL**: Always test tools BEFORE writing skill documentation.

## Why Test First?

**Real failures show the pattern**: Skills built without testing had 0-20% functionality because of:
- Parameter name mismatches (function name ≠ actual parameter — e.g., `name` vs `query`)
- Wrong tool names (e.g., `OpenTargets_search_gwas_studies_by_disease` doesn't exist)
- SOAP tools missing `operation` parameter
- Response format variations (`{status, data}` vs direct list vs direct dict)
- API quirks: `p_value=0.0` means underflow, not zero; EFO namespace mismatches returning 0 results

## Choose the Right Interface First

Skill documentation style depends on where the skill runs:

| Execution context | Interface to document |
|-------------------|-----------------------|
| LLM agent in MCP client (Claude Desktop, etc.) | `mcp__tooluniverse__execute_tool(...)` |
| Python script / notebook | `tu.tools.X()` or `ToolUniverse` class |
| Shell / one-off calls | `tu run <tool> <args>` CLI |
| Batch processing | Python SDK |

A skill using MCP calls in a Python notebook context, or Python SDK code in an agent-facing SKILL.md, is an **interface mismatch** — not a format or quality issue. Fix it by choosing the correct interface, not by blanket-banning one style.

## Test-First Workflow

```
1. Discover tools → mcp__tooluniverse__find_tools(query="[domain]")
2. Verify tool exists → mcp__tooluniverse__grep_tools(pattern="[tool_name]")
3. Check parameters → mcp__tooluniverse__get_tool_info(tool_names="[tool_name]", detail_level="full")
4. Execute with real data → mcp__tooluniverse__execute_tool(tool_name="[tool]", arguments={...})
5. Document actual behavior → note real parameter names, response format, edge cases
6. THEN write SKILL.md using the appropriate interface for the target context
```

## Step 1: Discover Relevant Tools

```
mcp__tooluniverse__find_tools(query="[domain keyword]", limit=20)
mcp__tooluniverse__grep_tools(pattern="[database_name]")
```

Do NOT assume tool names. Verify they exist before documenting them.

## Step 2: Verify Tool Parameters

```
mcp__tooluniverse__get_tool_info(tool_names=["TOOL_NAME"], detail_level="full")
```

Reveals: actual parameter names, required vs optional, data types. NEVER assume parameter names from function names.

Common surprises:
- `Reactome_map_uniprot_to_pathways` → uses `id` not `uniprot_id`
- `gwas_get_associations_for_trait` → use `efo_id` not `disease_trait` for disease-specific results
- Many tools have `operation` as a required param (SOAP-style)

## Step 3: Execute with Real Data

```
mcp__tooluniverse__execute_tool(
    tool_name="TOOL_NAME",
    arguments={"param1": "real_value", "param2": 10}
)
```

Use real entity IDs (not placeholders). Check:
- Response structure: `{status, data}` vs direct list vs direct dict
- Whether empty results return `[]` or `{"results": []}` or an error
- Whether `p_value = 0.0` means no p-value or floating-point underflow

## Step 4: Document Findings

Create a parameter corrections table BEFORE writing SKILL.md:

| Tool | WRONG (assumed) | CORRECT (tested) |
|------|-----------------|------------------|
| `gwas_get_associations_for_trait` | `disease_trait="Alzheimer's"` | `efo_id="MONDO_0004975"` |
| `OpenTargets_get_variant_credible_sets` | `variant_id="rs429358"` | `variantId="19_44908684_G_C"` |
| `Reactome_map_uniprot_to_pathways` | `uniprot_id="P12345"` | `id="P12345"` |

## Known API Quirks to Watch For

| Quirk | Example | How to Handle |
|-------|---------|---------------|
| EFO/MONDO namespace | EFO_0000249 = 0 results; MONDO_0004975 = 6200 | Always resolve via gwas_search_studies first |
| p_value = 0.0 | GWAS associations with p << 1e-300 | Treat as significant (p < 5e-8) |
| Co-localized genes | APOE/TOMM40/NECTIN2 all share APOE lead SNPs | Report as "APOE locus", not independent |
| Tool doesn't exist | OpenTargets_search_gwas_studies_by_disease | Verify with grep_tools before documenting |
| Direct list response | Some tools return `[...]` not `{status, data}` | Check isinstance before accessing .get() |
| SOAP tools | SAbDab, IMGT, etc. need `operation` param | Check tool definition for `operation` in schema |

## Confidence Signals

**You're ready to write SKILL.md when:**
- Every tool name verified to exist
- Every parameter name verified via get_tool_info
- At least one real execute_tool call succeeded per major tool
- Edge cases (empty results, 0.0 values, wrong namespaces) are documented
