# Tier 2: Medium Risk (tested rounds 85-87)

All scenarios below have been tested. Included for reference and regression.

## 10-omics (Round 85 — clean)

```bash
python -m tooluniverse.cli run PubMed_search_articles '{"query": "metabolomics type 2 diabetes", "max_results": 3}'
python -m tooluniverse.cli run PubChem_get_CID_by_compound_name '{"name": "glucose"}'
python -m tooluniverse.cli run Crossref_search_works '{"query": "metabolomics diabetes biomarkers", "limit": 3}'
python -m tooluniverse.cli run SemanticScholar_search_papers '{"query": "lipidomics insulin resistance", "limit": 3}'
python -m tooluniverse.cli run ArXiv_search_papers '{"query": "RNA structure prediction deep learning", "limit": 3}'
```

### Undertested omics tools (prior bugs, not yet regression-tested)

```bash
# MetaboLights — prior bug: pagination ignored (round 74)
python -m tooluniverse.cli grep "MetaboLights"
# Run each tool found with relevant args

# MetabolomicsWorkbench — prior bug: moverz URL broken (round 73-74)
python -m tooluniverse.cli grep "MetabolomicsWorkbench"
# Run each tool found with relevant args

# ProteomeXchange — prior bug: title/instruments (round 73)
python -m tooluniverse.cli grep "ProteomeXchange"
# Run each tool found with relevant args
```

## 08-pathways (Round 86 — 1 bug fixed)

```bash
python -m tooluniverse.cli run kegg_search_pathway '{"keyword": "PI3K-Akt"}'
python -m tooluniverse.cli run kegg_get_pathway_info '{"pathway_id": "hsa04151"}'
python -m tooluniverse.cli run Reactome_get_pathway '{"stId": "R-HSA-73817"}'
python -m tooluniverse.cli run Reactome_get_pathway_reactions '{"stId": "R-HSA-73817"}'
python -m tooluniverse.cli run OpenTargets_get_target_gene_ontology_by_ensemblID '{"ensemblId": "ENSG00000141510"}'
python -m tooluniverse.cli run kegg_get_pathway_info '{"pathway_id": "hsa05010"}'
```

## 05-clinical (Round 87 — clean)

```bash
python -m tooluniverse.cli run search_clinical_trials '{"condition": "non-small cell lung cancer", "intervention": "osimertinib", "pageSize": 3}'
python -m tooluniverse.cli run cBioPortal_get_cancer_studies '{"limit": 5}'
python -m tooluniverse.cli run cBioPortal_get_mutations '{"study_id": "luad_tcga", "gene_list": "EGFR,ALK,ROS1"}'
python -m tooluniverse.cli run search_clinical_trials '{"condition": "breast cancer", "intervention": "trastuzumab", "pageSize": 3}'
python -m tooluniverse.cli run search_clinical_trials '{"condition": "diabetes mellitus", "intervention": "metformin", "pageSize": 1}'
```
