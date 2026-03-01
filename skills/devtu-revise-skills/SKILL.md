---
name: devtu-revise-skills
description: Audit and revise existing ToolUniverse skills (SKILL.md files) to fix interface mismatches, wrong tool names, outdated API patterns, extraneous files, and over-length bodies. Use when asked to review, update, or improve existing skills; when a skill fails in practice; when skills contain Python SDK code in MCP-agent context; or when running a batch revision sweep of the skills directory. Distinct from devtu-optimize-skills (which is a principles reference) and create-tooluniverse-skill (which creates from scratch).
---

# Revise ToolUniverse Skills

Systematically audit and rewrite existing skills to match current standards: correct interface for context, verified tool names, real-world tested API patterns, no extraneous files, body ≤500 lines.

**KEY PRINCIPLES**:
1. **Audit before rewriting** — classify every issue before changing anything
2. **Preserve what works** — only fix what's broken or mismatched; don't reformulate correct content
3. **Interface matches context** — MCP calls for agent skills; Python SDK for script skills; `tu` CLI for shell skills
4. **Test to surface real bugs** — running the skill on a real query catches issues static review misses
5. **Document don't delete** — API quirks found during testing go into "Known Gotchas", not the trash

---

## Workflow

```
Phase 0: Triage (scan + prioritize)
Phase 1: Audit (deep read, classify issues)
Phase 2: Verify tools (grep_tools + get_tool_info)
Phase 3: Live test (execute_tool or subagent)
Phase 4: Rewrite SKILL.md + remove extraneous files
Phase 5: Validate (real query against revised skill)
```

---

## Phase 0: Triage

Scan the skills directory to find revision candidates:

```bash
ls skills/
wc -l skills/*/SKILL.md | sort -rn | head -20   # over-length candidates
ls skills/*/python_implementation.py 2>/dev/null  # wrong-format candidates
ls skills/*/README.md skills/*/QUICK_START.md 2>/dev/null  # extraneous file candidates
```

**Priority order** (highest to lowest):
1. Skills with `python_implementation.py` or test files — wrong paradigm
2. Skills >500 lines — too long
3. Skills with extraneous docs (README, QUICK_START, CHANGELOG, CHECKLIST)
4. Skills not touched in >6 months and using `tu.tools.X()` style — likely interface mismatch
5. Skills that users have reported failing in practice

For **batch revision**: process highest-priority first; use a subagent per skill to parallelize.

---

## Phase 1: Audit

Read the SKILL.md and classify every issue into one of these buckets:

### Issue Classification

| Code | Issue | Check |
|------|-------|-------|
| `IF` | Interface mismatch | Python SDK in agent skill, or MCP calls in Python script skill |
| `TN` | Wrong tool name | Tool name in skill doesn't match actual registry |
| `TP` | Wrong tool parameter | Parameter name assumed, not verified |
| `EF` | Extraneous files | `python_implementation.py`, `test_*.py`, `README.md`, `QUICK_START.md`, `CHANGELOG.md`, `CHECKLIST.md` |
| `OL` | Over-length | Body >500 lines |
| `NW` | No workflow structure | Pure documentation, no phase-based instructions |
| `GQ` | API quirks undocumented | Known edge cases missing from "Known Gotchas" |
| `FD` | Frontmatter too sparse | Description missing trigger phrases or "when to use" |

Record issues as a list before touching anything. Example audit output:
```
tooluniverse-gwas-trait-to-gene: IF, TN (OpenTargets_search_gwas_studies_by_disease), TP (efo_id vs disease_trait), GQ (EFO/MONDO namespace, p_value=0.0), EF (python_implementation.py, README.md)
```

---

## Phase 2: Verify Tools

For every tool name mentioned in the skill:

```
mcp__tooluniverse__grep_tools(pattern="<tool_name_fragment>")
```

For every tool you plan to keep or document:
```
mcp__tooluniverse__get_tool_info(tool_names=["TOOL_NAME"], detail_level="full")
```

Build a corrections table before rewriting:

| Tool | In Skill (may be wrong) | Verified Correct |
|------|------------------------|-----------------|
| `OpenTargets_search_gwas_studies_by_disease` | ❌ does not exist | use `gwas_search_studies` |
| `Reactome_map_uniprot_to_pathways` | `uniprot_id` | `id` |

---

## Phase 3: Live Test

Run the skill's core workflow on a real example to surface bugs that static review misses:

**Option A — Direct execution** (for simple skills):
```
mcp__tooluniverse__execute_tool(tool_name="<key_tool>", arguments={<real_params>})
```
Walk through each phase manually, noting failures.

**Option B — Subagent** (for complex multi-step skills):
Launch an Agent with `subagent_type=general-purpose`:
```
"Follow the skill at [path]/SKILL.md to answer: [real query].
Report every tool call, parameter used, and any error or unexpected behavior."
```

Document everything found:
- Wrong tool names → update corrections table
- Wrong parameters → update corrections table
- API quirks (0.0 values, namespace mismatches, response format surprises) → add to "Known Gotchas"
- Missing steps (e.g., disambiguation phase absent) → add to workflow

---

## Phase 4: Rewrite

### What to keep
- Correct tool names and parameters (after verification)
- Accurate description of what each phase does
- Any domain-specific interpretation notes that are still valid

### What to fix
- **IF**: Convert to the correct interface for the target context (see table below)
- **TN/TP**: Apply corrections table from Phase 2
- **EF**: Delete extraneous files (no `python_implementation.py`, `test_*.py`, `README.md`, etc.)
- **OL**: Move tool parameter tables and detailed examples to `references/`
- **NW**: Restructure as Phase 0 → Phase N → Report workflow
- **GQ**: Add or update "Known Gotchas" section with Phase 3 findings
- **FD**: Expand description with trigger phrases and all "when to use" context

### Interface conversion guide

| Target context | Use in SKILL.md |
|----------------|----------------|
| LLM agent / MCP client | `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})` |
| Python script / notebook | `tu.tools.ToolName(param=value)` or `ToolUniverse` class |
| Shell / CLI automation | `tu run <tool_name> '{"param": "value"}'` |

### Required SKILL.md sections (every skill)
1. Frontmatter description — trigger phrases + all "when to use"
2. Key principles (3-5 bullets)
3. Workflow overview (phase diagram)
4. Per-phase instructions with concrete tool names + parameters
5. Known Gotchas (even if just "None found")
6. Tool reference table

### Body length rule
≤500 lines. If still over after removing extraneous content, move to `references/`:
- `references/tools.md` — detailed parameter tables for 10+ tools
- `references/patterns.md` — domain-specific interpretation notes

---

## Phase 5: Validate

Run one real query against the **revised** skill to confirm it works end-to-end:

1. Pick a concrete test case matching the skill's primary use case
2. Execute each phase following the updated SKILL.md
3. Confirm: no broken tool names, no parameter errors, workflow completes
4. If new issues surface → fix and re-validate

---

## Output

After revising, provide a summary:

```
Skill: [skill_name]
Issues found: [list of issue codes]
Tools fixed: [tool corrections table]
Files removed: [list]
Lines: [before] → [after]
Validation: [query used + outcome]
```

---

## Common Patterns Table

| Issue | Symptom | Fix |
|-------|---------|-----|
| Tool doesn't exist | `grep_tools` returns nothing | Find correct name or remove from skill |
| Wrong param name | `execute_tool` returns parameter error | `get_tool_info` to get real name |
| EFO/MONDO mismatch | 0 results for GWAS query | Add Step 0 to resolve ID via `gwas_search_studies` |
| `p_value=0.0` | Appears to be non-significant | Note in Gotchas: treat as p < 5e-309 |
| Co-localized genes | Multiple genes same locus | Note in Gotchas: report as locus cluster |
| Python SDK in MCP skill | `tu.tools.X()` calls | Convert to `mcp__tooluniverse__execute_tool` |
| No disambiguation phase | Results include off-target entities | Add Phase 1 to resolve IDs/aliases |
| Silent tool failure | Skill skips failed calls | Add "Data Gaps" section; document in Gotchas |

---

## References

- **Optimization principles (evidence grading, completeness)**: `devtu-optimize-skills`
- **Creating skills from scratch**: `create-tooluniverse-skill`
- **Tool testing workflow + API quirks**: `create-tooluniverse-skill/references/tool_testing_workflow.md`
- **SKILL.md template**: `create-tooluniverse-skill/assets/skill_template/SKILL.md`
