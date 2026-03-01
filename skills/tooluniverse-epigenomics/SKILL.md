---
name: tooluniverse-epigenomics
description: Production-ready genomics and epigenomics data processing for BixBench questions. Handles methylation array analysis (CpG filtering, differential methylation, age-related CpG detection, chromosome-level density), ChIP-seq peak analysis (peak calling, motif enrichment, coverage stats), ATAC-seq chromatin accessibility, multi-omics integration (expression + methylation correlation), and genome-wide statistics. Pure Python computation (pandas, scipy, numpy, pysam, statsmodels) plus ToolUniverse annotation tools (Ensembl, ENCODE, SCREEN, JASPAR, ReMap, RegulomeDB, ChIPAtlas). Supports BED, BigWig, methylation beta-value matrices, Illumina manifest files, and multi-sample clinical data. Use when processing methylation data, ChIP-seq peaks, ATAC-seq signals, or answering questions about CpG sites, differential methylation, chromatin accessibility, histone marks, or epigenomic statistics.
---

# Genomics and Epigenomics Data Processing

Production-ready computational skill for processing and analyzing epigenomics data. Combines local Python computation (pandas, scipy, numpy, pysam, statsmodels) with ToolUniverse annotation tools for regulatory context. Designed to solve BixBench-style questions about methylation, ChIP-seq, ATAC-seq, and multi-omics integration.

## When to Use This Skill

**Triggers**:
- User provides methylation data (beta-value matrices, Illumina arrays) and asks about CpG sites
- Questions about differential methylation analysis
- Age-related CpG detection or epigenetic clock questions
- Chromosome-level methylation density or statistics
- ChIP-seq peak files (BED format) with analysis questions
- ATAC-seq chromatin accessibility questions
- Multi-omics integration (expression + methylation, expression + ChIP-seq)
- Genome-wide epigenomic statistics
- Questions mentioning "methylation", "CpG", "ChIP-seq", "ATAC-seq", "histone", "chromatin", "epigenetic"
- Questions about missing data across clinical/genomic/epigenomic modalities
- Regulatory element annotation for processed epigenomic data

**Example Questions This Skill Solves**:
1. "How many patients have no missing data for vital status, gene expression, and methylation data?"
2. "What is the ratio of filtered age-related CpG density between chromosomes?"
3. "What is the genome-wide average chromosomal density of unique age-related CpGs per base pair?"
4. "How many CpG sites show significant differential methylation (padj < 0.05)?"
5. "What is the Pearson correlation between methylation and expression for gene X?"
6. "How many ChIP-seq peaks overlap with promoter regions?"
7. "What fraction of ATAC-seq peaks are in enhancer regions?"
8. "Which chromosome has the highest density of hypermethylated CpGs?"
9. "Filter CpG sites by variance > threshold and map to nearest genes"
10. "What is the average beta value difference between tumor and normal for chromosome 17?"

**NOT for** (use other skills instead):
- Gene regulation lookup without data files → use existing epigenomics annotation pattern
- RNA-seq differential expression → use `tooluniverse-rnaseq-deseq2`
- Variant calling/annotation from VCF → use `tooluniverse-variant-analysis`
- Gene enrichment analysis → use `tooluniverse-gene-enrichment`
- Protein structure analysis → use `tooluniverse-protein-structure-retrieval`

---

## Key Principles

1. **Data-first** — Load and inspect all data files before any analysis
2. **Question-driven** — Parse what is actually being asked; extract the specific numeric answer
3. **File format detection** — Identify methylation arrays, BED files, BigWig, clinical data before loading
4. **Coordinate system awareness** — Track genome build (hg19, hg38, mm10); handle chr-prefix differences
5. **Statistical rigor** — Apply multiple testing correction; document effect size thresholds
6. **Missing data handling** — Explicitly report NaN/missing values; never silently drop
7. **Chromosome normalization** — Normalize names consistently (chr1 vs 1, chrX vs X)
8. **Report-first** — Create output file first, populate progressively
9. **English-first queries** — Use English in all ToolUniverse tool calls

---

## Complete Workflow

### Phase 0: Question Parsing and Data Discovery

**This is the mandatory first step — do not write analysis code before completing it.**

#### 0.1 Discover Available Data Files

Scan the working directory (and subdirectories) and categorize files by type:
- **Methylation**: filenames containing methyl, beta, cpg, illumina, 450k, 850k, epic, mval
- **ChIP-seq**: chip, peak, narrowpeak, broadpeak, histone
- **ATAC-seq**: atac, accessibility, openchromatin, dnase
- **BED/Peak**: extensions `.bed`, `.bed.gz`, `.narrowPeak`, `.broadPeak`
- **BigWig**: extensions `.bw`, `.bigwig`, `.bigWig`
- **Clinical**: clinical, patient, sample, metadata, phenotype, survival
- **Expression**: express, rnaseq, fpkm, tpm, counts, transcriptom
- **Manifest**: manifest, annotation, probe, platform

Print a summary of each category before proceeding.

#### 0.2 Parse Question Parameters

Extract these from the question before writing any code:

| Parameter | Default | Example |
|-----------|---------|---------|
| Significance threshold | 0.05 | "padj < 0.05", "FDR < 0.01" |
| Beta difference threshold | 0 | "\|delta_beta\| > 0.2" |
| Variance filter | None | "variance > 0.01", "top 5000 most variable" |
| Chromosome filter | All | "chromosome 17", "autosomes only" |
| Genome build | hg38 | "hg19", "GRCh37", "mm10" |
| CpG type filter | All | "cg probes only", "exclude ch probes" |
| Region filter | None | "promoter", "gene body", "intergenic" |
| Missing data handling | Report | "complete cases", "no missing data" |
| Comparison groups | Infer | "tumor vs normal", "old vs young" |
| Requested statistic | Infer | "density", "ratio", "count", "average" |

#### 0.3 Decision Tree

```
Type of data?
  METHYLATION -> Phase 1
  CHIP-SEQ    -> Phase 2
  ATAC-SEQ    -> Phase 3
  MULTI-OMICS -> Phase 4
  CLINICAL    -> Phase 5
  ANNOTATION  -> Phase 6

Genome-wide statistics question?
  YES -> Focus on chromosome-level aggregation (Phase 7)
  NO  -> Focus on site/region-level analysis
```

---

### Phase 1: Methylation Data Processing

#### 1.1 Load the methylation matrix

Load the beta-value (or M-value) matrix with probes as rows and samples as columns. Try tab-separated first, then comma-separated. For HDF5 or Parquet files use the corresponding pandas reader.

Detect value type: if all values are in [0, 1] it is a beta-value matrix; otherwise it is an M-value matrix. Convert between them as needed using `M = log2(beta / (1 - beta))`.

#### 1.2 Load the probe manifest

Load the Illumina manifest (450K or EPIC). It may have header rows to skip (try 0, 7, or 8 skiprows until "CHR" or "Name" columns appear). Normalize column names to: `probe_id`, `chr`, `position`, `gene_name`, `gene_group`, `cpg_island_relation`.

Always normalize chromosome names to include the "chr" prefix (e.g., "1" → "chr1").

#### 1.3 Filter CpG probes

Apply filters in this order based on what the question specifies:
1. Probe type — keep `cg` or `ch` probes by checking the probe ID prefix
2. Missing data — remove probes with more than the allowed fraction of NaN values
3. Variance — keep probes above a variance threshold (compute per-probe variance across samples)
4. Top-N most variable — if the question asks for "top N", rank by variance and take top N
5. Chromosome filter — use the manifest to keep only probes on specified chromosomes
6. CpG island relation — filter by Island, Shore, Shelf, or OpenSea using manifest annotation
7. Gene group filter — filter by TSS200, TSS1500, Body, 1stExon using manifest annotation

#### 1.4 Differential methylation

To find differentially methylated CpGs between two groups:
1. Split samples into group1 and group2 using clinical metadata
2. For each probe, run a two-sample t-test (Welch) or Mann-Whitney U test
3. Collect per-probe: mean_g1, mean_g2, delta_beta (= mean_g2 - mean_g1), p-value
4. Apply Benjamini-Hochberg FDR correction (`statsmodels.stats.multitest.multipletests`)
5. Filter significant DMPs: padj < alpha AND |delta_beta| >= threshold
6. Label direction: delta_beta > 0 = hypermethylated, delta_beta < 0 = hypomethylated

Use Wilcoxon/Mann-Whitney when sample sizes are small (< 10 per group) or distributions are skewed.

#### 1.5 Age-related CpG identification

For each probe, compute Pearson (or Spearman) correlation between beta values and sample ages. Apply FDR correction across all probes. Significant probes (padj < 0.05) are age-related CpGs.

Require at least 5 non-NaN paired observations per probe before computing a correlation.

#### 1.6 Chromosome-level CpG density

To calculate CpG density per chromosome:
1. Map each probe in the filtered set to its chromosome using the manifest
2. Count probes per chromosome
3. Divide by chromosome length (use reference lengths from `references/tools.md`)
4. Report density as CpGs per base pair (or per Mb)

For genome-wide average density: sum all CpG counts, divide by sum of all chromosome lengths.
For a density ratio between two chromosomes: divide their per-bp densities.

---

### Phase 2: ChIP-seq Peak Analysis

#### 2.1 Load peak files

Load BED or narrowPeak/broadPeak files as tab-separated DataFrames. Skip lines starting with `track`, `browser`, or `#`. Normalize chromosome names. Parse the correct number of columns:
- Standard BED: up to 12 columns (chrom, start, end, name, score, strand, ...)
- narrowPeak: 10 columns, adds signalValue, pValue, qValue, peak
- broadPeak: 9 columns, adds signalValue, pValue, qValue

Ensure start/end are numeric. Peak length = end - start.

#### 2.2 Annotate peaks to genomic features

To classify peaks as promoter, gene body, proximal, distal, or intergenic:
1. Load or fetch gene annotation (Ensembl coordinates)
2. For each peak midpoint, find the nearest TSS on the same chromosome
3. Classify: distance ≤ 2000 bp from TSS = promoter; within gene body = gene_body; ≤ 10000 bp = proximal; otherwise = distal or intergenic

For gene annotation without a local file, call `ensembl_get_overlap_features` with the region string.

#### 2.3 Peak overlap analysis

To find overlapping peaks between two BED sets:
- Group by chromosome, sort by start, then check pairwise overlap within each chromosome
- Overlap = max(startA, startB) to min(endA, endB); report only if overlap ≥ 1 bp (or specified threshold)
- Jaccard similarity = intersection bp / union bp

---

### Phase 3: ATAC-seq Analysis

Load ATAC-seq peaks (narrowPeak format). All BED operations from Phase 2 apply.

ATAC-seq specific considerations:
- Peaks < 150 bp are nucleosome-free regions (NFR) — open chromatin
- Peaks ≥ 150 bp likely contain a nucleosome
- Report NFR fraction and total peak counts separately
- Chromatin accessibility by region: annotate peaks (Phase 2.2), then count per region type and compute fractions

---

### Phase 4: Multi-Omics Integration

#### 4.1 Methylation-expression correlation

1. Find common samples between the methylation matrix (columns) and expression matrix (columns)
2. Require at least 5 common samples; raise an error if fewer
3. For each probe-gene pair in the probe-gene map (from manifest or provided), compute Pearson or Spearman correlation across common samples
4. Apply FDR correction
5. Anti-correlation (negative r, padj < 0.05) is the biologically expected pattern for promoter methylation silencing expression

#### 4.2 ChIP-seq + expression integration

1. Annotate ChIP-seq peaks to genes (Phase 2.2) using the TSS window
2. Identify genes with promoter peaks
3. Join with expression data to compare expression levels between genes with and without promoter peaks

---

### Phase 5: Clinical Data Integration

#### 5.1 Missing data / complete cases analysis

To answer "how many patients have complete data for X, Y, Z modalities":
1. Extract sample/patient IDs from each data modality (columns for omics matrices; rows or a dedicated ID column for clinical data)
2. For clinical variables, find the set of samples where each variable is non-NaN
3. Compute the intersection of all sample sets
4. Report the count and optionally list the IDs

For TCGA data: barcodes are 28-character strings (TCGA-XX-XXXX-01A); patient IDs are the first 12 characters. Truncate to match across modalities when needed.

---

### Phase 6: ToolUniverse Annotation Integration

Use ToolUniverse tools via `mcp__tooluniverse__execute_tool` for biological annotation of findings. Limit annotation batches to ~20 genes or regions at a time to respect API rate limits.

**Gene annotation workflow:**
1. Call `ensembl_lookup_gene` with `id=<gene_symbol>` and `species="homo_sapiens"` to get coordinates and biotype
2. Call `SCREEN_get_regulatory_elements` with `gene_name=<symbol>` to get nearby cCREs
3. Call `ReMap_get_transcription_factor_binding` for TF binding evidence
4. Optionally call `jaspar_search_matrices` to find motifs for TFs of interest

**Region annotation workflow:**
1. Strip "chr" prefix from chromosome name before passing to Ensembl (e.g., "17:7571720-7590868")
2. Call `ensembl_get_regulatory_features` with `region=<region_str>` and `feature="regulatory"`
3. Call `ENCODE_search_experiments` to find relevant ChIP-seq datasets for the region's histone marks

**ChIP-seq experiment lookup:**
1. Call `ChIPAtlas_get_experiments` with `operation="get_experiment_list"` plus antigen and genome
2. Call `ENCODE_search_experiments` with `assay_title="ChIP-seq"` and `target=<histone_mark>`

---

### Phase 7: Genome-Wide Statistics

For chromosome-level summary statistics:
1. Compute per-chromosome probe counts, mean beta values, and density (Phase 1.6)
2. Genome-wide average density = total probes / total genome size
3. For differential methylation summaries: count total tested, significant, hypermethylated, hypomethylated; compute fraction significant and mean delta_beta

For large datasets (> 500K probes), pre-filter by variance before running statistical tests. Use vectorized numpy/pandas operations rather than row-by-row loops.

---

## Known Gotchas

### API and Tool Quirks

- **ensembl_lookup_gene**: The `species` parameter is required and must be `"homo_sapiens"` (not "human"). Missing it causes a 400 error.
- **ensembl_get_regulatory_features**: Region string must NOT have a "chr" prefix. Use `"17:7571720-7590868"`, not `"chr17:7571720-7590868"`.
- **All ChIPAtlas tools**: Require an `operation` parameter (SOAP-style dispatch). Always pass `operation="get_experiment_list"` for `ChIPAtlas_get_experiments`.
- **All FourDN tools**: Require `operation="search_data"` as first parameter.
- **SCREEN**: Returns JSON-LD format with `@context` and `@graph` top-level keys. Extract results from `@graph`.
- **ToolUniverse annotation**: Limit batches to ~20 genes per call to avoid rate limiting.

### Data Format Gotchas

- **Illumina manifests**: Header rows vary (0, 7, or 8 rows to skip). The correct row can be identified by looking for the "CHR" or "Name" column.
- **Chromosome names**: Data sources are inconsistent — some use "1", others use "chr1". Always normalize before joining or comparing.
- **BED coordinates**: 0-based, half-open (start=0, end=100 means bases 1–100). Do not convert unless comparing with 1-based formats.
- **TCGA sample IDs**: Full barcodes (TCGA-XX-XXXX-01A) do not match patient IDs (TCGA-XX-XXXX). Truncate to first 12 characters when joining clinical and omics data.
- **Beta vs M-values**: Beta values are in [0, 1]; M-values are unbounded (log2 scale). Detect before analysis; use beta for biological interpretation, M-values for statistical testing (more homoscedastic).
- **Missing manifest**: If no manifest is provided, chromosome information cannot be recovered from probe IDs alone (probe IDs like "cg00000029" do not encode genomic location). Fall back to `ensembl_lookup_gene` to build a minimal annotation, or report the limitation.
- **Mixed genome builds**: Never mix hg19 and hg38 coordinates. Detect the genome build from data README, file names, or known landmark coordinates before running density calculations.

### Statistical Gotchas

- **Multiple testing**: Always apply FDR correction (Benjamini-Hochberg) when testing > 1 probe. Do not report raw p-values as significance.
- **Small sample sizes**: With fewer than 10 samples per group, use non-parametric tests (Mann-Whitney U instead of t-test).
- **Density ratios**: CpG density = count / chromosome_length. The result is very small (e.g., 3.2e-6 per bp). Report with sufficient precision; do not round to 0.

---

## Fallback Strategies

| Scenario | Primary | Fallback |
|----------|---------|----------|
| No manifest file | Load from data dir | Build minimal annotation via Ensembl lookup; report unmapped probes |
| No pybedtools | — | Pure Python interval intersection (group by chr, sort, scan) |
| No pyBigWig | — | Skip BigWig; use pre-computed summary tables if available |
| Missing clinical data | Report missing count | Use available samples only; note reduced N |
| Low sample count | Welch t-test | Mann-Whitney U (non-parametric) |
| Large dataset (> 500K probes) | Full analysis | Pre-filter by variance; chunk-based processing |

---

## Common Use Patterns

**Pattern 1: Methylation array — differential methylation count**
Data: beta matrix + manifest + clinical data
1. Load and filter probes (cg only, remove sex chr, apply variance filter)
2. Define groups from clinical metadata
3. Run differential methylation (t-test or Wilcoxon + BH correction)
4. Apply padj < 0.05 and |delta_beta| threshold
5. Report count and hyper/hypo split

**Pattern 2: Age-related CpG density ratio**
Data: beta matrix + manifest + age column in clinical data
1. Load beta matrix; extract ages from clinical data
2. Compute Pearson correlation per probe vs age; apply FDR correction
3. Keep significant age-related probes
4. Map to chromosomes using manifest; compute density per chromosome (count / chr length)
5. Compute and report the ratio between the two specified chromosomes

**Pattern 3: Multi-omics complete cases**
Data: clinical + expression matrix + methylation matrix
1. Extract sample ID sets from each modality
2. For clinical variables, narrow to non-NaN rows per variable
3. Intersect all sample sets
4. Report count of complete cases

**Pattern 4: ChIP-seq promoter fraction**
Data: BED or narrowPeak file
1. Load BED file; normalize chromosomes
2. Fetch gene annotation (Ensembl or local file)
3. Annotate each peak to nearest gene / feature class
4. Count peaks in "promoter" class; divide by total
5. Report fraction

**Pattern 5: Methylation-expression correlation**
Data: beta matrix + expression matrix + probe-gene mapping
1. Find common samples between matrices
2. Build probe → gene map from manifest (UCSC_RefGene_Name column)
3. For each probe-gene pair, compute Pearson r across common samples
4. Apply FDR correction; report significant anti-correlations (r < 0, padj < 0.05)

---

## Limitations

- No native pybedtools: uses pure Python interval operations (slower for very large BED files)
- No native pyBigWig: cannot read BigWig files without the package
- No R bridge: does not use methylKit, ChIPseeker, or DiffBind
- Illumina-centric: methylation functions designed for 450K/EPIC arrays
- Statistical simplicity: uses t-test/Wilcoxon (not limma/bumphunter)
- No peak calling: assumes peaks are pre-called; does not run MACS2 or similar
- API rate limits: ToolUniverse annotation limited to ~20 genes per batch

---

## Tool Reference

See `references/tools.md` for full parameter tables. Quick reference:

| Tool | Purpose |
|------|---------|
| `ensembl_lookup_gene` | Gene coordinates, biotype, Ensembl ID from symbol |
| `ensembl_get_regulatory_features` | Regulatory features (enhancers, promoters) overlapping a region |
| `ensembl_get_overlap_features` | Genes/transcripts overlapping a genomic region |
| `SCREEN_get_regulatory_elements` | ENCODE cCREs (enhancers, promoters, insulators) near a gene |
| `ReMap_get_transcription_factor_binding` | TF binding sites near a gene |
| `RegulomeDB_query_variant` | Regulatory evidence score for a SNP (rsID) |
| `jaspar_search_matrices` | JASPAR TF binding motifs by name or species |
| `ENCODE_search_experiments` | ENCODE ChIP-seq / ATAC-seq experiment metadata |
| `ChIPAtlas_get_experiments` | ChIPAtlas experiment list by antigen and genome |
| `ChIPAtlas_search_datasets` | ChIPAtlas dataset search by antigen and cell type |
| `ChIPAtlas_enrichment_analysis` | Enrichment analysis of regions against ChIPAtlas data |
| `ChIPAtlas_get_peak_data` | ChIPAtlas peak data and download URLs |
| `FourDN_search_data` | 4D Nucleome chromatin conformation datasets |
| `MyGene_query_genes` | Gene info from MyGene.info by symbol or keyword |
| `MyGene_batch_query` | Batch gene info from MyGene.info |
| `HGNC_get_gene_info` | HGNC-approved gene name, aliases, cross-references |
| `GO_get_annotations_for_gene` | Gene Ontology annotations for a gene |
