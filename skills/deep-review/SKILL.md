---
name: deep-review
description: >-
  Autonomous deep research agent. Investigates any scientific topic across
  1,700+ databases via ToolUniverse, finds cross-domain connections, generates
  novel hypotheses, and delivers a typeset review paper with verified
  bibliography and full reproducibility SI. Use when: "write a review on X",
  "deep dive into X", "publication-quality analysis of X", "comprehensive
  review of X", "investigate X across all databases", or any request for a
  systematic, auditable scientific review that produces a peer-reviewable PDF.
---

# Deep Review

Research a topic to exhaustion. Deliver a typeset paper a Nobel laureate
could validate.

## Principles

1. **Thesis before research** -- refuse to proceed without a falsifiable claim
2. **Research before writing** -- evidence first, prose second
3. **Evidence-traced** -- every claim maps to a timestamped tool call
4. **Cross-domain** -- query literature, expression, pathways, druggability, genetics
5. **Informative negatives** -- empty results ARE data
6. **Novel hypotheses** -- generate predictions; state what would falsify them
7. **Tufte figures** -- every mark encodes data; zero chartjunk

## Workflow

### Phase 0: Thesis Development

Socratic narrowing with user. Ask: What claim? What changes? What is the
antagonist (current consensus)? Run 5-10 recon queries. Write
`research_protocol.md` (thesis, gap, questions, falsification criteria,
timestamp). User approves before Phase 1.

### Phase 1: Research Harvest

Exhaustive. Use `grep_tools` to discover relevant tools, `get_tool_info`
before every `execute_tool`. Parallel waves. Follow the expanding frontier
(gene -> pathway -> disease -> drug -> trial). `max_results` 25-50.
Timestamp every call (ISO 8601 UTC). Save to `wave_N_results.md`.
Read `references/RESEARCH_STRATEGY.md` for domain-specific patterns.

### Phase 2: Insight Discovery

Build entity graph. For unconnected entity pairs, find linking databases.
Score informative negatives. Classify: VERIFIED / NOVEL INSIGHT / NOVEL IP /
GAP / INFORMATIVE NEGATIVE. State predictions with falsification criteria.
Read `references/NOVELTY_DETECTION.md`.

### Phase 3: Write

3 parallel agents + reconciliation. Read `references/WILLIAMS_STYLE.md` and
`references/JOURNAL_FORMAT.md`. Agent 1: intro + model. Agent 2: evidence +
implications. Agent 3: SI with timestamped tool call log and traceability
matrix.

### Phase 4: Typeset

Build `.bib` from DOIs (`natbib` + `naturemag.bst`). Figures per
`references/FIGURE_DECISION.md`. `lualatex` + `tufte-swiss` (never pdflatex
or xelatex). Read `references/COMPOSITION.md`.

### Phase 4.5: Logic Audit

Walk every chain: Claim -> \cite{} -> SI Call # -> Timestamp -> Database ->
Raw Result. Flag leaps. Build traceability matrix for SI.

### Phase 5: Final Audit

Fact-check numerics. Word counts. Inclusive language. Visual inspection.
Compile and open PDF.

## References

| File | When | What |
|------|------|------|
| `RESEARCH_STRATEGY.md` | Phase 1 | Query patterns by domain |
| `NOVELTY_DETECTION.md` | Phase 2 | Cross-domain strategies |
| `WILLIAMS_STYLE.md` | Phase 3 | Prose clarity guide |
| `JOURNAL_FORMAT.md` | Phase 3 | Nature Reviews checklist |
| `BIBLIOGRAPHY_GUIDE.md` | Phase 4 | BibTeX from DOIs |
| `SI_TEMPLATE.md` | Phase 3 | 10-section SI structure |
| `FIGURE_DECISION.md` | Phase 4 | Tufte protocol |
| `COMPOSITION.md` | Phase 4 | LuaLaTeX + fonts |

## Output

`paper.pdf`, `references.bib`, `si_unified.tex`, `research_protocol.md`,
`research_notes.md`, `entity_graph.md`, `figure*.pdf`
