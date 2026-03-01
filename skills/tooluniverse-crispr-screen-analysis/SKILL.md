---
name: tooluniverse-crispr-screen-analysis
description: Comprehensive CRISPR screen analysis for functional genomics. Analyze pooled or arrayed CRISPR screens (knockout, activation, interference) to identify essential genes, synthetic lethal interactions, and drug targets. Perform sgRNA count processing, gene-level scoring (MAGeCK, BAGEL), quality control, pathway enrichment, and drug target prioritization. Use for CRISPR screen analysis, gene essentiality studies, synthetic lethality detection, functional genomics, drug target validation, or identifying genetic vulnerabilities.
---

# ToolUniverse CRISPR Screen Analysis

Comprehensive skill for analyzing CRISPR-Cas9 genetic screens to identify essential genes, synthetic lethal interactions, and therapeutic targets through robust statistical analysis and pathway enrichment.

**Target runtime**: LLM agents in MCP clients — all tool calls use `mcp__tooluniverse__execute_tool`.

---

## Overview

CRISPR screens enable genome-wide functional genomics by systematically perturbing genes and measuring fitness effects. This skill provides an 8-phase workflow covering:

- sgRNA count matrix processing and QC
- Library-size normalization and log-fold change (LFC) calculation
- Gene-level essentiality scoring (MAGeCK-like RRA and BAGEL-like Bayes Factors)
- Synthetic lethality detection (cross-condition comparison)
- Pathway enrichment of essential gene sets
- Drug target prioritization with DGIdb druggability data
- Integration with expression and variant databases
- Final report assembly

---

## When to Use This Skill

Apply when users:

- Have sgRNA count matrices from pooled CRISPR screens (dropout / positive selection)
- Ask about MAGeCK scoring, RRA, BAGEL Bayes Factors, or gene essentiality
- Want to find context-specific essential genes or synthetic lethal pairs
- Need pathway enrichment on CRISPR hits
- Are prioritizing drug targets from a screen
- Mention "CRISPR screen", "pooled library", "Brunello", "Avana", "sgRNA counts", "dropout"

**NOT for**:
- Single-gene CRISPRi/a validation assays (use `tooluniverse-gene-enrichment` for enrichment only)
- Differential expression from RNA-seq (use `tooluniverse-rnaseq-deseq2`)
- Drug-gene interaction lookups without a screen (use `tooluniverse-drug-target-validation`)

---

## Core Principles

1. **Controls first** — Verify that positive-control essential genes (e.g., RPS6, RPL5, POLR2A) deplete and negative-control non-targeting sgRNAs are stable before calling hits.
2. **Replicate minimum** — Require at least 2 biological replicates per condition; flag analyses with only 1 replicate.
3. **Sequencing depth check** — Confirm 300+ reads/sgRNA at T0; warn if median drops below 100 at later timepoints.
4. **Normalize before scoring** — Always apply median-ratio normalization before computing LFC.
5. **RRA over mean** — Use robust rank aggregation (RRA) rather than simple mean LFC for gene-level scoring; RRA is resistant to single discordant sgRNAs.
6. **FDR correction** — Apply Benjamini-Hochberg correction; report both raw and adjusted p-values.
7. **Validate hits** — Cross-check top hits against DepMap/STRING/DGIdb before reporting.
8. **Context dependency** — Gene essentiality varies by cell line and genetic background; always document screen context.

---

## 8-Phase Workflow

### Phase 1: Data Import and sgRNA Count Processing

**Goal**: Load the sgRNA count matrix, validate its format, and extract design metadata.

Expected input format (MAGeCK TSV or equivalent):
```
sgRNA    Gene    T0_rep1    T0_rep2    T14_rep1    T14_rep2
sgRNA_1  BRCA1   1500       1200       1100        900
sgRNA_2  BRCA1   1800       1500       1400        1100
```

Steps:
1. Read the count file (tab-separated; columns: `sgRNA`, `Gene`, then one column per sample).
2. Record the number of sgRNAs, genes, and samples.
3. Build the sgRNA-to-gene mapping.
4. Record sample names grouped by condition (baseline vs. treatment) and replicate index.
5. Validate that both positive-control essential genes and non-targeting control sgRNAs are present in the library.

**Tool call — literature context if library source is unknown**:
Call `PubMed_search` with a query such as `"Brunello library" OR "Avana library" CRISPR sgRNA design` to retrieve library validation references.

See [references/tools.md](references/tools.md) for full parameter details.

---

### Phase 2: Quality Control and Filtering

**Goal**: Identify and remove low-quality sgRNAs; flag problematic samples.

QC metrics to compute and report:
- Library size (total reads) per sample
- Fraction of sgRNAs with zero counts (should be < 1%)
- Gini coefficient per sample (library evenness; < 0.2 = well-represented)
- Read count distribution (median and 10th percentile per sgRNA)

Filtering rules:
- Remove sgRNAs with fewer than 30 reads in more than half the samples.
- Flag samples with library size < 50% of the median as potential outliers.
- Require at least 3 sgRNAs per gene after filtering; genes with fewer are excluded from scoring.

**Positive-control check (CRITICAL)**:
Confirm that known essential genes (RPS6, RPL5, POLR2A, PSMC2, PSMD14) are present and that their T14 counts are substantially lower than T0. If essential gene sgRNAs do not deplete, the screen has likely failed — stop and report this.

---

### Phase 3: Normalization and LFC Calculation

**Goal**: Remove library-size bias; compute sgRNA-level log2 fold changes.

Normalization (median-ratio, preferred):
1. Compute a pseudo-reference for each sgRNA as the geometric mean of its counts across all samples.
2. For each sample, compute the median ratio of observed counts to the pseudo-reference.
3. Divide each sample's counts by its size factor.

Alternative: total-count (CPM) normalization is acceptable when the pseudo-reference approach produces unstable size factors (e.g., very few expressed sgRNAs).

LFC calculation:
- Average normalized counts within each condition across replicates.
- Add a pseudocount of 1 before log2 transformation.
- LFC = log2((treatment_mean + 1) / (baseline_mean + 1))

Interpretation guide:
- LFC < -1: strong dropout, candidate essential gene
- -1 to -0.5: moderate dropout
- -0.5 to +0.5: neutral
- LFC > +1: enriched, candidate positive-selection gene

---

### Phase 4: Gene-Level Scoring (MAGeCK RRA and BAGEL Bayes Factor)

**Goal**: Aggregate sgRNA-level LFCs to gene-level essentiality scores using two complementary methods.

#### MAGeCK-style Robust Rank Aggregation (RRA)

1. Rank all sgRNAs by LFC (ascending = most depleted first).
2. For each gene, collect the ranks of its sgRNAs.
3. The RRA score is derived from how consistently a gene's sgRNAs rank near the top (most depleted). Lower mean rank = more essential.
4. Compute a gene-level p-value using a rank-based test; apply BH correction for FDR.
5. Report: gene name, mean LFC, number of sgRNAs, RRA rank, p-value, FDR.

Essential gene thresholds (negative selection):
- Tier 1: FDR < 0.05 AND mean LFC < -1.0 (high confidence essential)
- Tier 2: FDR < 0.10 AND mean LFC < -0.5 (moderate confidence)
- Tier 3: mean LFC < -0.5 only (suggestive, not FDR-controlled)

Positive selection thresholds (enrichment):
- FDR < 0.05 AND mean LFC > +1.0

#### BAGEL-style Bayes Factor (BF)

Uses reference distributions from known essential and non-essential gene sets to compute a likelihood ratio:

1. Collect LFCs for positive controls (essential reference set: ribosomal genes, core proteasome, RNA polymerase subunits).
2. Collect LFCs for negative controls (non-essential reference set: AAVS1, ROSA26, non-targeting sgRNAs).
3. Fit Gaussian distributions to each reference set.
4. For each gene, compute BF = likelihood(LFC | essential) / likelihood(LFC | non-essential).
5. BF > 5: likely essential; BF > 10: high confidence essential; BF < 0: likely non-essential.

**Use both scores**: Genes that are Tier 1 by RRA AND BF > 10 are the highest-confidence hits.

---

### Phase 5: Synthetic Lethality Detection

**Goal**: Identify genes that are selectively essential in one genetic context but not another.

Setup: requires screens run in at least two matched cell lines (e.g., KRAS-wildtype vs. KRAS-mutant isogenic pair, or at minimum two cell lines with different driver mutations).

Detection logic:
1. Score each screen independently through Phase 4.
2. For every gene, compute:
   - delta_LFC = LFC_mutant - LFC_wildtype
   - delta_rank = rank_wildtype - rank_mutant (positive = more essential in mutant)
3. Synthetic lethal (SL) candidates satisfy all three conditions:
   - mean_LFC_mutant < -1.0 (essential in mutant context)
   - mean_LFC_wildtype > -0.5 (not essential in wildtype)
   - delta_rank > 100 (large rank change between contexts)
4. Sort SL candidates by delta_LFC (most negative first).

**DepMap cross-reference**: Use `PubMed_search` to find papers reporting the SL interaction. Query: `"<gene>" AND "synthetic lethal" AND "<driver mutation>"`.

**Tool call — known dependency context**:
Call `STRING_get_network` with the target gene and KRAS (or other driver) to check if there is a known physical or functional interaction that might explain the SL relationship.

---

### Phase 6: Pathway Enrichment of Essential Genes

**Goal**: Identify biological processes and pathways over-represented among essential gene hits.

Steps:
1. Extract the top-N essential genes (recommended: N = 100 or FDR < 0.05 set, whichever is smaller).
2. Submit this gene list to Enrichr via `Enrichr_submit_genelist`. Record the `userListId`.
3. Retrieve results from multiple databases via `Enrichr_get_results`:
   - KEGG_2021_Human
   - GO_Biological_Process_2021
   - Reactome_2022
   - MSigDB_Hallmark_2020
4. Filter results: Adjusted P-value < 0.05.
5. Report top 10 terms per database.

For positive-selection hits (enriched sgRNAs), repeat the enrichment on those genes separately — they may represent tumor suppressor or immune checkpoint pathways.

**Cross-validation**: Call `KEGG_get_pathway` for the top enriched KEGG pathway to retrieve the canonical pathway gene list and confirm overlap with your hits.

Tool call sequence:
1. `mcp__tooluniverse__execute_tool(tool_name="Enrichr_submit_genelist", arguments={"gene_list": [...], "description": "CRISPR_essential_genes"})`
2. Record `userListId` from the response.
3. `mcp__tooluniverse__execute_tool(tool_name="Enrichr_get_results", arguments={"userListId": "<id>", "backgroundType": "KEGG_2021_Human"})`
4. Repeat step 3 for each database.

---

### Phase 7: Drug Target Prioritization

**Goal**: Rank essential gene hits by their potential as therapeutic targets using multi-criteria scoring.

Scoring components (each normalized 0-1):
1. **Essentiality** (weight 0.5): derived from mean LFC (more negative = higher score)
2. **Druggability** (weight 0.3): number of known drug interactions from DGIdb
3. **Expression selectivity** (weight 0.2): if expression data is provided, genes overexpressed in disease vs. normal tissue score higher

Steps:
1. Take the top 50 essential genes by RRA score.
2. For each gene, call `DGIdb_query_gene` to retrieve drug interactions. Record `n_drugs`.
3. If RNA-seq differential expression data is available (e.g., from `tooluniverse-rnaseq-deseq2`), merge log2FC and padj columns.
4. Compute the composite priority score: 0.5 * essentiality_norm + 0.3 * druggability_norm + 0.2 * expression_norm.
5. Sort by priority score descending.
6. For the top 10 targets, call `DGIdb_query_gene` again to enumerate specific drug names and interaction types.
7. Cross-check against literature: call `PubMed_search` with `"<gene>" AND ("clinical trial" OR "drug target") AND cancer` for each top-5 target.

**Tier classification**:
- Tier 1: existing approved drug (n_drugs > 0, interaction_type includes "inhibitor")
- Tier 2: preclinical compound known
- Tier 3: druggable target class (kinase, GPCR, etc.) but no known drug

---

### Phase 8: Report Assembly

**Goal**: Produce a structured, self-contained analysis report.

Report sections:
1. **Screen metadata**: cell line, library, timepoints, replicate count, sequencing depth
2. **QC summary**: library sizes, Gini coefficients, fraction retained after filtering, positive-control behavior
3. **Essential gene summary**: total counts at each tier, top 20 gene table (gene, mean LFC, FDR, BF score, tier)
4. **Pathway enrichment**: top 10 terms per database, heatmap or ranked table
5. **Synthetic lethality** (if applicable): SL candidate table with delta_LFC and delta_rank
6. **Drug target priorities**: top 10 with priority score, drug count, interaction types
7. **Hit validation recommendations**: for each Tier 1 and Tier 2 target, suggest orthogonal validation method (siRNA, small molecule, rescue experiment)
8. **Methods**: normalization method, scoring method, FDR threshold, databases queried
9. **References**: MAGeCK, BAGEL, Enrichr, DGIdb citations

---

## Known Gotchas

**G1 — Copy number amplification artifacts**: In cancer cell lines, sgRNAs targeting amplified regions score as false essential because loss of one of many copies is lethal. Check CNV data (e.g., from TCGA or cell line databases) and flag genes in high-copy-number regions. Tools: `ClinVar_query_gene`, `gnomAD_get_gene` for population-level variant context.

**G2 — Positive controls must deplete**: If essential gene controls (RPS6, RPL5, POLR2A) do not show LFC < -1.5, the screen has likely failed due to insufficient selection time, cell line resistance, or poor library transduction. Do not proceed to scoring; report the failure.

**G3 — Non-targeting controls inflated by early timepoint noise**: At T0, all sgRNAs should have similar counts. If non-targeting controls appear enriched, the library may have been passaged too heavily before T0. Mention this in the QC section.

**G4 — Discordant sgRNAs within one gene**: If 3 of 4 sgRNAs for a gene show strong dropout but 1 shows enrichment, the enriched sgRNA likely has an off-target effect. RRA handles this correctly (it is rank-robust), but mean LFC scoring would give a misleadingly moderate result. Always compare RRA and mean LFC; flag genes where they diverge by more than 50 ranks.

**G5 — Enrichr rate limits**: If submitting many gene lists in rapid succession, Enrichr may return 429 errors. Wait briefly between submissions. The `userListId` from `Enrichr_submit_genelist` is reusable — do not resubmit the same list for each database.

**G6 — DGIdb gene name mismatches**: DGIdb uses HGNC symbols. If a gene symbol is non-standard or an alias, `DGIdb_query_gene` may return zero matches. Always normalize to current HGNC symbols before querying. Use `Ensembl_get_gene_by_symbol` to confirm current symbol.

**G7 — BAGEL scoring requires sufficient reference genes**: The BAGEL Bayes Factor is unreliable with fewer than 10 essential-reference sgRNAs or 5 non-essential-reference sgRNAs. If the library lacks these controls, fall back to RRA-only scoring and note this limitation.

**G8 — Context dependency of essentiality**: DepMap data shows that most "essential" genes are only essential in a subset of cell lines. A gene essential in one cell line may not be a good drug target if it is not essential in the patient's tumor type. Always filter hits against DepMap cell-line-specific dependency scores when available.

---

## Abbreviated Tool Reference

| Tool | Purpose | Key Arguments |
|------|---------|---------------|
| `Enrichr_submit_genelist` | Submit gene list for enrichment | `gene_list`, `description` |
| `Enrichr_get_results` | Retrieve enrichment by database | `userListId`, `backgroundType` |
| `DGIdb_query_gene` | Drug-gene interactions, druggability | `gene_symbol` |
| `STRING_get_network` | Protein interaction network | `identifiers`, `species` |
| `KEGG_get_pathway` | KEGG pathway gene members | `pathway_id` |
| `PubMed_search` | Literature evidence for hits | `query`, `max_results` |
| `ClinVar_query_gene` | Clinical variants for context | `gene_symbol` |
| `gnomAD_get_gene` | Population variant frequency | `gene_symbol` |
| `Ensembl_get_gene_by_symbol` | Canonical gene ID / symbol normalization | `symbol`, `species` |
| `GEO_get_dataset` | Download expression data for integration | `geo_id` |

Full parameter tables, return schemas, and example arguments are in [references/tools.md](references/tools.md).

---

## Use Case Summaries

### Use Case 1: Genome-Wide Essentiality Screen

Apply all 8 phases sequentially. Key decision points:
- If only a gene list is provided (no raw counts), skip Phases 1-3 and begin at Phase 4 using the provided LFC or ranking values.
- Use both RRA and BF scoring; report Tier 1 hits only (FDR < 0.05 AND BF > 10).
- Enrich the Tier 1 set and report top pathways.

### Use Case 2: Synthetic Lethality Screen (e.g., KRAS)

- Run two independent Phases 1-4 (wildtype and mutant cell lines).
- Apply Phase 5 SL detection.
- Prioritize SL hits that are also druggable (Phase 7).
- Validate top SL pairs via `PubMed_search` and `STRING_get_network`.

### Use Case 3: Drug Target Discovery from Screen

- Complete Phases 1-4.
- Skip Phase 5 unless a comparative context is available.
- Emphasize Phase 7: generate a druggability-weighted priority list.
- For each Tier 1 target, retrieve drug names from DGIdb and cite clinical trials via `PubMed_search`.

### Use Case 4: Integration with RNA-seq Expression Data

- Load DESeq2 results (log2FoldChange, padj) from `tooluniverse-rnaseq-deseq2`.
- Merge with CRISPR gene scores on gene symbol.
- Highlight genes that are both screen-essential (LFC < -1) and transcriptionally upregulated in disease (log2FC > 1, padj < 0.05) — these are the highest-confidence targets.

---

## Best Practices

1. Use validated sgRNA libraries (Brunello for KO, CRISPRa-v2 for activation, CRISPRi-v2 for interference).
2. Minimum 3 biological replicates per condition for FDR-controlled calling.
3. Aim for 500-1000 reads/sgRNA at T0; lower depths increase noise in RRA ranking.
4. Target 14-21 days (5-7 cell doublings) for dropout screens; shorter windows miss slowly-acting dependencies.
5. Always include at least 500 non-targeting control sgRNAs in the library.
6. When reporting, distinguish pan-essential (essential in DepMap >= 90% of lines) from context-specific essentials.
7. Validate top candidates by at least one orthogonal method (siRNA, dTAG, small molecule inhibitor, rescue overexpression) before advancing to drug development.

---

## References

- Li W, et al. (2014) MAGeCK enables robust identification of essential genes from genome-scale CRISPR/Cas9 knockout screens. *Genome Biology* 15:554.
- Hart T, et al. (2015) High-Resolution CRISPR Screens Reveal Fitness Genes and Genotype-Specific Cancer Liabilities. *Cell* 163:1515-1526.
- Meyers RM, et al. (2017) Computational correction of copy number effect improves specificity of CRISPR-Cas9 essentiality screens. *Nature Genetics* 49:1779-1784.
- Tsherniak A, et al. (2017) Defining a Cancer Dependency Map. *Cell* 170:564-576. (DepMap)
- Kanehisa M, et al. (2023) KEGG for taxonomy-based analysis of pathways and genomes. *Nucleic Acids Research* 51:D587-D592.
- Kuleshov MV, et al. (2016) Enrichr: a comprehensive gene set enrichment analysis web server. *Nucleic Acids Research* 44:W90-W97.
