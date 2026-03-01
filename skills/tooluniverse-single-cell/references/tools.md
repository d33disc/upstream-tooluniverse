# ToolUniverse Tool Reference — Single-Cell Skill

Full parameter tables and return format details for all ToolUniverse tools used in the `tooluniverse-single-cell` skill.

Agents call tools via:
```
mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})
```

---

## OmniPath Tools

### OmniPath_get_ligand_receptor_interactions

Retrieve validated ligand-receptor pairs from OmniPath, which integrates CellPhoneDB, CellChatDB, ICELLNET, Ramilowski2015, Kirouac2010, and 100+ other curated databases.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `proteins` | string | No | Comma-separated gene symbols to filter interactions (e.g., `"EGFR,TNF"`). Omit to retrieve all pairs. |
| `databases` | string | No | Comma-separated database names to restrict results. Options include `CellPhoneDB`, `CellChatDB`, `ICELLNET`, `Ramilowski2015`. Omit to use all. |
| `organism` | string | No | Organism (default: `"human"`). |

**Returns**: JSON with structure:
```json
{
  "metadata": {"success": true, "n_interactions": 1234},
  "data": {
    "interactions": [
      {
        "source_genesymbol": "TGFB1",
        "target_genesymbol": "TGFBR1",
        "is_directed": true,
        "is_stimulation": true,
        "is_inhibition": false,
        "consensus_direction": true,
        "sources": ["CellPhoneDB", "CellChatDB"],
        "references": "PMID:..."
      }
    ]
  }
}
```

**Key columns in interactions list**:
- `source_genesymbol` — ligand gene symbol
- `target_genesymbol` — receptor gene symbol
- `is_directed` — whether interaction has a defined direction
- `sources` — list of databases that support this interaction

---

### OmniPath_get_signaling_interactions

Retrieve downstream signaling interactions from OmniPath. Use this after identifying top receptor hits to trace intracellular signaling cascades and identify downstream transcription factors.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `proteins` | string | No | Comma-separated gene symbols for the signaling proteins of interest. |
| `databases` | string | No | Comma-separated database names to filter. |
| `organism` | string | No | Organism (default: `"human"`). |
| `directed` | boolean | No | If true, return only directed interactions. |

**Returns**: Same structure as `OmniPath_get_ligand_receptor_interactions` but includes intracellular signaling edges (kinase → substrate, TF → target, etc.).

---

### OmniPath_get_complexes

Retrieve the subunit composition of protein complexes from OmniPath. Essential for multi-subunit receptors where all components must be expressed for the interaction to occur.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `proteins` | string | No | Comma-separated gene symbols to find complexes containing these proteins. |

**Returns**: JSON with structure:
```json
{
  "metadata": {"success": true},
  "data": {
    "complexes": [
      {
        "name": "IL2R_complex",
        "components_genesymbols": "IL2RA;IL2RB;IL2RG",
        "sources": ["CORUM", "PDB"]
      }
    ]
  }
}
```

**Usage**: Split `components_genesymbols` on `;` to get individual subunits. Check all subunits are expressed in the receiver cell type before counting the receptor as "present".

---

### OmniPath_get_cell_communication_annotations

Get pathway category and biological role annotations for ligand-receptor pairs. Useful for classifying interactions (e.g., immune checkpoint, growth factor, cytokine).

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `proteins` | string | No | Comma-separated gene symbols to look up annotations for. |

**Returns**: JSON with annotations including pathway names, biological categories, and roles.

---

## Gene Annotation Tools

### HPA_search_genes_by_query

Search the Human Protein Atlas for genes based on biological queries, including cell type expression patterns. Useful for finding canonical markers for a cell type.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Free-text query (e.g., `"CD4 T cell markers"`, `"monocyte surface proteins"`). |

**Returns**: JSON with gene list, tissue/cell type specificity scores, and expression levels.

---

### MyGene_query_genes

Query MyGene.info for gene metadata including aliases, Ensembl IDs, Entrez IDs, and functional annotations.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Gene query (symbol, Ensembl ID, Entrez ID, or keyword). |
| `fields` | string | No | Comma-separated fields to return (e.g., `"symbol,ensembl,entrezgene,go"`). Default returns common fields. |
| `species` | string | No | Species filter (e.g., `"human"`, `"mouse"`). Default: all. |

**Returns**: JSON with matching gene records.

---

### MyGene_batch_query

Batch convert or look up multiple gene IDs or symbols in a single call. Efficient for converting Ensembl IDs to gene symbols or vice versa for a full gene list.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ids` | string | Yes | Comma-separated gene IDs or symbols to look up. |
| `fields` | string | No | Fields to return (e.g., `"symbol,ensembl.gene,entrezgene"`). |
| `species` | string | No | Species filter. |
| `scopes` | string | No | Which field to search in (e.g., `"ensembl.gene"` when input IDs are Ensembl). |

**Returns**: JSON list with one record per input ID. Missing entries will have `"notfound": true`.

---

### ensembl_lookup_gene

Look up gene details from Ensembl by Ensembl gene ID. Returns gene coordinates, biotype, transcripts, and cross-references.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene_id` | string | Yes | Ensembl gene ID (e.g., `"ENSG00000139618"`). |
| `expand` | boolean | No | If true, include transcript and exon details. |
| `species` | string | No | Species (default: `"human"`). |

**Returns**: JSON with gene name, biotype, chromosome, start, end, strand, and (if expanded) transcript list.

---

### UniProt_get_function_by_accession

Retrieve the functional description of a protein from UniProt.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `accession` | string | Yes | UniProt accession (e.g., `"P01375"` for TNF). |

**Returns**: JSON with protein name, gene name, function text, subcellular location, and involvement in disease/pathway entries.

---

## Enrichment Tools

### PANTHER_enrichment

Run GO enrichment analysis (Biological Process, Molecular Function, Cellular Component) against the PANTHER database. Recommended for curated, human-reviewed GO annotations.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene_list` | string | Yes | Comma-separated gene symbols or IDs. |
| `organism` | string | Yes | Organism code (e.g., `"9606"` for human, `"10090"` for mouse). |
| `annotation_type` | string | No | GO category. Options: `"GO:0008150"` (BP), `"GO:0003674"` (MF), `"GO:0005575"` (CC), `"ANNOT_TYPE_ID_PANTHER_PATHWAY"`. Default: BP. |
| `test_type` | string | No | Statistical test. Options: `"FISHER"`, `"BINOMIAL"`. Default: `"FISHER"`. |
| `correction` | string | No | Multiple testing correction. Options: `"FDR"`, `"BONFERRONI"`, `"NONE"`. Default: `"FDR"`. |

**Returns**: JSON with enrichment results including GO term names, p-values, FDR, fold enrichment, and gene counts.

---

### STRING_functional_enrichment

Run functional enrichment using the STRING protein network database. Integrates GO, KEGG, Reactome, and other annotation sources through the STRING network context.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identifiers` | string | Yes | Newline- or comma-separated gene symbols or STRING IDs. |
| `species` | string | No | NCBI taxonomy ID (e.g., `"9606"` for human). Default: 9606. |
| `background_string_identifiers` | string | No | Custom background gene list. Default: full genome. |

**Returns**: JSON list of enrichment results with category, term, description, p-value, FDR, and matching gene count.

---

### ReactomeAnalysis_pathway_enrichment

Run pathway enrichment analysis against the Reactome curated pathway database.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene_list` | string | Yes | Newline-separated gene symbols. |
| `species` | string | No | Species name (e.g., `"Homo sapiens"`). Default: `"Homo sapiens"`. |
| `p_value` | float | No | P-value cutoff for reporting results. Default: 0.05. |

**Returns**: JSON with pathway names, entity counts, p-values, FDR, and a Reactome analysis token for accessing the full interactive report at reactome.org.

---

## Common Return Format Notes

All ToolUniverse tools return a top-level JSON object. Most tools follow this envelope:

```json
{
  "metadata": {
    "success": true,
    "tool_name": "...",
    "execution_time_s": 1.23
  },
  "data": { ... }
}
```

Check `metadata.success` before accessing `data`. If `success` is false, `data` may contain an `error` or `message` field explaining the failure.

For OmniPath tools specifically, the relevant results are always under `data.interactions`, `data.complexes`, or similar nested keys — not at the top level.
