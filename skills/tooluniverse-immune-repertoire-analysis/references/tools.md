# Immune Repertoire Analysis — Detailed Tool Parameters

Reference supplement to `SKILL.md`. Contains full parameter tables, response schemas, and usage notes for every tool called in this skill.

---

## IMGT Tools

### `IMGT_search_genes`

Search IMGT for immunoglobulin/TCR germline V, D, J gene entries.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `operation` | string | Yes | Must be `"search_genes"` |
| `query` | string | No | Gene name or partial name (e.g., `"TRBV12"`) |
| `gene_type` | string | No | `"TRBV"`, `"TRBJ"`, `"TRAV"`, `"TRAJ"`, `"IGHV"`, `"IGHD"`, `"IGHJ"`, `"IGKV"`, `"IGLV"`, etc. |
| `species` | string | No | Default `"Homo sapiens"`. Also accepts `"Mus musculus"` |

**Response**: Returns IMGT GENE-DB search URL and gene type metadata. Does NOT return sequences directly.

**Gotcha**: This tool returns navigation metadata, not raw sequences. Use `IMGT_get_sequence` with an IMGT/LIGM-DB accession to fetch actual nucleotide or amino acid sequence.

**Example call**:
```
tool_name: IMGT_search_genes
arguments: {"operation": "search_genes", "gene_type": "TRBV", "species": "Homo sapiens"}
```

---

### `IMGT_get_sequence`

Retrieve a germline IG/TCR sequence by IMGT/LIGM-DB accession.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `operation` | string | Yes | Must be `"get_sequence"` |
| `accession` | string | Yes | IMGT/LIGM-DB or EMBL/GenBank accession (e.g., `"X12432"`) |
| `format` | string | No | `"fasta"` (default) or `"embl"` |

**Response**: FASTA or EMBL-format sequence string.

**Use case**: Fetch the canonical germline sequence for TRBV12-3 to compute somatic hypermutation rate of BCR clonotypes, or to verify CDR3 anchor positions.

---

### `IMGT_get_gene_info`

Get information about IMGT databases, gene nomenclature, and tool descriptions.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `operation` | string | Yes | Must be `"get_gene_info"` |

**Response**: Descriptive text about IMGT resources (LIGM-DB, GENE-DB, V-QUEST). Good starting point for understanding IMGT's naming conventions.

---

## Epitope Database Tools

### `EBIProteins_get_epitopes`

Get experimentally-mapped immune epitope regions for a protein, sourced from IEDB via EBI Proteins API.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `accession` | string | Yes | UniProt accession (e.g., `"P04637"` for TP53, `"P0DTC2"` for SARS-CoV-2 Spike) |

**Response fields**:
- `accession`: UniProt accession
- `features` (list): each entry has `type="EPITOPE"`, `begin`, `end`, `description`, `evidences` (publications)

**Gotcha**: Requires UniProt accession, NOT a gene name or CDR3 sequence. Resolve antigen to UniProt first. Many proteins have zero entries — this is normal.

**Use case**: Call this with the UniProt accession of a target tumor antigen or viral protein to find which peptide regions are known T-cell or B-cell epitopes. Then compare those peptide positions to candidate binding CDR3s from your repertoire data.

---

### `BVBRC_search_epitopes`

Search pathogen T-cell and B-cell epitopes from IEDB via BV-BRC database. Covers bacteria and viruses.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `taxon_id` | string | No | NCBI Taxonomy ID. Examples: `"2697049"` (SARS-CoV-2), `"11320"` (Influenza A), `"1773"` (M. tuberculosis) |
| `protein_name` | string | No | Target protein keyword. Examples: `"Spike glycoprotein"`, `"Nucleocapsid protein"` |
| `epitope_type` | string | No | `"Linear peptide"` or `"Discontinuous peptide"`. Most epitopes are linear. |
| `organism` | string | No | Organism name keyword. Examples: `"coronavirus"`, `"influenza"` |
| `limit` | integer | No | Max results. Default 25, max 100 |

**Response**: List of epitope entries with `epitope_sequence`, `epitope_type`, `protein_name`, `taxon_id`, assay results.

**Gotcha**: This tool returns pathogen-side peptide sequences that T/B cells recognize — it does NOT accept CDR3 sequences or TCR/BCR sequences as input. Use it to obtain candidate antigen peptides, then cross-reference your expanded clonotypes with those epitopes via literature search.

**Example call**:
```
tool_name: BVBRC_search_epitopes
arguments: {"taxon_id": "2697049", "protein_name": "Spike glycoprotein", "epitope_type": "Linear peptide", "limit": 50}
```

---

### `proteins_api_get_epitopes`

Get B-cell and T-cell epitope information with antigenicity predictions from the UniProt Proteins API.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `accession` | string or array | Yes | UniProt accession(s). Single: `"P05067"`, comma-separated: `"P05067,P04637"`, or list |
| `format` | string | No | `"json"` (default) or `"xml"` |

**Response**: Immunology comments and epitope features extracted from the main protein endpoint. Not a direct IEDB lookup — returns UniProt's in-record annotations.

**Note**: Prefer `EBIProteins_get_epitopes` for IEDB-derived experimental epitope data. Use this tool when you need antigenicity predictions alongside sequence features.

---

## Literature Search Tools

### `PubMed_search_articles`

Search PubMed for biomedical literature using NCBI E-utilities.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | Search string. Supports MeSH terms, Boolean operators. Examples: `"CASSDRGGQPQHF epitope specificity"`, `"TCR repertoire cancer immunotherapy"` |
| `max_results` | integer | No | Default 10, max 100 |

**Response fields per article**: `pmid`, `title`, `authors`, `journal`, `pub_year`, `doi`, `article_type`, `url`

**Use case for repertoire analysis**: Search for CDR3 sequences (wrapped in quotes) combined with disease or epitope terms to find papers reporting known specificity for that sequence. Example: `'"CASSDRGGQPQHF" AND melanoma'`

---

### `EuropePMC_search_articles`

Search Europe PMC for full-text literature including abstracts and indexed body text.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | Supports fielded queries. `BODY:"term"` for full-text body search (requires `HAS_FT:Y`) |

**Response**: Article metadata including PMID, title, authors, abstract, journal, publication date.

**Advantage over PubMed**: Supports full-text body search for articles where Europe PMC has indexed the full text. Useful for finding CDR3 sequences or VDJ combinations mentioned in methods sections.

---

### `LiteratureSearchTool`

Multi-database literature search (EuropePMC, OpenAlex, PubTator) with AI-powered summary.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `research_topic` | string | Yes | Research topic or query. Can be a full natural language question. |

**Response**: Synthesized summary of findings across databases.

**Use case**: Call with a topic like `"TRBV9 bias in multiple sclerosis T cell repertoire"` to get a synthesized overview of existing literature.

---

### `MultiAgentLiteratureSearch`

Multi-agent system that extracts keywords, runs parallel searches, and iterates for quality.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | Research query |
| `max_iterations` | integer | Yes | Default 3 |
| `quality_threshold` | float | Yes | Default 0.7 (range 0–1) |

**Use case**: Use when `LiteratureSearchTool` returns insufficient results and deeper cross-database mining is warranted.

---

## Single-Cell Tools

### `CELLxGENE_get_cell_metadata`

Query cell metadata from CELLxGENE Census (50M+ human/mouse cells).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `operation` | string | Yes | Must be `"get_obs_metadata"` |
| `obs_value_filter` | string | Yes | SQL-like filter. REQUIRED — unfiltered queries will time out. |
| `organism` | string | No | `"Homo sapiens"` (default) or `"Mus musculus"` |
| `column_names` | array | No | Columns to return. Default: all columns. |
| `census_version` | string | No | `"stable"` (default, LTS) or `"latest"` |

**Filter examples for immune repertoire analysis**:
- T cells in blood: `'cell_type == "T cell" and tissue_general == "blood"'`
- B cells normal vs disease: `'cell_type == "B cell" and disease in ["normal", "COVID-19"]'`
- Combined T and B: `'cell_type in ["T cell", "B cell"] and tissue_general == "lymph node"'`

**Gotcha**: `obs_value_filter` is mandatory. Always supply a meaningful filter or the query will time out on 50M+ cells.

---

## Supporting Tools (for Antigen Resolution)

### `UniProt_search`

Search UniProt for proteins by gene name, accession, or keyword. Use to resolve an antigen gene name to a UniProt accession before calling epitope tools.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | E.g., `"gene:TP53"`, `"SARS-CoV-2 spike"` |
| `organism` | string | No | E.g., `"human"` |
| `limit` | integer | No | Max results |

**Response fields**: `accession`, `id`, `protein_name`, `gene_names`, `organism`, `length`

**Use pattern**: Call `UniProt_search` to get the accession for a target antigen, then pass that accession to `EBIProteins_get_epitopes`.

---

## Tool Call Pattern for Epitope Specificity (Phase 7)

This sequence covers the full Phase 7 workflow in order:

1. **Identify candidate antigen** (based on experimental context or literature).
2. Call `UniProt_search` with `query="gene:ANTIGEN_GENE"` to obtain UniProt accession.
3. Call `EBIProteins_get_epitopes` with the accession to retrieve IEDB-mapped epitope regions.
4. For pathogen contexts, call `BVBRC_search_epitopes` with appropriate `taxon_id` to get known pathogen epitopes.
5. For top expanded/convergent/public CDR3 sequences, call `PubMed_search_articles` with the CDR3 sequence quoted.
6. Call `EuropePMC_search_articles` with `BODY:"CDR3_SEQUENCE"` for full-text hits.
7. Optionally call `LiteratureSearchTool` for a synthesized summary.

---

## Response Envelope Pattern

Most ToolUniverse tools wrap responses in a standard envelope:

```json
{
  "status": "success",
  "data": { ... }
}
```

On error:

```json
{
  "status": "error",
  "message": "..."
}
```

Always check `result["status"]` before accessing `result["data"]`. An HTTP error from an upstream API may return `status="error"` with an explanatory message rather than raising an exception.
