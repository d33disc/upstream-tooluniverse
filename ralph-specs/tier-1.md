# Tier 1: Highest Risk (tested rounds 81-84)

All scenarios below have been tested. Included for reference and regression.

## 07-safety-pharma (Round 81 — 1 bug fixed)

```bash
python -m tooluniverse.cli run FAERS_calculate_disproportionality '{"drug_name": "IBUPROFEN", "adverse_event": "Gastrointestinal haemorrhage"}'
python -m tooluniverse.cli run FAERS_stratify_by_demographics '{"drug_name": "IBUPROFEN", "adverse_event": "Gastrointestinal haemorrhage"}'
python -m tooluniverse.cli run DailyMed_search_spls '{"drug_name": "ibuprofen", "pagesize": 1, "page": 1}'
python -m tooluniverse.cli run FAERS_calculate_disproportionality '{"drug_name": "METFORMIN", "adverse_event": "Lactic acidosis"}'
python -m tooluniverse.cli run FAERS_stratify_by_demographics '{"drug_name": "WARFARIN", "adverse_event": "Haemorrhage"}'
```

## 12-misc (Round 82 — 1 bug fixed)

```bash
python -m tooluniverse.cli run STRING_get_network '{"identifiers": "TP53", "species": 9606, "limit": 10}'
python -m tooluniverse.cli run STRING_get_network '{"identifiers": "EGFR", "species": 9606, "limit": 5}'
python -m tooluniverse.cli run InterPro_search_domains '{"query": "zinc finger"}'
python -m tooluniverse.cli run clinvar_search_variants '{"gene": "BRCA1"}'
python -m tooluniverse.cli run ensembl_lookup_gene '{"gene_id": "ENSG00000012048", "species": "homo_sapiens"}'
python -m tooluniverse.cli run GO_search_terms '{"query": "apoptotic process"}'
```

## 06-expression (Round 83 — clean)

```bash
python -m tooluniverse.cli run GTEx_get_expression_summary '{"gene_symbol": "TP53"}'
python -m tooluniverse.cli run GTEx_query_eqtl '{"gene_symbol": "TP53"}'
python -m tooluniverse.cli run GTEx_get_expression_summary '{"gene_symbol": "BRCA1"}'
python -m tooluniverse.cli run GTEx_get_expression_summary '{"gene_symbol": "CD274"}'
python -m tooluniverse.cli run GTEx_get_expression_summary '{"gene_symbol": "INS"}'
```

### Undertested expression tools (prior bugs, not yet regression-tested)

```bash
# HPA — prior bug: deprecated ppi column (round 68)
python -m tooluniverse.cli grep "HPA"
# Run each HPA tool found with: '{"gene": "EGFR"}'

# GxA — prior bug: silent geneId ignore (round 69)
python -m tooluniverse.cli grep "GxA"
# Run each GxA tool found with: '{"geneId": "ENSG00000141510"}'

# ExpressionAtlas — prior bug: schema key mismatch (round 69)
python -m tooluniverse.cli grep "ExpressionAtlas"
# Run each tool found with: '{"query": "TP53"}'
```

## 11-structural (Round 84 — clean)

```bash
python -m tooluniverse.cli run pdbe_get_entry_summary '{"pdb_id": "1M17"}'
python -m tooluniverse.cli run pdbe_get_entry_quality '{"pdb_id": "1M17"}'
python -m tooluniverse.cli run get_protein_metadata_by_pdb_id '{"pdb_id": "1M17"}'
python -m tooluniverse.cli run alphafold_get_prediction '{"qualifier": "P00533"}'
python -m tooluniverse.cli run InterPro_search_domains '{"query": "kinase"}'
```
