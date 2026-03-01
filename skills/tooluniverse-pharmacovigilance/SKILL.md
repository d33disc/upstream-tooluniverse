---
name: tooluniverse-pharmacovigilance
description: Analyze drug safety signals from FDA adverse event reports, label warnings, and pharmacogenomic data. Calculates disproportionality measures (PRR, ROR), identifies serious adverse events, assesses pharmacogenomic risk variants. Use when asked about drug safety, adverse events, post-market surveillance, or risk-benefit assessment.
---

# Pharmacovigilance Safety Analyzer

Systematic drug safety analysis using FAERS adverse event data, FDA labeling, PharmGKB pharmacogenomics, and clinical trial safety signals.

**KEY PRINCIPLES**:
1. **Report-first approach** — Create report file FIRST, update progressively
2. **Signal quantification** — Use disproportionality measures (PRR, ROR, IC)
3. **Severity stratification** — Prioritize serious/fatal events
4. **Multi-source triangulation** — FAERS, labels, trials, literature
5. **Pharmacogenomic context** — Include genetic risk factors when available
6. **Actionable output** — Risk-benefit summary with recommendations
7. **English-first queries** — Always use English drug names in tool calls, even if the user writes in another language. Respond in the user's language.

---

## When to Use

- "What are the safety concerns for [drug]?"
- "What adverse events are associated with [drug]?"
- "Is [drug] safe? What are the risks?"
- "Should I be concerned about [specific adverse event] with [drug]?"
- "Compare safety profiles of [drug A] vs [drug B]"
- "Pharmacovigilance analysis for [drug]"

---

## Workflow Overview

```
Phase 1: Drug Disambiguation
├── Resolve drug name (brand → generic)
├── Get identifiers (ChEMBL, DailyMed)
└── Identify drug class and mechanism
    ↓
Phase 2: Adverse Event Profiling (FAERS)
├── Query FAERS for drug-event pairs
├── Calculate disproportionality (PRR, ROR, IC)
├── Stratify by seriousness
└── OUTPUT: Ranked AE table
    ↓
Phase 3: Label Warning Extraction
├── DailyMed boxed warnings
├── Contraindications
├── Warnings and precautions
└── OUTPUT: Label safety summary
    ↓
Phase 4: Pharmacogenomic Risk
├── PharmGKB clinical annotations
├── High-risk genotypes
├── CPIC/DPWG dosing recommendations
└── OUTPUT: PGx risk table
    ↓
Phase 5: Clinical Trial Safety
├── ClinicalTrials.gov phase 3/4 results
├── Discontinuation rates
├── Serious AEs vs placebo
└── OUTPUT: Trial safety summary
    ↓
Phase 5.5: Pathway & Mechanism Context
├── KEGG: Drug metabolism pathways
├── Reactome: Mechanism-linked pathways
└── OUTPUT: Mechanistic safety context
    ↓
Phase 5.6: Literature Intelligence
├── PubMed: Peer-reviewed safety studies
├── EuropePMC (source='PPR'): Preprints
├── OpenAlex/SemanticScholar: Citation analysis
└── OUTPUT: Literature evidence
    ↓
Phase 6: Signal Prioritization
├── Rank by PRR × severity × frequency
├── Identify actionable signals
└── OUTPUT: Prioritized signal list
    ↓
Phase 7: Report Synthesis
```

---

## Phase 0: Tool Verification (CRITICAL)

Before calling any tool, verify you are using the correct parameter names.

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `FAERS_count_reactions_by_drug_event` | `drug` | `drug_name` |
| `DailyMed_search_spls` | `name` | `drug_name` |
| `PharmGKB_search_drug` | `drug` | `query` |
| `OpenFDA_get_drug_events` | `drug_name` | `search` (OpenFDA query string) |

See [references/tools.md](references/tools.md) for complete parameter tables.

---

## Phase 1: Drug Disambiguation

**Goal**: Resolve the user's drug name to a canonical generic name and obtain cross-database identifiers.

**Steps**:

1. Call `DailyMed_search_spls` with `drug_name` set to the query. Extract the generic name, brand names, and `setid` for subsequent label retrieval.
2. Call `ChEMBL_search_drugs` with `query` set to the generic name. Extract the `molecule_chembl_id` and maximum approval phase.
3. Record the drug class and mechanism of action from the ChEMBL or DailyMed results.

Report section should include: generic name, brand names, drug class, ChEMBL ID, mechanism of action, first approval year. Cite both tools used.

---

## Phase 2: Adverse Event Profiling

### 2.1 FAERS Query Strategy

1. Call `FAERS_count_reactions_by_drug_event` with `drug_name` and `limit=50` to retrieve the top adverse events with counts.
2. For events of interest, call `FAERS_get_event_details` with `drug_name` and `reaction` to get seriousness breakdown (serious count, death count, hospitalization count).
3. If FAERS tools fail, fall back to `OpenFDA_get_drug_events` using `search="patient.drug.medicinalproduct:[DRUG_NAME]"`.

### 2.2 Disproportionality Analysis

Agents must calculate or extract disproportionality metrics. The three standard measures are:

**Proportional Reporting Ratio (PRR)**:
```
PRR = (A / (A+B)) / (C / (C+D))

A = reports of drug X with event Y
B = reports of drug X with any other event
C = reports of event Y with any other drug (excluding X)
D = total reports excluding drug X

95% CI: exp(ln(PRR) ± 1.96 * sqrt(1/A + 1/C - 1/(A+B) - 1/(C+D)))
Signal threshold: PRR ≥ 2.0, lower 95% CI > 1.0, N ≥ 3
```

**Reporting Odds Ratio (ROR)**:
```
ROR = (A/B) / (C/D)

Same 2×2 table as PRR.
Signal threshold: lower 95% CI > 1.0, N ≥ 3
ROR is more sensitive than PRR for large datasets.
```

**Information Component (IC, Bayesian)**:
```
IC = log2( (A * N) / ((A+B) * (A+C)) )

N = total reports in database
Positive IC (IC025 > 0) indicates a signal.
IC025 = IC - 3.3 * sqrt(1/A + 1/N)  [lower credible interval]
```

**Signal Thresholds Summary**:

| Measure | Signal | Strong Signal |
|---------|--------|---------------|
| PRR | >2.0 | >3.0 |
| Chi-squared | >4.0 | >10.0 |
| N (case count) | ≥3 | ≥10 |
| IC025 | >0 | >1.0 |

**Signal Scoring for Prioritization**:
```
Signal Score = PRR × Severity_Weight × log10(Case_Count + 1)

Severity Weights:
  Fatal:             10
  Life-threatening:   8
  Hospitalization:    5
  Disability:         5
  Other serious:      3
  Non-serious:        1
```

### 2.3 Severity Classification

| Category | Priority |
|----------|----------|
| Fatal (death outcome) | Highest |
| Life-threatening (immediate death risk) | Very High |
| Hospitalization (required or prolonged) | High |
| Disability (persistent impairment) | High |
| Congenital anomaly (birth defect) | High |
| Other serious (medical intervention) | Medium |
| Non-serious | Low |

Report section must state the data period, total report count, and include two tables: (1) top AEs ranked by frequency with PRR, 95% CI, serious%, and fatal count; (2) serious AEs only with signal tier (T1-T4). Cite tool and data period.

---

## Phase 3: Label Warning Extraction

**Steps**:

1. If `setid` was obtained in Phase 1, call `DailyMed_get_spl_by_set_id` with `setid`. Extract: `boxed_warning`, `contraindications`, `warnings_and_precautions`, `adverse_reactions`, `drug_interactions`, `use_in_specific_populations`, `overdosage`.
2. If no setid, search again via `DailyMed_search_spls` with the generic name and take the first result.

**Warning Severity Categories**:

| Category | Description |
|----------|-------------|
| Boxed Warning | Most serious; life-threatening risk |
| Contraindication | Must not use under specified conditions |
| Warning | Significant risk requiring monitoring |
| Precaution | Use caution; specific populations |

Report section must include: full boxed warning text (or "None"), a contraindications table with rationale, and a warnings/precautions table with clinical actions. Cite `DailyMed_get_spl_by_set_id` and the setid.

---

## Phase 4: Pharmacogenomic Risk

**Steps**:

1. Call `PharmGKB_search_drug` with `query` set to the drug name. Retrieve the PharmGKB drug ID.
2. Call `PharmGKB_get_clinical_annotations` with `drug_id` to get annotated gene-variant-phenotype triples.
3. Call `CPIC_get_guidelines` with `drug_name` to check for CPIC/DPWG actionable guidelines.

**PGx Evidence Levels**:

| Level | Description | Clinical Action |
|-------|-------------|-----------------|
| 1A | CPIC/DPWG guideline, implementable | Follow guideline |
| 1B | CPIC/DPWG guideline, annotation level | Consider testing |
| 2A | VIP annotation, moderate evidence | May inform prescribing |
| 2B | VIP annotation, weaker evidence | Research context only |
| 3 | Low-level annotation | Not actionable |

Report section must include: a table of all level 1–2 gene-variant-phenotype triples with recommendations, and explicit statement of CPIC/DPWG guideline status ("No guideline exists" if absent). Cite both tools.

---

## Phase 5: Clinical Trial Safety

**Steps**:

1. Call `search_clinical_trials` with `intervention=[drug]`, `phase="Phase 3"`, `status="Completed"`, `pageSize=20`.
2. For trials with posted results, call `get_clinical_trial_results` with `nct_id` to retrieve adverse event tables.
3. Compare serious AE rates between drug and placebo/comparator arms. Note discontinuation rates.

Report section must include: a trial summary table (NCT ID, N, duration, serious AE rate drug vs control, deaths) and a common AE comparison table (drug% vs placebo%). Cite `search_clinical_trials`.

---

## Phase 5.5: Pathway & Mechanism Context

**Steps**:

1. Call `kegg_search_pathway` with `query="[drug] metabolism"` to find metabolism pathways.
2. For key drug targets, call `kegg_get_gene_info` with `gene_id="hsa:[GENE_SYMBOL]"` to list target pathways.
3. Call `Reactome_search_pathway` with `query=[drug mechanism]` as a cross-check or fallback.
4. Map adverse events to pathway mechanisms (e.g., mitochondrial complex I inhibition → lactic acidosis).

Report section must include: a pathway-relevance-safety table and a mechanistic AE mapping table (AE → pathway mechanism). Cite KEGG and Reactome tools used.

---

## Phase 5.6: Literature Intelligence

**Steps**:

1. Call `PubMed_search_articles` with `query='"[drug]" AND (safety OR adverse OR toxicity)'` and `limit=30`.
2. Call `EuropePMC_search_articles` with `query="[drug] safety"`, `source="PPR"` (preprints only), `pageSize=15`.
3. Call `openalex_search_works` or `SemanticScholar_search` to rank key papers by citation count.

Note: BioRxiv and MedRxiv do not expose their own search APIs — use EuropePMC with `source="PPR"` to search preprints from both servers.

Report section must include: a key safety studies table (PMID, title, year, citation count, key finding) and a preprints table. Always label preprints "NOT peer-reviewed." Cite PubMed and EuropePMC tools.

---

## Phase 6: Signal Prioritization

Rank all signals using: `Signal Score = PRR × Severity_Weight × log10(Case_Count + 1)`

**Evidence Tiers**:

| Tier | Criteria | Example |
|------|----------|---------|
| T1 (Critical) | PRR >10, fatal outcomes, or boxed warning | Lactic acidosis with biguanides |
| T2 (Moderate) | PRR 3-10, serious outcomes | Hepatotoxicity |
| T3 (Mild) | PRR 2-3, moderate concern | Hypoglycemia |
| T4 (Expected) | PRR <2, known/manageable | GI side effects |

Report section must include three subsections — T1 Critical (PRR, fatal count, score, action), T2 Moderate (PRR, serious count, score, action), and T3/T4 Known/Expected (PRR, frequency, management). All signals must have a score and a recommended action.

---

## Phase 7: Report Synthesis

Complete the report file with:
- Executive summary (highest-priority signals, overall risk level)
- Risk-benefit assessment
- Monitoring recommendations (minimum 3)
- Patient counseling points
- Contraindication checklist
- Data gaps and limitations
- Data sources section (all tools and databases used)

Before delivery, run through [CHECKLIST.md](CHECKLIST.md).

---

## Report Template

**File**: `[DRUG]_safety_report.md`

Create this file BEFORE beginning research. Initialize with all 10 section headers and `[Researching...]` placeholder text. Update each section progressively as data is gathered. The 10 required sections are:

1. Drug Identification
2. Adverse Event Profile (FAERS) — subsections: Top AEs / Serious AEs / Signal Analysis
3. FDA Label Safety Information — subsections: Boxed Warnings / Contraindications / Warnings & Precautions
4. Pharmacogenomic Risk Factors — subsections: Actionable Variants / Testing Recommendations
5. Clinical Trial Safety
6. Prioritized Safety Signals — subsections: Critical (T1) / Moderate (T2) / Known/Expected (T3-T4)
7. Risk-Benefit Assessment
8. Clinical Recommendations — subsections: Monitoring / Patient Counseling / Contraindication Checklist
9. Data Gaps & Limitations
10. Data Sources (populated as research progresses)

Header line: `# Pharmacovigilance Safety Report: [DRUG]` with Generated date, original query, and status.

---

## Citation Format (MANDATORY)

Every safety signal and data point in the report MUST include a source line:

```markdown
*Source: FAERS via `FAERS_count_reactions_by_drug_event` (Q1 2020 - Q4 2025)*
*Source: DailyMed via `DailyMed_get_spl_by_set_id` (setid: abc123)*
*Source: PharmGKB via `PharmGKB_search_drug` (PA450360)*
*Source: ClinicalTrials.gov via `search_clinical_trials`*
```

---

## Known Gotchas

### Parameter Name Errors (Most Common)
- `FAERS_count_reactions_by_drug_event` requires `drug_name`, not `drug`. Passing `drug` silently returns wrong results or errors.
- `PharmGKB_search_drug` requires `query`, not `drug` or `name`.
- `OpenFDA_get_drug_events` requires `search` as an OpenFDA query string (e.g., `"patient.drug.medicinalproduct:metformin"`), not a plain drug name.
- `DailyMed_search_spls` requires `drug_name`, not `name`.

### BioRxiv/MedRxiv Search
- Neither BioRxiv nor MedRxiv expose their own search APIs. Do NOT attempt to call `BioRxiv_search_preprints` or `MedRxiv_search_preprints` directly.
- Use `EuropePMC_search_articles` with `source="PPR"` to search preprints from both servers.

### PRR vs ROR Interpretation
- PRR and ROR converge when the event is rare relative to total reports. For common events, ROR will be higher than PRR — report both when possible.
- A high PRR alone is not sufficient for signal detection: require N ≥ 3 AND lower 95% CI > 1.0 (WHO-UMC criteria).
- IC025 > 0 (Bayesian lower credible interval) is the EMA preferred criterion.

### FAERS Data Limitations
- FAERS reports are submitted voluntarily; reporting rates vary by drug notoriety, media coverage, and drug age.
- FAERS does not establish causality. Use language like "disproportionate reporting" rather than "causes."
- Duplicate reports exist in FAERS (manufacturers re-submit consumer reports). Count-based PRR may overestimate signal for high-profile drugs.

### DailyMed Label Retrieval
- SPL documents can be very large. If a label call times out, try `DailyMed_search_spls` first to get `setid`, then retrieve the label using `DailyMed_get_spl_by_set_id`.
- Combination products may have multiple SPLs. Check all entries; prefer the most recent revision date.

### PharmGKB / CPIC Coverage
- Many drugs have no CPIC guideline. Always explicitly document "No CPIC/DPWG guideline exists" rather than leaving the section blank.
- Evidence level 1A is rare. Most drugs will have level 2-3 annotations at most.

### ClinicalTrials.gov Results
- Not all completed trials have posted results. Check `has_results` before calling `get_clinical_trial_results`.
- Phase 2 trials frequently lack placebo-controlled safety data; prefer Phase 3/4 for comparative AE rates.

### Drug Name Disambiguation
- Always search using generic (INN) name first, then brand name as fallback.
- Some FAERS records use brand names; if the generic name returns low counts, try common brand names.
- For combination products (e.g., metformin/sitagliptin), analyze each component separately in FAERS, then combine findings.

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `FAERS_count_reactions_by_drug_event` | `OpenFDA_get_drug_events` | PubMed safety literature |
| `DailyMed_get_spl_by_set_id` | `OpenFDA_get_drug_labels` | DailyMed web search |
| `PharmGKB_search_drug` | `CPIC_get_guidelines` | FDA PGx table (literature) |
| `search_clinical_trials` | `get_clinical_trial_by_nct_id` | PubMed for trial results |
| `kegg_search_pathway` | `Reactome_search_pathway` | Literature search |
| `PubMed_search_articles` | `openalex_search_works` | `SemanticScholar_search` |
| `EuropePMC_search_articles` (source='PPR') | `openalex_search_works` | Skip preprints |

---

## Abbreviated Tool Reference

For full parameter tables and additional tools, see [references/tools.md](references/tools.md).

| Phase | Tool | Purpose | Key Parameter(s) |
|-------|------|---------|------------------|
| 1 | `DailyMed_search_spls` | Search drug labels | `drug_name` |
| 1 | `DailyMed_get_spl_by_set_id` | Retrieve full SPL | `setid` |
| 1 | `ChEMBL_search_drugs` | Drug identity/class | `query` |
| 2 | `FAERS_count_reactions_by_drug_event` | Top AE counts | `drug_name`, `limit` |
| 2 | `FAERS_get_event_details` | Seriousness breakdown | `drug_name`, `reaction` |
| 2 | `OpenFDA_get_drug_events` | AE fallback | `search` |
| 3 | `DailyMed_get_drug_interactions` | Drug interactions | `setid` |
| 4 | `PharmGKB_search_drug` | PGx drug lookup | `query` |
| 4 | `PharmGKB_get_clinical_annotations` | Variant annotations | `drug_id` |
| 4 | `CPIC_get_guidelines` | CPIC/DPWG guidelines | `drug_name` |
| 5 | `search_clinical_trials` | Trial search | `intervention`, `phase`, `status` |
| 5 | `get_clinical_trial_results` | Posted trial results | `nct_id` |
| 5.5 | `kegg_search_pathway` | Metabolism pathways | `query` |
| 5.5 | `Reactome_search_pathway` | Mechanism pathways | `query`, `species` |
| 5.6 | `PubMed_search_articles` | Safety literature | `query`, `limit` |
| 5.6 | `EuropePMC_search_articles` | Preprints | `query`, `source='PPR'` |
| 5.6 | `openalex_search_works` | Citation-ranked search | `query`, `limit` |
| Any | `AdverseEventICDMapper` | Map AE text to ICD-10 | `text` |
