---
name: devtu-optimize-skills
description: Optimize ToolUniverse skills for better report quality, evidence handling, and user experience. Apply patterns like tool verification, foundation data layers, disambiguation-first, evidence grading, quantified completeness, and report-only output. Use when reviewing skills, improving existing skills, or creating new ToolUniverse research skills.
---

# Optimizing ToolUniverse Skills

Best practices for high-quality research skills with evidence grading and source attribution.

## Tool Quality Standards

1. **Error messages must be actionable** — tell the user what went wrong AND what to do
2. **Schema must match API reality** — run `python3 -m tooluniverse.cli run <Tool> '<json>'` to verify
3. **Coverage transparency** — state what data is NOT included
4. **Input validation before API calls** — don't silently send invalid values
5. **Cross-tool routing** — name the correct tool when query is out-of-scope
6. **No silent parameter dropping** — if a parameter is ignored, say so

## Core Principles (13 Patterns)

Full details: [references/optimization-patterns.md](references/optimization-patterns.md)

| # | Pattern | Key Idea |
|---|---------|----------|
| 1 | Tool Interface Verification | `get_tool_info()` before first call; maintain corrections table |
| 2 | Foundation Data Layer | Query aggregator (Open Targets, PubChem) FIRST |
| 3 | Versioned Identifiers | Capture both `ENSG00000123456` and `.12` version |
| 4 | Disambiguation First | Resolve IDs, detect collisions, build negative filters |
| 5 | Report-Only Output | Narrative in report; methodology in appendix only if asked |
| 6 | Evidence Grading | T1 (mechanistic) → T2 (functional) → T3 (association) → T4 (mention) |
| 7 | Quantified Completeness | Numeric minimums per section (>=20 PPIs, top 10 tissues) |
| 8 | Mandatory Checklist | All sections exist, even if "Limited evidence" |
| 9 | Aggregated Data Gaps | Single section consolidating all missing data |
| 10 | Query Strategy | High-precision seeds → citation expansion → collision-filtered broad |
| 11 | Tool Failure Handling | Primary → Fallback 1 → Fallback 2 → document unavailable |
| 12 | Scalable Output | Narrative report + JSON/CSV bibliography |
| 13 | Synthesis Sections | Biological model + testable hypotheses, not just paper lists |

## Optimized Skill Workflow

```
Phase -1: Tool Verification (check params)
Phase  0: Foundation Data (aggregator query)
Phase  1: Disambiguation (IDs, collisions, baseline)
Phase  2: Specialized Queries (fill gaps)
Phase  3: Report Synthesis (evidence-graded narrative)
```

## Testing Standards

Full details: [references/testing-standards.md](references/testing-standards.md)

**Critical rule**: NEVER write skill docs without testing all tool calls first.

- 30+ tests per skill, 100% pass rate
- All tests use real data (no placeholders)
- Phase + integration + edge case tests
- SOAP tools (IMGT, SAbDab, TheraSAbDab) need `operation` parameter
- Distinguish transient errors (retry) from real bugs (fix)
- API docs are often wrong — always verify with actual calls

## Common Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| "Search Log" reports | Keep methodology internal; report findings only |
| Missing disambiguation | Add collision detection; build negative filters |
| No evidence grading | Apply T1-T4 grades; label each claim |
| Empty sections omitted | Include with "None identified" |
| No synthesis | Add biological model + hypotheses |
| Silent failures | Document in Data Gaps; implement fallbacks |
| Wrong tool parameters | Verify via `get_tool_info()` before calling |
| GTEx returns nothing | Try versioned ID `ENSG*.version` |
| No foundation layer | Query aggregator first |
| Untested tool calls | Test-driven: test script FIRST |

## Quick Fixes for User Complaints

| Complaint | Fix |
|-----------|-----|
| "Report too short" | Add Phase 0 foundation + Phase 1 disambiguation |
| "Too much noise" | Add collision filtering |
| "Can't tell what's important" | Add T1-T4 evidence tiers |
| "Missing sections" | Add mandatory checklist with minimums |
| "Too long/unreadable" | Separate narrative from JSON |
| "Just a list of papers" | Add synthesis sections |
| "Tool failed, no data" | Add retry + fallback chains |

## Skill Template

```markdown
---
name: [domain]-research
description: [What + when triggers]
---

# [Domain] Research

## Workflow
Phase -1: Tool Verification → Phase 0: Foundation → Phase 1: Disambiguate
→ Phase 2: Search → Phase 3: Report

## Phase -1: Tool Verification
[Parameter corrections table]

## Phase 0: Foundation Data
[Aggregator query]

## Phase 1: Disambiguation
[IDs, collisions, baseline]

## Phase 2: Specialized Queries
[Query strategy, fallbacks]

## Phase 3: Report Synthesis
[Evidence grading, mandatory sections]

## Output Files
- [topic]_report.md, [topic]_bibliography.json

## Quantified Minimums
[Numbers per section]

## Completeness Checklist
[Required sections with checkboxes]
```

## Additional References

- **Detailed patterns**: [references/optimization-patterns.md](references/optimization-patterns.md)
- **Testing standards**: [references/testing-standards.md](references/testing-standards.md)
- **Case studies** (4 real fixes): [references/case-studies.md](references/case-studies.md)
- **Checklists** (review + release): [references/checklists.md](references/checklists.md)
