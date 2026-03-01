# Rare Disease Diagnosis - Detailed Tool Reference

Detailed parameter tables, thresholds, and examples for each phase.
For the workflow guide, see [SKILL.md](../SKILL.md).

---

## Phase 1: Phenotype Standardization

### HPO Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `HPO_search_terms` | Search HPO by text | `query` |
| `HPO_get_term_by_id` | Get HPO term details | `hp_id` |
| `HPO_get_term_genes` | Genes associated with HPO term | `hp_id` |
| `HPO_get_term_diseases` | Diseases with HPO term | `hp_id` |

---

## Phase 2: Disease Matching

### Orphanet Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `Orphanet_search_diseases` | Search rare diseases | `operation="search_diseases"`, `query` |
| `Orphanet_get_disease` | Get disease details | `operation="get_disease"`, `orpha_code` |
| `Orphanet_get_genes` | Genes for disease | `operation="get_genes"`, `orpha_code` |
| `Orphanet_get_classification` | Disease hierarchy | `operation="get_classification"`, `orpha_code` |
| `Orphanet_search_by_name` | Exact name search | `operation="search_by_name"`, `name`, `exact` |

**Common Orphanet Disease Codes**:
| Disease | ORPHA Code |
|---------|------------|
| Marfan syndrome | 558 |
| Loeys-Dietz syndrome | 60030 |
| Vascular EDS | 286 |
| Alexander disease | 58 |
| Prader-Willi syndrome | 739 |

### OMIM Tools

**Requires**: `OMIM_API_KEY` environment variable (register at omim.org/api)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `OMIM_search` | Search OMIM | `operation="search"`, `query`, `limit` |
| `OMIM_get_entry` | Get MIM entry | `operation="get_entry"`, `mim_number` |
| `OMIM_get_clinical_synopsis` | Clinical features by organ | `operation="get_clinical_synopsis"`, `mim_number` |
| `OMIM_get_gene_map` | Gene-disease mappings | `operation="get_gene_map"`, `mim_number` or `chromosome` |

`OMIM_get_clinical_synopsis` returns features organized by organ system (e.g., `neurologicCentralNervousSystem`, `cardiovascular`).

### DisGeNET Tools

**Requires**: `DISGENET_API_KEY` environment variable (register free at disgenet.org)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `DisGeNET_search_gene` | Diseases for a gene | `operation="search_gene"`, `gene`, `limit` |
| `DisGeNET_search_disease` | Genes for a disease | `operation="search_disease"`, `disease`, `limit` |
| `DisGeNET_get_gda` | Gene-disease associations | `operation="get_gda"`, `gene`/`disease`, `source`, `min_score` |
| `DisGeNET_get_vda` | Variant-disease associations | `operation="get_vda"`, `variant`/`gene`, `limit` |
| `DisGeNET_get_disease_genes` | All genes for disease | `operation="get_disease_genes"`, `disease`, `min_score` |

**DisGeNET Score Interpretation**:
| Score | Interpretation |
|-------|----------------|
| >0.7 | Very Strong — high confidence |
| 0.4–0.7 | Strong — good evidence |
| 0.2–0.4 | Moderate — consider |
| <0.2 | Weak — low confidence |

Use `source="CURATED"` and `min_score=0.3` for high-confidence curated associations.

### ClinGen Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `ClinGen_search_gene_validity` | Gene-disease validity | `gene` |
| `ClinGen_search_dosage_sensitivity` | HI/TS scores | `gene` |
| `ClinGen_search_actionability` | Clinical actionability | `gene` |
| `ClinGen_get_variant_classifications` | Expert variant classifications | `gene`, `variant` |

**ClinGen Validity Classification**:
| Classification | Include in Panel? | Priority |
|----------------|-------------------|----------|
| Definitive | YES — mandatory | Highest |
| Strong | YES — highly recommended | High |
| Moderate | YES | Medium |
| Limited | Include but flag | Low |
| Disputed | Exclude or separate | Avoid |
| Refuted | EXCLUDE | Do not test |
| Not curated | Use other evidence | Variable |

**Dosage Sensitivity Scores** (for CNV interpretation):
| Score | Meaning | ACMG Impact |
|-------|---------|-------------|
| 3 | Sufficient evidence | PVS1 for LOF deletions |
| 2 | Emerging evidence | PM1 |
| 1 | Little evidence | Weak support |
| 0/40 | None/Unlikely | No dosage sensitivity |

### OpenTargets Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `OpenTargets_get_disease_info_by_efoId` | Disease details | `efoId` |
| `OpenTargets_get_disease_associated_targets` | Genes for disease | `efoId` |
| `OpenTargets_get_associated_diseases_by_target_ensemblId` | Diseases for gene | `ensemblId` |

---

## Phase 3: Gene Panel

### Gene Information Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `MyGene_query_genes` | Search genes | `q`, `species` |
| `MyGene_get_gene_by_id` | Gene details | `geneid` |
| `ensembl_lookup_gene` | Ensembl gene info | `id`, `species` |

Note: Use `q` not `gene` for `MyGene_query_genes`.

### Expression Validation

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `GTEx_get_median_gene_expression` | Tissue expression (bulk) | `gencode_id` (versioned, e.g. `ENSG00000166147.15`) |
| `HPA_get_gene_expression` | Protein expression | `ensembl_id` |
| `CELLxGENE_get_expression_data` | Cell-type specific expression | `gene`, `tissue` |
| `CELLxGENE_get_cell_metadata` | Cell type annotations | `gene` |

### Constraint Scores

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `gnomAD_get_gene_constraints` | pLI, LOEUF scores | `gene_symbol` |

### Regulatory Context

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `ChIPAtlas_enrichment_analysis` | TF binding enrichment | `gene`, `cell_type` |
| `ChIPAtlas_get_peak_data` | ChIP-seq peaks | `gene`, `experiment_type` |
| `ENCODE_search_experiments` | Find regulatory experiments | `assay_title`, `biosample` |

### Pathway Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `kegg_search_pathway` | Search KEGG pathways | `query` |
| `kegg_find_genes` | Find gene in KEGG | `query` (e.g. `hsa:FBN1`) |
| `kegg_get_gene_info` | Gene pathway membership | `gene_id` |
| `reactome_search_pathways` | Search Reactome | `query` |
| `reactome_get_pathway` | Pathway details | `pathway_id` |
| `intact_search_interactions` | Protein-protein interactions | `query`, `species` |
| `intact_get_interaction_network` | Network view | `gene`, `depth` |

---

## Phase 4: Variant Interpretation

### ClinVar Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `ClinVar_search_variants` | Search variants | `query` |
| `ClinVar_get_variant_by_id` | Get variant details | `id` (not `variant_id`) |
| `ClinVar_get_variant_classifications` | Classification history | `id` |

### Population Frequency

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `gnomAD_get_variant_frequencies` | Allele frequencies | `variant_id` (format: `1-55505647-G-A`) |
| `gnomAD_get_variant_annotations` | Variant annotations | `variant_id` |

### Pathogenicity Prediction Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `CADD_get_variant_score` | Deleteriousness | `chrom`, `pos`, `ref`, `alt`, `version` |
| `AlphaMissense_get_variant_score` | DeepMind pathogenicity | `uniprot_id`, `variant` (e.g. `E1541K`) |
| `EVE_get_variant_score` | Evolutionary prediction | `chrom`, `pos`, `ref`, `alt` |
| `SpliceAI_predict_splice` | Full splice prediction | `variant` (format: `chr15-48942946-G-A`), `genome` |
| `SpliceAI_get_max_delta` | Quick splice triage | `variant`, `genome` |

**Prediction Thresholds for ACMG PP3/BP4**:
| Tool | Damaging (PP3) | Uncertain | Benign (BP4) |
|------|----------------|-----------|--------------|
| AlphaMissense | >0.564 | 0.34–0.564 | <0.34 |
| CADD PHRED | ≥20 | 15–20 | <15 |
| EVE | >0.5 | — | ≤0.5 |
| SpliceAI max delta | ≥0.5 | 0.2–0.5 | <0.2 |

**SpliceAI Score Components**:
| Score | Meaning |
|-------|---------|
| DS_AG | Acceptor Gain |
| DS_AL | Acceptor Loss |
| DS_DG | Donor Gain |
| DS_DL | Donor Loss |

**SpliceAI ACMG Mapping**:
| Max Delta | ACMG |
|-----------|------|
| ≥0.8 | PP3 (strong) |
| 0.5–0.8 | PP3 (moderate) |
| 0.2–0.5 | PP3 (supporting) |
| <0.2 | BP7 (if synonymous) |

**Multi-predictor Strategy for VUS**:
1. Run AlphaMissense + CADD + EVE for missense variants; SpliceAI for any variant near a splice site.
2. ≥2 concordant damaging results → strong PP3 support.
3. ≥2 concordant benign results → BP4 support.
4. Discordant → weight AlphaMissense highest for missense; SpliceAI highest for splice.

---

## Phase 5: Structure Analysis

### Structure Prediction

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `NvidiaNIM_alphafold2` | High-accuracy structure prediction | `sequence`, `algorithm` (`mmseqs2`), `relax_prediction` |
| `NvidiaNIM_esmfold` | Fast structure prediction | `sequence` |

**Requires**: `NVIDIA_API_KEY` environment variable. Rate limit: 40 RPM. AlphaFold2 may return HTTP 202 (accepted/pending); the tool handles polling internally.

### Domain Annotation

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `InterPro_get_protein_domains` | Domain architecture | `accession` (UniProt ID) |
| `UniProt_get_protein_features` | Sequence features | `accession` |
| `Pfam_get_domains` | Pfam domains | `uniprot_id` |

---

## Phase 6: Literature Evidence

### Literature Search Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `PubMed_search_articles` | Published literature | `query`, `limit` |
| `PubMed_get_article` | Article by PMID | `pmid` |
| `EuropePMC_search_articles` | Preprints (bioRxiv/medRxiv) | `query`, `source="PPR"`, `pageSize` |
| `BioRxiv_get_preprint` | Full preprint metadata | `doi` (must start with `10.1101/`) |
| `openalex_search_works` | Citation analysis | `query`, `limit` |
| `SemanticScholar_search_papers` | AI-ranked search | `query`, `limit` |
| `ArXiv_search_papers` | ArXiv preprints | `query`, `category`, `limit` |

Note: bioRxiv/medRxiv have no public search API. Use `EuropePMC_search_articles` with `source="PPR"` to find preprints.

---

## Fallback Chains

### Disease Matching
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `Orphanet_search_diseases` | `OMIM_search` | `DisGeNET_search_disease` |
| `Orphanet_get_genes` | `OMIM_get_gene_map` | `DisGeNET_get_disease_genes` |
| `OMIM_get_clinical_synopsis` | `Orphanet_get_disease` | `OpenTargets` |
| `DisGeNET_search_gene` | `OpenTargets_diseases` | PubMed phenotype search |

### Expression & Regulatory
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `CELLxGENE_get_expression_data` | `GTEx_get_median_gene_expression` | `HPA_get_gene_expression` |
| `ChIPAtlas_enrichment_analysis` | `ENCODE_search_experiments` | Literature search |

### Pathway Analysis
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `kegg_get_gene_info` | `reactome_search_pathways` | `OpenTargets_pathways` |
| `intact_search_interactions` | `STRING_interactions` | Literature search |

### Variant Annotation
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `ClinVar_get_variant` | `gnomAD_get_variant` | Literature search |
| `gnomAD_get_variant_frequencies` | `ExAC_frequencies` | 1000 Genomes |

### Pathogenicity Prediction
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `AlphaMissense_get_variant_score` | `CADD_get_variant_score` | `EVE_get_variant_score` |
| `SpliceAI_predict_splice` | `SpliceAI_get_max_delta` | VEP annotation |

### Structure Prediction
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `NvidiaNIM_alphafold2` | `alphafold_get_prediction` | `NvidiaNIM_esmfold` |
| `InterPro_get_protein_domains` | `Pfam_get_domains` | `UniProt_features` |

### Literature
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `PubMed_search_articles` | `EuropePMC_search_articles` | `SemanticScholar_search_papers` |
| `EuropePMC_search_articles` (source='PPR') | web search (site:biorxiv.org) | Skip preprints |
| `openalex_search_works` | `Crossref_search_works` | PubMed |
