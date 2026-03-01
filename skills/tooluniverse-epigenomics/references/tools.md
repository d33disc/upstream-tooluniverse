# ToolUniverse Epigenomics Tool Reference

Full parameter reference for ToolUniverse annotation tools used in the epigenomics skill.
All tools are called via `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

---

## Regulatory Annotation Tools

### ensembl_lookup_gene
Look up a gene by symbol or Ensembl ID.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `id` | str | yes | Gene symbol or Ensembl ID (e.g. "BRCA1", "ENSG00000012048") |
| `species` | str | yes | **Must be `"homo_sapiens"`** (or other Ensembl species name) |

Returns: `{status, data: {id, display_name, seq_region_name, start, end, strand, biotype}, url}`

---

### ensembl_get_regulatory_features
Get regulatory features overlapping a genomic region.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `region` | str | yes | Format: `"17:7571720-7590868"` — **NO "chr" prefix** |
| `feature` | str | yes | e.g. `"regulatory"`, `"motif"`, `"enhancer"` |
| `species` | str | yes | e.g. `"homo_sapiens"` |

Returns: `{status, data: [...features...]}`

---

### ensembl_get_overlap_features
Get genomic features (genes, transcripts) overlapping a region.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `region` | str | yes | Same format as above — no "chr" prefix |
| `feature` | str | yes | e.g. `"gene"`, `"transcript"` |
| `species` | str | yes | e.g. `"homo_sapiens"` |

---

### SCREEN_get_regulatory_elements
Query ENCODE SCREEN for candidate cis-Regulatory Elements (cCREs).

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_name` | str | yes | Gene symbol |
| `element_type` | str | no | `"enhancer"`, `"promoter"`, `"insulator"` |
| `limit` | int | no | Max results (default 10) |

Returns: JSON-LD format with `@context` and `@graph` keys. Extract results from `@graph`.

---

### ReMap_get_transcription_factor_binding
Get TF binding sites near a gene from ReMap.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_name` | str | yes | Gene symbol |
| `cell_type` | str | no | Cell type filter |
| `limit` | int | no | Max results |

---

### RegulomeDB_query_variant
Query RegulomeDB for regulatory evidence at a variant.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `rsid` | str | yes | dbSNP rsID (e.g. `"rs12345"`) |

Returns: `{status, data, url}` with regulatory score (1a = strongest evidence).

---

### jaspar_search_matrices
Search JASPAR for transcription factor binding motifs.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `search` | str | yes | TF name or motif name |
| `collection` | str | no | e.g. `"CORE"` |
| `species` | str | no | e.g. `"9606"` (human) |

Returns: `{count, results: [...matrices...]}`

---

### ENCODE_search_experiments
Search ENCODE for experimental datasets.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `assay_title` | str | no | e.g. `"ChIP-seq"`, `"ATAC-seq"` |
| `target` | str | no | e.g. `"H3K27ac"`, `"CTCF"` |
| `organism` | str | no | e.g. `"Homo sapiens"` |
| `limit` | int | no | Max results |

---

### ChIPAtlas_get_experiments
List ChIP-seq experiments in ChIPAtlas.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `operation` | str | yes | **Must be `"get_experiment_list"`** |
| `genome` | str | no | e.g. `"hg38"`, `"mm10"` |
| `antigen` | str | no | e.g. `"H3K27ac"`, `"CTCF"` |
| `cell_type` | str | no | Cell type filter |
| `limit` | int | no | Max results |

---

### ChIPAtlas_search_datasets
Search ChIPAtlas datasets.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `operation` | str | yes | Required SOAP-style parameter |
| `antigenList` | list | no | List of antigens to search |
| `celltypeList` | list | no | List of cell types |

---

### ChIPAtlas_enrichment_analysis
Run enrichment analysis against ChIPAtlas data.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `operation` | str | yes | Required SOAP-style parameter |
| Input params | varied | yes | BED regions, motifs, or gene lists depending on operation |

---

### ChIPAtlas_get_peak_data
Retrieve ChIP-seq peak data and download URLs.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `operation` | str | yes | Required SOAP-style parameter |

---

### FourDN_search_data
Search 4D Nucleome for chromatin conformation data.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `operation` | str | yes | **Must be `"search_data"`** |
| `assay_title` | str | no | e.g. `"Hi-C"`, `"ChIA-PET"` |
| `limit` | int | no | Max results |

---

## Gene Annotation Tools

### MyGene_query_genes
Query MyGene.info for gene information.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | str | yes | Gene symbol, ID, or keyword |

Returns: `{hits: [{_id, symbol, ensembl, entrezgene, ...}]}`

---

### MyGene_batch_query
Batch query multiple genes.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_ids` | list[str] | yes | List of gene symbols or IDs |
| `fields` | str | no | Comma-separated fields (e.g. `"symbol,ensembl,go"`) |

Returns: `{results: [{query, symbol, ...}]}`

---

### HGNC_get_gene_info
Get HGNC-approved gene information.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `symbol` | str | yes | HGNC-approved gene symbol |

Returns gene symbol, aliases, cross-references.

---

### GO_get_annotations_for_gene
Get Gene Ontology annotations for a gene.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_id` | str | yes | Gene symbol or UniProt ID |

---

## Data Format Reference

| Format | Description | Key fields |
|--------|-------------|------------|
| Methylation beta matrix | Probes (rows) x samples (columns), values 0–1 | Index = cg/ch probe IDs |
| M-value matrix | Log2-ratio version of beta; unbounded | Convert: M = log2(beta/(1-beta)) |
| Illumina manifest | Probe annotation file (450K or EPIC) | IlmnID/Name, CHR, MAPINFO, Strand, UCSC_RefGene_Name |
| BED | Tab-sep, 0-based half-open coords | chrom, start, end [, name, score, strand] |
| narrowPeak | BED + signalValue, pValue, qValue, peak | 10-column format from MACS2 |
| broadPeak | BED + signalValue, pValue, qValue | 9-column format |
| BigWig | Binary continuous signal track | Requires pyBigWig to read |
| Clinical data | Patient/sample rows, variable columns | ID column varies by source |

## Chromosome Length Tables

For density calculations (CpGs per base pair), use these reference chromosome lengths:

**hg38 (GRCh38):**
chr1=248956422, chr2=242193529, chr3=198295559, chr4=190214555, chr5=181538259,
chr6=170805979, chr7=159345973, chr8=145138636, chr9=138394717, chr10=133797422,
chr11=135086622, chr12=133275309, chr13=114364328, chr14=107043718, chr15=101991189,
chr16=90338345, chr17=83257441, chr18=80373285, chr19=58617616, chr20=64444167,
chr21=46709983, chr22=50818468, chrX=156040895, chrY=57227415

**hg19 (GRCh37):**
chr1=249250621, chr2=243199373, chr3=198022430, chr4=191154276, chr5=180915260,
chr6=171115067, chr7=159138663, chr8=146364022, chr9=141213431, chr10=135534747,
chr11=135006516, chr12=133851895, chr13=115169878, chr14=107349540, chr15=102531392,
chr16=90354753, chr17=81195210, chr18=78077248, chr19=59128983, chr20=63025520,
chr21=48129895, chr22=51304566, chrX=155270560, chrY=59373566

**mm10 (GRCm38):**
chr1=195471971, chr2=182113224, chr3=160039680, chr4=156508116, chr5=151834684,
chr6=149736546, chr7=145441459, chr8=129401213, chr9=124595110, chr10=130694993,
chr11=122082543, chr12=120129022, chr13=120421639, chr14=124902244, chr15=104043685,
chr16=98207768, chr17=94987271, chr18=90702639, chr19=61431566, chrX=171031299, chrY=91744698
