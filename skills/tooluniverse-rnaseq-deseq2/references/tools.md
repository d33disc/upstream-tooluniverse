# ToolUniverse Tool Reference

Detailed parameter tables for all ToolUniverse tools used in RNA-seq / DESeq2 analysis workflows.

Call tools from an MCP client using:
```
mcp__tooluniverse__execute_tool(tool_name="<tool_name>", arguments={...})
```

Use ToolUniverse tools **only for gene annotation**, not for differential expression or enrichment. Use PyDESeq2 and gseapy for those.

---

## MyGene_query_genes

Query MyGene.info for gene information, ID conversion, and annotation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Gene symbol, Entrez ID, Ensembl ID, or free-text search term |
| `species` | string | No | Filter by organism: `human`, `mouse`, `rat`, or NCBI taxon ID. Default: no filter |
| `fields` | string | No | Comma-separated fields to return. Default: `symbol,name,entrezgene,ensembl.gene`. Common values: `all`, `summary`, `go`, `pathway` |
| `size` | integer | No | Max results to return. Default: 10 |
| `from` | integer | No | Offset for pagination. Default: 0 |

**Example:** Convert gene symbol to Ensembl ID
```
mcp__tooluniverse__execute_tool(
    tool_name="MyGene_query_genes",
    arguments={"query": "TP53", "species": "human", "fields": "symbol,ensembl.gene,entrezgene"}
)
```

---

## ensembl_lookup_gene

Fetch gene details from Ensembl REST API by Ensembl gene ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene_id` | string | Yes | Ensembl gene ID (e.g., `ENSG00000141510`) |
| `species` | string | No | Species name: `homo_sapiens`, `mus_musculus`, etc. Default: inferred from ID |
| `expand` | boolean | No | If true, include transcripts and exons. Default: false |

**Example:** Look up human TP53
```
mcp__tooluniverse__execute_tool(
    tool_name="ensembl_lookup_gene",
    arguments={"gene_id": "ENSG00000141510", "species": "homo_sapiens"}
)
```

---

## ensembl_get_sequence

Retrieve nucleotide or protein sequence from Ensembl.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Ensembl gene, transcript, or protein ID |
| `type` | string | No | Sequence type: `genomic`, `cdna`, `cds`, `protein`. Default: `genomic` |
| `species` | string | No | Species name (e.g., `homo_sapiens`) |

**Example:** Get CDS for a transcript
```
mcp__tooluniverse__execute_tool(
    tool_name="ensembl_get_sequence",
    arguments={"id": "ENST00000269305", "type": "cds"}
)
```

---

## UniProt_search_proteins

Search UniProt for protein entries by name, gene, or keyword.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query: protein name, gene name, UniProt accession, or keyword |
| `organism` | string | No | NCBI taxon ID or name (e.g., `9606` for human, `10090` for mouse) |
| `reviewed` | boolean | No | If true, restrict to Swiss-Prot (manually reviewed). Default: false |
| `fields` | string | No | Comma-separated return fields. Default: `accession,id,gene_names,organism_name,protein_name` |
| `size` | integer | No | Max results. Default: 10 |

**Example:** Find human BRCA1 protein entry
```
mcp__tooluniverse__execute_tool(
    tool_name="UniProt_search_proteins",
    arguments={"query": "BRCA1", "organism": "9606", "reviewed": true}
)
```

---

## UniProt_get_protein

Fetch a full UniProt entry by accession number.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `accession` | string | Yes | UniProt accession (e.g., `P04637` for human TP53) |
| `format` | string | No | Response format: `json`, `fasta`, `txt`. Default: `json` |

**Example:** Get TP53 UniProt entry
```
mcp__tooluniverse__execute_tool(
    tool_name="UniProt_get_protein",
    arguments={"accession": "P04637"}
)
```

---

## OpenTargets_get_gene

Get disease-gene associations, tractability, and target safety information from Open Targets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene_id` | string | Yes | Ensembl gene ID (e.g., `ENSG00000141510`) |
| `fields` | list | No | Fields to include: `associatedDiseases`, `tractability`, `safetyLiabilities`, `expressions`, `pathways`. Default: all |
| `size` | integer | No | Max disease associations to return. Default: 10 |

**Example:** Get disease associations for TP53
```
mcp__tooluniverse__execute_tool(
    tool_name="OpenTargets_get_gene",
    arguments={"gene_id": "ENSG00000141510", "fields": ["associatedDiseases"], "size": 20}
)
```

---

## NCBI_gene_search

Search NCBI Gene database by name, symbol, or keyword.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Gene name, symbol, or free-text query |
| `organism` | string | No | Organism name or taxon ID (e.g., `Homo sapiens`, `9606`) |
| `retmax` | integer | No | Max results to return. Default: 20 |
| `retstart` | integer | No | Offset for pagination. Default: 0 |

**Example:** Search for EGFR in human
```
mcp__tooluniverse__execute_tool(
    tool_name="NCBI_gene_search",
    arguments={"query": "EGFR", "organism": "Homo sapiens", "retmax": 5}
)
```

---

## NCBI_fetch_gene

Fetch a full NCBI Gene entry by gene ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene_id` | string or integer | Yes | NCBI Gene ID (Entrez ID), e.g., `1956` for EGFR |
| `format` | string | No | Response format: `json`, `xml`, `text`. Default: `json` |

**Example:** Fetch human EGFR gene record
```
mcp__tooluniverse__execute_tool(
    tool_name="NCBI_fetch_gene",
    arguments={"gene_id": 1956}
)
```

---

## Notes for Agent Callers

- All tool calls return JSON. Parse the returned object for the specific field needed.
- For ID conversion workflows: use `MyGene_query_genes` first to get Ensembl IDs, then pass those to `ensembl_lookup_gene` or `OpenTargets_get_gene`.
- When annotating large gene lists (>100 genes), batch requests or use the `size` parameter; avoid calling one tool per gene in a loop.
- Use the `find_tools` MCP endpoint to discover additional annotation tools (e.g., for STRING PPI, Reactome pathway membership, or organism-specific databases).
