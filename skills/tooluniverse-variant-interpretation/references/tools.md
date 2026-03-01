# Variant Interpretation - Tool Reference

Detailed parameter tables and score thresholds for all tools used in the variant interpretation workflow.
For workflow steps and decision logic, see `../SKILL.md`. For tool gotchas, see the "Known Gotchas" section in `../SKILL.md`.

---

## Phase 1: Variant Identity

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `myvariant_query` | Aggregated annotations (ClinVar, gnomAD, CADD, dbNSFP) | `variant_id` (HGVS or rsID), `fields` |
| `Ensembl_get_variant_info` | VEP data: consequence, SIFT, PolyPhen | `variant_id` (rsID or HGVS) |
| `NCBI_gene_search` | Gene details | `query` (gene symbol) |

---

## Phase 2: Clinical Databases

### ClinVar

| Tool | Key Parameters |
|------|----------------|
| `clinvar_search` | `variant` (HGVS), `gene` |
| `clinvar_get_variant` | `variation_id` (VCV ID) |

**Review Status Stars**:
| Stars | Status |
|-------|--------|
| 4 | Expert panel / Practice guideline |
| 3 | Multiple submitters, criteria provided |
| 2 | Single submitter, criteria provided |
| 1 | Single submitter, no criteria |

### gnomAD

| Tool | Key Parameters |
|------|----------------|
| `gnomad_search` | `variant` (chr-pos-ref-alt format, e.g., `17-41245466-A-G`), `dataset` |

**Frequency Thresholds (rare disease)**:
| Frequency | ACMG Code |
|-----------|-----------|
| >5% | BA1 (stand-alone benign) |
| >1% | BS1 (strong benign) |
| Absent | PM2_Supporting (pathogenic) |

**Ancestry Codes**: `nfe`, `fin`, `afr`, `amr`, `eas`, `sas`, `asj`

### OMIM

**Requires**: `OMIM_API_KEY` environment variable.

| Tool | Key Parameters |
|------|----------------|
| `OMIM_search` | `operation="search"`, `query`, `limit` |
| `OMIM_get_entry` | `operation="get_entry"`, `mim_number` |
| `OMIM_get_clinical_synopsis` | `operation="get_clinical_synopsis"`, `mim_number` |
| `OMIM_get_gene_map` | `operation="get_gene_map"`, `mim_number` |

### ClinGen

| Tool | Key Parameters |
|------|----------------|
| `ClinGen_search_gene_validity` | `gene` |
| `ClinGen_get_gene_validity` | `gene` (optional filter) |
| `ClinGen_search_dosage_sensitivity` | `gene` |
| `ClinGen_get_dosage_sensitivity` | `gene`, `include_regions` |
| `ClinGen_search_actionability` | `gene` |
| `ClinGen_get_actionability_adult` | `gene` (optional) |
| `ClinGen_get_actionability_pediatric` | `gene` (optional) |

**Validity Levels**:
| Level | ACMG Impact |
|-------|-------------|
| Definitive | Supports PS4, PP4 strongly |
| Strong | Supports PP4 |
| Moderate | Supports PP4 (weak) |
| Limited | Do not apply PP4 |
| Disputed / Refuted | Do not classify using this gene-disease pair |

**Dosage Scores** (for CNV interpretation):
| Score | Meaning |
|-------|---------|
| 3 | Haploinsufficiency/triplosensitivity established |
| 2 | Emerging evidence |
| 1 | Little evidence |
| 0 | No evidence |

### COSMIC (somatic context)

| Tool | Key Parameters |
|------|----------------|
| `COSMIC_search_mutations` | `operation="search"`, `terms` (e.g., `"BRAF V600E"`), `max_results`, `genome_build` |
| `COSMIC_get_mutations_by_gene` | `operation="get_by_gene"`, `gene`, `max_results` |

**Somatic Evidence for ACMG**:
| COSMIC Finding | ACMG Code |
|----------------|-----------|
| Recurrent hotspot (>100 samples) | PS3 (functional evidence) |
| Moderate frequency (10-100 samples) | PM1 (hotspot) |
| Rare (<10 samples) | No support |

### DisGeNET

**Requires**: `DISGENET_API_KEY` environment variable.

| Tool | Key Parameters |
|------|----------------|
| `DisGeNET_search_gene` | `operation="search_gene"`, `gene`, `limit` |
| `DisGeNET_get_gda` | `operation="get_gda"`, `gene`, `source="CURATED"`, `min_score` |
| `DisGeNET_get_vda` | `operation="get_vda"`, `variant` (rsID) or `gene` |

**Score to ACMG Mapping**:
| GDA Score | ACMG Support |
|-----------|--------------|
| >0.7 | PP4 (phenotype specific) |
| 0.4-0.7 | Supporting |
| <0.4 | Insufficient |

### SpliceAI

| Tool | Key Parameters |
|------|----------------|
| `SpliceAI_predict_splice` | `variant` (chr-pos-ref-alt or chr:pos:ref:alt), `genome` ("38" or "37"), `distance`, `mask` |
| `SpliceAI_get_max_delta` | `variant`, `genome` |
| `SpliceAI_predict_pangolin` | `variant`, `genome` |

**Delta Score Types**: DS_AG (acceptor gain), DS_AL (acceptor loss), DS_DG (donor gain), DS_DL (donor loss)

**Thresholds**:
| Max Delta Score | ACMG Support |
|-----------------|--------------|
| ≥0.8 | PP3 (strong splice impact) |
| 0.5-0.8 | PP3 (supporting) |
| 0.2-0.5 | PP3 (weak) |
| <0.2 | BP7 (if synonymous) |

---

## Phase 2.5: Regulatory Context

| Tool | Key Parameters |
|------|----------------|
| `ChIPAtlas_enrichment_analysis` | `gene`, `cell_type` |
| `ChIPAtlas_get_peak_data` | `gene`, `experiment_type` ("TF") |
| `ChIPAtlas_search_datasets` | `antigen`, `cell_type` |
| `ENCODE_search_experiments` | `assay_title` (e.g., "ATAC-seq"), `biosample` |
| `ENCODE_get_experiment` | `accession` |

**Key ENCODE Assays**: ATAC-seq (open chromatin), H3K27ac (active enhancers), H3K4me3 (active promoters), CTCF (insulator binding)

---

## Phase 3: Computational Predictions

| Tool | Key Parameters | Score Range |
|------|----------------|-------------|
| `CADD_get_variant_score` | `chrom`, `pos`, `ref`, `alt`, `version` ("GRCh38-v1.7") | PHRED 0-99 |
| `CADD_get_position_scores` | `chrom`, `pos` | PHRED 0-99 |
| `AlphaMissense_get_variant_score` | `uniprot_id`, `variant` (e.g., "L858R") | 0-1 |
| `AlphaMissense_get_residue_scores` | `uniprot_id`, `position` | 0-1 |
| `EVE_get_variant_score` | `chrom`, `pos`, `ref`, `alt` OR `variant` (HGVS) | 0-1 |
| `EVE_get_gene_info` | `gene_symbol` (check coverage first) | — |

**Score Thresholds**:
| Predictor | Damaging | Uncertain | Benign |
|-----------|----------|-----------|--------|
| AlphaMissense | >0.564 | 0.34-0.564 | <0.34 |
| CADD PHRED | ≥20 | 15-20 | <15 |
| EVE | >0.5 | — | ≤0.5 |
| SIFT | <0.05 | 0.05-0.15 | >0.15 |
| PolyPhen-2 | >0.85 | 0.15-0.85 | <0.15 |
| REVEL | >0.75 | 0.5-0.75 | <0.5 |

**PP3/BP4 Concordance Rule**: Apply PP3 (or BP4) only when ≥2 predictors agree and none disagree.

**Recommended priority**: AlphaMissense (highest accuracy ~90%) > CADD (all variant types) > EVE (unsupervised, complements AM) > SIFT/PolyPhen (legacy, for context)

---

## Phase 4: Structural Analysis

| Tool | Key Parameters |
|------|----------------|
| `PDB_search_by_uniprot` | `uniprot_id` |
| `PDB_get_structure` | `pdb_id` |
| `alphafold_get_prediction` | `accession` (UniProt ID) |
| `NvidiaNIM_alphafold2` | `sequence` (protein sequence), `algorithm` ("mmseqs2") |
| `InterPro_get_protein_domains` | `accession` (UniProt ID) |
| `UniProt_get_protein_function` | `accession` (UniProt ID) |
| `UniProt_get_protein_sequence` | `accession` (UniProt ID) |

**pLDDT Confidence**:
| Score | Reliability for Variant Assessment |
|-------|------------------------------------|
| >90 | Very high — reliable position |
| 70-90 | High — reliable |
| 50-70 | Moderate — use with caution |
| <50 | Low — likely disordered |

**Structural Impact → ACMG**:
| Impact | Description | Code |
|--------|-------------|------|
| Critical | Active site / catalytic residue | PM1 (strong) |
| High | Buried residue, disulfide, structural core | PM1 (moderate) |
| Moderate | Domain interface, binding site | PM1 (supporting) |
| Low | Surface / flexible region | No support |

**NVIDIA NIM Rate Limit**: 40 RPM — add delays between structure prediction calls.

---

## Phase 4.5: Expression Context

| Tool | Key Parameters |
|------|----------------|
| `CELLxGENE_get_expression_data` | `gene`, `tissue` |
| `CELLxGENE_get_cell_metadata` | `gene` |
| `GTEx_get_median_gene_expression` | `gene` |

---

## Phase 5: Literature

| Tool | Key Parameters |
|------|----------------|
| `PubMed_search` | `query`, `max_results` |
| `PubMed_get_abstract` | `pmid` |
| `EuropePMC_search_articles` | `query`, `source` ("PPR" for preprints only), `pageSize` |
| `BioRxiv_get_preprint` | `doi` |
| `openalex_search_works` | `query`, `limit` |
| `SemanticScholar_search_papers` | `query`, `limit` |

**Search Query Patterns**:
| Goal | Query |
|------|-------|
| Specific variant | `"{GENE}" AND ("{HGVS_p}" OR "{AA_change}")` |
| Functional studies | `"{GENE}" AND (functional OR mutagenesis)` |
| Clinical reports | `"{GENE}" AND (case report OR patient) AND "{phenotype}"` |
| Preprints (via EuropePMC) | same query with `source="PPR"` |

**Rate Limits**: PubMed 3 req/sec, Ensembl 15 req/sec.

---

## Fallback Chains

| Task | Primary | Fallback 1 | Fallback 2 |
|------|---------|------------|------------|
| Variant annotation | `myvariant_query` | `clinvar_search` + `gnomad_search` | Direct database queries |
| Protein structure | `PDB_search_by_uniprot` | `alphafold_get_prediction` | `NvidiaNIM_alphafold2` |
| Gene information | `OMIM_search` | `NCBI_gene_search` | `Ensembl_get_gene_info` |
| Literature | `PubMed_search` | `EuropePMC_search_articles` | — |

---

## Common Parameter Mistakes

| Tool | Wrong | Correct |
|------|-------|---------|
| `myvariant_query` | `id="rs123"` | `variant_id="rs123"` |
| `clinvar_search` | `gene="BRCA1:c.123"` | `variant="NM_007294.4:c.123A>G"` |
| `gnomad_search` | `variant="c.123A>G"` | `variant="17-41245466-A-G"` (chr-pos-ref-alt) |
| `alphafold_get_prediction` | `uniprot="P04637"` | `accession="P04637"` |
| `EVE_get_variant_score` | any call without checking coverage | call `EVE_get_gene_info` first |
