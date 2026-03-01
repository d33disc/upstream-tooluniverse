---
name: tooluniverse-cancer-variant-interpretation
description: Provide comprehensive clinical interpretation of somatic mutations in cancer. Given a gene symbol + variant (e.g., EGFR L858R, BRAF V600E) and optional cancer type, performs multi-database analysis covering clinical evidence (CIViC), mutation prevalence (cBioPortal), therapeutic associations (OpenTargets, ChEMBL, FDA), resistance mechanisms, clinical trials, prognostic impact, and pathway context. Generates an evidence-graded markdown report with actionable recommendations for precision oncology. Use when oncologists, molecular tumor boards, or researchers ask about treatment options for specific cancer mutations, resistance mechanisms, or clinical trial matching.
---

# Cancer Variant Interpretation for Precision Oncology

Comprehensive clinical interpretation of somatic mutations in cancer. Transforms a gene + variant input into an actionable precision oncology report covering clinical evidence, therapeutic options, resistance mechanisms, clinical trials, and prognostic implications.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create the report file FIRST, then populate it progressively as each phase completes.
2. **Evidence-graded** - Every recommendation must have an evidence tier (T1-T4).
3. **Actionable output** - Prioritized treatment options, not data dumps.
4. **Clinical focus** - Answer "what should we treat with?" not "what databases exist?"
5. **Resistance-aware** - Always check for known resistance mechanisms.
6. **Cancer-type specific** - Tailor all recommendations to the patient's cancer type when provided.
7. **Source-referenced** - Every statement must cite the tool/database source.
8. **English-first queries** - Always use English terms in tool calls (gene names, drug names, cancer types), even if the user writes in another language. Respond in the user's language.

---

## When to Use

Apply when user asks:
- "What treatments exist for EGFR L858R in lung cancer?"
- "Patient has BRAF V600E melanoma - what are the options?"
- "Is KRAS G12C targetable?"
- "Patient progressed on osimertinib - what's next?"
- "What clinical trials are available for PIK3CA E545K?"
- "Interpret this somatic mutation: TP53 R273H"
- "Molecular tumor board: EGFR exon 19 deletion, NSCLC"

---

## Input Parsing

**Required**: Gene symbol + variant notation
**Optional**: Cancer type (improves specificity)

| Format | Example | How to Parse |
|--------|---------|-------------|
| Gene + amino acid change | EGFR L858R | gene=EGFR, variant=L858R |
| Gene + HGVS protein | BRAF p.V600E | gene=BRAF, variant=V600E |
| Gene + exon notation | EGFR exon 19 deletion | gene=EGFR, variant=exon 19 deletion |
| Gene + fusion | EML4-ALK fusion | gene=ALK, variant=EML4-ALK |
| Gene + amplification | HER2 amplification | gene=ERBB2, variant=amplification |
| Full query with cancer | "EGFR L858R in lung adenocarcinoma" | gene=EGFR, variant=L858R, cancer=lung adenocarcinoma |

**Gene symbol normalization**: HER2 -> ERBB2, PD-L1 -> CD274, VEGF -> VEGFA.

---

## Known Gotchas

Verify these before calling any tool for the first time.

| Tool | Wrong | Correct |
|------|-------|---------|
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblID` | `ensemblId` (camelCase) |
| `OpenTargets_get_drug_chembId_by_generic_name` | `genericName` | `drugName` |
| `OpenTargets_target_disease_evidence` | `ensemblID` | `ensemblId` + `efoId` both required |
| `MyGene_query_genes` | `q` | `query` |
| `search_clinical_trials` | `disease`, `biomarker` | `condition`, `query_term` (required) |
| `civic_get_variants_by_gene` | `gene_symbol` | `gene_id` (CIViC numeric ID, not Entrez) |
| `drugbank_*` | any 3 params | ALL 4 required: `query`, `case_sensitive`, `exact_match`, `limit` |
| `ChEMBL_get_drug_mechanisms` | `chembl_id` | `drug_chembl_id__exact` |
| `ensembl_lookup_gene` | no species | `species='homo_sapiens'` is REQUIRED when using Ensembl IDs |
| `PubMed_search_articles` | `result["articles"]` | response is a **plain list**, not a dict |
| `UniProt_get_function_by_accession` | `result["function"]` | response is a **list of strings**, not a dict |
| `cBioPortal_get_mutations` | treat result as list | use `result.get("data", [])` (wrapped in `{status, data}`) |
| `civic_search_genes` | expects name filter | does NOT filter server-side; returns genes alphabetically, max 100 per call |

**CIViC lookup strategy**: `civic_search_genes` returns genes alphabetically with no server-side filtering. For genes starting beyond "C" (e.g., EGFR, KRAS, TP53), the first 100 results will not contain them. Use the Entrez ID from MyGene to cross-reference, or use known CIViC IDs from the table in Phase 2 below. Fall back to OpenTargets and cBioPortal if CIViC lookup fails.

**GTEx versioned ID**: GTEx requires a versioned Ensembl ID (e.g., `ENSG00000146648.12`). Call `ensembl_lookup_gene` with `species='homo_sapiens'` first to get the version, then append it: `{ensembl_id}.{version}`.

---

## Workflow Overview

```
Input: Gene symbol + Variant notation + Optional cancer type

Phase 1: Gene Disambiguation & ID Resolution
  - Resolve gene to Ensembl ID, UniProt accession, Entrez ID
  - Get gene function, pathways, protein domains
  - Identify cancer type EFO ID (if cancer type provided)

Phase 2: Clinical Variant Evidence (CIViC)
  - Find gene in CIViC (via Entrez ID or known CIViC gene IDs)
  - Get all variants for the gene and match the specific variant
  - Retrieve evidence items (predictive, prognostic, diagnostic)
  - Get CIViC assertions

Phase 3: Mutation Prevalence (cBioPortal)
  - Frequency across cancer studies
  - Co-occurring mutations
  - Cancer type distribution

Phase 4: Therapeutic Associations (OpenTargets + ChEMBL + FDA + DrugBank)
  - FDA-approved targeted therapies
  - Clinical trial drugs (phase 2-3)
  - Drug mechanisms of action
  - Drug label information

Phase 5: Resistance Mechanisms
  - Known resistance variants (CIViC, literature)
  - Bypass pathway analysis (Reactome)
  - Secondary mutations

Phase 6: Clinical Trials
  - Active trials recruiting for this mutation
  - Trial phase and status

Phase 7: Prognostic Impact & Pathway Context
  - Survival associations (PubMed)
  - Pathway context (Reactome)
  - Expression data (GTEx)

Phase 8: Report Synthesis
  - Executive summary
  - Clinical actionability score
  - Treatment recommendations (prioritized)
  - Completeness checklist
```

---

## Phase 1: Gene Disambiguation & ID Resolution

**Goal**: Resolve gene symbol to all cross-database identifiers needed for downstream queries.

Call `MyGene_query_genes` with `query=<gene_symbol>` and `species='human'`. Take the top hit where `symbol` matches exactly (case-insensitive). Extract `ensembl.gene` (Ensembl ID), `entrezgene` (Entrez ID), and `name`.

Call `UniProt_search` with `query='gene:<SYMBOL>'` and `organism='human'`. Extract `results[0].accession` as the UniProt accession.

Call `OpenTargets_get_target_id_description_by_name` with `targetName=<gene_symbol>`. Match the hit where `name` equals the gene symbol (case-insensitive). Extract `id` as the OpenTargets Ensembl ID.

If cancer type is provided, call `OpenTargets_get_disease_id_description_by_name` with `diseaseName=<cancer_type>`. Extract `data.search.hits[0].id` as the EFO ID for disease-specific queries.

Call `UniProt_get_function_by_accession` with the UniProt accession. The response is a list of strings — join them as the protein function summary.

---

## Phase 2: Clinical Variant Evidence (CIViC)

**Goal**: Get clinical interpretations for the specific variant.

**Step 2.1 - Find the CIViC gene ID**: First check the known ID table below. If not listed, call `civic_search_genes` with `limit=100` and search the result nodes client-side by matching `entrezId` against the Entrez ID from Phase 1.

**Known CIViC Gene IDs for common cancer genes**:

| Gene | CIViC Gene ID | Entrez ID |
|------|--------------|-----------|
| ABL1 | 4 | 25 |
| ALK | 1 | 238 |
| BRAF | 5 | 673 |

For genes not listed, use `civic_search_genes` with `limit=100` and match `entrezId`. If still not found, document this and proceed with OpenTargets and cBioPortal evidence.

**Step 2.2 - Get variants**: Call `civic_get_variants_by_gene` with the CIViC numeric `gene_id` and `limit=200`. Response path: `data.gene.variants.nodes[]` where each node has `{id, name}`. Match the target variant by comparing (case-insensitive, stripping `p.` prefix). Try exact match first, then partial match.

**Step 2.3 - Get variant details**: Call `civic_get_variant` with the numeric `variant_id`. Response path: `data.variant`.

**Step 2.4 - Fallback if CIViC unavailable**: Search PubMed for `"<GENE>" "<VARIANT>" clinical significance cancer`. Also use `OpenTargets_target_disease_evidence` with both `ensemblId` and `efoId` for target-disease evidence.

### Evidence Level Mapping

| CIViC Level | Tier | Meaning | Clinical Action |
|-------------|------|---------|-----------------|
| A | T1 | FDA-approved, guideline | Standard of care |
| B | T2 | Clinical evidence | Strong recommendation |
| C | T2 | Case study | Consider with caution |
| D | T3 | Preclinical | Research context only |
| E | T4 | Inferential | Computational evidence |

---

## Phase 3: Mutation Prevalence (cBioPortal)

**Goal**: Determine how common this mutation is across cancer types and studies.

Call `cBioPortal_get_cancer_studies` with `limit=50`. Filter studies by the cancer keyword if a cancer type was provided. Key TCGA study IDs: `luad_tcga` (lung adenocarcinoma), `brca_tcga` (breast), `coadread_tcga` (colorectal), `skcm_tcga` (melanoma), `paad_tcga` (pancreatic), `gbm_tcga` (glioblastoma), `prad_tcga` (prostate), `ov_tcga` (ovarian).

For each relevant study, call `cBioPortal_get_mutations` with `study_id=<study>` and `gene_list=<GENE>`. Extract mutations from `result.get("data", [])` (never treat the result as a plain list). From the mutation list, count samples carrying the target variant (match `proteinChange` case-insensitively) and report: total mutated samples, target variant count, and top co-occurring variants.

---

## Phase 4: Therapeutic Associations

**Goal**: Identify all available therapies — approved, in trials, and experimental.

**Step 4.1 - OpenTargets drug-target associations (primary source)**: Call `OpenTargets_get_associated_drugs_by_target_ensemblID` with `ensemblId=<ensembl_id>` and `size=50`. Response path: `data.target.knownDrugs.rows[]`. Each row contains `drug.name`, `drug.isApproved`, `drug.maximumClinicalTrialPhase`, `mechanismOfAction`, and `disease.name`. Categorize: approved drugs (`drug.isApproved=true`), Phase 3 (`phase=3`), Phase 2 (`phase=2`).

**Step 4.2 - Disease-specific filtering**: If cancer type EFO ID is available, call `OpenTargets_get_associated_drugs_by_disease_efoId` with `efoId=<efo_id>` and `size=30` to intersect with cancer-type-specific drugs.

**Step 4.3 - FDA label details**: For each recommended drug, call `FDA_get_indications_by_drug_name` and `FDA_get_mechanism_of_action_by_drug_name`. If not found in FDA, fall back to `drugbank_get_drug_basic_info_by_drug_name_or_id` (all four params required: `query`, `case_sensitive=false`, `exact_match=false`, `limit`).

**Step 4.4 - ChEMBL mechanism**: Obtain the ChEMBL ID via `OpenTargets_get_drug_chembId_by_generic_name` with `drugName=<name>`. Then call `ChEMBL_get_drug_mechanisms` with `drug_chembl_id__exact=<chembl_id>`.

### Treatment Prioritization

| Priority | Criteria | Tier |
|----------|----------|------|
| 1st Line | FDA-approved for exact indication + biomarker | T1 |
| 2nd Line | FDA-approved for different indication, same biomarker | T1-T2 |
| 3rd Line | Phase 3 clinical trial data | T2 |
| 4th Line | Phase 1-2 data, off-label with evidence | T3 |
| 5th Line | Preclinical or computational only | T4 |

---

## Phase 5: Resistance Mechanisms

**Goal**: Identify known resistance patterns and strategies to overcome them.

Search CIViC variants (from Phase 2) for nodes with "Resistance" in the name. Additionally, call `PubMed_search_articles` with `query='"<GENE>" AND "<DRUG>" AND resistance AND mechanism'` and `limit=15`, `include_abstract=true`. The response is a plain list of article dicts — do not wrap in `{articles: [...]}`.

Call `Reactome_map_uniprot_to_pathways` with the UniProt accession to identify bypass pathway candidates.

### Known Resistance Patterns (Reference)

| Primary Target | Primary Drug | Resistance Mutation | Mechanism | Strategy |
|---------------|-------------|-------------------|-----------|----------|
| EGFR L858R | Erlotinib/Gefitinib | T790M | Steric hindrance | Osimertinib (3rd-gen TKI) |
| EGFR T790M | Osimertinib | C797S | Covalent bond loss | 4th-gen TKI trials |
| BRAF V600E | Vemurafenib | Splice variants | Paradoxical activation | BRAF+MEK combination |
| ALK fusion | Crizotinib | L1196M, G1269A | Kinase domain mutations | Alectinib, Lorlatinib |
| KRAS G12C | Sotorasib | Y96D, R68S | Drug binding loss | KRAS G12C combo trials |

---

## Phase 6: Clinical Trials

**Goal**: Find actively recruiting clinical trials relevant to this mutation.

Make two `search_clinical_trials` calls:
1. `query_term="<GENE> <VARIANT>"`, `condition=<cancer_type or "cancer">`, `pageSize=20`
2. `query_term="<GENE> mutation"`, `condition=<cancer_type or "cancer">`, `pageSize=20`

Response path: `studies[]` with fields `NCT ID`, `brief_title`, `overall_status`, `phase`. Prioritize trials with status `RECRUITING` or `NOT_YET_RECRUITING`, Phase 2 or 3, and variant-specific enrollment criteria.

Report format:

| NCT ID | Phase | Agent(s) | Status | Cancer Type | Biomarker |
|--------|-------|----------|--------|-------------|-----------|

---

## Phase 7: Prognostic Impact & Pathway Context

**Goal**: Assess the variant's impact on prognosis and biological context.

Call `PubMed_search_articles` with `query='"<GENE>" "<VARIANT>" prognosis survival'` (append cancer type if provided), `limit=10`, `include_abstract=true`.

Call `Reactome_map_uniprot_to_pathways` with the UniProt accession for pathway context.

For GTEx expression: first call `ensembl_lookup_gene` with `gene_id=<ensembl_id>` and `species='homo_sapiens'` to get the version number. Then call `GTEx_get_median_gene_expression` with `gencode_id="<ENSEMBL_ID>.<version>"` and `operation="median"`.

Call `UniProt_get_disease_variants_by_accession` with the UniProt accession to surface known disease-associated variants in the same gene.

---

## Phase 8: Report Synthesis

### Report File Naming

File name: `{GENE}_{VARIANT}_cancer_variant_report.md` (e.g., `EGFR_L858R_cancer_variant_report.md`).

### Required Report Sections

The report must contain these sections in order:

1. **Header**: Gene, variant, date, cancer type.
2. **Executive Summary**: 1-2 actionable sentences. Clinical Actionability score (HIGH / MODERATE / LOW / UNKNOWN).
3. **Gene & Variant Overview**: Table with symbol, full name, Ensembl ID, UniProt accession, Entrez ID, variant notation, protein function summary.
4. **Clinical Variant Evidence**: CIViC interpretation table (Evidence Type | Description | Level | Clinical Significance). Evidence summary with source citation.
5. **Mutation Prevalence**: Table per study (Study | Cancer Type | Total Mutated | This Variant | Frequency). Source: cBioPortal.
6. **Therapeutic Options**: Sub-sections for FDA-approved therapies (T1) and clinical trial drugs (T2-T3), each as a table (Drug | Trade Name | Indication | Mechanism | Phase). Drug detail narrative per recommended drug. Sources: OpenTargets, FDA, DrugBank, ChEMBL.
7. **Resistance Mechanisms**: Table (Resistance Mutation | Drug Affected | Mechanism | Strategy to Overcome). Sources: CIViC, PubMed, Reactome.
8. **Clinical Trials**: Table (NCT ID | Phase | Agent(s) | Status | Biomarker Required). Source: ClinicalTrials.gov.
9. **Prognostic Impact**: Survival associations (PubMed), pathway context (Reactome), expression profile (GTEx).
10. **Evidence Grading Summary**: Table (Finding | Evidence Tier | Source | Confidence).
11. **Data Sources Queried**: Table listing every tool called.

### Completeness Checklist

Before finalizing, verify:
- [ ] Gene resolved to Ensembl, UniProt, and Entrez IDs
- [ ] Clinical variant evidence queried (CIViC or alternative)
- [ ] Mutation prevalence assessed (at least 1 cBioPortal study)
- [ ] At least 1 therapeutic option identified with evidence tier, OR documented as "no targeted therapy available"
- [ ] FDA label information retrieved for recommended drugs
- [ ] Resistance mechanisms assessed (known patterns + literature search)
- [ ] At least 3 clinical trials listed, OR "no matching trials found"
- [ ] Prognostic literature searched; pathway context attempted (Reactome)
- [ ] Executive summary is actionable (says what to DO, not just what was found)
- [ ] All recommendations cite the source tool/database
- [ ] Evidence tiers (T1-T4) assigned to all findings

---

## Evidence Grading System

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|---------|
| T1 | [T1] | FDA-approved therapy, Level A CIViC, phase 3 trial | Osimertinib for EGFR T790M |
| T2 | [T2] | Phase 2/3 clinical data, Level B CIViC evidence | Combination trial data |
| T3 | [T3] | Preclinical data, Level D CIViC, case reports | Novel mechanisms, in vitro |
| T4 | [T4] | Computational prediction, pathway inference | Docking, pathway analysis |

---

## Clinical Actionability Scoring

| Score | Criteria |
|-------|----------|
| HIGH | FDA-approved targeted therapy exists for this exact mutation + cancer type |
| MODERATE | Approved therapy for different cancer type with same mutation, OR phase 2-3 trial data |
| LOW | Only preclinical evidence or pathway-based rationale |
| UNKNOWN | Insufficient data to assess actionability |

---

## Fallback Chains

| Primary Tool | Fallback | Use When |
|-------------|----------|----------|
| CIViC variant lookup | PubMed literature search | Gene not found in CIViC |
| OpenTargets drugs | ChEMBL drug search | No OpenTargets drug hits |
| FDA indications | DrugBank drug info | Drug not in FDA database |
| cBioPortal TCGA study | cBioPortal pan-cancer | Specific cancer study not available |
| GTEx expression | Ensembl gene lookup | GTEx returns empty |
| Reactome pathways | UniProt function | Pathway mapping fails |

---

## Tool Reference (Abbreviated)

Full parameter details and response schemas: `references/tools.md`

### Gene Resolution

| Tool | Key Parameters | Key Response Fields |
|------|---------------|---------------------|
| `MyGene_query_genes` | `query` (req), `species` | `hits[].symbol`, `hits[].ensembl.gene`, `hits[].entrezgene` |
| `UniProt_search` | `query` (req), `organism`, `limit` | `results[].accession`, `results[].gene_names` |
| `OpenTargets_get_target_id_description_by_name` | `targetName` (req) | `data.search.hits[].id` (ensemblId) |
| `OpenTargets_get_disease_id_description_by_name` | `diseaseName` (req) | `data.search.hits[].id` (efoId) |
| `ensembl_lookup_gene` | `gene_id` (req), `species='homo_sapiens'` (req) | `data.id`, `data.version` |
| `UniProt_get_function_by_accession` | `accession` (req) | Returns list of strings |

### Clinical Evidence

| Tool | Key Parameters | Key Response Fields |
|------|---------------|---------------------|
| `civic_search_genes` | `query`, `limit` | `data.genes.nodes[].id`, `.entrezId` |
| `civic_get_variants_by_gene` | `gene_id` (req, CIViC numeric), `limit` | `data.gene.variants.nodes[].id`, `.name` |
| `civic_get_variant` | `variant_id` (req) | `data.variant.id`, `.name` |

### Mutation Prevalence

| Tool | Key Parameters | Key Response Fields |
|------|---------------|---------------------|
| `cBioPortal_get_mutations` | `study_id`, `gene_list` | `data[].proteinChange`, `.sampleId` |
| `cBioPortal_get_cancer_studies` | `limit` | `[].studyId`, `.name`, `.cancerTypeId` |

### Drug Information

| Tool | Key Parameters | Key Response Fields |
|------|---------------|---------------------|
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblId` (req), `size` | `data.target.knownDrugs.rows[].drug.name`, `.isApproved` |
| `OpenTargets_get_drug_chembId_by_generic_name` | `drugName` (req) | `data.search.hits[].id` (ChEMBL ID) |
| `FDA_get_indications_by_drug_name` | `drug_name`, `limit` | `results[].indications_and_usage` |
| `FDA_get_mechanism_of_action_by_drug_name` | `drug_name`, `limit` | `results[].mechanism_of_action` |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | `query`, `case_sensitive`, `exact_match`, `limit` (ALL req) | `results[].drug_name`, `.description` |
| `ChEMBL_get_drug_mechanisms` | `drug_chembl_id__exact` (req), `limit` | `data.mechanisms[]` |

### Clinical Trials & Literature

| Tool | Key Parameters | Key Response Fields |
|------|---------------|---------------------|
| `search_clinical_trials` | `query_term` (req), `condition`, `pageSize` | `studies[].NCT ID`, `.overall_status`, `.phase` |
| `PubMed_search_articles` | `query` (req), `limit`, `include_abstract` | Plain list: `[{pmid, title, abstract}]` |
| `Reactome_map_uniprot_to_pathways` | `id` (req, UniProt accession) | Pathway mappings |
| `GTEx_get_median_gene_expression` | `gencode_id` (req, versioned), `operation="median"` | Expression by tissue |

---

## Common Use Cases

**EGFR L858R in lung adenocarcinoma**: Expected output shows osimertinib as 1st-line [T1], FDA label details, resistance pattern (T790M -> osimertinib), clinical trials for combinations, and prognostic context.

**BRAF V600E in colorectal cancer**: Expected output notes BRAF V600E is actionable in melanoma but requires combination (encorafenib + cetuximab) in CRC, with distinct resistance patterns from melanoma.

**KRAS G12C, any cancer type**: Expected output with sotorasib/adagrasib as approved [T1], comprehensive KRAS G12C trial listing, resistance mutations (Y96D, R68S), mutation prevalence across cancer types.

**EGFR T790M after osimertinib failure**: Expected output focused on C797S resistance, 4th-generation TKI trials, amivantamab/lazertinib combinations, bypass pathway mechanisms (MET amplification, HER2 activation).

**PIK3CA E545K**: Expected output showing this is a known hotspot oncogenic mutation (not a VUS), alpelisib as FDA-approved for HR+/HER2- breast cancer [T1], and prevalence across cancer types.

---

## Quantified Minimums

| Section | Requirement |
|---------|-------------|
| Gene IDs | At least Ensembl + UniProt resolved |
| Clinical evidence | CIViC queried + PubMed literature search |
| Mutation prevalence | At least 1 cBioPortal study |
| Therapeutic options | All approved drugs listed (OpenTargets) + FDA label for top drugs |
| Resistance | Literature search performed + known patterns documented |
| Clinical trials | At least 1 search query executed |
| Prognostic impact | PubMed literature search performed |
| Pathway context | Reactome pathway mapping attempted |

---

## See Also

- `references/tools.md` - Full tool parameter tables and response schemas
- `EXAMPLES.md` - Complete example reports
