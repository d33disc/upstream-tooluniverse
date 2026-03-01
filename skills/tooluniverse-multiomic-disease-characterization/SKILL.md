---
name: tooluniverse-multiomic-disease-characterization
description: Comprehensive multi-omics disease characterization integrating genomics, transcriptomics, proteomics, pathway, and therapeutic layers for systems-level understanding. Produces a detailed multi-omics report with quantitative confidence scoring (0-100), cross-layer gene concordance analysis, biomarker candidates, therapeutic opportunities, and mechanistic hypotheses. Uses 80+ ToolUniverse tools across 8 analysis layers. Use when users ask about disease mechanisms, multi-omics analysis, systems biology of disease, biomarker discovery, or therapeutic target identification from a disease perspective.
---

# Multi-Omics Disease Characterization Pipeline

Characterize diseases across multiple molecular layers to provide systems-level understanding of disease mechanisms, identify therapeutic opportunities, and discover biomarker candidates.

**KEY PRINCIPLES**:
1. **Report-first** - Create report file FIRST, then populate progressively
2. **Disease disambiguation FIRST** - Resolve all identifiers before omics analysis
3. **Layer-by-layer** - Systematically cover all omics layers
4. **Cross-layer integration** - Identify genes/targets appearing in multiple layers
5. **Evidence grading** - Grade all evidence T1 (human/clinical) to T4 (computational)
6. **Tissue context** - Emphasize disease-relevant tissues/organs
7. **Quantitative scoring** - Multi-Omics Confidence Score (0-100)
8. **Druggable focus** - Prioritize targets with therapeutic potential
9. **Biomarker identification** - Highlight diagnostic/prognostic markers
10. **Mechanistic synthesis** - Generate testable hypotheses
11. **Source references** - Every statement must cite tool/database
12. **English-first queries** - Always use English in tool calls; respond in user's language

---

## When to Use This Skill

Apply when users ask about disease mechanisms across omics layers, multi-omics characterization, systems biology of disease, biomarker discovery, druggable target identification, cross-layer concordance analysis, or disease network biology / hub genes.

**NOT for**: single gene validation (`tooluniverse-drug-target-validation`), drug safety (`tooluniverse-adverse-event-detection`), general disease overview (`tooluniverse-disease-research`), variant interpretation (`tooluniverse-variant-interpretation`), GWAS-only analysis, or pathway-only analysis (`tooluniverse-systems-biology`).

---

## Multi-Omics Confidence Score (0-100)

**Data Availability (0-40 pts)**: Genomics data (10), transcriptomics data (10), protein data (5), pathway data (10), clinical/drug data (5).

**Evidence Concordance (0-40 pts)**: Multi-layer genes in 3+ layers — up to 20 pts (2 per gene, max 10); consistent genetics + expression direction (10); pathway-gene concordance (10).

**Evidence Quality (0-20 pts)**: Strong genetic evidence GWAS p < 5e-8 (10); clinical validation via approved drugs (10).

| Score | Tier | Interpretation |
|-------|------|----------------|
| 80-100 | Excellent | Comprehensive coverage, strong cross-layer concordance |
| 60-79 | Good | Good coverage, some gaps |
| 40-59 | Moderate | Limited cross-layer integration |
| 0-39 | Limited | Single-layer analysis dominates |

**Evidence tiers**: [T1] Direct human/clinical (GWAS p<5e-8, FDA-approved drug) | [T2] Experimental (validated DEGs, mouse KO) | [T3] Computational/DB (PPI, pathway mapping) | [T4] Annotation/prediction only.

---

## Report Template

Create `{disease_name}_multiomic_report.md` at the start with these sections (fill progressively):

```
# Multi-Omics Disease Characterization: {Disease Name}
Report Generated / Disease Identifiers / Multi-Omics Confidence Score

## Executive Summary  (fill last)
## 1. Disease Definition & Context
   Identifiers table | Description | Synonyms | Disease Hierarchy | Tissues | Therapeutic Areas
## 2. Genomics Layer
   GWAS Associations | GWAS Studies | Associated Genes | Rare Variants | Layer Summary
## 3. Transcriptomics Layer
   DEG Studies | Expression Atlas Scores | Tissue Expression | Biomarker Candidates | Summary
## 4. Proteomics & Interaction Layer
   PPI (STRING) | Hub Genes | Protein Complexes (IntAct) | Tissue-Specific PPI | Summary
## 5. Pathway & Network Layer
   Enriched Pathways | Reactome Detail | KEGG | WikiPathways | Summary
## 6. Gene Ontology & Functional Annotation
   Biological Processes | Molecular Functions | Cellular Components
## 7. Therapeutic Landscape
   Approved Drugs | Druggable Targets | Repurposing Candidates | Clinical Trials | Summary
## 8. Multi-Omics Integration
   Cross-Layer Gene Concordance | Hub Genes Top 20 | Biomarker Candidates |
   Mechanistic Hypotheses | Systems-Level Insights
## Multi-Omics Confidence Score  (scored table)
## Data Availability Checklist
## Completeness Checklist
## References  (all tools used)
```

---

## Phase 0: Disease Disambiguation (ALWAYS FIRST)

**Objective**: Resolve disease to standard identifiers for all downstream queries.

**Steps**:
1. Call `OpenTargets_get_disease_id_description_by_name` with the disease name to get MONDO/EFO ID and description.
2. Call `OpenTargets_get_disease_description_by_efoId` with that ID to get full description and cross-references (OMIM, UMLS, DOID, ICD10).
3. Call `OpenTargets_get_disease_synonyms_by_efoId` — expand synonym list for later search terms.
4. Call `OpenTargets_get_disease_therapeutic_areas_by_efoId` for disease context.
5. Call `OpenTargets_get_disease_ancestors_parents_by_efoId` and `OpenTargets_get_disease_descendants_children_by_efoId` for hierarchy.
6. If user gave an OMIM/UMLS/other ID, call `OpenTargets_map_any_disease_id_to_all_other_ids` first to get the MONDO/EFO ID.
7. If name search returns multiple hits, present top 3-5 to the user and ask for selection. Prefer the most specific disease over parent categories.

**Track for all downstream phases**: `efo_id` (underscore format, e.g. `MONDO_0004975`), `disease_name`, `synonyms`, `therapeutic_areas`, `dbXRefs`.

**Gotcha**: OpenTargets disease IDs use underscore format (`MONDO_0004975`), NOT colon format (`MONDO:0004975`). Always normalize.

---

## Phase 1: Genomics Layer

**Objective**: Identify genetic variants, GWAS associations, and genetically implicated genes.

**Steps**:
1. Call `OpenTargets_get_associated_targets_by_disease_efoId` to get all disease-associated genes ranked by overall evidence score (returns top 25 by default; note the total `count`).
2. For the top 10-15 genes, call `OpenTargets_get_evidence_by_datasource` with `datasourceIds: ['ot_genetics_portal']` for GWAS/genetics evidence, and `['eva']` for ClinVar variants.
3. Call `gwas_search_associations` with the disease name (not ID) to get genome-wide significant associations from GWAS Catalog.
4. Call `OpenTargets_search_gwas_studies_by_disease` with the `diseaseIds` array for GWAS study metadata.
5. Call `clinvar_search_variants` with the disease name or condition for rare variant / monogenic evidence.
6. For top GWAS genes, optionally call `GWAS_search_associations_by_gene` per gene.

**Track**: `genomics_genes` dict — gene symbol, association score, evidence type, Ensembl ID.

**Gotcha**: `gwas_search_associations` requires a disease name string (e.g., `"Alzheimer"`), not an ID. Try synonyms if the primary name returns no results.

---

## Phase 2: Transcriptomics Layer

**Objective**: Identify differentially expressed genes, tissue-specific expression, and expression-based biomarkers.

**Steps**:
1. Call `ExpressionAtlas_search_differential` with the disease as the condition to find differential expression studies.
2. Call `expression_atlas_disease_target_score` with `efoId` and `pageSize` to get expression-based disease-gene scores.
3. Call `europepmc_disease_target_score` with `efoId` and `pageSize` to supplement with literature-mined associations.
4. For the top 10-15 genes from the genomics layer, call `HPA_get_rna_expression_by_source` for disease-relevant tissues.
5. For cancer context, call `HPA_get_cancer_prognostics_by_gene` for prognostic biomarker data.

**Track**: `transcriptomics_genes` dict — gene symbol, expression score, tissues, evidence type.

**Gotcha**: `HPA_get_rna_expression_by_source` requires ALL THREE parameters: `gene_name`, `source_type` (one of `tissue`, `blood`, `brain`, `cell_line`, `single_cell`), and `source_name`. `expression_atlas_disease_target_score` requires `pageSize` explicitly.

---

## Phase 3: Proteomics & Interaction Layer

**Objective**: Map protein-protein interactions, identify hub genes, and characterize interaction networks.

**Steps**:
1. Take top 15-20 genes from the combined genomics + transcriptomics gene lists.
2. Call `STRING_get_interaction_partners` for each gene (pass `protein_ids` as an array of gene symbols, e.g. `["APOE"]`).
3. Call `STRING_get_network` on the combined gene set to build the disease-specific PPI network.
4. Call `STRING_ppi_enrichment` to test whether the disease genes form a more connected module than expected by chance.
5. Call `STRING_functional_enrichment` on the gene set for integrated functional characterization.
6. For the disease-relevant tissue, call `humanbase_ppi_analysis` with the gene list and tissue name for tissue-specific PPI.
7. Call `intact_search_interactions` for individual top genes to get experimentally validated interactions.
8. Identify hub genes: those with interaction degree > mean + 1 SD.

**Gotcha**: `STRING_get_interaction_partners` requires `protein_ids` as an array, not a string. `humanbase_ppi_analysis` requires ALL of: `gene_list`, `tissue`, `max_node`, `interaction`, and `string_mode`.

---

## Phase 4: Pathway & Network Layer

**Objective**: Identify enriched biological pathways and cross-pathway connections.

**Steps**:
1. Collect all genes from genomics + transcriptomics layers (top 20-30 genes).
2. Call `enrichr_gene_enrichment_analysis` with the gene list and `libs: ['KEGG_2021_Human', 'Reactome_2022', 'WikiPathway_2023_Human']`. Note: `data` in the response is a JSON string that needs parsing.
3. Call `ReactomeAnalysis_pathway_enrichment` with space-separated gene identifiers for statistically rigorous Reactome enrichment with p-values and FDR.
4. Call `kegg_search_pathway` for disease-specific KEGG pathway lookups.
5. Call `WikiPathways_search` for disease name to find community-curated pathways.
6. For top Reactome pathways, call `Reactome_get_pathway` and `Reactome_get_pathway_reactions` to get mechanistic detail.
7. Identify genes appearing in multiple enriched pathways — these are pathway hub nodes.

**Gotcha**: `enrichr_gene_enrichment_analysis` requires `libs` as an array (not a string) and `gene_list` must contain at least 2 genes. The `data` response field is a JSON string — parse it before reading results.

---

## Phase 5: Gene Ontology & Functional Annotation

**Objective**: Characterize biological processes, molecular functions, and cellular components.

**Steps**:
1. Call `enrichr_gene_enrichment_analysis` three times with `libs: ['GO_Biological_Process_2023']`, `['GO_Molecular_Function_2023']`, and `['GO_Cellular_Component_2023']` using the combined gene list.
2. For the top 5 hub genes, call `QuickGO_annotations_by_gene` with `gene_product_id` in `UniProtKB:ACCESSION` format for detailed GO annotations with evidence codes.
3. Call `OpenTargets_get_target_gene_ontology_by_ensemblID` for top genes to cross-reference with OpenTargets GO data.
4. Summarize key biological processes, molecular functions, and cellular components.

**Gotcha**: `QuickGO_annotations_by_gene` requires `gene_product_id` in the form `UniProtKB:P02649`, not a plain gene symbol.

---

## Phase 6: Therapeutic Landscape

**Objective**: Map approved drugs, druggable targets, repurposing opportunities, and clinical trials.

**Steps**:
1. Call `OpenTargets_get_associated_drugs_by_disease_efoId` with `size: 100` (the `size` parameter is required) to get all drugs associated with the disease.
2. For the top disease-associated genes with no approved drugs, call `OpenTargets_get_target_tractability_by_ensemblID` to assess druggability (small molecule, antibody, PROTAC, etc.).
3. Call `OpenTargets_get_associated_drugs_by_target_ensemblID` for individual gene targets to find drugs that may be repurposable.
4. Call `search_clinical_trials` with `query_term` (required) and `condition` for the disease.
5. For top approved drugs, call `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` for mechanism detail.

**Gotcha**: `OpenTargets_get_associated_drugs_by_disease_efoId` and `OpenTargets_get_associated_drugs_by_target_ensemblID` both require `size` explicitly. `search_clinical_trials` requires `query_term` even when `condition` is also provided.

---

## Phase 7: Multi-Omics Integration

**Objective**: Integrate all layers, identify cross-layer genes, calculate confidence score, generate mechanistic hypotheses.

**Cross-Layer Gene Concordance** — for each gene, record which layers it appeared in:
- Genomics (GWAS hit / rare variant / genetic association)
- Transcriptomics (DEG / expression score)
- Proteomics (PPI hub / protein expression)
- Pathways (enriched pathway member)
- Therapeutics (drug target)

Genes appearing in 3+ layers are **multi-omics hub genes**. Rank by layer count, then by evidence quality within tier.

**Direction concordance**: Does the genetic signal agree with expression direction?
- Risk allele + upregulation → concordant gain-of-function [T1/T2 combined]
- Risk allele + downregulation → concordant loss-of-function [T1/T2 combined]
- Discordant → flag for investigation; may indicate indirect mechanisms

**Biomarker assessment** for each hub gene:
- Diagnostic: distinguishes disease vs. healthy state
- Prognostic: predicts outcome (use HPA cancer prognostics for cancer)
- Predictive: predicts treatment response
- Record supporting layer count as confidence metric

**Mechanistic hypothesis generation**:
1. Identify the most supported biological processes (top GO + pathway terms).
2. Map causal chain: genetic variant → gene expression change → protein function → pathway disruption → disease phenotype.
3. Identify intervention points that are druggable nodes in the causal chain.
4. Write 2-5 specific, testable hypotheses with supporting evidence citations.

**Calculate Multi-Omics Confidence Score** using the rubric in the scoring section above.

---

## Phase 8: Report Finalization

**Steps**:
1. Write the Executive Summary (2-3 sentences): disease mechanism in systems terms, key genes/pathways, therapeutic opportunities.
2. Complete the Multi-Omics Confidence Score table.
3. Complete the Data Availability Checklist and Completeness Checklist.
4. Fill the References section with every tool called and section it served.

**Quality gates before presenting to user**:
- All 8 report sections have content (or note "No data available")
- Every data point cites its source tool
- Top 20 genes ranked by multi-omics evidence
- Top 10 enriched pathways listed
- Biomarker candidates identified with layer support
- Cross-layer concordance table complete
- Mechanistic hypotheses include supporting evidence

---

## Known Gotchas

| Issue | Detail |
|-------|--------|
| OpenTargets ID format | Always use underscore: `MONDO_0004975`, NOT `MONDO:0004975` |
| GWAS search requires name | `gwas_search_associations` takes disease name string, not an ID; try synonyms if empty |
| `gwas_get_studies_for_trait` | May return empty if trait name does not match exactly — try synonyms |
| HPA expression — all 3 params required | `source_type` and `source_name` are both required alongside `gene_name` |
| STRING `protein_ids` is an array | Pass `["GENE"]`, not `"GENE"` |
| humanbase — all params required | `gene_list`, `tissue`, `max_node`, `interaction`, `string_mode` — none optional |
| Enrichr `data` is a JSON string | Parse the `data` field before reading enrichment results |
| Enrichr `libs` must be an array | `libs: ['KEGG_2021_Human']`, not a plain string |
| `expression_atlas_disease_target_score` | `pageSize` is required, not optional |
| `europepmc_disease_target_score` | `pageSize` is required |
| `OpenTargets_get_associated_drugs_*` | `size` is required in both disease and target drug calls |
| `search_clinical_trials` | `query_term` is required even when `condition` is provided |
| `QuickGO_annotations_by_gene` | `gene_product_id` must be in `UniProtKB:ACCESSION` format |
| `ReactomeAnalysis_pathway_enrichment` | `identifiers` is a single space-separated string, not an array |
| Rare diseases | GWAS data may be absent; rely on ClinVar + OpenTargets genetic evidence; expect lower confidence score |
| Common/polygenic diseases | Thousands of GWAS hits — cap at top 20-30 genes by effect size + significance (p < 5e-8) |

---

## Edge Cases

**Rare / monogenic diseases**: GWAS absent; ClinVar + OpenTargets genetic evidence dominates; pathway analysis reveals downstream effects; expect lower confidence score.

**Common / polygenic diseases**: Use strict p < 5e-8 threshold; focus on top 20-30 genes; pathway enrichment reveals convergent biology; network analysis identifies hub genes.

**Cancer**: Check cancer prognostics via `HPA_get_cancer_prognostics_by_gene`; include tumor-specific expression; clinical trial landscape may be extensive.

**Tissue ambiguity**: Query HPA for all relevant tissues; compare tissue-specific patterns; use tissue context from disease ontology.

**No data fallbacks**: If disease name fails → try synonyms → broader category → OMIM/UMLS ID mapping. If no GWAS → check ClinVar + OpenTargets evidence. If no expression data → try synonyms or query HPA per gene. If no pathway enrichment → relax gene list, try different DBs, map individual genes via Reactome. If no drugs → check drugs targeting individual genes, check clinical trials, note as novel opportunity.

---

## Tool Reference

See [`references/tools.md`](references/tools.md) for full parameter schemas and verified response examples.

| Tool | Purpose |
|------|---------|
| `OpenTargets_get_disease_id_description_by_name` | Resolve disease name to MONDO/EFO ID |
| `OSL_get_efo_id_by_disease_name` | Secondary disease name-to-ID lookup |
| `OpenTargets_get_disease_description_by_efoId` | Full description + cross-references |
| `OpenTargets_get_disease_synonyms_by_efoId` | Disease synonym expansion |
| `OpenTargets_get_disease_therapeutic_areas_by_efoId` | Therapeutic area context |
| `OpenTargets_get_disease_ancestors_parents_by_efoId` | Disease hierarchy (parents) |
| `OpenTargets_get_disease_descendants_children_by_efoId` | Disease hierarchy (children) |
| `OpenTargets_map_any_disease_id_to_all_other_ids` | Cross-map OMIM/UMLS/ICD10 to MONDO |
| `OpenTargets_get_associated_targets_by_disease_efoId` | All disease-associated genes, ranked |
| `OpenTargets_get_evidence_by_datasource` | Per-gene evidence filtered by datasource |
| `OpenTargets_search_gwas_studies_by_disease` | GWAS study metadata from OpenTargets |
| `gwas_search_associations` | GWAS Catalog genome-wide associations |
| `gwas_get_studies_for_trait` | GWAS Catalog studies for a trait |
| `gwas_get_variants_for_trait` | GWAS Catalog variants for a trait |
| `GWAS_search_associations_by_gene` | GWAS associations for a specific gene |
| `clinvar_search_variants` | Rare / pathogenic variants from ClinVar |
| `ExpressionAtlas_search_differential` | Differential expression studies |
| `ExpressionAtlas_search_experiments` | Expression experiments for condition |
| `expression_atlas_disease_target_score` | Expression-based disease-gene scores |
| `europepmc_disease_target_score` | Literature-mined disease-gene scores |
| `HPA_get_rna_expression_by_source` | Tissue-specific RNA expression |
| `HPA_get_rna_expression_in_specific_tissues` | Expression across a list of tissues |
| `HPA_get_cancer_prognostics_by_gene` | Cancer prognostic data |
| `HPA_get_subcellular_location` | Subcellular localization |
| `HPA_search_genes_by_query` | HPA gene search |
| `STRING_get_interaction_partners` | PPI partners from STRING |
| `STRING_get_network` | PPI network for a gene set |
| `STRING_functional_enrichment` | Functional enrichment from STRING |
| `STRING_ppi_enrichment` | Test PPI network significance |
| `intact_get_interactions` | IntAct interactions by UniProt ID |
| `intact_search_interactions` | IntAct interaction search |
| `HPA_get_protein_interactions_by_gene` | HPA protein interaction data |
| `humanbase_ppi_analysis` | Tissue-specific PPI via HumanBase |
| `enrichr_gene_enrichment_analysis` | Pathway + GO enrichment via Enrichr |
| `ReactomeAnalysis_pathway_enrichment` | Reactome enrichment with p-values/FDR |
| `Reactome_map_uniprot_to_pathways` | Map UniProt protein to Reactome pathways |
| `Reactome_get_pathway` | Reactome pathway details |
| `Reactome_get_pathway_reactions` | Reactions within a Reactome pathway |
| `kegg_search_pathway` | Search KEGG pathways by keyword |
| `kegg_get_pathway_info` | KEGG pathway details |
| `WikiPathways_search` | Search WikiPathways |
| `GO_get_annotations_for_gene` | GO annotations for a gene |
| `GO_search_terms` | Search GO terms by keyword |
| `QuickGO_annotations_by_gene` | Detailed GO annotations with evidence codes |
| `OpenTargets_get_target_gene_ontology_by_ensemblID` | OpenTargets GO data for a target |
| `OpenTargets_get_associated_drugs_by_disease_efoId` | All drugs for a disease |
| `OpenTargets_get_target_tractability_by_ensemblID` | Target druggability assessment |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | Drugs targeting a gene |
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | Drug mechanism of action |
| `search_clinical_trials` | Clinical trial search |
| `PubMed_search_articles` | PubMed literature search |
| `ensembl_lookup_gene` | Ensembl gene lookup |
| `MyGene_query_genes` | Gene metadata via MyGene.info |
| `OpenTargets_get_similar_entities_by_disease_efoId` | Similar diseases |
