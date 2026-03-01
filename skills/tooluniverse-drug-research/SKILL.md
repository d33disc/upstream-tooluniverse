---
name: tooluniverse-drug-research
description: Generates comprehensive drug research reports with compound disambiguation, evidence grading, and mandatory completeness sections. Covers identity, chemistry, pharmacology, targets, clinical trials, safety, pharmacogenomics, and ADMET properties. Use when users ask about drugs, medications, therapeutics, or need drug profiling, safety assessment, or clinical development research.
---

# Drug Research Strategy

Comprehensive drug investigation using 50+ ToolUniverse tools across chemical databases, clinical trials, adverse events, pharmacogenomics, and literature.

**KEY PRINCIPLES**:
1. **Report-first approach** — Create report file FIRST, then populate progressively
2. **Compound disambiguation FIRST** — Resolve identifiers before research
3. **Citation requirements** — Every fact must have inline source attribution
4. **Evidence grading** — Grade claims by evidence strength (★★★/★★☆/★☆☆/☆☆☆)
5. **Mandatory completeness** — All sections must exist, even if "data unavailable"
6. **English-first queries** — Always use English drug/compound names in tool calls, even if the user writes in another language. Respond in the user's language.

---

## Mandatory Workflow (Follow in Order)

### Step 1 — Create Report File

Before any tool calls, create `[DRUG]_drug_report.md` with all 11 section headers below and `[Researching...]` as placeholder in each subsection. The user watches the file grow; do not show raw tool output.

```
## Executive Summary [Researching...]

## 1. Compound Identity
### 1.1 Database Identifiers [Researching...]
### 1.2 Structural Information [Researching...]
### 1.3 Names & Synonyms [Researching...]

## 2. Chemical Properties
### 2.1 Physicochemical Profile [Researching...]
### 2.2 Drug-Likeness Assessment [Researching...]
### 2.3 Solubility & Permeability [Researching...]
### 2.4 Salt Forms & Polymorphs [Researching...]
### 2.5 Structure Visualization [Researching...]

## 3. Mechanism & Targets
### 3.1 Primary Mechanism of Action [Researching...]
### 3.2 Primary Target(s) [Researching...]
### 3.3 Target Selectivity & Off-Targets [Researching...]
### 3.4 Bioactivity Profile (ChEMBL) [Researching...]

## 4. ADMET Properties
### 4.1 Absorption [Researching...]
### 4.2 Distribution [Researching...]
### 4.3 Metabolism [Researching...]
### 4.4 Excretion [Researching...]
### 4.5 Toxicity Predictions [Researching...]

## 5. Clinical Development
### 5.1 Development Status [Researching...]
### 5.2 Clinical Trial Landscape [Researching...]
### 5.3 Approved Indications [Researching...]
### 5.4 Investigational Indications [Researching...]
### 5.5 Key Efficacy Data [Researching...]
### 5.6 Biomarkers & Companion Diagnostics [Researching...]

## 6. Safety Profile
### 6.1 Clinical Adverse Events [Researching...]
### 6.2 Post-Marketing Safety (FAERS) [Researching...]
### 6.3 Black Box Warnings [Researching...]
### 6.4 Contraindications [Researching...]
### 6.5 Drug-Drug Interactions [Researching...]
### 6.5.2 Drug-Food Interactions [Researching...]
### 6.6 Dose Modification Guidance [Researching...]
### 6.7 Drug Combinations & Regimens [Researching...]

## 7. Pharmacogenomics
### 7.1 Relevant Pharmacogenes [Researching...]
### 7.2 Clinical Annotations [Researching...]
### 7.3 Dosing Guidelines (CPIC/DPWG) [Researching...]
### 7.4 Actionable Variants [Researching...]

## 8. Regulatory & Labeling
### 8.1 Approval Status [Researching...]
### 8.2 Label Highlights [Researching...]
### 8.3 Patents & Exclusivity [Researching...]
### 8.4 Label Changes & Warnings [Researching...]
### 8.5 Special Populations [Researching...]
### 8.6 Regulatory Timeline & History [Researching...]

## 9. Literature & Research Landscape
### 9.1 Publication Metrics [Researching...]
### 9.2 Research Themes [Researching...]
### 9.3 Recent Key Publications [Researching...]
### 9.4 Real-World Evidence [Researching...]

## 10. Conclusions & Assessment
### 10.1 Drug Profile Scorecard [Researching...]
### 10.2 Key Strengths [Researching...]
### 10.3 Key Concerns/Limitations [Researching...]
### 10.4 Research Gaps [Researching...]
### 10.5 Comparative Analysis [Researching...]

## 11. Data Sources & Methodology
### 11.1 Primary Data Sources [Researching...]
### 11.2 Tool Call Summary [Researching...]
### 11.3 Quality Control Metrics [Researching...]
```

---

### Step 2 — Compound Disambiguation (Phase 1)

Resolve all identifiers before starting research. Update Section 1 immediately.

1. Call `PubChem_get_CID_by_compound_name` → extract CID, canonical SMILES, formula
2. Call `ChEMBL_search_compounds` with drug name → extract ChEMBL ID, pref_name
3. Call `DailyMed_search_spls` with drug name → extract set_id, NDC codes (if approved drug)
4. Call `PharmGKB_search_drugs` with drug name → extract PharmGKB ID (PA...)

**Ambiguity rules**:
- Salt forms (metformin vs metformin HCl): note all CIDs, use parent compound for ADMET
- Isomers (omeprazole vs esomeprazole): verify SMILES, treat as separate entries if distinct
- Prodrugs (enalapril vs enalaprilat): document both, note conversion
- Brand confusion: clarify with user before proceeding

---

### Step 3 — FDA Label Core Fields (Approved Drugs)

For any approved drug, retrieve label sections early. Call `DailyMed_get_spl_sections_by_setid` with the set_id from Step 2. Batch into 3-4 calls grouped by phase:

- **Phase 1 (Mechanism & Chemistry)**: `mechanism_of_action`, `pharmacodynamics`, `chemistry`
- **Phase 2 (ADMET & PK)**: `clinical_pharmacology`, `pharmacokinetics`, `drug_interactions`
- **Phase 3 (Safety & Dosing)**: `warnings_and_cautions`, `adverse_reactions`, `dosage_and_administration`
- **Phase 4 (PGx & Regulatory)**: `pharmacogenomics`, `clinical_studies`, `description`, `inactive_ingredients`, `indications_and_usage`

This ensures authoritative data even if prediction tools fail.

---

### Step 4 — Chemical Properties (Section 2)

1. Call `PubChem_get_compound_properties_by_CID` → MW, formula, XLogP, TPSA, HBD, HBA, rotatable bonds
2. Call `ADMETAI_predict_physicochemical_properties(smiles=[smiles])` → MW, logP, HBD, HBA, Lipinski, QED, TPSA
3. Call `ADMETAI_predict_solubility_lipophilicity_hydration(smiles=[smiles])` → Solubility, Lipophilicity
4. Call `DailyMed_get_spl_sections_by_setid` with `sections=["chemistry"]` → salt forms, polymorphs
5. Call `DailyMed_get_spl_sections_by_setid` with `sections=["description", "inactive_ingredients"]` → formulation, excipients
6. If multiple formulations exist, call `DailyMed_parse_clinical_pharmacology` per set_id to compare Tmax/Cmax/AUC/half-life across IR/ER/XR forms

Embed 2D structure image: `https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=[CID]&t=l`

---

### Step 5 — Mechanism & Targets (Section 3)

1. Call `DailyMed_get_spl_sections_by_setid` with `sections=["mechanism_of_action", "pharmacodynamics"]` → quote FDA label MOA verbatim [★★★]
2. Call `ChEMBL_search_activities(molecule_chembl_id=chembl_id, limit=100)` → get activity records with target_chembl_id, pChEMBL, standard_type
3. For each unique target_chembl_id, call `ChEMBL_get_target` → name, UniProt ID, organism [★★★]
4. Call `DGIdb_get_drug_info(drugs=[drug_name])` → target genes, interaction types [★★☆]
5. Call `PubChem_get_bioactivity_summary_by_CID` → assay summary [★★☆]

**Gotcha**: Do NOT use `ChEMBL_get_molecule_targets` — it returns unfiltered targets including irrelevant entries. Derive targets from activities instead. Filter to potent activities (pChEMBL ≥ 6.0 or IC50/EC50 ≤ 1 µM) for the primary target table. Include mutant form potency (e.g., ESR1 Y537S/D538G) for targeted therapies.

---

### Step 6 — ADMET Properties (Section 4)

**Primary path (ADMET-AI)**:
1. Call `ADMETAI_predict_bioavailability(smiles=[smiles])` → Bioavailability_Ma, HIA_Hou, PAMPA_NCATS, Caco2_Wang, Pgp_Broccatelli
2. Call `ADMETAI_predict_BBB_penetrance(smiles=[smiles])` → BBB_Martins (0-1 probability)
3. Call `ADMETAI_predict_CYP_interactions(smiles=[smiles])` → CYP1A2, CYP2C9, CYP2C19, CYP2D6, CYP3A4
4. Call `ADMETAI_predict_clearance_distribution(smiles=[smiles])` → Clearance, Half_Life_Obach, VDss_Lombardo, PPBR_AZ
5. Call `ADMETAI_predict_toxicity(smiles=[smiles])` → AMES, hERG, DILI, ClinTox, LD50_Zhu, Carcinogens

**Fallback (if ADMET-AI fails)**: Use label sections `clinical_pharmacology`, `pharmacokinetics`, `drug_interactions`, `warnings_and_cautions` from Step 3. Do NOT leave Section 4 as "predictions unavailable" — label PK is acceptable alternative [★★★].

---

### Step 7 — Clinical Development (Section 5)

1. Call `search_clinical_trials(intervention=drug_name, pageSize=100)` → full result set
2. **Compute phase counts from results** — count by phase (1/2/3/4) and status (Completed/Recruiting/Active/Terminated). Show actual counts in a table, not just a list of trials.
3. Group top 5 conditions by count
4. Call `get_clinical_trial_conditions_and_interventions(nct_ids=[top_5_phase3])` → detailed conditions, arm groups
5. Call `extract_clinical_trial_outcomes(nct_ids=[completed_phase3])` → primary outcomes, efficacy measures
6. Call `extract_clinical_trial_adverse_events(nct_ids=[completed_ids])` → serious AEs, common AEs
7. Call `fda_pharmacogenomic_biomarkers(drug_name=drug_name)` → FDA-required biomarker testing, companion diagnostics [★★★]
8. Call `PharmGKB_get_clinical_annotations(drug_id=pharmgkb_id)` → response/toxicity biomarkers [★★☆]

Section 5.6 must distinguish: FDA-required testing (T1), approved companion diagnostics with device info (T1), and response predictors from PharmGKB (T2).

---

### Step 8 — Post-Marketing Safety (Section 6)

**FAERS calls**:
1. Call `FAERS_count_reactions_by_drug_event(medicinalproduct=drug_name)` → top 20 MedDRA PTs [★★★]
2. Call `FAERS_count_seriousness_by_drug_event` → serious vs non-serious counts [★★★]
3. Call `FAERS_count_outcomes_by_drug_event` → recovered/fatal/unresolved counts [★★★]
4. Call `FAERS_count_death_related_by_drug` → fatal outcome count [★★★]
5. Call `FAERS_count_patient_age_distribution` → reports by age group [★★★]

**Label-based safety**:
6. Call `DailyMed_get_spl_sections_by_setid` with `sections=["drug_interactions"]` → DDI table, CYP/transporter interactions, contraindicated combinations [★★★]
7. Call `DailyMed_get_spl_sections_by_setid` with `sections=["dosage_and_administration", "warnings_and_cautions"]` → dose modification triggers (ALT/AST thresholds, renal/hepatic impairment, CYP3A inhibitor/inducer adjustments) [★★★]
8. Call `DailyMed_get_spl_by_setid` and parse for drug-food interactions — search sections `drug_and_or_food_interactions`, `food_effect`; keywords: grapefruit, alcohol, food, meal, dairy, high-fat, fasting [★★★]
9. Call `search_clinical_trials(intervention=f"{drug_name} AND combination", pageSize=50)` → approved combinations, regimens [★★★]

**FAERS reporting requirements** (mandatory in Section 6.2):
- State the date window (e.g., "Reports from 2004–2026")
- Include seriousness breakdown (serious vs non-serious counts and ratio)
- Include a limitations paragraph: voluntary reporting, reporting bias toward serious events, causality not established, incomplete data

---

### Step 9 — Pharmacogenomics (Section 7)

**Primary path (PharmGKB)**:
1. Call `PharmGKB_search_drugs` → get PharmGKB drug ID
2. Call `PharmGKB_get_drug_details(drug_id)` → cross-references, related genes
3. For each related gene, call `PharmGKB_get_clinical_annotations` → variant-drug associations, evidence levels
4. Call `PharmGKB_get_dosing_guidelines` for relevant genes → CPIC/DPWG recommendations

**Fallback (if PharmGKB fails or times out)**: Call `DailyMed_get_spl_sections_by_setid` with `sections=["pharmacogenomics", "clinical_pharmacology"]` [★★★]; call `PubMed_search_articles(query="[drug] pharmacogenomics", max_results=5)` [★★☆]. Document the failure and note "PharmGKB unavailable; using label + literature". Do NOT leave Section 7 empty.

---

### Step 10 — Regulatory Status & Patents (Section 8)

1. Call `FDA_OrangeBook_search_drug(brand_name=drug_name)` → application number, approval dates [★★★]
2. Call `FDA_OrangeBook_get_approval_history(appl_no=app_number)` → original approval, supplements [★★★]
3. Call `FDA_OrangeBook_get_exclusivity(brand_name=drug_name)` → NCE/Pediatric/Orphan exclusivity, expiration [★★★]
4. Call `FDA_OrangeBook_get_patent_info(brand_name=drug_name)` → patent numbers, substance/formulation claims [★★★]
5. Call `FDA_OrangeBook_check_generic_availability(brand_name=drug_name)` → generic entries, TE codes, first generic date [★★★]
6. Call `DailyMed_get_spl_sections_by_setid` with `sections=["indications_and_usage"]` → breakthrough designation, priority review, orphan status [★★★]
7. Call `DailyMed_get_spl_by_setid` and extract special populations by LOINC code: pediatric (34076-0), geriatric (34082-8), pregnancy (42228-7), nursing_mothers (34080-2) [★★★]
8. Parse SPL revision history for regulatory timeline (initial approval date, major label changes, PMR/PMC commitments)

**Gotcha**: Orange Book data is US-only. Always note "EMA and PMDA approval/patent data not available via public API" in Section 8. Exact patent expiration dates may require Orange Book file download; mark estimates clearly.

---

### Step 11 — Literature (Section 9)

1. Call `PubMed_search_articles(query=drug_name, max_results=20)` → publication count, key papers
2. Call `PubMed_search_articles(query=f"{drug_name} (real-world OR observational OR effectiveness)", max_results=20)` → RWE publications
3. Call `search_clinical_trials(study_type="OBSERVATIONAL", intervention=drug_name, pageSize=50)` → registry studies, observational cohorts
4. Synthesize efficacy-vs-effectiveness gap: compare clinical trial primary outcomes vs real-world outcomes; note adherence differences

---

### Step 12 — Comparative Analysis (Section 10.5) — Optional

Run only if the user asks for comparison or if therapeutically relevant:

1. Identify comparator drugs (user-provided or inferred from indication + mechanism)
2. For each comparator, call abbreviated chain: `PubChem_get_CID_by_compound_name`, `ChEMBL_search_activities` (filter to primary target), `search_clinical_trials` (Phase 3 counts), `FAERS_count_reactions_by_drug_event` (top 5 AEs)
3. Call `search_clinical_trials(intervention=f"{drug_name} AND {comparator}")` → head-to-head trials [★★★]
4. Call `PubMed_search_articles(query=f"{drug_name} vs {comparator}", max_results=10)` → network meta-analyses [★★☆]

---

### Step 13 — Finalize Report

1. Write Executive Summary (3-5 sentences: class, mechanism, approval status, key efficacy, key safety concern)
2. Write Section 10 Scorecard — score efficacy, safety, PK, target validation, competitive position on 1-5 scale
3. Run completeness audit against checklist below
4. Update Section 11 with all data sources and tool call log

---

## Section Completeness Checklist

Verify before delivering the report:

**Section 1 (Identity)**
- [ ] PubChem CID with link
- [ ] ChEMBL ID (or "Not in ChEMBL")
- [ ] Canonical SMILES
- [ ] Molecular formula and weight
- [ ] At least 3 brand names or "Generic only"
- [ ] Salt forms identified

**Section 2 (Chemistry)**
- [ ] 6+ physicochemical properties in table (including pKa if available)
- [ ] Lipinski assessment with pass/fail
- [ ] QED score with interpretation
- [ ] Solubility data
- [ ] Salt forms documented
- [ ] 2D structure image embedded

**Section 3 (Mechanism)**
- [ ] FDA label MOA quoted verbatim (if approved) OR literature MOA
- [ ] Primary mechanism in 2-3 sentences
- [ ] At least 1 target with UniProt ID, potency, assay count
- [ ] Target selectivity addressed

**Section 4 (ADMET)**
- [ ] All 5 subsections present (A, D, M, E, T)
- [ ] Each subsection has at least 2 endpoints (predicted OR label PK)
- [ ] If ADMET-AI failed, fallback to label documented

**Section 5 (Clinical)**
- [ ] Development status clearly stated
- [ ] Phase/status counts in table format (not just a trial list)
- [ ] Indication breakdown by count
- [ ] Key efficacy data with trial references

**Section 6 (Safety)**
- [ ] Top 5 adverse events with frequencies
- [ ] FAERS seriousness breakdown with date window
- [ ] FAERS limitations paragraph present
- [ ] Black box warnings stated (or "None")
- [ ] At least 3 drug-drug interactions with mechanism
- [ ] Dose modification triggers (renal/hepatic/CYP)

**Section 7 (PGx)**
- [ ] Pharmacogenes listed (or "None identified")
- [ ] CPIC/DPWG guideline status
- [ ] If PharmGKB failed, fallback documented

**Section 10 (Conclusions)**
- [ ] 5-criterion scorecard (efficacy, safety, PK, target, competition)
- [ ] 3+ key strengths
- [ ] 3+ key concerns
- [ ] 2+ research gaps

---

## Known Gotchas

**ChEMBL targets**: Do NOT call `ChEMBL_get_molecule_targets` — it returns irrelevant entries. Always derive targets from `ChEMBL_search_activities`, then look up each unique `target_chembl_id` with `ChEMBL_get_target`.

**ID type errors**: Many tools require string inputs but IDs returned by other tools may be integers. Always convert: `str(chembl_id)`, `str(nct_id)`, `str(pmid)` before passing to any tool. Validation errors will occur silently if you skip this.

**ADMET-AI SMILES**: ADMET-AI tools require a valid SMILES string in a list (`smiles=["CCO"]`). If the SMILES is invalid (salts, radicals, unusual notation), the tool will fail. Switch to label PK sections as fallback immediately — do not retry with modified SMILES unless you are certain of the correction.

**PharmGKB availability**: PharmGKB has intermittent API timeouts. Always have the DailyMed PGx section fallback ready. Document the failure in Section 11 when using fallback.

**Clinical trial phase counts**: `search_clinical_trials` returns individual trial records, not counts. You must compute phase/status counts from the result set. Do not state counts you did not compute — common mistake is to guess.

**Orange Book limitations**: Orange Book only covers US-approved drugs. For EMA/PMDA data, note explicitly: "International regulatory data not available via public API."

**DailyMed SPL full XML**: Special population data (pediatric, geriatric, pregnancy, lactation) may only appear in the full SPL XML accessible via `DailyMed_get_spl_by_setid`, not in named section queries. Use LOINC codes to locate them: 34076-0 (pediatric), 34082-8 (geriatric), 42228-7 (pregnancy), 34080-2 (nursing_mothers).

**FAERS drug name matching**: FAERS queries are case-sensitive and use the exact brand/generic name submitted in reports. Try both brand name and generic name if the first query returns very few reports.

**Bioavailability discrepancy**: ADMET-AI predictions and label-reported bioavailability often differ. When they conflict, always use the label value (T1: ★★★) over the prediction (T4: ☆☆☆). Document the discrepancy in Section 11.3.

**Empty `categories` field**: If the profile.yaml categories field is empty or nil, treat as "load all categories" rather than filtering to an empty set.

---

## Evidence Grading

| Tier | Symbol | Description |
|------|--------|-------------|
| T1 | ★★★ | Phase 3 RCT, meta-analysis, FDA approval, official label |
| T2 | ★★☆ | Phase 1/2 trial, large case series, PharmGKB annotation |
| T3 | ★☆☆ | In vivo animal, in vitro cellular, literature inference |
| T4 | ☆☆☆ | Computational prediction, ADMET-AI, speculation |

Use inline: `Metformin activates AMPK [★★★: FDA Label].`
Include per-section evidence quality summary: `**Evidence Quality**: Strong (156 Phase 3 trials)`

---

## Fallback Chains

| Primary Tool | Fallback | Use When |
|--------------|----------|----------|
| `PubChem_get_CID_by_compound_name` | `ChEMBL_search_compounds` | Name not in PubChem |
| `ChEMBL_get_molecule_targets` | **Use `ChEMBL_search_activities` instead** | Always — avoid this tool |
| `DailyMed_search_spls` | `PubChem_get_drug_label_info_by_CID` | DailyMed timeout |
| `ADMETAI_*` (any) | `DailyMed_get_spl_sections_by_setid` (clinical_pharmacology, pharmacokinetics) | Invalid SMILES or API error |
| `PharmGKB_search_drugs` | `DailyMed` pharmacogenomics section + `PubMed_search_articles` | PharmGKB unavailable |
| `PharmGKB_get_dosing_guidelines` | `DailyMed_get_spl_sections_by_setid` (pharmacogenomics) | PharmGKB API error |
| `FAERS_count_reactions_by_drug_event` | Document unavailable + use label adverse_reactions | API error |

---

## Common Use Cases

| User Request | Emphasis | Notes |
|-------------|----------|-------|
| "Tell me about metformin" | Full 11-section report | Emphasize FAERS, PGx, clinical data |
| "What do we know about ChEMBL123456?" | Preclinical data, mechanism, early trials | Safety sections may be sparse or N/A |
| "Safety concerns with drug Y?" | Deep-dive Sections 6+7; lighter on chemistry | Include FAERS + DDI + dose mods |
| "Evaluate this SMILES for drug-likeness" | Sections 2 and 4 | Other sections brief or N/A |
| "What trials are ongoing for drug Z?" | Heavy Section 5 with phase/status tables | Use `study_type="OBSERVATIONAL"` for RWE |

---

## When NOT to Use This Skill

- **Target research** → Use target-intelligence-gatherer skill
- **Disease research** → Use disease-research skill
- **Literature-only** → Use literature-deep-research skill
- **Single property lookup** → Call the tool directly
- **Structure similarity search** → Call `PubChem_search_compounds_by_similarity` directly

---

## Tool Quick Reference

| Tool | Purpose |
|------|---------|
| `PubChem_get_CID_by_compound_name` | Name → CID + SMILES |
| `PubChem_get_compound_properties_by_CID` | MW, formula, XLogP, TPSA, HBD, HBA |
| `PubChem_get_bioactivity_summary_by_CID` | Assay counts summary |
| `PubChem_get_drug_label_info_by_CID` | Drug label text from PubChem |
| `PubChem_search_compounds_by_similarity` | Structural similarity search |
| `ChEMBL_search_compounds` | Name/structure → ChEMBL ID |
| `ChEMBL_search_activities` | Bioactivity records for a molecule |
| `ChEMBL_get_target` | Target name + UniProt for a ChEMBL target ID |
| `DGIdb_get_drug_info` | Drug-gene interaction database |
| `ADMETAI_predict_physicochemical_properties` | MW, logP, Lipinski, QED |
| `ADMETAI_predict_solubility_lipophilicity_hydration` | Solubility, lipophilicity |
| `ADMETAI_predict_bioavailability` | Oral BA, HIA, Caco-2, P-gp |
| `ADMETAI_predict_BBB_penetrance` | Blood-brain barrier probability |
| `ADMETAI_predict_CYP_interactions` | CYP1A2/2C9/2C19/2D6/3A4 |
| `ADMETAI_predict_clearance_distribution` | Clearance, half-life, VDss, PPBR |
| `ADMETAI_predict_toxicity` | AMES, hERG, DILI, ClinTox, LD50 |
| `DailyMed_search_spls` | Drug name → SPL set_id |
| `DailyMed_get_spl_sections_by_setid` | Extract named sections from label |
| `DailyMed_get_spl_by_setid` | Full SPL XML |
| `DailyMed_parse_clinical_pharmacology` | Structured PK parameters |
| `DailyMed_parse_adverse_reactions` | Structured AE table |
| `DailyMed_parse_dosing` | Structured dose tables |
| `DailyMed_parse_drug_interactions` | Structured DDI table |
| `search_clinical_trials` | ClinicalTrials.gov search |
| `get_clinical_trial_conditions_and_interventions` | Detailed trial conditions |
| `extract_clinical_trial_outcomes` | Primary outcomes + efficacy data |
| `extract_clinical_trial_adverse_events` | Trial-reported AEs |
| `FAERS_count_reactions_by_drug_event` | Top post-marketing AEs |
| `FAERS_count_seriousness_by_drug_event` | Serious vs non-serious ratio |
| `FAERS_count_outcomes_by_drug_event` | Outcome distribution |
| `FAERS_count_death_related_by_drug` | Fatal outcome count |
| `FAERS_count_patient_age_distribution` | Reports by age group |
| `FAERS_calculate_disproportionality` | Signal detection (ROR, PRR, IC) |
| `FAERS_stratify_by_demographics` | Age/sex/country breakdown |
| `FAERS_filter_serious_events` | Deaths/hospitalizations only |
| `PharmGKB_search_drugs` | Drug name → PharmGKB ID |
| `PharmGKB_get_drug_details` | Drug cross-refs + related genes |
| `PharmGKB_get_clinical_annotations` | Variant-drug associations |
| `PharmGKB_get_dosing_guidelines` | CPIC/DPWG guideline text |
| `FDA_OrangeBook_search_drug` | Brand/generic → application number |
| `FDA_OrangeBook_get_approval_history` | Approval dates + supplements |
| `FDA_OrangeBook_get_exclusivity` | NCE/orphan/pediatric exclusivity |
| `FDA_OrangeBook_get_patent_info` | Patent numbers + claims |
| `FDA_OrangeBook_check_generic_availability` | Generic count + TE codes |
| `fda_pharmacogenomic_biomarkers` | FDA-required companion diagnostics |
| `PubMed_search_articles` | Literature search |
| `EuropePMC_search_articles` | Europe PMC literature search |

For detailed parameter schemas and output format examples, see [references/tools.md](references/tools.md).
