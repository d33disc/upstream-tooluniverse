---
name: tooluniverse-multi-omics-integration
description: Integrate and analyze multiple omics datasets (transcriptomics, proteomics, epigenomics, genomics, metabolomics) for systems biology and precision medicine. Performs cross-omics correlation, multi-omics clustering (MOFA+, NMF), pathway-level integration, and sample matching. Coordinates ToolUniverse skills for expression data (RNA-seq), epigenomics (methylation, ChIP-seq), variants (SNVs, CNVs), protein interactions, and pathway enrichment. Use when analyzing multi-omics datasets, performing integrative analysis, discovering multi-omics biomarkers, studying disease mechanisms across molecular layers, or conducting systems biology research that requires coordinated analysis of transcriptome, genome, epigenome, proteome, and metabolome data.
---

# Multi-Omics Integration

Coordinate and integrate multiple omics datasets for comprehensive systems biology analysis. This skill orchestrates specialized ToolUniverse skills and MCP tools to perform cross-omics correlation, multi-omics clustering, pathway-level integration, and unified interpretation across molecular layers.

**Tool calls in this skill use the MCP interface**:
```
mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})
```

---

## When to Use This Skill

**Triggers**:
- User has multiple omics datasets (RNA-seq + proteomics, methylation + expression, etc.)
- Requests for integrative multi-omics analysis
- Cross-omics correlation queries (e.g., "How does methylation affect expression?")
- Multi-omics biomarker discovery
- Systems biology questions requiring multiple molecular layers
- Precision medicine applications with multi-omics patient data
- Questions about molecular mechanisms across omics types

**Example questions this skill solves**:
1. "Integrate RNA-seq and proteomics data to find genes with concordant changes"
2. "How does promoter methylation correlate with gene expression?"
3. "Perform multi-omics clustering to identify patient subtypes"
4. "Which pathways are dysregulated across transcriptome, proteome, and metabolome?"
5. "Find multi-omics biomarkers for disease classification"
6. "Correlate CNV with gene expression to identify dosage effects"
7. "Integrate GWAS variants, eQTLs, and expression data"
8. "Perform MOFA+ analysis on multi-omics cancer data"

---

## Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Data Integration** | Match samples across omics, handle missing data, normalize scales |
| **Cross-Omics Correlation** | Correlate features across molecular layers (expression vs protein, methylation vs expression) |
| **Multi-Omics Clustering** | MOFA+, NMF, joint clustering to identify omics-driven subtypes |
| **Pathway Integration** | Combine omics evidence at pathway level for unified biological interpretation |
| **Biomarker Discovery** | Identify multi-omics signatures with improved predictive power |
| **Skill Coordination** | Orchestrate RNA-seq, epigenomics, variant-analysis, protein-interactions, gene-enrichment skills |

---

## Workflow Overview

```
Input: Multiple Omics Datasets
    |
    v
Phase 1: Data Loading & QC
    |-- Load each omics type (RNA-seq, proteomics, methylation, CNV, metabolomics)
    |-- Quality control per omics type
    |-- Normalize values to comparable scales
    |
    v
Phase 2: Sample Matching & Harmonization
    |-- Match sample IDs across omics
    |-- Identify common samples (intersection)
    |-- Document sample availability matrix
    |
    v
Phase 3: Feature Mapping
    |-- Map all features to gene-level identifiers
    |-- CpG → gene (promoter/gene body annotation)
    |-- CNV regions → overlapping genes
    |-- Metabolites → enzyme genes
    |
    v
Phase 4: Cross-Omics Correlation
    |-- RNA vs protein (translation efficiency)
    |-- Promoter methylation vs expression (epigenetic regulation)
    |-- CNV vs expression (gene dosage effect)
    |-- eQTL variants vs expression (genetic regulation)
    |-- Metabolite vs enzyme expression (metabolic flux)
    |
    v
Phase 5: Multi-Omics Clustering
    |-- MOFA+ for latent factors across omics
    |-- NMF or SNF for patient subtype discovery
    |-- Characterize per-subtype omics profiles
    |
    v
Phase 6: Pathway-Level Integration
    |-- Pool dysregulated genes from all omics layers
    |-- Run enrichment (Reactome, KEGG, GO) via ToolUniverse tools
    |-- Score each pathway by multi-omics evidence weight
    |
    v
Phase 7: Biomarker Discovery
    |-- Feature selection per omics layer
    |-- Combine and cross-validate multi-omics signatures
    |-- Report top biomarkers with per-layer evidence
    |
    v
Phase 8: Generate Integrated Report
    |-- Summary statistics per omics
    |-- Cross-omics correlation findings
    |-- Multi-omics cluster/subtype description
    |-- Top dysregulated pathways with evidence scores
    |-- Multi-omics biomarkers with AUC
    |-- Biological interpretation
```

---

## Phase Details

### Phase 1: Data Loading & Quality Control

**Supported omics types and formats**:

| Omics | Common Formats | Key QC Steps |
|-------|---------------|--------------|
| Transcriptomics | CSV/TSV count matrices, HDF5, AnnData (.h5ad) | Filter low-count genes, normalize (TPM/DESeq2), log-transform |
| Proteomics | MaxQuant, Spectronaut, DIA-NN output | Filter high-missingness proteins, impute (KNN/minimum), median-normalize |
| Epigenomics | IDAT, beta value matrices, peak BED files | Remove failed probes, filter cross-reactive probes, batch-correct (ComBat) |
| Genomics | VCF (SNV), SEG files (CNV) | Use variant-analysis skill for VCF QC; validate CNV segmentation |
| Metabolomics | Peak tables, identified metabolite tables | Filter low-abundance features, log-transform, scale |

For RNA-seq loading and DESeq2 normalization, delegate to the `tooluniverse-rnaseq-deseq2` skill. For methylation QC and ChIP-seq peak handling, delegate to the `tooluniverse-epigenomics` skill. For CNV/SNV QC, delegate to `tooluniverse-variant-analysis`.

---

### Phase 2: Sample Matching & Harmonization

**Objective**: Identify the common set of samples present across all omics datasets and harmonize sample IDs.

Steps:
1. Extract sample IDs from each omics matrix (columns for samples-as-columns format).
2. Compute the intersection of sample IDs across all omics types.
3. Subset each matrix to the common samples, sorted consistently.
4. For missing omics in a subset of samples, document a sample-availability matrix and proceed with pairwise integration where applicable.
5. Apply batch correction if samples come from different processing batches (e.g., run ComBat on each omics layer independently before merging).

Common pitfalls:
- Sample ID format differences (e.g., `TCGA-01-A` vs `TCGA.01.A`) — normalize separators before matching.
- Tumor vs normal mismatch in TCGA data — ensure the same sample type is used across omics.

---

### Phase 3: Feature Mapping

**Objective**: Map features from different omics layers to a shared gene-level namespace.

| Source Omics | Feature Type | Mapping Strategy |
|-------------|-------------|-----------------|
| RNA-seq | Gene symbol / Ensembl ID | Already gene-level; convert IDs if needed |
| Proteomics | UniProt / protein name | Map to gene symbol via UniProt API or STRING |
| Methylation | CpG probe ID | Map to gene: promoter = TSS ± 2 kb; gene body = within gene boundaries; average beta per gene |
| CNV | Genomic segment (chr:start-end) | Intersect segments with gene coordinates; report log2 ratio per gene |
| Metabolomics | Metabolite name / HMDB ID | Map to enzyme gene via metabolite-reaction-enzyme databases (HMDB, KEGG) |

Use `mcp__tooluniverse__execute_tool` with identifier-conversion tools (e.g., Ensembl, UniProt, MyGene.info) to resolve cross-database IDs. See [references/tools.md](references/tools.md) for available ToolUniverse tools and their parameters.

---

### Phase 4: Cross-Omics Correlation

**Objective**: Quantify relationships between molecular layers to reveal regulatory mechanisms.

#### 4.1: Expression vs Protein (Translation Efficiency)

For each gene present in both RNA-seq and proteomics matrices (matched samples):
- Compute Spearman correlation between mRNA and protein abundance across samples.
- Typical expectation: r ≈ 0.4–0.6. Lower values indicate post-transcriptional regulation.
- Flag genes with |r| < 0.2 as discordant (candidates for miRNA regulation, protein stability, etc.).

#### 4.2: Promoter Methylation vs Expression (Epigenetic Regulation)

For each gene with mapped promoter methylation values:
- Compute Spearman correlation between average promoter beta value and expression.
- Typical expectation: negative correlation (methylation represses expression).
- Flag genes with r < −0.5 and p < 0.01 as epigenetically regulated.
- Direction label: r < 0 → "repressive", r > 0 → "activating" (gene-body context).

#### 4.3: CNV vs Expression (Gene Dosage Effect)

For each gene with both CNV (log2 ratio) and expression data:
- Compute Pearson correlation between copy number and expression across samples.
- Typical expectation: positive correlation (amplification drives increased expression).
- Flag genes with r > 0.5 and p < 0.01 as dosage-sensitive.
- Distinguish CNV-driven from expression-only changes in downstream analysis.

#### 4.4: eQTL / Variant vs Expression

For GWAS SNPs or candidate variants:
- For each variant, test association with expression of cis genes (within 1 Mb).
- If methylation data is available, test SNP → CpG methylation (meQTL) and CpG → expression chains.
- Report variant → methylation → expression regulatory triples.

Use enrichment and annotation tools via `mcp__tooluniverse__execute_tool` to annotate identified regulatory genes. See [references/tools.md](references/tools.md) for enrichment tool parameters.

---

### Phase 5: Multi-Omics Clustering

**Objective**: Identify patient or sample subtypes driven by integrated omics variation.

#### Method 1: MOFA+ (Multi-Omics Factor Analysis)

MOFA+ decomposes multiple omics matrices into shared latent factors. Each factor captures a source of variation and its contribution to each omics layer.

Workflow:
1. Prepare one matrix per omics type (samples × features), normalized and scaled.
2. Run MOFA+ (R: `MOFA2` package, or Python: `mofapy2`) with desired number of factors (start with 10–15).
3. Inspect variance explained per factor per omics. Assign biological labels to top factors.
4. Cluster samples using factor scores (k-means, hierarchical, or UMAP + DBSCAN).
5. Characterize each cluster by top feature weights per factor and per omics.

Example factor interpretation:
- Factor 1 explains 40% variance in RNA-seq and 30% in proteomics → likely cell proliferation axis.
- Factor 2 explains 50% variance in methylation → epigenetic subtype.
- Factor 3 explains 20% variance in CNV → genomic instability subtype.

#### Method 2: Joint NMF (Non-negative Matrix Factorization)

Concatenate normalized omics matrices vertically (features × samples) after ensuring all values are non-negative. Run NMF to obtain sample coefficient matrix H. Cluster samples by their NMF component weights. Choose rank k by cophenetic correlation or gap statistic.

#### Method 3: Similarity Network Fusion (SNF)

Construct a per-omics patient similarity network (Gaussian kernel on feature distances). Fuse networks iteratively using the SNF algorithm. Cluster the fused network (spectral clustering). SNF is robust to noise and missing omics per sample.

For all methods: report cluster-defining features per omics, clinical variable associations per cluster, and survival or outcome differences if available.

---

### Phase 6: Pathway-Level Integration

**Objective**: Aggregate multi-omics evidence at the pathway level to identify key dysregulated biological processes.

Steps:
1. Pool dysregulated genes from all omics layers into a unified gene set (union of DEGs, differential proteins, methylation-regulated genes, dosage-effect genes).
2. Run pathway enrichment using ToolUniverse tools via `mcp__tooluniverse__execute_tool`.
3. For each returned pathway, compute a multi-omics evidence score: sum the absolute effect sizes (fold change, correlation, beta difference) for pathway genes across all omics layers, normalized by the number of layers with evidence. Prioritize pathways supported by 3+ omics layers.
4. Report top pathways ranked by multi-omics score with per-layer supporting gene counts.

Available enrichment tools (call via `mcp__tooluniverse__execute_tool`):

| Tool Name | Database | Use When |
|-----------|----------|---------|
| `enrichr_enrich` | 220+ Enrichr libraries | ORA on a gene list; specify `library` (e.g., `KEGG_2021_Human`) |
| `reactome_pathway_analysis` | Reactome | Pathway hierarchy and reaction-level detail |
| `string_enrichment` | STRING functional enrichment | Combined PPI + pathway evidence |
| `panther_enrichment` | PANTHER | GO enrichment with PANTHER gene function |

See [references/tools.md](references/tools.md) for full parameter details on each tool.

---

### Phase 7: Biomarker Discovery

**Objective**: Identify a compact multi-omics feature signature for disease classification or stratification.

Steps:
1. Per omics layer, select top candidate features using univariate association tests against the outcome label (ANOVA F-score, Mann-Whitney U, or correlation with a continuous outcome). Keep top k features per layer (e.g., k = 15–30).
2. Concatenate selected features from all layers into a combined feature matrix.
3. Train a classification model (Random Forest or logistic regression with elastic-net regularization) using 5-fold cross-validation. Report mean AUC ± SD.
4. Compute per-feature importance. Report the top 10–20 multi-omics biomarkers with their omics of origin.
5. Validate top biomarkers using ToolUniverse annotation tools (literature support, protein databases, drug targetability).

Minimum standards:
- At least 10 samples per class for reliable CV performance.
- Report both single-omics AUC baselines and multi-omics combined AUC for comparison.
- Flag overfitting risk if n_samples < 3 × n_features.

---

### Phase 8: Integrated Reporting

Generate a structured multi-omics report covering:

**Dataset Summary**: Omics types loaded, sample counts per omics, common sample count, feature counts per layer.

**Cross-Omics Correlations**:
- RNA-protein: overall Spearman r, % concordant genes, n discordant candidates.
- Methylation-expression: median anticorrelation r, n epigenetically regulated genes, examples.
- CNV-expression: n dosage-sensitive genes, examples with amplification/expression concordance.

**Multi-Omics Clustering**:
- Method used, number of clusters, samples per cluster.
- Top defining features per cluster per omics layer.
- MOFA+ factors: % variance explained, biological annotation.

**Pathway Integration**:
- Top 10 pathways by multi-omics score.
- Per-pathway: omics layers contributing, n supporting genes, adjusted p-value.

**Multi-Omics Biomarkers**:
- Model AUC (multi-omics) vs per-layer AUC baselines.
- Top biomarkers with omics origin, effect size, and biological annotation.

**Biological Interpretation**:
- Narrative summary of key findings.
- Mechanistic hypotheses linking molecular layers.
- Clinical or therapeutic implications.

---

## ToolUniverse Skills Coordination

This skill orchestrates multiple specialized skills. Delegate sub-tasks as follows:

| Skill | Used For | Phase |
|-------|----------|-------|
| `tooluniverse-rnaseq-deseq2` | Load and normalize RNA-seq data, identify DEGs | 1, 4 |
| `tooluniverse-epigenomics` | Methylation QC, CpG annotation, ChIP-seq peaks | 1, 3, 4 |
| `tooluniverse-variant-analysis` | CNV and SNV QC, gene-level copy number | 1, 3, 4 |
| `tooluniverse-protein-interactions` | PPI network context for integration hubs | 6 |
| `tooluniverse-gene-enrichment` | Pathway and GO enrichment | 6 |
| `tooluniverse-expression-data-retrieval` | Retrieve public omics datasets | 1 |
| `tooluniverse-target-research` | Gene/protein annotation, drug targetability | 3, 8 |
| `tooluniverse-metabolomics-analysis` | Metabolite identification and pathway mapping | 1, 3 |

---

## Abbreviated Tool Reference

Full parameter tables are in [references/tools.md](references/tools.md). Key tools used across phases:

| Tool | Phase | Purpose |
|------|-------|---------|
| `enrichr_enrich` | 6 | Pathway ORA on pooled dysregulated genes |
| `reactome_pathway_analysis` | 6 | Reactome hierarchy enrichment |
| `string_enrichment` | 6 | PPI-informed functional enrichment |
| `uniprot_search` | 3 | Protein → gene symbol mapping |
| `mygene_query` | 3 | Gene ID conversion (Ensembl ↔ symbol ↔ Entrez) |
| `ensembl_gene_lookup` | 3 | Genomic coordinates for CpG-to-gene mapping |
| `opentargets_gene` | 8 | Gene–disease associations for biomarker validation |
| `string_network` | 6, 8 | PPI context for integration hubs |

---

## Example Use Cases

### Use Case 1: Cancer Multi-Omics (TCGA)

**Question**: "Integrate TCGA breast cancer RNA-seq, proteomics, methylation, and CNV data"

Workflow summary:
1. Load 4 omics layers for all available samples.
2. Harmonize sample IDs; identify common samples across all 4 layers.
3. Correlate RNA-protein to find translation-regulated genes.
4. Correlate promoter methylation-expression to find epigenetically silenced genes.
5. Correlate CNV-expression to find dosage-sensitive driver genes.
6. Run MOFA+ to identify latent factors. Cluster into subtypes.
7. Run pathway enrichment per subtype using `mcp__tooluniverse__execute_tool(tool_name="reactome_pathway_analysis", ...)`.
8. Select multi-omics biomarkers and validate with OpenTargets.

### Use Case 2: eQTL + Methylation + Expression

**Question**: "How do GWAS variants affect gene expression through methylation?"

Workflow summary:
1. Load genotype (SNP), RNA-seq expression, and methylation data for the same samples.
2. For each GWAS variant: test cis-eQTL (SNP → expression) and meQTL (SNP → CpG methylation).
3. For significant meQTLs, test whether the affected CpG methylation also correlates with gene expression.
4. Report SNP → methylation → expression regulatory chains with effect sizes.
5. Annotate GWAS traits using `mcp__tooluniverse__execute_tool(tool_name="gwas_catalog_search", ...)`.

### Use Case 3: Drug Response Multi-Omics

**Question**: "Predict drug response using multi-omics profiles"

Workflow summary:
1. Load baseline multi-omics (pre-treatment) and drug response labels (IC50 or clinical response).
2. Correlate each omics layer independently with response; document single-layer predictive power.
3. Select top predictive features per layer.
4. Combine into multi-omics classifier; compare AUC against single-layer baselines.
5. Run pathway enrichment on response-associated features.
6. Annotate resistance/sensitivity pathways with drug targets using ToolUniverse.

---

## Data Harmonization Details

### Normalization Before Cross-Omics Correlation

Each omics layer requires appropriate normalization before correlation or clustering:

- **RNA-seq**: Use log2(TPM + 1) or variance-stabilizing transform (VST from DESeq2). Do not use raw counts.
- **Proteomics**: Median-center each sample (log-scale). Impute missing values before normalization.
- **Methylation**: Beta values (0–1) are interpretable as-is. M-values (logit-transform of beta) are preferable for statistical tests.
- **CNV**: Use segmented log2 ratio. Center at zero (diploid = 0). Threshold extreme values (cap at ±3).
- **Metabolomics**: Log-transform + autoscaling (z-score per feature). Remove features with >30% missing.

### Batch Effect Correction

Apply within each omics layer independently before cross-omics analysis:
- Use ComBat (parametric or non-parametric) for known batch variables.
- For unknown batch effects, use SVA (surrogate variable analysis) and regress out top SVs.
- Document batch variables corrected per layer in the report.

---

## Known Gotchas

1. **Sample ID format mismatch**: TCGA sample IDs differ by separator character (`-` vs `.`) across omics files. Always normalize sample ID format before computing intersection — otherwise the common set appears empty when all samples are actually present.

2. **Methylation direction depends on context**: Promoter methylation anticorrelates with expression (repressive). Gene body methylation can positively correlate with expression (elongation-related). Always annotate CpGs by region type before interpreting correlations as "epigenetic regulation."

3. **CNV log2 ratio is relative, not absolute**: A log2 ratio of 0 means diploid (2 copies), not absence. Amplifications are log2 > 0.6 (approx. 3+ copies), deletions are log2 < −1 (hemizygous). Do not threshold at 0.

4. **MOFA+ requires pre-filtered features**: Running MOFA+ on the full feature space (e.g., all 20,000 genes) is computationally expensive and degrades factor quality. Pre-filter to high-variance features per layer (e.g., top 5,000 by median absolute deviation) before passing to MOFA+.

5. **Pooled gene set for enrichment inflates results**: Combining all dysregulated genes from all omics layers into one enrichment analysis can produce high-scoring generic terms (e.g., "metabolic process"). Prefer per-layer enrichment first, then compute multi-omics overlap at the pathway level for specificity.

6. **Missing omics for some samples**: When not all samples have all omics types, avoid silently dropping samples. Use pairwise integration for each omics pair on their shared samples, and document which pairs were analyzed with how many samples.

7. **Protein-to-gene mapping ambiguity**: Multiple proteins can map to the same gene (isoforms, post-translational variants). When averaging per-gene, report the number of proteins aggregated and flag genes with high isoform diversity.

8. **NMF requires non-negative input**: RNA-seq log-normalized values can be negative after mean-centering. Do not mean-center before NMF. Use min-max scaling or shift by the minimum value to ensure non-negativity.

9. **execute_tool argument types**: ToolUniverse tools called via `mcp__tooluniverse__execute_tool` expect `arguments` as a JSON object (`{}`), not a string. Passing gene lists as comma-separated strings vs. JSON arrays depends on the specific tool — check [references/tools.md](references/tools.md) for the correct format per tool.

10. **MOFA+ factor count selection**: Do not default to 10 factors without inspection. Use the elbow of the cumulative variance-explained curve to select the number of informative factors. Over-factoring fragments biological signals across redundant factors.

---

## Quantified Minimums

| Component | Requirement |
|-----------|-------------|
| Omics types | At least 2 omics datasets |
| Common samples | At least 10 samples across all omics layers |
| Cross-correlation | Spearman or Pearson computed with p-value and FDR correction |
| Clustering | At least one method (MOFA+, NMF, or SNF) applied |
| Pathway integration | Enrichment run with multi-omics evidence score computed |
| Report | Dataset summary, correlations, clusters, pathways, biomarkers, interpretation |

---

## Limitations

- **Sample size**: Multi-omics integration requires sufficient samples (n ≥ 20 recommended for clustering; n ≥ 30 for reliable biomarker CV).
- **Missing data**: Patients without complete omics coverage reduce effective sample sizes for integration.
- **Batch effects**: Different omics platforms and processing batches require careful normalization; uncorrected batch effects can dominate latent factors.
- **Computational cost**: Full MOFA+/SNF on large cohorts (n > 200, features > 10K per omics) may require significant memory and time.
- **Interpretation**: Multi-omics results require biological domain expertise for validation and clinical translation.

---

## References

**Methods**:
- MOFA+: https://doi.org/10.1186/s13059-020-02015-1
- Similarity Network Fusion: https://doi.org/10.1038/nmeth.2810
- Multi-omics review: https://doi.org/10.1038/s41576-019-0093-7

**ToolUniverse Tools**: See [references/tools.md](references/tools.md) for full parameter tables.

**Related Skills**: See individual skill documentation for omics-specific methods (tooluniverse-rnaseq-deseq2, tooluniverse-epigenomics, tooluniverse-variant-analysis, tooluniverse-gene-enrichment).
