# Tool Parameter Reference

Detailed parameter tables, response formats, and notes for all tools used in the Spatial Multi-Omics Analysis skill. Tools are called via `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

---

## Phase 0 — Input Processing

### `OpenTargets_get_disease_id_description_by_name`
- **Key param**: `diseaseName` (string)
- **Returns**: `{data: {search: {hits: [{id, name, description}]}}}`
- **Use**: Resolve disease name to MONDO/EFO ID

### `OpenTargets_get_disease_description_by_efoId`
- **Key param**: `efoId` (string, e.g. `MONDO_0007254`)
- **Returns**: `{data: {disease: {id, name, description, dbXRefs}}}`
- **Note**: Disease IDs use underscore format, not colon

### `HPA_search_genes_by_query`
- **Key param**: `query` (string)
- **Returns**: List of gene entries matching query
- **Use**: Verify tissue-relevant genes

---

## Phase 1 — Gene Characterization

### `MyGene_query_genes`
- **Key param**: `query` (string — gene symbol)
- **Returns**: `{hits: [{_id, symbol, name, ensembl: {gene}, entrezgene}]}`
- **Note**: First hit may not be exact match; filter results by `symbol` field

### `UniProtIDMap_gene_to_uniprot`
- **Key params**: `gene_name` (string), `organism` (string, default `'human'`)
- **Returns**: UniProt accession string

### `UniProt_get_function_by_accession`
- **Key param**: `accession` (string — UniProt accession)
- **Returns**: List of function description strings

### `UniProt_get_subcellular_location_by_accession`
- **Key param**: `accession` (string — UniProt accession)
- **Returns**: Subcellular location information

### `HPA_get_subcellular_location`
- **Key param**: `gene_name` (string — gene symbol)
- **Returns**: `{gene_name, main_locations: [], additional_locations: [], location_summary}`
- **Note**: Uses gene symbol, NOT Ensembl ID

### `HPA_get_rna_expression_by_source`
- **Key params**: `gene_name` (string), `source_type` (string: `'tissue'`), `source_name` (string — tissue name)
- **Returns**: `{data: {gene_name, source_type, source_name, expression_value, expression_level}}`
- **Note**: ALL 3 parameters are REQUIRED

### `HPA_get_comprehensive_gene_details_by_ensembl_id`
- **Key params**: `ensembl_id` (string), `include_isoforms` (bool), `include_images` (bool), `include_antibodies` (bool), `include_expression` (bool)
- **Returns**: `{ensembl_id, gene_name, uniprot_ids, summary, protein_classes, tissue_expression, ...}`
- **Note**: ALL 5 parameters are REQUIRED. Set booleans to `false` except `include_expression=true` for faster response

### `HPA_get_cancer_prognostics_by_gene`
- **Key param**: `ensembl_id` (string — Ensembl gene ID, NOT gene symbol)
- **Returns**: `{gene_name, prognostic_cancers_count, prognostic_summary: [{cancer_type, prognostic_type, p_value}]}`
- **Note**: Takes Ensembl ID, NOT gene symbol

### `HPA_get_rna_expression_in_specific_tissues`
- **Key params**: `ensembl_id` (string), `tissue_name` (string)
- **Returns**: Expression data for specific tissue
- **Note**: Takes Ensembl ID, NOT gene symbol

---

## Phase 2 — Pathway & Functional Enrichment

### `STRING_functional_enrichment`
- **Key params**: `protein_ids` (array of gene symbols), `species` (int, `9606` for human)
- **Returns**: `{status: 'success', data: [{category, term, number_of_genes, number_of_genes_in_background, p_value, fdr, description, inputGenes, preferredNames}]}`
- **Categories**: `Process` (GO:BP), `Function` (GO:MF), `Component` (GO:CC), `KEGG`, `Reactome`, `COMPARTMENTS`, `DISEASES`, `Keyword`, `PMID`
- **Note**: This is the PRIMARY enrichment tool. Returns all categories in one call. Filter by `fdr < 0.05`

### `ReactomeAnalysis_pathway_enrichment`
- **Key param**: `identifiers` (string — space-separated gene symbols)
- **Returns**: `{data: {token, pathways_found, pathways: [{pathway_id, name, p_value, fdr, entities_found, entities_total}]}}`
- **Note**: `identifiers` is a SPACE-SEPARATED STRING, not an array

### `Reactome_map_uniprot_to_pathways`
- **Key param**: `id` (string — UniProt accession)
- **Returns**: Plain list of pathway objects (no `data` wrapper)

### `GO_get_annotations_for_gene`
- **Key param**: `gene_id` (string — gene symbol or ID)
- **Returns**: Plain list of GO annotation objects

### `kegg_search_pathway`
- **Key param**: `query` (string — pathway name or keyword)
- **Returns**: Pathway search results

### `WikiPathways_search`
- **Key param**: `query` (string)
- **Returns**: WikiPathways search results

---

## Phase 3 — Spatial Domain Characterization

### `HPA_get_biological_processes_by_gene`
- **Key param**: `gene_name` (string)
- **Returns**: Biological processes associated with the gene

### `HPA_get_protein_interactions_by_gene`
- **Key param**: `gene_name` (string)
- **Returns**: Known protein interaction partners

---

## Phase 4 — Cell-Cell Interaction Inference

### `STRING_get_interaction_partners`
- **Key params**: `protein_ids` (array of gene symbols), `species` (int, `9606`), `limit` (int), `confidence_score` (float, `0.7`)
- **Returns**: `{status: 'success', data: [{preferredName_A, preferredName_B, score, nscore, fscore, pscore, ascore, escore, dscore, tscore}]}`
- **Score types**: nscore=neighborhood, fscore=fusion, pscore=phylogenetic, ascore=coexpression, escore=experimental, dscore=database, tscore=textmining
- **Note**: Use `confidence_score=0.7` for high-confidence interactions only

### `STRING_get_protein_interactions`
- **Key params**: `protein_ids` (array), `species` (int, `9606`)
- **Returns**: Pairwise interaction data between specified proteins

### `intact_search_interactions`
- **Key params**: `query` (string), `max` (int)
- **Returns**: Interaction data from IntAct database

### `Reactome_get_interactor`
- **Key param**: Protein/gene identifier
- **Returns**: Reactome interaction data

### `DGIdb_get_drug_gene_interactions`
- **Key param**: `genes` (array of strings)
- **Returns**: Drug-gene interaction data
- **Note**: Takes array of strings, NOT a single gene name

---

## Phase 5 — Disease & Therapeutic Context

### `OpenTargets_get_associated_targets_by_disease_efoId`
- **Key params**: `efoId` (string), `size` (int)
- **Returns**: `{data: {disease: {associatedTargets: {count, rows: [{target: {id, approvedSymbol}, score}]}}}}`

### `OpenTargets_get_target_tractability_by_ensemblID`
- **Key param**: `ensemblId` (string — camelCase, not `ensemblID`)
- **Returns**: `{data: {target: {id, tractability: [{label, modality, value}]}}}`
- **Note**: Check `value=true` entries; parameter name is camelCase `ensemblId`

### `OpenTargets_get_associated_drugs_by_target_ensemblID`
- **Key params**: `ensemblId` (string), `size` (int)
- **Returns**: Drug data for the target
- **Note**: Both `ensemblId` AND `size` are REQUIRED

### `OpenTargets_get_drug_mechanisms_of_action_by_chemblId`
- **Key param**: `chemblId` (string)
- **Returns**: Mechanism of action data

### `OpenTargets_target_disease_evidence`
- **Key params**: `ensemblId` (string), `efoId` (string)
- **Returns**: Evidence items linking target to disease

### `clinical_trials_search`
- **Key params**: `action` (string, MUST be `"search_studies"`), `condition` (string), `intervention` (string), `limit` (int)
- **Returns**: `{total_count, studies: [{nctId, title, status, conditions}]}`
- **Note**: `action='search_studies'` is REQUIRED; `total_count` can be `None`

### `DGIdb_get_gene_druggability`
- **Key param**: `genes` (array of strings)
- **Returns**: `{data: {genes: {nodes: [{name, geneCategories: [{name}]}]}}}`
- **Note**: GraphQL-style response; takes array, NOT single gene name

### `civic_search_genes`
- **Key params**: (no filter required)
- **Returns**: Gene list with CIViC clinical evidence
- **Use**: Cancer contexts only; check if SVGs have clinical actionability evidence

---

## Phase 6 — Multi-Modal Integration

### `kegg_get_pathway_info`
- **Key param**: `pathway_id` (string — KEGG pathway ID)
- **Returns**: Pathway information including metabolites

---

## Phase 7 — Immune Microenvironment

### `iedb_search_epitopes`
- **Key params**: `organism_name` (string), `source_antigen_name` (string)
- **Returns**: `{status, data, count}`
- **Use**: Check if spatial antigens have known immune epitopes

---

## Phase 8 — Literature & Validation

### `PubMed_search_articles`
- **Key params**: `query` (string), `max_results` (int)
- **Returns**: Plain list of `[{pmid, title, authors, journal, pub_date, doi}]` (no `data` wrapper)

### `openalex_literature_search`
- **Key params**: `query` (string), `per_page` (int)
- **Returns**: List of works with titles, DOIs, abstracts

---

## Parameter Quick-Reference (Common Mistakes)

| Tool | Correct Parameter | Common Mistake | Note |
|------|-------------------|----------------|------|
| `MyGene_query_genes` | `query` | `q` | Filter results by `symbol` field |
| `STRING_functional_enrichment` | `protein_ids` (array) | `identifiers` | Also needs `species=9606` |
| `STRING_get_interaction_partners` | `protein_ids` (array) | `identifiers` | Use `confidence_score=0.7` |
| `ReactomeAnalysis_pathway_enrichment` | `identifiers` (space-separated string) | Passing an array | MUST be a string, not array |
| `HPA_get_subcellular_location` | `gene_name` | `ensembl_id` | Uses gene symbol |
| `HPA_get_cancer_prognostics_by_gene` | `ensembl_id` | `gene_name` | Uses Ensembl ID, NOT symbol |
| `HPA_get_rna_expression_by_source` | `gene_name`, `source_type`, `source_name` | Omitting any one | ALL 3 required |
| `HPA_get_rna_expression_in_specific_tissues` | `ensembl_id` | `gene_name` | Uses Ensembl ID |
| `HPA_get_comprehensive_gene_details_by_ensembl_id` | all 5 booleans | Omitting booleans | ALL 5 params required |
| `OpenTargets_get_target_tractability_by_ensemblID` | `ensemblId` (camelCase) | `ensemblID` | Case-sensitive camelCase |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblId`, `size` | Omitting `size` | Both REQUIRED |
| `OpenTargets_get_associated_targets_by_disease_efoId` | `efoId` | `diseaseId` | Returns nested `{data:{disease:{associatedTargets}}}` |
| `DGIdb_get_gene_druggability` | `genes` (array) | `gene_name` | Array of strings |
| `DGIdb_get_drug_gene_interactions` | `genes` (array) | `gene_name` | Array of strings |
| `clinical_trials_search` | `action='search_studies'` | Omitting `action` | `action` is REQUIRED |
| `ensembl_lookup_gene` | `species='homo_sapiens'` | Omitting species | REQUIRED parameter |
| GTEx tools | `operation` (SOAP param) | Omitting `operation` | All GTEx tools need `operation`; also need versioned GENCODE IDs like `ENSG00000141510.16` |

---

## Response Format Summary

| Tool | Top-level Shape | Key Fields to Extract |
|------|----------------|----------------------|
| `STRING_functional_enrichment` | `{status, data: [...]}` | `category`, `term`, `description`, `p_value`, `fdr`, `inputGenes`; filter `fdr < 0.05` |
| `ReactomeAnalysis_pathway_enrichment` | `{data: {pathways: [...]}}` | `pathway_id`, `name`, `p_value`, `fdr`, `entities_found`, `entities_total` |
| `STRING_get_interaction_partners` | `{status, data: [...]}` | `preferredName_A`, `preferredName_B`, `score`; keep `score > 0.7` |
| `MyGene_query_genes` | `{hits: [...]}` | Filter by exact `symbol` match before using |
| `HPA_get_subcellular_location` | Direct dict | `main_locations`, `additional_locations`, `location_summary` |
| `OpenTargets_get_target_tractability_by_ensemblID` | `{data:{target:{tractability:[...]}}}` | Check entries where `value=true` |
| `DGIdb_get_gene_druggability` | `{data:{genes:{nodes:[...]}}}` | GraphQL; `geneCategories[].name` |
| `PubMed_search_articles` | Plain list | `pmid`, `title`, `authors`, `journal`, `pub_date` — no wrapper |
| `clinical_trials_search` | `{total_count, studies: [...]}` | `nctId`, `title`, `status`, `conditions`; `total_count` may be `None` |

---

## Cell Type Marker Reference

| Cell Type | Key Markers | Extended Markers |
|-----------|-------------|-----------------|
| CD8+ T cell | CD8A, CD8B | GZMA, GZMB, PRF1, IFNG |
| CD4+ T cell | CD4 | IL2, IL4, IL17A, FOXP3 (Treg) |
| Regulatory T cell | FOXP3, IL2RA | CTLA4, TIGIT |
| B cell | CD19, MS4A1, CD79A | IGHG1, IGHM |
| Plasma cell | SDC1 (CD138), XBP1 | IGHG1, MZB1 |
| M1 Macrophage | CD68, NOS2, TNF | IL1B, CXCL10 |
| M2 Macrophage | CD68, CD163, MRC1 | ARG1, IL10 |
| Dendritic cell | ITGAX (CD11c), HLA-DRA | CD80, CD86 |
| NK cell | NCAM1 (CD56), NKG7 | GNLY, KLRD1 |
| Neutrophil | FCGR3B, CXCR2 | S100A8, S100A9 |
| Mast cell | KIT, TPSAB1 | CPA3, HDC |
| Epithelial | CDH1, EPCAM, KRT18, KRT19 | — |
| Fibroblast/CAF | VIM, COL1A1, COL3A1, FAP, ACTA2 | — |
| Endothelial | PECAM1, VWF, CDH5 | — |
| Neuronal | SNAP25, SYP, MAP2, NEFL | — |
| Hepatocyte | ALB, HNF4A, CYP3A4 | — |

---

## Immune Checkpoint Reference

| Checkpoint | Gene | Ligand Gene | Approved Antibodies |
|------------|------|-------------|---------------------|
| PD-1/PD-L1 | PDCD1 / CD274 | CD274, PDCD1LG2 | Pembrolizumab, Nivolumab, Atezolizumab |
| CTLA-4 | CTLA4 | CD80, CD86 | Ipilimumab |
| TIM-3 | HAVCR2 | LGALS9 | Sabatolimab |
| LAG-3 | LAG3 | HLA class II | Relatlimab |
| TIGIT | TIGIT | PVR, PVRL2 | Tiragolumab |
| VISTA | VSIR | PSGL1 | — |

---

## Known Ligand-Receptor Pairs to Check in SVG Lists

- Growth factors: EGF-EGFR, HGF-MET, VEGFA-KDR, FGF-FGFR, PDGF-PDGFRA/B
- Cytokines: TNF-TNFR, IL6-IL6R, IFNG-IFNGR, TGFB1-TGFBR1/2
- Chemokines: CXCL12-CXCR4, CCL2-CCR2, CXCL10-CXCR3
- Immune checkpoints: CD274(PD-L1)-PDCD1(PD-1), CD80/CD86-CTLA4, LGALS9-HAVCR2(TIM-3)
- Notch: DLL1/3/4-NOTCH1/2/3/4, JAG1/2-NOTCH1/2
- Wnt: WNT ligands-FZD receptors
- Adhesion: CDH1-CDH1 (homotypic), ITGA/B integrins-ECM
- Hedgehog: SHH-PTCH1
