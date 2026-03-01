# Tool Parameters Reference

Complete parameter documentation for ToolUniverse tools used in multi-omics integration. All tools are called via:

```
mcp__tooluniverse__execute_tool(tool_name="<name>", arguments={...})
```

---

## Enrichment Tools

### enrichr_enrich

Run over-representation analysis (ORA) against any of 220+ Enrichr libraries.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `gene_list` | string | Yes | — | Comma-separated gene symbols (e.g., `"TP53,BRCA1,EGFR"`) |
| `library` | string | Yes | — | Enrichr library name (e.g., `"KEGG_2021_Human"`, `"GO_Biological_Process_2021"`, `"Reactome_2022"`) |
| `organism` | string | No | `"human"` | Organism: `"human"`, `"mouse"`, `"rat"`, `"fly"`, `"yeast"`, `"worm"` |
| `cutoff` | float | No | `0.05` | Adjusted p-value threshold for returned results |

**Returns**: Object with `results` list. Each result includes `Term`, `P-value`, `Adjusted P-value`, `Overlap` (format `"X/Y"`), `Odds Ratio`, `Combined Score`, `Genes` (semicolon-separated).

**Example call**:
```
mcp__tooluniverse__execute_tool(
    tool_name="enrichr_enrich",
    arguments={
        "gene_list": "TP53,BRCA1,MYC,CDK1,EGFR",
        "library": "KEGG_2021_Human",
        "organism": "human"
    }
)
```

**Common libraries for multi-omics**:
- `"KEGG_2021_Human"` — metabolic and signaling pathways
- `"GO_Biological_Process_2021"` — biological process GO terms
- `"Reactome_2022"` — curated reaction-level pathways
- `"MSigDB_Hallmark_2020"` — 50 hallmark gene sets
- `"DisGeNET"` — gene-disease associations
- `"ClinVar_2019"` — clinically significant variants

---

### reactome_pathway_analysis

Submit gene list to Reactome for hierarchical pathway enrichment.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `gene_list` | list[string] | Yes | — | List of gene symbols |
| `species` | string | No | `"Homo sapiens"` | Species name (full binomial) |
| `projection` | boolean | No | `true` | Project to human orthologs if using non-human genes |
| `include_interactors` | boolean | No | `false` | Expand with Reactome interactors |

**Returns**: Pathway results with `stId` (Reactome stable ID), `name`, `entities.pValue`, `entities.fdr`, `entities.found`, `entities.total`, `entities.ratio`.

**Example call**:
```
mcp__tooluniverse__execute_tool(
    tool_name="reactome_pathway_analysis",
    arguments={
        "gene_list": ["TP53", "BRCA1", "CDK1", "CCND1"],
        "species": "Homo sapiens"
    }
)
```

**Notes**:
- Use `stId` to retrieve pathway diagrams and sub-pathway hierarchies.
- Reactome is preferred over KEGG for mechanistic reaction-level detail.

---

### string_enrichment

Functional enrichment using STRING database (combines PPI evidence with pathway annotation).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `identifiers` | string | Yes | — | Newline-separated gene/protein identifiers |
| `species` | integer | No | `9606` | NCBI taxonomy ID (9606 = human, 10090 = mouse) |
| `caller_identity` | string | No | `"tooluniverse"` | Identifier for STRING API usage tracking |

**Returns**: List of enrichment terms with `category`, `term`, `description`, `number_of_genes`, `number_of_genes_in_background`, `p_value`, `fdr`.

**Example call**:
```
mcp__tooluniverse__execute_tool(
    tool_name="string_enrichment",
    arguments={
        "identifiers": "TP53\nBRCA1\nMYC\nCDK1",
        "species": 9606
    }
)
```

**Notes**:
- STRING enrichment incorporates network topology context.
- Categories returned include: `Process` (GO BP), `Component` (GO CC), `Function` (GO MF), `KEGG`, `Reactome`, `PFAM`, `InterPro`.

---

### panther_enrichment

GO enrichment via PANTHER with gene function classification.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `gene_list` | string | Yes | — | Comma-separated gene symbols or IDs |
| `organism` | string | Yes | — | Organism code (e.g., `"HUMAN"`, `"MOUSE"`) |
| `annotation_dataset` | string | No | `"GO:0008150"` | GO namespace: `"GO:0008150"` (BP), `"GO:0003674"` (MF), `"GO:0005575"` (CC) |
| `test_type` | string | No | `"FISHER"` | Statistical test: `"FISHER"` or `"BINOMIAL"` |
| `correction` | string | No | `"FDR"` | Multiple testing: `"FDR"`, `"BONFERRONI"`, or `"NONE"` |

---

## Gene ID Conversion Tools

### mygene_query

Convert between gene identifier types (Ensembl, symbol, Entrez, UniProt, RefSeq).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | — | Query string. For batch: comma-separated IDs. For single: any ID format |
| `fields` | string | No | `"symbol,ensembl,entrezgene"` | Comma-separated fields to return |
| `species` | string | No | `"human"` | Species filter |
| `scopes` | string | No | auto-detect | Input ID type: `"symbol"`, `"ensembl.gene"`, `"entrezgene"`, `"uniprot"` |

**Returns**: List of gene records with requested fields. Unmatched queries flagged with `"notfound": true`.

**Example call** (batch Ensembl → symbol conversion):
```
mcp__tooluniverse__execute_tool(
    tool_name="mygene_query",
    arguments={
        "q": "ENSG00000141510,ENSG00000012048",
        "fields": "symbol,entrezgene",
        "scopes": "ensembl.gene",
        "species": "human"
    }
)
```

---

### ensembl_gene_lookup

Retrieve gene annotation and genomic coordinates from Ensembl.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `id` | string | Yes | — | Ensembl gene ID (e.g., `"ENSG00000141510"`) |
| `expand` | boolean | No | `false` | Include transcript and exon details |
| `species` | string | No | `"human"` | Species (used if querying by symbol) |

**Returns**: Gene record with `id`, `display_name` (symbol), `description`, `seq_region_name` (chromosome), `start`, `end`, `strand`, `biotype`.

**Use in CpG-to-gene mapping**: Retrieve gene TSS and boundaries to classify CpG probes as promoter (TSS ± 2 kb) or gene body.

---

## Protein Annotation Tools

### uniprot_search

Search UniProt for protein records and retrieve gene mappings.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | — | UniProt query string (e.g., gene symbol, UniProt accession, protein name) |
| `fields` | string | No | `"accession,gene_names,organism_name,reviewed"` | Fields to return |
| `format` | string | No | `"json"` | Output format: `"json"`, `"tsv"`, `"fasta"` |
| `size` | integer | No | `25` | Maximum number of results |

**Example call** (map protein accession to gene symbol):
```
mcp__tooluniverse__execute_tool(
    tool_name="uniprot_search",
    arguments={
        "query": "accession:P04637",
        "fields": "accession,gene_names,protein_name",
        "format": "json"
    }
)
```

**Notes**:
- Filter to reviewed (Swiss-Prot) entries by appending `AND reviewed:true` to the query.
- Use `gene_names` field to extract primary gene symbol from proteomics data.

---

### string_network

Retrieve protein-protein interaction network from STRING.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `identifiers` | string | Yes | — | Newline-separated gene/protein identifiers |
| `species` | integer | No | `9606` | NCBI taxonomy ID |
| `required_score` | integer | No | `400` | Minimum interaction confidence (0–1000). 400 = medium, 700 = high |
| `network_type` | string | No | `"functional"` | `"functional"` (co-expression + text + experiments) or `"physical"` (direct binding only) |

**Returns**: Edge list with `stringId_A`, `stringId_B`, `preferredName_A`, `preferredName_B`, `score`.

**Use in multi-omics**: Identify hub genes in the PPI network that appear as multi-omics biomarkers, suggesting regulatory centrality.

---

## Disease & Drug Target Annotation Tools

### opentargets_gene

Retrieve gene-disease associations and drug target evidence from Open Targets.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `gene_id` | string | Yes | — | Ensembl gene ID (e.g., `"ENSG00000141510"`) |

**Returns**: Associated diseases with scores per evidence type (genetic, somatic, drugs, literature, RNA expression, animal models).

**Use in biomarker validation**: Confirm that multi-omics biomarker candidates have prior disease-gene evidence and drug target tractability.

---

### gwas_catalog_search

Search the GWAS Catalog for trait-variant-gene associations.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | — | Trait name, gene symbol, or rsID |
| `p_value_cutoff` | float | No | `5e-8` | GWAS significance threshold |

**Returns**: List of associations with `trait`, `snp`, `gene`, `p_value`, `odds_ratio`, `pubmed_id`.

**Use in eQTL integration**: Map GWAS variants to genes; cross-reference with eQTL results to identify genetic regulatory mechanisms.

---

## Multi-Omics Evidence Scoring

When aggregating pathway evidence across omics layers, use this scoring approach:

For each pathway returned by any enrichment tool:
1. Record which omics layers have genes in the pathway (RNA-seq, proteomics, methylation, CNV).
2. For each omics layer, compute the mean absolute effect size for pathway genes (mean |log2FC|, mean |correlation|, mean |beta difference|, mean |log2 CNV ratio|).
3. Compute the multi-omics score as: `mean(per-layer effect sizes) × log2(n_layers + 1)`.
4. Rank pathways by multi-omics score. Pathways supported by 3+ layers with consistent direction receive the highest priority.

Example pathway score table format:

| Pathway | RNA DEGs | Protein DEPs | Methyl DMGs | CNV Genes | Score | Layers |
|---------|----------|-------------|-------------|-----------|-------|--------|
| Cell Cycle | 45 (↑) | 22 (↑) | 8 (hypo) | 5 (amp) | 8.5 | 4 |
| Immune Response | 38 (↑) | 12 (↑) | 15 (hypo) | — | 7.2 | 3 |
| Glycolysis | 20 (↑) | 10 (↑) | — | — | 5.1 | 2 |
