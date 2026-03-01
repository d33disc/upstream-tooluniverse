---
name: tooluniverse-spatial-omics-analysis
description: Computational analysis framework for spatial multi-omics data integration. Given spatially variable genes (SVGs), spatial domain annotations, tissue type, and disease context from spatial transcriptomics/proteomics experiments (10x Visium, MERFISH, DBiTplus, SLIDE-seq, etc.), performs comprehensive biological interpretation including pathway enrichment, cell-cell interaction inference, druggable target identification, immune microenvironment characterization, and multi-modal integration. Produces a detailed markdown report with Spatial Omics Integration Score (0-100), domain-by-domain characterization, and validation recommendations. Uses 70+ ToolUniverse tools across 9 analysis phases. Use when users ask about spatial transcriptomics analysis, spatial omics interpretation, tissue heterogeneity, spatial gene expression patterns, tumor microenvironment mapping, tissue zonation, or cell-cell communication from spatial data.
---

# Spatial Multi-Omics Analysis Pipeline

Comprehensive biological interpretation of spatial omics data. Transforms spatially variable genes (SVGs), domain annotations, and tissue context into actionable biological insights covering pathway enrichment, cell-cell interactions, druggable targets, immune microenvironment, and multi-modal integration.

**KEY PRINCIPLES**:
1. **Report-first** — Create report file FIRST, then populate progressively
2. **Domain-by-domain** — Characterize each spatial region independently before cross-domain comparison
3. **Gene-list-centric** — Analyze user-provided SVGs and marker genes with ToolUniverse databases
4. **Biological interpretation** — Go beyond statistics to explain the biological meaning of spatial patterns
5. **Disease focus** — Emphasize disease mechanisms and therapeutic opportunities when disease context is given
6. **Evidence grading** — Grade all evidence T1 (human/clinical) to T4 (computational)
7. **Multi-modal thinking** — Integrate RNA, protein, and metabolite information when available
8. **Validation guidance** — Suggest experimental validation approaches for key findings
9. **Source references** — Every statement must cite a tool/database source
10. **English-first queries** — Always use English terms in tool calls; respond in the user's language

> Full parameter tables, response formats, cell-type markers, and ligand-receptor references:
> see `references/tools.md` in this skill directory.

---

## When to Use This Skill

Apply when users provide spatially variable genes from spatial transcriptomics, ask about biological interpretation of spatial domains, need pathway enrichment of spatial gene expression, want to understand cell-cell interactions or tissue zonation, or need tumor microenvironment characterization from spatial omics data.

**NOT for**: Single-gene interpretation without spatial context, variant interpretation, GWAS analysis, bulk RNA-seq (non-spatial), or raw spatial data processing (Seurat/Scanpy/squidpy handle that upstream step).

---

## Input Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `svgs` | Yes | Spatially variable genes (gene symbols) | `['EGFR','CDH1','VIM','MYC','CD3E']` |
| `tissue_type` | Yes | Tissue/organ type | `brain`, `liver`, `lung`, `breast` |
| `technology` | No | Spatial omics platform | `10x Visium`, `MERFISH`, `DBiTplus` |
| `disease_context` | No | Disease if applicable | `breast cancer`, `Alzheimer disease` |
| `spatial_domains` | No | Domain name -> marker genes mapping | `{'Tumor core': ['MYC','EGFR'], 'Stroma': ['VIM','COL1A1']}` |
| `cell_types` | No | Cell types from deconvolution | `['Epithelial','T cell','Macrophage']` |
| `proteins` | No | Proteins detected (multi-modal) | `['CD3','CD8','PD-L1','Ki67']` |
| `metabolites` | No | Metabolites detected (SpatialMETA) | `['glutamine','lactate','ATP']` |

---

## Spatial Omics Integration Score (0-100)

| Component | Max | Criteria |
|-----------|-----|---------|
| SVGs provided (>10 genes) | 5 | |
| Disease context provided | 5 | |
| Spatial domains defined | 5 | |
| Cell type composition available | 5 | |
| Multi-modal data (protein/metabolite) | 5 | |
| Literature context found | 5 | |
| Significant pathway enrichment (FDR<0.05) | 10 | |
| Cell-cell interaction predictions | 10 | |
| Disease mechanism identified | 10 | |
| Druggable targets in disease regions | 10 | |
| Cross-database validation (3+ databases) | 10 | |
| Clinical validation (approved drugs) | 10 | |
| Literature support for spatial patterns | 10 | |
| **TOTAL** | **100** | |

| Score | Tier | Interpretation |
|-------|------|----------------|
| 80-100 | Excellent | Comprehensive spatial characterization, strong insights, druggable targets found |
| 60-79 | Good | Good pathway/interaction analysis, some disease/therapeutic context |
| 40-59 | Moderate | Basic enrichment done, limited domain comparison or interaction analysis |
| 0-39 | Limited | Minimal data, gene-level annotation only |

**Evidence grading**: [T1] direct human/clinical proof; [T2] experimental evidence; [T3] computational/database; [T4] annotation/prediction only.

---

## Report Template

Create `{tissue}_{disease}_spatial_omics_report.md` at analysis start. Sections:

1. Tissue & Disease Context — tissue info, disease IDs, expected cell types
2. Spatially Variable Gene Characterization — ID resolution, tissue expression, subcellular localization, disease associations
3. Pathway Enrichment Analysis — STRING (GO BP/MF/CC, KEGG, Reactome), ReactomeAnalysis
4. Spatial Domain Characterization — per-domain pathways, cell type assignment, narrative; then cross-domain comparison table
5. Cell-Cell Interaction Inference — STRING PPI network, ligand-receptor pairs, signaling pathway axes
6. Disease & Therapeutic Context — disease gene overlap, druggable targets per domain, approved drugs, clinical trials
7. Multi-Modal Integration — RNA-protein concordance, subcellular context, metabolic integration (if data available)
8. Immune Microenvironment — immune cell markers, checkpoint expression, hot/cold/excluded classification (cancer/inflammation only)
9. Literature & Validation Context — PubMed/OpenAlex evidence, known spatial patterns, validation recommendations
10. Spatial Omics Integration Score table + Completeness checklist + References

---

## Tool Reference (Abbreviated)

Full parameter tables in `references/tools.md`.

| Tool | Purpose |
|------|---------|
| `OpenTargets_get_disease_id_description_by_name` | Resolve disease name to MONDO/EFO ID |
| `OpenTargets_get_disease_description_by_efoId` | Full disease description and cross-refs |
| `MyGene_query_genes` | Resolve gene symbol to Ensembl/Entrez IDs |
| `UniProtIDMap_gene_to_uniprot` | Map gene symbol to UniProt accession |
| `UniProt_get_function_by_accession` | Protein function annotation |
| `UniProt_get_subcellular_location_by_accession` | Subcellular localization (UniProt) |
| `HPA_get_subcellular_location` | Experimentally validated protein localization |
| `HPA_get_rna_expression_by_source` | Tissue RNA expression level |
| `HPA_get_rna_expression_in_specific_tissues` | RNA expression in named tissue (by Ensembl ID) |
| `HPA_get_comprehensive_gene_details_by_ensembl_id` | One-stop HPA gene characterization |
| `HPA_get_cancer_prognostics_by_gene` | Cancer prognostic significance (by Ensembl ID) |
| `HPA_search_genes_by_query` | Search HPA by keyword |
| `HPA_get_biological_processes_by_gene` | GO biological processes per gene |
| `HPA_get_protein_interactions_by_gene` | Known interaction partners (HPA) |
| `STRING_functional_enrichment` | Primary enrichment: GO, KEGG, Reactome, DISEASES in one call |
| `STRING_get_interaction_partners` | PPI network for gene set |
| `STRING_get_protein_interactions` | Pairwise interactions between specified proteins |
| `ReactomeAnalysis_pathway_enrichment` | Reactome pathway enrichment with hierarchy |
| `Reactome_map_uniprot_to_pathways` | Map single protein to Reactome pathways |
| `Reactome_get_interactor` | Pathway-level interaction context |
| `GO_get_annotations_for_gene` | GO annotations for individual gene |
| `kegg_search_pathway` | Find KEGG pathways by keyword |
| `kegg_get_pathway_info` | KEGG pathway details including metabolites |
| `WikiPathways_search` | Search WikiPathways |
| `intact_search_interactions` | IntAct molecular interactions |
| `OpenTargets_get_associated_targets_by_disease_efoId` | Disease-associated genes |
| `OpenTargets_get_target_tractability_by_ensemblID` | Drug tractability (small mol / antibody) |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | Approved/clinical drugs for a target |
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | Drug mechanism of action |
| `OpenTargets_target_disease_evidence` | Specific evidence linking gene to disease |
| `DGIdb_get_gene_druggability` | Classify genes as kinase, GPCR, druggable, etc. |
| `DGIdb_get_drug_gene_interactions` | Drug-gene interaction data |
| `clinical_trials_search` | Search clinical trials by condition + intervention |
| `civic_search_genes` | CIViC clinical actionability evidence (cancer) |
| `PubMed_search_articles` | PubMed literature search |
| `openalex_literature_search` | Broader literature including preprints |
| `iedb_search_epitopes` | Immune epitope database (antigen validation) |

---

## Phase 0: Input Processing & Disambiguation (ALWAYS FIRST)

**Objective**: Parse user input, resolve identifiers, establish analysis scope.

1. Parse SVG list; confirm valid gene symbols
2. Identify tissue type; map to standard ontology term
3. If disease provided, resolve name to MONDO/EFO ID using `OpenTargets_get_disease_id_description_by_name`, then fetch full description with `OpenTargets_get_disease_description_by_efoId`
4. Determine analysis scope:
   - Cancer -> enable immune microenvironment, somatic mutation, druggable-target phases
   - Neurological -> include brain region specificity, neuronal markers
   - Metabolic disease / normal tissue -> focus on tissue architecture, metabolic zonation
   - Small list (<20 genes) -> warn about limited enrichment power; emphasize gene-level analysis
   - Large list (>500 genes) -> suggest filtering to top SVGs by significance before enrichment
5. Create report file with header section

---

## Phase 1: Gene Characterization

**Objective**: Resolve gene identifiers, annotate functions, tissue specificity, and subcellular localization.

For each SVG (batch if >20; characterize top genes, sample rest):
1. Query `MyGene_query_genes` — get Ensembl ID and Entrez ID (filter results by exact `symbol` match)
2. Map to UniProt accession using `UniProtIDMap_gene_to_uniprot`
3. Get protein function from `UniProt_get_function_by_accession`
4. Get subcellular localization from `HPA_get_subcellular_location` (uses gene symbol)
5. Get tissue RNA expression from `HPA_get_rna_expression_by_source` (all 3 params required)
6. If cancer context: check `HPA_get_cancer_prognostics_by_gene` (uses Ensembl ID)

**Batch strategy**: characterize all individually up to 50 genes; top 50 for 50-200; top 30 for 200+. Always run enrichment on the full list.

**Spatial interpretation note**: secreted proteins suggest paracrine signaling; membrane proteins indicate cell surface markers; nuclear proteins indicate transcription factors — these inform cross-domain interaction predictions.

---

## Phase 2: Pathway & Functional Enrichment

**Objective**: Identify enriched biological pathways and functions in SVGs and per-domain gene sets.

1. Run `STRING_functional_enrichment` on ALL SVGs (primary tool; covers GO BP/MF/CC, KEGG, Reactome, DISEASES in one call). Filter by FDR < 0.05; report top 10-15 per category.
2. Run `ReactomeAnalysis_pathway_enrichment` for Reactome hierarchy detail (pass genes as space-separated string, not array).
3. If spatial domains provided: run `STRING_functional_enrichment` per domain gene set; compare enriched pathways; identify domain-specific vs shared pathways.

**Enrichment interpretation**:
- Signaling pathways (RTK, Wnt, Notch, Hedgehog) -> cell-cell communication
- Metabolic pathways -> tissue metabolic zonation
- Immune pathways -> immune infiltration/exclusion
- ECM/adhesion pathways -> tissue structure and remodeling
- Cell cycle/proliferation -> growth zones
- Apoptosis/stress -> damage zones

---

## Phase 3: Spatial Domain Characterization

**Objective**: Characterize each spatial domain biologically; compare between domains.

For each domain:
1. Get marker gene list
2. Run `STRING_functional_enrichment` on domain gene set
3. Assign likely cell type(s) from marker genes (see `references/tools.md` for full marker table). Confidence: high = 3+ markers match, medium = 2, low = 1.
4. Write biological interpretation narrative

Then cross-domain comparison:
- Differential pathways between domains
- Unique vs shared genes
- Disease-relevant vs homeostatic regions
- Transition zones (genes shared between adjacent domains)

---

## Phase 4: Cell-Cell Interaction Inference

**Objective**: Predict cell-cell communication from spatial gene expression patterns.

1. Run `STRING_get_interaction_partners` on all SVGs (confidence_score=0.7 for high-confidence only); identify hub genes with most connections.
2. Scan SVG list for known ligand-receptor pairs (full list in `references/tools.md`); cross-reference with domain assignments to identify potential cross-domain signaling.
3. Build interaction map:
   - Intra-domain interactions (within same spatial region)
   - Inter-domain interactions (between different regions), e.g., tumor-stroma, immune-tumor signaling axes
4. Map interactions to Reactome signaling pathways using `Reactome_map_uniprot_to_pathways`.
5. Complement STRING with `intact_search_interactions` for experimental evidence.

**Important**: Ligand-receptor inference here is based on gene co-expression + known pairs, not spatial proximity statistics. For quantitative spatial statistics use CellChat, NicheNet, or COMMOT externally.

---

## Phase 5: Disease & Therapeutic Context

**Objective**: Connect spatial findings to disease mechanisms; identify druggable targets per domain.

1. Get disease-associated genes from `OpenTargets_get_associated_targets_by_disease_efoId`; intersect with SVGs; get specific evidence for overlapping genes via `OpenTargets_target_disease_evidence`.
2. Classify druggable genes with `DGIdb_get_gene_druggability` (array input); assess tractability with `OpenTargets_get_target_tractability_by_ensemblID` (camelCase `ensemblId`).
3. For druggable spatial targets, retrieve approved drugs via `OpenTargets_get_associated_drugs_by_target_ensemblID` (both `ensemblId` and `size` required) and mechanisms via `OpenTargets_get_drug_mechanisms_of_action_by_chemblId`.
4. Search clinical trials with `clinical_trials_search` (`action='search_studies'` is required) targeting spatial genes in the disease context.
5. If cancer: check `civic_search_genes` for clinical actionability evidence.

---

## Phase 6: Multi-Modal Integration

**Objective**: Integrate protein, RNA, and metabolite spatial data when available.

1. **RNA-Protein concordance** (if protein data provided): compare spatial RNA pattern with protein detection; note concordant vs discordant patterns (discordance is often the most interesting finding, suggesting post-transcriptional regulation).
2. **Subcellular context**: map spatial RNA localization to protein subcellular location via `HPA_get_subcellular_location`; interpret secreted/membrane/nuclear categories for interaction inference.
3. **Metabolic integration** (if metabolomics available): map enzyme-encoding genes to metabolic pathways via `Reactome_map_uniprot_to_pathways` and `kegg_get_pathway_info`; link detected metabolites to spatial enzyme genes; identify known metabolic zonation patterns (e.g., liver periportal vs pericentral).

---

## Phase 7: Immune Microenvironment

**Objective**: Characterize immune cell composition and checkpoint expression in spatial context.

**Activate only if**: disease context is cancer, autoimmune, or inflammatory; OR SVGs include immune markers (CD3E, CD8A, CD68, CD163, etc.); OR user explicitly asks about immune patterns.

1. Identify immune-related SVGs using the marker table in `references/tools.md`.
2. Classify immune cell types present per spatial domain.
3. Check immune checkpoint gene expression (PD-1/PD-L1, CTLA-4, TIM-3, LAG-3, TIGIT); see checkpoint table in `references/tools.md`.
4. Classify immune infiltration pattern: hot (T cell infiltrated), cold (immune desert), or excluded.
5. Check for tertiary lymphoid structure signatures (co-occurring B cell + T cell markers).
6. Assess checkpoint druggability with `OpenTargets_get_target_tractability_by_ensemblID`; check `iedb_search_epitopes` for antigen immunogenicity.

---

## Phase 8: Literature & Validation Context

**Objective**: Provide literature evidence for spatial findings; suggest validation experiments.

**Literature search strategy**:
1. `"{tissue} spatial transcriptomics"` — baseline tissue spatial atlas papers
2. `"{disease} spatial omics"` — disease-specific spatial findings
3. `"{top_gene} {tissue} expression"` — per-gene literature for key SVGs
4. `"{tissue} zonation gene expression"` — if zonation patterns detected
5. `"{technology} {tissue}"` — technology-specific papers (e.g., "Visium breast cancer")

Use `PubMed_search_articles` as primary; fall back to `openalex_literature_search` for broader or preprint coverage.

**Validation recommendations priority**:
| Priority | Target | Recommended Method | Rationale |
|----------|--------|-------------------|-----------|
| High | Key SVG | smFISH / RNAscope | Validate spatial pattern at single-molecule resolution |
| High | Druggable target | IHC on serial sections | Confirm protein expression in spatial domain |
| High | Ligand-receptor pair | Proximity ligation assay (PLA) | Confirm physical interaction at tissue level |
| Medium | Domain markers | Multiplexed IF (CODEX/IBEX) | Validate multiple markers simultaneously |
| Medium | Pathway | Spatial metabolomics (MALDI/DESI) | Confirm metabolic pathway activity |
| Low | Novel interaction | Co-culture + conditioned media | Functional validation of predicted interaction |

---

## Known Gotchas

### API Behavior Quirks
- **`STRING_functional_enrichment`**: Primary enrichment tool. Do NOT use `enrichr_gene_enrichment_analysis` — it returns a connectivity graph (~107 MB), not standard enrichment results.
- **`ReactomeAnalysis_pathway_enrichment`**: `identifiers` must be a space-separated STRING, not an array. Passing an array silently fails or returns unexpected results.
- **`MyGene_query_genes`**: The first hit may not be the exact gene queried. Always filter results by the `symbol` field before using ID values.
- **`HPA_get_cancer_prognostics_by_gene`**: Takes Ensembl ID (`ensembl_id`), NOT gene symbol. Using gene symbol returns no results without error.
- **`HPA_get_rna_expression_in_specific_tissues`**: Takes Ensembl ID, NOT gene symbol (opposite of most HPA tools).
- **`HPA_get_comprehensive_gene_details_by_ensembl_id`**: All 5 boolean parameters are REQUIRED; omitting any causes a validation error.
- **`OpenTargets_get_target_tractability_by_ensemblID`**: Parameter is camelCase `ensemblId`, not `ensemblID`. The case difference matters.
- **`OpenTargets_get_associated_drugs_by_target_ensemblID`**: Both `ensemblId` AND `size` are required; omitting `size` causes an error.
- **`clinical_trials_search`**: `action='search_studies'` is REQUIRED and must be passed explicitly; `total_count` in response can be `None`.
- **`DGIdb_get_gene_druggability` and `DGIdb_get_drug_gene_interactions`**: Parameter is `genes` (array of strings), not `gene_name`.
- **GTEx tools**: Use SOAP-style interface requiring an `operation` parameter; also require versioned GENCODE IDs (e.g., `ENSG00000141510.16`), not plain Ensembl IDs.
- **OpenTargets disease IDs**: Use underscore format (`MONDO_0007254`), not colon format (`MONDO:0007254`).
- **`cBioPortal_get_cancer_studies`**: Broken — has a literal `{limit}` placeholder in the URL causing 400 errors. Avoid.
- **`HPA_get_rna_expression_by_source`**: All three parameters (`gene_name`, `source_type`, `source_name`) are required; any missing parameter returns an error.

### Conceptual Scope Boundaries
- This skill analyzes gene LISTS, not raw spatial matrices. Raw data processing (spot-level normalization, spatial clustering, SVG detection) must be done upstream with Seurat, Scanpy, or squidpy.
- **No spatial statistics**: Cannot compute Moran's I, spatial autocorrelation, or variogram analysis.
- **No image analysis**: Cannot process H&E or fluorescence microscopy images.
- **No deconvolution**: Cannot perform spot deconvolution — use BayesSpace, cell2location, or RCTD externally, then pass resulting cell type annotations as `cell_types` input.
- **Ligand-receptor inference**: Based on gene co-expression + known pairs, not spatial proximity statistics. For quantitative spatial communication inference, use CellChat, NicheNet, or COMMOT externally.
- **Large gene lists**: >200 genes may slow STRING queries; batch or sample representative genes.

---

## Fallback Strategies

| Step | Primary | Fallback | Default if all fail |
|------|---------|----------|---------------------|
| Pathway enrichment | `STRING_functional_enrichment` | `ReactomeAnalysis_pathway_enrichment` | `GO_get_annotations_for_gene` per gene |
| Tissue expression | `HPA_get_rna_expression_by_source` | `HPA_get_comprehensive_gene_details_by_ensembl_id` | Note "tissue expression data unavailable" |
| Disease association | `OpenTargets_get_associated_targets_by_disease_efoId` | `OpenTargets_target_disease_evidence` per gene | Skip disease section if no context |
| Drug information | `OpenTargets_get_associated_drugs_by_target_ensemblID` | `DGIdb_get_drug_gene_interactions` | Note "no approved drugs identified" |
| Literature | `PubMed_search_articles` | `openalex_literature_search` | Note "no spatial-specific literature found" |

---

## Common Use Cases

**Cancer spatial heterogeneity** (Visium, breast cancer, 5 domains, 200 SVGs): Focus on tumor-specific pathways, immune infiltration (hot/cold), tumor-stroma CAF signaling, druggable targets in tumor core, immune checkpoint patterns, prognostic genes per domain.

**Brain tissue zonation** (MERFISH, hippocampus): Focus on neuronal subtype characterization, synaptic signaling, neurotransmitter receptor distribution, known hippocampal zonation (CA1/CA3/DG), neurodegenerative disease gene overlap.

**Liver metabolic zonation** (spatial transcriptomics, periportal vs pericentral gradients): Focus on CYP450/gluconeogenesis/lipogenesis enzyme distribution, Wnt signaling gradient, oxygen-responsive genes, drug metabolism enzyme patterns.

**Tumor-immune interface** (DBiTplus, melanoma, spatial RNA + protein): Focus on immune cell composition at boundary, checkpoint ligand-receptor pairs, immune exclusion mechanisms, immunotherapy target identification, RNA-protein concordance.

**Developmental spatial patterns**: Focus on morphogen gradients (Wnt, BMP, FGF, SHH), transcription factor spatial patterns, cell fate determination genes.

**Disease progression mapping** (neurodegeneration, affected-to-unaffected gradient): Focus on disease gene expression gradient, inflammatory response pattern, neuronal loss markers, glial activation, therapeutic window identification.

---

## Summary

This skill provides biological interpretation of spatial omics experiments (post-processing step, after upstream spatial analysis tools). It covers gene characterization, pathway enrichment, spatial domain characterization, cell-cell interaction inference, disease and therapeutic context, multi-modal integration, immune microenvironment characterization, and literature-backed validation recommendations.

**Output**: Comprehensive markdown report with Spatial Omics Integration Score (0-100)
**Uses**: 70+ ToolUniverse tools across 9 analysis phases
**Tools called as**: `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`
**Detailed parameter reference**: `references/tools.md`
