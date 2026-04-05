# Research Strategy

Multi-database query patterns by domain. For each domain: key tools, correct
parameter names, recommended `max_results`, and common mistakes.

## The Expanding Frontier

Follow entities across domains. Each hop reveals new entities for the next.

```text
gene -> pathway -> disease -> drug -> trial -> company -> filings
```

Every tool call returns entities you did not search for. Chase them.

## Domain: Literature

| Tool | Key Params | max_results | Gotcha |
| ------ | ----------- | ------------- | -------- |
| `PubMed_search_articles` | `query`, `max_results` | 25-50 | NCBI rate limit: 3/s (no key), 10/s (with key) |
| `openalex_literature_search` | `search_keywords`, `max_results` | 25 | WRONG: `query`. CORRECT: `search_keywords` |
| `Crossref_search_works` | `query`, `limit` | 25 | `filter`: `"type:journal-article"` |
| `SemanticScholar_search_papers` | `query`, `limit` | 25 | Optional API key |
| `EuropePMC_search_articles` | `query`, `limit` | 25 | Returns `data_quality` field |

## Domain: Preprints

| Tool | Key Params | max_results | Gotcha |
| ------ | ----------- | ------------- | -------- |
| `BioRxiv_search_preprints` | `query`, `max_results` | 25 | Biology only |
| `MedRxiv_search_preprints` | `query`, `max_results` | 25 | Clinical/medical |
| `DOAJ_search_articles` | `query`, `max_results`, `type` | 25 | Open access journals |
| `CORE_search_papers` | `query`, `limit`, `year_from`, `year_to` | 25 | Largest OA aggregator |
| `PMC_search_papers` | `query`, `limit`, `date_from`, `article_type` | 25 | Full-text access |

## Domain: Genomics

| Tool | Key Params | max_results | Gotcha |
| ------ | ----------- | ------------- | -------- |
| `ClinVar_search_variants` | `gene` | 25 | Gene symbol, not Ensembl ID |
| `ensembl_lookup_gene` | gene symbol | -- | Returns Ensembl ID for ID resolution |
| `KEGG_link_entries` | `source`, `target` | -- | Use `hsa:GENE_ID` format |
| `KEGG_convert_ids` | `source_db`, `target_db`, `ids` | -- | Converts between Ensembl/UniProt/KEGG |
| `GWAS_Catalog_search` | `query` | 25 | Trait-to-SNP associations |

## Domain: Molecular / Protein

| Tool | Key Params | max_results | Gotcha |
| ------ | ----------- | ------------- | -------- |
| `UniProt_get_entry_by_accession` | `accession` | -- | e.g., `"P04637"` |
| `STRING_get_interaction_partners` | `identifiers`, `species` | -- | `species`: `9606` for human |
| `STRING_get_functional_annotations` | `identifiers`, `species` | -- | GO/KEGG enrichment |
| `PDB_search` | `query` | 10 | Structural data |
| `AlphaFold_get_prediction` | `uniprot_id` | -- | Predicted structure |

## Domain: Pharmacology

| Tool | Key Params | max_results | Gotcha |
| ------ | ----------- | ------------- | -------- |
| `PubChem_get_CID_by_compound_name` | `name` | -- | Returns CID (numeric) |
| `ChEMBL_get_molecule` | `chembl_id` | -- | e.g., `"CHEMBL25"` |
| `ChEMBL_get_molecule_targets` | `chembl_id` | -- | Drug-target binding |
| `OpenTargets_get_drug_indications_by_chemblId` | `chemblId` | -- | Approved + trial indications |
| `DrugBank_search` | `query` | 10 | Pharmacokinetics, interactions |

## Domain: Clinical

| Tool | Key Params | max_results | Gotcha |
| ------ | ----------- | ------------- | -------- |
| `ClinicalTrials_search_studies` | `query`, `max_results` | 25 | clinicaltrials.gov |
| `FAERS_count_reactions_by_drug_event` | `medicinalproduct` | -- | Free-text drug name |
| `FDA_get_adverse_reactions_by_drug_name` | `drug_name` | -- | OpenFDA adverse events |
| `DailyMed_search` | `query` | 10 | FDA-approved labeling |

## Domain: Expression

| Tool | Key Params | max_results | Gotcha |
| ------ | ----------- | ------------- | -------- |
| `GEO_search_datasets` | `query` | 10 | Gene expression datasets |
| `ArrayExpress_search` | `query` | 10 | European expression data |
| `GTEx_get_expression` | `gene` | -- | Tissue-level expression |

## Domain: Ontology

| Tool | Key Params | max_results | Gotcha |
| ------ | ----------- | ------------- | -------- |
| `GeneOntology_search` | `query` | 25 | GO terms |
| `OpenTargets_get_target_gene_ontology_by_ensemblID` | `ensemblId` | -- | WRONG: `ensembl_id`. CORRECT: `ensemblId` |
| `HPO_search` | `query` | 10 | Human phenotype terms |
| `Disease_Ontology_search` | `query` | 10 | Disease classification |

## Domain: Structural

| Tool | Key Params | max_results | Gotcha |
| ------ | ----------- | ------------- | -------- |
| `PDB_search` | `query` | 10 | Crystal/cryo-EM structures |
| `AlphaFold_get_prediction` | `uniprot_id` | -- | AI-predicted structures |
| `InterPro_search` | `query` | 10 | Protein domains/families |

## Domain: Web / Grey Literature

| Tool | Key Params | max_results | Gotcha |
| ------ | ----------- | ------------- | -------- |
| `WebSearch` | `query` | 10 | Press releases, news, regulatory docs |
| `Zenodo_search_records` | `query`, `max_results` | 10 | Datasets, preprints, software |

## Query Design Rules

1. Run `get_tool_info` before every `execute_tool` -- never guess param names.
2. Start broad (`"BRCA1 cancer"`), narrow on second pass
   (`"BRCA1 PARP synthetic lethality"`).
3. Use synonyms: gene aliases, drug brand vs generic, MeSH terms.
4. Set `max_results` 25-50 for discovery, 5-10 for targeted validation.
5. Timestamp every call (ISO 8601 UTC) for SI traceability.
6. Empty results are data -- record them as informative negatives.
7. When a tool fails, search the catalog for alternatives in the same category.
