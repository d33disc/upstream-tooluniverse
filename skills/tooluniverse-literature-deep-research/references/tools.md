# Tool Reference: Literature Deep Research

Full tool lists by category for the `tooluniverse-literature-deep-research` skill.

---

## Literature Search

| Tool | Purpose |
|------|---------|
| `PubMed_search_articles` | Search PubMed; returns plain list of article dicts |
| `PMC_search_papers` | Search PubMed Central full-text |
| `EuropePMC_search_articles` | Europe PMC; supports `extract_terms_from_fulltext` and `source="PPR"` for preprints |
| `openalex_literature_search` | OpenAlex broad literature search |
| `Crossref_search_works` | Crossref DOI-linked search |
| `SemanticScholar_search_papers` | Semantic Scholar AI-ranked results |
| `BioRxiv_search_preprints` | bioRxiv preprint search |
| `MedRxiv_search_preprints` | medRxiv clinical preprint search |
| `ArXiv_search_papers` | ArXiv (q-bio, cs) preprint search |

## Citation Tools

| Tool | Purpose |
|------|---------|
| `PubMed_get_cited_by` | Papers citing a given PMID (primary; can be flaky — always fall back) |
| `EuropePMC_get_citations` | Fallback when PubMed citation lookup returns unexpectedly low counts |
| `PubMed_get_related` | Computationally related papers for a given PMID |
| `EuropePMC_get_references` | Backward citations from a given paper |

## Full-Text Snippet Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `EuropePMC_search_articles` with `extract_terms_from_fulltext` | Auto-snippet from OA full text | OA only; max 5 terms; first 3 OA articles per call |
| `SemanticScholar_get_pdf_snippets` | Targeted PDF snippet extraction | Requires OA PDF URL |
| `ArXiv_get_pdf_snippets` | ArXiv PDF snippets by arXiv ID | All ArXiv papers are OA |
| `get_webpage_text_from_url` | Manual download from DOI URL | Last resort; quality varies |

## Protein / Gene Annotation

| Tool | Purpose |
|------|---------|
| `UniProt_search` | Find UniProt accession for human protein |
| `UniProt_get_entry_by_accession` | Full UniProt entry with cross-references |
| `UniProt_id_mapping` | Map between ID types (UniProt AC ↔ Ensembl, etc.) |
| `UniProt_get_ptm_processing_by_accession` | PTMs and active sites |
| `InterPro_get_protein_domains` | Domain architecture with InterPro IDs |
| `MyGene_get_gene_annotation` | NCBI Gene ID, aliases, summary |
| `ensembl_lookup_gene` | Ensembl gene ID and biotype; provides versioned ID for GTEx |
| `alphafold_get_prediction` | AlphaFold structure availability |
| `proteins_api_get_protein` | Additional protein features |

## Expression

| Tool | Purpose | Notes |
|------|---------|-------|
| `GTEx_get_median_gene_expression` | Tissue expression in TPM | Requires versioned Ensembl ID (e.g., `ENSG00000114573.15`) |
| `HPA_get_rna_expression_by_source` | Human Protein Atlas expression data | |
| `HPA_get_subcellular_location` | Human Protein Atlas localization | |
| `CELLxGENE_get_expression_data` | Single-cell expression data | |

## Pathway and GO

| Tool | Purpose |
|------|---------|
| `GO_get_annotations_for_gene` | GO annotations (MF, BP, CC) |
| `Reactome_map_uniprot_to_pathways` | Reactome pathway memberships |
| `kegg_get_gene_info` | KEGG pathway membership |
| `OpenTargets_get_target_gene_ontology_by_ensemblID` | Open Targets GO annotations |

## Interaction

| Tool | Purpose |
|------|---------|
| `STRING_get_protein_interactions` | STRING protein-protein interactions |
| `intact_get_interactions` | IntAct curated interactions |
| `intact_get_complex_details` | IntAct complex details |
| `OpenTargets_get_target_interactions_by_ensemblID` | Open Targets interaction data |

## Variant and Disease

| Tool | Purpose |
|------|---------|
| `gnomad_get_gene_constraints` | pLI/LOEUF constraint scores |
| `gnomad_get_gene` | gnomAD variant data |
| `clinvar_search_variants` | ClinVar variant classifications |
| `OpenTargets_get_diseases_phenotypes_by_target_ensembl` | Disease-target associations |
| `DGIdb_get_drug_gene_interactions` | Drug-gene interaction database |

## Open Access

| Tool | Purpose | Notes |
|------|---------|-------|
| `Unpaywall_check_oa_status` | OA status + best URL | Requires email configuration |
| Europe PMC `isOpenAccess` field | Best-effort OA flag | No email needed |
| OpenAlex `is_oa` field | Best-effort OA flag | No email needed |
