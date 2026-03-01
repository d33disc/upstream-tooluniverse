---
name: tooluniverse-single-cell
description: Production-ready single-cell and expression matrix analysis using scanpy, anndata, and scipy. Performs scRNA-seq QC, normalization, PCA, UMAP, Leiden/Louvain clustering, differential expression (Wilcoxon, t-test, DESeq2), cell type annotation, per-cell-type statistical analysis, gene-expression correlation, batch correction (Harmony), trajectory inference, and cell-cell communication analysis. NEW: Analyzes ligand-receptor interactions between cell types using OmniPath (CellPhoneDB, CellChatDB), scores communication strength, identifies signaling cascades, and handles multi-subunit receptor complexes. Integrates with ToolUniverse gene annotation tools (HPA, Ensembl, MyGene, UniProt) and enrichment tools (gseapy, PANTHER, STRING). Supports h5ad, 10X, CSV/TSV count matrices, and pre-annotated datasets. Use when analyzing single-cell RNA-seq data, studying cell-cell interactions, performing cell type differential expression, computing gene-expression correlations by cell type, analyzing tumor-immune communication, or answering questions about scRNA-seq datasets.
---

# Single-Cell Genomics and Expression Matrix Analysis

Comprehensive single-cell RNA-seq analysis and expression matrix processing using scanpy, anndata, scipy, and ToolUniverse. Designed for both full scRNA-seq workflows (raw counts to annotated cell types) and targeted expression-level analyses (per-cell-type DE, correlation, ANOVA, clustering).

---

## When to Use This Skill

Apply when users:
- Have scRNA-seq data (h5ad, 10X, CSV count matrices) and want analysis
- Ask about cell type identification, clustering, or annotation
- Need differential expression analysis by cell type or condition
- Want gene-expression correlation analysis (e.g., gene length vs expression by cell type)
- Ask about PCA, UMAP, t-SNE for expression data
- Need Leiden/Louvain clustering on expression matrices
- Want statistical comparisons between cell types (t-test, ANOVA, fold change)
- Ask about marker genes for cell populations
- Need batch correction (Harmony, ComBat)
- Want trajectory or pseudotime analysis
- Ask about cell-cell communication (ligand-receptor interactions)
- Questions mention "single-cell", "scRNA-seq", "cell type", "h5ad"
- Questions involve immune cell types (CD4, CD8, CD14, CD19, monocytes, etc.)

**BixBench Coverage**: 18+ questions across 5 projects (bix-22, bix-27, bix-31, bix-33, bix-36)

**NOT for**:
- Bulk RNA-seq DESeq2 analysis only → Use `tooluniverse-rnaseq-deseq2`
- Gene enrichment only (no expression data) → Use `tooluniverse-gene-enrichment`
- VCF/variant analysis → Use `tooluniverse-variant-analysis`
- Statistical modeling (regression, survival) → Use `tooluniverse-statistical-modeling`

---

## Core Principles

1. **Data-first** — Load, inspect, and validate data before any analysis
2. **AnnData-centric** — All data flows through anndata objects for consistency
3. **Cell type awareness** — Many questions require per-cell-type subsetting
4. **Statistical rigor** — Proper normalization, multiple testing correction, effect sizes
5. **Scanpy standard pipeline** — Follow established scRNA-seq best practices
6. **Flexible input** — Handle h5ad, 10X, CSV/TSV, pre-processed and raw data
7. **Question-driven** — Parse what the user is asking; extract the specific answer

---

## High-Level Workflow Decision Tree

```
START: User question about scRNA-seq data

Q1: What type of analysis is needed?

  FULL PIPELINE (raw counts → annotated clusters)
    Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
    (Load → QC → Normalize → HVG/PCA → Cluster → Annotate → DE)

  DIFFERENTIAL EXPRESSION (per-cell-type comparison)
    Load → Normalize → Per-CT DE → Report
    Most common BixBench pattern (bix-33). See Phase 5.

  CORRELATION ANALYSIS (gene property vs expression)
    Load → Filter genes → Subset cell type → Compute correlation
    Gene length vs expression (bix-22). See Phase 6.

  CLUSTERING & PCA (expression matrix)
    Load → Transform → PCA/Cluster → Report
    See Phase 4. Details: references/clustering_guide.md

  CELL COMMUNICATION (ligand-receptor)
    Load → Get L-R pairs → Score → Identify signaling
    See Phase 7. Details: references/cell_communication.md

  TRAJECTORY ANALYSIS (pseudotime)
    Load → Normalize → Compute trajectory → Pseudotime
    See Phase 8. Details: references/trajectory_analysis.md

Q2: What data format is available?
  h5ad      → sc.read_h5ad()
  10X files → sc.read_10x_mtx() or sc.read_10x_h5()
  CSV/TSV   → pd.read_csv() then convert to AnnData (check orientation!)

Q3: Are there pre-computed results to use?
  Has cell type annotations → Skip clustering, go to Phase 5/6
  Has PCA/UMAP             → Skip Phase 4
  Raw counts only          → Full pipeline
```

---

## Phase 1: Data Loading

**Goal**: Load data into an AnnData object and attach any metadata or gene annotations.

**Key decision — matrix orientation**: AnnData expects cells as rows and genes as columns. When loading CSV/TSV files, check whether rows are genes or cells. If there are far more rows than columns (a 5x heuristic works well), the matrix is genes-by-cells and must be transposed before creating AnnData.

**Steps**:
1. Load the count matrix (h5ad, 10X MTX/H5, or CSV/TSV).
2. Check shape, obs column names, and var column names.
3. If metadata is in a separate file, align barcodes/sample IDs and attach to `adata.obs`.
4. If gene annotations (gene length, gene type) are in a separate file, align gene names and attach to `adata.var`.

**Gotcha**: Index mismatches between metadata and the count matrix are a common failure point. Always take the intersection of indices before attaching.

See `references/scanpy_workflow.md` Phase 1 for code details.

---

## Phase 2: Quality Control

**Goal**: Remove low-quality cells and uninformative genes before downstream analysis.

**Standard filters**:
- Minimum genes per cell (commonly 200)
- Maximum mitochondrial read fraction (commonly 20%)
- Minimum cells per gene (commonly 3)

**Steps**:
1. Flag mitochondrial genes (gene names starting with `MT-` or `mt-`).
2. Compute QC metrics with `sc.pp.calculate_qc_metrics`.
3. Apply cell-level and gene-level filters.
4. Print final cell and gene counts.

**Gotcha**: If the dataset is already filtered (common in h5ad files from public repos), applying aggressive QC again can over-filter. Inspect the dataset first.

See `references/scanpy_workflow.md` Phase 2.

---

## Phase 3: Normalization and Log-Transform

**Goal**: Make gene expression values comparable across cells with different sequencing depths.

**Standard scanpy pipeline**:
1. Normalize each cell to a total count of 10,000 (`sc.pp.normalize_total`).
2. Log-transform with a pseudocount of 1 (`sc.pp.log1p`).
3. Store the normalized, log-transformed matrix as the raw layer for DE reference.

**Alternative** — for PCA on raw expression matrices (non-scRNA-seq): apply log10(x+1) directly on the matrix without cell-level normalization.

**Gotcha**: Running normalization twice (e.g., on an already-normalized h5ad) will distort results. Check `adata.raw` and obs/var metadata to determine whether the data is already normalized.

---

## Phase 4: Dimensionality Reduction and Clustering

**Goal**: Identify cell populations through unsupervised clustering.

**Steps**:
1. Select highly variable genes (HVGs) — typically top 2000.
2. Scale gene expression (zero mean, unit variance).
3. Run PCA — typically 50 components.
4. Build a k-nearest-neighbor graph on the top PCs (typically 30).
5. Run Leiden (preferred) or Louvain clustering.
6. Run UMAP for visualization.

**Resolution tuning**: Higher Leiden resolution → more, smaller clusters. Start at 0.5 and adjust based on the expected number of cell types.

**Batch correction**: If samples come from multiple batches, run Harmony after PCA. Harmony corrects the PCA embedding; all downstream steps (neighbors, clustering, UMAP) use the Harmony-corrected embedding instead of raw PCA.

**Gotcha**: Clustering on uncorrected PCA when batches are present will produce batch-driven clusters rather than biology-driven ones. Always check batch metadata before clustering.

See `references/clustering_guide.md` for hierarchical and bootstrap consensus clustering.

---

## Phase 5: Cell Type Annotation and Differential Expression

### 5a: Cell Type Annotation

**Goal**: Assign biological identity to each cluster.

**Approach**:
1. Run `sc.tl.rank_genes_groups` with `groupby='leiden'` to find marker genes per cluster.
2. Inspect top 10 markers per cluster.
3. Match against known canonical markers (e.g., CD3D/CD3E → T cells, CD19/MS4A1 → B cells, CD14/LYZ → Monocytes).
4. Assign cell type labels to each cluster in `adata.obs['cell_type']`.
5. Optionally use ToolUniverse HPA or MyGene tools to validate or look up marker gene expression patterns.

**Canonical immune markers**:
- T cells: CD3D, CD3E, CD8A (cytotoxic), CD4 (helper)
- B cells: CD19, MS4A1, CD79A
- NK cells: GNLY, NKG7, NCAM1
- Monocytes: CD14, LYZ, S100A9
- Dendritic cells: FCER1A, CST3

### 5b: Per-Cell-Type Differential Expression

**Goal**: Find genes that differ between conditions (e.g., treatment vs control) within each cell type.

**BixBench pattern (bix-33)**: "Which immune cell type has the most DEGs after treatment?"

**Steps**:
1. Load and normalize the data.
2. Iterate over each unique cell type.
3. Subset the data to cells of that type.
4. Check that both conditions have at least 3 cells (skip if not).
5. Run `sc.tl.rank_genes_groups` with `groupby='condition'`, `method='wilcoxon'`, and set the reference group.
6. Extract results with `sc.get.rank_genes_groups_df`.
7. Count significant DEGs (adjusted p-value < 0.05).
8. Report which cell type has the most DEGs and the full table.

**Methods**: Wilcoxon (default, non-parametric, recommended for scRNA-seq), t-test, logreg. For pseudo-bulk comparisons with replicates, use DESeq2 via PyDESeq2.

**Multiple testing**: scanpy's `rank_genes_groups` applies Benjamini-Hochberg correction by default. The adjusted p-value column is `pvals_adj`.

See `references/scanpy_workflow.md` Phase 5.

---

## Phase 6: Statistical Analysis on Expression Data

**Goal**: Answer targeted statistical questions about expression patterns.

### 6a: Gene Property vs Expression Correlation (bix-22)

**Question type**: "What is the Pearson correlation between gene length and mean expression in CD4 T cells?"

**Steps**:
1. Load the h5ad and attach gene annotations (gene length, gene type) to `adata.var`.
2. Filter to protein-coding genes only (check `gene_type == 'protein_coding'`).
3. Subset to the target cell type.
4. Compute mean expression per gene across cells in that subset (handle sparse matrices by converting to dense first).
5. Remove genes where either the gene property or mean expression is NaN.
6. Compute Pearson or Spearman correlation between the gene property and mean expression.
7. Report the correlation coefficient and p-value.

**Sparse matrix handling**: Check `scipy.sparse.issparse(adata.X)` before calling `.mean()`. Convert with `.toarray()` if sparse.

### 6b: T-Tests Between Cell Type Groups (bix-31)

**Question type**: "Is the mean LFC significantly different between T cells and other cell types?"

**Steps**:
1. After running per-cell-type DE (Phase 5b), collect log2 fold change values for each cell type.
2. Combine LFCs for the target group (e.g., CD4 + CD8).
3. Combine LFCs for the reference group (all other cell types).
4. Run Welch's t-test (unequal variances) with `scipy.stats.ttest_ind(..., equal_var=False)`.
5. Report the t-statistic and p-value.

### 6c: ANOVA Across Cell Types (bix-36)

**Question type**: "What is the F-statistic for miRNA expression differences across immune cell types?"

**Steps**:
1. Load the expression matrix and metadata separately.
2. Exclude any aggregate groups (e.g., "PBMC" rows if comparing individual cell types).
3. Group expression values by cell type.
4. Run one-way ANOVA with `scipy.stats.f_oneway(*groups)`.
5. Report the F-statistic and p-value.

### 6d: Multiple Testing Correction

Use `statsmodels.stats.multitest.multipletests`. Common methods:
- `fdr_bh` — Benjamini-Hochberg (FDR control, recommended)
- `bonferroni` — Conservative, controls family-wise error rate

---

## Phase 7: Cell-Cell Communication Analysis

**Goal**: Identify ligand-receptor interactions between cell types using OmniPath.

**BixBench pattern**: "Which ligand-receptor interactions are strongest between tumor cells and T cells?"

**Steps**:
1. Call `mcp__tooluniverse__execute_tool` with `tool_name="OmniPath_get_ligand_receptor_interactions"` to retrieve validated L-R pairs. Optionally filter by database (e.g., `databases="CellPhoneDB,CellChatDB"`).
2. Filter the returned pairs to those where both the ligand and receptor genes are present in the dataset's gene names.
3. For each L-R pair, compute a communication score: the mean ligand expression in the sender cell type multiplied by the mean receptor expression in the receiver cell type.
4. Build a sender-receiver-pair matrix and rank by score.
5. Filter to the cell type pairs of interest (e.g., tumor → T cell, T cell → tumor).
6. Optionally call `OmniPath_get_signaling_interactions` to trace downstream signaling from the top receptor hits.
7. Call `OmniPath_get_complexes` for any multi-subunit receptor to get all required components.

**Key**: OmniPath integrates CellPhoneDB, CellChatDB, ICELLNET, Ramilowski2015, and 100+ curated databases. Use the `databases` parameter to restrict to specific ones.

See `references/cell_communication.md` for the full scoring helper and signaling cascade workflow.

---

## Phase 8: Trajectory and Pseudotime Analysis

**Goal**: Order cells along a developmental or differentiation trajectory to study dynamic gene expression.

**Steps**:
1. Load and normalize data (Phases 1-3).
2. Run the standard dimensionality reduction (Phase 4) to get PCA and UMAP embeddings.
3. Set the root cell or root cluster (known starting state, e.g., stem cells or progenitors).
4. Run diffusion pseudotime (`sc.tl.dpt`) or PAGA (`sc.tl.paga`) for trajectory inference.
5. For PAGA: run `sc.tl.paga` then `sc.pl.paga` to visualize connectivity between clusters, then embed using PAGA-initialized UMAP.
6. For DPT: set `adata.uns['iroot']` to the index of the root cell, then run `sc.tl.dpt`.
7. Identify genes that correlate with pseudotime (Spearman correlation of gene expression vs pseudotime value).

**Gotcha**: DPT requires a diffusion map embedding first (`sc.tl.diffmap`). PAGA requires cluster labels.

See `references/trajectory_analysis.md` for complete details.

---

## ToolUniverse Tool Reference

Agents call tools via `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

| Tool | Purpose | Key Arguments |
|------|---------|--------------|
| `OmniPath_get_ligand_receptor_interactions` | Fetch L-R pairs from CellPhoneDB, CellChatDB, etc. | `proteins`, `databases` |
| `OmniPath_get_signaling_interactions` | Downstream signaling cascades from receptors | `proteins`, `databases` |
| `OmniPath_get_complexes` | Multi-subunit receptor composition | `proteins` |
| `OmniPath_get_cell_communication_annotations` | Pathway/role annotations for L-R pairs | `proteins` |
| `HPA_search_genes_by_query` | Cell-type marker gene search | `query` |
| `MyGene_query_genes` | Gene ID conversion, gene info lookup | `q`, `fields`, `species` |
| `MyGene_batch_query` | Batch gene ID/info lookup | `ids`, `fields` |
| `ensembl_lookup_gene` | Ensembl gene details | `gene_id` |
| `UniProt_get_function_by_accession` | Protein function description | `accession` |
| `PANTHER_enrichment` | GO enrichment (BP, MF, CC) | `gene_list`, `organism`, `annotation_type` |
| `STRING_functional_enrichment` | Network-based enrichment | `identifiers`, `species` |
| `ReactomeAnalysis_pathway_enrichment` | Curated Reactome pathway enrichment | `gene_list` |

See `references/tools.md` for full parameter tables and return format details.

---

## Scanpy vs Seurat Quick Reference

| Operation | Seurat (R) | Scanpy (Python) |
|-----------|------------|-----------------|
| Load 10X | `Read10X()` | `sc.read_10x_mtx()` |
| Normalize | `NormalizeData()` | `sc.pp.normalize_total() + sc.pp.log1p()` |
| Find HVGs | `FindVariableFeatures()` | `sc.pp.highly_variable_genes()` |
| Scale | `ScaleData()` | `sc.pp.scale()` |
| PCA | `RunPCA()` | `sc.tl.pca()` |
| Neighbors | `FindNeighbors()` | `sc.pp.neighbors()` |
| Cluster | `FindClusters()` | `sc.tl.leiden()` or `sc.tl.louvain()` |
| UMAP | `RunUMAP()` | `sc.tl.umap()` |
| Find markers | `FindMarkers()` | `sc.tl.rank_genes_groups()` |
| Batch correction | `RunHarmony()` | `harmonypy.run_harmony()` |

---

## Known Gotchas

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Sparse matrix `.mean()` gives wrong shape | `adata.X` is a scipy sparse matrix | Check `issparse(adata.X)`; call `.toarray()` before numpy operations |
| Wrong matrix orientation (CSV) | Genes as rows, cells as columns | If rows >> columns (5x), transpose before creating AnnData |
| Double normalization | Loading an already-normalized h5ad then normalizing again | Check `adata.raw` and obs metadata; skip normalization if already done |
| DE result column `logfoldchanges` not `log2FoldChange` | Scanpy uses different column name than DESeq2 | scanpy column is `logfoldchanges`; DESeq2 column is `log2FoldChange` |
| Too few cells for DE | Condition has < 3 cells of a given cell type | Skip that cell type; add a guard: `if n_treat < 3 or n_ctrl < 3: continue` |
| Batch-driven clusters | PCA without batch correction when multiple batches exist | Run Harmony after PCA; use `X_pca_harmony` for neighbors |
| `leidenalg` not found | Package not installed | `pip install leidenalg` |
| NaN in correlation | Gene property (e.g., gene length) missing for some genes | Filter: `valid = ~np.isnan(x) & ~np.isnan(y)` before `pearsonr` |
| Gene name mismatches (Ensembl vs symbol) | Dataset uses Ensembl IDs; annotations use gene symbols | Use `MyGene_batch_query` to convert IDs before joining |
| DPT fails without diffusion map | `sc.tl.dpt` requires diffusion map embedding first | Run `sc.tl.diffmap` before `sc.tl.dpt` |
| OmniPath returns multi-subunit complexes as single entries | Receptor is a complex (e.g., IL2RA+IL2RB+IL2RG) | Use `OmniPath_get_complexes` to expand and validate all subunits are expressed |
| Memory error on large datasets (>100k cells) | Full dense matrix allocation | Use HVG selection to reduce to 2000-3000 genes before PCA; avoid `.toarray()` on full matrix |
| `pvals_adj` all 1.0 after DE | Too few cells or all expression identical | Check cell counts; check if matrix is pre-normalized log-counts passed to a method expecting raw counts |

---

## Workflow Summary

**Full scRNA-seq pipeline** (Phase 1 → 2 → 3 → 4 → 5a): Load → QC → Normalize → HVG/PCA/Cluster → Annotate → DE

**Per-cell-type DE** (most common BixBench pattern): Load → Normalize → Iterate cell types → Wilcoxon DE → Count DEGs → Report top cell type

**Gene correlation by cell type**: Load → Attach gene properties → Filter protein-coding → Subset cell type → Mean expression → pearsonr

**Cell-cell communication**: Load → OmniPath L-R pairs → Filter to expressed → Score sender×receiver → Rank → Report

**Trajectory inference**: Load → Normalize → PCA → PAGA or diffusion map → Pseudotime → Correlate genes with pseudotime

---

## Reference Documentation

| File | Contents |
|------|---------|
| `references/scanpy_workflow.md` | Complete scanpy pipeline with code (QC, normalize, PCA, cluster, DE) |
| `references/clustering_guide.md` | Leiden, Louvain, hierarchical, bootstrap consensus clustering |
| `references/marker_identification.md` | Marker genes, cell type annotation workflows |
| `references/trajectory_analysis.md` | Pseudotime, PAGA, diffusion pseudotime |
| `references/cell_communication.md` | Full OmniPath/CellPhoneDB workflow with scoring helpers |
| `references/seurat_workflow.md` | Seurat → Scanpy translation guide |
| `references/troubleshooting.md` | Common errors, package issues, data format problems |
| `references/tools.md` | Full parameter tables and return formats for all ToolUniverse tools used here |
