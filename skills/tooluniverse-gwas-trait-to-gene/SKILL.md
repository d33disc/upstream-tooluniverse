---
name: tooluniverse-gwas-trait-to-gene
description: Discover genes associated with diseases and traits using GWAS data from the GWAS Catalog (500,000+ associations) and Open Targets Genetics (L2G predictions). Identifies genetic risk factors, prioritizes causal genes via locus-to-gene scoring, and assesses druggability. Use when asked to find genes associated with a disease or trait, discover genetic risk factors, translate GWAS signals to gene targets, or answer questions like "What genes are associated with type 2 diabetes?"
---

# GWAS Trait-to-Gene Discovery

Systematically identify genes linked to a disease or trait by aggregating GWAS data from GWAS Catalog and Open Targets Genetics.

**KEY PRINCIPLES**:
1. **English-first queries** — always use English trait names in tool calls, even if the user writes in another language
2. **EFO/MONDO ID first** — resolve the ontology ID before searching associations; text searches return off-target global results
3. **Genome-wide significance** — default threshold p < 5×10⁻⁸; treat `p_value=0.0` as significant (API floating-point underflow)
4. **Evidence ranking** — aggregate across studies, prioritize L2G-confirmed genes
5. **Negative results documented** — "no associations found" is a valid answer, not a failure

---

## Workflow

```
Step 0: Resolve working EFO/MONDO ID for the trait
Step 1: Retrieve trait-specific associations from GWAS Catalog
Step 2: Aggregate genes; rank by p-value, study count, L2G score
Step 3: Enrich top genes with Open Targets fine-mapping (L2G)
Step 4: Report prioritized gene list with evidence levels
```

---

## Step 0: Resolve Trait EFO/MONDO ID (REQUIRED)

Do NOT skip this step. Text-based disease_trait searches in the API are unreliable:
- "Alzheimer's disease" as text → returns unrelated traits (buccal mucosa cancer, bilirubin, etc.)
- `EFO_0000249` for Alzheimer's → returns 0 results (wrong namespace)
- `MONDO_0004975` for Alzheimer's → returns 6,200+ results (correct namespace)

**Resolve the correct ID:**

```
gwas_search_studies(disease_trait=<trait_name>, size=5)
# → inspect efo_traits[].efo_id from any returned study
# → note: may be MONDO_*, EFO_*, HP_*, ORPHA_* depending on disease
# → verify with: gwas_search_studies(efo_id=<candidate_id>, size=1) — should return results

# Fallback: EpiGraphDB_map_gwas_to_efo(trait=<name>)
# → returns GWAS IDs; then cross-reference with gwas_search_studies
```

---

## Step 1: Retrieve Associations (Use efo_id, Not Text)

```
gwas_get_associations_for_trait(efo_id=<resolved_id>, size=100)
gwas_search_studies(efo_id=<resolved_id>, size=50)  # also needed for Step 3
```

**Important caveats:**
- **`p_value=0.0`** in API responses = floating-point underflow (p < 5e-309); treat as genome-wide significant
- Paginate when needed (page=1, page=2...) to capture loci beyond top-100; for well-studied diseases, 3-4 pages cover all major loci
- Use `efo_id` parameter, not `disease_trait` text; `gwas_search_associations(disease_trait=...)` without efo_id is unreliable for disease-specific queries

---

## Step 2: Aggregate and Rank Genes

From the associations retrieved, extract mapped genes and compute:

| Field | Source |
|-------|--------|
| `symbol` | `mappedGenes` field in association |
| `min_p_value` | lowest p-value across studies |
| `evidence_count` | number of independent studies with p < 5e-8 |
| `snps` | list of associated rs IDs |
| `confidence_level` | see below |

**Confidence levels:**
- **High**: evidence_count ≥ 3 OR L2G score > 0.5
- **Medium**: evidence_count = 2 OR (1 study with p < 5e-10)
- **Low**: single study at p < 5e-8

**Watch for co-localized genes:** Multiple genes in a single locus (e.g., APOE/TOMM40/NECTIN2/APOC1 at 19q13.32) share the same lead SNPs. Report these as a single locus cluster, not independent signals.

---

## Step 3: Open Targets Fine-Mapping (for top genes)

Use GCST accessions from Step 1's `gwas_search_studies` output (sort by sample size; use the largest 1-2 studies):

```
OpenTargets_get_study_credible_sets(studyIds=[<GCST_accession>], size=30)
# → returns loci with l2GPredictions[].gene.symbol and l2GPredictions[].score
# → L2G score > 0.5 = strong causal evidence; > 0.8 = very high confidence

# To look up a specific variant's credible sets (optional):
OpenTargets_get_variant_credible_sets(variantId=<chr_pos_ref_alt>)
# IMPORTANT: variantId format = "19_44908684_G_C" (NOT rsID)
# Get chr_pos_ref_alt from variant.id field in OpenTargets_get_study_credible_sets output
```

**Note**: `OpenTargets_search_gwas_studies_by_disease` does NOT exist. Use `gwas_search_studies` to find GCST IDs.

---

## Step 4: Report

Present a prioritized table:

```markdown
## Genes Associated with [Trait]

**Search**: EFO/MONDO ID: [id] | Total associations: [N] | Analyzed: [N] (p < 5e-8)

| Gene | Min p-value | Studies | L2G Score | Confidence |
|------|-------------|---------|-----------|------------|
| APOE | ~0.0* | 40 | 0.17† | High |
| BIN1 | 6e-118 | 11 | 0.836 | High |
| CR1  | 7e-46  | 3  | 0.935 | High |
| CLU  | 2e-44  | 3  | 0.847 | High |

*p_value=0.0 = floating-point underflow; interpret as p < 5e-309
†APOE locus: APOE, TOMM40, NECTIN2, APOC1, BCAM are co-localized (share lead SNPs)
```

Always include:
- Total associations searched and p-value threshold used
- Whether L2G data was available and which study was used
- Any co-localized locus clusters
- Any trait search ambiguity and the working EFO/MONDO ID used

---

## Tool Reference

| Tool | Use Case |
|------|----------|
| `gwas_search_studies` | Find GCST accessions + resolve EFO/MONDO IDs for a trait |
| `gwas_get_associations_for_trait` | Get associations using efo_id (preferred over text search) |
| `gwas_get_associations_for_study` | All associations from one specific study |
| `gwas_get_associations_for_snp` | All traits for a specific SNP (rs ID lookup) |
| `gwas_search_snps` | SNPs mapped to a gene |
| `gwas_get_snp_by_id` | SNP details (MAF, consequence, location) |
| `OpenTargets_get_study_credible_sets` | Fine-mapped loci with L2G scores (use GCST ID) |
| `OpenTargets_get_variant_credible_sets` | Credible sets for a variant (use chr_pos_ref_alt format) |
| `OpenTargets_get_variant_info` | Variant frequencies + functional consequences |
| `OpenTargets_get_gwas_study` | Metadata for a single GWAS study by GCST ID |
| `EpiGraphDB_map_gwas_to_efo` | Map trait name to GWAS IDs (fallback for EFO resolution) |

---

## Interpretation Notes

- **Association ≠ causation** — positional mapping assigns SNPs to nearest gene, which may not be causal; L2G mitigates this
- **LD confounding** — the lead SNP may tag a causal variant in a nearby gene; L2G integrates QTL and regulatory evidence
- **APOE locus co-localization** — many genes near 19q13.32 (TOMM40, NECTIN2, APOC1, BCAM) share APOE lead SNPs; report as "APOE locus," not independent signals
- **EFO namespace mismatch** — GWAS Catalog uses MONDO_* for many diseases; EFO_* IDs for the same disease may return zero results from REST API v2; always verify with `gwas_search_studies`
- **Population bias** — most GWAS are in European cohorts; effect sizes may differ across ancestries
- **Winner's curse** — discovery p-values overestimate effect size; prefer replicated loci
