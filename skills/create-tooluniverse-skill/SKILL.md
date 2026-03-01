---
name: create-tooluniverse-skill
description: Create high-quality ToolUniverse skills following test-driven, implementation-agnostic methodology. Discovers tools via MCP, verifies tool APIs before documenting, and produces concise SKILL.md workflow guides with reference files as needed. Use when asked to create new ToolUniverse skills, build research workflows, or develop domain-specific analysis capabilities for biology, chemistry, or medicine. Also invoke devtu-create-tool if required tools are missing.
---

# Create ToolUniverse Skill

Systematic workflow for creating production-ready ToolUniverse skills. A skill is a `SKILL.md` workflow guide that tells Claude agents how to use ToolUniverse tools — it is NOT a Python implementation.

**KEY RULE**: Test tools via MCP BEFORE writing SKILL.md. Skills fail when they document tools that don't exist or use wrong parameter names.

---

## Skill Architecture (What to Create)

A ToolUniverse skill is:
```
skills/tooluniverse-[domain-name]/
├── SKILL.md          (required — the workflow guide)
├── references/       (optional — detailed docs Claude loads on demand)
│   ├── tools.md      (parameter reference for many tools)
│   └── patterns.md   (domain-specific patterns)
└── assets/           (optional — templates Claude uses in output)
    └── skill_template/SKILL.md   (SKILL.md template for this domain)
```

**Do NOT create**: `python_implementation.py`, `QUICK_START.md`, `test_skill.py`, `README.md`, `CHANGELOG.md`, or any auxiliary documentation files. These violate skill-creator guidelines and waste context.

---

## 5-Phase Workflow

```
Phase 1: Understand domain + use cases
Phase 2: Discover & verify tools via MCP (TEST FIRST)
Phase 3: Create missing tools if needed (devtu-create-tool)
Phase 4: Write SKILL.md + reference files
Phase 5: Validate with a real example query
```

---

## Phase 1: Understand Domain

Clarify before starting:
- What analyses should this skill perform?
- Typical input types (gene list, compound name, disease, sample data)?
- Expected output (table, report file, structured data)?
- Related existing skills to learn from?

Check existing skills for patterns:
```
ls skills/tooluniverse-*/SKILL.md
```

Review the closest match (e.g., `tooluniverse-target-research` for protein workflows, `tooluniverse-drug-research` for compound workflows).

---

## Phase 2: Discover & Verify Tools (CRITICAL — Do This Before Writing Anything)

### 2.1 Find Candidate Tools

```
mcp__tooluniverse__find_tools(query="[domain keyword]", limit=20)
mcp__tooluniverse__grep_tools(pattern="[database_name]")
mcp__tooluniverse__list_tools(mode="by_category")
```

Do NOT assume tool names from memory. Verify they exist.

### 2.2 Verify Parameters

For every tool you plan to document:
```
mcp__tooluniverse__get_tool_info(tool_names=["TOOL_NAME"], detail_level="full")
```

Never assume parameters from function names. Common traps:
- `Reactome_map_uniprot_to_pathways` → uses `id`, not `uniprot_id`
- `gwas_get_associations_for_trait` → use `efo_id`, not `disease_trait` text for disease-specific queries
- Many tools require `operation` parameter (SOAP-style)

### 2.3 Execute with Real Data

Test each major tool before documenting it:
```
mcp__tooluniverse__execute_tool(
    tool_name="TOOL_NAME",
    arguments={"param1": "real_entity_id", "size": 5}
)
```

Record: actual parameter names, response structure (`{status,data}` vs direct list vs direct dict), edge case behaviors.

See `references/tool_testing_workflow.md` for known API quirks (EFO namespace issues, p_value=0.0 edge cases, co-localization patterns, etc.).

### 2.4 Build Parameter Corrections Table

BEFORE writing SKILL.md, document what testing revealed:

| Tool | WRONG (assumed) | CORRECT (verified) |
|------|-----------------|--------------------|
| [tool] | [wrong param] | [correct param] |

---

## Phase 3: Create Missing Tools (If Needed)

If critical functionality has no existing tool, invoke `devtu-create-tool`:
- Required functionality completely absent
- Alternative tools are inadequate workarounds
- Tool would NOT duplicate existing functionality

Skip tool creation if: a similar tool exists, analysis can be restructured, or it would be a minor variant.

After creating tools, verify all 3 registration steps (class → config → wrapper) using `devtu-create-tool` checklist.

---

## Phase 4: Write SKILL.md + Reference Files

### SKILL.md Structure

Follow the template in `assets/skill_template/SKILL.md`. Core principles:

1. **Description (frontmatter)**: This is the trigger mechanism. Include all "when to use" information here, plus trigger phrases, databases, and entity types. The body is only loaded after triggering.

2. **Body ≤ 500 lines**: If approaching this limit, move tool parameter tables and detailed examples to `references/`.

3. **Match interface to execution context**: Choose the right interface for how the skill will be used:
   - LLM agents in MCP clients (Claude Desktop, etc.) → `mcp__tooluniverse__execute_tool`
   - Python scripts / notebooks → Python SDK (`tu.tools.X()` or `ToolUniverse` class)
   - Shell automation / one-off calls → `tu` CLI (`tu run`, `tu find`)
   - Batch processing → Python SDK
   Document which interface the skill targets in the frontmatter description. Old skills using Python SDK code were not wrong per se — they were mismatched to the MCP agent context.

4. **Progressive disclosure**: Keep SKILL.md to the essentials; use `references/` files for detailed tool parameter tables.

5. **Document gotchas explicitly**: Any API quirk discovered in Phase 2 must appear in a "Known Gotchas" section.

**Required sections:**
- Key principles (2-5 bullet points)
- Workflow overview (diagram)
- Phase-by-phase instructions (concrete tool names + what params to use)
- Known gotchas (from Phase 2 testing)
- Tool reference table

**What NOT to include in SKILL.md:**
- Interface-mismatched code (e.g., Python SDK `tu.tools.X()` in a skill targeting MCP agents — or MCP calls in a Python script skill)
- "When to Use This Skill" section in body (belongs in description)
- Glossaries, version history, license, citation sections
- Time estimates

### Reference Files

Use `references/` for content that exceeds SKILL.md budget:

| File | When to Create |
|------|---------------|
| `references/tools.md` | Detailed parameter tables for 10+ tools |
| `references/patterns.md` | Domain-specific interpretation patterns |
| `references/disambiguation.md` | Complex ID resolution procedures |

Reference from SKILL.md: "See `references/tools.md` for complete parameter reference."

---

## Phase 5: Validate with Real Example

After writing SKILL.md, actually execute the workflow on a real query:

1. Pick a concrete example (e.g., "find genes for type 2 diabetes")
2. Follow SKILL.md instructions step by step using `mcp__tooluniverse__execute_tool`
3. Note any gaps, wrong tool names, missing parameters
4. Update SKILL.md with corrections

This validation step has caught: nonexistent tool names, wrong parameter names, missing disambiguation steps, API namespace mismatches.

---

## Quality Checklist

### Before Writing SKILL.md
- [ ] Every tool name verified to exist via `grep_tools`
- [ ] Every parameter name verified via `get_tool_info`
- [ ] At least one `execute_tool` call succeeded for each major tool
- [ ] API quirks documented (namespace issues, 0.0 values, response formats)

### SKILL.md Quality
- [ ] Description includes trigger phrases and all "when to use" info
- [ ] Body ≤ 500 lines (reference files used for overflow)
- [ ] Interface matches execution context (MCP calls for agent skills, SDK/CLI for script skills)
- [ ] No auxiliary docs (QUICK_START.md, README.md, etc.)
- [ ] Concrete tool names + parameters in each workflow phase
- [ ] Known gotchas section covers API quirks found in testing
- [ ] Fallback chain documented for every critical tool

### Completeness
- [ ] Skill handles "no data found" gracefully
- [ ] Disambiguation step before any analysis
- [ ] English-first principle documented
- [ ] Real validation query executed successfully

---

## Common Patterns to Copy From Existing Skills

| Pattern | Good Example Skill |
|---------|-------------------|
| Report-first + progressive update | `tooluniverse-disease-research` |
| Disambiguation + evidence grading | `tooluniverse-target-research` |
| GWAS EFO/MONDO namespace resolution | `tooluniverse-gwas-trait-to-gene` |
| Multi-source search with fallbacks | `tooluniverse-literature-deep-research` |
| Sequence retrieval with accession routing | `tooluniverse-sequence-retrieval` |

---

## References

- **Tool testing workflow + known API quirks**: `references/tool_testing_workflow.md`
- **Implementation-agnostic format guide**: `references/implementation_agnostic_format.md`
- **Standards checklist**: `references/skill_standards_checklist.md`
- **devtu-optimize-skills integration**: `references/devtu_optimize_integration.md`
- **SKILL.md template**: `assets/skill_template/SKILL.md`
