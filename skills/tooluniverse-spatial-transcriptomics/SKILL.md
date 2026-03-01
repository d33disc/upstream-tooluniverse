---
name: tooluniverse-spatial-transcriptomics
description: Analyze spatial transcriptomics data to map gene expression in tissue architecture. Supports 10x Visium, MERFISH, seqFISH, Slide-seq, and imaging-based platforms. Performs spatial clustering, domain identification, cell-cell proximity analysis, spatial gene expression patterns, tissue architecture mapping, and integration with single-cell data. Use when analyzing spatial transcriptomics datasets, studying tissue organization, identifying spatial expression patterns, mapping cell-cell interactions in tissue context, characterizing tumor microenvironment spatial structure, or integrating spatial and single-cell RNA-seq data for comprehensive tissue analysis.
---

# Spatial Transcriptomics Analysis

Comprehensive analysis of spatially-resolved transcriptomics data to understand gene expression patterns in tissue architecture context. Combines expression profiling with spatial coordinates to reveal tissue organization, cell-cell interactions, and spatially variable genes.

## When to Use This Skill

**Triggers**:
- User has spatial transcriptomics data (Visium, MERFISH, seqFISH, etc.)
- Questions about tissue architecture or spatial organization
- Spatial gene expression pattern analysis
- Cell-cell proximity or neighborhood analysis requests
- Tumor microenvironment spatial structure questions
- Integration of spatial with single-cell data
- Spatial domain identification
- Tissue morphology correlation with expression

**Example Questions This Skill Solves**:
1. "Analyze this 10x Visium dataset to identify spatial domains"
2. "Which genes show spatially variable expression in this tissue?"
3. "Map the tumor microenvironment spatial organization"
4. "Find genes enriched at tissue boundaries"
5. "Identify cell-cell interactions based on spatial proximity"
6. "Integrate spatial transcriptomics with scRNA-seq annotations"
7. "Characterize spatial gradients in gene expression"
8. "Map ligand-receptor pairs in tissue context"

---

## Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Data Import** | 10x Visium, MERFISH, seqFISH, Slide-seq, STARmap, Xenium formats |
| **Quality Control** | Spot/cell QC, spatial alignment verification, tissue coverage |
| **Normalization** | Spatial-aware normalization accounting for tissue heterogeneity |
| **Spatial Clustering** | Identify spatial domains with similar expression profiles |
| **Spatial Variable Genes** | Find genes with non-random spatial patterns |
| **Neighborhood Analysis** | Cell-cell proximity, spatial neighborhoods, niche identification |
| **Spatial Patterns** | Gradients, boundaries, hotspots, expression waves |
| **Integration** | Merge with scRNA-seq for cell type mapping |
| **Ligand-Receptor Spatial** | Map cell communication in tissue context |
| **Visualization** | Spatial plots, heatmaps on tissue, 3D reconstruction |

---

## Workflow Overview

```
Input: Spatial Transcriptomics Data + Tissue Image
    |
    v
Phase 1: Data Import & QC
    |-- Load spatial coordinates + expression matrix
    |-- Load tissue histology image
    |-- Quality control per spot/cell
    |-- Filter low-quality spots
    |-- Align spatial coordinates to tissue
    |
    v
Phase 2: Preprocessing
    |-- Normalization (spatial-aware methods)
    |-- Highly variable gene selection
    |-- Dimensionality reduction (PCA)
    |-- Spatial lag smoothing (optional)
    |
    v
Phase 3: Spatial Clustering
    |-- Identify spatial domains/regions
    |-- Graph-based clustering with spatial constraints
    |-- Annotate domains with marker genes
    |-- Visualize domains on tissue
    |
    v
Phase 4: Spatial Variable Genes
    |-- Test for spatial autocorrelation (Moran's I, Geary's C)
    |-- Identify genes with spatial patterns
    |-- Classify pattern types (gradient, hotspot, boundary)
    |-- Rank by spatial significance
    |
    v
Phase 5: Neighborhood Analysis
    |-- Define spatial neighborhoods (k-NN, radius)
    |-- Calculate neighborhood composition
    |-- Identify interaction zones
    |-- Niche characterization
    |
    v
Phase 6: Integration with scRNA-seq
    |-- Cell type deconvolution per spot
    |-- Map cell types to spatial locations
    |-- Predict cell type spatial distributions
    |-- Validate with marker genes
    |
    v
Phase 7: Spatial Cell Communication
    |-- Identify proximal cell type pairs
    |-- Query ligand-receptor database (OmniPath via ToolUniverse)
    |-- Score spatial interactions
    |-- Map communication hotspots
    |
    v
Phase 8: Generate Spatial Report
    |-- Tissue overview with domains
    |-- Spatially variable genes
    |-- Cell type spatial maps
    |-- Interaction networks in tissue context
    |-- 3D visualization (if applicable)
```

---

## Phase Details

### Phase 1: Data Import & Quality Control

**Objective**: Load spatial data and assess quality.

**Supported platforms**:

- **10x Visium** (most common): 55 μm diameter spots, ~50 cells per spot, 5,000–10,000 spots per capture area. Data includes expression matrix + spatial coordinates + H&E image.
- **MERFISH / seqFISH** (imaging-based): Single-cell resolution with targeted gene panels (100–10,000 genes) and absolute coordinates per cell.
- **Slide-seq / Slide-seqV2**: 10 μm bead resolution with genome-wide profiling.
- **Xenium** (10x single-cell spatial): Single-cell resolution, large gene panels (300+ genes), subcellular resolution.

**Loading Visium data**: Use `scanpy.read_visium(data_dir)`. The expected directory structure has `filtered_feature_bc_matrix/` (barcodes, features, matrix) and `spatial/` (tissue positions, scale factors, H&E image). Spatial coordinates are stored in `adata.obsm['spatial']`; tissue images in `adata.uns['spatial']`.

**Quality control steps**:
1. Calculate QC metrics per spot: total counts, genes detected, mitochondrial fraction.
2. Filter spots with fewer than 200 genes or 500 UMI counts.
3. Remove spots where mitochondrial content exceeds 20%.
4. Verify spatial alignment by overlaying spot coordinates on the tissue image.

**QC thresholds** (adjust per tissue type):
| Metric | Default threshold |
|--------|------------------|
| Min genes per spot | 200 |
| Min UMI counts | 500 |
| Max mitochondrial % | 20% |

---

### Phase 2: Preprocessing & Normalization

**Objective**: Normalize data accounting for spatial heterogeneity.

1. Filter genes detected in fewer than 3 spots.
2. Normalize each spot to 10,000 total counts (`normalize_total`).
3. Apply log1p transformation.
4. Store raw counts before normalization for downstream use.
5. Select highly variable genes (default: top 2,000) for dimensionality reduction.
6. Run PCA (50 components).

**Optional: Spatial smoothing** — Average expression over k spatial neighbors before clustering. Reduces noise but may blur sharp domain boundaries. Use with caution on high-resolution platforms (Xenium, MERFISH).

---

### Phase 3: Spatial Clustering

**Objective**: Identify spatial domains (tissue regions with distinct expression profiles).

**Approach**: Build a spatial neighbor graph using squidpy (`sq.gr.spatial_neighbors`), then apply Leiden clustering. The neighbor graph encodes both expression similarity (via PCA) and spatial proximity.

Key parameters:
- `n_neighs`: Number of spatial neighbors per spot (default 6 for Visium hexagonal grid).
- `coord_type`: Use `"generic"` for Visium; `"grid"` for perfectly regular grids.
- `resolution`: Leiden resolution controls the number of domains. Start at 0.5–1.0 and adjust based on tissue complexity.

After clustering, identify marker genes per domain using differential expression (Wilcoxon rank-sum test). Visualize domain assignments on tissue with `sc.pl.spatial`.

**Annotation guidance**: Match domain marker genes to known cell type signatures or tissue anatomy. Use GTEx (`GTEx_get_top_expressed_genes`) or HPA data to validate tissue-specific expression patterns.

---

### Phase 4: Spatially Variable Genes

**Objective**: Find genes with non-random spatial patterns.

**Moran's I** is the standard spatial autocorrelation statistic:
- I > 0: Positive spatial autocorrelation (spatially clustered expression)
- I ~= 0: Random spatial distribution
- I < 0: Negative autocorrelation (dispersed/checkerboard pattern)

Run `sq.gr.spatial_autocorr(adata, mode='moran', n_perms=100)`. Results are stored in `adata.uns['moranI']`. Filter to FDR < 0.05 for significant spatial genes.

**Pattern classification** (for top spatially variable genes):
| Pattern type | Characteristics |
|-------------|-----------------|
| Gradient | Smooth directional change across tissue axis |
| Hotspot | Localized high expression in a small region |
| Boundary | Expression concentrated at domain edges/interfaces |
| Periodic | Regular spacing (e.g., cortical layers) |

Report the top 10–20 spatial genes with Moran's I values and pattern type.

---

### Phase 5: Neighborhood Analysis

**Objective**: Analyze cell-cell proximity and spatial niches.

**Neighborhood enrichment** (`sq.gr.nhood_enrichment`): Tests whether pairs of cell types/domains are spatially co-localized more than expected by chance. Results reveal which domains are frequently adjacent.

**Interaction zone identification**: For two domains A and B, find spots from A that have at least one neighbor from B (and vice versa). These boundary spots form the interaction zone and are candidates for cell-cell communication analysis.

**Niche characterization**: Characterize the local microenvironment of each spot by computing the composition of its k-nearest spatial neighbors. Summarize per domain.

---

### Phase 6: Integration with Single-Cell RNA-seq

**Objective**: Map cell types from scRNA-seq to spatial locations.

**Cell type deconvolution** (for multi-cell-resolution platforms like Visium):
- Methods: Cell2location, Tangram, SPOTlight
- Input: Spatial expression matrix + scRNA-seq cell type signatures
- Output: Estimated cell type proportions per spot stored in `adata.obsm['cell_type_fractions']`

**Cell2location workflow**:
1. Extract cell type signature matrix from scRNA-seq reference (marker genes per cell type).
2. Fit the Cell2location model on the spatial data.
3. Train for ~30,000 epochs.
4. Retrieve cell type abundances per spot.
5. Visualize each cell type's spatial distribution with `sc.pl.spatial`.

**For single-cell-resolution platforms** (Xenium, MERFISH): Assign cell type labels directly using a scRNA-seq reference via label transfer (Seurat or scVI).

---

### Phase 7: Spatial Cell Communication

**Objective**: Map ligand-receptor interactions in tissue context.

**Two-step approach**:

**Step 1 — Retrieve ligand-receptor pairs via ToolUniverse**:

Call `mcp__tooluniverse__execute_tool` with `tool_name="OmniPath_get_ligand_receptor_interactions"` to fetch curated L-R pairs. Query by specific genes of interest (e.g., `partners="CD274,TGFB1"`) or retrieve all pairs for a cell type pair of interest. See `references/tools.md` for full parameter reference.

**Step 2 — Score spatial proximity**:

Use squidpy's `sq.gr.ligrec` to test which L-R pairs are significantly expressed in spatially proximal cell type pairs. Results are stored per cell type pair with permutation-based p-values.

**Interaction score for a specific L-R pair**: Multiply ligand expression by receptor expression per spot to produce a co-expression score. Spots with high scores are communication hotspots. Visualize on tissue with `sc.pl.spatial`.

**Cross-reference with OmniPath annotation tools**: Use `OmniPath_get_cell_communication_annotations` to retrieve the signaling pathway context for top L-R pairs (e.g., whether TGFB1-TGFBR2 is classified as "Secreted Signaling" in CellChatDB).

---

### Phase 8: Spatial Report Generation

Generate a structured report covering:

1. **Dataset summary**: Platform, tissue, spot count after QC, genes detected.
2. **Quality control**: Mean genes/spot, mean UMI, mitochondrial %, tissue coverage %.
3. **Spatial domains**: Number and characterization of domains, marker genes per domain, relative tissue proportions.
4. **Spatially variable genes**: Top genes by Moran's I, pattern classification.
5. **Cell type mapping** (if scRNA-seq reference available): Cell type composition per domain, spatial distribution maps.
6. **Cell-cell communication**: Top L-R pairs with spatial context, interaction hotspot locations, pathway annotations.
7. **Spatial gradients**: Directional expression trends (e.g., hypoxia gradient, proliferation gradient).
8. **Biological interpretation**: Tissue architecture summary, clinically relevant findings.

**Example findings for a breast tumor section**:
- 7 spatial domains: tumor core (32%), invasive margin (18%), stroma (25%), immune infiltrate (12%), necrosis (8%), normal epithelium (3%), adipose (2%).
- 456 spatially variable genes (Moran's I FDR < 0.05); top genes include MKI67 (hotspot, tumor core), CD8A (gradient, margin), VIM (boundary, invasive margin).
- Immune checkpoint interaction: CD274 (PD-L1) → PDCD1 (PD-1) hotspot at invasive margin.
- CAF-tumor interface: TGFB1 → TGFBR2 at stromal-tumor boundary.

---

## Integration with ToolUniverse Skills

| Skill | Used For | Phase |
|-------|----------|-------|
| `tooluniverse-single-cell` | scRNA-seq reference preparation for deconvolution | Phase 6 |
| `tooluniverse-gene-enrichment` | Pathway enrichment for domain marker genes | Phase 3 |
| `tooluniverse-multi-omics-integration` | Integrate with bulk omics or proteomics | Phase 8 |

---

## Example Use Cases

### Use Case 1: Tumor Microenvironment Mapping

**Question**: "Map the spatial organization of tumor, immune, and stromal cells"

**Workflow**:
1. Load Visium data, apply QC and normalization.
2. Spatial clustering to identify domains (e.g., 7 domains).
3. Cell type deconvolution using scRNA-seq reference.
4. Map cell type distributions on tissue.
5. Identify interaction zones (tumor-immune, tumor-stroma).
6. Query OmniPath for L-R pairs relevant to identified cell type pairs.
7. Score spatial interactions; map communication hotspots.
8. Report: Comprehensive TME spatial architecture.

### Use Case 2: Developmental Gradient Analysis

**Question**: "Identify spatial gene expression gradients in developing tissue"

**Workflow**:
1. Load spatial data (e.g., mouse embryo section).
2. Identify spatially variable genes with Moran's I.
3. Classify gradient patterns (anterior-posterior, dorsal-ventral axes).
4. Map morphogen expression (WNT, BMP, FGF families).
5. Correlate with cell fate markers.
6. Report: Developmental spatial patterns.

### Use Case 3: Brain Region Identification

**Question**: "Automatically segment brain tissue into anatomical regions"

**Workflow**:
1. Load Visium mouse brain data.
2. Spatial clustering at high resolution.
3. Match domains to known brain regions (cortex, hippocampus, striatum, etc.).
4. Identify region-specific marker genes.
5. Validate with Allen Brain Atlas reference expression.
6. Report: Automated brain region annotation.

---

## Known Gotchas

| Issue | Detail |
|-------|--------|
| Visium coordinate system | `adata.obsm['spatial']` contains pixel coordinates in the full-resolution image space; always check `adata.uns['spatial'][library_id]['scalefactors']` for the correct scale factor before computing distances |
| `sq.gr.spatial_neighbors` coord_type | Use `"generic"` for Visium (not `"grid"`); `"grid"` is for perfectly regular arrays only and will produce incorrect neighbor graphs on Visium data |
| Moran's I requires neighbor graph | Must call `sq.gr.spatial_neighbors` before `sq.gr.spatial_autocorr`; the spatial autocorr function does not build the graph itself |
| Leiden clustering ignores spatial graph | Standard `sc.tl.leiden` uses the expression-based neighbor graph from `sc.pp.neighbors`, not the spatial graph from squidpy; build a combined graph or run them separately and compare |
| Cell2location needs raw counts | The Cell2location model requires unnormalized integer count data; pass `adata.raw.to_adata()` not the normalized layer |
| OmniPath returns all interactions by default | Calling `OmniPath_get_ligand_receptor_interactions` with no parameters returns all pairs (thousands); always filter by `partners=` or `sources=`/`targets=` for the cell types of interest |
| MERFISH/seqFISH gene panels | These platforms measure only a targeted gene panel (e.g., 500 genes); HVG selection and PCA are not meaningful — use all detected genes directly |
| Mitochondrial gene prefix varies | Human genes use `MT-` prefix; mouse genes use `mt-` (lowercase); always check before calculating mitochondrial QC metrics |
| Deconvolution requires matched species | The scRNA-seq reference and spatial data must be from the same species; gene name capitalization differs between human and mouse |
| `sq.gr.nhood_enrichment` needs cluster key | The `cluster_key` must correspond to a column in `adata.obs`; run cell type assignment or domain clustering first |

---

## Quantified Minimums

| Component | Requirement |
|-----------|-------------|
| Spots/cells | At least 500 spatial locations |
| QC | Filter low-quality spots; verify spatial alignment |
| Spatial clustering | At least one domain identification method |
| Spatial genes | Moran's I or equivalent spatial autocorrelation test |
| Visualization | Spatial plots overlaid on tissue images |
| Report | Domains, top spatial genes, and visualizations at minimum |

---

## Limitations

- **Resolution**: Visium spots contain multiple cells (not single-cell); deconvolution is required to resolve cell types.
- **Gene coverage**: Imaging-based methods (MERFISH, seqFISH) have limited gene panels.
- **3D structure**: Most platforms produce 2D sections; serial sectioning or 3D-capable platforms required for volumetric analysis.
- **Tissue quality**: Fresh-frozen or OCT-embedded tissue required for most platforms; FFPE compatibility varies.
- **Computational resources**: Large datasets (Xenium, multi-sample) require significant memory (32+ GB RAM).
- **Reference dependency**: Deconvolution quality depends on the completeness and quality of the scRNA-seq reference.

---

## Tool Reference

See [`references/tools.md`](references/tools.md) for full parameter tables and response formats for all ToolUniverse tools used in this workflow.

| Tool | Purpose | Phase |
|------|---------|-------|
| `OmniPath_get_ligand_receptor_interactions` | Fetch curated L-R pairs for cell communication | 7 |
| `OmniPath_get_cell_communication_annotations` | Get signaling pathway context for L-R pairs | 7 |
| `OmniPath_get_intercell_roles` | Classify genes as ligands/receptors/ECM | 7 |
| `GTEx_get_top_expressed_genes` | Validate tissue-specific marker gene expression | 3 |
| `enrichr_gene_enrichment_analysis` | Pathway enrichment for domain markers | 3, 8 |
| `HPA_get_rna_expression_in_specific_tissues` | Validate spatial domain markers against HPA | 3 |

---

## References

**Methods**:
- Squidpy: https://doi.org/10.1038/s41592-021-01358-2
- Cell2location: https://doi.org/10.1038/s41587-021-01139-4
- SpatialDE: https://doi.org/10.1038/nmeth.4636

**Platforms**:
- 10x Visium: https://www.10xgenomics.com/products/spatial-gene-expression
- MERFISH: https://doi.org/10.1126/science.aaa6090
- Slide-seq: https://doi.org/10.1126/science.aaw1219
