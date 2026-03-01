# Tool Parameter Reference: Clinical Trial Design

Detailed parameter listings for each tool used in the clinical trial design skill.
Use `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})` to call them.

---

## PATH 1: Patient Population Sizing

### OpenTargets_get_disease_id_description_by_name
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| diseaseName | string | yes | English name, e.g. "non-small cell lung cancer" |

Returns `data.id` (EFO ID) and description. Use the EFO ID in downstream calls.

### OpenTargets_get_diseases_phenotypes
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| efoId | string | yes | EFO identifier, e.g. "EFO_0003060" |

Prevalence data may be sparse; supplement with PubMed epidemiology papers.

### ClinVar_search_variants
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| gene | string | yes | Gene symbol, e.g. "EGFR" |
| significance | string | no | "pathogenic", "pathogenic,likely_pathogenic" |

Returns variant list; filter client-side for specific mutations (e.g., "L858R").

### gnomAD_search_gene_variants
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| gene | string | yes | Gene symbol |

Population allele frequencies. Note: gnomAD is germline-focused; somatic variants are better in COSMIC.

### search_clinical_trials
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| condition | string | no | Disease/indication |
| phase | string | no | "1", "2", "3" |
| status | string | no | "completed", "recruiting", "active" |
| nct_id | string | no | Specific trial lookup |
| intervention | string | no | Drug name |

---

## PATH 2: Biomarker Prevalence & Testing

### ClinVar_get_variant_details
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| variant_id | string | yes | ClinVar variation ID (numeric) |

### COSMIC_search_mutations
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| gene | string | yes | Gene symbol |
| cancer_type | string | no | Histology filter |

Best source for somatic mutation frequency in specific cancer types.

### gnomAD_get_variant_details
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| variant_id | string | yes | gnomAD variant ID |

---

## PATH 3: Comparator Selection

### drugbank_get_drug_basic_info_by_drug_name_or_id
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| drug_name_or_drugbank_id | string | yes | Drug name or "DB00001" style ID |

### drugbank_get_indications_by_drug_name_or_drugbank_id
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| drug_name_or_drugbank_id | string | yes | Drug name or DrugBank ID |

### drugbank_get_pharmacology_by_drug_name_or_drugbank_id
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| drug_name_or_drugbank_id | string | yes | Drug name or DrugBank ID |

Returns mechanism of action, toxicity profile. Useful for class-effect toxicity lookup.

### FDA_OrangeBook_search_drugs
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| ingredient | string | yes | Active ingredient |

Identifies patent status and generic availability for comparator sourcing.

### FDA_get_drug_approval_history
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| drug_name | string | yes | Brand or generic name |

---

## PATH 4: Endpoint Selection

Use `search_clinical_trials` (see above) with `condition`, `phase`, and `status` to find precedent trials. Extract primary endpoint text from results.

Use `FDA_get_drug_approval_history` to confirm which endpoints supported approval in the indication.

---

## PATH 5: Safety Endpoints & Monitoring

### FDA_get_warnings_and_cautions_by_drug_name
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| drug_name | string | yes | Drug name for label lookup |

Returns boxed warnings and precautions from FDA label.

### FAERS_search_reports_by_drug_and_reaction
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| drug_name | string | yes | Drug name (case-insensitive) |
| limit | integer | no | Max reports (default 100, max 500) |

Real-world adverse event reports. Use for class-effect reference drugs.

### FAERS_count_reactions_by_drug_event
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| medicinalproduct | string | yes | Drug name in UPPERCASE |

Returns ranked AE frequency table. Most useful for quick toxicity profile.

### FAERS_count_death_related_by_drug
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| medicinalproduct | string | yes | Drug name in UPPERCASE |

---

## PATH 6: Regulatory Pathway

Use `FDA_get_drug_approval_history` and `search_clinical_trials` to establish precedent approvals. Use `PubMed_search_articles` for breakthrough therapy designations and FDA guidance documents.

### PubMed_search_articles
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| query | string | yes | PubMed search string |
| max_results | integer | no | Default 10, max 100 |

Always use English query strings. Include MeSH terms for precision (e.g., "FDA[sb] AND NSCLC").
