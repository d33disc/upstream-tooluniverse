# Tool Parameter Reference — GWAS-to-Drug Discovery

Detailed parameter tables for all tools used in the GWAS-to-Drug Discovery skill.
Agents call tools via `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

---

## Disease ID Resolution

### `OpenTargets_get_dise_id_desc_by_name`

Resolve a free-text disease name to an EFO/MONDO ID required by Open Targets tools.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `diseaseName` | string | Yes | Free-text disease name (e.g., `"type 2 diabetes"`, `"Alzheimer disease"`) |

Returns: array of `{ id, name, description }`. Use the `id` from the top hit as the EFO ID.

Example: `diseaseName="type 2 diabetes"` → `MONDO_0005148`

---

### `OpenTargets_map_any_dise_id_to_all_othe_ids`

Convert any known disease ID (OMIM, UMLS, ICD-10, EFO, MONDO, MedDRA, etc.) to all cross-referenced IDs including EFO.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `inputId` | string | Yes | Any disease ID in any namespace (e.g., `"OMIM:604302"`, `"UMLS:C0003873"`, `"ICD10:M05"`, `"EFO_0000685"`) |

Returns: mapped EFO ID and all cross-referenced external IDs.

---

## GWAS Catalog Tools

### `gwas_get_associations_for_trait`

Get all GWAS Catalog associations for a trait, sorted by p-value.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `efo_id` | string | One of four | Preferred. EFO/OBA term ID (e.g., `"EFO_0001645"`) |
| `disease_trait` | string | One of four | Free-text search. Less precise than `efo_id`. |
| `efo_uri` | string | One of four | Full EFO URI (e.g., `"http://www.ebi.ac.uk/efo/EFO_0001645"`) |
| `efo_trait` | string | One of four | Exact canonical EFO label string |
| `size` | integer | No | Results per page (default: API default) |
| `page` | integer | No | Page number for pagination |

Returns: array of association objects. Key fields: `p_value`, `mapped_genes[]`, `snp_allele[]`, `accession_id`, `efo_traits[]`.

Note: `p_value = 0.0` indicates extreme significance (underflow artifact), not a data error.

---

### `gwas_search_associations`

Flexible GWAS Catalog association search supporting multiple filter types.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `disease_trait` | string | No | Free-text trait/disease name |
| `efo_id` | string | No | EFO/OBA term ID |
| `efo_uri` | string | No | Full EFO URI |
| `efo_trait` | string | No | Exact EFO label |
| `rs_id` | string | No | dbSNP rs identifier (e.g., `"rs7903146"`) |
| `accession_id` | string | No | GWAS study accession (e.g., `"GCST000392"`) |
| `sort` | string | No | Sort field: `"p_value"` or `"or_value"` |
| `direction` | string | No | `"asc"` or `"desc"` |
| `size` | integer | No | Number of results |
| `page` | integer | No | Page number |

---

### `gwas_get_associations_for_snp`

Get all GWAS Catalog associations for a specific SNP.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `rs_id` | string | Yes | dbSNP rs identifier (e.g., `"rs7903146"`) |
| `sort` | string | No | `"p_value"` or `"or_value"` |
| `direction` | string | No | `"asc"` or `"desc"` |
| `size` | integer | No | Results per page |
| `page` | integer | No | Page number |

---

## Open Targets Genetics — GWAS Studies and Credible Sets

### `OpenTargets_search_gwas_studies_by_disease`

Search for GWAS studies associated with a disease in Open Targets.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `diseaseIds` | array of strings | Yes | EFO or MONDO IDs (e.g., `["MONDO_0005148"]`, `["EFO_0000249"]`) |
| `enableIndirect` | boolean | No | Include child disease terms (default: `true`) |
| `size` | integer | No | Results per page (default: 10) |
| `index` | integer | No | 0-based page index (default: 0) |

Returns: `{ count, rows[] }` where each row has `id` (GCST accession), `traitFromSource`, `nSamples`, `nCases`, `nControls`, `hasSumstats`, `diseases[]`.

---

### `OpenTargets_get_study_credible_sets`

Get all fine-mapped loci and L2G predictions for a GWAS study.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `studyIds` | array of strings | Yes | GCST accession IDs (e.g., `["GCST000392"]`) |
| `size` | integer | No | Credible sets to return (default: 20) |
| `index` | integer | No | 0-based page index (default: 0) |

Returns: `{ count, rows[] }` where each row has:
- `studyLocusId` — 32-character hash identifying this credible set; pass to `OpenTargets_get_credible_set_detail`
- `variant.id` — `chr_pos_ref_alt` format; pass to `OpenTargets_get_variant_credible_sets`
- `variant.rsIds[]` — dbSNP rs IDs (if mapped)
- `pValueMantissa`, `pValueExponent` — p-value = mantissa × 10^exponent
- `beta` — effect size
- `finemappingMethod` — e.g., `SuSiE`, `FINEMAP`
- `l2GPredictions.rows[]` — `{ target.id, target.approvedSymbol, score }` (score 0-1, higher = more likely causal)

---

### `OpenTargets_get_variant_credible_sets`

Get credible sets that contain a specific variant (by Open Targets variant ID).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `variantId` | string | Yes | Open Targets format: `chr_position_ref_alt` (e.g., `"10_112998590_C_T"`). NOT an rs ID. |
| `size` | integer | No | Number of credible sets (default: 10) |

Returns: same structure as `OpenTargets_get_study_credible_sets` rows, plus `studyId` and study metadata.

---

### `OpenTargets_get_credible_set_detail`

Get full detail on a single fine-mapped locus, including colocalization with QTLs.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `studyLocusId` | string | Yes | 32-character hex hash (e.g., `"b758d8fb10924f5338cbad8d27c7dee8"`). Obtain from `studyLocusId` field in credible set rows. |

Returns: lead variant, finemapping stats, full study metadata, L2G predictions, and colocalization evidence.

---

## Open Targets Platform — Target Information

### `OpenTargets_get_target_id_description_by_name`

Look up a gene's Ensembl ID from its symbol or common name.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `name` | string | Yes | Gene symbol or name (e.g., `"TCF7L2"`, `"PCSK9"`) |

Returns: `ensemblId`, description, and synonyms.

---

### `OpenTargets_get_target_classes_by_ensemblID`

Retrieve the protein family / target class for a gene.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | Ensembl gene ID (e.g., `"ENSG00000148737"`) |

Returns: array of `{ id, label, level }`. Common labels: `GPCR`, `Kinase`, `Ion channel`, `Nuclear receptor`, `Enzyme`, `Transcription factor`, `Epigenetic`.

Druggability tiers:
- Tier 1 (high): GPCR, Kinase, Ion channel, Nuclear receptor
- Tier 2 (moderate): Protease, Phosphatase, Epigenetic
- Tier 3 (difficult): Transcription factor, Scaffold/adaptor protein

---

### `OpenTargets_get_targ_trac_by_ense`

Retrieve tractability assessments by therapeutic modality.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | Ensembl gene ID |

Returns: array of `{ label, modality, value }` where `value` is boolean.

Key modalities: `Small molecule`, `Antibody`, `PROTAC`, `Oligonucleotide`, `Other modalities`.

Interpret: `value: true` means tractability evidence exists for that modality. A target with `Small molecule: true` has precedent for oral drug development.

---

### `OpenTargets_get_targ_cons_info_by_ense`

Retrieve genetic constraint (gnomAD) for a target.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | Ensembl gene ID |

Returns: array of `{ constraintType, exp, obs, oe, oeLower, oeUpper, score }`.

Key metric: `pLI` (probability of loss-of-function intolerance). pLI > 0.9 = high constraint = higher risk of on-target toxicity from inhibition.

---

### `OpenTargets_get_targ_safe_prof_by_ense`

Retrieve known safety liabilities for a target.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | Ensembl gene ID |

Returns: array of `{ event, eventId, biosamples[], effects[], studies[], datasource, literature }`.

`effects[].direction` values: `activation`, `inhibition`. `effects[].dosing` values: `general`, `high`.

Flag events in: cardiac tissue, liver (hepatocellular), CNS, reproductive tissues.

---

## Open Targets Platform — Disease-Drug Associations

### `OpenTargets_get_asso_drug_by_dise_efoI`

Retrieve known drugs for a disease (directly from Open Targets clinical trial data).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `efoId` | string | Yes | EFO or MONDO disease ID (e.g., `"EFO_0000384"`) |
| `size` | integer | Yes | Number of results to retrieve. Use 50-100 to avoid missing drugs. |

Returns: `{ count, rows[] }` where each row has:
- `drug.id` — ChEMBL ID
- `drug.name` — generic name
- `drug.maximumClinicalTrialPhase` — highest phase (4 = approved)
- `drug.isApproved` — boolean
- `drug.hasBeenWithdrawn` — boolean
- `mechanismOfAction` — text description
- `target.approvedSymbol` — gene symbol of drug target

---

### `OpenTargets_get_asso_drug_by_targ_ense`

Retrieve known drugs that modulate a specific target (across all indications).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | Ensembl gene ID |
| `size` | integer | Yes | Number of results |
| `cursor` | string | No | Cursor string for pagination |

Returns: same structure as `OpenTargets_get_asso_drug_by_dise_efoI` rows, with `disease.name` per row.

---

### `OpenTargets_get_asso_targ_by_dise_efoI`

Retrieve all targets associated with a disease, ranked by Open Targets association score.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `efoId` | string | Yes | EFO or MONDO disease ID |

Returns: `{ count, rows[] }` with `target.id`, `target.approvedSymbol`, `score` (0-1).

---

## ChEMBL Tools

### `ChEMBL_search_targets`

Find a ChEMBL target ID from a gene symbol or target name.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| target name / gene symbol | string | Yes | Passed as query filter. E.g., `"PCSK9"` |

Returns: ChEMBL target IDs (format: `CHEMBL_TGT_...`).

---

### `ChEMBL_get_target_activities`

Retrieve bioactivity measurements for a target.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| ChEMBL target ID | string | Yes | From `ChEMBL_search_targets` |

Returns: activity rows with `standard_type` (IC50, Ki, EC50, Kd), `standard_value`, `standard_units`, and molecule ChEMBL ID.

---

### `ChEMBL_search_drugs`

Search for drugs by name or approval status.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| drug name | string | Yes | Generic or brand name |

Returns: ChEMBL drug IDs, max clinical phase, approval status.

---

### `ChEMBL_get_drug_mechanisms`

Get mechanism(s) of action for a drug.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| ChEMBL drug ID | string | Yes | Format: `CHEMBL25` |

Returns: mechanism text, action type (inhibitor/agonist/antagonist/activator), and target.

---

## Safety and Clinical Tools

### `OpenTargets_get_drug_warnings_by_chemblId`

Retrieve drug safety warnings and withdrawal history.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `chemblId` | string | Yes | ChEMBL drug ID (e.g., `"CHEMBL25"`) |

Returns: `drugWarnings[]` with `warningType`, `description`, `toxicityClass`, `country`, `year`, and `efoIdForWarningClass`.

---

### `FDA_get_adverse_reactions_by_drug_name`

Retrieve FDA drug label adverse reaction text and warnings.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `drug_name` | string | Yes | Brand or generic name (e.g., `"Aspirin"`) |
| `limit` | integer | No | Number of label records to return |
| `skip` | integer | No | Records to skip (pagination) |

Returns: `results[]` with `adverse_reactions[]` and `warnings_and_cautions[]` as free text from drug labels.

---

## ID Format Quick Reference

| ID Type | Example | Used By |
|---------|---------|---------|
| EFO ID | `EFO_0000249` | Open Targets Platform disease tools |
| MONDO ID | `MONDO_0005148` | Open Targets Platform disease tools |
| GCST accession | `GCST000392` | `OpenTargets_get_study_credible_sets`, `OpenTargets_get_gwas_study` |
| studyLocusId | `b758d8fb10924f5338cbad8d27c7dee8` | `OpenTargets_get_credible_set_detail` |
| Open Targets variantId | `10_112998590_C_T` | `OpenTargets_get_variant_credible_sets` |
| dbSNP rs ID | `rs7903146` | GWAS Catalog tools, `gwas_get_associations_for_snp` |
| Ensembl gene ID | `ENSG00000148737` | All Open Targets target tools |
| ChEMBL drug ID | `CHEMBL25` | ChEMBL tools, `OpenTargets_get_drug_warnings_by_chemblId` |
