# Tool Parameter Reference — Adverse Event Detection

Detailed parameter tables for all tools used in the adverse event detection workflow.
See `SKILL.md` for the workflow guide.

---

## FAERS Count Tools (OpenFDA-based)

| Tool | Key Parameters | Returns |
|------|---------------|---------|
| `FAERS_count_reactions_by_drug_event` | `medicinalproduct` (REQUIRED), `patientsex`, `patientagegroup`, `occurcountry` | `[{term, count}]` |
| `FAERS_count_seriousness_by_drug_event` | `medicinalproduct` (REQUIRED), `patientsex`, `patientagegroup`, `occurcountry` | `[{term: "Serious"/"Non-serious", count}]` |
| `FAERS_count_outcomes_by_drug_event` | `medicinalproduct` (REQUIRED), `patientsex`, `patientagegroup`, `occurcountry` | `[{term: "Fatal"/"Recovered"/..., count}]` |
| `FAERS_count_patient_age_distribution` | `medicinalproduct` (REQUIRED) | `[{term: "Elderly"/"Adult"/..., count}]` |
| `FAERS_count_death_related_by_drug` | `medicinalproduct` (REQUIRED) | `[{term: "alive"/"death", count}]` |
| `FAERS_count_reportercountry_by_drug_event` | `medicinalproduct` (REQUIRED), `patientsex`, `patientagegroup`, `serious` | `[{term: "US"/"GB"/..., count}]` |

## FAERS Search Tools

| Tool | Key Parameters | Returns |
|------|---------------|---------|
| `FAERS_search_adverse_event_reports` | `medicinalproduct`, `limit` (max 100), `skip` | Individual case reports with patient/drug/reaction data |
| `FAERS_search_reports_by_drug_and_reaction` | `medicinalproduct` (REQUIRED), `reactionmeddrapt` (REQUIRED), `limit`, `skip`, `patientsex`, `serious` | Reports filtered by specific reaction |
| `FAERS_search_serious_reports_by_drug` | `medicinalproduct` (REQUIRED), `seriousnessdeath`, `seriousnesshospitalization`, `seriousnesslifethreatening`, `seriousnessdisabling`, `limit` | Serious event reports |

## FAERS Analytics Tools (operation-based)

| Tool | Key Parameters | Returns |
|------|---------------|---------|
| `FAERS_calculate_disproportionality` | `operation`="calculate_disproportionality", `drug_name` (REQUIRED), `adverse_event` (REQUIRED) | PRR, ROR, IC with 95% CI and signal detection verdict |
| `FAERS_analyze_temporal_trends` | `operation`="analyze_temporal_trends", `drug_name` (REQUIRED), `adverse_event` (optional) | Yearly counts and trend direction |
| `FAERS_compare_drugs` | `operation`="compare_drugs", `drug1` (REQUIRED), `drug2` (REQUIRED), `adverse_event` (REQUIRED) | PRR/ROR/IC for both drugs side-by-side |
| `FAERS_filter_serious_events` | `operation`="filter_serious_events", `drug_name` (REQUIRED), `seriousness_type` (death/hospitalization/disability/life_threatening/all) | Top serious reactions with counts |
| `FAERS_stratify_by_demographics` | `operation`="stratify_by_demographics", `drug_name` (REQUIRED), `adverse_event` (REQUIRED), `stratify_by` (sex/age/country) | Stratified counts and percentages. Sex codes: 0=Unknown, 1=Male, 2=Female |
| `FAERS_rollup_meddra_hierarchy` | `operation`="rollup_meddra_hierarchy", `drug_name` (REQUIRED) | Top 50 MedDRA preferred terms with counts |

## FAERS Aggregate Tools (multi-drug)

| Tool | Key Parameters | Returns |
|------|---------------|---------|
| `FAERS_count_additive_adverse_reactions` | `medicinalproducts` (REQUIRED, array), `patientsex`, `patientagegroup`, `occurcountry`, `serious`, `seriousnessdeath` | Aggregated AE counts across multiple drugs |
| `FAERS_count_additive_seriousness_classification` | `medicinalproducts` (REQUIRED, array), `patientsex`, `patientagegroup`, `occurcountry` | Aggregated seriousness across multiple drugs |
| `FAERS_count_additive_reaction_outcomes` | `medicinalproducts` (REQUIRED, array) | Aggregated outcomes across multiple drugs |

## FDA Label Tools

| Tool | Key Parameters | Returns |
|------|---------------|---------|
| `FDA_get_boxed_warning_info_by_drug_name` | `drug_name` | `{error: {code: "NOT_FOUND"}}` if no boxed warning exists; else `{meta: {total}, results: [{boxed_warning: [...]}]}` |
| `FDA_get_contraindications_by_drug_name` | `drug_name` | `{meta: {total}, results: [{contraindications: [...]}]}` |
| `FDA_get_adverse_reactions_by_drug_name` | `drug_name` | `{meta: {total}, results: [{adverse_reactions: [...]}]}` |
| `FDA_get_warnings_by_drug_name` | `drug_name` | `{meta: {total}, results: [{warnings: [...]}]}` |
| `FDA_get_drug_interactions_by_drug_name` | `drug_name` | `{meta: {total}, results: [{drug_interactions: [...]}]}` |
| `FDA_get_pharmacogenomics_info_by_drug_name` | `drug_name` | PGx section from label |
| `FDA_get_pregnancy_or_breastfeeding_info_by_drug_name` | `drug_name` | Pregnancy/lactation text |
| `FDA_get_geriatric_use_info_by_drug_name` | `drug_name` | Geriatric use section |
| `FDA_get_pediatric_use_info_by_drug_name` | `drug_name` | Pediatric use section |

## OpenTargets Tools

| Tool | Key Parameters | Returns |
|------|---------------|---------|
| `OpenTargets_get_drug_chembId_by_generic_name` | `drugName` | `{data: {search: {hits: [{id, name, description}]}}}` |
| `OpenTargets_get_drug_adverse_events_by_chemblId` | `chemblId` | `{data: {drug: {adverseEvents: {count, criticalValue, rows: [{name, meddraCode, count, logLR}]}}}}` |
| `OpenTargets_get_drug_blackbox_status_by_chembl_ID` | `chemblId` | `{data: {drug: {name, hasBeenWithdrawn, blackBoxWarning}}}` |
| `OpenTargets_get_drug_warnings_by_chemblId` | `chemblId` | Drug withdrawal/safety warnings (may be empty) |
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | `chemblId` | `{data: {drug: {mechanismsOfAction: {rows: [{mechanismOfAction, actionType, targetName, targets: [{id, approvedSymbol}]}]}}}}` |
| `OpenTargets_get_drug_indications_by_chemblId` | `chemblId` | Approved and investigational indications with max phase |
| `OpenTargets_get_target_safety_profile_by_ensemblID` | `ensemblId` | `{data: {target: {safetyLiabilities: [{event, eventId, effects, studies, datasource}]}}}` |

## DrugBank Tools

| Tool | Key Parameters | Returns |
|------|---------------|---------|
| `drugbank_get_safety_by_drug_name_or_drugbank_id` | `query`, `case_sensitive` (bool), `exact_match` (bool), `limit` | Toxicity, food interactions |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | Drug targets list |
| `drugbank_get_drug_interactions_by_drug_name_or_id` | `query`, `case_sensitive`, `exact_match`, `limit` | DDIs |
| `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | Pharmacology data |

## PharmGKB & PGx Tools

| Tool | Key Parameters | Returns |
|------|---------------|---------|
| `PharmGKB_search_drugs` | `query` | `{status: "success", data: [{id, name, smiles}]}` |
| `PharmGKB_get_drug_details` | `drug_id` (e.g., "PA448500") | Detailed drug info |
| `PharmGKB_get_dosing_guidelines` | `guideline_id`, `gene` (both optional) | Dosing guidelines |
| `PharmGKB_get_clinical_annotations` | `annotation_id`, `gene_id` (both optional) | Clinical annotations |
| `fda_pharmacogenomic_biomarkers` | `drug_name`, `biomarker`, `limit` | `{count, results: [...]}` — may return empty for some drugs |

## ADMETAI Tools

| Tool | Key Parameters | Returns |
|------|---------------|---------|
| `ADMETAI_predict_toxicity` | `smiles` (REQUIRED, array of strings) | Hepatotoxicity, cardiotoxicity, and other toxicity predictions |
| `ADMETAI_predict_CYP_interactions` | `smiles` (REQUIRED, array) | CYP inhibition/substrate predictions |

## Literature Tools

| Tool | Key Parameters | Returns |
|------|---------------|---------|
| `PubMed_search_articles` | `query`, `limit` | List of article dicts with pmid, title, authors, journal, pub_date, doi |
| `openalex_search_works` | `query`, `limit` | Works with citation counts |
| `EuropePMC_search_articles` | `query`, `source` ("PPR" for preprints), `pageSize` | Articles including preprints |
| `search_clinical_trials` | `query_term` (REQUIRED), `condition`, `intervention`, `pageSize` | Clinical trial records |

## DailyMed Tools

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `DailyMed_parse_drug_interactions` | `drug_name` | Drug interaction section from DailyMed labels |

---

## Response Shape Notes

**FAERS `calculate_disproportionality` full response shape:**
```json
{
  "status": "success",
  "drug_name": "ATORVASTATIN",
  "adverse_event": "Rhabdomyolysis",
  "contingency_table": {
    "a_drug_and_event": 2226,
    "b_drug_no_event": 241655,
    "c_no_drug_event": 37658,
    "d_no_drug_no_event": 19725450
  },
  "metrics": {
    "ROR": {"value": 4.825, "ci_95_lower": 4.622, "ci_95_upper": 5.037},
    "PRR": {"value": 4.79, "ci_95_lower": 4.59, "ci_95_upper": 4.998},
    "IC":  {"value": 2.194, "ci_95_lower": 2.136, "ci_95_upper": 2.252}
  },
  "signal_detection": {
    "signal_detected": true,
    "signal_strength": "Strong signal",
    "criteria": "ROR lower CI > 1.0 and case count >= 3"
  }
}
```

**FAERS `compare_drugs` full response shape:**
```json
{
  "status": "success",
  "adverse_event": "Rhabdomyolysis",
  "drug1": {
    "name": "ATORVASTATIN",
    "metrics": {"PRR": {"value": 4.79, "ci_95_lower": 4.59, "ci_95_upper": 4.998}, "ROR": {...}, "IC": {...}},
    "signal_detection": {"signal_detected": true, "signal_strength": "Strong signal"}
  },
  "drug2": {"name": "SIMVASTATIN", "metrics": {...}, "signal_detection": {...}},
  "comparison": "SIMVASTATIN shows stronger signal than ATORVASTATIN"
}
```
