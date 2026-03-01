---
name: tooluniverse-variant-interpretation
description: Systematic clinical variant interpretation from raw variant calls to ACMG-classified recommendations with structural impact analysis. Aggregates evidence from ClinVar, gnomAD, CIViC, UniProt, and PDB across ACMG criteria. Produces pathogenicity scores (0-100), clinical recommendations, and treatment implications. Use when interpreting genetic variants, classifying variants of uncertain significance (VUS), performing ACMG variant classification, or translating variant calls to clinical actionability.
---

# Clinical Variant Interpreter

Systematic variant interpretation skill — from raw variant calls to ACMG-classified clinical recommendations with structural impact analysis.

---

## Key Principles

1. **ACMG-Guided Classification** — Follow ACMG/AMP 2015 guidelines with explicit evidence codes.
2. **Structural Evidence Integration** — Use AlphaFold2 for novel structural impact analysis.
3. **Population Context** — gnomAD frequencies with ancestry-specific data.
4. **Gene-Disease Validity** — ClinGen curation status before applying classification criteria.
5. **Actionable Output** — Clear recommendations, not just classifications.
6. **English-first queries** — Always use English terms in tool calls (gene names, variant descriptions, disease names), even if the user writes in another language. Respond in the user's language.

---

## Workflow Overview

```
Phase 1  VARIANT IDENTITY
         Normalize to HGVS; map to gene, transcript, protein; get consequence type

Phase 2  CLINICAL DATABASES
         ClinVar (existing classifications) → gnomAD (population frequency) →
         OMIM (gene-disease) → ClinGen (validity + dosage) →
         COSMIC (somatic context) → DisGeNET (gene-disease evidence) →
         SpliceAI (if intronic or synonymous)

Phase 2.5  REGULATORY CONTEXT  [non-coding / intronic / UTR variants only]
           ChIPAtlas (TF binding) + ENCODE (regulatory elements)

Phase 3  COMPUTATIONAL PREDICTIONS
         AlphaMissense + CADD + EVE (missense); SIFT/PolyPhen for context

Phase 4  STRUCTURAL ANALYSIS  [VUS / novel missense]
         PDB (experimental) or AlphaFold (predicted); InterPro domains; UniProt sites

Phase 4.5  EXPRESSION CONTEXT
           GTEx (tissue expression) + CELLxGENE (cell-type expression)

Phase 5  LITERATURE EVIDENCE
         PubMed + EuropePMC preprints (BioRxiv/MedRxiv via PPR source)

Phase 6  ACMG CLASSIFICATION
         Apply evidence codes → classify → generate recommendations
```

---

## Phase 1: Variant Identity & Normalization

**Goal**: Standardize variant notation and determine molecular consequence.

Call `myvariant_query` with the variant identifier and fields `clinvar,gnomad,cadd,dbnsfp` to get aggregated annotations in one call. Use `Ensembl_get_variant_info` for VEP consequence data, and `NCBI_gene_search` if gene context is missing.

**Capture**:
- HGVS c. and p. notations
- Gene symbol and Ensembl ID
- MANE Select transcript
- Consequence type (missense, nonsense, splice, etc.)
- Exon/intron location

---

## Phase 2: Clinical Database Queries

**Goal**: Aggregate existing clinical knowledge before applying computational evidence.

### 2.1 ClinVar

Call `clinvar_search` with the HGVS variant notation. Record: classification, review star level, number of submitters, and whether an expert panel has reviewed it.

**Classification map**:
| ClinVar | Interpretation |
|---------|----------------|
| Pathogenic / Likely pathogenic | Disease-causing (>90% confidence) |
| VUS | Uncertain significance |
| Likely benign / Benign | Not disease-causing |
| Conflicting interpretations | Multiple submissions disagree — do not use directly |

### 2.2 gnomAD

Call `gnomad_search` using chr-pos-ref-alt format (e.g., `17-41245466-A-G`). Report overall AF and at least 3 ancestry-specific AFs, plus homozygote count.

**Frequency thresholds**:
| Frequency | ACMG Code |
|-----------|-----------|
| >5% | BA1 (stand-alone benign — stops interpretation) |
| >1% | BS1 (strong benign) |
| Absent from controls | PM2_Supporting (pathogenic) |
| <0.0001 | Rare — use in context |

### 2.3 OMIM

Call `OMIM_search` then `OMIM_get_entry` for gene-disease associations and inheritance pattern. Call `OMIM_get_clinical_synopsis` to match phenotype features. Requires `OMIM_API_KEY`.

### 2.4 ClinGen (Critical — run for every variant)

ClinGen establishes whether the gene-disease relationship is sufficiently validated to use ACMG evidence criteria. Do not apply PP4 for genes with Limited, Disputed, or Refuted validity.

Call `ClinGen_search_gene_validity` to get the validity level (Definitive / Strong / Moderate / Limited / Disputed / Refuted). Call `ClinGen_search_dosage_sensitivity` to get haploinsufficiency and triplosensitivity scores (0-3) — score 3 = established, required for PVS1 on LOF CNVs. Call `ClinGen_search_actionability` for incidental findings context.

### 2.5 COSMIC (cancer variants)

For somatic/cancer contexts, call `COSMIC_search_mutations` with `"{GENE} {AA_change}"` to check if the variant is a recurrent hotspot. Call `COSMIC_get_mutations_by_gene` to assess overall mutation landscape. Recurrent hotspot (>100 samples) supports PS3; moderate frequency (10-100) supports PM1.

### 2.6 DisGeNET (gene-disease evidence)

Call `DisGeNET_search_gene` to get gene-disease associations with evidence scores. If an rsID is available, call `DisGeNET_get_vda` for variant-disease associations. Score >0.7 supports PP4; 0.4-0.7 is supporting evidence; <0.4 is insufficient. Requires `DISGENET_API_KEY`.

### 2.7 SpliceAI (splice-altering assessment)

Run SpliceAI for: intronic variants within ±50bp of splice sites, synonymous variants, exonic variants near junctions, and any variant where splice disruption is suspected.

Call `SpliceAI_predict_splice` with format `chr{chrom}-{pos}-{ref}-{alt}` and `genome="38"`. Use `SpliceAI_get_max_delta` for a quick triage score.

**Delta score to ACMG**:
| Max Delta Score | ACMG Support |
|-----------------|--------------|
| ≥0.8 | PP3 (strong splice impact) |
| 0.5-0.8 | PP3 (supporting) |
| 0.2-0.5 | PP3 (weak) |
| <0.2 | BP7 (if synonymous) |

---

## Phase 2.5: Regulatory Context (Non-Coding Variants Only)

**Apply when**: variant is intronic (not canonical splice site), in a promoter, 5'/3'UTR, or intergenic near a disease gene.

Call `ChIPAtlas_enrichment_analysis` with the nearby gene to identify transcription factors with binding peaks at the variant position. Call `ChIPAtlas_get_peak_data` to confirm peak coordinates. Call `ENCODE_search_experiments` with assay types (ATAC-seq for open chromatin, H3K27ac for active enhancers) to assess regulatory activity.

**Impact tiers**:
- High: variant disrupts a known TF binding motif in an active regulatory element → PP3 (supporting)
- Moderate: variant falls in an annotated regulatory region → assess with conservation
- Low: no regulatory annotation → no ACMG support from this phase

---

## Phase 3: Computational Predictions

**Goal**: Collect concordant in silico evidence for PP3 or BP4.

**For missense variants**: Call `AlphaMissense_get_variant_score` (requires UniProt ID and AA change like "L858R") — this is the highest-accuracy predictor (~90% on ClinVar pathogenic). Call `CADD_get_variant_score` (works for all variant types; use `version="GRCh38-v1.7"`). Call `EVE_get_variant_score` after first verifying gene coverage with `EVE_get_gene_info`.

**For non-missense variants**: CADD is the primary predictor. SpliceAI (Phase 2.7) handles splice assessment.

**Thresholds**:
| Predictor | Damaging | Benign |
|-----------|----------|--------|
| AlphaMissense | >0.564 | <0.34 |
| CADD PHRED | ≥20 | <15 |
| EVE | >0.5 | ≤0.5 |
| SIFT | <0.05 | ≥0.05 |

**PP3/BP4 rule**: Apply PP3 when ≥2 predictors indicate damaging and none indicate benign. Apply BP4 when ≥2 predictors indicate benign and none indicate damaging. Discordant results = neutral.

---

## Phase 4: Structural Analysis (VUS / Novel Missense)

**Goal**: Assess 3D protein impact, especially for VUS where computational predictions are discordant.

First try `PDB_search_by_uniprot` to find an experimental structure. If none exists, use `alphafold_get_prediction` (AlphaFold DB) or `NvidiaNIM_alphafold2` to predict de novo (supply the protein sequence from `UniProt_get_protein_sequence`; use `algorithm="mmseqs2"`; respect the 40 RPM rate limit).

Get domain annotations from `InterPro_get_protein_domains` and functional site annotations from `UniProt_get_protein_function`. Cross-reference the variant residue position against domain boundaries and active/binding sites.

**Structural impact to ACMG**:
| Context | ACMG Code |
|---------|-----------|
| Active site / catalytic residue | PM1 (strong) |
| Buried in structural core / disulfide | PM1 (moderate) |
| Domain interface / binding site | PM1 (supporting) |
| Surface / flexible loop | No support |

**pLDDT confidence for AlphaFold positions**: >90 = very high, 70-90 = high, 50-70 = moderate (use with caution), <50 = likely disordered (unreliable for variant assessment).

**Key structural features to report**: pLDDT at position, secondary structure, solvent accessibility, distance to active site, hydrogen bonds or salt bridges disrupted.

---

## Phase 4.5: Expression Context

**Goal**: Confirm the gene is expressed in disease-relevant tissues to support PP4 or challenge a classification.

Call `GTEx_get_median_gene_expression` for bulk tissue expression (TPM per tissue). Call `CELLxGENE_get_expression_data` for cell-type-specific expression in the relevant tissue.

If the gene is not expressed (TPM < 1) in the tissue affected by the reported phenotype, document this discrepancy. High tissue-restricted expression (e.g., only in cardiomyocytes for a cardiac phenotype) can support PP4.

---

## Phase 5: Literature Evidence

**Goal**: Find functional studies, case reports, and segregation data.

Call `PubMed_search` with queries:
- Specific variant: `"{GENE}" AND ("{HGVS_p}" OR "{AA_change}")`
- Functional studies: `"{GENE}" AND (functional study OR mutagenesis)`
- Clinical: `"{GENE}" AND (case report OR patient) AND "{phenotype}"`

For recent preprints, call `EuropePMC_search_articles` with `source="PPR"`. Always flag preprints as NOT peer-reviewed in the report.

Use `openalex_search_works` or `SemanticScholar_search_papers` for citation analysis of key papers.

**Evidence to ACMG**:
| Evidence Type | ACMG Code | Weight |
|---------------|-----------|--------|
| Functional study (null effect) | PS3 | Strong |
| Functional study (reduced function) | PS3_Moderate | Moderate |
| Case reports with segregation | PP1 | Supporting to Moderate |
| Co-occurrence with known pathogenic | BP2 | Supporting against |

---

## Phase 6: ACMG Classification

**Goal**: Systematic classification with explicit evidence codes.

### Pathogenic Evidence Codes
| Code | Strength | Trigger |
|------|----------|---------|
| PVS1 | Very Strong | Null variant in gene where LOF is the mechanism |
| PS1 | Strong | Same amino acid change as established pathogenic variant |
| PS2 | Strong | De novo (parentage confirmed) |
| PS3 | Strong | Well-established functional studies showing damaging effect |
| PS4 | Strong | Significantly increased prevalence in affected individuals |
| PM1 | Moderate | Mutational hotspot or in functional domain (no benign variation) |
| PM2 | Moderate | Absent from controls (or extremely low frequency) |
| PM3 | Moderate | Detected in trans with a pathogenic variant |
| PM4 | Moderate | Protein length change (in-frame indel or stop-loss) |
| PM5 | Moderate | Novel missense at residue where different missense is pathogenic |
| PM6 | Moderate | De novo (parentage not confirmed) |
| PP1 | Supporting | Segregation with disease in affected family members |
| PP2 | Supporting | Missense in gene with low missense benign variation rate |
| PP3 | Supporting | Concordant damaging computational predictions |
| PP4 | Supporting | Phenotype highly specific to gene with established validity |
| PP5 | Supporting | Reputable source reports pathogenic, criteria not shared |

### Benign Evidence Codes
| Code | Strength | Trigger |
|------|----------|---------|
| BA1 | Stand-alone | MAF >5% in any population |
| BS1 | Strong | MAF greater than expected for disorder |
| BS2 | Strong | Observed healthy homozygotes/hemizygotes |
| BS3 | Strong | Functional studies show no damaging effect |
| BS4 | Strong | No segregation with disease |
| BP1 | Supporting | Missense in gene where only LOF causes disease |
| BP2 | Supporting | Observed in trans with pathogenic (dominant) or in cis (any) |
| BP3 | Supporting | In-frame indel in region without known function |
| BP4 | Supporting | Concordant benign computational predictions |
| BP5 | Supporting | Alternate molecular explanation found |
| BP7 | Supporting | Synonymous, no predicted splice impact |

### Classification Algorithm
| Classification | Evidence Required |
|----------------|-------------------|
| Pathogenic | (1 Very Strong + ≥1 Strong); OR (≥2 Strong); OR (1 Strong + ≥3 Moderate) |
| Likely Pathogenic | (1 Very Strong + 1 Moderate); OR (1 Strong + 1-2 Moderate); OR (1 Strong + ≥2 Supporting) |
| Likely Benign | (1 Strong Benign + 1 Supporting Benign); OR (≥2 Supporting Benign) |
| Benign | (1 Stand-alone); OR (≥2 Strong Benign) |
| VUS | Criteria not met for any above |

### PVS1 Strength Modifiers (Truncating Variants)
| Scenario | PVS1 Strength |
|----------|---------------|
| Canonical splice/frameshift/nonsense; LOF-mechanism gene; NMD predicted | Very Strong |
| As above but variant in last exon (may escape NMD) | Moderate |
| In-frame indel; or gene where LOF is not the mechanism | Not applicable |

---

## Special Scenarios

### Scenario: Novel Missense VUS

Beyond the standard workflow, additionally:
1. Check ClinVar for other pathogenic variants at the same residue (supports PM5).
2. Get AlphaFold2 or PDB structure; assess burial depth, secondary structure, proximity to functional sites.
3. Apply PM1 if the residue is in a functional domain with no benign variation.
4. Apply PP3 only if ≥2 predictors (AlphaMissense, CADD, EVE) concordantly indicate damaging.

### Scenario: Truncating Variant

1. Confirm LOF is the disease mechanism using ClinGen haploinsufficiency data.
2. Determine whether the variant is in the last exon or last 50bp of the penultimate exon (NMD escape).
3. Check for alternative isoforms where the truncation may be tolerated.

### Scenario: Splice Variant

1. Run SpliceAI (Phase 2.7) as the primary evidence tool.
2. Determine distance from canonical splice site (canonical ±1,2 = strong LOF evidence even without SpliceAI).
3. Assess whether in-frame exon skipping would preserve protein function.
4. Check for cryptic splice site activation in the SpliceAI DS_AG/DS_DG scores.

---

## Output Report Structure

```markdown
# Variant Interpretation Report: {GENE} {VARIANT}

## Executive Summary
- Variant: {HGVS notation}
- Gene: {symbol} | Transcript: {MANE Select}
- Classification: {Pathogenic / Likely Pathogenic / VUS / Likely Benign / Benign}
- Evidence Strength: {strong / moderate / limited}
- Key Finding: {one-sentence summary}

## 1. Variant Identity
{gene, transcript, protein change, consequence, exon/intron location}

## 2. Population Data
{gnomAD: overall AF, ≥3 ancestry AFs, homozygote count}

## 3. Clinical Database Evidence
{ClinVar classification + review status; ClinGen validity level; OMIM associations}

## 4. Computational Predictions
{AlphaMissense, CADD, EVE scores; SpliceAI if applicable}

## 5. Structural Analysis
{Domain, functional site proximity, pLDDT, structural interpretation}

## 6. Literature Evidence
{Functional studies, case reports; flag preprints}

## 7. ACMG Classification
{All evidence codes applied with justification; final classification}

## 8. Clinical Recommendations
{Testing, management, family screening}

## 9. Limitations & Uncertainties
{Missing data, conflicting evidence, data gaps}

## Data Sources
{All tools and databases queried}
```

**Report file naming**: `{GENE}_{VARIANT}_interpretation_report.md`
(Example: `BRCA1_c.5266dupC_interpretation_report.md`)

---

## Clinical Recommendations Framework

**Pathogenic / Likely Pathogenic**:
- Cancer predisposition: Enhanced surveillance, risk-reducing interventions
- Pharmacogenomics: Drug dosing adjustment per guidelines
- Carrier status: Reproductive counseling
- Predictive testing: Cascade family screening

**VUS**:
- Do not use for medical decisions
- Reinterpret in 1-2 years as evidence accumulates
- Seek functional studies if available
- Collect segregation data from family members

**Benign / Likely Benign**:
- Not expected to cause disease
- No cascade family testing needed
- Document in report for completeness

---

## Quantified Minimums

| Section | Minimum Requirement |
|---------|---------------------|
| Population frequency | gnomAD overall + ≥3 ancestry groups |
| Computational predictions | ≥3 predictors (AlphaMissense, CADD, + one more) |
| Literature search | ≥2 search queries with different strategies |
| ACMG codes | All applicable codes listed with justification |

---

## Known Gotchas

- **gnomAD variant format**: Must be `chr-pos-ref-alt` (e.g., `17-41245466-A-G`), not HGVS notation. Using c. notation will fail silently or return no results.
- **OMIM requires API key**: `OMIM_API_KEY` must be set. DisGeNET also requires `DISGENET_API_KEY`. Check before relying on these tools.
- **EVE gene coverage is incomplete**: Always call `EVE_get_gene_info` first to confirm the gene is covered (~3,000 disease genes). Missing EVE score for an uncovered gene is not informative.
- **SpliceAI variant format**: Use `chr{chrom}-{pos}-{ref}-{alt}` or `{chrom}:{pos}:{ref}:{alt}`. The `chr` prefix is important for GRCh38.
- **AlphaMissense requires UniProt ID**, not gene symbol or Ensembl ID. Get the UniProt accession from `UniProt_get_protein_function` or `myvariant_query` before calling AlphaMissense.
- **ClinVar "Conflicting interpretations"**: Do not use directly as evidence in either direction. Extract individual submitter classifications and assess separately.
- **AlphaFold2 via NvidiaNIM**: Rate-limited to 40 RPM. Prediction may take 30-120 seconds. Only predict de novo if AlphaFold DB (`alphafold_get_prediction`) has no entry for the UniProt ID.
- **Preprints via EuropePMC**: BioRxiv and MedRxiv do not have direct search APIs. Use `EuropePMC_search_articles` with `source="PPR"` to search preprints. Always flag preprint findings as NOT peer-reviewed.
- **BA1 stops interpretation**: If gnomAD AF >5% in any population, classify as Benign and do not apply pathogenic codes. Document and close.
- **ClinGen Disputed/Refuted validity**: If ClinGen has refuted a gene-disease association, do not apply any pathogenic criteria. Report the refutation explicitly.
- **COSMIC is somatic context only**: COSMIC data supports somatic variant classification (cancer). It is not direct evidence for germline pathogenicity unless the functional mechanism is shared.
- **myvariant_query parameter**: Use `variant_id=`, not `id=`. Wrong parameter name returns an error.
- **alphafold_get_prediction parameter**: Use `accession=`, not `uniprot=`.

---

## Tool Quick Reference

| Tool | One-Line Purpose |
|------|-----------------|
| `myvariant_query` | Aggregated variant annotations (ClinVar, gnomAD, CADD, dbNSFP) in one call |
| `Ensembl_get_variant_info` | VEP consequence, SIFT, PolyPhen via Ensembl |
| `clinvar_search` | ClinVar classifications and review status |
| `gnomad_search` | Population allele frequencies (ancestry-specific) |
| `OMIM_search` / `OMIM_get_entry` | Gene-disease associations and inheritance |
| `ClinGen_search_gene_validity` | Gene-disease validity level (Definitive to Refuted) |
| `ClinGen_search_dosage_sensitivity` | Haploinsufficiency / triplosensitivity scores |
| `ClinGen_search_actionability` | Clinical actionability for incidental findings |
| `COSMIC_search_mutations` | Somatic mutation frequency and cancer type distribution |
| `DisGeNET_search_gene` | Gene-disease association evidence scores |
| `DisGeNET_get_vda` | Variant-disease associations by rsID |
| `SpliceAI_predict_splice` | Splice-altering delta scores (DS_AG/AL/DG/DL) |
| `SpliceAI_get_max_delta` | Quick triage: max SpliceAI delta score |
| `ChIPAtlas_enrichment_analysis` | TF binding peaks near a gene |
| `ENCODE_search_experiments` | Regulatory element annotations (ATAC-seq, H3K27ac, etc.) |
| `CADD_get_variant_score` | CADD PHRED deleteriousness score |
| `AlphaMissense_get_variant_score` | DeepMind missense pathogenicity score |
| `EVE_get_variant_score` | Evolutionary variant effect score |
| `EVE_get_gene_info` | Check if gene has EVE coverage |
| `PDB_search_by_uniprot` | Find experimental protein structures |
| `alphafold_get_prediction` | Get AlphaFold DB predicted structure |
| `NvidiaNIM_alphafold2` | Predict protein structure de novo (40 RPM limit) |
| `InterPro_get_protein_domains` | Domain annotations and boundaries |
| `UniProt_get_protein_function` | Functional sites, active/binding residues |
| `GTEx_get_median_gene_expression` | Bulk tissue expression (TPM) |
| `CELLxGENE_get_expression_data` | Cell-type-specific single-cell expression |
| `PubMed_search` | Peer-reviewed literature search |
| `EuropePMC_search_articles` | Literature + preprints (use `source="PPR"` for preprints) |
| `openalex_search_works` | Literature search with citation metrics |
| `SemanticScholar_search_papers` | AI-ranked literature search |

---

## See Also

- `CHECKLIST.md` — Pre-delivery verification checklist
- `EXAMPLES.md` — Sample variant interpretations
- `TOOLS_REFERENCE.md` — Detailed tool parameters (legacy)
- `references/tools.md` — Detailed parameter tables, score thresholds, fallback chains
