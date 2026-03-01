---
name: tooluniverse-adverse-event-detection
description: Detect and analyze adverse drug event signals using FDA FAERS data, drug labels, disproportionality analysis (PRR, ROR, IC), and biomedical evidence. Generates quantitative safety signal scores (0-100) with evidence grading. Use for post-market surveillance, pharmacovigilance, drug safety assessment, adverse event investigation, and regulatory decision support.
---

# Adverse Drug Event Signal Detection & Analysis

Automated pipeline for detecting, quantifying, and contextualizing adverse drug event signals using FAERS disproportionality analysis, FDA label mining, mechanism-based prediction, and literature evidence. Produces a quantitative Safety Signal Score (0-100) for regulatory and clinical decision-making.

**KEY PRINCIPLES**:
1. **Signal quantification first** — Every adverse event must have PRR/ROR/IC with confidence intervals
2. **Serious events priority** — Deaths, hospitalizations, life-threatening events always analyzed first
3. **Multi-source triangulation** — FAERS + FDA labels + OpenTargets + DrugBank + literature
4. **Context-aware assessment** — Distinguish drug-specific vs class-wide vs confounding signals
5. **Report-first approach** — Create report file FIRST, update progressively
6. **Evidence grading mandatory** — T1 (regulatory/boxed warning) through T4 (computational)
7. **English-first queries** — Always use English drug names in tool calls, respond in user's language

---

## When to Use

Apply when user asks about: safety signals for a drug, adverse event detection, FAERS signals, "Is [drug] associated with [event]?", comparative safety of drug classes, post-market surveillance, pharmacovigilance signal detection, or disproportionality analysis.

**Differentiation from tooluniverse-pharmacovigilance**: This skill focuses specifically on **signal detection and quantification** using disproportionality analysis (PRR, ROR, IC) with statistical rigor, produces a quantitative **Safety Signal Score (0-100)**, and performs **comparative safety analysis** across drug classes.

---

## Workflow Overview

```
Phase 0: Input Parsing & Drug Disambiguation
  Resolve drug name → ChEMBL ID, DrugBank ID, drug class, mechanism
    |
Phase 1: FAERS Adverse Event Profiling
  Top AEs by frequency, seriousness/outcome distributions, demographics
    |
Phase 2: Disproportionality Analysis (Signal Detection)  ← CORE
  Calculate PRR, ROR, IC with 95% CI for each AE; classify signal strength
    |
Phase 3: FDA Label Safety Information
  Boxed warnings, contraindications, warnings/precautions, special populations
    |
Phase 4: Mechanism-Based Adverse Event Context
  OpenTargets target safety, off-target effects, ADMET predictions
    |
Phase 5: Comparative Safety Analysis
  Compare to drug class; identify unique vs class-wide signals
    |
Phase 6: Drug-Drug Interactions & Risk Factors
  FDA label DDIs, PharmGKB pharmacogenomics, FDA PGx biomarkers
    |
Phase 7: Literature Evidence
  PubMed safety studies, citation analysis, preprint signals
    |
Phase 8: Risk Assessment & Safety Signal Score
  Calculate Safety Signal Score (0-100); evidence grading T1-T4
    |
Phase 9: Report Synthesis & Recommendations
  Monitoring, risk mitigation, patient counseling, completeness checklist
```

---

## Phase 0: Input Parsing & Drug Disambiguation

Resolve the drug name to structured identifiers before any FAERS queries.

1. Call `OpenTargets_get_drug_chembId_by_generic_name` with the drug name to get ChEMBL ID. Extract `data.search.hits[0].id`.
2. Call `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` to get mechanism of action and primary target Ensembl ID.
3. Call `OpenTargets_get_drug_blackbox_status_by_chembl_ID` to check `hasBeenWithdrawn` and `blackBoxWarning`.
4. Call `OpenTargets_get_drug_indications_by_chemblId` for approved indications.
5. Call `drugbank_get_safety_by_drug_name_or_drugbank_id` (exact_match=False) to get DrugBank ID, toxicity, and food interactions.
6. Call `drugbank_get_targets_by_drug_name_or_drugbank_id` for primary drug targets.

Output a Drug Identification table: generic name, ChEMBL ID, DrugBank ID, drug class, mechanism, primary target, black box warning status, withdrawn status.

---

## Phase 1: FAERS Adverse Event Profiling

Use the drug's uppercase generic name (e.g., "ATORVASTATIN") for all `medicinalproduct` parameters.

1. Call `FAERS_count_reactions_by_drug_event` — top adverse events by report count.
2. Call `FAERS_count_seriousness_by_drug_event` — serious vs non-serious breakdown.
3. Call `FAERS_count_outcomes_by_drug_event` — outcomes (Fatal, Recovered, Unknown, etc.).
4. Call `FAERS_count_patient_age_distribution` — age group breakdown.
5. Call `FAERS_count_death_related_by_drug` — alive vs death counts.
6. Call `FAERS_count_reportercountry_by_drug_event` — geographic distribution.
7. Call `FAERS_filter_serious_events` with seriousness_type="all" for top serious reactions, then repeat with seriousness_type="death".
8. Call `FAERS_rollup_meddra_hierarchy` for MedDRA preferred-term rollup (top 50 terms).

**MedDRA hierarchy note**: The rollup groups individual reactions into MedDRA Preferred Terms (PT). Use PT-level data for disproportionality analysis (Phase 2). Higher-level System Organ Classes (SOC) are useful for executive summaries.

Output: total reports, serious/non-serious split, fatal count, top 10 AEs table, outcome distribution table.

---

## Phase 2: Disproportionality Analysis (Signal Detection)

**This is the core of the skill.** For each of the top 15-20 adverse events (prioritize serious ones), calculate disproportionality metrics.

Call `FAERS_calculate_disproportionality` with `drug_name` and `adverse_event` for each event. The tool returns PRR, ROR, and IC each with 95% confidence intervals, a signal detection verdict, and the 2x2 contingency table (a=drug+event, b=drug-no-event, c=no-drug+event, d=no-drug-no-event).

### Signal Detection Criteria

**Proportional Reporting Ratio (PRR)**:
- Formula: PRR = (a/(a+b)) / (c/(c+d))
- Signal threshold: PRR >= 2.0 AND lower 95% CI > 1.0 AND case count >= 3

**Reporting Odds Ratio (ROR)**:
- Formula: ROR = (a*d) / (b*c)
- Signal threshold: lower 95% CI > 1.0

**Information Component (IC)**:
- Formula: IC = log2(observed/expected)
- Signal threshold: lower 95% CI > 0

### Signal Strength Classification

| Strength | PRR | ROR Lower CI | IC Lower CI | Action |
|----------|-----|-------------|-------------|--------|
| **Strong** | >= 5.0 | >= 3.0 | >= 2.0 | Immediate investigation |
| **Moderate** | 3.0-4.9 | 2.0-2.9 | 1.0-1.9 | Active monitoring |
| **Weak** | 2.0-2.9 | 1.0-1.9 | 0-0.9 | Routine monitoring |
| **No signal** | < 2.0 | < 1.0 | < 0 | Standard pharmacovigilance |

For strong and moderate signals, call `FAERS_stratify_by_demographics` with stratify_by="sex" and stratify_by="age" to understand the affected population. Sex code note: 0=Unknown, 1=Male, 2=Female.

Output: signal detection summary table (event, case count a, PRR + CI, ROR + CI, IC, signal strength), demographics breakdown for key signals.

---

## Phase 3: FDA Label Safety Information

Query each label section separately. Most sections use lowercase drug name.

1. Call `FDA_get_boxed_warning_info_by_drug_name` — check for boxed warning text.
2. Call `FDA_get_contraindications_by_drug_name` — absolute contraindications.
3. Call `FDA_get_warnings_by_drug_name` — warnings and precautions.
4. Call `FDA_get_adverse_reactions_by_drug_name` — labeled adverse reactions.
5. Call `FDA_get_drug_interactions_by_drug_name` — labeled DDIs.
6. Call `FDA_get_pharmacogenomics_info_by_drug_name` — PGx from label.
7. Call `FDA_get_pregnancy_or_breastfeeding_info_by_drug_name`.
8. Call `FDA_get_geriatric_use_info_by_drug_name`.
9. Call `FDA_get_pediatric_use_info_by_drug_name`.

Output: boxed warning status, contraindications list, warnings/precautions table, DDI table, special populations summary.

---

## Phase 4: Mechanism-Based Adverse Event Context

1. Call `OpenTargets_get_target_safety_profile_by_ensemblID` using the target Ensembl ID from Phase 0 — returns safety liabilities (direction, effect type, evidence source).
2. Call `OpenTargets_get_drug_adverse_events_by_chemblId` — returns FAERS-derived AEs with log-likelihood ratios (useful for cross-checking Phase 2 results).
3. Call `OpenTargets_get_drug_warnings_by_chemblId` — safety warnings and withdrawal history.
4. If SMILES is available (from DrugBank or PharmGKB): call `ADMETAI_predict_toxicity` and `ADMETAI_predict_CYP_interactions` for computational toxicity predictions.

Output: target safety liability table, OpenTargets significant AEs with logLR, ADMET predictions if available.

---

## Phase 5: Comparative Safety Analysis

1. For each key adverse event with a signal, call `FAERS_compare_drugs` with drug1=target drug, drug2=class comparator, adverse_event=event. Repeat for 2-4 comparators in the same drug class.
2. Call `FAERS_count_additive_adverse_reactions` with the full list of class members to get aggregate class AE profile.
3. Call `FAERS_count_additive_seriousness_classification` for class-wide seriousness.
4. Identify which signals are class-wide (present in all comparators) vs drug-specific (unique to target drug).

Output: head-to-head comparison table per event (drug, PRR, ROR, cases, signal strength), class-wide vs drug-specific signal classification.

---

## Phase 6: Drug-Drug Interactions & Risk Factors

1. Call `FDA_get_drug_interactions_by_drug_name` (already done in Phase 3 — reuse results).
2. Call `drugbank_get_drug_interactions_by_drug_name_or_id` for additional DDI data.
3. Call `DailyMed_parse_drug_interactions` for DailyMed label DDIs.
4. Call `PharmGKB_search_drugs` to get PharmGKB drug ID, then `PharmGKB_get_drug_details`.
5. Call `PharmGKB_get_dosing_guidelines` with key pharmacogenes (e.g., SLCO1B1 for statins, CYP2C19 for PPIs).
6. Call `fda_pharmacogenomic_biomarkers` with the drug name.

Output: DDI table (drug, mechanism, AE risk, management), PGx risk factors table (gene, variant, phenotype, recommendation, evidence level).

---

## Phase 7: Literature Evidence

1. Call `PubMed_search_articles` with query "[drug] adverse events safety [key signal]", limit=20.
2. Call `openalex_search_works` with similar query for citation counts.
3. Call `EuropePMC_search_articles` with source="PPR" for preprint emerging signals.

Output: key safety publications table (PMID, title, year, journal), evidence summary (meta-analyses, RCTs, case reports counts with key findings).

---

## Phase 8: Risk Assessment & Safety Signal Score

### Safety Signal Score Components (0-100)

**Component 1: FAERS Signal Strength (0-35 pts)**
- Any signal with PRR >= 5 AND ROR lower CI >= 3: 35 pts
- Any signal with PRR 3-5 AND ROR lower CI 2-3: 20 pts
- Any signal with PRR 2-3 AND ROR lower CI 1-2: 10 pts
- No signals: 0 pts

**Component 2: Serious Adverse Events (0-30 pts)**
- Deaths with high count (>100): 30 pts
- Deaths with low count (1-100): 25 pts
- Life-threatening events only: 20 pts
- Hospitalizations only: 15 pts
- Non-serious only: 0 pts

**Component 3: FDA Label Warnings (0-25 pts)**
- Boxed warning OR drug withdrawn/restricted: 25 pts
- Contraindications present: 15 pts
- Warnings and precautions present: 10 pts
- Adverse reactions only: 5 pts
- No label warnings: 0 pts

**Component 4: Literature Evidence (0-10 pts)**
- Meta-analyses confirming signals: 10 pts
- Multiple RCTs with safety concerns: 7 pts
- Case reports/case series: 4 pts
- No published safety concerns: 0 pts

**Score Interpretation:**
| Score | Interpretation | Action |
|-------|---------------|--------|
| 75-100 | High concern | Immediate regulatory attention required |
| 50-74 | Moderate concern | Significant monitoring; consider risk mitigation |
| 25-49 | Low-moderate concern | Enhanced monitoring; standard risk management |
| 0-24 | Low concern | Standard safety profile; routine pharmacovigilance |

### Evidence Grading (apply to each signal)

| Tier | Criteria | Example |
|------|----------|---------|
| **T1** | Boxed warning + confirmed by RCTs + PRR > 10 | Metformin: Lactic acidosis |
| **T2** | Label warning + FAERS signal (PRR 3-10) + published studies | Atorvastatin: Rhabdomyolysis |
| **T3** | FAERS signal (PRR 2-3) + case reports | Atorvastatin: Pancreatitis |
| **T4** | Computational prediction only (ADMET) or weak signal | ADMETAI hepatotoxicity prediction |

---

## Phase 9: Report Synthesis

Create and progressively update a file named `[DRUG]_adverse_event_report.md`. Structure:

1. **Executive Summary** — 2-3 paragraphs; list top 3 signals with PRR/ROR; state Safety Signal Score and regulatory status.
2. **Drug Identification** (Phase 0 output)
3. **FAERS Adverse Event Profile** (Phase 1 output)
4. **Disproportionality Analysis** (Phase 2 output)
5. **FDA Label Safety** (Phase 3 output)
6. **Mechanism-Based Context** (Phase 4 output)
7. **Comparative Safety** (Phase 5 output)
8. **DDIs & PGx Risk** (Phase 6 output)
9. **Literature Evidence** (Phase 7 output)
10. **Risk Assessment** (Phase 8 output)
11. **Clinical Recommendations** — monitoring frequency table, risk mitigation table, patient counseling points, high-risk populations table.
12. **Data Sources** — all tools and databases used with timestamps.

---

## Known Gotchas

**FDA label NOT_FOUND is normal**: `FDA_get_boxed_warning_info_by_drug_name` returns `{error: {code: "NOT_FOUND"}}` when no boxed warning exists — most drugs have no boxed warning. Always check for this pattern before accessing results. Same applies to other label section tools when sections are absent.

**FAERS uses uppercase drug names**: Pass drug names in ALL CAPS (e.g., "ATORVASTATIN", "SIMVASTATIN") for the `medicinalproduct` parameter. Mixed case or lowercase may return fewer results.

**FAERS brand vs generic names**: FAERS reporters sometimes use brand names (e.g., "LIPITOR" vs "ATORVASTATIN"). Try both if initial counts seem low; use `FDA_get_brand_name_generic_name` for cross-reference.

**OpenTargets adverse events use logLR, not PRR**: `OpenTargets_get_drug_adverse_events_by_chemblId` returns `logLR` values from their internal FAERS analysis — these are not directly comparable to PRR/ROR. Use them for cross-checking, not as the primary disproportionality metric.

**Sex codes in FAERS stratification**: `FAERS_stratify_by_demographics` with stratify_by="sex" returns numeric codes: 0=Unknown, 1=Male, 2=Female.

**PharmGKB drug IDs**: `PharmGKB_search_drugs` returns IDs in format "PA448500". These are required for `PharmGKB_get_drug_details`; do not confuse with DrugBank IDs ("DB01076").

**fda_pharmacogenomic_biomarkers may return empty**: This tool returns empty results for many drugs. Treat as supplementary — fall back to PharmGKB and the FDA label PGx section.

**ADMETAI requires SMILES array**: Pass SMILES as an array of strings, not a single string: `smiles=["CC(C)..."]`.

**OpenTargets `get_drug_warnings_by_chemblId` may return empty**: This is normal for drugs with no regulatory warnings — an empty result means no warnings on record, not a tool failure.

**Confounding by indication**: Death reports for chemotherapy or heart failure drugs often reflect disease progression, not drug toxicity. Always note this limitation for drugs treating severe diseases.

**Drug combinations in FAERS**: For polypharmacy analysis, use `FAERS_search_reports_by_drug_combination`. Counts from single-drug queries may include reports where other drugs are co-suspects.

---

## Common Patterns

**Full Safety Signal Profile** (single drug, comprehensive): Run all phases 0-9. Best for regulatory submissions and safety reviews.

**Specific Adverse Event Investigation** ("Does [drug] cause [event]?"): Focus on Phases 0, 2, 3, 7. Calculate disproportionality for the specific event, check label, search literature.

**Drug Class Comparison**: Focus on Phases 0, 2, 5. Compare 3-5 class members for key events using `FAERS_compare_drugs`.

**Emerging Signal Detection**: Focus on Phases 1, 2, 7. Screen top 20+ FAERS events for signals not yet in FDA label.

**Pharmacogenomic Risk Assessment**: Focus on Phases 0, 6. PharmGKB + FDA PGx biomarkers + label PGx section.

**Pre-Approval Assessment** (new drug with limited FAERS): Focus on Phases 4, 7. ADMET predictions + target safety + literature.

**Drug with No FAERS Reports**: Skip Phases 1-2; rely on label (Phase 3), mechanism (Phase 4), and literature (Phase 7). Safety Signal Score will be lower due to absence of signal detection data.

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `FAERS_calculate_disproportionality` | Manual calculation from `FAERS_count_*` raw data | Published PRR values from literature |
| `FAERS_count_reactions_by_drug_event` | `FAERS_rollup_meddra_hierarchy` | `OpenTargets_get_drug_adverse_events_by_chemblId` |
| `FDA_get_boxed_warning_info_by_drug_name` | `OpenTargets_get_drug_blackbox_status_by_chembl_ID` | DrugBank safety section |
| `FDA_get_contraindications_by_drug_name` | `FDA_get_warnings_by_drug_name` | DrugBank safety |
| `OpenTargets_get_drug_chembId_by_generic_name` | `ChEMBL_search_drugs` | Manual ChEMBL search |
| `PharmGKB_search_drugs` | `fda_pharmacogenomic_biomarkers` | FDA label PGx section |
| `PubMed_search_articles` | `openalex_search_works` | `EuropePMC_search_articles` |

---

## Tool Quick Reference

Detailed parameter tables and full response shapes: see `references/tools.md`.

| Tool | Purpose |
|------|---------|
| `OpenTargets_get_drug_chembId_by_generic_name` | Resolve drug name to ChEMBL ID |
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | Mechanism of action and target Ensembl ID |
| `OpenTargets_get_drug_blackbox_status_by_chembl_ID` | Black box warning and withdrawal status |
| `OpenTargets_get_drug_indications_by_chemblId` | Approved/investigational indications |
| `OpenTargets_get_drug_adverse_events_by_chemblId` | FAERS-derived AEs with logLR (cross-check) |
| `OpenTargets_get_target_safety_profile_by_ensemblID` | Target-based safety liabilities |
| `OpenTargets_get_drug_warnings_by_chemblId` | Regulatory warnings and withdrawal history |
| `drugbank_get_safety_by_drug_name_or_drugbank_id` | DrugBank ID, toxicity, food interactions |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | Drug targets from DrugBank |
| `drugbank_get_drug_interactions_by_drug_name_or_id` | DDIs from DrugBank |
| `FAERS_count_reactions_by_drug_event` | Top AEs by report count |
| `FAERS_count_seriousness_by_drug_event` | Serious vs non-serious split |
| `FAERS_count_outcomes_by_drug_event` | Outcome distribution (fatal, recovered, etc.) |
| `FAERS_count_patient_age_distribution` | Age group breakdown |
| `FAERS_count_death_related_by_drug` | Alive vs death counts |
| `FAERS_count_reportercountry_by_drug_event` | Geographic distribution |
| `FAERS_filter_serious_events` | Top reactions for a given seriousness type |
| `FAERS_rollup_meddra_hierarchy` | MedDRA PT-level rollup (top 50) |
| `FAERS_calculate_disproportionality` | PRR, ROR, IC with 95% CI and signal verdict |
| `FAERS_stratify_by_demographics` | Sex/age/country breakdown for a drug+event pair |
| `FAERS_compare_drugs` | Side-by-side PRR/ROR/IC for two drugs and one event |
| `FAERS_count_additive_adverse_reactions` | Aggregate AEs across a list of drugs |
| `FAERS_count_additive_seriousness_classification` | Aggregate seriousness across a list of drugs |
| `FAERS_search_reports_by_drug_and_reaction` | Individual reports for drug+reaction pair |
| `FDA_get_boxed_warning_info_by_drug_name` | Boxed warning text (NOT_FOUND = no warning) |
| `FDA_get_contraindications_by_drug_name` | Contraindications from FDA label |
| `FDA_get_warnings_by_drug_name` | Warnings and precautions from FDA label |
| `FDA_get_adverse_reactions_by_drug_name` | Labeled adverse reactions section |
| `FDA_get_drug_interactions_by_drug_name` | Labeled DDIs |
| `FDA_get_pharmacogenomics_info_by_drug_name` | PGx section from FDA label |
| `FDA_get_pregnancy_or_breastfeeding_info_by_drug_name` | Pregnancy/lactation section |
| `FDA_get_geriatric_use_info_by_drug_name` | Geriatric use section |
| `FDA_get_pediatric_use_info_by_drug_name` | Pediatric use section |
| `fda_pharmacogenomic_biomarkers` | FDA PGx biomarker table |
| `PharmGKB_search_drugs` | Find PharmGKB drug ID |
| `PharmGKB_get_drug_details` | Detailed PharmGKB drug record |
| `PharmGKB_get_dosing_guidelines` | Dosing guidelines by gene |
| `PharmGKB_get_clinical_annotations` | Clinical PGx annotations |
| `DailyMed_parse_drug_interactions` | DDI section from DailyMed label |
| `ADMETAI_predict_toxicity` | Computational toxicity predictions from SMILES |
| `ADMETAI_predict_CYP_interactions` | CYP inhibition/substrate predictions from SMILES |
| `PubMed_search_articles` | PubMed safety literature search |
| `openalex_search_works` | Literature with citation counts |
| `EuropePMC_search_articles` | Articles and preprints via EuropePMC |
| `search_clinical_trials` | Clinical trial safety data |
