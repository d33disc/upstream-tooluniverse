---
name: tooluniverse-metabolomics-analysis
description: Analyze metabolomics data including metabolite identification, quantification, pathway analysis, and metabolic flux. Processes LC-MS, GC-MS, NMR data from targeted and untargeted experiments. Performs normalization, statistical analysis, pathway enrichment, metabolite-enzyme integration, and biomarker discovery. Use when analyzing metabolomics datasets, identifying differential metabolites, studying metabolic pathways, integrating with transcriptomics/proteomics, discovering metabolic biomarkers, performing flux balance analysis, or characterizing metabolic phenotypes in disease, drug response, or physiological conditions.
---

# Metabolomics Analysis

Comprehensive analysis of metabolomics data from metabolite identification through quantification, statistical analysis, pathway interpretation, and integration with other omics layers.

**IMPORTANT**: This skill targets LLM agents in MCP clients. All tool calls use `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`. No Python SDK code is required.

---

## When to Use This Skill

**Triggers**:
- User has metabolomics data (LC-MS, GC-MS, NMR)
- Questions about metabolite abundance or concentrations
- Differential metabolite analysis requests
- Metabolic pathway analysis
- Multi-omics integration with metabolomics
- Metabolic biomarker discovery
- Flux balance analysis or metabolic modeling
- Metabolite-enzyme correlation

**Example Questions**:
1. "Analyze this LC-MS metabolomics data for differential metabolites"
2. "Which metabolic pathways are dysregulated between conditions?"
3. "Identify metabolite biomarkers for disease classification"
4. "Correlate metabolite levels with enzyme expression"
5. "Perform pathway enrichment for differential metabolites"
6. "Integrate metabolomics with transcriptomics data"
7. "Characterize the metabolic phenotype of this cell line"

**NOT for**:
- Pure chemical property lookup only → use `tooluniverse-chemical-compound-retrieval`
- Gene enrichment only (no metabolomics data) → use `tooluniverse-gene-enrichment`

---

## Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Metabolite Identification** | Match to HMDB, KEGG, PubChem, MetaboLights via m/z, exact mass, or name |
| **Quality Control** | Peak quality, blank subtraction, internal standard normalization |
| **Normalization** | Probabilistic quotient (PQN), total ion current (TIC), internal standards |
| **Statistical Analysis** | Univariate and multivariate (PCA, PLS-DA, OPLS-DA) |
| **Differential Analysis** | Identify significant metabolite changes with FDR correction |
| **Pathway Enrichment** | KEGG, MetaboAnalyst, Reactome metabolic pathway analysis |
| **Metabolite-Enzyme Integration** | Correlate with expression data from transcriptomics/proteomics |
| **Biomarker Discovery** | Multi-metabolite signatures using random forest or LASSO |

---

## Workflow Overview

```
Input: Metabolomics Data (Peak Table or Spectra)
    |
    v
Phase 1: Metabolite Identification
    |-- Match features by m/z, exact mass, or name
    |-- Query HMDB, MetaboWorkbench, KEGG
    |-- Standardize IDs via MetaboAnalyst_name_to_id
    |-- Assign confidence levels (1-4)
    |
    v
Phase 2: Quality Control & Filtering
    |-- Assess CV in QC samples (threshold: <30%)
    |-- Blank subtraction (sample/blank ratio >3)
    |-- Filter missing values (>50% threshold)
    |
    v
Phase 3: Normalization
    |-- TIC, PQN, or internal standard normalization
    |-- Batch effect correction (if multi-batch)
    |-- Log2 transform or Pareto scaling
    |
    v
Phase 4: Exploratory Analysis
    |-- PCA for sample clustering and outlier detection
    |-- PLS-DA for supervised discrimination
    |-- Sample correlation heatmaps
    |
    v
Phase 5: Differential Analysis
    |-- t-test/Wilcoxon + FDR correction (BH)
    |-- Fold change calculation (log2FC)
    |-- Thresholds: adj. p < 0.05, |log2FC| > 1
    |
    v
Phase 6: Pathway Enrichment
    |-- MetaboAnalyst_pathway_enrichment (KEGG ORA)
    |-- MetaboAnalyst_biomarker_enrichment (SMPDB/HMDB sets)
    |-- Reactome or KEGG pathway topology (optional)
    |
    v
Phase 7: Multi-Omics Integration
    |-- Correlate metabolites with enzyme expression
    |-- Pathway-level integration (metabolite + gene FC)
    |-- Metabolic flux inference
    |
    v
Phase 8: Report
    |-- QC summary, differential metabolites table
    |-- Pathway enrichment results
    |-- Biological interpretation, biomarker panel
```

---

## Phase Details

### Phase 1: Metabolite Identification

**Objective**: Identify metabolites from LC-MS/GC-MS features or metabolite name lists.

**Input types**:
- **Peak tables**: Pre-processed metabolite abundances (rows = samples, columns = metabolites)
- **Feature lists**: m/z + RT pairs from untargeted MS
- **Named metabolite lists**: Common names from targeted panels

**Identification strategy by data type**:

| Data Available | Primary Tool | Fallback |
|----------------|--------------|----------|
| m/z value (MS) | `MetabolomicsWorkbench_search_by_mz` | `MetabolomicsWorkbench_search_by_exact_mass` |
| Metabolite name | `MetaboAnalyst_name_to_id` | `HMDB_search` |
| HMDB ID | `HMDB_get_metabolite` | — |
| PubChem CID | `MetabolomicsWorkbench_get_comp_by_pubc_cid` | — |
| Study-level | `metabolights_get_study` | `MetabolomicsWorkbench_get_study` |

**Identification confidence levels**:
```
Level 1: Confirmed with authentic standard (MS + RT match)
Level 2: Probable structure (accurate mass + MS/MS)
Level 3: Tentative match (accurate mass only, ≤5 ppm)
Level 4: Unknown metabolite (feature only)
```

**Workflow**:

1. For each feature or metabolite name, call `MetaboAnalyst_name_to_id` with the metabolite name list. This resolves to KEGG, HMDB, PubChem, and ChEBI IDs simultaneously.

2. For unresolved features with m/z, call `MetabolomicsWorkbench_search_by_mz` with the m/z value and ion mode. Use a mass tolerance appropriate to your instrument (5 ppm for high-resolution Orbitrap, 0.5 Da for low-resolution).

3. For features resolved to HMDB IDs, call `HMDB_get_metabolite` to retrieve pathways, chemical formula, and biological roles. Call `HMDB_get_diseases` to capture biomarker associations.

4. Retrieve RefMet-standardized names via `MetabolomicsWorkbench_get_refmet_info` for cross-study harmonization.

**Key gotchas**:
- `MetabolomicsWorkbench_search_by_mz` searches against RefMet, which prioritizes small molecules with biological relevance. Lipids may require separate lipidomics databases.
- Pass metabolite names exactly as reported; abbreviations (e.g., "alpha-KG" vs "alpha-ketoglutarate") may not resolve — try both.

---

### Phase 2: Quality Control & Filtering

**Objective**: Remove low-quality features and background noise before statistical analysis.

**QC criteria**:

| Metric | Acceptable Threshold | Action if Failed |
|--------|---------------------|------------------|
| CV in QC samples | <30% | Remove metabolite |
| Sample/blank ratio | >3x | Remove metabolite (contaminant) |
| Missing values | <50% | Remove metabolite; impute if 20-50% |
| Internal standard recovery | 80-120% | Flag sample; exclude if <70% |
| Total ion current | Within 2 SD of median | Flag as outlier sample |

**Steps**:
1. Separate samples by type: biological samples, QC pooled samples, blanks
2. Compute per-metabolite CV across QC samples; remove those exceeding threshold
3. Compute sample/blank ratios; remove metabolites dominated by background
4. Assess missing value pattern; impute remaining missing values using half-minimum or KNN
5. Flag samples with anomalous total signal for potential exclusion

No ToolUniverse tool is required for these steps — they are computed from the peak table directly. Document removed counts in the QC section of the final report.

---

### Phase 3: Normalization

**Objective**: Account for technical variation and enable fair cross-sample comparison.

**Choose normalization method based on biology**:

| Method | When to Use | Notes |
|--------|------------|-------|
| **TIC** | Global abundance expected similar | Sensitive to large metabolite changes |
| **PQN** | Some metabolites expected to be highly changed | More robust than TIC |
| **Internal standard** | IS was spiked before extraction | Most accurate; requires IS metabolite column |
| **LOESS** | Large batch effects, reference samples available | Corrects run-order drift |

After normalization, apply **log2 transformation** to stabilize variance. Use **Pareto scaling** (divide by square root of std) rather than auto-scaling for metabolomics, as auto-scaling over-emphasizes low-abundance noisy features.

No ToolUniverse tool required — normalization is performed computationally on the peak table.

---

### Phase 4: Exploratory Analysis

**Objective**: Visualize sample structure, detect outliers, and validate group separation.

**Steps**:
1. Perform **PCA** on normalized, log2-transformed data. Report variance explained by PC1/PC2. Samples that cluster separately from their group are outlier candidates.
2. Perform **PLS-DA** for supervised discrimination (requires group labels). Report R2X, R2Y, Q2 via cross-validation. Q2 > 0.5 indicates good predictive separation; Q2 < 0 indicates overfitting.
3. Generate **sample correlation heatmap** to identify batch structure or sample swaps.

**Acceptable outcomes before proceeding**:
- PCA shows reasonable group separation
- No obvious batch structure confounding group separation
- Outlier samples identified and decision made (exclude or flag)

No ToolUniverse tool required for this phase.

---

### Phase 5: Differential Metabolite Analysis

**Objective**: Identify metabolites with statistically significant abundance changes between conditions.

**Statistical workflow**:

1. For two-group comparison: Welch's t-test (unequal variances) or Wilcoxon rank-sum test (non-parametric)
2. For multi-group: one-way ANOVA with Tukey post-hoc
3. Compute fold change: log2(mean_group2 / mean_group1)
4. Apply Benjamini-Hochberg FDR correction to all p-values
5. Apply significance thresholds: adj. p < 0.05 AND |log2FC| > 1.0

**Output**: Table of significant metabolites with columns: metabolite, log2FC, p_value, adj_p_value, mean_group1, mean_group2, direction (up/down).

No ToolUniverse tool required for core statistics — all computed from the peak table. ToolUniverse tools are used in Phase 1 to obtain IDs and in Phase 6 for pathway analysis.

---

### Phase 6: Metabolic Pathway Enrichment

**Objective**: Interpret differential metabolites at the pathway level to identify dysregulated metabolic processes.

**Primary approach — Over-Representation Analysis (ORA)**:

Call `MetaboAnalyst_pathway_enrichment` with the list of significant differential metabolite names and the organism code. This tool:
- Maps metabolite names to KEGG compound IDs internally
- Tests pathway enrichment using hypergeometric test
- Returns pathways with p-value, FDR, fold enrichment, and hit metabolite list

**Secondary approach — Biomarker set enrichment**:

Call `MetaboAnalyst_biomarker_enrichment` with the same metabolite list. This tests against curated metabolite sets from SMPDB and HMDB (glycolysis, TCA cycle, amino acid pathways, etc.) and is complementary to KEGG ORA.

**Pathway details retrieval**:
- For a specific KEGG pathway, call `kegg_get_pathway_info` with the pathway ID (e.g., `hsa00010` for Glycolysis)
- To get all compounds in a KEGG pathway, call `KEGG_get_compound` for individual compound details
- For Reactome pathway context, call `ReactomeContent_search` with pathway keywords, then `Reactome_get_pathway` for details

**Pathway topology considerations**:
- Metabolites at pathway hubs (many connections) have higher impact on pathway score
- Metabolites at pathway bottlenecks (connecting two major branches) are particularly informative
- KEGG pathway topology is not automatically computed by `MetaboAnalyst_pathway_enrichment` — report ORA results and manually assess centrality based on metabolic knowledge

**Key gotchas**:
- `MetaboAnalyst_pathway_enrichment` requires metabolite common names matching KEGG nomenclature. Use `MetaboAnalyst_name_to_id` first to check which names resolve correctly. Submit only the names that map successfully.
- ORA requires a background set. The default background is all KEGG metabolites for the organism. Results are only meaningful if your identified metabolite list is a reasonable coverage of the metabolome.
- Very short metabolite lists (<10 metabolites) produce unreliable enrichment p-values.

---

### Phase 7: Multi-Omics Integration

**Objective**: Integrate metabolomics with transcriptomics or proteomics to link metabolite changes to enzyme activity.

**Metabolite-enzyme linking**:

1. For each significant metabolite, retrieve its associated enzymes (reactions) from KEGG:
   - Call `KEGG_get_compound` with the KEGG compound ID. The response includes linked enzymes (EC numbers) and reactions.
   - Call `kegg_get_pathway_info` for the relevant pathway to see which enzymes catalyze reactions producing or consuming this metabolite.

2. Cross-reference enzyme gene symbols with transcriptomics DE results:
   - Substrate metabolite increased + producing enzyme decreased → accumulation (enzyme bottleneck)
   - Product metabolite increased + catalyzing enzyme increased → pathway activation (flux increase)
   - Opposite direction changes suggest regulation or feedback

3. For pathway-level integration, score each pathway by combining:
   - Fraction of metabolites significantly changed
   - Fraction of pathway enzymes significantly changed
   - Directional concordance (metabolite and enzyme changes in expected relationship)

**Enzyme lookup tools**:

| Goal | Tool | Key Arguments |
|------|------|---------------|
| Get metabolite-linked reactions | `KEGG_get_compound` | `compound_id` |
| Get genes in metabolic pathway | `KEGG_get_pathway_genes` | `pathway_id` |
| Get pathway with reactions | `kegg_get_pathway_info` | `pathway_id` |

---

### Phase 8: Report Generation

**Structure of the metabolomics analysis report**:

```markdown
## Dataset Summary
- Platform, method (targeted/untargeted), instrument
- Sample counts per group
- Metabolites identified (by confidence level)
- Metabolites passing QC

## Quality Control
- CV in QC samples (median, range)
- Blank subtraction results
- Missing value rate
- Internal standard recovery (if applicable)
- Sample outliers identified/excluded

## Normalization
- Method applied
- Transformation applied
- Batch correction (if applicable)

## Exploratory Analysis
- PCA: variance explained, group separation observed
- PLS-DA: R2Y, Q2, model quality
- Outliers: any excluded samples

## Differential Metabolites
- Total significant: N (adj. p < 0.05, |log2FC| > 1)
- Increased: N, Decreased: N
- Top 5 increased (metabolite, log2FC, adj. p)
- Top 5 decreased (metabolite, log2FC, adj. p)

## Pathway Enrichment
- Top enriched pathways (pathway name, p-value, FDR, hit metabolites)
- Biological interpretation per pathway

## Multi-Omics Integration (if applicable)
- Key metabolite-enzyme pairs with concordant changes
- Metabolic phenotype summary

## Biomarker Panel (if requested)
- Classification performance metrics
- Top biomarker metabolites ranked by importance

## Biological Interpretation
- Summary of metabolic reprogramming
- Mechanistic hypotheses
- Clinical/biological relevance
```

---

## Integration with Other Skills

| Skill | Used For | Phase |
|-------|----------|-------|
| `tooluniverse-gene-enrichment` | Enzyme/gene enrichment for integration | Phase 7 |
| `tooluniverse-rnaseq-deseq2` | Enzyme expression for integration | Phase 7 |
| `tooluniverse-proteomics-analysis` | Protein-level enzyme data | Phase 7 |
| `tooluniverse-multi-omics-integration` | Comprehensive omics integration | Phase 7 |
| `tooluniverse-metabolomics` | Database lookup, study retrieval | Phase 1 |

---

## Abbreviated Tool Reference

| Tool | Phase | Purpose |
|------|-------|---------|
| `MetaboAnalyst_name_to_id` | 1 | Map metabolite names → KEGG/HMDB/PubChem/ChEBI IDs |
| `MetabolomicsWorkbench_search_by_mz` | 1 | Identify metabolites by m/z (MS data) |
| `MetabolomicsWorkbench_search_by_exact_mass` | 1 | Identify by exact mass (high-res MS) |
| `MetabolomicsWorkbench_search_compound_by_name` | 1 | Search compound by name (RefMet) |
| `MetabolomicsWorkbench_get_refmet_info` | 1 | Get RefMet standardized name |
| `HMDB_search` | 1 | Search HMDB by name, formula, or mass |
| `HMDB_get_metabolite` | 1 | Get pathways, formula, bio roles for HMDB ID |
| `HMDB_get_diseases` | 1 | Get disease/biomarker associations |
| `MetabolomicsWorkbench_get_comp_by_pubc_cid` | 1 | Get compound info by PubChem CID |
| `metabolights_get_study` | 1 | Retrieve MetaboLights study metadata |
| `metabolights_search_studies` | 1 | Search MetaboLights studies |
| `MetabolomicsWorkbench_get_study` | 1 | Retrieve MetaboWorkbench study |
| `MetaboAnalyst_pathway_enrichment` | 6 | KEGG ORA for differential metabolites |
| `MetaboAnalyst_biomarker_enrichment` | 6 | SMPDB/HMDB metabolite set enrichment |
| `MetaboAnalyst_get_pathway_library` | 6 | List KEGG pathways for organism |
| `kegg_search_pathway` | 6 | Search KEGG pathways by keyword |
| `kegg_get_pathway_info` | 6, 7 | Get pathway details, genes, compounds |
| `KEGG_get_compound` | 6, 7 | Get compound details, linked reactions/enzymes |
| `KEGG_get_pathway_genes` | 7 | Get all genes in a KEGG pathway |
| `ReactomeContent_search` | 6 | Search Reactome by keyword |
| `Reactome_get_pathway` | 6 | Get Reactome pathway details |

Full parameter tables: see `references/tools.md`.

---

## Known Gotchas

### Metabolite Identification
- **Name ambiguity**: Common names like "vitamin B6" map to multiple compounds. Prefer IUPAC names or specific synonyms. Use `MetaboAnalyst_name_to_id` to validate before enrichment.
- **Isobar confusion**: LC-MS cannot distinguish isobaric compounds (same nominal mass). If two metabolites share m/z, annotate both and report the ambiguity.
- **Adduct forms**: LC-MS features appear as `[M+H]+`, `[M+Na]+`, `[M-H]-` etc. Search `MetabolomicsWorkbench_search_by_mz` using the neutral mass (subtract adduct mass) or specify ion mode.
- **GC-MS fragmentation**: GC-MS features are fragmented; match against NIST or specific GC-MS libraries, not high-resolution tools.

### Pathway Enrichment
- **Name mismatch in MetaboAnalyst**: `MetaboAnalyst_pathway_enrichment` uses KEGG nomenclature. Call `MetaboAnalyst_name_to_id` first and use only names that resolve. Pass resolved names (not HMDB or PubChem IDs) to the enrichment tool.
- **Small metabolite lists fail ORA**: With fewer than 10 input metabolites, hypergeometric test p-values are unreliable. Report pathway coverage instead.
- **Organism code**: Default organism is `hsa` (human). For mouse use `mmu`, rat `rno`, yeast `sce`. Call `MetaboAnalyst_get_pathway_library` to confirm available pathways for non-human organisms.

### Normalization
- **TIC vs PQN**: TIC assumes total metabolite abundance is constant across samples — invalid for studies where disease dramatically alters global metabolism (e.g., cancer vs normal). Use PQN in those cases.
- **Log of zero**: When applying log2 transformation, add a small pseudocount (e.g., half the minimum non-zero value). Do not simply add 1, as this can distort abundances of low-intensity metabolites.
- **Order of operations**: Always normalize before transformation; transform before scaling.

### Statistical Analysis
- **Multiple testing burden**: Untargeted metabolomics with hundreds of metabolites requires FDR correction. BH correction is standard. Do not use Bonferroni — it is overly conservative for correlated metabolites.
- **Paired vs unpaired**: Use paired t-test or Wilcoxon signed-rank test for matched sample designs (e.g., before/after treatment in same subject).

### Multi-Omics Integration
- **Direction of metabolite-enzyme relationships**: A substrate accumulates when its consuming enzyme is downregulated OR when the upstream enzyme is upregulated. Do not assume a simple positive correlation between enzyme expression and product metabolite level without checking the full reaction context.
- **Spearman vs Pearson**: Use Spearman rank correlation for metabolomics-transcriptomics correlation — metabolite distributions are rarely normal.

---

## Quantified Minimums

| Component | Requirement |
|-----------|-------------|
| Metabolites | At least 50 identified metabolites for meaningful analysis |
| Replicates | At least 3 per condition (5+ recommended) |
| QC | CV < 30% in QC samples; blank subtraction performed |
| Statistical test | t-test or Wilcoxon with BH-FDR correction |
| Pathway analysis | ORA with KEGG or SMPDB metabolite sets |
| Report | QC summary, differential metabolite table, pathway results |

---

## Limitations

- **Identification coverage**: Many features remain unidentified (Level 4); this is normal for untargeted metabolomics
- **Relative vs absolute**: Peak table values are relative abundances unless stable-isotope internal standards were used for absolute quantification
- **Isomers**: Structural isomers (e.g., leucine vs isoleucine) cannot be distinguished without MS/MS or retention time matching to authentic standards
- **Ion suppression**: Matrix effects reduce quantitative accuracy; internal standards partially correct for this
- **Dynamic range**: Typically 3-4 orders of magnitude; low-abundance metabolites may be below detection

---

## References

**Methods**:
- MetaboAnalyst 5.0: https://doi.org/10.1093/nar/gkab382
- XCMS (peak detection): https://doi.org/10.1021/ac051437y
- PQN normalization: https://doi.org/10.1007/s11306-006-0026-4
- MSEA: https://doi.org/10.1186/1471-2105-11-395

**Databases**:
- HMDB: https://hmdb.ca
- KEGG Compound: https://www.genome.jp/kegg/compound/
- MetaboLights: https://www.ebi.ac.uk/metabolights/
- Metabolomics Workbench: https://www.metabolomicsworkbench.org/
- RefMet: https://www.metabolomicsworkbench.org/databases/refmet/
