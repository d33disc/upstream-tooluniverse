# Spatial Transcriptomics - Tool Reference

Full parameter reference for ToolUniverse tools used in the spatial transcriptomics workflow.
All tools are called via `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.
For workflow steps and decision logic, see `../SKILL.md`. For API quirks, see the "Known Gotchas" section in `../SKILL.md`.

---

## Phase 7: Spatial Cell Communication (OmniPath)

### OmniPath_get_ligand_receptor_interactions

Fetch curated ligand-receptor interaction pairs from OmniPath (CellPhoneDB, CellChatDB, CellTalkDB, connectomeDB, and 20+ other resources).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `partners` | str | no | Gene symbol(s) queried as either source or target. Comma-separated. e.g. `"TGFB1"`, `"CD274,PDCD1"` |
| `sources` | str | no | Gene symbol(s) for ligand side only. Use instead of `partners` to get outgoing interactions |
| `targets` | str | no | Gene symbol(s) for receptor side only. Use instead of `partners` to get incoming interactions |
| `databases` | str | no | Filter by source database(s), comma-separated. e.g. `"CellPhoneDB,CellChatDB"`. Default: all |
| `organisms` | int | no | NCBI taxonomy ID. Default: `9606` (human). Use `10090` for mouse |
| `limit` | int | no | Max interactions to return. Default: no limit (can be thousands) |

Returns: List of interaction records with fields `source`, `target`, `source_genesymbol`, `target_genesymbol`, `is_stimulation`, `is_inhibition`, `n_resources`, `n_references`, `databases`.

**Important**: Calling with no parameters returns all pairs (thousands). Always filter using `partners=`, `sources=`, or `targets=`.

**Example — query PD-L1/PD-1 checkpoint**:
```
tool_name: OmniPath_get_ligand_receptor_interactions
arguments: {"partners": "CD274,PDCD1"}
```

**Example — get all interactions where TGFB1 is ligand**:
```
tool_name: OmniPath_get_ligand_receptor_interactions
arguments: {"sources": "TGFB1"}
```

---

### OmniPath_get_cell_communication_annotations

Get cell-cell communication functional annotations for proteins from databases like CellPhoneDB, CellChatDB, CellTalkDB.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `proteins` | str | yes | UniProt accession(s) or gene symbol(s), comma-separated. e.g. `"TGFB1,TGFBR2"` |
| `databases` | str | no | Filter by annotation database(s). Options: `CellPhoneDB`, `CellChatDB`, `CellTalkDB`, `ICELLNET`, `iTALK`, `scConnect`, `Cellinker`, `connectomeDB2020`, `Ramilowski2015`. Default: `"CellPhoneDB,CellChatDB"` |
| `genesymbols` | bool | no | Include gene symbols in output. Default: `true` |

Returns: Annotation records with `source` (gene), `label` (ligand/receptor), `pathway`, `category` (e.g., "Secreted Signaling", "Cell-Cell Contact", "ECM-Receptor"), `database`.

**Example — annotate TGFB1 pathway context**:
```
tool_name: OmniPath_get_cell_communication_annotations
arguments: {"proteins": "TGFB1,TGFBR2", "databases": "CellChatDB"}
```

---

### OmniPath_get_intercell_roles

Classify proteins as ligands, receptors, transmembrane proteins, secreted factors, or ECM components.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `proteins` | str | no | Gene symbol(s) or UniProt ID(s), comma-separated |
| `categories` | str | no | Filter by role: `"ligand"`, `"receptor"`, `"adhesion"`, `"transporter"`, `"ecm"`, `"transmembrane"`. Comma-separated |
| `transmitter` | bool | no | Filter for sender/transmitter proteins |
| `receiver` | bool | no | Filter for receiver proteins |
| `secreted` | bool | no | Filter for secreted proteins |
| `limit` | int | no | Max results |

Returns: Records with `category`, `scope` (generic/specific), `consensus_score`, `n_sources`, `transmitter`, `receiver`, `secreted`.

**Example — confirm EGFR is a receptor**:
```
tool_name: OmniPath_get_intercell_roles
arguments: {"proteins": "EGFR", "categories": "receptor"}
```

---

### OmniPath_get_complexes

Get protein complex compositions (relevant for heteromeric L-R complexes, e.g., integrin pairs, cytokine receptor heterodimers).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `proteins` | str | yes | UniProt accession(s), comma-separated. **Gene symbols are NOT supported** — must use UniProt IDs |
| `databases` | str | no | Filter by source: `CORUM`, `CellPhoneDB`, `CellChatDB`, `ComplexPortal`, `SIGNOR`, `KEGG-MEDICUS`. Default: all |

Returns: Complex records with `name`, `components_genesymbols` (pipe-separated), `databases`.

**Note**: This tool requires UniProt IDs, not gene symbols. Convert gene symbols to UniProt IDs first using another tool (e.g., `UniProt_search`).

---

## Phase 3: Domain Marker Validation (Expression Databases)

### GTEx_get_top_expressed_genes

Get top expressed genes in a tissue, useful for validating that spatial domain markers are tissue-appropriate.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `operation` | str | yes | Must be `"get_top_expressed_genes"` |
| `tissue_site_detail_id` | str | yes | Tissue ID, e.g. `"Brain_Cortex"`, `"Breast_Mammary_Tissue"`, `"Liver"`. Use `GTEx_get_tissue_sites` to find valid IDs |
| `filter_mt_genes` | bool | no | Exclude mitochondrial genes. Default: `true` |
| `dataset_id` | str | no | GTEx version: `"gtex_v8"`, `"gtex_v10"` (default), `"gtex_snrnaseq_pilot"` |
| `items_per_page` | int | no | Results per page, max 100,000. Default: 250 |

Returns: Gene list with `geneSymbol`, `median` (TPM), `unit`.

**Example — validate breast tumor markers**:
```
tool_name: GTEx_get_top_expressed_genes
arguments: {"operation": "get_top_expressed_genes", "tissue_site_detail_id": "Breast_Mammary_Tissue"}
```

---

### HPA_get_rna_expression_in_specific_tissues

Query Human Protein Atlas RNA expression for specific tissues to validate spatial domain marker genes.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `ensembl_id` | str | yes | Ensembl Gene ID, e.g. `"ENSG00000141510"` for TP53 |
| `tissue_names` | list | yes | List of tissue names, e.g. `["breast", "liver", "brain"]`. Case-insensitive |

Returns: Expression values (nTPM) per tissue with tissue name and cell type breakdown.

---

## Phase 3 & 8: Pathway Enrichment for Domain Markers

### enrichr_gene_enrichment_analysis

Perform gene enrichment analysis for spatial domain marker gene lists.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_list` | list | yes | Gene symbols. Minimum 2 genes. e.g. `["MKI67", "TOP2A", "CCNB1"]` |
| `libs` | list | yes | Enrichment libraries. e.g. `["KEGG_2021_Human", "GO_Biological_Process_2023", "MSigDB_Hallmark_2020"]` |

Returns: Enrichment results per library with `term`, `pval`, `adj_pval`, `genes`.

**Important**: `data` field in the response is a JSON string — parse it before reading enrichment results. `libs` must be an array, not a plain string.

**Example — enrich tumor core markers**:
```
tool_name: enrichr_gene_enrichment_analysis
arguments: {
  "gene_list": ["EPCAM", "KRT19", "MKI67", "CCNB1", "TOP2A"],
  "libs": ["MSigDB_Hallmark_2020", "KEGG_2021_Human", "GO_Biological_Process_2023"]
}
```

---

## Response Format Summary

All ToolUniverse tools return a consistent envelope:

```
{
  "status": "success" | "error",
  "data": <tool-specific payload>,
  "url": <optional: source API URL>
}
```

Always check `result["status"]` before reading `result["data"]`. On error, `result["data"]` contains an error message string.

---

## Key Thresholds and Interpretation

### Moran's I (spatial autocorrelation)

| I value | Interpretation |
|---------|----------------|
| > 0.6 | Strong spatial clustering |
| 0.3–0.6 | Moderate spatial pattern |
| 0.1–0.3 | Weak spatial structure |
| < 0.1 | Effectively random |

Use FDR < 0.05 (Benjamini-Hochberg) for significance filtering.

### Cell type deconvolution confidence

| Method | Notes |
|--------|-------|
| Cell2location | Best for Visium with heterogeneous tissue; requires scRNA-seq reference |
| Tangram | Good for small gene panels (MERFISH/seqFISH); uses gene expression directly |
| SPOTlight | Faster, lower memory; suitable for exploratory analysis |

### OmniPath curation effort scores

Higher `n_references` and `n_resources` indicate better-supported interactions:

| n_references | Confidence |
|-------------|------------|
| > 50 | High confidence (well-studied interaction) |
| 10–50 | Moderate confidence |
| < 10 | Low confidence (use with caution) |
