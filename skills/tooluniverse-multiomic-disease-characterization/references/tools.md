# Tool Parameter Reference

Detailed parameter schemas and verified response examples for all tools used in the multi-omics disease characterization pipeline. See the main `SKILL.md` for workflow context.

---

## Disease Disambiguation Tools

### `OpenTargets_get_disease_id_description_by_name`
- **Input**: `diseaseName` (string)
- **Output**: `{data: {search: {hits: [{id, name, description}]}}}`

### `OSL_get_efo_id_by_disease_name`
- **Input**: `disease` (string)
- **Output**: `{efo_id, name}`

### `OpenTargets_get_disease_description_by_efoId`
- **Input**: `efoId` (string, e.g. `MONDO_0004975`)
- **Output**: `{data: {disease: {id, name, description, dbXRefs}}}`

### `OpenTargets_get_disease_synonyms_by_efoId`
- **Input**: `efoId` (string)
- **Output**: `{data: {disease: {id, name, synonyms: [{relation, terms}]}}}`

### `OpenTargets_get_disease_therapeutic_areas_by_efoId`
- **Input**: `efoId` (string)
- **Output**: `{data: {disease: {id, name, therapeuticAreas: [{id, name}]}}}`

### `OpenTargets_get_disease_ancestors_parents_by_efoId`
- **Input**: `efoId` (string)
- **Output**: `{data: {disease: {id, name, ancestors: [{id, name}]}}}`

### `OpenTargets_get_disease_descendants_children_by_efoId`
- **Input**: `efoId` (string)
- **Output**: `{data: {disease: {id, name, descendants: [{id, name}]}}}`

### `OpenTargets_map_any_disease_id_to_all_other_ids`
- **Input**: `inputId` (string) — any known disease ID, e.g. `OMIM:104300`, `UMLS:C0002395`
- **Output**: `{data: {disease: {id, name, dbXRefs: [str], ...}}}`

---

## Genomics Layer Tools

### `OpenTargets_get_associated_targets_by_disease_efoId`
- **Input**: `efoId` (string)
- **Output**: `{data: {disease: {id, name, associatedTargets: {count, rows: [{target: {id, approvedSymbol}, score}]}}}}`
- **Note**: Returns top 25 by default. Note total `count` for completeness.

**Verified response example**:
```json
{
  "data": {
    "disease": {
      "id": "MONDO_0004975",
      "name": "Alzheimer disease",
      "associatedTargets": {
        "count": 2456,
        "rows": [
          {"target": {"id": "ENSG00000080815", "approvedSymbol": "PSEN1"}, "score": 0.87}
        ]
      }
    }
  }
}
```

### `OpenTargets_get_evidence_by_datasource`
- **Input**: `efoId` (string), `ensemblId` (string), optional `datasourceIds` (array), `size` (int, default 50)
- **Output**: `{data: {disease: {evidences: {count, rows: [{...evidence details}]}}}}`
- **Key datasourceIds**: `['ot_genetics_portal']` (GWAS), `['gene2phenotype', 'genomics_england', 'orphanet']` (rare variants), `['eva']` (ClinVar)

### `gwas_search_associations`
- **Input**: `disease_trait` (string — disease name, NOT ID), `size` (int, default 20)
- **Output**: `{data: [{association_id, p_value, or_per_copy_num, or_value, beta, risk_frequency, efo_traits: [{...}], ...}], metadata: {pagination: {totalElements}}}`

**Verified response example**:
```json
{
  "data": [
    {
      "association_id": 216440893,
      "p_value": 2e-09,
      "or_per_copy_num": 0.94,
      "or_value": "0.94",
      "efo_traits": [{"..."}],
      "risk_frequency": "NR"
    }
  ],
  "metadata": {"pagination": {"totalElements": 1061816}}
}
```

### `gwas_get_studies_for_trait`
- **Input**: `disease_trait` (string), `size` (int)
- **Output**: `{data: [...studies], metadata: {pagination}}`
- **Note**: May return empty if trait name does not match exactly — try synonyms.

### `gwas_get_variants_for_trait`
- **Input**: `disease_trait` (string), `size` (int)
- **Output**: `{data: [...variants], metadata: {pagination}}`

### `GWAS_search_associations_by_gene`
- **Input**: `gene_name` (string)
- **Output**: Associations for a specific gene

### `OpenTargets_search_gwas_studies_by_disease`
- **Input**: `diseaseIds` (array of strings), `enableIndirect` (bool, default true), `size` (int, default 10)
- **Output**: `{data: {studies: {count, rows: [{id, studyType, traitFromSource, publicationFirstAuthor, publicationDate, pubmedId, nSamples, nCases, nControls, ...}]}}}`

### `clinvar_search_variants`
- **Input**: `condition` (string) or `gene` (string), optional `max_results` (int)
- **Output**: List of ClinVar variants with clinical significance

---

## Transcriptomics Layer Tools

### `ExpressionAtlas_search_differential`
- **Input**: optional `gene` (string), `condition` (string), `species` (string, default `'homo sapiens'`)
- **Output**: Differential expression studies and results

### `ExpressionAtlas_search_experiments`
- **Input**: optional `gene` (string), `condition` (string), `species` (string)
- **Output**: Expression experiments relevant to condition

### `expression_atlas_disease_target_score`
- **Input**: `efoId` (string), `pageSize` (int, **REQUIRED**)
- **Output**: Genes scored by expression evidence for the disease

### `europepmc_disease_target_score`
- **Input**: `efoId` (string), `pageSize` (int, **REQUIRED**)
- **Output**: Genes scored by literature evidence for the disease

### `HPA_get_rna_expression_by_source`
- **Input**: `gene_name` (string), `source_type` (string: `'tissue'`, `'blood'`, `'brain'`, `'cell_line'`, `'single_cell'`), `source_name` (string, e.g. `'brain'`, `'liver'`) — **ALL 3 REQUIRED**
- **Output**: `{status, data: {gene_name, source_type, source_name, expression_value, expression_level, expression_unit}}`

**Verified response example**:
```json
{
  "status": "success",
  "data": {
    "gene_name": "APOE",
    "source_type": "tissue",
    "source_name": "brain",
    "expression_value": "2714.9",
    "expression_level": "very high",
    "expression_unit": "nTPM"
  }
}
```

### `HPA_get_rna_expression_in_specific_tissues`
- **Input**: `gene_name` (string), `tissues` (array of strings)
- **Output**: Expression across specified tissues

### `HPA_get_cancer_prognostics_by_gene`
- **Input**: `gene_name` (string)
- **Output**: Cancer prognostic data

### `HPA_get_subcellular_location`
- **Input**: `gene_name` (string)
- **Output**: Subcellular localization data

### `HPA_search_genes_by_query`
- **Input**: `query` (string)
- **Output**: Matching genes in HPA

---

## Proteomics & Interaction Layer Tools

### `STRING_get_interaction_partners`
- **Input**: `protein_ids` (array of strings — gene symbols work, e.g. `['APOE']`), `species` (int, default 9606), `confidence_score` (float, default 0.4), `limit` (int, default 20)
- **Output**: `{status: 'success', data: [{stringId_A, stringId_B, preferredName_A, preferredName_B, ncbiTaxonId, score, nscore, fscore, pscore, ascore, escore, dscore, tscore}]}`
- **Note**: `protein_ids` MUST be an array, not a string.

**Verified response example**:
```json
{
  "status": "success",
  "data": [
    {
      "stringId_A": "9606.ENSP00000252486",
      "stringId_B": "9606.ENSP00000466775",
      "preferredName_A": "APOE",
      "preferredName_B": "APOC2",
      "score": 0.999
    }
  ]
}
```

### `STRING_get_network`
- **Input**: `protein_ids` (array), `species` (int), `confidence_score` (float)
- **Output**: Network of interactions between input proteins

### `STRING_functional_enrichment`
- **Input**: `protein_ids` (array), `species` (int)
- **Output**: Functional enrichment results (GO, KEGG, etc.)

### `STRING_ppi_enrichment`
- **Input**: `protein_ids` (array), `species` (int)
- **Output**: Statistical test — more interactions than expected?

### `intact_get_interactions`
- **Input**: `identifier` (string — UniProt ID or gene name)
- **Output**: Molecular interaction data from IntAct

### `intact_search_interactions`
- **Input**: `query` (string), `first` (int, default 0), `max` (int, default 25)
- **Output**: Search results for interactions

### `HPA_get_protein_interactions_by_gene`
- **Input**: `gene_name` (string)
- **Output**: `{gene, interactions, interactor_count, interactors: [...]}`

### `humanbase_ppi_analysis`
- **Input**: `gene_list` (array), `tissue` (string), `max_node` (int), `interaction` (string: `'coexpression'`, `'interaction'`, or `'coexpression_and_interaction'`), `string_mode` (bool) — **ALL REQUIRED**
- **Output**: Tissue-specific PPI network

---

## Pathway & Network Layer Tools

### `enrichr_gene_enrichment_analysis`
- **Input**: `gene_list` (array of gene symbols, min 2), `libs` (array of library names, **REQUIRED**)
- **Output**: `{status: 'success', data: '{...JSON string...}'}`
- **Note**: The `data` field is a JSON string — must be parsed. Contains `connected_paths` and per-library results.
- **Key libraries**: `'KEGG_2021_Human'`, `'Reactome_2022'`, `'WikiPathway_2023_Human'`, `'GO_Biological_Process_2023'`, `'GO_Molecular_Function_2023'`, `'GO_Cellular_Component_2023'`

**Verified response example**:
```json
{
  "status": "success",
  "data": "{\"connected_paths\": {\"Path: ...\": \"Total Weight: ...\"}}"
}
```

### `ReactomeAnalysis_pathway_enrichment`
- **Input**: `identifiers` (string — space-separated gene list), optional `page_size` (int, default 20), `include_disease` (bool), `projection` (bool)
- **Output**: `{data: {token, analysis_type, pathways_found, pathways: [{pathway_id, name, species, is_disease, is_lowest_level, entities_found, entities_total, entities_ratio, p_value, fdr, reactions_found, reactions_total}]}}`

**Verified response example**:
```json
{
  "data": {
    "token": "...",
    "pathways_found": 154,
    "pathways": [
      {
        "pathway_id": "R-HSA-1251985",
        "name": "Nuclear signaling by ERBB4",
        "species": "Homo sapiens",
        "is_disease": false,
        "is_lowest_level": true,
        "entities_found": 3,
        "entities_total": 47,
        "p_value": 4.0e-06,
        "fdr": 0.00068
      }
    ]
  }
}
```

### `Reactome_map_uniprot_to_pathways`
- **Input**: `id` (string — UniProt accession)
- **Output**: List of Reactome pathways containing this protein

### `Reactome_get_pathway`
- **Input**: `stId` (string — Reactome stable ID, e.g. `'R-HSA-73817'`)
- **Output**: Pathway details

### `Reactome_get_pathway_reactions`
- **Input**: `stId` (string)
- **Output**: Reactions within pathway

### `kegg_search_pathway`
- **Input**: `keyword` (string)
- **Output**: Array of KEGG pathway matches

### `kegg_get_pathway_info`
- **Input**: `pathway_id` (string, e.g. `'hsa04930'`)
- **Output**: Detailed pathway information

### `WikiPathways_search`
- **Input**: `query` (string), optional `organism` (string, e.g. `'Homo sapiens'`)
- **Output**: Matching community-curated pathways

---

## Gene Ontology Tools

### `GO_get_annotations_for_gene`
- **Input**: `gene_id` (string — gene symbol or UniProt ID)
- **Output**: List of GO annotations with terms, aspects, evidence codes

### `GO_search_terms`
- **Input**: `query` (string)
- **Output**: Matching GO terms

### `QuickGO_annotations_by_gene`
- **Input**: `gene_product_id` (string — UniProt accession in `UniProtKB:ACCESSION` format, e.g. `'UniProtKB:P02649'`), optional `aspect` (string: `'biological_process'`, `'molecular_function'`, `'cellular_component'`), `taxon_id` (int: 9606), `limit` (int: 25)
- **Output**: GO annotations with evidence codes

### `OpenTargets_get_target_gene_ontology_by_ensemblID`
- **Input**: `ensemblId` (string)
- **Output**: GO terms associated with target

---

## Therapeutic Landscape Tools

### `OpenTargets_get_associated_drugs_by_disease_efoId`
- **Input**: `efoId` (string), `size` (int, **REQUIRED** — use 100)
- **Output**: `{data: {disease: {knownDrugs: {count, rows: [{drug: {id, name, tradeNames, maximumClinicalTrialPhase, isApproved, hasBeenWithdrawn}, phase, mechanismOfAction, target: {id, approvedSymbol}, disease: {id, name}, urls: [{url, name}]}]}}}}`

### `OpenTargets_get_target_tractability_by_ensemblID`
- **Input**: `ensemblId` (string)
- **Output**: Tractability assessment (small molecule, antibody, PROTAC, etc.)

### `OpenTargets_get_associated_drugs_by_target_ensemblID`
- **Input**: `ensemblId` (string), `size` (int, **REQUIRED**)
- **Output**: Drugs targeting this gene/protein

### `OpenTargets_get_drug_mechanisms_of_action_by_chemblId`
- **Input**: `chemblId` (string)
- **Output**: Mechanism of action details

### `search_clinical_trials`
- **Input**: `query_term` (string, **REQUIRED**), optional `condition` (string), `intervention` (string), `pageSize` (int, default 10)
- **Output**: Clinical trial results
- **Note**: `query_term` is required even if `condition` is provided.

---

## Utility Tools

### `PubMed_search_articles`
- **Input**: `query` (string), `limit` (int)
- **Output**: PubMed article results

### `ensembl_lookup_gene`
- **Input**: `gene_id` (string), `species` (string — `'homo_sapiens'` **REQUIRED**)
- **Output**: Gene lookup from Ensembl

### `MyGene_query_genes`
- **Input**: `query` (string), `species` (string), `fields` (string), `size` (int)
- **Output**: Gene metadata via MyGene.info

### `OpenTargets_get_similar_entities_by_disease_efoId`
- **Input**: `efoId` (string), `threshold` (float), `size` (int) — **ALL REQUIRED**
- **Output**: Similar diseases
