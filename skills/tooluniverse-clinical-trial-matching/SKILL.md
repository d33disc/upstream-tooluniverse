---
name: tooluniverse-clinical-trial-matching
description: AI-driven patient-to-trial matching for precision medicine and oncology. Given a patient profile (disease, molecular alterations, stage, prior treatments), discovers and ranks clinical trials from ClinicalTrials.gov using multi-dimensional matching across molecular eligibility, clinical criteria, drug-biomarker alignment, evidence strength, and geographic feasibility. Produces a quantitative Trial Match Score (0-100) per trial with tiered recommendations and a comprehensive markdown report. Use when oncologists, molecular tumor boards, or patients ask about clinical trial options for specific cancer types, biomarker profiles, or post-progression scenarios.
---

# Clinical Trial Matching for Precision Medicine

Transform patient molecular profiles and clinical characteristics into prioritized clinical trial recommendations. Searches ClinicalTrials.gov and cross-references with molecular databases (CIViC, OpenTargets, ChEMBL, FDA) to produce evidence-graded, scored trial matches.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Patient-centric** - Every recommendation considers the individual patient's profile
3. **Molecular-first matching** - Prioritize trials targeting patient's specific biomarkers
4. **Evidence-graded** - Every recommendation has an evidence tier (T1-T4)
5. **Quantitative scoring** - Trial Match Score (0-100) for every trial
6. **Eligibility-aware** - Parse and evaluate inclusion/exclusion criteria
7. **Actionable output** - Clear next steps, contact info, enrollment status
8. **Source-referenced** - Every statement cites the tool/database source
9. **Completeness checklist** - Mandatory section showing analysis coverage
10. **English-first queries** - Always use English terms in tool calls. Respond in user's language

---

## When to Use

Apply when user asks:
- "What clinical trials are available for my NSCLC with EGFR L858R?"
- "Patient has BRAF V600E melanoma, failed ipilimumab - what trials?"
- "Find basket trials for NTRK fusion"
- "Breast cancer with HER2 amplification, post-CDK4/6 inhibitor trials"
- "KRAS G12C colorectal cancer clinical trials"
- "Immunotherapy trials for TMB-high solid tumors"
- "Clinical trials near Boston for lung cancer"
- "What are my options after failing osimertinib for EGFR+ NSCLC?"

**NOT for** (use other skills instead):
- Single variant interpretation without trial focus -> Use `tooluniverse-cancer-variant-interpretation`
- Drug safety profiling -> Use `tooluniverse-adverse-event-detection`
- Target validation -> Use `tooluniverse-drug-target-validation`
- General disease research -> Use `tooluniverse-disease-research`

---

## Input Parsing

### Required Input
- **Disease/cancer type**: Free-text disease name (e.g., "non-small cell lung cancer", "melanoma")

### Strongly Recommended
- **Molecular alterations**: One or more biomarkers (e.g., "EGFR L858R", "KRAS G12C", "PD-L1 50%", "TMB-high")
- **Stage/grade**: Disease stage (e.g., "Stage IV", "metastatic", "locally advanced")
- **Prior treatments**: Previous therapies and outcomes (e.g., "failed platinum chemotherapy", "progressed on osimertinib")

### Optional
- **Performance status**: ECOG or Karnofsky score
- **Geographic location**: City/state for proximity filtering
- **Trial phase preference**: I, II, III, IV, or "any"
- **Recruiting status preference**: recruiting, not yet recruiting, active

### Biomarker Parsing Rules

| Input Format | Parsed As | Example |
|-------------|-----------|---------|
| Gene + amino acid change | Specific mutation | EGFR L858R |
| Gene + exon notation | Exon-level alteration | EGFR exon 19 deletion |
| Gene + fusion partner | Fusion | EML4-ALK fusion |
| Gene + amplification | Copy number gain | HER2 amplification |
| Gene + expression level | Expression biomarker | PD-L1 50% |
| Gene + status | Status biomarker | MSI-high, TMB-high |
| Gene + resistance | Resistance mutation | EGFR T790M |

### Gene Symbol Normalization

Before querying any tool, normalize common aliases to official symbols:

| Common Alias | Official Symbol |
|-------------|----------------|
| HER2, HER-2 | ERBB2 (search both in trials) |
| PD-L1, PDL1 | CD274 (use "PD-L1" string in trial queries) |
| PD-1, PD1 | PDCD1 (use "PD-1" in trial queries) |
| VEGF | VEGFA |
| BRCA | Specify BRCA1 or BRCA2 |

---

## Workflow Overview

```
Phase 1: Patient Profile Standardization
  - Resolve disease to EFO/ontology ID
  - Parse molecular alterations (gene + variant type)
  - Resolve gene symbols to Ensembl/Entrez IDs
  - Classify biomarker actionability (FDA-approved vs investigational)

Phase 2: Broad Trial Discovery
  - Disease-based trial search (ClinicalTrials.gov)
  - Biomarker-specific trial search
  - Intervention-based search (drugs targeting patient's biomarkers)
  - Deduplicate collected NCT IDs

Phase 3: Trial Characterization
  - Batch-fetch eligibility criteria for top candidates
  - Batch-fetch conditions and interventions
  - Batch-fetch locations and status
  - Batch-fetch trial descriptions

Phase 4: Molecular Eligibility Matching
  - Parse eligibility text for biomarker requirements
  - Check patient's biomarkers against inclusion/exclusion criteria
  - Score molecular eligibility

Phase 5: Drug-Biomarker Alignment
  - Identify trial intervention drugs
  - Check drug mechanisms vs patient biomarkers (OpenTargets, ChEMBL)
  - Verify FDA approval for biomarker-drug combinations

Phase 6: Evidence Assessment
  - FDA-approved biomarker-drug combinations (T1)
  - Phase III clinical results (T2)
  - CIViC and phase I/II evidence (T3)
  - Mechanistic/computational support (T4)

Phase 7: Geographic & Feasibility Analysis
  - Trial site locations vs patient location
  - Enrollment status and key dates

Phase 8: Alternative Options
  - Basket trials (biomarker-driven, tumor-agnostic)
  - Expanded access / compassionate use programs

Phase 9: Scoring & Ranking
  - Calculate Trial Match Score (0-100) per trial
  - Assign tier (Optimal/Good/Possible/Exploratory)
  - Rank and generate recommendations

Phase 10: Report Synthesis
  - Executive summary (top 3 trials)
  - Ranked trial list with score breakdown
  - Evidence grading
  - Completeness checklist
```

---

## Phase 1: Patient Profile Standardization

**Goal**: Resolve all patient inputs to standardized identifiers for cross-database queries.

### 1.1 Disease Resolution

Call `OpenTargets_get_disease_id_description_by_name` with the disease name. Extract the first hit's `id` (EFO ID) and `name`. If that returns no hits, fall back to `ols_search_efo_terms` and extract `short_form` as the EFO ID.

**Result needed**: EFO ID (e.g., `EFO_0003060`) and standardized disease name.

### 1.2 Gene/Biomarker Resolution

For each gene symbol, first apply alias normalization (HER2->ERBB2, etc.), then call `MyGene_query_genes` with `species="human"`. Find the hit where `symbol` matches exactly. Extract `entrezgene` and `ensembl.gene` (the Ensembl ID).

**Result needed**: Official symbol, Entrez ID, Ensembl ID per gene.

### 1.3 Biomarker Actionability Classification

Call `fda_pharmacogenomic_biomarkers` (no parameters needed). Filter results where `Biomarker` field contains the gene symbol. If matches exist, the biomarker is **FDA-approved** level; list the associated drugs. If no matches, classify as **investigational** (revisit in Phase 5).

### 1.4 Parallelization Opportunity

All Phase 1 tool calls are independent — run simultaneously:
- `MyGene_query_genes` for each gene
- `OpenTargets_get_disease_id_description_by_name` for disease
- `ols_search_efo_terms` for disease (fallback prep)
- `fda_pharmacogenomic_biomarkers` (no params)

---

## Phase 2: Broad Trial Discovery

**Goal**: Cast a wide net to find all potentially relevant clinical trials.

### 2.1 Disease-Based Search

Call `search_clinical_trials` with `condition` = disease name and `query_term` = disease name, `pageSize=20`. This is the primary search tool.

### 2.2 Biomarker-Specific Search

Call `search_clinical_trials` with `query_term` = "[GENE] [variant]" (e.g., "EGFR L858R"). If a disease filter is appropriate, also pass `condition`.

### 2.3 Intervention-Based Search

For each known drug targeting the patient's biomarkers (from Phase 1 FDA check): call `search_clinical_trials` with `intervention` = drug name and `query_term` = drug name.

### 2.4 Alternative Search

Call `clinical_trials_search` with `action="search_studies"` as a complement to the main search. Note: `action` must be the exact string `"search_studies"`.

### 2.5 Deduplication

Collect all NCT IDs from all search results. The NCT ID field is `"NCT ID"` in `search_clinical_trials` responses and `"nctId"` in `clinical_trials_search` responses. Deduplicate before proceeding.

**All Phase 2 searches are independent — run them simultaneously.**

---

## Phase 3: Trial Characterization

**Goal**: Get detailed information for the top 15-20 candidate trials.

Batch NCT IDs in groups of 10. Run all five batch fetches simultaneously per batch:

1. **Eligibility criteria**: Call `get_clinical_trial_eligibility_criteria` with `nct_ids=[...]` and `eligibility_criteria="all"`. Returns inclusion and exclusion criteria text.

2. **Conditions and interventions**: Call `get_clinical_trial_conditions_and_interventions` with `nct_ids=[...]` and `condition_and_intervention="all"`. Returns arm groups and intervention names.

3. **Locations**: Call `get_clinical_trial_locations` with `nct_ids=[...]` and `location="all"`. Returns sites with facility, city, state, country.

4. **Status and dates**: Call `get_clinical_trial_status_and_dates` with `nct_ids=[...]` and `status_and_date="all"`. Returns enrollment status and start/completion dates.

5. **Descriptions**: Call `get_clinical_trial_descriptions` with `nct_ids=[...]` and `description_type="full"`. Returns titles and detailed descriptions.

---

## Phase 4: Molecular Eligibility Matching

**Goal**: Determine how well the patient's molecular profile matches each trial's biomarker requirements.

### 4.1 Parse Eligibility Text

Split the eligibility criteria text at "Exclusion Criteria" to separate inclusion from exclusion sections. Scan each section for gene name mentions using a list of target genes from the patient profile. Context around each mention (±100 characters) indicates whether a match is required or excluded.

Check for basket/tumor-agnostic language: "tumor-agnostic", "histology-independent", "basket", "any solid tumor", "biomarker-selected".

### 4.2 Molecular Match Scoring (0-40 points)

| Match Type | Points |
|-----------|--------|
| Exact biomarker match (specific variant in inclusion criteria) | 40 |
| Gene-level match (gene required, specific variant unclear) | 30 |
| Pathway match (trial targets same pathway) | 20 |
| No molecular criteria (general disease trial) | 10 |
| Patient biomarker is in exclusion criteria | 0 |

---

## Phase 5: Drug-Biomarker Alignment

**Goal**: Verify that trial drugs actually target the patient's biomarkers.

For each trial's intervention drugs:

1. Call `OpenTargets_get_drug_id_description_by_name` with the drug name to get its ChEMBL ID.
2. Call `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` with the ChEMBL ID to get targets and mechanism of action.
3. Check if any target gene in the mechanism matches the patient's gene symbols. If yes, the drug directly targets the patient's biomarker.

Also call `OpenTargets_get_associated_drugs_by_target_ensemblID` with the patient's gene Ensembl ID to discover additional drugs targeting that gene that may appear in trials.

**Run drug lookups for all trial drugs in parallel.**

---

## Phase 6: Evidence Assessment

**Goal**: Assign an evidence tier to each trial-drug-biomarker combination.

| Tier | Symbol | Criteria | Score Impact |
|------|--------|----------|-------------|
| T1 | [T1] | FDA-approved biomarker-drug, NCCN guideline | 20 points |
| T2 | [T2] | Phase III positive, clinical evidence | 15 points |
| T3 | [T3] | Phase I/II results, preclinical | 10 points |
| T4 | [T4] | Computational, mechanism inference | 5 points |

### Data Sources per Tier

**T1**: Call `FDA_get_indications_by_drug_name` — check if disease appears in the labeled indications text.

**T2/T3**: Call `PubMed_search_articles` with query "[GENE] [variant] [drug] [disease] clinical trial". Call `civic_get_variants_by_gene` with the CIViC gene ID (integer, see Known CIViC Gene IDs below) to find clinical evidence entries.

**T4**: Drug mechanism overlap from Phase 5 alone constitutes T4 if no clinical data found.

**Known CIViC Gene IDs**: EGFR=19, BRAF=5, ALK=1, ABL1=4, KRAS=30, TP53=45, ERBB2=20, NTRK1=197, NTRK2=560, NTRK3=561, PIK3CA=37, MET=52, ROS1=118, RET=122, BRCA1=2370, BRCA2=2371

---

## Phase 7: Geographic & Feasibility Analysis

**Goal**: Assess practical feasibility of trial enrollment.

From the locations batch fetch (Phase 3), extract countries and US states. Compute:
- Total number of sites
- Whether US sites exist
- If patient location was provided, whether any site is in the same state/city

### Geographic Scoring (0-5 points)

| Criterion | Points |
|-----------|--------|
| Trial sites in patient's state/city | 5 |
| Trial sites within ~100 miles / same country | 3 |
| International sites only | 1 |
| No location info | 0 |

---

## Phase 8: Alternative Options

**Goal**: Identify basket trials, expanded access, and related studies.

### 8.1 Basket Trial Search

Call `search_clinical_trials` with simpler queries first. Complex multi-word queries often return zero results.

Recommended query sequence (try each):
- `"[GENE] solid tumor"`
- `"[GENE]"`
- `"[GENE] basket"`

Deduplicate results. In eligibility text, look for "tumor-agnostic" or "any solid tumor" language to confirm basket design.

### 8.2 Expanded Access

Call `search_clinical_trials` with `query_term="[drug_name] expanded access"`. Flag any results with status "EXPANDED_ACCESS".

---

## Phase 9: Trial Match Scoring System

### Score Components (Total: 0-100)

**Molecular Match** (0-40 points): See Phase 4 scoring table.

**Clinical Eligibility** (0-25 points):

| Criterion | Points |
|-----------|--------|
| All criteria met (disease, stage, prior treatment) | 25 |
| Most criteria met (1-2 unclear) | 18 |
| Some criteria met (several unclear) | 10 |
| Clearly ineligible (fails major criterion) | 0 |

**Evidence Strength** (0-20 points): See Phase 6 tier table.

**Trial Phase** (0-10 points):

| Phase | Points |
|-------|--------|
| Phase III | 10 |
| Phase II | 8 |
| Phase I/II | 6 |
| Phase I | 4 |

**Geographic Feasibility** (0-5 points): See Phase 7 scoring table.

### Recommendation Tiers

| Score | Tier | Label | Action |
|-------|------|-------|--------|
| 80-100 | Tier 1 | Optimal Match | Strongly recommend - contact site immediately |
| 60-79 | Tier 2 | Good Match | Recommend - discuss with care team |
| 40-59 | Tier 3 | Possible Match | Consider - needs further eligibility review |
| 0-39 | Tier 4 | Exploratory | Backup option - consider if Tier 1-3 unavailable |

---

## Phase 10: Report Synthesis

Save the report as: `clinical_trial_matching_[DISEASE]_[BIOMARKER]_[DATE].md`

### Report Structure

```
# Clinical Trial Matching Report

**Patient**: [Disease] with [biomarker(s)]
**Date**: [Date]
**Trials Analyzed**: [N] | **Top Matches**: [N with score >= 60]

## Executive Summary
Top 3 trials with NCT ID, title, score, and one-line reason.

## Patient Profile Summary
Table: disease (with EFO ID), biomarkers, stage, prior treatment, ECOG, location.
Biomarker actionability table: biomarker | level | FDA-approved drugs | evidence tier.

## Ranked Trial Matches
For each trial:
  - Trial Match Score breakdown table (molecular/clinical/evidence/phase/geo)
  - Trial details (phase, status, sponsor, dates)
  - Interventions with mechanism
  - Molecular eligibility match
  - Clinical eligibility assessment
  - Evidence for efficacy (FDA, literature, mechanism)
  - Top 5 trial sites
  - Next steps / contact info

## Trials by Category
  Targeted therapy | Immunotherapy | Combination | Basket/Platform

## Additional Testing Recommendations
  Table: biomarker not yet tested | test needed | trials unlocked | priority

## Alternative Options
  Expanded access programs | Off-label FDA-approved options

## Evidence Grading Summary
  Count of T1/T2/T3/T4 evidence items

## Completeness Checklist
  Each analysis step: Done/Partial/Failed | source tool

## Disclaimer
  "For informational purposes only. Verify current status at ClinicalTrials.gov."

## Sources
  ClinicalTrials.gov, OpenTargets, CIViC, ChEMBL, FDA, DrugBank, PubMed, OLS/EFO, MyGene
```

---

## Known Gotchas

1. **`search_clinical_trials` requires `query_term`**: This parameter is REQUIRED even for pure disease-only searches. Passing only `condition` without `query_term` will fail.

2. **`clinical_trials_search` requires `action="search_studies"`**: The `action` field must be the exact string `"search_studies"`. Similarly, `clinical_trials_get_details` requires `action="get_study_details"`.

3. **CIViC search tools do NOT filter**: `civic_search_variants` and `civic_search_evidence_items` return results alphabetically and ignore the `query` parameter for filtering. To get variants for a specific gene, use `civic_get_variants_by_gene` with the integer CIViC gene ID.

4. **CIViC takes integer gene ID, not symbol**: `civic_get_variants_by_gene` requires `gene_id` as an integer (e.g., `19` for EGFR), not the gene symbol string.

5. **DrugBank tools require all four parameters**: `drugbank_get_targets_by_drug_name_or_drugbank_id` and `drugbank_get_indications_by_drug_name_or_drugbank_id` require ALL of: `query`, `case_sensitive`, `exact_match`, `limit`. Omitting any causes an error.

6. **`fda_pharmacogenomic_biomarkers` takes no parameters**: Call it without arguments to get the full list. Use `limit=1000` if a limit parameter is needed to retrieve all entries.

7. **Basket trial search: use simple queries**: Overly specific queries like "NTRK fusion tumor agnostic" return zero results from ClinicalTrials.gov. Start with `"NTRK solid tumor"` then broaden/narrow from there.

8. **NCT ID field name differs between tools**: `search_clinical_trials` returns `"NCT ID"` (with space), while `clinical_trials_search` returns `"nctId"` (camelCase). Handle both when deduplicating.

9. **HER2/ERBB2 dual search**: Search trials using both "HER2" and "ERBB2" — trial descriptions use both interchangeably.

10. **Eligibility text is free-form**: There is no structured biomarker field. Parse the `eligibility_criteria` text from `get_clinical_trial_eligibility_criteria`. Scan inclusion section for required biomarkers and exclusion section for disqualifying ones.

11. **Batch limit of 10 NCT IDs**: All `get_clinical_trial_*` batch tools accept arrays of NCT IDs. Process in batches of 10 for reliability.

12. **OpenTargets drug lookup uses `drugName` not `genericName`**: Pass the common drug name (e.g., `"osimertinib"`) as `drugName`.

---

## Edge Case Handling

- **No trials found**: Broaden to gene-level, then pathway-level, then basket trials. Suggest additional biomarker testing and report off-label/compassionate use options.
- **Rare biomarkers**: Search gene-level and mechanism-level trials. Check CIViC for any evidence. Note rarity and recommend molecular tumor board review.
- **Multiple biomarkers**: Search each independently and in combination. Score by most actionable biomarker. Flag synergistic targets.
- **Conflicting eligibility**: Score partial match transparently. Highlight which criteria are met vs unmet. Suggest contacting the PI for borderline cases.

---

## Common Patterns

**Targeted therapy** (e.g., NSCLC + EGFR L858R, failed platinum): Resolve NSCLC (EFO_0003060) and EGFR (ENSG00000146648). Search "EGFR mutation" and "EGFR L858R". Identify TKIs and check FDA approval. Prioritize targeted therapy trials; include immunotherapy options.

**Immunotherapy** (e.g., Melanoma, TMB-high, PD-L1+, failed ipilimumab): Search melanoma + "TMB" + "PD-L1". Identify checkpoint inhibitors. Check FDA TMB-high indications. Focus on anti-PD-1/PD-L1 and combination trials.

**Basket trial** (e.g., any solid tumor with NTRK fusion): Search "NTRK fusion" and "NTRK solid tumor". Filter for biomarker-agnostic trials. Identify larotrectinib/entrectinib. Highlight FDA tissue-agnostic approval.

**Post-progression** (e.g., Breast cancer, failed CDK4/6, ESR1 mutation): Search "breast cancer" + "ESR1" + "CDK4/6 resistance". Score by ESR1 mutation and prior treatment requirements. Identify SERDs and novel endocrine agents.

**Geographic** (e.g., lung cancer within 100 miles of Boston): Broad lung cancer search. Batch-fetch locations. Filter for Massachusetts/nearby states. Prioritize by proximity.

---

## Tool Quick Reference

Full parameter schemas and response structures: `references/tools.md`.

**ClinicalTrials.gov**: `search_clinical_trials` (primary search) · `clinical_trials_search` (alternative) · `clinical_trials_get_details` (single trial) · `get_clinical_trial_eligibility_criteria` · `get_clinical_trial_locations` · `get_clinical_trial_descriptions` · `get_clinical_trial_status_and_dates` · `get_clinical_trial_conditions_and_interventions` · `get_clinical_trial_outcome_measures` · `extract_clinical_trial_outcomes` · `extract_clinical_trial_adverse_events`

**Gene/Disease**: `MyGene_query_genes` · `OpenTargets_get_disease_id_description_by_name` · `OpenTargets_get_target_id_description_by_name` · `ols_search_efo_terms` · `ols_get_efo_term` · `ols_get_efo_term_children`

**Drug/Mechanism**: `OpenTargets_get_drug_id_description_by_name` · `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` · `OpenTargets_get_associated_drugs_by_target_ensemblID` · `OpenTargets_get_associated_drugs_by_disease_efoId` · `OpenTargets_get_approved_indications_by_drug_chemblId` · `OpenTargets_target_disease_evidence` · `ChEMBL_search_drugs` · `ChEMBL_get_drug_mechanisms` · `drugbank_get_targets_by_drug_name_or_drugbank_id` · `drugbank_get_indications_by_drug_name_or_drugbank_id`

**Evidence**: `fda_pharmacogenomic_biomarkers` · `FDA_get_indications_by_drug_name` · `FDA_get_mechanism_of_action_by_drug_name` · `FDA_get_clinical_studies_info_by_drug_name` · `FDA_get_adverse_reactions_by_drug_name` · `civic_get_variants_by_gene` · `civic_get_variant` · `civic_search_evidence_items` · `civic_search_therapies` · `civic_search_diseases` · `PubMed_search_articles` · `openalex_literature_search` · `PharmGKB_search_genes` · `PharmGKB_get_clinical_annotations`
