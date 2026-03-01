# Tool Reference — CRISPR Screen Analysis

Detailed parameter tables, return schemas, and example calls for all ToolUniverse tools used in the CRISPR screen analysis skill. All calls use `mcp__tooluniverse__execute_tool`.

---

## Enrichr_submit_genelist

Submit a gene list to Enrichr for enrichment analysis. Returns a `userListId` that is reused for all subsequent database queries.

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `gene_list` | list[str] | Yes | HGNC gene symbols | `["TP53","BRCA1","EGFR"]` |
| `description` | str | No | Label stored on the Enrichr server | `"CRISPR_essential_T1"` |

**Return schema**:
```json
{
  "status": "ok",
  "data": {
    "userListId": 12345,
    "shortId": "abc123"
  }
}
```

**Notes**:
- Gene list should be deduplicated before submission.
- Avoid submitting more than one list per second to prevent rate-limit errors (see Gotcha G5 in SKILL.md).
- The `userListId` is valid for several days; cache it for the session.

**Example call**:
```
mcp__tooluniverse__execute_tool(
  tool_name="Enrichr_submit_genelist",
  arguments={
    "gene_list": ["RPS6","RPL5","POLR2A","CDK2","CHEK1"],
    "description": "CRISPR_screen_Tier1_hits"
  }
)
```

---

## Enrichr_get_results

Retrieve enrichment results for a previously submitted gene list against one Enrichr library.

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `userListId` | int | Yes | ID returned by `Enrichr_submit_genelist` | `12345` |
| `backgroundType` | str | Yes | Enrichr library name | `"KEGG_2021_Human"` |

**Commonly used libraries for CRISPR screen analysis**:

| Library Name | Description |
|---|---|
| `KEGG_2021_Human` | KEGG metabolic and signaling pathways |
| `GO_Biological_Process_2021` | Gene Ontology biological process terms |
| `GO_Molecular_Function_2021` | Gene Ontology molecular function terms |
| `GO_Cellular_Component_2021` | Gene Ontology cellular component terms |
| `Reactome_2022` | Reactome pathway hierarchy |
| `MSigDB_Hallmark_2020` | 50 hallmark cancer biology gene sets |
| `WikiPathway_2021_Human` | Community-curated pathway maps |

**Return schema** (abbreviated):
```json
{
  "status": "ok",
  "data": {
    "KEGG_2021_Human": [
      [rank, term_name, p_value, z_score, combined_score, overlapping_genes, adj_p_value, null, null]
    ]
  }
}
```

Column order in the result list: `[rank, term, p_value, z_score, combined_score, genes, adj_p_value, _, _]`

**Significance filter**: Use `adj_p_value` (index 6) < 0.05.

**Example call**:
```
mcp__tooluniverse__execute_tool(
  tool_name="Enrichr_get_results",
  arguments={
    "userListId": 12345,
    "backgroundType": "Reactome_2022"
  }
)
```

---

## DGIdb_query_gene

Query the Drug-Gene Interaction Database for known drug interactions and druggability annotations for a gene.

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `gene_symbol` | str | Yes | HGNC gene symbol | `"EGFR"` |

**Return schema** (abbreviated):
```json
{
  "status": "ok",
  "data": {
    "matchedTerms": [
      {
        "geneName": "EGFR",
        "interactions": [
          {
            "drugName": "Erlotinib",
            "interactionTypes": ["inhibitor"],
            "source": "CIViC",
            "pmids": [12345678]
          }
        ],
        "categories": ["KINASE", "DRUGGABLE GENOME"]
      }
    ]
  }
}
```

**Key fields**:
- `matchedTerms[0].interactions` — list of drug-gene interaction records
- `matchedTerms[0].interactions[i].interactionTypes` — interaction class (inhibitor, activator, binder, etc.)
- `matchedTerms[0].categories` — druggability category (KINASE, GPCR, ION CHANNEL, etc.)
- `n_drugs` = `len(matchedTerms[0].interactions)` — use this as the druggability count in priority scoring

**Gotcha**: DGIdb uses current HGNC symbols. Aliases (e.g., HER2 instead of ERBB2) return zero results. Normalize symbols first using `Ensembl_get_gene_by_symbol`.

**Example call**:
```
mcp__tooluniverse__execute_tool(
  tool_name="DGIdb_query_gene",
  arguments={"gene_symbol": "WEE1"}
)
```

---

## STRING_get_network

Retrieve protein-protein interaction network data for one or more proteins from the STRING database.

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `identifiers` | str | Yes | Gene symbols separated by `%0d` (URL-encoded newline) | `"KRAS%0dSTK11"` |
| `species` | int | No | NCBI taxonomy ID (default 9606 = human) | `9606` |
| `required_score` | int | No | Minimum interaction score 0-1000 (default 400) | `700` |
| `network_type` | str | No | `"functional"` or `"physical"` (default functional) | `"physical"` |
| `limit` | int | No | Max interactions returned | `50` |

**Return schema** (abbreviated):
```json
{
  "status": "ok",
  "data": {
    "interactions": [
      {
        "stringId_A": "9606.ENSP00000...",
        "stringId_B": "9606.ENSP00000...",
        "preferredName_A": "KRAS",
        "preferredName_B": "RAF1",
        "score": 998
      }
    ]
  }
}
```

**Use in CRISPR analysis**: Check for network connections between synthetic lethal pairs and the driver mutation gene. A high-confidence interaction (score > 700) supports the SL hypothesis.

**Example call**:
```
mcp__tooluniverse__execute_tool(
  tool_name="STRING_get_network",
  arguments={
    "identifiers": "WEE1%0dTP53%0dCHEK1",
    "species": 9606,
    "required_score": 700
  }
)
```

---

## KEGG_get_pathway

Retrieve the list of genes in a KEGG pathway and pathway metadata.

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `pathway_id` | str | Yes | KEGG pathway ID | `"hsa04110"` |

**Common KEGG pathway IDs relevant to CRISPR screens**:

| Pathway | ID |
|---|---|
| Cell cycle | `hsa04110` |
| p53 signaling pathway | `hsa04115` |
| DNA replication | `hsa03030` |
| Proteasome | `hsa03050` |
| Ribosome | `hsa03010` |
| mTOR signaling | `hsa04150` |
| MAPK signaling | `hsa04010` |

**Return schema** (abbreviated):
```json
{
  "status": "ok",
  "data": {
    "pathway_id": "hsa04110",
    "name": "Cell cycle",
    "genes": ["CDK1","CDK2","CCNA2","CCNB1","TP53","RB1","E2F1"]
  }
}
```

**Example call**:
```
mcp__tooluniverse__execute_tool(
  tool_name="KEGG_get_pathway",
  arguments={"pathway_id": "hsa04110"}
)
```

---

## PubMed_search

Search PubMed for literature evidence supporting a hit or SL interaction.

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `query` | str | Yes | PubMed query string (supports MeSH terms, boolean operators) | `"WEE1 AND synthetic lethal AND KRAS"` |
| `max_results` | int | No | Maximum papers to return (default 10) | `20` |
| `sort` | str | No | Sort order: `"relevance"` or `"date"` | `"relevance"` |

**Return schema** (abbreviated):
```json
{
  "status": "ok",
  "data": {
    "papers": [
      {
        "pmid": "12345678",
        "title": "...",
        "abstract": "...",
        "authors": ["Smith J", "..."],
        "year": 2023,
        "journal": "Nature"
      }
    ]
  }
}
```

**Recommended query patterns**:
- Essentiality evidence: `"<GENE>"[Gene] AND ("CRISPR screen" OR "gene essentiality" OR "DepMap")`
- SL evidence: `"<GENE1>" AND "synthetic lethal" AND "<MUTATION_CONTEXT>"`
- Drug target context: `"<GENE>" AND ("clinical trial" OR "inhibitor") AND cancer`

---

## ClinVar_query_gene

Retrieve known pathogenic and likely pathogenic variants for a gene from ClinVar.

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `gene_symbol` | str | Yes | HGNC gene symbol | `"BRCA1"` |
| `clinical_significance` | str | No | Filter by significance (e.g., `"Pathogenic"`) | `"Pathogenic"` |

**Use in CRISPR analysis**: Confirms whether screen hits have disease-relevant mutations in the target gene, supporting prioritization as a therapeutic target.

---

## gnomAD_get_gene

Retrieve population-level variant frequency and constraint metrics from gnomAD.

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `gene_symbol` | str | Yes | HGNC gene symbol | `"POLR2A"` |
| `dataset` | str | No | gnomAD dataset version | `"gnomad_r2_1"` |

**Key constraint metrics**:
- `pLI` (probability of loss-of-function intolerance): > 0.9 suggests the gene is essential in humans (consistent with CRISPR screen essential hits)
- `LOEUF` (loss-of-function observed/expected upper bound): < 0.35 = highly constrained

---

## Ensembl_get_gene_by_symbol

Retrieve canonical Ensembl gene information and verify current HGNC symbol.

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `symbol` | str | Yes | Gene name (current or alias) | `"HER2"` |
| `species` | str | No | Species name (default `"homo_sapiens"`) | `"homo_sapiens"` |

**Return schema** (abbreviated):
```json
{
  "status": "ok",
  "data": {
    "id": "ENSG00000141736",
    "display_name": "ERBB2",
    "description": "erb-b2 receptor tyrosine kinase 2",
    "biotype": "protein_coding",
    "synonyms": ["HER2","NEU","NGL"]
  }
}
```

Use `display_name` as the canonical symbol before querying DGIdb or Enrichr.

---

## GEO_get_dataset

Download expression dataset metadata and sample information from GEO.

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `geo_id` | str | Yes | GEO accession (GSE or GDS prefix) | `"GSE123456"` |

**Use in CRISPR analysis**: Retrieve matched expression data for the same cell line used in the screen to enable Phase 7 expression-weighted target prioritization.

---

## ArrayExpress_get_experiment

Retrieve experiment metadata from ArrayExpress (alternative expression data source).

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `accession` | str | Yes | ArrayExpress accession (E-MTAB prefix) | `"E-MTAB-1234"` |

---

## Quick-Reference: Tool Call Pattern

All tools follow this pattern in MCP clients:

```
mcp__tooluniverse__execute_tool(
  tool_name="<TOOL_NAME>",
  arguments={
    "<param1>": <value1>,
    "<param2>": <value2>
  }
)
```

Response envelope is always:
```json
{
  "status": "ok" | "error",
  "data": { ... }
}
```

Always check `result["status"] == "ok"` before accessing `result["data"]`.
