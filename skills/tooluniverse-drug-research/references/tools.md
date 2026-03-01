# Drug Research: Detailed Tool Reference

This file contains the verbose parameter details and output format examples moved from SKILL.md.
For the workflow guide, see [SKILL.md](../SKILL.md).

---

## Tool Parameter Details

### Compound Identity

| Tool | Key Parameters | Key Output Fields |
|------|---------------|-------------------|
| `PubChem_get_CID_by_compound_name` | `compound_name` (str) | CID, canonical SMILES, molecular formula |
| `PubChem_get_CID_by_SMILES` | `smiles` (str) | CID |
| `PubChem_get_compound_properties_by_CID` | `cid` (str) | MW, formula, XLogP, TPSA, HBD, HBA, rotatable bonds |
| `PubChem_get_bioactivity_summary_by_CID` | `cid` (str) | Assay summary, active/inactive counts |
| `PubChem_get_drug_label_info_by_CID` | `cid` (str) | Label text |
| `PubChem_search_compounds_by_similarity` | `smiles` (str), `threshold` (float) | List of similar CIDs |
| `ChEMBL_search_compounds` | `query` (str) | ChEMBL ID, pref_name, SMILES |
| `ChEMBL_search_activities` | `molecule_chembl_id` (str), `limit` (int) | activity records: target_chembl_id, pChEMBL, standard_type |
| `ChEMBL_get_target` | `target_chembl_id` (str) | target name, UniProt ID, organism |

**Critical**: All ChEMBL IDs must be passed as strings. Convert integers before the call.

### DailyMed

| Tool | Key Parameters | Key Output |
|------|---------------|------------|
| `DailyMed_search_spls` | `drug_name` (str) | set_id, NDC codes |
| `DailyMed_get_spl_sections_by_setid` | `setid` (str), `sections` (list[str]) | Section text keyed by section name |
| `DailyMed_get_spl_by_setid` | `setid` (str) | Full SPL XML |
| `DailyMed_parse_clinical_pharmacology` | `setid` (str) | Tmax, Cmax, AUC, half-life |
| `DailyMed_parse_adverse_reactions` | `setid` (str) | Structured AE table |
| `DailyMed_parse_dosing` | `setid` (str) | Dose tables |
| `DailyMed_parse_drug_interactions` | `setid` (str) | Interaction tables |

**DailyMed section names** (pass in `sections` list):
- Identity/Chemistry: `mechanism_of_action`, `pharmacodynamics`, `chemistry`, `description`, `inactive_ingredients`
- PK: `clinical_pharmacology`, `pharmacokinetics`, `drug_interactions`
- Safety: `warnings_and_cautions`, `adverse_reactions`, `dosage_and_administration`
- PGx/Clinical: `pharmacogenomics`, `clinical_studies`, `indications_and_usage`
- Special populations via full SPL (LOINC codes): `34076-0` (pediatric), `34082-8` (geriatric), `42228-7` (pregnancy), `34080-2` (nursing_mothers)

### ADMET-AI

All ADMET-AI tools accept `smiles` as a list of SMILES strings.

| Tool | Key Output Fields |
|------|-------------------|
| `ADMETAI_predict_physicochemical_properties` | MW, logP, HBD, HBA, Lipinski, QED, stereo_centers, TPSA |
| `ADMETAI_predict_solubility_lipophilicity_hydration` | Solubility_AqSolDB, Lipophilicity_AstraZeneca |
| `ADMETAI_predict_bioavailability` | Bioavailability_Ma, HIA_Hou, PAMPA_NCATS, Caco2_Wang, Pgp_Broccatelli |
| `ADMETAI_predict_BBB_penetrance` | BBB_Martins (0-1 probability) |
| `ADMETAI_predict_CYP_interactions` | CYP1A2, CYP2C9, CYP2C19, CYP2D6, CYP3A4 (inhibitor/substrate) |
| `ADMETAI_predict_clearance_distribution` | Clearance, Half_Life_Obach, VDss_Lombardo, PPBR_AZ |
| `ADMETAI_predict_toxicity` | AMES, hERG, DILI, ClinTox, LD50_Zhu, Carcinogens |

### FAERS

| Tool | Key Parameters | Key Output |
|------|---------------|------------|
| `FAERS_count_reactions_by_drug_event` | `medicinalproduct` (str) | Top MedDRA PTs with counts |
| `FAERS_count_seriousness_by_drug_event` | `medicinalproduct` (str) | Serious vs non-serious counts |
| `FAERS_count_outcomes_by_drug_event` | `medicinalproduct` (str) | Recovered, recovering, fatal, unresolved |
| `FAERS_count_death_related_by_drug` | `medicinalproduct` (str) | Fatal outcome count |
| `FAERS_count_patient_age_distribution` | `medicinalproduct` (str) | Reports by age group |
| `FAERS_calculate_disproportionality` | `medicinalproduct`, `reaction` | ROR, PRR, IC signal metrics |
| `FAERS_stratify_by_demographics` | `medicinalproduct` | By age/sex/country |
| `FAERS_filter_serious_events` | `medicinalproduct` | Deaths, hospitalizations only |

### Clinical Trials

| Tool | Key Parameters | Key Output |
|------|---------------|------------|
| `search_clinical_trials` | `intervention` (str), `pageSize` (int), `study_type` (str) | NCT IDs, phases, statuses, conditions |
| `get_clinical_trial_conditions_and_interventions` | `nct_ids` (list[str]) | Detailed conditions, arm groups |
| `extract_clinical_trial_outcomes` | `nct_ids` (list[str]) | Primary outcomes, efficacy measures |
| `extract_clinical_trial_adverse_events` | `nct_ids` (list[str]) | Serious AEs, common AEs |

### PharmGKB

| Tool | Key Parameters | Key Output |
|------|---------------|------------|
| `PharmGKB_search_drugs` | `query` (str) | PharmGKB drug ID (PA...) |
| `PharmGKB_get_drug_details` | `drug_id` (str) | Cross-references, related genes |
| `PharmGKB_get_clinical_annotations` | `gene_id` or `drug_id` (str) | Variant-drug associations, evidence levels |
| `PharmGKB_get_dosing_guidelines` | `gene` (str) | CPIC/DPWG guideline recommendations |

### FDA Orange Book

| Tool | Key Parameters | Key Output |
|------|---------------|------------|
| `FDA_OrangeBook_search_drug` | `brand_name` (str) | Application number, approval dates |
| `FDA_OrangeBook_get_approval_history` | `appl_no` (str) | Original approval, supplements, label changes |
| `FDA_OrangeBook_get_exclusivity` | `brand_name` (str) | Exclusivity types (NCE, Pediatric, Orphan), expiration dates |
| `FDA_OrangeBook_get_patent_info` | `brand_name` (str) | Patent numbers, substance/formulation claims |
| `FDA_OrangeBook_check_generic_availability` | `brand_name` (str) | Generic entries, TE codes, first generic date |

### DGIdb

| Tool | Key Parameters | Key Output |
|------|---------------|------------|
| `DGIdb_get_drug_info` | `drugs` (list[str]) | Target genes, interaction types, sources |

### Literature

| Tool | Key Parameters | Key Output |
|------|---------------|------------|
| `PubMed_search_articles` | `query` (str), `max_results` (int) | PMIDs, titles, abstracts |
| `EuropePMC_search_articles` | `query` (str), `max_results` (int) | PMIDs, titles |

### FDA Pharmacogenomics

| Tool | Key Parameters | Key Output |
|------|---------------|------------|
| `fda_pharmacogenomic_biomarkers` | `drug_name` (str) | FDA-required biomarker testing, approved companion diagnostics |

---

## Section Output Format Examples

### Section 2.1 — Physicochemical Profile Table

```markdown
| Property | Value | Drug-Likeness | Source |
|----------|-------|---------------|--------|
| Molecular Weight | 129.16 g/mol | ✓ (< 500) | PubChem |
| LogP | -2.64 | ✓ (< 5) | ADMET-AI |
| TPSA | 91.5 Å² | ✓ (< 140) | PubChem |
| H-Bond Donors | 2 | ✓ (≤ 5) | PubChem |
| H-Bond Acceptors | 5 | ✓ (< 10) | PubChem |
| Rotatable Bonds | 2 | ✓ (< 10) | PubChem |
| pKa | 12.4 (basic) | - | DailyMed Label |
| Solubility | 300 mg/mL (water) | High | DailyMed Label |

**Lipinski Rule of Five**: ✓ PASS (0 violations)
**QED Score**: 0.74 (Good drug-likeness)
```

### Section 3.2 — Target Table

```markdown
| Target | UniProt | Type | Potency | Assays | Evidence | Source |
|--------|---------|------|---------|--------|----------|--------|
| PRKAA1 (AMPK α1) | Q13131 | Activator | EC50 ~10 µM | 12 | ★★★ | ChEMBL |
| PRKAA2 (AMPK α2) | P54646 | Activator | EC50 ~15 µM | 8 | ★★★ | ChEMBL |
| SLC22A1 (OCT1) | O15245 | Substrate | Km ~1.5 mM | 5 | ★★☆ | DGIdb |
```

### Section 4.1 — ADMET Absorption Table

```markdown
| Endpoint | Prediction | Interpretation |
|----------|------------|----------------|
| Oral Bioavailability | 0.72 | Good (>50%) |
| Human Intestinal Absorption | 0.89 | High |
| Caco-2 Permeability | -5.2 (log cm/s) | Moderate |
| PAMPA | 0.34 | Low-moderate |
| P-gp Substrate | 0.23 | Unlikely substrate |
```

### Section 5.2 — Clinical Trial Phase Count Table

```markdown
| Phase | Total | Completed | Recruiting | Terminated |
|-------|-------|-----------|------------|------------|
| Phase 4 | 89 | 72 | 12 | 5 |
| Phase 3 | 156 | 134 | 15 | 7 |
| Phase 2 | 203 | 178 | 18 | 7 |
| Phase 1 | 67 | 61 | 4 | 2 |
```

### Section 6.2 — FAERS Safety Block

```markdown
**Total FAERS Reports**: 45,234 (Date range: 2004Q1 - 2026Q1)

| Reaction (MedDRA PT) | Count | % of Reports |
|----------------------|-------|--------------|
| Diarrhoea | 8,234 | 18.2% |
| Nausea | 6,892 | 15.2% |
| Lactic acidosis | 3,456 | 7.6% |

**Data Limitations**: FAERS data represents voluntary reports. Serious events are more likely
to be reported (reporting bias). Reports do not establish causality. Many reports lack outcome
information. This data supplements but does not replace label safety information.
```

### Section 8.3 — Patents & Exclusivity Table

```markdown
| Type | Code | Expiration Date | Protections |
|------|------|-----------------|-------------|
| New Chemical Entity (NCE) | N | 2028 | Blocks ANDA filing for 5 years |
| Orphan Drug | O | 2030 | Market exclusivity for indication |
| Pediatric | P | 2030 | +6 months extension |
```

### Section 10.1 — Drug Profile Scorecard

```markdown
| Criterion | Score (1-5) | Rationale |
|-----------|-------------|-----------|
| Efficacy Evidence | 5 | Multiple Phase 3 trials |
| Safety Profile | 4 | Well-tolerated; rare serious AE |
| PK/ADMET | 4 | Good bioavailability; renal elimination |
| Target Validation | 4 | Mechanism well-established |
| Competitive Position | 3 | First-line but many alternatives |
| Overall | 4.0 | Strong drug profile |

Interpretation: 5 = Excellent, 4 = Good, 3 = Moderate, 2 = Concerning, 1 = Poor
```

---

## Report Completeness Audit Template

Add to Section 11 (Data Sources & Methodology):

```markdown
## Report Completeness Audit

**Overall Completeness**: 85% (17/20 minimum requirements met)

### Missing Data Items
| Section | Missing Item | Recommended Action |
|---------|--------------|-------------------|
| 2 | Salt forms | Call DailyMed_get_spl_sections_by_setid (chemistry section) |
| 5 | Phase count breakdown | Compute counts from search_clinical_trials results |

### Tool Failures Encountered
| Tool | Error | Fallback Used |
|------|-------|---------------|
| PharmGKB_search_drugs | API timeout | DailyMed label PGx sections [done] |
| ADMETAI_predict_toxicity | Invalid SMILES | FDA label warnings section [done] |

### Cross-Source Validation
| Property | PubChem | ChEMBL | DailyMed | Agreement |
|----------|---------|--------|----------|-----------|
| Molecular Weight | 378.88 | 378.88 | 378.88 | Exact match |
| Bioavailability | Predicted: 85% | N/A | ~60% (fed) | Discrepancy — use label (T1) |
```
