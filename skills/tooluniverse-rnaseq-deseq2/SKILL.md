---
name: tooluniverse-rnaseq-deseq2
description: Production-ready RNA-seq differential expression analysis using PyDESeq2. Performs DESeq2 normalization, dispersion estimation, Wald testing, LFC shrinkage, and result filtering. Handles multi-factor designs, multiple contrasts, batch effects, and integrates with gene enrichment (gseapy) and ToolUniverse annotation tools (UniProt, Ensembl, OpenTargets). Supports CSV/TSV/H5AD input formats and any organism. Use when analyzing RNA-seq count matrices, identifying DEGs, performing differential expression with statistical rigor, or answering questions about gene expression changes.
---

# RNA-seq Differential Expression Analysis (DESeq2)

Comprehensive differential expression analysis of RNA-seq count data using PyDESeq2, with integrated enrichment analysis (gseapy) and gene annotation via ToolUniverse.

**BixBench Coverage**: Validated on 53 BixBench questions across 15 computational biology projects covering RNA-seq, miRNA-seq, and differential expression analysis tasks.

---

## Core Principles

1. **Data-first** — Load and validate count data and metadata BEFORE any analysis.
2. **Statistical rigor** — Always use proper normalization, dispersion estimation, and multiple testing correction.
3. **Inspect everything** — Examine all metadata columns before choosing a design formula.
4. **Threshold awareness** — Apply user-specified thresholds exactly (padj, log2FC, baseMean).
5. **Question-driven** — Parse what the user is actually asking and extract the specific answer.
6. **English-first queries** — Use English gene/pathway names in all tool calls.

---

## When to Use This Skill

Apply when users:
- Have RNA-seq count matrices and want differential expression analysis
- Ask about DESeq2, DEGs, differential expression, padj, log2FC
- Need dispersion estimates or diagnostics
- Want enrichment analysis (GO, KEGG, Reactome) on DEGs
- Ask about specific gene expression changes between conditions
- Need to compare multiple strains/conditions/treatments
- Ask about batch effect correction in RNA-seq
- Questions mention "count data", "count matrix", "RNA-seq", "transcriptomics"

---

## Required Packages

Install before analysis:

```
pip install pydeseq2 gseapy pandas numpy scipy anndata
```

Core imports: `pandas`, `numpy`, `pydeseq2.dds.DeseqDataSet`, `pydeseq2.ds.DeseqStats`. For enrichment: `gseapy`. For annotation: call ToolUniverse tools via MCP (`mcp__tooluniverse__execute_tool`).

---

## Analysis Workflow

### Phase 1: Question Parsing

Before writing any code, parse the question to identify:

- **Data files** — Look for `*counts*.csv`, `*metadata*.csv`, `*.h5ad`
- **Thresholds** — Extract padj (default 0.05), log2FC (default 0, meaning no filter), baseMean (default 0)
- **Design** — Identify factors mentioned ("strain", "condition", "batch")
- **Contrast** — Determine comparison ("A vs B", "mutant vs wildtype")
- **Direction** — Check if "upregulated", "downregulated", or both
- **Enrichment** — Look for "GO", "KEGG", "Reactome", "pathway"
- **Specific genes** — Check if asking about individual genes

See [references/question_parsing.md](references/question_parsing.md) for detailed extraction patterns.

---

### Phase 2: Data Loading and Validation

Load count matrix and metadata, then validate alignment. Key requirements:

- **Orientation** — PyDESeq2 requires samples as rows, genes as columns. Transpose if needed.
- **Integer counts** — Round float values to integers; warn if data looks normalized (FPKM/TPM).
- **Sample alignment** — Intersect sample names between counts and metadata; strip whitespace.
- **Zero genes** — Remove genes with zero counts across all samples before fitting.

For H5AD files, extract the count matrix from `adata.X` and metadata from `adata.obs`. For RDS files, convert to CSV in R first or use rpy2.

See [references/data_loading.md](references/data_loading.md) for format-specific patterns.

---

### Phase 3: Design Formula Decision (CRITICAL)

**Always inspect ALL metadata columns before choosing a design formula.** Many experiments have hidden batch effects (media conditions, sequencing batches, time points) that must be included as covariates.

**Decision process:**

1. List all metadata columns and their unique values.
2. Classify each column:
   - **Biological factor to test** (strain, treatment, genotype, condition)
   - **Batch/block covariate** (media, batch, sequencing_run, time, plate)
   - **Irrelevant** (sample ID, file name, notes)
3. Build formula: put covariates first, then the factor of interest.

| Situation | Design formula |
|-----------|---------------|
| Single factor only | `~condition` |
| One covariate + one factor | `~batch + condition` |
| Two covariates + factor | `~batch1 + batch2 + condition` |
| Interaction | `~batch + factor1 + factor2 + factor1:factor2` |

**Real-world example:**
```
Metadata: Strain (4 levels), Media (3 levels), Replicate (3 levels)
Question: "strain effects"

WRONG:   ~Strain          (ignores Media)
CORRECT: ~Media + Strain  (accounts for media variation)
```

The rule of thumb: if a column has 2+ levels and represents a systematic experimental condition (not a sample ID), include it in the design.

---

### Phase 4: Run PyDESeq2

**Step 4a — Set reference levels.** In PyDESeq2 the first category in a `pd.Categorical` is the reference. Set it explicitly for every factor in the design before creating the dataset.

**Step 4b — Fit DESeq2.** Create a `DeseqDataSet` with the count matrix, metadata, and design formula, then call `.deseq2()`. This runs normalization, dispersion estimation, and testing in one step.

**Step 4c — Extract results.** Create a `DeseqStats` object with the fitted dataset and the specific contrast `[factor, numerator, denominator]`. Call `.run_wald_test()` then `.summary()`. Access results via `.results_df`.

**Step 4d — LFC shrinkage (if requested).** After the Wald test, call `.lfc_shrink(coeff=...)`. The coefficient name format is `factor[T.level]` where `level` is the numerator of the contrast. Verify the coefficient exists in `dds.varm['LFC'].columns` before shrinking.

**Step 4e — Multiple contrasts.** Fit the model once, then extract multiple `DeseqStats` objects with different contrasts.

See [references/pydeseq2_workflow.md](references/pydeseq2_workflow.md) for complete code patterns including multi-factor designs, interaction terms, continuous covariates, and batch correction.

---

### Phase 5: Filter Results

Apply thresholds exactly as specified in the question:

- Filter on `padj < threshold` AND (if specified) `log2FoldChange.abs() > lfc_threshold` AND (if specified) `baseMean > basemean_threshold`.
- Always drop rows with `NaN` in `padj` before counting DEGs — NaN means independent filtering removed the gene, not that it passed.
- For direction-specific questions, additionally filter `log2FoldChange > 0` (upregulated) or `< 0` (downregulated).
- For set operations across multiple contrasts ("unique to A", "shared between A and B"), convert each DEG list to a Python `set` and use set arithmetic.

**Dispersion column mapping** (for dispersion-specific questions):

| Question phrasing | PyDESeq2 column |
|-------------------|-----------------|
| "prior to fitting" / "prior to shrinkage" | `dds.var['genewise_dispersions']` |
| "fitted dispersions" | `dds.var['fitted_dispersions']` |
| "after shrinkage" / "MAP" | `dds.var['MAP_dispersions']` |
| "dispersion estimate" (general) | `dds.var['dispersions']` |

See [references/result_filtering.md](references/result_filtering.md) and [references/dispersion_analysis.md](references/dispersion_analysis.md) for advanced patterns.

---

### Phase 6: Enrichment Analysis (optional)

Use `gseapy` (no R required) for pathway enrichment on the DEG list.

**Standard ORA (over-representation analysis):**
Call `gseapy.enrich(gene_list, gene_sets, background, outdir=None, cutoff=0.05, no_plot=True)`. Access results via `.results` DataFrame.

**Library selection by organism and database:**

| Organism | GO BP | KEGG | Reactome |
|----------|-------|------|----------|
| Human | `GO_Biological_Process_2023` | `KEGG_2021_Human` | `Reactome_2022` |
| Mouse | `GO_Biological_Process_2023` | `KEGG_2019_Mouse` | — |

**GSEA (gene set enrichment, ranked):**
Use `gseapy.prerank(rnk, gene_sets, outdir=None, permutation_num=1000, no_plot=True)`. Rank genes by `-log10(pvalue) * sign(log2FoldChange)`.

**Extracting a specific pathway result:**
Search the `Term` column case-insensitively. The `Overlap` column contains `"n_overlap/pathway_size"` (e.g., `"11/42"`). The `Genes` column contains semicolon-separated contributing genes.

**gseapy vs R clusterProfiler:**
Results may differ due to different algorithms and database versions. Use R clusterProfiler via rpy2 only when exact reproducibility with R benchmarks is required.

See [references/enrichment_analysis.md](references/enrichment_analysis.md) for complete workflows.

---

### Phase 7: Gene Annotation with ToolUniverse (optional)

Use ToolUniverse tools **only for annotation**, not for statistical analysis.

Call tools via MCP using `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

**Use ToolUniverse for:**
- Gene ID conversion (Ensembl ↔ symbol ↔ Entrez)
- Gene summaries and functional descriptions
- Protein-level annotation (UniProt)
- Disease-gene associations (OpenTargets)

**Do not use ToolUniverse for:**
- Differential expression (use PyDESeq2)
- Statistical testing (use scipy.stats)
- Enrichment analysis (use gseapy)

See [references/tools.md](references/tools.md) for the full ToolUniverse tool reference with parameter details.

---

## Output Formatting

Match the format requested in the question:

| Request | Format |
|---------|--------|
| "2 decimal places" | `round(value, 2)` |
| "scientific notation" | `f"{value:.2E}"` |
| "as percentage" | `f"{value * 100:.1f}%"` |
| "how many genes" | `int(len(sig_genes))` |
| "gene list" | newline-separated or Python list |

See [references/output_formatting.md](references/output_formatting.md) for all format patterns.

---

## Common BixBench Patterns

### Pattern 1: Basic DEG Count
Filter by padj and |log2FC|, count rows after dropping NaN padj.

### Pattern 2: Specific Gene Value
Look up a single gene by name in the results DataFrame index; handle case-insensitive matching.

### Pattern 3: Direction-Specific Count
Add a sign filter on log2FoldChange after the standard padj/lfc filters.

### Pattern 4: Set Operations
Run multiple contrasts, convert each significant gene set to a Python `set`, use `-` for unique, `&` for shared.

### Pattern 5: Dispersion Count
After fitting, access `dds.var['genewise_dispersions']` and apply a threshold comparison.

See [references/bixbench_examples.md](references/bixbench_examples.md) for all 10 patterns with complete examples.

---

## Known Gotchas

1. **NaN in padj is not a zero** — Independent filtering sets padj to NaN for low-evidence genes. Always call `.dropna(subset=['padj'])` before counting DEGs. Never count NaN rows as passing.

2. **PyDESeq2 reference level = first Categorical category** — Unlike R, there is no `relevel()`. Set the order of categories in `pd.Categorical` explicitly, with the reference level first.

3. **Hidden batch variables invalidate analysis** — If metadata has a column that represents a systematic condition (media, batch, plate) that correlates with gene expression, omitting it from the design formula inflates or deflates fold changes and produces false positives/negatives. Always inspect all metadata columns.

4. **LFC shrinkage coefficient format** — The coefficient must match the PyDESeq2 internal naming convention: `factor[T.level]`. If it does not match, shrinkage silently fails or raises an error. Always print `dds.varm['LFC'].columns` to verify available coefficients before calling `.lfc_shrink()`.

5. **Contrast direction matters** — `contrast = [factor, numerator, denominator]`. Swapping numerator and denominator flips the sign of all log2FC values. Positive log2FC means higher in the numerator group.

6. **PyDESeq2 vs R DESeq2 numerical differences** — Dispersion estimates can differ from R, especially for very low dispersions (< 1e-5), due to different underlying numerical optimizers. Results are statistically valid but not identical to R output.

7. **gseapy organism parameter is deprecated in v1.1+** — Do not pass `organism=`. Specify the organism via the gene set library name (e.g., `KEGG_2021_Human` not `KEGG_2019` + `organism='human'`).

8. **Continuous covariates need explicit declaration** — Pass `continuous_factors=['age']` to `DeseqDataSet` for any numeric covariate. Otherwise PyDESeq2 may treat it as a categorical factor.

9. **Matrix orientation** — PyDESeq2 requires samples as rows and genes as columns. Many public datasets ship genes as rows. If loading fails or sample counts look wrong, transpose the matrix.

10. **Single replicate per condition** — DESeq2 cannot estimate dispersion with only one sample per group. Fall back to simple fold-change calculation or pool replicates from similar conditions.

---

## Error Quick Reference

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| "No matching samples" | Counts need transposing or whitespace difference | Strip whitespace, try transposing |
| "Dispersion trend did not converge" | Small sample size / low variation | Use `fit_type='mean'` |
| "Contrast not found" | Wrong factor or level name | Check `metadata['factor'].unique()` for exact names |
| "Non-integer counts" | Normalized data (FPKM/TPM) | Round to int, or use t-test |
| NaN in padj | Independent filtering removed genes | Drop NaN before counting |
| "Singular design matrix" | Confounded factors | Check `pd.crosstab(batch, condition)` |
| "Coefficient not found" | Wrong shrinkage coefficient format | Print `dds.varm['LFC'].columns` |

See [references/troubleshooting.md](references/troubleshooting.md) for detailed debugging guidance.

---

## Validation Checklist

**Data Loading:**
- [ ] Count matrix: samples as rows, genes as columns
- [ ] Metadata index matches count index exactly
- [ ] Integer counts confirmed

**DESeq2 Analysis:**
- [ ] All metadata columns inspected before design choice
- [ ] Covariates included before factor of interest in formula
- [ ] Reference level set as first Categorical category
- [ ] Correct contrast extracted [factor, numerator, denominator]

**Results:**
- [ ] NaN padj rows dropped before counting
- [ ] Thresholds match question exactly
- [ ] Direction filter applied if specified
- [ ] Answer formatted to requested precision

---

## Tool Reference (Abbreviated)

Use `mcp__tooluniverse__execute_tool` to call any tool below. Full parameter tables in [references/tools.md](references/tools.md).

| Tool name | Purpose |
|-----------|---------|
| `MyGene_query_genes` | Convert gene symbols, look up Entrez/Ensembl IDs |
| `ensembl_lookup_gene` | Get gene details by Ensembl ID |
| `ensembl_get_sequence` | Fetch gene/transcript sequence |
| `UniProt_search_proteins` | Search proteins by name or ID |
| `UniProt_get_protein` | Get full UniProt entry |
| `OpenTargets_get_gene` | Disease-gene associations, tractability |
| `NCBI_gene_search` | Search NCBI Gene by name or keyword |
| `NCBI_fetch_gene` | Fetch NCBI Gene entry by ID |

---

## References

- [question_parsing.md](references/question_parsing.md) — Extract parameters from questions
- [data_loading.md](references/data_loading.md) — Data loading and validation patterns
- [pydeseq2_workflow.md](references/pydeseq2_workflow.md) — Complete PyDESeq2 code examples
- [result_filtering.md](references/result_filtering.md) — Advanced filtering and extraction
- [dispersion_analysis.md](references/dispersion_analysis.md) — Dispersion diagnostics
- [enrichment_analysis.md](references/enrichment_analysis.md) — GO/KEGG/Reactome workflows
- [output_formatting.md](references/output_formatting.md) — Format answers correctly
- [bixbench_examples.md](references/bixbench_examples.md) — All 10 question patterns
- [troubleshooting.md](references/troubleshooting.md) — Common issues and debugging
- [tools.md](references/tools.md) — ToolUniverse tool parameter reference

## Utility Scripts

- [scripts/format_deseq2_output.py](scripts/format_deseq2_output.py) — Output formatters
- [scripts/load_count_matrix.py](scripts/load_count_matrix.py) — Data loading utilities
