# SI Template

Ten-section Supplementary Information structure. Every section is mandatory;
write "Not applicable" if genuinely empty.

## SI-0: Pre-registered Protocol

The `research_protocol.md` frozen before Phase 1 began. Include: thesis
statement, research questions, falsification criteria, database scope,
timestamp of user approval.

## SI-1: Search Strategy

For each domain queried: database name, query string, filters applied,
date range, number of results returned. Organized by research wave.
Enables exact replication of every search.

## SI-2: Tool Call Log

Complete timestamped record of every `execute_tool` invocation.

```latex
\begin{longtable}{p{1.2cm} p{4cm} p{3.5cm} p{1cm} p{1cm} p{1.5cm}}
\toprule
Call \# & Tool & Query/Args & Items & Tier & Timestamp \\
\midrule
\endhead
1 & PubMed\_search & "BRCA1 PARP" & 15 & T2 & 2024-01-15T10:03Z \\
\bottomrule
\end{longtable}
```

Include the timestamp column (ISO 8601 UTC). This is the audit trail.

## SI-3: Statistical Methods

Any statistical tests, thresholds, or scoring methods applied to the
evidence. Include: enrichment analysis parameters, p-value corrections,
effect size thresholds, scoring rubrics for evidence grading.

## SI-4: Evidence Grading (Traceability Matrix)

Map every claim in the main text to its supporting evidence chain.

```text
Claim (Section, Line) -> Citation -> SI Call #
  -> Timestamp -> Database -> Raw Result
```

Flag any claim where the chain is incomplete. This matrix is how a
reviewer validates the paper without re-running every query.

## SI-5: Limitations

Honest accounting of: databases not queried and why, tools that failed,
entity types not resolved, time-sensitive data that may have changed,
potential biases in database coverage, languages excluded.

## SI-6: Author Contributions

CRediT taxonomy. For AI-assisted reviews, state explicitly which phases
were human-directed vs. AI-executed. Example: "Thesis development (Phase 0)
was human-directed. Database queries (Phase 1) were AI-executed under human
supervision."

## SI-7: Prompts

The exact prompts or instructions that initiated the review. Include: the
user's original question, any refinements during Phase 0, the skill
configuration used. Transparency for reproducibility.

## SI-8: Negative Results

Dedicated section for informative negatives. For each:

- Tool queried
- Query parameters
- Expected result
- Actual result (empty/null)
- What this absence constrains in the hypothesis

Negative results are evidence. They deserve the same documentation rigor
as positive findings.

## SI-9: Data Availability

Where to find the raw data: tool call outputs saved by FileSaveHook
(path: `/tmp/tooluniverse_outputs/`), `.bib` file, entity graph,
research state JSON. Include file hashes if reproducibility is critical.

## Formatting Rules

- Use `longtable` for tables that span pages.
- Number all tables and figures with SI prefix: "Supplementary Table 1".
- Cross-reference from main text: `see Supplementary Table~\ref{tab:si-calls}`.
- Same font and margins as main paper (tufte-swiss with `[nofonts]`).
