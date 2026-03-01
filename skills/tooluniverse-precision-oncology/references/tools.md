# Precision Oncology — Detailed Tool Reference

Detailed parameter tables for all tools used in the precision oncology workflow.
For the workflow itself, see [../SKILL.md](../SKILL.md).

---

## Phase 1: Gene/Protein ID Resolution

### MyGene.info

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `MyGene_query_genes` | Search genes by symbol | `q` (gene symbol), `species="human"` |
| `MyGene_get_gene_by_id` | Get gene by Entrez/Ensembl ID | `geneid` |

**Returns**: Ensembl gene ID (`ensembl.gene`), Entrez ID, synonyms.

### UniProt

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `UniProt_search` | Search proteins by gene name | `query`, `organism` |
| `UniProt_get_protein_by_accession` | Get full protein record | `accession` |
| `UniProt_get_protein_sequence` | Get amino acid sequence | `accession` |

**Returns**: `primaryAccession` (e.g., `P00533` for EGFR), protein name, sequence.

### ChEMBL Targets

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `ChEMBL_search_targets` | Find ChEMBL target ID | `query`, `organism="Homo sapiens"` |

**Returns**: `target_chembl_id` (e.g., `CHEMBL203`).

---

## Phase 2: Variant Interpretation

### CIViC (Clinical Interpretation of Variants in Cancer)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `civic_search_variants` | Search variants by gene/name | `query` (e.g., `"EGFR L858R"`) |
| `civic_get_variant` | Get variant details + evidence items | `id` (numeric variant ID, NOT name) |
| `civic_get_evidence_item` | Get single evidence item | `id` (evidence item ID) |
| `civic_search_genes` | Search gene records | `query` (gene name) |
| `civic_search_evidence_items` | Search evidence by drug/disease | `drug`, `disease`, `evidence_type`, `clinical_significance` |

**Workflow**: Always call `civic_search_variants` first to get the numeric ID, then call `civic_get_variant` with that ID. Never pass a variant name to `civic_get_variant`.

**Evidence types**: `"Predictive"` (drug sensitivity/resistance), `"Prognostic"`, `"Diagnostic"`.
**Clinical significance for resistance**: `clinical_significance="Resistance"`.

### ClinVar

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `ClinVar_search_variants` | Search by gene/variant | `query`, `gene` |
| `ClinVar_get_variant_by_id` | Get variant details | `variant_id` |

**Returns**: Pathogenicity classification (Pathogenic, Likely Pathogenic, VUS, Benign).

### COSMIC — Somatic Cancer Mutations

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `COSMIC_search_mutations` | Search specific mutations | `operation="search"`, `terms`, `max_results`, `genome_build` |
| `COSMIC_get_mutations_by_gene` | All mutations for gene | `operation="get_by_gene"`, `gene`, `max_results`, `genome_build` |

**Genome build**: `genome_build=38` for GRCh38 (default), `genome_build=37` for GRCh37.

**Returns**: `mutation_id`, `GeneName`, `MutationCDS`, `MutationAA`, `PrimarySite`, `PrimaryHistology`, FATHMM prediction.

**Use cases**:
- Specific mutation frequency: `COSMIC_search_mutations(operation="search", terms="BRAF V600E", max_results=20)`
- Hotspot analysis: `COSMIC_get_mutations_by_gene(operation="get_by_gene", gene="EGFR", max_results=500)`

### GDC / TCGA — Patient Tumor Data

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `GDC_get_mutation_frequency` | Pan-cancer mutation stats | `gene_symbol` |
| `GDC_get_ssm_by_gene` | Somatic mutations per project | `gene_symbol`, `project_id` (optional), `size` |
| `GDC_get_gene_expression` | RNA-seq file metadata | `project_id`, `size` |
| `GDC_get_cnv_data` | Copy number variation | `project_id`, `gene_symbol` (optional), `size` |
| `GDC_list_projects` | List TCGA/TARGET projects | `program` (e.g., `"TCGA"`), `size` |
| `GDC_search_cases` | Search patient cases | `project_id`, `size` |

**Note**: `GDC_get_gene_expression` returns file metadata, not expression values directly. For actual expression levels, use Human Protein Atlas or CELLxGENE.

**TCGA Project IDs**:
| Cancer Type | Project ID |
|-------------|------------|
| Lung Adenocarcinoma | TCGA-LUAD |
| Lung Squamous Cell | TCGA-LUSC |
| Breast | TCGA-BRCA |
| Colorectal | TCGA-COAD |
| Melanoma | TCGA-SKCM |
| Glioblastoma | TCGA-GBM |
| Pancreatic | TCGA-PAAD |
| Ovarian | TCGA-OV |

### DepMap — Target Essentiality (CRISPR Screens)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `DepMap_get_gene_dependencies` | CRISPR knockout effect scores | `gene_symbol` |
| `DepMap_get_cell_lines` | List cell lines with metadata | `tissue`, `cancer_type`, `page_size` |
| `DepMap_search_cell_lines` | Search cell lines by name | `query` |
| `DepMap_get_cell_line` | Detailed cell line info | `model_id` OR `model_name` |
| `DepMap_get_drug_response` | Drug sensitivity data | `drug_name` |

**Effect Score Interpretation**:
| Score Range | Interpretation |
|-------------|----------------|
| < -1.0 | Strongly essential (cell dies without gene) |
| -0.5 to -1.0 | Essential |
| -0.5 to 0 | Weakly essential |
| > 0 | Not essential |

**Tissue values** (case-sensitive): `"Lung"`, `"Breast"`, `"Pancreas"`, `"Skin"`, `"Brain"`.

### OncoKB — Therapeutic Actionability

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `OncoKB_annotate_variant` | Variant actionability level | `operation="annotate_variant"`, `gene`, `variant`, `tumor_type` |
| `OncoKB_get_gene_info` | Oncogene / TSG classification | `operation="get_gene_info"`, `gene` |
| `OncoKB_get_cancer_genes` | Full cancer gene list | (no parameters) |
| `OncoKB_get_levels` | Level definitions | (no parameters) |
| `OncoKB_annotate_copy_number` | CNV actionability | `operation="annotate_copy_number"`, `gene`, `copy_number_type`, `tumor_type` |

**The `operation` parameter is required for all OncoKB tools.**

**`copy_number_type` values**: `"AMPLIFICATION"` or `"DELETION"`.

**OncoTree Tumor Type Codes** (common):
| Cancer | OncoTree Code |
|--------|---------------|
| Melanoma | MEL |
| Non-Small Cell Lung Cancer | NSCLC |
| Lung Adenocarcinoma | LUAD |
| Breast Cancer | BRCA |
| Colorectal Cancer | COADREAD |
| Pancreatic Adenocarcinoma | PAAD |
| Glioblastoma | GBM |
| Ovarian Carcinoma | OV |

**OncoKB Evidence Levels**:
| Level | Tier | Description |
|-------|------|-------------|
| LEVEL_1 | ★★★ | FDA-recognized biomarker in this tumor type |
| LEVEL_2 | ★★★ | Standard care (non-FDA, e.g., NCCN guideline) |
| LEVEL_3A | ★★☆ | Compelling clinical evidence |
| LEVEL_3B | ★★☆ | Standard care in a different tumor type |
| LEVEL_4 | ★☆☆ | Biological evidence only |
| LEVEL_R1 | Resistance ★★★ | FDA-recognized resistance biomarker |
| LEVEL_R2 | Resistance ★★☆ | Compelling resistance evidence |

### cBioPortal — Cross-Study Analysis

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `cBioPortal_get_cancer_studies` | List available studies | `limit` |
| `cBioPortal_get_mutations` | Mutations for gene list | `study_id`, `gene_list` (comma-separated) |
| `cBioPortal_get_molecular_profiles` | Study molecular profiles | `study_id` |
| `cBioPortal_get_sample_clinical_data` | Sample clinical annotations | `study_id`, `sample_ids` |
| `cBioPortal_get_patient_clinical_data` | Patient clinical annotations | `study_id`, `patient_ids` |

**cBioPortal study IDs use lowercase with underscores** — different from GDC's `TCGA-*` format:
| Study | cBioPortal ID | GDC Equivalent |
|-------|---------------|----------------|
| TCGA Lung Adeno | `luad_tcga` | `TCGA-LUAD` |
| TCGA Breast | `brca_tcga` | `TCGA-BRCA` |
| TCGA Colorectal | `coadread_tcga` | `TCGA-COAD` |
| TCGA Melanoma | `skcm_tcga` | `TCGA-SKCM` |
| AACR GENIE | `genie_public` | (N/A) |

**`gene_list` format**: comma-separated HUGO symbols, e.g., `"EGFR,KRAS,ALK"`.

### Human Protein Atlas — Expression Validation

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `HPA_search_genes_by_query` | Search gene in HPA | `search_query` (gene symbol) |
| `HPA_generic_search` | Custom HPA search | `search_query`, `columns` |
| `HPA_get_comparative_expression_by_gene_and_cellline` | Tumor vs normal expression | `gene_name`, `cell_line` |

**Supported cancer cell lines**:
| Cell Line | Cancer Type |
|-----------|-------------|
| `a549` | Lung adenocarcinoma |
| `mcf7` | Breast cancer (ER+) |
| `hepg2` | Hepatocellular carcinoma |
| `hela` | Cervical cancer |
| `pc3` | Prostate cancer |
| `jurkat` | T-cell leukemia |

---

## Phase 2.5: Tumor Expression Context

### CELLxGENE — Single-Cell Expression

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `CELLxGENE_get_expression_data` | Cell-type expression in tissue | `gene`, `tissue` |
| `CELLxGENE_get_cell_metadata` | Cell annotations | `gene` |

**`tissue` values**: lowercase anatomical terms, e.g., `"lung"`, `"breast"`, `"colon"`, `"brain"`.

**Returns**: Expression per cell type (tumor epithelial, cancer-associated fibroblasts, immune cells, endothelial cells).

---

## Phase 3: Treatment Options

### OpenTargets

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `OpenTargets_get_associated_drugs_by_target_ensemblId` | Approved drugs for target | `ensemblId` (camelCase, lowercase d) |
| `OpenTargets_get_disease_associated_targets` | Targets for disease | `efoId` |
| `OpenTargets_get_target_tractability` | Target druggability | `ensemblId` |

**Critical**: Parameter is `ensemblId` (capital I, lowercase d). `ensemblID` (capital D) will not work.

### ChEMBL

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `ChEMBL_search_drugs` | Search drugs by name | `query`, `max_phase` |
| `ChEMBL_get_drug_mechanisms_of_action_by_chemblId` | Drug MOA | `chemblId` |
| `ChEMBL_get_target_activities` | Bioactivity (IC50, Ki, etc.) | `target_chembl_id` |

**`max_phase` filter**: `4` = approved, `3` = Phase 3, `2` = Phase 2.

### DailyMed — FDA Labels

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `DailyMed_search_spls` | Search FDA drug labels | `drug_name` |
| `DailyMed_get_spl_by_set_id` | Get full label | `setid` |

**Returns**: Indications, contraindications, dosing, boxed warnings.

---

## Phase 3.5: Pathway & Network Analysis

### KEGG — Cancer Pathways

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `kegg_search_pathway` | Search pathways by keyword | `query` |
| `kegg_find_genes` | Find KEGG gene entry | `query` (e.g., `"hsa:EGFR"`) |
| `kegg_get_gene_info` | Gene pathway membership | `gene_id` (e.g., `"hsa:1956"`) |

**KEGG gene ID format**: `hsa:<ENTREZ_ID>` (e.g., `hsa:1956` for EGFR).

### Reactome

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `reactome_disease_target_score` | Disease-gene relevance | `disease`, `target` |

### IntAct — Protein Interactions

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `intact_search_interactions` | Find interactions | `query`, `species` |
| `intact_get_interaction_network` | Network view | `gene`, `depth` |

**`depth` values**: `1` = direct interactors only; `2` = includes second-degree partners.

---

## Phase 4: Resistance Analysis

### NvidiaNIM — Structure Prediction & Docking

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `NvidiaNIM_alphafold2` | Predict protein structure | `sequence` (full AA sequence) |
| `NvidiaNIM_esmfold` | Fast structure prediction | `sequence` |
| `NvidiaNIM_diffdock` | Protein-ligand docking | `protein` (structure), `ligand` (SMILES), `num_poses`, `is_staged` |

**Workflow for resistance modeling**:
1. Get sequence: `UniProt_get_protein_sequence(accession=<UNIPROT_ID>)`
2. Predict WT structure: `NvidiaNIM_alphafold2(sequence=<WT_SEQ>)`
3. Dock drug: `NvidiaNIM_diffdock(protein=<STRUCTURE>, ligand=<SMILES>, num_poses=5)`
4. Repeat with mutant sequence, compare binding geometry

**SMILES for common drugs** (look up via ChEMBL if needed):
- Erlotinib: `C22H23N3O4`
- Osimertinib: `C28H33N7O2`
- Vemurafenib: `C23H18ClF2N3O3S`

---

## Phase 5: Clinical Trials

### ClinicalTrials.gov

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `search_clinical_trials` | Search active trials | `condition`, `intervention`, `status`, `pageSize` |
| `get_clinical_trial_by_nct_id` | Get trial details | `nct_id` |
| `get_clinical_trial_eligibility_criteria` | Eligibility criteria | `nct_ids` (list of NCT IDs) |

**`status` values**: `"Recruiting"`, `"Active, not recruiting"`, `"Completed"`, `"Not yet recruiting"`.

**`condition`**: Cancer type in plain English, e.g., `"Non-Small Cell Lung Cancer"`, `"Melanoma"`.

**`intervention`**: Drug name, biomarker, or target, e.g., `"EGFR"`, `"osimertinib"`, `"KRAS G12C"`.

---

## Phase 5.5: Literature

### PubMed

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `PubMed_search_articles` | Search published papers | `query` (PubMed syntax), `limit` |
| `PubMed_get_article_details` | Get abstract + metadata | `pmid` |

**Query syntax**: Use quotes for exact phrases, AND/OR/NOT for Boolean logic.
Example: `'"osimertinib" AND "T790M" AND ("resistance" OR "mechanism")'`

### EuropePMC — Preprints and Literature

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `EuropePMC_search_articles` | Search literature + preprints | `query`, `source`, `pageSize` |
| `EuropePMC_get_citations` | Get citing papers | `source`, `ext_id` |

**`source` values**: `"MED"` (PubMed/Medline), `"PPR"` (preprints — bioRxiv, medRxiv, etc.).

**Note**: bioRxiv and medRxiv do not expose their own search APIs. Always use `EuropePMC_search_articles` with `source="PPR"` to search preprints.

### OpenAlex — Citation Analysis

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `openalex_search_works` | Search papers with citation counts | `query`, `limit` |
| `openalex_get_author` | Author metrics | `author_id` |

**Returns**: `cited_by_count`, `publication_year`, `is_oa` (open access), DOI.

---

## Fallback Chain Details

### Variant Interpretation
```
CIViC → COSMIC → OncoKB → ClinVar → PubMed
```

### Somatic Mutation Frequency
```
COSMIC_get_mutations_by_gene → GDC_get_mutation_frequency → cBioPortal_get_mutations
```

### Drug Information
```
OpenTargets → ChEMBL → DailyMed
```

### Clinical Trials
```
ClinicalTrials.gov → WHO ICTRP
```

### Structure Prediction
```
AlphaFold DB (precomputed, look up by UniProt ID) → NvidiaNIM_alphafold2 → NvidiaNIM_esmfold
```

### Expression Data
```
Human Protein Atlas → CELLxGENE → GDC_get_gene_expression (file metadata only)
```

---

## TMB/MSI Special Cases

**Tumor Mutational Burden (TMB)** and **Microsatellite Instability (MSI)** are tumor-agnostic biomarkers for immunotherapy:

| Biomarker | Threshold | FDA-Approved Drug | Indication |
|-----------|-----------|-------------------|------------|
| TMB-High | ≥10 mut/Mb | Pembrolizumab (Keytruda) | Any solid tumor (TMB-H) |
| MSI-High / dMMR | MSI-H or dMMR | Pembrolizumab (Keytruda) | Any solid tumor |
| MSI-H | MSI-H | Dostarlimab (Jemperli) | dMMR solid tumors |

If the patient profile reports TMB-High or MSI-H/dMMR, always check pembrolizumab eligibility regardless of the primary driver mutation.

Query: `search_clinical_trials(condition=<CANCER>, intervention="pembrolizumab TMB", status="Recruiting")`.
