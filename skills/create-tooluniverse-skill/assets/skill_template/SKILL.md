---
name: tooluniverse-[domain-name]
description: [What this skill does and which databases/tools it uses. Include specific trigger phrases like "analyze [domain]", "find [data type] for [entity]", "research [topic]". Mention the key databases (e.g., GWAS Catalog, PubMed, ChEMBL). This description determines when the skill triggers — be comprehensive about use cases.]
---

# [Domain Name]

[One paragraph: what the skill does, what inputs it accepts, what outputs it produces.]

**KEY PRINCIPLES**:
1. **[Disambiguation first]** — resolve IDs/identifiers before running analyses
2. **[English-first queries]** — always use English terms in tool calls
3. **[Report-first output]** — create report file first, populate progressively
4. **[Negative results documented]** — missing data is a result, not a failure

---

## Workflow

```
Phase 0: Clarify (if needed)
Phase 1: [Disambiguation / ID resolution]
Phase 2: [Core data retrieval — silent]
Phase 3: [Analysis / enrichment]
Phase 4: Report
```

---

## Phase 0: Clarify Only When Needed

Ask the user ONLY if:
- [Ambiguous entity: could be X or Y]
- [Missing required context: organism, condition, etc.]

Skip for: [specific enough input types that don't need clarification].

---

## Phase 1: [Disambiguation]

Resolve [entity type] before searching. Use:
- `[TOOL_NAME]([param]=<input>)` — [what it returns]
- Fallback: `[TOOL_NAME_2]([param]=<input>)` — [what it returns]

Record: [ID1], [ID2], [aliases/synonyms].

---

## Phase 2: [Core Data Retrieval — Silent]

Do not narrate. Retrieve in parallel where possible:

**[Data source 1]:**
```
[TOOL_1](param=<value>, size=N)
[TOOL_2](param=<value>)   # enrich top N results
```

**[Data source 2]:**
```
[TOOL_3](param=<value>, limit=N)
```

**Fallback chain**: [Primary] → [Fallback] → document "No data available"

---

## Phase 3: [Analysis / Enrichment]

For top [N] results from Phase 2:
- [What to look up and why]
- [Evidence grading: High/Medium/Low based on X]

**Evidence levels:**
- **High**: [criteria]
- **Medium**: [criteria]
- **Low**: [criteria]

---

## Phase 4: Report

Create `[entity]_[domain]_report.md`. Structure:

```markdown
# [Domain] Report: [Entity]

**[Identifier]**: [value] | **Total [data]**: [N] | **[Threshold]**: [value]

---

## [Section 1 Title]

| [Field] | [Field] | [Field] | [Confidence] |
|---------|---------|---------|--------------|
| [value] | [value] | [value] | High |

---

## [Section 2 Title]

[...]
```

Always include:
- What was searched and which IDs were used
- Any disambiguation issues (e.g., namespace mismatches)
- "No data found" if a source returned nothing

---

## Known Gotchas

- **[Tool name issue]**: [e.g., "Tool X uses `query` not `name` as parameter"]
- **[API behavior]**: [e.g., "Returns empty list, not error, when no results found"]
- **[Data format]**: [e.g., "p_value=0.0 means floating-point underflow — treat as significant"]

---

## Tool Reference

| Tool | Use Case |
|------|----------|
| `[TOOL_1]` | [Purpose] |
| `[TOOL_2]` | [Purpose] |
| `[TOOL_3]` | [Purpose — fallback for TOOL_1] |
