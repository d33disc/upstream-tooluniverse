---
name: tooluniverse-immune-repertoire-analysis
description: Comprehensive immune repertoire analysis for T-cell and B-cell receptor sequencing data. Analyze TCR/BCR repertoires to assess clonality, diversity, V(D)J gene usage, CDR3 characteristics, convergence, and predict epitope specificity. Integrate with single-cell data for clonotype-phenotype associations. Use for adaptive immune response profiling, cancer immunotherapy research, vaccine response assessment, autoimmune disease studies, or repertoire diversity analysis in immunology research.
---

# ToolUniverse Immune Repertoire Analysis

Comprehensive skill for analyzing T-cell receptor (TCR) and B-cell receptor (BCR) repertoire sequencing data to characterize adaptive immune responses, clonal expansion, and antigen specificity. Agents call tools via `mcp__tooluniverse__execute_tool`.

## Overview

Adaptive immune receptor repertoire sequencing (AIRR-seq) profiles T-cell and B-cell populations through high-throughput sequencing of TCR/BCR variable regions. This skill provides an 8-phase workflow:

- Phase 1: Data import and clonotype definition
- Phase 2: Diversity and clonality assessment
- Phase 3: V(D)J gene usage analysis
- Phase 4: CDR3 sequence characterization
- Phase 5: Clonal expansion detection
- Phase 6: Convergence and public clonotype detection
- Phase 7: Epitope specificity prediction
- Phase 8: Integration with single-cell phenotyping

---

## Known Gotchas

1. **V/J gene name formats differ by tool and aligner.** MiXCR produces `TRBV12-3*01`, 10x produces `TRBV12-3`, AIRR standard uses `TRBV12-3*01`. Normalize before merging or comparing. Extract gene family with a regex like `TRBV\d+` when aligner-specific allele suffixes are present.

2. **CDR3 definition varies.** MiXCR `aaSeqCDR3` includes anchor residues C and F/W; AIRR `junction_aa` also includes anchors; some tools report the CDR3 loop only (without anchors). Check your source format before computing length distributions.

3. **Clonotype definition is not standardized.** CDR3aa alone, CDR3nt alone, and V+J+CDR3aa give different clonotype counts for the same dataset. Report which definition you used.

4. **IMGT_search_genes does not return sequences directly.** It returns a search URL to GENE-DB. Use `IMGT_get_sequence` with an IMGT/LIGM-DB accession to fetch actual germline sequences.

5. **EBIProteins_get_epitopes requires a UniProt accession, not a gene name.** Resolve antigen proteins to a UniProt accession first (e.g., via `UniProt_search`) before querying epitopes.

6. **BVBRC_search_epitopes covers pathogen epitopes from IEDB, not TCR/BCR sequences.** Use it to find known pathogen epitopes that expanded clonotypes might recognize; it does not accept CDR3 sequences as input.

7. **Rarefaction comparisons require equal depth.** If comparing diversity across samples, downsample all to the same read depth before computing Shannon entropy or Simpson index, or use rarefied richness curves.

8. **10x VDJ barcodes must match GEX barcodes exactly.** Even a suffix mismatch (e.g., `-1` appended in GEX but not VDJ) will silently cause zero clonotype-to-cell linkage. Check barcode formats before merging.

9. **Public clonotype frequency depends heavily on cohort size.** A clonotype present in 2 of 5 samples looks different from 2 of 500. Always report the denominator alongside the share count.

10. **Convergence is underestimated if only CDR3aa is stored.** You need both `cdr3aa` and `cdr3nt` columns. Verify your input data retains nucleotide-level resolution.

---

## Tool Reference (Abbreviated)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `IMGT_search_genes` | Find V/J/D germline gene entries | `operation="search_genes"`, `gene_type` (TRBV, TRAV, IGHV…), `species` |
| `IMGT_get_sequence` | Fetch germline sequence by accession | `operation="get_sequence"`, `accession`, `format` |
| `EBIProteins_get_epitopes` | Known IEDB epitopes for an antigen protein | `accession` (UniProt) |
| `BVBRC_search_epitopes` | Pathogen T/B-cell epitopes from IEDB | `taxon_id`, `protein_name`, `epitope_type`, `limit` |
| `PubMed_search_articles` | Literature on CDR3 specificity / TCR studies | `query`, `max_results` |
| `EuropePMC_search_articles` | Full-text literature search | `query` |
| `CELLxGENE_get_cell_metadata` | Single-cell T/B cell populations | `operation="get_obs_metadata"`, `obs_value_filter` |
| `LiteratureSearchTool` | Multi-database summary search | `research_topic` |

For full parameter tables and response schemas see `references/tools.md`.

---

## Phase 1: Data Import and Clonotype Definition

**Goal**: Load AIRR-seq data from any common format and assign each unique receptor sequence a clonotype identity.

### Supported Input Formats

| Format | Source | Key fields needed |
|--------|--------|-------------------|
| MiXCR `.txt` | MiXCR aligner | `cloneCount`, `cloneFraction`, `aaSeqCDR3`, `nSeqCDR3`, `allVHitsWithScore`, `allJHitsWithScore` |
| AIRR TSV | AIRR Community Standard | `clone_id`, `duplicate_count`, `junction_aa`, `junction`, `v_call`, `j_call`, `locus` |
| 10x `filtered_contig_annotations.csv` | 10x Genomics VDJ | `barcode`, `cdr3`, `cdr3_nt`, `v_gene`, `j_gene`, `chain`, `umis` |
| ImmunoSEQ | Adaptive Biotechnologies | `rearrangement`, `amino_acid`, `v_resolved`, `j_resolved`, `count_(templates)` |

### Steps

1. Load the file into a tabular structure. Rename columns to a standard schema: `cloneId`, `count`, `frequency`, `cdr3aa`, `cdr3nt`, `v_gene`, `j_gene`, `chain`.

2. For 10x data, group by `barcode` first. Each barcode can have two rows (alpha/beta or heavy/light). Combine chains as comma-separated strings before deduplification.

3. Compute `cdr3_length` as the number of amino acid characters in `cdr3aa`. Flag sequences where length falls outside the expected range (TCR: 12–18 aa; BCR: 10–20 aa).

4. Define clonotypes by one of these methods (report which you chose):
   - **CDR3aa only**: fastest, may merge convergent sequences sharing identical translations
   - **CDR3nt**: nucleotide-level resolution, more stringent
   - **V + J + CDR3aa**: recommended default — balances specificity with sensitivity to allelic variation

5. Aggregate identical clonotypes: sum `count` values, sum `frequency` values, assign a rank (rank 1 = most abundant).

---

## Phase 2: Diversity and Clonality Analysis

**Goal**: Characterize the breadth (richness) and evenness of the repertoire using standard ecological diversity metrics.

### Key Metrics to Compute

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Richness | Count of unique clonotypes | Raw breadth |
| Shannon entropy | -sum(p_i * log2(p_i)) | Diversity weighted by frequency |
| Simpson index (D) | sum(p_i^2) | Probability two random reads are same clonotype |
| Inverse Simpson (1/D) | 1 / D | Effective number of clonotypes |
| Gini coefficient | Lorenz curve area ratio | Inequality; 0 = perfectly even, 1 = one dominant clone |
| Clonality | 1 - (Shannon / log2(Richness)) | 0 = polyclonal, 1 = fully monoclonal |

All metrics should be computed using read-count-weighted frequencies (not clone counts).

### Rarefaction

Generate a rarefaction curve by subsampling to increasing sequencing depths and counting observed unique clonotypes at each depth. If the curve has not plateaued at your actual depth, additional sequencing will reveal new clonotypes — interpret richness comparisons with caution.

**Minimum recommended depths**: 10,000 unique UMIs for bulk TCR-seq; 500 per cell for single-cell.

### Comparing Samples

- Always downsample all samples to the same depth before comparing Shannon entropy or Gini.
- Report at least three metrics (e.g., Shannon, clonality, richness) — no single metric is sufficient.
- Use biological replicates (n >= 3) for statistical comparisons.

---

## Phase 3: V(D)J Gene Usage Analysis

**Goal**: Determine which germline V and J gene segments are over- or under-represented compared to baseline.

### Steps

1. Extract V and J gene family identifiers from the raw call strings. For TCR-beta, the pattern `TRBV\d+` captures the family without allele. For TCR-alpha use `TRAV\d+`; for BCR heavy use `IGHV\d+`.

2. Compute V gene usage frequencies: for each V gene, sum all clonal counts bearing that gene, then divide by total reads. Repeat for J genes.

3. Build a V–J pairing matrix: rows = V genes, columns = J genes, values = frequency. High-contrast cells indicate preferred pairings.

4. Test for biased usage with a chi-square goodness-of-fit test against uniform expectation (or against a healthy donor reference if available). Report chi2 statistic and p-value per gene.

### TCR vs BCR Notes

- **TCR-alpha/beta**: TRAV + TRAJ (alpha chain), TRBV + TRBD + TRBJ (beta chain). Most diversity is in CDR3 beta. V gene bias is a hallmark of superantigen exposure or autoimmune disease.
- **TCR-gamma/delta**: TRGV + TRGJ, TRDV + TRDD + TRDJ. Much more restricted repertoire than alpha/beta.
- **BCR heavy/light**: IGHV + IGHD + IGHJ (heavy), IGKV + IGKJ or IGLV + IGLJ (light). Somatic hypermutation (SHM) causes divergence from germline; compute % identity to germline as a SHM proxy.

### Using IMGT Tools

Call `IMGT_search_genes` with `gene_type="TRBV"` (or `IGHV`, `TRAV`, etc.) to retrieve the canonical gene list and confirm naming conventions. Use `IMGT_get_sequence` to fetch a specific germline sequence for SHM alignment.

---

## Phase 4: CDR3 Sequence Analysis

**Goal**: Characterize the structural and biochemical properties of CDR3 sequences.

### Length Distribution

Compute the read-count-weighted CDR3 amino acid length distribution. Report mean and median. Flag samples where the modal length deviates by more than 2 aa from the species/chain-specific typical value, as this often indicates PCR primer bias or poor-quality sequencing.

Typical ranges:
- Human TCR-beta CDR3: 13–15 aa modal
- Human TCR-alpha CDR3: 12–14 aa modal
- Human BCR heavy CDR3 (HCDR3): highly variable, 10–25 aa

### Amino Acid Composition

Compute position-specific amino acid frequencies across CDR3 sequences aligned by length. Positions 1 (after anchor C) and -1 (before anchor F/W) should show restricted usage (conserved by V/J gene). Middle positions are hypervariable. Unusual enrichment of charged residues (D, E, K, R) at central positions may reflect antigen contact constraints.

### Physicochemical Properties

For each CDR3, derive:
- Net charge at physiological pH
- Hydrophobicity score (e.g., Grand Average of Hydropathicity, GRAVY)
- Aromaticity (fraction of F, W, Y)

These properties are interpretable in the context of antigen contact and MHC binding.

---

## Phase 5: Clonal Expansion Detection

**Goal**: Identify T or B cell clones that have undergone antigen-driven proliferation.

### Expansion Thresholds

Define expanded clonotypes by frequency threshold. Common approaches:
- **Absolute frequency**: clonotypes with frequency > 0.1% of total repertoire
- **Percentile cutoff**: clonotypes above the 95th or 99th frequency percentile
- **Fold-over-baseline**: clonotypes at post-stimulation/post-treatment timepoint that increased > 5-fold vs baseline

Report the threshold used. Note that a highly clonal baseline (e.g., post-HSCT) makes percentile thresholds less informative.

### Key Summary Statistics

- Number of expanded clonotypes
- Combined frequency of expanded clonotypes (% of total repertoire)
- Top 10 expanded clonotypes with their V gene, J gene, and CDR3aa sequences

### Longitudinal Tracking

When tracking across multiple timepoints:

1. Build a clonotype-by-timepoint frequency matrix. Fill missing entries with 0 (absent = not detected).
2. Compute persistence: number of timepoints where the clonotype was detected.
3. Compute fold-change: frequency at final timepoint divided by frequency at baseline.
4. Identify newly expanded clonotypes (absent or very rare at baseline, expanded post-treatment/vaccination).
5. Identify persistent clonotypes (present at all timepoints) — these are candidates for long-lived memory.

---

## Phase 6: Convergence and Public Clonotypes

**Goal**: Detect convergent recombination and identify clonotypes shared across individuals.

### Convergent Recombination

Convergence = multiple distinct nucleotide sequences encoding the same CDR3 amino acid sequence. Highly convergent sequences are likely antigen-driven because the same amino acid solution was independently reached by different rearrangements.

Steps:
1. Group clonotypes by `cdr3aa`.
2. For each group, count the number of distinct `cdr3nt` sequences.
3. Sequences with 2+ distinct nucleotide encodings are convergent.
4. Rank by number of nucleotide variants — the most convergent sequences are strongest candidates for antigen specificity.

Requires both `cdr3aa` and `cdr3nt` columns in input data.

### Public Clonotypes

Public clonotypes = those detected in multiple donors/samples. Steps:

1. For each sample in a cohort, record the set of clonotype identifiers (V + J + CDR3aa recommended).
2. Count how many samples each clonotype appears in.
3. Define public as present in >= N samples (set N based on cohort size — e.g., >= 3 of 10 donors, or >= 20%).
4. Report the public fraction and list the top public clonotypes.

Cross-reference public CDR3 sequences against VDJdb (https://vdjdb.cdr3.net) and McPAS-TCR manually, or use `PubMed_search_articles` with the CDR3 sequence as a search term to find publications reporting that sequence.

---

## Phase 7: Epitope Specificity Prediction

**Goal**: Link expanded or public clonotypes to known antigens using IEDB and literature resources.

### Approach 1: Query IEDB via EBI Proteins

For a candidate antigen protein (e.g., a viral or tumor antigen suspected of driving expansion):

1. Retrieve the protein's UniProt accession (use `UniProt_search` or similar).
2. Call `EBIProteins_get_epitopes` with that accession. The response lists experimentally mapped T-cell and B-cell epitope regions from IEDB, with positions and supporting literature.
3. Check whether any epitope sequence is similar to or overlapping with your candidate CDR3 sequences or antigen peptides.

### Approach 2: Query BVBRC for Pathogen Epitopes

For infectious disease contexts (SARS-CoV-2, influenza, tuberculosis, etc.):

1. Find the pathogen's NCBI Taxonomy ID (e.g., 2697049 for SARS-CoV-2).
2. Call `BVBRC_search_epitopes` with `taxon_id` and optionally `protein_name` (e.g., "Spike glycoprotein") and `epitope_type="Linear peptide"`.
3. This returns peptide sequences from IEDB confirmed as T-cell or B-cell epitopes. Compare to your identified CDR3 sequences or peptide binding predictions.

### Approach 3: Literature Mining

For any CDR3 sequence of interest — especially convergent or public ones:

1. Call `PubMed_search_articles` with a query like `"CASSDRGGQPQHF" AND (epitope OR antigen OR specificity)`. Replace the CDR3 with your actual sequence.
2. Call `EuropePMC_search_articles` similarly. The full-text search can surface papers mentioning CDR3 sequences that PMID abstract-level search misses.
3. Call `LiteratureSearchTool` with `research_topic` describing the CDR3 sequence and biological context for a cross-database summary.

### TCR-specific Notes

- Most TCR specificities are unknown. Even for expanded clonotypes, negative database results are common.
- CDR3 beta alone is not sufficient for specificity — MHC-peptide recognition requires both alpha and beta chains in most contexts.
- Use convergence as supporting evidence: a convergent CDR3 with 5+ nucleotide encodings in multiple donors strongly implies antigen selection.

### BCR-specific Notes

- BCR sequences diverge from germline through somatic hypermutation. Compute germline identity before querying databases that store germline-derived sequences.
- Use `IMGT_get_sequence` to fetch the closest germline V segment, then align your clonotype to estimate SHM percentage.

---

## Phase 8: Integration with Single-Cell Data

**Goal**: Link clonotypes to cell phenotypes using paired VDJ + gene expression data.

### Data Requirements

- 10x Genomics Chromium Immune Profiling: `filtered_contig_annotations.csv` (VDJ) + `filtered_feature_bc_matrix` or `.h5` (GEX)
- Cell barcodes must match exactly between VDJ and GEX libraries (check suffix conventions)

### Steps

1. Load VDJ clonotype table (10x format). Assign each barcode a clonotype identifier (V + J + CDR3aa for each chain).

2. Load GEX data as an AnnData object. Run standard preprocessing: filter cells, normalize, log-transform, select highly variable genes, PCA, neighbors graph, UMAP, Leiden clustering.

3. Add clonotype metadata to the AnnData observation table (`obs`). Map barcode to clonotype identity. Add boolean column `has_clonotype` and `is_expanded` (True if clonotype appears in more than a threshold number of cells, e.g., 5).

4. Visualize on UMAP: color by clonotype identity, by `is_expanded`, and by cluster. Identify whether expanded clones cluster in specific phenotypic states.

5. Build a clonotype-by-cluster cross-tabulation (rows = clonotypes, columns = Leiden clusters, values = fraction of cells per clonotype in each cluster). Clonotypes with >80% cells in one cluster are phenotypically restricted.

6. Use `CELLxGENE_get_cell_metadata` with `obs_value_filter='cell_type in ["T cell", "B cell"] and disease == "normal"'` to retrieve reference cell type metadata from the CZ CELLxGENE corpus for comparison.

### Clonotype-Phenotype Interpretation

- **CD8+ effector clusters + expanded clonotypes**: cytotoxic response, cancer/viral antigen-specific
- **CD4+ T follicular helper (Tfh) clusters + clonotypes**: germinal center involvement (BCR co-analysis)
- **Mixed cluster distribution for a clonotype**: may indicate plasticity or bystander activation
- **Expanded clones in exhaustion clusters**: chronic antigen exposure (tumor or chronic infection)

---

## Use Cases

### Cancer Immunotherapy Response

Compare TCR repertoires before and after treatment:
1. Run Phase 1–5 independently for baseline and post-treatment samples.
2. Compute diversity change (Shannon post minus Shannon baseline). A positive increase post-treatment can indicate immune reconstitution; a decrease with rising clonality indicates oligoclonal expansion.
3. Identify newly expanded clonotypes (present post but absent or < 0.01% at baseline).
4. Query those CDR3 sequences against IEDB using `EBIProteins_get_epitopes` for the target tumor antigens.

### Vaccine Response Tracking

Track repertoire across 4 timepoints (pre, week 1, week 4, week 12):
1. Identify clonotypes that expand between week 0 and week 1 (acute response).
2. Identify clonotypes that persist to week 12 (memory candidates).
3. Assess convergence among expanded clonotypes — convergent vaccine-responding clonotypes are more likely antigen-specific.

### Autoimmune Disease

Compare TCR repertoires between patients and healthy controls:
1. Compare clonality index — autoimmune patients often show higher clonality in affected tissue.
2. Test for V gene bias: chi-square test on V gene frequencies, patient vs control. TRBV biases are documented in multiple sclerosis, rheumatoid arthritis, and type 1 diabetes.
3. Identify patient-specific expanded clonotypes. Mine literature with `PubMed_search_articles` for those CDR3 sequences in the context of the disease.

### Single-Cell TCR + RNA-seq (10x VDJ + GEX)

1. Follow Phase 8 steps to link clonotypes to clusters.
2. Run differential expression (Wilcoxon rank-sum) between expanded and non-expanded cells to find marker genes.
3. Use `CellMarker_search_by_cell_type` to annotate clusters with canonical markers.
4. Report phenotypic state of the top 10 expanded clonotypes (exhausted, naive, effector, memory, Treg).

---

## Best Practices

1. **Clonotype definition**: Report which method you used (CDR3aa, CDR3nt, V+J+CDR3aa). Use V+J+CDR3aa as the default for bulk TCR-seq.

2. **Rare clonotype filtering**: Remove clonotypes with frequency < 0.001% or count < 2 to exclude likely sequencing errors before diversity calculations.

3. **Multiple diversity metrics**: Always report Shannon entropy, clonality, and richness together. No single metric is interpretable alone.

4. **Batch effects**: Samples processed in different sequencing runs require batch correction before cross-sample diversity comparisons.

5. **V/J annotation**: Use IMGT-referenced allele names. Check IMGT tool responses to confirm gene naming conventions match your aligner's output.

6. **CDR3 length anomalies**: Distributions shifted more than 2 residues from the expected modal length should be flagged as possible PCR bias before proceeding.

7. **Productive sequences only**: Filter to productive rearrangements (no stop codons, in-frame) before all analyses unless you specifically study non-productive sequences.

8. **VDJdb / McPAS manual check**: After identifying top expanded/convergent/public clonotypes, manually check VDJdb (https://vdjdb.cdr3.net) and McPAS-TCR for known specificity annotations — these databases are not yet accessible via ToolUniverse tools.

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Very low diversity (1–2 dominant clones) | Clonal malignancy, or PCR bias | Check CDR3 length distribution for normality; verify sequencing QC |
| No CDR3 sequences found | Wrong column name for input format | Check aligner-specific column names listed in Phase 1 table |
| IMGT tool returns URL only, no sequence | Expected behavior of `IMGT_search_genes` | Use `IMGT_get_sequence` with an accession for actual sequence data |
| Zero clonotype-cell links in single-cell integration | Barcode suffix mismatch | Inspect first 5 barcodes from both files; strip or add `-1` suffix as needed |
| CDR3 length distribution bimodal | Likely mixed TCR alpha + beta chains in same file | Split by `chain` column before length analysis |
| BVBRC returns no epitopes for your CDR3 | BVBRC stores pathogen-side peptides, not receptor sequences | Use it to get candidate antigen peptides, then compare; not a CDR3 lookup |
| EBIProteins_get_epitopes returns empty | Protein has no IEDB-curated epitopes | Most proteins have none; this is normal |
| High non-productive fraction (>30%) | BCR dataset with SHM, or contamination | Filter `productive == True`; for BCR, SHM-induced non-productive sequences are expected at lower levels |

---

## References

- Dash P, et al. (2017) Quantifiable predictive features define epitope-specific T cell receptor repertoires. *Nature* 547:89–93.
- Glanville J, et al. (2017) Identifying specificity groups in the T cell receptor repertoire. *Nature* 547:94–98.
- Stubbington MJT, et al. (2016) T cell fate and clonality inference from single-cell transcriptomes. *Nature Methods* 13:329–332.
- Vander Heiden JA, et al. (2014) pRESTO: a toolkit for processing high-throughput sequencing raw reads of lymphocyte receptor repertoires. *Bioinformatics* 30:1930–1932.
- Robins HS, et al. (2009) Comprehensive assessment of T-cell receptor beta-chain diversity in alphabeta T cells. *Blood* 114:4099–4107.
