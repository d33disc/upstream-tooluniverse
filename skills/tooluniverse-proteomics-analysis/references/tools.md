# Proteomics Tool Parameter Reference

Full parameter reference for ToolUniverse tools used in the proteomics analysis skill.
All tools are called via `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

---

## PTM and Peptide Evidence Tools

### EBIProteins_get_proteomics_ptm
Get experimentally detected PTMs from MS proteomics databases (PeptideAtlas, ProteomicsDB, MaxQB, EPD).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `accession` | str | yes | UniProt accession (e.g. `"P04637"` for TP53, `"P00533"` for EGFR) |

Returns: list of PTM features with `{position, modification_type, source_database, confidence}`.
Common modification types: `phosphoserine`, `phosphothreonine`, `phosphotyrosine`, `acetyllysine`, `ubiquitination`.

---

### EBIProteins_get_proteomics_peptides
Get MS-detected peptides with positions and detection confidence for a protein.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `accession` | str | yes | UniProt accession |

Returns: list of peptides with `{sequence, start, end, unique, source_database}`.
Use to validate protein detection and coverage.

---

### OmniPath_get_enzyme_substrate
Get kinase/phosphatase -> substrate PTM relationships from OmniPath (integrates PhosphoSite, phosphoELM, dbPTM, SIGNOR, HPRD, KEA).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `enzymes` | str | no | Gene symbol(s) or UniProt ID(s) for kinase/enzyme. Comma-separated for multiple. Example: `"CDK1"`, `"SRC,LCK"` |
| `substrates` | str | no | Gene symbol(s) or UniProt ID(s) for substrate. Example: `"STAT3"` |
| `types` | str | no | Modification type filter: `"phosphorylation"`, `"ubiquitination"`, `"acetylation"`, `"methylation"`. Default: all types |
| `organisms` | int | no | NCBI taxonomy ID. Default: `9606` (human) |
| `limit` | int | no | Max results to return |

At least one of `enzymes` or `substrates` must be provided.
Returns: edges with `{enzyme, substrate, residue, position, modification_type, references}`.

**Usage pattern** for kinase prediction: pass each significant phosphosite gene as `substrates` to find predicted upstream kinases.

---

## Enrichment and Pathway Tools

### enrichr_gene_enrichment_analysis
Perform gene set enrichment analysis via Enrichr across multiple libraries.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_list` | list[str] | yes | List of gene symbols. Minimum 2 genes. Example: `["TP53", "BRCA1", "EGFR"]` |
| `libs` | list[str] | yes | Enrichr library names. Default libraries: `["WikiPathways_2024_Human", "Reactome_Pathways_2024", "MSigDB_Hallmark_2020", "GO_Molecular_Function_2023", "GO_Biological_Process_2023"]` |

**Recommended `libs` for proteomics**:
```
["GO_Biological_Process_2023", "GO_Molecular_Function_2023",
 "KEGG_2021_Human", "Reactome_Pathways_2024", "MSigDB_Hallmark_2020"]
```

Returns: enrichment paths with connectivity scores per library. Run separately for upregulated and downregulated gene lists.

---

### STRING_functional_enrichment
Identify enriched biological functions for a protein set (STRING-based, no API key required).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `protein_ids` | list[str] | yes | Gene names, UniProt IDs, or Ensembl IDs. Minimum 3 recommended |
| `species` | int | no | NCBI taxonomy ID. Default: `9606`. Mouse: `10090` |
| `category` | str | no | One of: `"Process"` (GO-BP), `"Component"` (GO-CC), `"Function"` (GO-MF), `"KEGG"`, `"Reactome"`, `"WikiPathways"`, `"COMPARTMENTS"`, `"TISSUES"`, `"DISEASES"`. Default: `"Process"` |

**IMPORTANT**: `category` accepts only one value per call. Run multiple calls for GO-BP, KEGG, and Reactome separately.
Returns: enriched terms with `{term, description, p_value, fdr, matching_proteins}`.

---

### Reactome_map_uniprot_to_pathways
Map a single UniProt protein to all Reactome pathways it participates in.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `id` | str | yes | UniProt accession (e.g. `"P04637"`) — parameter is `id`, NOT `uniprot_id` |

Returns: list of pathways with `{stId, name, species}`.
Use for single-protein context or to validate bulk enrichment results.

---

### GO_search_terms
Search Gene Ontology for terms by keyword.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | str | yes | Keyword (e.g. `"kinase activity"`, `"apoptosis"`) |

Returns: GO terms with IDs, names, definitions, and associated genes.

---

## Protein Interaction Tools

### STRING_get_network
Retrieve the protein-protein interaction network for a set of proteins.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `identifiers` | str | yes | **Newline-separated** gene symbols or identifiers. Example: `"TP53\nBRCA1\nEGFR"`. NOT comma-separated |
| `species` | int | no | NCBI taxonomy ID. Default: `9606` |
| `required_score` | int | no | Minimum STRING confidence score (0-1000). `400`=medium, `700`=high, `900`=highest. Default: `400` |
| `add_nodes` | int | no | Add N additional interacting nodes to expand network. Default: `0` |
| `show_query_node_labels` | int | no | `1` to label nodes. Default: `0` |

Returns: edges list with combined score and per-evidence scores (experimental, database, text-mining, coexpression, cooccurrence, fusion, neighborhood).

---

### STRING_get_interaction_partners
Get ranked interaction partners for a single query protein.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `identifiers` | str | yes | Single protein identifier (gene name, UniProt ID, or STRING ID) |
| `species` | int | no | Default: `9606` |
| `limit` | int | no | Max partners to return. Default: `10` |
| `required_score` | int | no | Minimum score threshold (0-1000) |

Returns: ranked list of interaction partners with detailed per-evidence-type scores.

---

### STRING_ppi_enrichment
Test whether a protein set has more interactions than expected by chance.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `protein_ids` | list[str] | yes | List of gene names or UniProt IDs. Minimum 3 proteins |
| `species` | int | no | Default: `9606` |
| `confidence_score` | float | no | Minimum score for counting interactions (0-1). Default: `0.4` |

Returns: `{observed_interactions, expected_interactions, p_value, avg_node_degree}`.
Significant (p < 0.05) indicates proteins form a real functional module.

---

### intact_get_interactions
Get curated experimental interactions from IntAct for a protein.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | str | yes | Gene name, UniProt accession, or IntAct identifier |
| `species` | str | no | Species filter (e.g. `"human"`, `"mouse"`) |
| `page` | int | no | Pagination (default: `0`) |
| `page_size` | int | no | Results per page (default: `25`) |

Returns: curated interactions with detection method, publication, and interaction type.
Higher specificity than STRING — use to confirm key edges.

---

### intact_get_interaction_network
Get interaction network centered on a protein (up to depth 3).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `identifier` | str | yes | IntAct identifier, UniProt ID, or gene name |
| `depth` | int | no | Network depth: `1`=direct only, `2`=2-hop, `3`=3-hop. Default: `1` |
| `format` | str | no | `"json"` or `"xml"`. Default: `"json"` |

---

## Protein Annotation Tools

### MyGene_query_genes
Batch query gene information including Ensembl IDs for identifier conversion.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | str | yes | Gene symbol, Ensembl ID, Entrez ID, or keyword |

Returns: `{hits: [{_id, symbol, ensembl, entrezgene, name}]}`.
Use to convert between gene symbols and Ensembl IDs before enrichment.

---

### MyGene_batch_query
Batch query multiple genes at once.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_ids` | list[str] | yes | List of gene symbols or IDs |
| `fields` | str | no | Comma-separated fields (e.g. `"symbol,ensembl,go,pathway"`) |

Returns: `{results: [{query, symbol, ensembl, ...}]}`.

---

### UniProt_search
Search UniProt for proteins by name, function, or organism.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | str | yes | Search query (e.g. `"EGFR human"`, `"kinase cancer"`) |
| `size` | int | no | Max results. Default: `10` |
| `fields` | str | no | Fields to return (e.g. `"accession,gene_names,organism_name"`) |

Returns: list of proteins with accessions and metadata.
Use to resolve gene names to UniProt accessions for downstream tool calls.

---

## Data Format Reference

| Platform | Intensity Column Pattern | Sample Naming | Notes |
|----------|--------------------------|---------------|-------|
| MaxQuant LFQ | `LFQ intensity [sample]` | After `LFQ intensity ` prefix | Use LFQ, not raw Intensity |
| MaxQuant raw | `Intensity [sample]` | After `Intensity ` prefix | Use only if LFQ unavailable |
| Spectronaut | `[sample].PG.Quantity` | Full sample name | Check report type |
| DIA-NN pr_matrix | Columns after `Protein.Group` | Sample file names | One column per sample |
| Proteome Discoverer | `Abundance: [sample]` | After `Abundance: ` prefix | Ratio or intensity depending on quant method |

---

## Phosphosite Localization Probability Thresholds

| Threshold | Class | Recommended Use |
|-----------|-------|-----------------|
| > 0.75 | Class I | Standard analysis; reliable site localization |
| > 0.90 | Class I (strict) | High-confidence analyses; kinase mapping |
| 0.50–0.75 | Class II | Exploratory only; flag as uncertain |
| < 0.50 | Class III | Exclude from quantitative analysis |

---

## Common Organism Taxonomy IDs (for STRING)

| Organism | Taxonomy ID |
|----------|-------------|
| Human | 9606 |
| Mouse | 10090 |
| Rat | 10116 |
| Zebrafish | 7955 |
| Yeast (S. cerevisiae) | 4932 |
| Fruit fly | 7227 |
| C. elegans | 6239 |
