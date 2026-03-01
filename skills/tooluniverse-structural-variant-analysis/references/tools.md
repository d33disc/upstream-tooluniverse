# Tool Parameter Reference — Structural Variant Analysis

Detailed call signatures for all tools used in the SV analysis workflow. All calls use `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

---

## ClinGen_search_dosage_sensitivity

Query the ClinGen Dosage Sensitivity Map for haploinsufficiency (HI) and triplosensitivity (TS) scores.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene` | string | Yes | HGNC gene symbol (e.g., `"KANSL1"`) |

**Response fields of interest**:
- `Haploinsufficiency Score` — 0, 1, 2, or 3
- `Triplosensitivity Score` — 0, 1, 2, or 3
- `Haploinsufficiency Description` — narrative
- `Triplosensitivity Description` — narrative

**Score meanings**:
| Score | Meaning |
|-------|---------|
| 3 | Sufficient evidence for dosage sensitivity |
| 2 | Emerging evidence |
| 1 | Little evidence (do NOT treat as supporting pathogenicity) |
| 0 | No evidence |

---

## ClinGen_search_gene_validity

Query ClinGen gene-disease validity classifications.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene` | string | Yes | HGNC gene symbol |

**Response fields**:
- `Classification` — Definitive / Strong / Moderate / Limited / Disputed / Refuted
- `Disease` — disease name
- `MOI` — mode of inheritance

---

## ClinVar_search_variants

Search ClinVar for known pathogenic or benign structural variants overlapping a region.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chromosome` | string | Yes | Chromosome number as string (e.g., `"17"`) |
| `start` | integer | Yes | Start coordinate (1-based) |
| `stop` | integer | Yes | End coordinate |
| `variant_type` | string | No | `"DEL"`, `"DUP"`, `"INV"`, `"TRA"` |

**Response fields**:
- `clinical_significance` — Pathogenic / Likely pathogenic / Benign / VUS / etc.
- `review_status` — expert panel, criteria provided, etc.
- `chromosome`, `start`, `stop` — coordinates for overlap calculation
- `accession` — VCV or RCV ID

**Note**: Always compute reciprocal overlap (≥70% threshold) before applying PS1 or BA1/BS1 codes.

---

## DECIPHER_search

Search the DECIPHER database for patient-reported SVs and phenotypes.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Gene symbol, region (e.g., `"chr17:44039927-44352659"`), or phenotype term |
| `search_type` | string | No | `"gene"`, `"region"`, or `"phenotype"` |

**Response fields**:
- Case ID, SV type, coordinates, size
- HPO phenotype terms
- Inheritance

**Note**: DECIPHER may return empty results if API access is restricted. If so, note the limitation — do not assert absence of patient cases.

---

## Ensembl_lookup_gene

Retrieve gene coordinates, exon structure, and transcript information.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene_id` | string | Yes | Ensembl gene ID (e.g., `"ENSG00000182170"`) or HGNC symbol |
| `species` | string | No | Default `"human"` |
| `expand` | boolean | No | `true` to include exon/transcript details |

**Response fields**:
- `start`, `end`, `seq_region_name` — genomic coordinates
- `strand` — orientation (+1 or −1)
- `Transcript` — list with exon coordinates when `expand=true`

---

## OMIM_search

Search OMIM for gene or phenotype entries.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `operation` | string | Yes | `"search"` |
| `query` | string | Yes | Gene symbol or disease name |
| `limit` | integer | No | Max results (default 10) |

**Response**: List of entries with `mimNumber`, `title`, `entryType` (gene vs. phenotype).

---

## OMIM_get_entry

Fetch detailed OMIM entry including inheritance, clinical synopsis, and allelic variants.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `operation` | string | Yes | `"get_entry"` |
| `mim_number` | string | Yes | MIM number as string (e.g., `"605543"`) |

**Response fields**:
- `inheritancePattern` — AD, AR, XL, etc.
- `clinicalSynopsis` — phenotype features
- `allelicVariants` — known pathogenic variants

**Tip**: OMIM has separate entries for genes (e.g., KANSL1 = 612452) and phenotypes (e.g., Koolen-De Vries = 610443). Look up both. Gene entries reliably encode inheritance mode.

---

## DisGeNET_search_gene

Retrieve gene-disease associations from DisGeNET with evidence scores.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `operation` | string | Yes | `"search_gene"` |
| `gene` | string | Yes | HGNC gene symbol |
| `limit` | integer | No | Max results (default 20) |

**Response fields**:
- `diseaseName`, `diseaseId`
- `score` — DisGeNET evidence score (0–1)
- `EL` — evidence level

---

## gnomad_search

Query gnomAD for allele frequencies and constraint metrics (pLI, LOEUF).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene` | string | Yes/No | HGNC gene symbol (for constraint scores) |
| `variant_id` | string | Yes/No | Variant ID for small variant frequency |

**For SV analysis, use this tool primarily for gene constraint scores**:
- `pLI` — probability of LoF intolerance (gnomAD v2; ≥0.9 = HI candidate)
- `LOEUF` — LoF observed/expected upper bound (gnomAD v4; <0.35 = HI candidate)

**Note**: gnomAD SV frequencies (for large structural variants) are NOT queryable via this tool. Use the gnomAD browser directly and note the limitation in your report.

---

## PubMed_search

Search PubMed for peer-reviewed literature.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | PubMed search query with boolean operators |
| `max_results` | integer | No | Max papers to return (default 20) |

**Recommended query patterns for SV analysis**:
- Dosage sensitivity: `"GENE" AND (haploinsufficiency OR "dosage sensitivity" OR "deletion syndrome")`
- Case reports: `"GENE" AND deletion AND "phenotype term"`
- SV-specific: `deletion AND "GENE1" AND "GENE2" AND syndrome`

---

## EuropePMC_search

Search Europe PubMed Central for additional literature coverage.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `limit` | integer | No | Max results |

Use as a complement to `PubMed_search` for European literature and preprints.

---

## NCBI_gene_search

Search NCBI Gene for official gene symbol, aliases, and description.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `term` | string | Yes | Gene symbol or alias |
| `organism` | string | No | Default `"human"` |

**Response fields**: official symbol, full name, aliases, gene ID, chromosome location.

---

## Gene_Ontology_get_term_info

Retrieve GO term information for a gene.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `term_id` | string | Yes | GO term ID (e.g., `"GO:0003674"`) or gene symbol |

**Use**: Supplement OMIM/DisGeNET with pathway/function context. Lower priority than dosage sensitivity data for SV classification.

---

## API Quirks and Known Issues

| Tool | Quirk |
|------|-------|
| `gnomad_search` | Does NOT provide SV frequencies; only gene-level constraint metrics |
| `DECIPHER_search` | May return empty if public API access is restricted; never assert "absent" |
| `ClinVar_search_variants` | Coordinate search returns all overlapping variants; always filter by SV type and apply reciprocal overlap cutoff manually |
| `OMIM_get_entry` | `mim_number` must be a string, not integer |
| `ClinGen_search_dosage_sensitivity` | Score 1 = "little evidence" — do NOT use as supportive of pathogenicity |
| `gnomad_search` pLI | gnomAD v4 reports LOEUF instead of pLI; if pLI is unavailable, use LOEUF <0.35 as the equivalent threshold |
