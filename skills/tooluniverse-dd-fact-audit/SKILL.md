---
name: tooluniverse-dd-fact-audit
description: Fan-out verification of every fact in a biotech DD report's canonical.yaml against ToolUniverse databases (ClinicalTrials.gov, FAERS, OpenTargets, PubChem, ChEMBL, FDA, SEC EDGAR, PubMed, Semantic Scholar), custom Python verification code, and live web sources. Produces a scored audit ledger (VERIFIED/CONTRADICTED/STALE/UNREACHABLE/SELF_AUDIT) with ship-readiness verdict. Use when asked to "audit", "fact-check", or "verify" a DD report, or before any DD report ships to a recipient.
---

# DD Fact Audit — Full-Surface Verification

Every fact is a liability until verified. This skill reads a biotech due
diligence report's structured fact file (canonical.yaml or equivalent),
classifies every claim by type, fans out verification across all available
ToolUniverse databases and supplementary sources, and produces a scored
audit ledger.

## Trigger

- "audit [TICKER]" / "fact-check [report]" / "verify canonical"
- Before any DD report ships to a recipient
- After any structured fact field is modified

## Inputs

- A structured YAML file containing verifiable claims with `primary_source`
  blocks (`{url, verbatim, retrieved_date}`)
- Optional: custom Python verification scripts (SEC EDGAR clients,
  valuation models, audit gate scripts)
- Optional: companion audit artifacts (numeric_audit.md,
  company_claims_ledger.yaml, provenance_log.yaml)

## Architecture

```
canonical.yaml
      |
      v
[Claim Extractor]  -- parses every field with a value + primary_source
      |
      v
[Claim Classifier] -- assigns each claim to 1+ fact categories (24 types)
      |
      v
[Fan-Out Verifier]  -- dispatches to verification sources in parallel:
  |   |   |   |
  |   |   |   +-- ToolUniverse (MCP: 1,361 live tools)
  |   |   +------ Custom Python (SEC EDGAR, valuation scripts)
  |   +---------- Live web (SEC API, ClinicalTrials.gov, FDA)
  +-------------- Audit gate scripts (if available)
      |
      v
[Reconciler]  -- compares tool output to canonical claim
      |
      v
[Audit Ledger]  -- VERIFIED / CONTRADICTED / STALE / UNREACHABLE per claim
```

## Phase 1 — Claim Extraction

Read the canonical YAML. For every field that carries a specific value
(number, date, name, ID, status), extract a claim record:

```yaml
- field_path: company.funding_total_usd
  canonical_value: 247_000_000
  primary_source_url: https://www.sec.gov/...
  primary_source_verbatim: "Form D filings ... totaling $247M"
  retrieved_date: 2026-04-03
  category: financial_funding
```

### Fact Categories (24 types — verify ALL)

| # | Category | Example Fields | Verification Sources |
|---|----------|---------------|---------------------|
| 1 | **Clinical trial identity** | NCT IDs, phase, status, sponsor | ClinicalTrials.gov tools, `search_clinical_trials` |
| 2 | **Clinical trial enrollment** | n_dosed, enrollment, discontinuation | `get_clinical_trial_design`, `extract_clinical_trial_outcomes` |
| 3 | **Clinical endpoints** | p-values, hazard ratios, remission %, ORR | `extract_clinical_trial_outcomes`, PubMed |
| 4 | **Safety events** | SAEs, grade 3/4 AEs, deaths | `extract_clinical_trial_adverse_events`, FAERS |
| 5 | **FAERS signals** | report counts, PRR, CI bounds | `FAERS_count_reactions_by_drug_event`, `FAERS_calculate_disproportionality` |
| 6 | **Drug/asset identity** | drug name, compound ID, route | PubChem, ChEMBL, DailyMed |
| 7 | **Mechanism of action** | target, mechanism tags | OpenTargets MOA, DGIdb, DailyMed |
| 8 | **FDA/regulatory milestones** | approval dates, BTD, NDA/BLA | FDA Orange Book, DailyMed, ToolUniverse FDA tools |
| 9 | **SEC filings** | CIK, filing accession, form type | SEC EDGAR Submissions API |
| 10 | **Financial metrics** | revenue, R&D, cash, EV, market cap | SEC EDGAR Company-Concept XBRL API |
| 11 | **Funding rounds** | Series A/B/C amounts, investors | SEC Form D filings |
| 12 | **Company metadata** | legal name, HQ, CEO, founding | SEC submissions API, company website |
| 13 | **Patent data** | patent numbers, expiry dates | USPTO tools via ToolUniverse, PubChem patents |
| 14 | **Competitor drug status** | competitor phase, approval | ClinicalTrials.gov, FDA Orange Book |
| 15 | **Competitor trial outcomes** | competitor efficacy, safety | `extract_clinical_trial_outcomes`, PubMed |
| 16 | **Collaboration terms** | partner names, milestones, royalties | SEC 8-K filings, PubMed press release search |
| 17 | **Publication data** | PMID, DOI, journal, paper count | PubMed `search_articles`, Semantic Scholar `get_paper` |
| 18 | **Stock/trading data** | close price, % moves, halts | SEC filings, web search |
| 19 | **Workforce events** | layoff %, restructuring dates | SEC 8-K, web search |
| 20 | **Indication tags** | therapeutic area, disease names | OpenTargets disease lookup, ClinicalTrials.gov |
| 21 | **Conference abstracts** | abstract ID, session type, presenter | Conference website, PubMed |
| 22 | **Conference sponsorship** | booth number, sponsor tier | Conference website |
| 23 | **Clinical conventions** | threshold values (e.g., 11 uM M-AAT) | PubMed literature verification |
| 24 | **Prior corrections** | withdrawn claims, replacement values | Internal YAML history, git blame |

## Phase 2 — Fan-Out Verification

Dispatch verification in parallel using subagents. Each subagent gets
the claim records for its scope and full absolute paths to all files.

### 2a. ToolUniverse verification (subagent)

Route each claim category to the appropriate tool chain. Always
`get_tool_info` before `execute_tool`. Key chains:

```
Clinical trials:
  search_clinical_trials(intervention=...) OR by NCT ID
  -> get_clinical_trial_status_and_dates(nct_ids=[...])
  -> get_clinical_trial_design(nct_ids=[...])
  -> extract_clinical_trial_outcomes(nct_ids=[...])
  -> extract_clinical_trial_adverse_events(nct_ids=[...])

Safety (FAERS — 40% breakage, have fallbacks):
  FAERS_count_reactions_by_drug_event(drug_name="UPPERCASE")
  FAERS_calculate_disproportionality(drug_name=..., adverse_event=...)
  Fallback: OpenFDA_get_drug_events, FDA label AE sections

Drug identity:
  PubChem_get_CID_by_compound_name -> PubChem_get_compound_properties_by_CID
  ChEMBL_search_compounds -> ChEMBL_get_bioactivity_by_chemblid
  OpenTargets_get_drug_mechanisms_of_action_by_chemblId

Target biology:
  OpenTargets_get_target_by_ensemblId
  OpenTargets_get_target_tractability_by_ensemblId
  OpenTargets_get_diseases_phenotypes_by_target_ensemblId

Regulatory:
  FDA_OrangeBook_search_drug
  FDA_OrangeBook_get_approval_history
  DailyMed_search_spls

Literature:
  PubMed_search_articles(query="\"drug_name\"")
  SemanticScholar_get_paper(paper_id="PMID:...")
  SemanticScholar_search_papers(query=...)

Oncology (if applicable):
  cBioPortal_get_mutations(gene=...)
  gnomAD_get_variant(variant_id=...)
  clinvar_search_variants(gene=...)

Patents:
  PubChem_get_associated_patents_by_CID
  FDA_OrangeBook_get_patent_info
  FDA_OrangeBook_get_exclusivity
```

### 2b. Custom Python verification (subagent)

If the project has SEC EDGAR or valuation Python scripts, run them to
cross-check financial and regulatory claims. Compare script output
against canonical fields:

- CIK resolution and filing history
- XBRL financial metrics (revenue, R&D, cash)
- Form D funding round totals
- Valuation metrics (EV, catalyst density, composite scores)

### 2c. Audit gate scripts (subagent, if available)

If companion audit scripts exist (e.g., dd_audit_gate.py), run them and
cross-reference:

- Claims ledger verdicts vs canonical values
- Provenance log source URLs still resolve
- Live verification findings

### 2d. Live web verification (subagent)

For claims no database covers (stock prices, workforce events,
conference sponsorship), use web search MCP tools:

- Verify specific claims via tavily/exa/jina search
- Re-fetch primary_source URLs and confirm verbatim text still appears

### 2e. Staleness check (subagent)

For every `retrieved_date` in the canonical file:

- If >90 days old: flag as STALE
- If >180 days old: flag as STALE-CRITICAL
- Re-fetch primary_source URL and compare verbatim text
- Check if ClinicalTrials.gov status changed since retrieval
- Check if SEC filings were amended since retrieval

## Phase 3 — Reconciliation

For each claim, compare canonical value against all verification results:

```
VERIFIED        — >=1 source confirms, 0 contradict
CONTRADICTED    — >=1 source returns a different value (report the delta)
STALE           — source confirms but retrieved_date >90 days
UNREACHABLE     — all verification sources failed/broken/timed out
NOT_CHECKABLE   — no available tool covers this fact type
SELF_AUDIT      — only the canonical's own primary_source confirms
```

### Scoring

```
Audit Score = VERIFIED / (VERIFIED + CONTRADICTED + STALE + SELF_AUDIT) * 100

Thresholds:
  >= 95%  SHIP-READY
  >= 87%  SHIP-WITH-CAVEATS (list every non-VERIFIED claim)
  >= 70%  HOLD — too many unverified claims
  <  70%  DO NOT SHIP
```

### Contradiction handling

Every CONTRADICTED claim gets a structured entry:

```yaml
- field: competitor_peresolimab.enrollment
  canonical: 491
  tool_result: 485
  source: ClinicalTrials.gov NCT04572502
  delta: -1.2%
  severity: LOW  # <5% = LOW, 5-10% = MEDIUM, >10% = HIGH
  action: INVESTIGATE  # or AUTO_CORRECT if tool source is Tier 1
```

HIGH severity contradictions (>10% delta) halt the audit and surface
immediately. Do not auto-correct.

## Phase 4 — Output

### 4a. Audit ledger

Write `fact_audit_YYYYMMDD.md` alongside the canonical file:

```markdown
# Fact Audit — [TICKER] [DATE]

Generated: YYYY-MM-DDTHH:MM:SS.sssZ
Canonical: path/to/canonical.yaml
Score: XX% (N VERIFIED / M total checkable claims)
Verdict: SHIP-READY | SHIP-WITH-CAVEATS | HOLD | DO NOT SHIP

## Summary
- VERIFIED: N
- CONTRADICTED: N (list)
- STALE: N (list)
- UNREACHABLE: N (list)
- NOT_CHECKABLE: N (list)
- SELF_AUDIT: N (list)

## Contradictions (requires resolution)
[structured entries per Phase 3]

## Stale Claims (requires re-verification)
[list with retrieved_date and age in days]

## Full Claim Ledger
[every claim with verdict, source, and tool output excerpt]
```

### 4b. Canonical patch (if auto-corrections warranted)

For CONTRADICTED claims where the tool source is Tier 1, delta is <5%,
and canonical value is older: propose a patch. Never auto-apply —
require explicit approval before any canonical write.

## Verification Source Priority

```
Tier 1 (regulatory — highest authority):
  ClinicalTrials.gov API      — trial status, enrollment, outcomes
  SEC EDGAR JSON API           — CIK, filings, XBRL financials
  FDA FAERS                    — adverse event counts, PRR
  FDA Orange Book              — approval history, patents, exclusivity
  USPTO                        — patent claims, expiry

Tier 2 (peer-reviewed):
  PubMed / Semantic Scholar    — publication verification
  OpenTargets                  — disease-target-drug associations
  ChEMBL                       — compound bioactivity

Tier 3 (company disclosures — lowest authority):
  Company website / IR         — pipeline pages, press releases
  Conference websites          — abstracts, exhibitor lists
  News / web search            — workforce events, stock moves
```

When Tier 1 and Tier 3 conflict, Tier 1 wins. When Tier 2 and Tier 3
conflict, flag for review.

## Concurrency and Performance

- Fan out independent verification calls in parallel within each subagent
- FAERS tools have 40% breakage — always include OpenFDA fallback
- ADMET-AI and NVIDIA NIM are 100% dead — skip
- ChEMBL has 34.5% breakage — verify tool liveness before chaining
- PubMed: 10 req/sec with NCBI_API_KEY, 3 without
- Semantic Scholar: 100 req/sec with S2_API_KEY, 1 without
- SEC EDGAR: 10 req/sec (User-Agent with email required)

## Rules

- **Never auto-correct the canonical file.** Propose patches only.
- **Never skip a fact category.** If no tool covers it, mark NOT_CHECKABLE.
- **Every verification gets a UTC ms-precision timestamp.**
- **Audit the auditor.** If a tool contradicts both canonical AND a second
  tool, flag the tool as suspect, not the canonical.
- **Tier 1 sources win ties.** ClinicalTrials.gov > company press release.
- **Score honestly.** SELF_AUDIT claims count against the score.
- **Preserve provenance.** The audit ledger cites every tool call with
  exact arguments and output for reproducibility.
