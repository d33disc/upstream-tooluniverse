# Tool Parameter Reference

Detailed parameter tables and verified response structures for tools used in the Network Pharmacology Pipeline.

Back to: [SKILL.md](../SKILL.md)

---

## Compound Identification

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_drug_chembId_by_generic_name` | `drugName: str` | `{data: {search: {hits: [{id, name, description}]}}}` |
| `OpenTargets_get_drug_id_description_by_name` | `drugName: str` | `{data: {search: {hits: [{id, name, description}]}}}` |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | `query: str`, `case_sensitive: bool`, `exact_match: bool`, `limit: int` (ALL 4 required) | `{status, data: {drug_name, drugbank_id, ...}}` |
| `PubChem_get_CID_by_compound_name` | `name: str` | `{IdentifierList: {CID: [int]}}` — no data wrapper |
| `PubChem_get_compound_properties_by_CID` | `cid: int` | `{CID, MolecularWeight, ConnectivitySMILES, IUPACName}` |
| `ChEMBL_search_drugs` | `query: str`, `limit: int` | `{status, data: {drugs: [...]}}` |

---

## Target Identification

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_target_id_description_by_name` | `targetName: str` | `{data: {search: {hits: [{id, name, description}]}}}` |
| `ensembl_lookup_gene` | `gene_id: str`, `species: str` (REQUIRED — e.g., `"homo_sapiens"`) | `{status, data: {display_name, biotype, ...}}` |
| `MyGene_query_genes` | `query: str` | Gene info with cross-references |
| `Pharos_get_target` | `target_name: str` | Target with development level (Tclin/Tchem/Tbio/Tdark) |

---

## Disease Identification

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_disease_id_description_by_name` | `diseaseName: str` | `{data: {search: {hits: [{id, name, description}]}}}` |
| `OpenTargets_get_disease_description_by_efoId` | `efoId: str` | `{data: {disease: {id, name, description}}}` |
| `OpenTargets_get_disease_ids_by_efoId` | `efoId: str` | Disease cross-references (MONDO, OMIM, etc.) |
| `OpenTargets_multi_entity_search_by_query_string` | `queryString: str` | Broad fuzzy matching across all entity types |

---

## PPI / Network Edges

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `STRING_get_interaction_partners` | `protein_ids: list[str]`, `species: int` (9606), `limit: int` | `{status, data: [{stringId_A, stringId_B, preferredName_A, preferredName_B, score, ...}]}` |
| `STRING_get_network` | `protein_ids: list[str]`, `species: int` | Network data |
| `STRING_functional_enrichment` | `protein_ids: list[str]`, `species: int` | Enrichment results per category |
| `STRING_ppi_enrichment` | `protein_ids: list[str]`, `species: int` | PPI enrichment statistics (p-value, expected edges) |
| `OpenTargets_get_target_interactions_by_ensemblID` | `ensemblId: str`, `size: int` | `{data: {target: {interactions: {count, rows: [{intA, targetA: {id, approvedSymbol}, intB, targetB, score, sourceDatabase}]}}}}` |
| `intact_search_interactions` | `query: str`, `max: int` | Interaction data |
| `humanbase_ppi_analysis` | `gene_list: list`, `tissue: str`, `max_node: int`, `interaction: str`, `string_mode: str` (ALL 5 required) | Tissue-specific PPI network |

---

## Drug-Target Edges

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | `chemblId: str` | `{data: {drug: {mechanismsOfAction: {rows: [{mechanismOfAction, actionType, targetName, targets: [{id, approvedSymbol}]}]}}}}` |
| `OpenTargets_get_associated_targets_by_drug_chemblId` | `chemblId: str`, `size: int` | `{data: {drug: {linkedTargets: {count, rows: [{id, approvedSymbol}]}}}}` |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | `query: str`, `case_sensitive: bool`, `exact_match: bool`, `limit: int` (ALL 4 required) | `{status, data: {drug_name, targets: [{id, name, organism, actions}]}}` |
| `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` | `query: str`, `case_sensitive: bool`, `exact_match: bool`, `limit: int` (ALL 4 required) | Pharmacology details |
| `DGIdb_get_drug_gene_interactions` | `genes: list[str]` | `{data: {genes: {nodes: [{name, interactions: [{drug: {name, conceptId}, interactionTypes: [{type}]}]}]}}}` |
| `CTD_get_chemical_gene_interactions` | `input_terms: str` | `{data: [{ChemicalName, GeneSymbol, InteractionActions, ...}]}` |
| `ChEMBL_get_target_activities` | `target_chembl_id__exact: str`, `limit: int` | Activity data with `pchembl_value`, `standard_type` (IC50, Ki, etc.) |
| `ChEMBL_search_mechanisms` | `query: str`, `limit: int` | Mechanism data |
| `STITCH_resolve_identifier` | `identifier: str`, `species: int` | Resolved STITCH chemical ID |
| `STITCH_get_chemical_protein_interactions` | `identifiers: list[str]`, `species: int` | Chemical-protein interaction data |
| `BindingDB_get_ligands_by_uniprot` | `uniprot_accession: str` | Binding affinity data (Ki, Kd, IC50, EC50) |

---

## Target-Disease Edges

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_associated_targets_by_disease_efoId` | `efoId: str`, `limit: int` | `{data: {disease: {associatedTargets: {count, rows: [{target: {id, approvedSymbol}, score}]}}}}` |
| `OpenTargets_target_disease_evidence` | `efoId: str`, `ensemblId: str` (BOTH required) | Evidence across datasources (genetics, pathways, literature, etc.) |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblId: str`, `size: int` | Drugs linked to target |
| `OpenTargets_get_diseases_phenotypes_by_target_ensembl` | `ensemblId: str`, `size: int` | Diseases and phenotypes associated with target |
| `CTD_get_gene_diseases` | `input_terms: str` | `{data: [{GeneName, DiseaseName, DirectEvidence, ...}]}` |
| `GWAS_search_associations_by_gene` | `gene_name: str` | GWAS association data |
| `PharmGKB_get_gene_details` | `gene_symbol: str` | PharmGKB gene data with PGx annotations |

---

## Drug-Disease Edges

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_drug_indications_by_chemblId` | `chemblId: str`, `size: int` | `{data: {drug: {indications: {rows: [{disease: {id, name}, maxPhaseForIndication, references}]}}}}` |
| `OpenTargets_get_associated_diseases_by_drug_chemblId` | `chemblId: str`, `size: int` | `{data: {drug: {linkedDiseases: {count, rows: [{id, name, description}]}}}}` |
| `OpenTargets_get_approved_indications_by_drug_chemblId` | `chemblId: str` | `{data: {drug: {approvedIndications: ["EFO_XXXXX", ...]}}}` |
| `CTD_get_chemical_diseases` | `input_terms: str` | `{data: [{ChemicalName, DiseaseName, DirectEvidence: "therapeutic"\|"marker/mechanism", ...}]}` |
| `search_clinical_trials` | `query_term: str` (REQUIRED), `condition: str`, `pageSize: int` | `{studies: [{NCT ID, brief_title, brief_summary, ...}]}` |
| `clinical_trials_search` | `query: str`, `limit: int` | Trial data |
| `clinical_trials_get_details` | `nct_id: str` | Full trial details |
| `extract_clinical_trial_outcomes` | `nct_id: str` | Trial outcome measures and results |
| `extract_clinical_trial_adverse_events` | `nct_id: str` | Trial adverse event data |

---

## Pathway Analysis

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `ReactomeAnalysis_pathway_enrichment` | `identifiers: str` (space-separated gene symbols, NOT a list) | `{data: {pathways: [{pathway_id, name, p_value, fdr, entities_found, ...}]}}` |
| `enrichr_gene_enrichment_analysis` | `gene_list: list[str]`, `libs: list[str]` (REQUIRED) | Enrichment results per library |
| `drugbank_get_pathways_reactions_by_drug_or_id` | `query: str`, `case_sensitive: bool`, `exact_match: bool`, `limit: int` | Drug pathway and reaction data |

---

## Target Druggability

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `DGIdb_get_gene_druggability` | `genes: list[str]` | Druggability categories per gene |
| `OpenTargets_get_target_tractability_by_ensemblID` | `ensemblId: str` | Tractability buckets (small molecule, antibody, other modalities) |
| `OpenTargets_get_target_classes_by_ensemblID` | `ensemblId: str` | Target family classification (GPCR, kinase, etc.) |

---

## Safety Tools

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `FAERS_search_reports_by_drug_and_reaction` | `drug_name: str`, `limit: int` | Raw FAERS adverse event reports |
| `FAERS_filter_serious_events` | `operation: str` (REQUIRED), `drug_name: str`, `seriousness_type: str` | Serious event data |
| `FAERS_count_death_related_by_drug` | `medicinalproduct: str` (NOT `drug_name`) | `[{term: "alive", count: N}, {term: "death", count: N}]` |
| `FAERS_calculate_disproportionality` | `operation: str` (REQUIRED), `drug_name: str`, `adverse_event: str` | `{metrics: {PRR: {value, ci_95_lower, ci_95_upper}, ROR: {...}, IC: {...}}, signal_detection: {signal_detected, signal_strength}}` |
| `OpenTargets_get_drug_adverse_events_by_chemblId` | `chemblId: str` | `{data: {drug: {adverseEvents: {count, rows: [{name, meddraCode, count, logLR}]}}}}` |
| `OpenTargets_get_drug_warnings_by_chemblId` | `chemblId: str` | Drug warning data |
| `OpenTargets_get_drug_blackbox_status_by_chembl_ID` | `chemblId: str` | Black box warning boolean and description |
| `OpenTargets_get_target_safety_profile_by_ensemblID` | `ensemblId: str` | Known safety liabilities per target |
| `gnomad_get_gene_constraints` | `gene_symbol: str` | Gene constraint metrics: pLI (>0.9 = LoF intolerant), LOEUF |
| `FDA_get_warnings_and_cautions_by_drug_name` | `drug_name: str` | FDA label warning and caution text |
| `HPA_get_rna_expression_by_source` | `gene_name: str`, `source_type: str`, `source_name: str` | RNA expression by tissue/cell type |

---

## Literature Tools

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `PubMed_search_articles` | `query: str`, `max_results: int` | Plain list of `{pmid, title, authors, journal, pub_date, ...}` — NOT `{articles: [...]}` |
| `PubMed_Guidelines_Search` | `query: str` | Clinical guideline articles |
| `EuropePMC_search_articles` | `query: str`, `limit: int` | Article list |
| `OpenTargets_get_publications_by_drug_chemblId` | `chemblId: str`, `size: int` | Drug-associated publications |
| `OpenTargets_get_publications_by_disease_efoId` | `efoId: str`, `size: int` | Disease-associated publications |

---

## ADMET / Pharmacogenomics

| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `ADMETAI_predict_toxicity` | `smiles: list[str]` | Toxicity predictions |
| `ADMETAI_predict_BBB_penetrance` | `smiles: list[str]` | BBB penetrance score |
| `ADMETAI_predict_bioavailability` | `smiles: list[str]` | Oral bioavailability score |
| `PharmGKB_get_drug_details` | `drug_name: str` | PharmGKB drug entry |
| `PharmGKB_get_clinical_annotations` | `query: str` | Clinical PGx annotations |
