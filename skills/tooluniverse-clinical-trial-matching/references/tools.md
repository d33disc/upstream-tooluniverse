# Clinical Trial Matching — Detailed Tool Reference

Full parameter schemas and response structures for every tool used by the
`tooluniverse-clinical-trial-matching` skill. For the workflow guide, see
`../SKILL.md`.

---

## Clinical Trial Tools

### `search_clinical_trials` (primary search)

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query_term` | str | YES | Required even for disease-only searches |
| `condition` | str | no | Disease/condition filter |
| `intervention` | str | no | Drug/intervention filter |
| `pageSize` | int | no | Default 10; use 20-30 for broad searches |
| `pageToken` | str | no | Pagination token from previous response |

**Response**:
```
{
  studies: [
    {
      "NCT ID": "NCT...",
      brief_title: str,
      brief_summary: str,
      overall_status: str,
      condition: [str],
      phase: [str]
    }
  ],
  nextPageToken: str,
  total_count: int
}
```
Note: if no studies found, may return a string message rather than the above dict.

---

### `clinical_trials_search` (alternative search)

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `action` | str | YES | Must be exactly `"search_studies"` |
| `condition` | str | no | Disease filter |
| `intervention` | str | no | Intervention filter |
| `limit` | int | no | Max results |

**Response**:
```
{
  total_count: int,
  studies: [
    {nctId: str, title: str, status: str, conditions: [str]}
  ]
}
```

---

### `clinical_trials_get_details`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `action` | str | YES | Must be exactly `"get_study_details"` |
| `nct_id` | str | YES | Single NCT ID |

**Response**: Full study object including `{nctId, title, summary, eligibility: {eligibilityCriteria}, ...}`

---

### `get_clinical_trial_eligibility_criteria`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `nct_ids` | array | YES | Array of NCT ID strings (batch up to 10) |
| `eligibility_criteria` | str | YES | Use `"all"` |

**Response**: `[{NCT ID: str, eligibility_criteria: "Inclusion Criteria:\n...\nExclusion Criteria:\n..."}]`

---

### `get_clinical_trial_locations`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `nct_ids` | array | YES | Array of NCT ID strings |
| `location` | str | YES | Use `"all"` |

**Response**: `[{NCT ID: str, locations: [{facility: str, city: str, state: str, country: str}]}]`

---

### `get_clinical_trial_descriptions`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `nct_ids` | array | YES | Array of NCT ID strings |
| `description_type` | str | YES | `"brief"` or `"full"` |

**Response**: `[{NCT ID, brief_title, official_title, brief_summary, detailed_description}]`

---

### `get_clinical_trial_status_and_dates`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `nct_ids` | array | YES | Array of NCT ID strings |
| `status_and_date` | str | YES | Use `"all"` |

**Response**: `[{NCT ID, overall_status, start_date, primary_completion_date, completion_date}]`

---

### `get_clinical_trial_conditions_and_interventions`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `nct_ids` | array | YES | Array of NCT ID strings |
| `condition_and_intervention` | str | YES | Use `"all"` |

**Response**:
```
[{
  NCT ID: str,
  condition: [str],
  arm_groups: [{label, type, description, interventionNames}],
  interventions: [{type, name, description}]
}]
```

---

### `get_clinical_trial_outcome_measures`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `nct_ids` | array | YES | Array of NCT ID strings |
| `outcome_measures` | str | no | `"primary"`, `"secondary"`, or `"all"` |

**Response**: `[{NCT ID, primary_outcomes: [...], secondary_outcomes: [...]}]`

---

### `extract_clinical_trial_outcomes` / `extract_clinical_trial_adverse_events`

Both accept `nct_ids` (array, required) and return result data from completed trials.

---

## Gene and Disease Resolution Tools

### `MyGene_query_genes`

| Parameter | Type | Required |
|-----------|------|----------|
| `query` | str | YES |
| `species` | str | no (use `"human"`) |

**Response**: `{hits: [{symbol, entrezgene, ensembl: {gene}, name}]}`

Note: `ensembl` may be a dict `{gene: str}` or a list of dicts. Handle both cases.

---

### `ols_search_efo_terms`

| Parameter | Type | Required |
|-----------|------|----------|
| `query` | str | YES |
| `limit` | int | no |

**Response**: `{data: {terms: [{iri, obo_id, short_form, label, description}]}}`

---

### `ols_get_efo_term` / `ols_get_efo_term_children`

Both accept `term_id` (str, EFO short form). Return term metadata or child terms.

---

## OpenTargets Tools

### `OpenTargets_get_disease_id_description_by_name`

| Parameter | Type | Required |
|-----------|------|----------|
| `diseaseName` | str | YES |

**Response**: `{data: {search: {hits: [{id: "EFO_...", name, description}]}}}`

---

### `OpenTargets_get_target_id_description_by_name`

| Parameter | Type | Required |
|-----------|------|----------|
| `targetName` | str | YES |

**Response**: `{data: {search: {hits: [{id: "ENSG...", name, description}]}}}`

---

### `OpenTargets_get_drug_id_description_by_name`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `drugName` | str | YES | Use common drug name, NOT `genericName` |

**Response**: `{data: {search: {hits: [{id: "CHEMBL...", name, description}]}}}`

---

### `OpenTargets_get_drug_mechanisms_of_action_by_chemblId`

| Parameter | Type | Required |
|-----------|------|----------|
| `chemblId` | str | YES |

**Response**:
```
{data: {drug: {id, name, mechanismsOfAction: {rows: [
  {mechanismOfAction, actionType, targetName, targets: [{id, approvedSymbol}]}
]}}}}
```

---

### `OpenTargets_get_associated_drugs_by_target_ensemblID`

| Parameter | Type | Required |
|-----------|------|----------|
| `ensemblId` | str | YES |
| `size` | int | no |

**Response**:
```
{data: {target: {id, approvedSymbol, knownDrugs: {count, rows: [
  {drug: {id, name, isApproved}, phase, mechanismOfAction, disease: {id, name}}
]}}}}
```

---

### `OpenTargets_get_associated_drugs_by_disease_efoId`

| Parameter | Type | Required |
|-----------|------|----------|
| `efoId` | str | YES |
| `size` | int | no |

**Response**: `{data: {disease: {knownDrugs: {count, rows: [...same as above...]}}}}`

---

### `OpenTargets_get_approved_indications_by_drug_chemblId`

| Parameter | Type | Required |
|-----------|------|----------|
| `chemblId` | str | YES |

**Response**: `{data: {drug: {approvedIndications: [efoIds]}}}`

---

### `OpenTargets_target_disease_evidence`

| Parameter | Type | Required |
|-----------|------|----------|
| `ensemblId` | str | YES |
| `efoId` | str | YES |
| `size` | int | no |

Returns target-disease association evidence rows.

---

## CIViC Tools

**IMPORTANT**: `civic_search_variants` and `civic_search_evidence_items` do NOT filter by `query`. They return results alphabetically. Use `civic_get_variants_by_gene` for gene-specific lookup.

### `civic_get_variants_by_gene`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_id` | int | YES | CIViC gene ID (integer, NOT gene symbol) |
| `limit` | int | no | Max 100 per call |

**Response**: `{data: {gene: {variants: {nodes: [{id, name}]}}}}`

**Known CIViC Gene IDs**:

| Gene | ID | Gene | ID |
|------|----|------|----|
| ALK | 1 | MET | 52 |
| ABL1 | 4 | PIK3CA | 37 |
| BRAF | 5 | ROS1 | 118 |
| EGFR | 19 | RET | 122 |
| ERBB2 | 20 | NTRK1 | 197 |
| KRAS | 30 | NTRK2 | 560 |
| TP53 | 45 | NTRK3 | 561 |
| BRCA1 | 2370 | BRCA2 | 2371 |

---

### `civic_get_variant`

| Parameter | Type | Required |
|-----------|------|----------|
| `variant_id` | int | YES |

**Response**: `{data: {variant: {id, name, ...}}}`

---

### `civic_search_therapies` / `civic_search_diseases`

Both accept `query` (str) and `limit` (int). Results are alphabetical — filter client-side.

---

## FDA Tools

### `fda_pharmacogenomic_biomarkers`

No parameters required. Returns the full FDA pharmacogenomic biomarker table.

**Response**: `{count, shown, results: [{Drug, TherapeuticArea, Biomarker, LabelingSection}]}`

Use `limit=1000` if a limit parameter is available to retrieve all entries.

---

### `FDA_get_indications_by_drug_name`

| Parameter | Type | Required |
|-----------|------|----------|
| `drug_name` | str | YES |
| `limit` | int | no |

**Response**: List of FDA label records with `indications_and_usage` text field.

---

### `FDA_get_mechanism_of_action_by_drug_name` / `FDA_get_clinical_studies_info_by_drug_name` / `FDA_get_adverse_reactions_by_drug_name`

All accept `drug_name` (str, required) and `limit` (int, optional). Return FDA label text sections.

---

## DrugBank Tools

**IMPORTANT**: All four parameters are REQUIRED for both DrugBank tools.

### `drugbank_get_targets_by_drug_name_or_drugbank_id`

| Parameter | Type | Required |
|-----------|------|----------|
| `query` | str | YES |
| `case_sensitive` | bool | YES |
| `exact_match` | bool | YES |
| `limit` | int | YES |

**Response**: `{results: [{drug_name, drugbank_id, targets: [{name, organism, actions}]}]}`

---

### `drugbank_get_indications_by_drug_name_or_drugbank_id`

Same four required parameters. Returns drug indication records.

---

## ChEMBL Tools

### `ChEMBL_search_drugs`

| Parameter | Type | Required |
|-----------|------|----------|
| `query` | str | YES |
| `limit` | int | no |

**Response**: `{status, data: {drugs: [...]}}`

---

### `ChEMBL_get_drug_mechanisms`

| Parameter | Type | Required |
|-----------|------|----------|
| `drug_chembl_id__exact` | str | YES |

Returns drug mechanism records.

---

## Literature Tools

### `PubMed_search_articles`

| Parameter | Type | Required |
|-----------|------|----------|
| `query` | str | YES |
| `max_results` | int | no |

**Response**: `[{pmid, title, abstract, authors, journal, pub_date}]`

---

### `openalex_literature_search`

| Parameter | Type | Required |
|-----------|------|----------|
| `query` | str | YES |
| `limit` | int | no |

---

## PharmGKB Tools

### `PharmGKB_search_genes` / `PharmGKB_get_clinical_annotations`

Both accept `query` (str). Return pharmacogenomics gene data and clinical annotations respectively.

---

## Response Structure Quick Reference

```
search_clinical_trials:
  {studies: [{"NCT ID", brief_title, brief_summary, overall_status, condition[], phase[]}],
   nextPageToken, total_count}

clinical_trials_search:
  {total_count, studies: [{nctId, title, status, conditions[]}]}

get_clinical_trial_eligibility_criteria:
  [{"NCT ID", eligibility_criteria: "Inclusion Criteria:\n...\nExclusion Criteria:\n..."}]

get_clinical_trial_locations:
  [{"NCT ID", locations: [{facility, city, state, country}]}]

get_clinical_trial_conditions_and_interventions:
  [{"NCT ID", condition[], arm_groups: [{label, type, description, interventionNames}],
    interventions: [{type, name, description}]}]

get_clinical_trial_status_and_dates:
  [{"NCT ID", overall_status, start_date, primary_completion_date, completion_date}]

OpenTargets_get_drug_mechanisms_of_action_by_chemblId:
  {data: {drug: {id, name, mechanismsOfAction: {rows: [
    {mechanismOfAction, actionType, targetName, targets: [{id, approvedSymbol}]}]}}}}

OpenTargets_get_associated_drugs_by_target_ensemblID:
  {data: {target: {id, approvedSymbol, knownDrugs: {count,
    rows: [{drug: {id, name, isApproved}, phase, mechanismOfAction, disease: {id, name}}]}}}}

fda_pharmacogenomic_biomarkers:
  {count, shown, results: [{Drug, TherapeuticArea, Biomarker, LabelingSection}]}

MyGene_query_genes:
  {hits: [{symbol, entrezgene, ensembl: {gene} or [{gene}], name}]}

PubMed_search_articles:
  [{pmid, title, abstract, authors, journal, pub_date}]
```
