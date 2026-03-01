# Tool Parameter Reference

Detailed parameter tables for tools used in the drug target validation pipeline.
For workflow guidance see `../SKILL.md`.

---

## Phase 0: Target Disambiguation

### MyGene_query_genes
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | Gene symbol or name. NOT `q` |
| `species` | string | No | Use `"human"` for human genes |
| `fields` | string | No | Comma-separated: `"symbol,name,ensembl.gene,uniprot.Swiss-Prot,entrezgene"` |

### UniProt_get_entry_by_accession
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `accession` | string | Yes | UniProt accession (e.g., `"P00533"`) |

Returns full entry including `uniProtKBCrossReferences` — parse for PDB and Ensembl xrefs.

### ensembl_lookup_gene
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_id` | string | Yes | Ensembl gene ID (e.g., `"ENSG00000146648"`) |
| `species` | string | Yes | REQUIRED. Use `"homo_sapiens"` |

**Warning**: Response is wrapped — access data via `result['data']` or `result.get('data', result)`.
Returns versioned ID in `result['data']['id']` (e.g., `"ENSG00000146648.18"`).

### ensembl_get_xrefs
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `id` | string | Yes | Ensembl gene ID. NOT `gene_id` |

### OpenTargets_get_target_id_description_by_name
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `targetName` | string | Yes | Gene symbol or target name |

### ChEMBL_search_targets
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pref_name__contains` | string | No | Partial name match |
| `organism` | string | No | Use `"Homo sapiens"` |
| `limit` | integer | No | Default 20 |

### UniProt_get_function_by_accession
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `accession` | string | Yes | UniProt accession |

**Warning**: Returns a **list of strings**, NOT a dict.

### UniProt_get_alternative_names_by_accession
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `accession` | string | Yes | UniProt accession |

---

## Phase 1: Disease Association

### OpenTargets_get_diseases_phenotypes_by_target_ensembl
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase, NOT `ensemblID` |

### OpenTargets_get_disease_id_description_by_name
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `diseaseName` | string | Yes | Disease name in English |

Returns EFO ID used in subsequent evidence calls.

### OpenTargets_target_disease_evidence
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `efoId` | string | Yes | EFO disease ID (e.g., `"EFO_0003060"`) |
| `ensemblId` | string | Yes | Target Ensembl ID |

### OpenTargets_get_evidence_by_datasource
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `efoId` | string | Yes | EFO disease ID |
| `ensemblId` | string | Yes | Target Ensembl ID |
| `datasourceIds` | array | No | e.g., `["ot_genetics_portal", "eva", "gene2phenotype", "genomics_england"]` |
| `size` | integer | No | Max results, default 10 |

### gwas_get_snps_for_gene
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `mapped_gene` | string | Yes | Gene symbol |
| `size` | integer | No | Default 10 |

### gwas_search_studies
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | Disease or trait name |
| `size` | integer | No | Default 10 |

### gnomad_get_gene_constraints
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_symbol` | string | Yes | Gene symbol. NOT `gene_id` |

Returns: `pLI` (probability of loss-of-function intolerance), `LOEUF`, `missense_z`, `pRec`.
Interpretation: pLI > 0.9 = highly LoF intolerant = likely essential.

### PubMed_search_articles
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | PubMed query string with field tags |
| `limit` | integer | No | Max results |

**Warning**: Returns a **plain list** of article dicts. Do NOT expect `{"articles": [...]}` wrapper.

### OpenTargets_get_publications_by_target_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `entityId` | string | Yes | Ensembl ID. NOT `ensemblId` |

---

## Phase 2: Druggability

### OpenTargets_get_target_tractability_by_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase |

Returns: label, modality (`SM`/`AB`/`PR`/`OC`), value (boolean or score).

### OpenTargets_get_target_classes_by_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase |

### Pharos_get_target
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene` | string | No | Gene symbol |
| `uniprot` | string | No | UniProt accession |

At least one of `gene` or `uniprot` is needed.
TDL levels: Tclin (approved drug) > Tchem (compounds) > Tbio (biology only) > Tdark (unknown).

### DGIdb_get_gene_druggability
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `genes` | array | Yes | Array of gene symbols, e.g., `["EGFR"]` |

### alphafold_get_prediction
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `qualifier` | string | Yes | UniProt accession. NOT `uniprot_accession` |

### alphafold_get_summary
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `qualifier` | string | Yes | UniProt accession |

### ProteinsPlus_predict_binding_sites
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pdb_id` | string | Yes | 4-character PDB ID |

Returns: pocket locations, druggability scores (DrugScore), volume, surface area.

### OpenTargets_get_chemical_probes_by_target_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase |

### OpenTargets_get_target_enabling_packages_by_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase |

---

## Phase 3: Chemical Matter

### ChEMBL_get_target_activities
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `target_chembl_id__exact` | string | Yes | Double underscore before `exact`; ChEMBL target ID |
| `limit` | integer | No | Default 20, max 100 per page |

Returns bioactivity records. Filter for `pChEMBL_value >= 6.0` for drug-like potency (IC50 <= 1 µM).

### BindingDB_get_ligands_by_uniprot
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `uniprot` | string | Yes | UniProt accession |
| `affinity_cutoff` | integer | No | Cutoff in nM (e.g., 10000 for 10 µM) |

Returns: SMILES, affinity_type (Ki/IC50/Kd), affinity value, PMID.

### PubChem_search_assays_by_target_gene
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_symbol` | string | Yes | Gene symbol |

### PubChem_get_assay_summary
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `aid` | string | Yes | PubChem assay ID as string |

### PubChem_get_assay_targets
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `aid` | string | Yes | PubChem assay ID as string |

### PubChem_get_assay_active_compounds
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `aid` | string | Yes | PubChem assay ID as string |

### OpenTargets_get_associated_drugs_by_target_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase |
| `size` | integer | Yes | REQUIRED — call will fail without it |

### ChEMBL_search_mechanisms
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `target_chembl_id` | string | No | ChEMBL target ID |
| `limit` | integer | No | Default 20 |

### DGIdb_get_gene_info
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `genes` | array | Yes | Array of gene symbols |

---

## Phase 4: Clinical Precedent

### FDA_get_mechanism_of_action_by_drug_name
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `drug_name` | string | Yes | Drug name (English) |

### FDA_get_indications_by_drug_name
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `drug_name` | string | Yes | Drug name |

### drugbank_get_targets_by_drug_name_or_drugbank_id
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | Drug name or DrugBank ID |
| `case_sensitive` | boolean | Yes | Typically `false` |
| `exact_match` | boolean | Yes | Typically `false` |
| `limit` | integer | Yes | Max results |

### drugbank_get_safety_by_drug_name_or_drugbank_id
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | Drug name or DrugBank ID |
| `case_sensitive` | boolean | Yes | Required |
| `exact_match` | boolean | Yes | Required |
| `limit` | integer | Yes | Required |

**Warning**: ALL four parameters are required. Missing any will cause an error.

### search_clinical_trials
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query_term` | string | Yes | REQUIRED. Search term |
| `intervention` | string | No | Intervention filter |
| `condition` | string | No | Condition/disease filter |
| `pageSize` | integer | No | Results per page |

### OpenTargets_get_drug_warnings_by_chemblId
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `chemblId` | string | Yes | ChEMBL drug ID |

### OpenTargets_get_drug_adverse_events_by_chemblId
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `chemblId` | string | Yes | ChEMBL drug ID |

---

## Phase 5: Safety

### OpenTargets_get_target_safety_profile_by_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase |

### GTEx_get_median_gene_expression
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gencode_id` | string | Yes | Versioned Ensembl ID (e.g., `"ENSG00000146648.18"`) |
| `operation` | string | Yes | REQUIRED. Must be `"median"` |

**Fallback**: If versioned ID returns empty, retry with unversioned Ensembl ID.

### HPA_search_genes_by_query
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `search_query` | string | Yes | Gene symbol |

### HPA_get_comprehensive_gene_details_by_ensembl_id
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensembl_id` | string | Yes | Ensembl gene ID |

### HPA_get_rna_expression_by_source
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_name` | string | Yes | Gene symbol |
| `source_type` | string | Yes | Required |
| `source_name` | string | Yes | Required |

**Warning**: All three parameters required.

### OpenTargets_get_biological_mouse_models_by_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase |

### FDA_get_adverse_reactions_by_drug_name
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `drug_name` | string | Yes | Drug name |

### FDA_get_warnings_and_cautions_by_drug_name
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `drug_name` | string | Yes | Drug name |

### FDA_get_boxed_warning_info_by_drug_name
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `drug_name` | string | Yes | Drug name |

### FDA_get_contraindications_by_drug_name
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `drug_name` | string | Yes | Drug name |

### OpenTargets_get_target_homologues_by_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase |

Returns paralogs and orthologs. High-identity human paralogs = selectivity risk.

---

## Phase 6: Pathway & Network

### Reactome_map_uniprot_to_pathways
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `id` | string | Yes | UniProt accession. NOT `uniprot_id` |

### Reactome_get_pathway
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `id` | string | Yes | Reactome pathway stId (e.g., `"R-HSA-177929"`) |

### Reactome_get_pathway_reactions
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `id` | string | Yes | Reactome pathway stId |

### STRING_get_protein_interactions
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `protein_ids` | array | Yes | Array of gene symbols, e.g., `["EGFR"]` |
| `species` | integer | Yes | NCBI taxon ID, use `9606` for human |
| `confidence_score` | float | No | Threshold 0-1, use `0.7` for high confidence |

### intact_get_interactions
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `identifier` | string | Yes | UniProt accession or gene name |

### OpenTargets_get_target_interactions_by_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase |

### OpenTargets_get_target_gene_ontology_by_ensemblID
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensemblId` | string | Yes | camelCase |

### GO_get_annotations_for_gene
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_id` | string | Yes | Gene symbol |

### STRING_functional_enrichment
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `protein_ids` | array | Yes | Array of gene symbols |
| `species` | integer | Yes | `9606` for human |

---

## Phase 7: Validation Evidence

### DepMap_get_gene_dependencies
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_symbol` | string | Yes | Gene symbol. NOT `gene_id` |

Score interpretation: < -0.5 = moderately essential; < -1.0 = strongly essential in cancer cell lines.

### CTD_get_gene_diseases
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `input_terms` | string | Yes | Gene symbol |

---

## Phase 8: Structural Insights

### pdbe_get_entry_summary
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pdb_id` | string | Yes | 4-character PDB ID (lowercase) |

### pdbe_get_entry_quality
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pdb_id` | string | Yes | 4-character PDB ID |

### pdbe_get_entry_experiment
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pdb_id` | string | Yes | 4-character PDB ID |

### pdbe_get_entry_molecules
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pdb_id` | string | Yes | 4-character PDB ID |

### get_protein_metadata_by_pdb_id
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pdb_id` | string | Yes | 4-character PDB ID |

### ProteinsPlus_generate_interaction_diagram
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `pdb_id` | string | Yes | PDB ID with co-crystallized ligand |

### InterPro_get_protein_domains
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `uniprot_accession` | string | Yes | UniProt accession |

### InterPro_get_domain_details
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `entry_id` | string | Yes | InterPro entry ID (e.g., `"IPR000719"`) |

---

## Phase 9: Literature

### EuropePMC_search_articles
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | Search query |
| `limit` | integer | No | Max results |

### openalex_search_works
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | Search query |
| `limit` | integer | No | Max results |

---

## Parameter Gotchas Summary

| Tool | Wrong | Correct |
|------|-------|---------|
| `ensembl_lookup_gene` | `id` | `gene_id` (+ species REQUIRED) |
| `ensembl_get_xrefs` | `gene_id` | `id` |
| `Reactome_map_uniprot_to_pathways` | `uniprot_id` | `id` |
| `GTEx_get_median_gene_expression` | missing `operation` | `operation="median"` REQUIRED |
| `OpenTargets_*` | `ensemblID` | `ensemblId` (camelCase d) |
| `OpenTargets_get_publications_*` | `ensemblId` | `entityId` |
| `OpenTargets_get_associated_drugs_*` | missing `size` | `size` REQUIRED |
| `MyGene_query_genes` | `q` | `query` |
| `alphafold_get_prediction` | `uniprot_accession` | `qualifier` |
| `drugbank_get_safety_*` | missing params | all four params REQUIRED |
| `PubMed_search_articles` | expect `{articles:[...]}` | plain list returned |
| `UniProt_get_function_by_accession` | expect dict | list of strings returned |
| `ChEMBL_get_target_activities` | `target_chembl_id=` | `target_chembl_id__exact=` |
| `search_clinical_trials` | missing `query_term` | `query_term` REQUIRED |
| `STRING_get_protein_interactions` | string `protein_ids` | array REQUIRED |
