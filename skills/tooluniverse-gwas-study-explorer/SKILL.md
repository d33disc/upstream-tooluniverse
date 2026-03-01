---
name: tooluniverse-gwas-study-explorer
description: Compare GWAS studies, perform meta-analyses, and assess replication across cohorts. Integrates NHGRI-EBI GWAS Catalog and Open Targets Genetics to compare study designs, effect sizes, ancestry diversity, and heterogeneity statistics. Use when comparing GWAS studies for a trait, performing meta-analysis of genetic loci, assessing replication across cohorts, or exploring the genetic architecture of complex diseases.
---

# GWAS Study Explorer & Meta-Analysis

Compare GWAS studies, meta-analyze loci, and assess replication for any trait.

**KEY PRINCIPLES**:
1. **English-first queries** — always use English trait names in tool calls
2. **Heterogeneity first** — calculate I² before interpreting combined effect sizes
3. **Ancestry-aware** — report ancestry breakdown; stratify if studies mix populations
4. **Direction consistency** — replication requires same effect direction, not just p < 0.05

---

## Workflow

```
Phase 0: Identify user goal (comparison / meta-analysis / replication)
Phase 1: Retrieve all studies for the trait
Phase 2: Pull associations per study; extract locus data
Phase 3: Meta-analysis / replication assessment
Phase 4: Report
```

---

## Phase 0: Clarify Goal

Three distinct modes — pick the right one:

| User Request | Mode |
|---|---|
| "Compare GWAS studies for [trait]" | Study comparison |
| "Is [SNP/gene] consistent across studies?" | Locus meta-analysis |
| "Did [discovery] replicate in [cohort]?" | Replication analysis |

---

## Phase 1: Retrieve Studies

```
gwas_search_studies(diseaseOrTrait=<trait_name>, size=50)
OpenTargets_search_gwas_studies_by_disease(disease_id=<efo_id>)
```

For each study, record: accession, sample size, ancestry, platform, pubYear, initialSampleSize.

Use `OSL_get_efo_id_by_disease_name` if you need an EFO ID for Open Targets queries.

---

## Phase 2: Pull Associations

```
gwas_get_associations_for_study(study_id=<accession>, size=100)
gwas_get_associations_for_snp(variant_id=<rsid>)   # for locus-specific queries
OpenTargets_get_study_credible_sets(study_id=<ot_study_id>)
OpenTargets_get_variant_info(variant_id=<rsid>)     # allele frequencies
```

Collect per-SNP: rsid, p-value, beta/OR, confidence interval, effect allele.

---

## Phase 3: Analysis

### Study Comparison
Build a summary table across studies:

| Study | n | Ancestry | Platform | Top loci (p<5e-8) | Year |
|-------|---|----------|----------|-------------------|------|
| GCST001 | 50,000 | EUR | Illumina | 42 | 2021 |
| GCST002 | 30,000 | EAS | Affymetrix | 18 | 2022 |

Assess: sample size tiers (High ≥50K, Moderate ≥10K, Limited <10K), ancestry diversity, data availability.

### Locus Meta-Analysis
For SNPs present in ≥2 studies:

1. Collect beta + SE from each study
2. Calculate inverse-variance weighted combined effect:
   - `weight_i = 1 / SE_i²`
   - `beta_combined = Σ(weight_i × beta_i) / Σ(weight_i)`
   - `SE_combined = 1 / sqrt(Σ(weight_i))`
3. Compute Cochran's Q and I²:
   - `Q = Σ(weight_i × (beta_i − beta_combined)²)`
   - `I² = max(0, (Q − df) / Q × 100%)`

**I² interpretation**: <25% low heterogeneity → fixed-effects OK; 25-50% moderate; >50% use random-effects or stratify; >75% meta-analysis questionable.

### Replication Analysis
For each top hit from the discovery study:
1. Check if SNP appears in replication study (`gwas_get_associations_for_snp`)
2. Verify: same direction? replication p < 0.05? OR/beta similar magnitude?
3. Classify: Replicated / Directionally consistent / Failed replication / Not tested

---

## Phase 4: Report

```markdown
## GWAS Study Summary: [Trait]

### Studies Found: N

| Study | n | Ancestry | Top Loci | Quality |
|-------|---|----------|----------|---------|
...

### Meta-Analysis: [Locus/SNP]

| Study | Beta | SE | p-value |
|-------|------|----|---------|
...
Combined: beta=X.XX (SE=X.XX), p=X.Xe-XX, I²=XX%

**Interpretation**: [Low/Moderate/High] heterogeneity. [Fixed/Random]-effects model appropriate.

### Replication Summary
- Replicated: N/M loci (XX%)
- Failed: [list with p-values from replication attempt]
- Not tested: [list]
```

---

## Common Pitfalls

- **Cohort overlap**: Some cohorts participate in multiple studies → inflates significance when combined; check `initialSampleSize` descriptions
- **Winner's curse**: Discovery p-values overestimate effect size; replicated effect sizes are more reliable
- **Allele harmonization**: Ensure effect alleles match before combining beta values (flip sign if needed)
- **Ancestry mismatch**: High I² from mixed-ancestry meta-analysis may reflect real population differences, not errors

---

## Tool Reference

| Tool | Use Case |
|------|----------|
| `gwas_search_studies` | Find studies by trait |
| `gwas_get_study_by_id` | Study metadata (sample size, ancestry) |
| `gwas_get_associations_for_study` | All SNPs from a study |
| `gwas_get_associations_for_snp` | Trait associations for a SNP |
| `gwas_search_associations` | Cross-study search by trait |
| `OpenTargets_search_gwas_studies_by_disease` | OT disease-based study lookup |
| `OpenTargets_get_gwas_study` | OT study metadata with LD populations |
| `OpenTargets_get_study_credible_sets` | Fine-mapped credible sets |
| `OpenTargets_get_variant_info` | Variant annotation + allele frequencies |
