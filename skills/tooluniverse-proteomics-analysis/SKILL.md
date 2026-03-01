---
name: tooluniverse-proteomics-analysis
description: Analyze mass spectrometry proteomics data including protein quantification, differential expression, post-translational modifications (PTMs), and protein-protein interactions. Processes MaxQuant, Spectronaut, DIA-NN, and other MS platform outputs. Performs normalization, statistical analysis, pathway enrichment, and integration with transcriptomics. Use when analyzing proteomics data, comparing protein abundance between conditions, identifying PTM changes, studying protein complexes, integrating protein and RNA data, discovering protein biomarkers, or conducting quantitative proteomics experiments.
---

# Proteomics Analysis

Comprehensive analysis of mass spectrometry-based proteomics data from protein identification through quantification, differential expression, PTM characterization, and systems-level interpretation.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Platform-aware loading** - Detect input format (MaxQuant, Spectronaut, DIA-NN, Proteome Discoverer) before processing
3. **DIA vs DDA awareness** - DDA (data-dependent) has more missing values; DIA (data-independent) is more complete
4. **PTM localization filtering** - Only use phosphosites with localization probability > 0.75
5. **Multiple testing correction** - Always apply Benjamini-Hochberg FDR; never report uncorrected p-values
6. **Tool parameter verification** - Call `get_tool_info` before unfamiliar tools
7. **English-first queries** - Use English in all tool calls, even if the user writes in another language. Respond in the user's language

---

## When to Use This Skill

**Triggers**:
- User has proteomics data (MS output files: proteinGroups.txt, report.tsv, etc.)
- Questions about protein abundance or expression changes
- Differential protein expression analysis requests
- PTM analysis (phosphorylation, acetylation, ubiquitination, methylation)
- Protein-RNA correlation or translation efficiency analysis
- Multi-omics integration involving proteomics
- Protein complex or interaction network analysis
- Proteomics biomarker discovery

**Example Questions This Skill Solves**:
1. "Analyze this MaxQuant output for differential protein expression"
2. "Which proteins are significantly upregulated in disease vs control?"
3. "Correlate protein abundance with mRNA expression"
4. "What post-translational modifications change between conditions?"
5. "Identify protein complexes in my co-IP MS data"
6. "Which pathways are enriched in differentially expressed proteins?"
7. "Find protein biomarkers for disease classification"
8. "Compare protein and RNA levels to identify translation-regulated genes"

**NOT for** (use other skills instead):
- RNA-seq differential expression only -> Use `tooluniverse-rnaseq-deseq2`
- Pathway enrichment only (no proteomics data) -> Use `tooluniverse-gene-enrichment`
- Protein-protein interactions only -> Use `tooluniverse-protein-interactions`
- Multi-omics integration -> Use `tooluniverse-multi-omics-integration`

---

## Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Data Import** | MaxQuant, Spectronaut, DIA-NN, Proteome Discoverer, FragPipe outputs |
| **Quality Control** | Missing value analysis, intensity distributions, sample clustering |
| **Normalization** | Median, quantile, TMM, VSN normalization methods |
| **Imputation** | MinProb, KNN, QRILC for missing values |
| **Differential Expression** | Limma-style testing, t-test, ANOVA with BH correction |
| **PTM Analysis** | Phospho-site localization, PTM enrichment, kinase prediction |
| **Protein-RNA Integration** | Correlation analysis, translation efficiency |
| **Pathway Enrichment** | Over-representation and GSEA for protein sets |
| **PPI Analysis** | Protein complex detection, interaction networks via STRING/IntAct |
| **Reporting** | Summary statistics, volcano plots, heatmaps, pathway diagrams |

---

## Workflow Overview

```
Input: MS Proteomics Data
    |
    v
Phase 1: Data Import & QC
    |-- Detect format (MaxQuant / Spectronaut / DIA-NN / Proteome Discoverer)
    |-- Parse protein groups, intensities, modifications
    |-- Quality control: missing values, intensity distributions, PCA
    |
    v
Phase 2: Preprocessing
    |-- Filter low-confidence proteins (2+ unique peptides, remove CON__/REV__)
    |-- Handle missing values (imputation strategy depends on DIA vs DDA)
    |-- Log2-transform intensities
    |-- Normalize across samples
    |
    v
Phase 3: Differential Expression Analysis
    |-- Statistical testing (limma-style, t-test, ANOVA)
    |-- Multiple testing correction (Benjamini-Hochberg FDR)
    |-- Fold change calculation
    |-- Default thresholds: adj. p < 0.05 AND |log2FC| > 1
    |
    v
Phase 4: PTM Analysis (if applicable)
    |-- Filter phosphosites by localization probability > 0.75
    |-- Differential phosphorylation per site
    |-- Kinase-substrate prediction via OmniPath
    |-- PTM enrichment analysis
    |
    v
Phase 5: Functional Enrichment
    |-- GO (BP, MF, CC) enrichment via Enrichr
    |-- KEGG and Reactome pathway enrichment
    |-- Protein complex enrichment (STRING functional enrichment)
    |
    v
Phase 6: Protein-Protein Interactions
    |-- Query STRING for interaction networks
    |-- PPI enrichment test (are proteins more connected than random?)
    |-- Network clustering for functional modules
    |-- Hub protein identification
    |
    v
Phase 7: Multi-Omics Integration (optional)
    |-- Match proteins to RNA-seq data by gene symbol
    |-- Spearman correlation: protein vs mRNA per gene
    |-- Classify regulation: transcriptional / post-transcriptional / degradation
    |
    v
Phase 8: Generate Report
    |-- Summary statistics (proteins quantified, DE count, top hits)
    |-- Volcano plot, heatmap, pathway diagram descriptions
    |-- Protein network module summary
    |-- Biomarker candidates
```

---

## Phase Details

### Phase 0: Tool Parameter Verification

Before calling any unfamiliar tool, verify its parameters using `get_tool_info`:

```
mcp__tooluniverse__execute_tool(
    tool_name="mcp__tooluniverse__get_tool_info",
    arguments={"tool_names": "STRING_get_network"}
)
```

### Known Parameter Corrections

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `STRING_get_network` | `protein_list` | `identifiers` (newline-separated string) |
| `STRING_functional_enrichment` | `proteins` | `protein_ids` (list) |
| `OmniPath_get_enzyme_substrate` | `kinase` | `enzymes` |
| `EBIProteins_get_proteomics_ptm` | `uniprot_id` | `accession` |
| `enrichr_gene_enrichment_analysis` | `genes` | `gene_list` (list) |

---

### Phase 1: Data Import & Quality Control

**Objective**: Load proteomics data and assess data quality before any analysis.

**Supported input formats**:

| Platform | Key Files | Notes |
|----------|-----------|-------|
| **MaxQuant (DDA)** | `proteinGroups.txt`, `Phospho (STY)Sites.txt` | LFQ intensity columns; contaminants marked CON__ |
| **Spectronaut (DIA)** | `*_Report.tsv` | Fewer missing values than MaxQuant |
| **DIA-NN (DIA)** | `report.tsv`, `report.pr_matrix.tsv` | Protein groups in pr_matrix |
| **Proteome Discoverer** | `*_Proteins.txt`, `*_PSMs.txt` | Requires Abundance column extraction |
| **FragPipe** | `combined_protein.tsv` | Gene-level aggregation pre-done |

**DIA vs DDA decision for imputation**:
- DDA (MaxQuant LFQ): missing values common (15-30%); use MinProb (assumes MNAR — missing not at random)
- DIA (Spectronaut/DIA-NN): missing values rare (<5%); KNN imputation preferred

**Quality control steps (in order)**:

1. **Missing value assessment** — Calculate % missing per protein and per sample. Flag proteins with >70% missing.
2. **Intensity distribution** — Compare log10 intensity distributions per sample. Expect similar medians and spreads.
3. **Sample correlation** — Pearson correlation of log-transformed intensities. Expect r > 0.90 within replicates.
4. **PCA** — PC1/PC2 plot colored by condition. Expect clear group separation.

**QC thresholds**:
- Within-replicate correlation r < 0.85: flag as potential outlier
- Missing per sample > 50%: flag sample for exclusion
- PC1 explained variance < 15%: data may lack strong signal

---

### Phase 2: Preprocessing & Normalization

**Objective**: Clean data and normalize for fair cross-sample comparison.

**Filtering criteria** (apply before normalization):
- Keep proteins with at least 2 unique peptides
- Remove contaminants (IDs containing `CON__`) and reverse sequences (`REV__`)
- Require detection in at least N samples per group (N >= minimum replicates per condition)

**Imputation methods**:

| Method | When to Use | How |
|--------|-------------|-----|
| **MinProb** | DDA, MNAR (missing = low abundance) | Random draw from left tail of intensity distribution; shift = 1.8 SD below minimum |
| **KNN** | DIA, MAR (missing at random) | K-nearest neighbors on log-transformed matrix |
| **QRILC** | Mixed patterns | Quantile regression imputation from left-censored distribution |

**Normalization methods**:

| Method | When to Use |
|--------|-------------|
| **Median normalization** | Default for most datasets; divide by per-sample median |
| **Quantile normalization** | When distributions are highly variable across samples |
| **TMM** | When a few highly abundant proteins dominate intensity |
| **VSN** | When variance scales with mean (common in label-free) |

Apply normalization AFTER log2 transformation.

---

### Phase 3: Differential Expression Analysis

**Objective**: Identify proteins with significant abundance changes between conditions.

**Statistical testing approach**:
- For 2-group comparisons: Welch t-test or limma-style moderated t-test
- For 3+ groups: one-way ANOVA followed by pairwise post-hoc tests
- For matched samples: paired t-test
- For MS-specific analysis: MSstats framework (handles technical replicates and runs)

**Required outputs per protein**:
- Mean log2 intensity in each group
- log2 Fold Change (group2 - group1 in log space)
- p-value (from statistical test)
- Adjusted p-value (Benjamini-Hochberg FDR)
- Significance classification

**Default significance thresholds** (adjust based on user preference):
- adj. p-value < 0.05 AND |log2FC| > 1.0

**Volcano plot description** for report:
- X-axis: log2FC; Y-axis: -log10(p-value)
- Red: significant up; blue: significant down; gray: not significant
- Label top 10 hits by adjusted p-value

---

### Phase 4: PTM Analysis

**Objective**: Analyze post-translational modification site-level changes.

**Input files**:
- MaxQuant: `Phospho (STY)Sites.txt` (phosphorylation), `modificationSpecificPeptides.txt` (others)
- Spectronaut: PTM-enabled report with site-level quantities
- DIA-NN: PTM localization with site annotation

**Phosphoproteomics workflow**:

1. **Load phospho file** - Extract site intensity columns
2. **Filter by localization probability** - Keep sites with probability > 0.75 (use 0.9 for high-confidence analyses)
3. **Construct site IDs** - Format: `GENE_S123` (gene name + amino acid + position)
4. **Normalize and impute** - Same methods as protein-level, but applied to phosphosites
5. **Differential phosphorylation** - Same statistical approach as Phase 3
6. **Kinase prediction** - Query OmniPath for upstream kinases of significant phosphosites

**Kinase-substrate query via OmniPath** (`OmniPath_get_enzyme_substrate`):
- Pass phosphosite gene as `substrates` parameter
- Returns kinase -> substrate edges with residue positions and modification types
- Cross-reference your significant sites against the returned substrate positions

**PTM types supported by EBI Proteins** (`EBIProteins_get_proteomics_ptm`):
- Phosphorylation, acetylation, ubiquitination, methylation, sumoylation
- Returns: position, modification type, evidence source (PeptideAtlas, ProteomicsDB, MaxQB)

**Common PTM-specific considerations**:
- Phosphoproteomics: normalize by total protein abundance (phospho-peptide intensity / protein intensity) when possible
- Ubiquitinomics: enriched via K-GG (diglycine) remnant antibody; filter for K residues only
- Acetylomics: check for crosstalk with histone modifications in histone-enriched samples

---

### Phase 5: Functional Enrichment

**Objective**: Interpret biological meaning of protein changes via pathway analysis.

**Step-by-step approach**:

1. **Extract gene names** from significant DE proteins (use gene symbol, not protein accession)
2. **Run Enrichr** via `enrichr_gene_enrichment_analysis`:
   - Pass `gene_list` as list of gene symbols
   - Use `libs`: `["GO_Biological_Process_2023", "KEGG_2021_Human", "Reactome_Pathways_2024", "MSigDB_Hallmark_2020"]`
3. **Cross-validate with Reactome** via `Reactome_map_uniprot_to_pathways` for top proteins
4. **Run STRING functional enrichment** via `STRING_functional_enrichment`:
   - Pass `protein_ids` as gene symbol list
   - Try categories: `"Process"`, `"KEGG"`, `"Reactome"` separately
5. **Protein complex enrichment** - Test via `STRING_ppi_enrichment` to check if significant proteins form a network

Report top 10 terms per database; separate upregulated and downregulated protein enrichments.

---

### Phase 6: Protein-Protein Interactions

**Objective**: Build interaction networks and identify functional modules.

**Workflow**:
1. `STRING_get_network` — pass `identifiers` as **newline-separated** gene symbols; `required_score`: 400 (medium), 700 (high), 900 (highest)
2. `STRING_ppi_enrichment` — test if proteins form a denser network than random (p < 0.05 confirms real functional module)
3. Identify hub proteins by node degree
4. `STRING_functional_enrichment` per detected cluster to annotate modules
5. `intact_get_interactions` — validate key edges with curated experimental data (higher specificity than STRING)

---

### Phase 7: Multi-Omics Integration

**Objective**: Integrate proteomics with RNA-seq to dissect transcriptional vs post-transcriptional regulation.

**Protein-RNA correlation workflow**:
1. Match samples present in both datasets; align by gene symbol
2. Spearman correlation per gene across matched samples
3. Expected global correlation: r ~ 0.4–0.6 (moderate)

**Regulatory classification**:

| Pattern | Interpretation |
|---------|----------------|
| r > 0.6, both up/down | Transcriptional regulation |
| r < 0.2, protein up / RNA down | Translational upregulation or protein stabilization |
| r < 0.2, protein down / RNA up | Protein degradation or translational repression |
| r > 0.6, protein changes / RNA unchanged | Likely batch effect — investigate |

Report top 20 discordant genes as post-transcriptional regulation candidates.
Use `tooluniverse-multi-omics-integration` for MOFA or factor-level integration.

---

### Phase 8: Report Generation

**Report file**: `[project_name]_proteomics_report.md`

Create this file FIRST with placeholder sections, then fill progressively.

**Required sections** (initialize all with `[Researching...]`, then fill progressively):

1. **Dataset Summary** — platform, software version, sample counts, proteins identified and quantified, missing value rate
2. **Quality Control** — within-group correlation range, PCA variance explained, outlier samples flagged
3. **Differential Expression** — total significant (adj. p < 0.05, |log2FC| > 1), up/down counts, top 10 up and top 10 down with statistics
4. **PTM Summary** (if applicable) — phosphosites quantified, differentially phosphorylated sites, top predicted kinases
5. **Pathway Enrichment** — top 5 pathways (up and down separately), source databases
6. **Protein Network** — node/edge counts, confidence threshold, PPI enrichment p-value, functional modules
7. **Protein-RNA Integration** (if applicable) — global correlation, transcriptionally vs post-transcriptionally regulated counts
8. **Biomarker Candidates** — top proteins ranked by effect size and significance
9. **Biological Interpretation** — 1-3 paragraph narrative

---

## Known Gotchas

**Data loading**:
- MaxQuant LFQ columns are named `LFQ intensity [sample]` — extract these, NOT `Intensity [sample]` (unnormalized)
- MaxQuant proteinGroups.txt has multi-gene rows (semicolon-separated); take the first gene name for enrichment
- DIA-NN `report.tsv` is peptide-level; use `report.pr_matrix.tsv` for protein-level analysis
- Spectronaut reports vary by version; look for `PG.Quantity` or `PG.NrOfStrippedSequencesMeasured` columns

**Missing value imputation**:
- Do NOT impute before filtering — apply protein/sample filters first, then impute
- MinProb requires log-transformed data as input; impute AFTER log2 transformation
- Never impute more than 40% of values per protein — results become unreliable

**Statistical testing**:
- For very small sample sizes (n < 3 per group), report effect sizes with caution; flag results
- limma borrows strength across proteins (empirical Bayes); better than plain t-test for n < 10
- Do not use raw p-values for cutoffs — always use BH-adjusted p-values

**PTM-specific**:
- Phospho (STY)Sites.txt from MaxQuant has multiplicity (e.g., a peptide with 2 phospho groups = 2 rows); aggregate by site position
- "Class I" phosphosites = localization probability > 0.75 — required for reliable site-level analysis
- Check for co-eluting phospho isoforms when localization probabilities are ambiguous

**STRING tool calls**:
- `STRING_get_network` `identifiers` must be newline-separated (`"\n".join(genes)`) not comma-separated
- `STRING_functional_enrichment` `category` is one value at a time — run separately for GO, KEGG, Reactome
- STRING scores are 0-1000 internally; `required_score=700` = high confidence

**Enrichment analysis**:
- Use gene symbols (not accessions) for Enrichr; convert with MyGene if needed
- Background gene list matters — use all quantified proteins as background, not genome-wide
- Separate enrichment runs for upregulated and downregulated proteins

**Protein-RNA integration**:
- Match samples by name carefully — proteomics and RNA-seq often have different naming conventions
- Protein-RNA correlation is often sample-count-limited; report confidence intervals
- Global correlation r < 0.3 may indicate sample swap or data quality issues — investigate before reporting

---

## Integration with ToolUniverse

| Skill / Tool | Used For | Phase |
|--------|----------|-------|
| `enrichr_gene_enrichment_analysis` | GO, KEGG, Reactome enrichment | Phase 5 |
| `STRING_functional_enrichment` | Network-aware pathway enrichment | Phase 5, 6 |
| `STRING_get_network` | PPI network construction | Phase 6 |
| `STRING_ppi_enrichment` | Test if proteins form real network | Phase 6 |
| `OmniPath_get_enzyme_substrate` | Kinase-substrate prediction for phosphosites | Phase 4 |
| `EBIProteins_get_proteomics_ptm` | PTM evidence from databases | Phase 4 |
| `EBIProteins_get_proteomics_peptides` | Peptide-level MS evidence | Phase 1 |
| `intact_get_interactions` | Curated PPI validation | Phase 6 |
| `Reactome_map_uniprot_to_pathways` | Single-protein pathway mapping | Phase 5 |
| `tooluniverse-gene-enrichment` | In-depth enrichment analysis | Phase 5 |
| `tooluniverse-rnaseq-deseq2` | RNA-seq data for integration | Phase 7 |
| `tooluniverse-multi-omics-integration` | Cross-omics factor analysis | Phase 7 |

For full parameter tables, see [references/tools.md](references/tools.md).

---

## Example Use Cases

### Use Case 1: Cancer Proteomics (DDA, MaxQuant)

**Question**: "Analyze MaxQuant LFQ data from breast cancer vs normal tissue (n=10 each)"

**Workflow summary**:
1. Load `proteinGroups.txt`, extract LFQ intensity columns
2. Remove contaminants (CON__) and reverse (REV__); keep 2+ peptide proteins
3. Replace zeros with NaN, log2 transform, MinProb impute, median normalize
4. Welch t-test + BH correction; volcano plot
5. `enrichr_gene_enrichment_analysis` on up/down gene lists separately
6. `STRING_get_network` at score 700; `STRING_ppi_enrichment` to confirm module
7. Report: ~4,500 proteins quantified, ~400 significant, cell cycle and metabolic pathways enriched

### Use Case 2: Phosphoproteomics Signaling (after kinase inhibitor treatment)

**Question**: "What kinase signaling is activated in response to drug treatment?"

**Workflow summary**:
1. Load `Phospho (STY)Sites.txt`; filter localization probability > 0.75
2. Construct site IDs (GENE_S123 format); log2 transform, impute, normalize
3. t-test per phosphosite + BH correction; identify significant sites
4. For each significant site's gene, call `OmniPath_get_enzyme_substrate` with gene as `substrates`
5. Count which kinases appear most frequently as upstream regulators
6. `enrichr_gene_enrichment_analysis` on significant phosphosite gene list
7. Report: top kinases predicted (e.g., CDK1, MAPK1, AKT1), signaling pathway activation

### Use Case 3: DIA Proteomics with Protein-RNA Correlation

**Question**: "Which proteins are regulated post-transcriptionally?"

**Workflow summary**:
1. Load DIA-NN `report.pr_matrix.tsv`; minimal missing values expected
2. KNN impute, quantile normalize, log2 transform
3. Differential expression (t-test + BH)
4. Load matched RNA-seq results (normalized counts or log-TPM)
5. Spearman correlation per gene across matched samples
6. Classify genes: r < 0.2 with discordant direction = post-transcriptional regulation
7. `enrichr_gene_enrichment_analysis` on post-transcriptional gene list
8. Report: ~90 translation-regulated proteins enriched for RNA-binding protein substrates

---

## Quantified Minimums

| Component | Requirement |
|-----------|-------------|
| Proteins quantified | At least 500 for meaningful differential analysis |
| Replicates | At least 3 per condition (limma requires minimum 2) |
| Filtering | 2+ unique peptides per protein; remove CON__/REV__ |
| Statistical test | t-test or limma with BH multiple testing correction |
| Pathway enrichment | At least one method (GO-BP, KEGG, or Reactome) |
| Report sections | Dataset summary, QC, DE results, pathways, interpretation |

---

## Limitations

- **Platform-specific**: Optimized for MS-based proteomics (not Western blot or ELISA quantification)
- **Missing values**: High missing rate (>50% per protein) limits statistical power in DDA experiments
- **PTM coverage**: Requires enrichment protocols for comprehensive phospho/ubiquitin/acetyl profiling
- **Absolute quantification**: Provides relative abundance only (unless TMT, SILAC, or iBAQ used)
- **Protein isoforms**: Typically collapsed to gene level; isoform-resolved analysis requires different tools
- **Dynamic range**: MS has limited dynamic range (~4 orders of magnitude vs 6+ for transcriptomics)
- **Protein-RNA correlation**: Requires matched samples and well-normalized data from both assays

---

## References

**Methods**:
- MaxQuant: https://doi.org/10.1038/nbt.1511
- Limma for proteomics: https://doi.org/10.1093/nar/gkv007
- DEP workflow: https://doi.org/10.1038/nprot.2018.107
- MSstats: https://doi.org/10.1021/pr400880y

**Databases**:
- STRING: https://string-db.org
- PhosphoSitePlus: https://www.phosphosite.org
- OmniPath (PTMs): https://omnipathdb.org
- CORUM (protein complexes): https://mips.helmholtz-muenchen.de/corum
