---
name: tooluniverse-disease-research
description: Generate comprehensive disease research reports using 100+ ToolUniverse tools. Creates a detailed markdown report file and progressively updates it with findings from 10 research dimensions. All information includes source references. Use when users ask about diseases, syndromes, or need systematic disease analysis.
---

# ToolUniverse Disease Research

Generate a comprehensive, detailed disease research report with full source citations. The report is created as a markdown file and progressively updated during research.

**IMPORTANT**: Always use English disease names and search terms in tool calls, even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

## When to Use

Apply when the user:
- Asks about any disease, syndrome, or medical condition
- Needs comprehensive disease intelligence
- Wants a detailed research report with citations
- Asks "what do we know about [disease]?"

---

## Core Workflow: Report-First Approach

Do not narrate the search process to the user. Work silently through all phases and deliver the completed report.

```
User: "Research Parkinson's disease"

Agent (internal):
Phase 1 → Disambiguate: get EFO/UMLS/ICD identifiers
Phase 2 → Create report file with template
Phase 3 → Research each of the 10 dimensions, update file after each
Phase 4 → Write Executive Summary, verify checklist
Phase 5 → Present report path and summary to user
```

---

## Phase 1: Disambiguation

Resolve canonical identifiers before starting any section. These are reused across all tool calls.

**Primary EFO lookup.** Call `OSL_get_efo_id_by_disease_name` with the English disease name. Store the `efo_id` (e.g. `EFO_0000249`). This is the key identifier for OpenTargets calls.

**Cross-reference ontologies** (call in parallel):
- `OpenTargets_get_disease_id_description_by_name` — confirm EFO ID and get description
- `umls_search_concepts` — get UMLS CUI
- `icd_search_codes` with `version="ICD10CM"` — get ICD-10 codes
- `snomed_search_concepts` — get SNOMED CT code
- `ols_get_efo_term` — get synonyms and hierarchy (colon format: `EFO:0000249`)
- `ols_get_efo_term_children` — get disease subtypes

**Handle ambiguity.** If the disease name matches multiple EFO entries, pick the most specific term. If no EFO entry exists, fall back to UMLS CUI or MONDO ID.

**ID Format Note**: OpenTargets expects underscore format (`EFO_0000249`). OLS expects colon format (`EFO:0000249`). Convert between formats as needed.

---

## Phase 2: Initialize Report File

Create `{disease_slug}_research_report.md` (e.g. `parkinsons_disease_research_report.md`). Populate the header with resolved identifiers and fill section placeholders with `*Researching...*`.

### Report Template

```markdown
# Disease Research Report: {Disease Name}

**Report Generated**: {date}
**Disease Identifiers**: EFO: {efo_id} | ICD-10: {icd} | UMLS: {cui}

---

## Executive Summary

*To be written after all sections complete.*

---

## 1. Disease Identity & Classification

### Ontology Identifiers
| System | ID | Source |
|--------|-----|--------|
| EFO | | |
| ICD-10 | | |
| UMLS CUI | | |
| SNOMED CT | | |

### Synonyms & Alternative Names
- (list with source)

### Disease Hierarchy
- Parent:
- Subtypes:

**Sources**: (list tools used)

---

## 2. Clinical Presentation

### Phenotypes (HPO)
| HPO ID | Phenotype | Description | Source |
|--------|-----------|-------------|--------|

### Symptoms & Signs
- (list with source)

### Diagnostic Criteria
- (from literature/MedlinePlus)

**Sources**: (list tools used)

---

## 3. Genetic & Molecular Basis

### Associated Genes
| Gene | Score | Ensembl ID | Evidence | Source |
|------|-------|------------|----------|--------|

### GWAS Associations
| SNP | P-value | Odds Ratio | Study | Source |
|-----|---------|------------|-------|--------|

### Pathogenic Variants (ClinVar)
| Variant | Clinical Significance | Condition | Source |
|---------|----------------------|-----------|--------|

**Sources**: (list tools used)

---

## 4. Treatment Landscape

### Approved Drugs
| Drug | ChEMBL ID | Mechanism | Phase | Target | Source |
|------|-----------|-----------|-------|--------|--------|

### Clinical Trials
| NCT ID | Title | Phase | Status | Intervention | Source |
|--------|-------|-------|--------|--------------|--------|

### Treatment Guidelines
- (from literature)

**Sources**: (list tools used)

---

## 5. Biological Pathways & Mechanisms

### Key Pathways
| Pathway | Reactome ID | Genes Involved | Source |
|---------|-------------|----------------|--------|

### Protein-Protein Interactions
- (tissue-specific networks)

### Expression Patterns
| Tissue | Expression Level | Source |
|--------|------------------|--------|

**Sources**: (list tools used)

---

## 6. Epidemiology & Risk Factors

### Prevalence & Incidence
- (from literature)

### Risk Factors
| Factor | Evidence | Source |
|--------|----------|--------|

**Sources**: (list tools used)

---

## 7. Literature & Research Activity

### Publication Trends
- Total publications (5 years):
- Current year:
- Trend:

### Key Publications
| PMID | Title | Year | Citations | Source |
|------|-------|------|-----------|--------|

### Research Institutions
- (from OpenAlex)

**Sources**: (list tools used)

---

## 8. Similar Diseases & Comorbidities

### Similar Diseases
| Disease | Similarity Score | Shared Genes | Source |
|---------|-----------------|--------------|--------|

**Sources**: (list tools used)

---

## 9. Cancer-Specific Information (if applicable)

### CIViC Variants
| Gene | Variant | Evidence Level | Clinical Significance | Source |
|------|---------|----------------|----------------------|--------|

### Targeted Therapies
| Therapy | Target | Evidence | Source |
|---------|--------|----------|--------|

**Sources**: (list tools used)

---

## 10. Drug Safety & Adverse Events

### Drug Warnings
| Drug | Warning Type | Description | Source |
|------|--------------|-------------|--------|

### Clinical Trial Adverse Events
| Trial | Drug | Adverse Event | Frequency | Source |
|-------|------|---------------|-----------|--------|

**Sources**: (list tools used)

---

## References

### Tools Used
| # | Tool | Parameters | Section | Items Retrieved |
|---|------|------------|---------|-----------------|

### Data Retrieved Summary
- Total tools used:
- Sections completed:
```

---

## Phase 3: Research Each Dimension

After each dimension completes, write results to the report file before starting the next.

**Dim 1 — Identity**: Fill from Phase 1 results directly.

**Dim 2 — Clinical**: `OpenTargets_get_associated_phenotypes_by_disease_efoId`, `MedlinePlus_search_topics_by_keyword`, `MedlinePlus_get_genetics_condition_by_name`, `MedlinePlus_connect_lookup_by_code`, then `get_HPO_ID_by_phenotype` and `get_phenotype_by_HPO_ID` for key symptoms.

**Dim 3 — Genetics**: `OpenTargets_get_associated_targets_by_disease_efoId`, `clinvar_search_variants`, `gwas_search_associations`, `gwas_get_studies_for_trait`. For top 5 genes: `OpenTargets_target_disease_evidence`, `GWAS_search_associations_by_gene`. For key variants: `clinvar_get_variant_details`, `clinvar_get_clinical_significance`, `gnomad_get_variant_frequency`.

**Dim 4 — Treatment**: `OpenTargets_get_associated_drugs_by_disease_efoId`, `search_clinical_trials`, `GtoPdb_list_diseases`. For top drugs: `OpenTargets_get_drug_mechanisms_of_action_by_chemblId`. For top trials (as list): `get_clinical_trial_descriptions`, `get_clinical_trial_conditions_and_interventions`, `get_clinical_trial_outcome_measures`.

**Dim 5 — Pathways**: `Reactome_get_diseases`, `humanbase_ppi_analysis` (top genes, relevant tissue), `gtex_get_expression_by_gene`, `HPA_get_protein_expression`, `geo_search_datasets`. For top pathway IDs: `Reactome_get_pathway`, `Reactome_map_uniprot_to_pathways`.

**Dim 6 — Epidemiology**: `PubMed_search_articles` with queries `"{disease}" AND epidemiology`, `"{disease}" AND incidence OR prevalence`, `"{disease}" AND risk factors`. Also `gwas_get_associations_for_trait` for genetic risk.

**Dim 7 — Literature**: `PubMed_search_articles` (limit=100), `openalex_search_works`, `europe_pmc_search_abstracts`, `semantic_scholar_search_papers`, `OpenTargets_get_publications_by_disease_efoId`. Then `PubMed_get_article` for top 10 PMIDs.

**Dim 8 — Similar**: `OpenTargets_get_similar_entities_by_disease_efoId` (threshold=0.3, size=30).

**Dim 9 — Cancer** (skip if not a cancer): `civic_search_diseases`, `civic_search_genes`, `civic_get_variants_by_gene`, `civic_get_evidence_item`, `civic_search_therapies`, `civic_search_molecular_profiles`.

**Dim 10 — Safety**: For each drug: `OpenTargets_get_drug_warnings_by_chemblId`, `OpenTargets_get_drug_blackbox_status_by_chembl_ID`, `FAERS_count_reactions_by_drug_event`. For top trials: `extract_clinical_trial_adverse_events`. Optionally: `AdverseEventPredictionQuestionGenerator`.

---

## Phase 4: Finalize Report

1. Write the Executive Summary (3-5 sentences: top genes, drugs, trial count, epidemiology).
2. Append the complete References table listing every tool call, parameters, section, and item count.
3. Run the quality checklist.

### Quality Checklist

- All 10 sections have content (or explicitly marked "No data available")
- Every data point has a source citation
- Executive Summary reflects key findings
- References section lists all tool calls
- Tables are properly formatted markdown
- No placeholder text (`*Researching...*`) remains

---

## Citation Format

**In tables** — add a `Source` column:
```
| Gene | Score | Source |
|------|-------|--------|
| APOE | 0.92  | OpenTargets_get_associated_targets_by_disease_efoId |
```

**In lists** — append inline:
```
- Memory loss [Source: OpenTargets_get_associated_phenotypes_by_disease_efoId]
```

**In prose**:
```
The disease affects ~6.5 million Americans
(Source: PubMed_search_articles, query: "Alzheimer disease epidemiology").
```

---

## Abbreviated Tool Reference

Full parameter details: [references/tools.md](references/tools.md)

| Section | Key Tools |
|---------|-----------|
| Identity | `OSL_get_efo_id_by_disease_name`, `OpenTargets_get_disease_id_description_by_name`, `ols_search_efo_terms`, `ols_get_efo_term`, `ols_get_efo_term_children`, `umls_search_concepts`, `umls_get_concept_details`, `icd_search_codes`, `snomed_search_concepts` |
| Clinical | `OpenTargets_get_associated_phenotypes_by_disease_efoId`, `get_HPO_ID_by_phenotype`, `get_phenotype_by_HPO_ID`, `get_joint_associated_diseases_by_HPO_ID_list`, `MedlinePlus_search_topics_by_keyword`, `MedlinePlus_get_genetics_condition_by_name`, `MedlinePlus_connect_lookup_by_code` |
| Genetics | `OpenTargets_get_associated_targets_by_disease_efoId`, `OpenTargets_target_disease_evidence`, `clinvar_search_variants`, `clinvar_get_variant_details`, `clinvar_get_clinical_significance`, `gwas_search_associations`, `gwas_get_variants_for_trait`, `gwas_get_associations_for_trait`, `gwas_get_studies_for_trait`, `GWAS_search_associations_by_gene`, `gnomad_get_variant_frequency` |
| Treatment | `OpenTargets_get_associated_drugs_by_disease_efoId`, `OpenTargets_get_drug_chembId_by_generic_name`, `OpenTargets_get_drug_mechanisms_of_action_by_chemblId`, `search_clinical_trials`, `get_clinical_trial_descriptions`, `get_clinical_trial_conditions_and_interventions`, `get_clinical_trial_eligibility_criteria`, `get_clinical_trial_outcome_measures`, `extract_clinical_trial_outcomes`, `GtoPdb_list_diseases`, `GtoPdb_get_disease` |
| Pathways | `Reactome_get_diseases`, `Reactome_get_pathway`, `Reactome_get_pathway_reactions`, `Reactome_map_uniprot_to_pathways`, `humanbase_ppi_analysis`, `gtex_get_expression_by_gene`, `HPA_get_protein_expression`, `geo_search_datasets` |
| Literature | `PubMed_search_articles`, `PubMed_get_article`, `PubMed_get_related`, `PubMed_get_cited_by`, `OpenTargets_get_publications_by_disease_efoId`, `openalex_search_works`, `europe_pmc_search_abstracts`, `semantic_scholar_search_papers` |
| Similar | `OpenTargets_get_similar_entities_by_disease_efoId` |
| Cancer | `civic_search_diseases`, `civic_search_genes`, `civic_get_variants_by_gene`, `civic_get_variant`, `civic_get_evidence_item`, `civic_search_therapies`, `civic_search_molecular_profiles` |
| Pharmacology | `GtoPdb_get_targets`, `GtoPdb_get_target`, `GtoPdb_get_target_interactions`, `GtoPdb_search_interactions`, `GtoPdb_list_ligands` |
| Safety | `OpenTargets_get_drug_warnings_by_chemblId`, `OpenTargets_get_drug_blackbox_status_by_chembl_ID`, `extract_clinical_trial_adverse_events`, `FAERS_count_reactions_by_drug_event`, `AdverseEventPredictionQuestionGenerator` |

---

## Known Gotchas

**EFO ID format mismatch.** OpenTargets tools expect underscore format (`EFO_0000249`). OLS tools expect colon format (`EFO:0000249`). Always convert before passing to a tool.

**`OSL_get_efo_id_by_disease_name` may return no result.** Fall back to `ols_search_efo_terms` or `OpenTargets_get_disease_id_description_by_name` and pick the best match manually.

**UMLS requires an API key.** If `UMLS_API_KEY` is not set, skip UMLS calls gracefully and note the gap in the References section.

**OpenTargets returns sparse data for rare diseases.** If the disease maps to an Orphanet or MONDO ID rather than an EFO ID, some OpenTargets endpoints may return empty results. Try the EFO mapping first; use Orphanet/MONDO directly as fallback.

**`MedlinePlus_get_genetics_condition_by_name` expects a URL slug**, not a plain name. Convert "Alzheimer disease" to `alzheimer-disease` before calling.

**`MedlinePlus_connect_lookup_by_code` needs the ICD-10-CM OID** (`2.16.840.1.113883.6.90`) as `cs` and the code (e.g. `E11.9`) as `c` — two separate parameters.

**Clinical trial tools accept a list of NCT IDs**, not a single string. Pass `nct_ids` as a JSON array even when fetching a single trial.

**`humanbase_ppi_analysis` is slow for large gene lists.** Limit `gene_list` to the top 10 genes and choose a tissue relevant to the disease (e.g. `"brain"` for neurological conditions).

**`Reactome_get_diseases` returns all diseases.** Filter the response locally by DOID or disease name after the call.

**CIViC tools use internal numeric IDs**, not standard identifiers. Always call `civic_search_diseases` or `civic_search_genes` first to retrieve the CIViC-specific ID before calling detail endpoints.

**`gwas_search_associations` uses free-text trait matching.** Try both the exact disease name and common synonyms if results are sparse.

**`gnomad_get_variant_frequency` requires chr-pos-ref-alt format** (e.g. `1-55505647-G-T`), not rsID. Convert from ClinVar or GWAS data before calling.

**Empty results are not errors.** If a tool returns an empty list or `{}`, record "No data available" in the report section and continue.

**PubMed query quoting.** Wrap multi-word disease names in double quotes inside the query string (e.g. `'"Parkinson disease" AND treatment'`).

---

## Evidence Grading

When reporting findings, grade the strength of evidence:

| Grade | Criteria |
|-------|----------|
| A — Strong | Replicated GWAS (p<5×10⁻⁸), FDA-approved drug, Cochrane review |
| B — Moderate | Single GWAS, Phase 3 trial, systematic review |
| C — Limited | Candidate gene study, Phase 1-2 trial, case series |
| D — Preliminary | Animal model, in vitro only, preprint |

Include the grade in summary statements about gene associations or treatment efficacy.

---

## Data Gaps

When a section cannot be populated, add an explicit note rather than leaving it blank:

```
**Data Gap**: UMLS data unavailable — UMLS_API_KEY not configured.
**Data Gap**: No ClinVar variants found for this disease name; try gene-based search.
**Data Gap**: GEO returned no expression datasets matching "{disease_name}".
```

---

## Expected Report Scale

For a well-studied disease (e.g. Alzheimer's), the completed report should contain 500+ individual data points, each with a source citation:

- Sec 1: 5+ ontology IDs, 10+ synonyms, disease hierarchy
- Sec 2: 20+ HPO phenotypes, symptoms list, diagnostic criteria
- Sec 3: 50+ genes with scores, 30+ GWAS associations, 100+ ClinVar variants
- Sec 4: 20+ drugs, 50+ clinical trials with phase/status/intervention
- Sec 5: 10+ pathways, PPI network, tissue expression data
- Sec 6: Epidemiology stats, 10+ risk factors with evidence
- Sec 7: 100+ publications, citation counts, institution list
- Sec 8: 15+ similar diseases with similarity scores
- Sec 9: (if cancer) variants, evidence items, targeted therapies
- Sec 10: Drug warnings and blackbox status, adverse events per drug

---

See [references/tools.md](references/tools.md) for full parameter reference by tool.
See [EXAMPLES.md](EXAMPLES.md) for sample reports.
