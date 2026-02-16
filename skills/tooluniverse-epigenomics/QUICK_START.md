# Epigenomics & Gene Regulation - Quick Start

## Overview

This skill provides comprehensive regulatory landscape analysis using 21 tools across 7 databases (SCREEN, JASPAR, ReMap, RegulomeDB, ENCODE, 4D Nucleome, Ensembl). It generates structured reports covering cis-regulatory elements, transcription factor binding, regulatory variants, chromatin conformation, and integrated regulatory models.

---

## Quick Start Examples

### Example 1: Gene Regulatory Landscape

**Query**: "What regulates the TP53 gene? Show me its regulatory landscape."

**What happens**:
1. Resolves TP53 to Ensembl ID, coordinates (chr17:7661779-7687550)
2. Queries SCREEN for enhancers, promoters, and insulators near TP53
3. Searches JASPAR for TP53 binding motif (it is a TF) and TFs binding its promoter
4. Gets ReMap validated TF binding sites at the TP53 locus
5. Finds ENCODE ChIP-seq, ATAC-seq, histone mark experiments
6. Searches 4DN for Hi-C chromatin conformation data
7. Gets Ensembl regulatory build annotations
8. Synthesizes integrated regulatory model

**Output**: `TP53_regulatory_report.md` with full regulatory element catalog and TF network

---

### Example 2: Non-Coding Variant Interpretation

**Query**: "What is the regulatory impact of rs6983267?"

**What happens**:
1. Queries RegulomeDB for variant regulatory score
2. Identifies nearby genes and regulatory elements (SCREEN)
3. Checks TF binding sites at variant position (ReMap)
4. Maps to ENCODE functional data (histone marks, accessibility)
5. Assesses likely regulatory function with evidence grading

---

### Example 3: Transcription Factor Analysis

**Query**: "Find CTCF binding sites and target regulatory elements"

**What happens**:
1. Searches JASPAR for CTCF binding motif (MA0139.1)
2. Queries ReMap for CTCF ChIP-seq binding sites
3. Finds ENCODE CTCF ChIP-seq experiments across cell types
4. Maps CTCF binding to SCREEN insulator elements
5. Generates TF binding profile report

---

### Example 4: Cell-Type Specific Regulation

**Query**: "Show the epigenetic regulation of MYC in HepG2 cells"

**What happens**:
1. Resolves MYC gene coordinates
2. Queries SCREEN for enhancers/promoters active in HepG2
3. Gets ReMap TF binding specifically in HepG2
4. Searches ENCODE for HepG2-specific ChIP-seq, ATAC-seq
5. Generates cell-type focused regulatory report

---

## Python SDK Usage

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

# Phase 1: SCREEN cis-regulatory elements
enhancers = tu.tools.SCREEN_get_regulatory_elements(
    gene_name="TP53", element_type="enhancer", limit=20
)
promoters = tu.tools.SCREEN_get_regulatory_elements(
    gene_name="TP53", element_type="promoter", limit=10
)

# Phase 2: TF binding
jaspar_motifs = tu.tools.jaspar_search_matrices(
    search="TP53", collection="CORE", species="9606"
)
remap_binding = tu.tools.ReMap_get_transcription_factor_binding(
    gene_name="TP53", cell_type="HepG2", limit=20
)

# Phase 3: Regulatory variant
regulome = tu.tools.RegulomeDB_query_variant(rsid="rs6983267")

# Phase 4: ENCODE experiments
encode_chipseq = tu.tools.ENCODE_search_experiments(
    assay_title="ChIP-seq", target="H3K27ac",
    organism="Homo sapiens", limit=5
)
encode_atacseq = tu.tools.ENCODE_search_experiments(
    assay_title="ATAC-seq", organism="Homo sapiens", limit=5
)

# Phase 5: 4DN chromatin data
hic_data = tu.tools.FourDN_search_data(
    operation="search_data", assay_title="Hi-C", limit=10
)

# Phase 6: Ensembl regulatory features
ensembl_reg = tu.tools.ensembl_get_regulatory_features(
    region="17:7661779-7687550", feature="regulatory", species="human"
)
```

---

## MCP Integration

When used via MCP (Claude Desktop, Cursor, etc.), simply ask:

- "What are the regulatory elements near BRCA1?"
- "Find transcription factors that bind the MYC promoter"
- "Is rs6983267 in a regulatory region?"
- "Show me ENCODE ChIP-seq data for H3K27ac in liver"
- "What is the chromatin structure around the HoxD cluster?"
- "Analyze the epigenetic regulation of EGFR"

The skill will automatically invoke the appropriate tools and generate a structured report.

---

## Key Tool Reference

| Tool | Input | What It Returns |
|------|-------|-----------------|
| `SCREEN_get_regulatory_elements` | Gene name + element type | cCREs (enhancers, promoters, insulators) |
| `jaspar_search_matrices` | TF name or search term | TF binding motifs (PWMs) |
| `ReMap_get_transcription_factor_binding` | Gene + cell type | Validated TF binding sites |
| `RegulomeDB_query_variant` | rsID | Regulatory evidence score (1a-7) |
| `ENCODE_search_experiments` | Assay + target + organism | Functional genomics experiments |
| `FourDN_search_data` | Assay title + cell type | Chromatin conformation data |
| `ensembl_get_regulatory_features` | Genomic region | Regulatory build annotations |

---

## Evidence Tiers

| Tier | Meaning | Source Examples |
|------|---------|----------------|
| [T1] | Functionally validated | CRISPR deletion, reporter assay |
| [T2] | Experimental data | ENCODE ChIP-seq, SCREEN cCRE, ReMap binding |
| [T3] | Computational prediction | JASPAR motif, RegulomeDB score, Ensembl build |
| [T4] | Association/annotation | Literature mention, low-confidence prediction |
