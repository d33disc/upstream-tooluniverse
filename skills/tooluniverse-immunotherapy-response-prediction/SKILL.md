---
name: tooluniverse-immunotherapy-response-prediction
description: Predict patient response to immune checkpoint inhibitors (ICIs) using multi-biomarker integration. Given a cancer type, somatic mutations, and optional biomarkers (TMB, PD-L1, MSI status), performs systematic analysis across 11 phases covering TMB classification, neoantigen burden estimation, MSI/MMR assessment, PD-L1 evaluation, immune microenvironment profiling, mutation-based resistance/sensitivity prediction, clinical evidence retrieval, and multi-biomarker score integration. Generates a quantitative ICI Response Score (0-100), response likelihood tier, specific ICI drug recommendations with evidence, resistance risk factors, and a monitoring plan. Use when oncologists ask about immunotherapy eligibility, checkpoint inhibitor selection, or biomarker-guided ICI treatment decisions.
---

# Immunotherapy Response Prediction

Transforms a tumor profile (cancer type + mutations + biomarkers) into a quantitative ICI Response Score with drug-specific recommendations, resistance risk assessment, and monitoring plan.

**KEY PRINCIPLES**:
1. **Report-first** — create report file first, populate progressively
2. **Evidence-graded** — every finding has a tier (T1–T4)
3. **Quantitative** — ICI Response Score (0–100) with component breakdown
4. **Cancer-specific** — thresholds and predictions are cancer-type adjusted
5. **Multi-biomarker** — integrate TMB + MSI + PD-L1 + neoantigen + mutations
6. **Resistance-aware** — always check STK11, PTEN, JAK1/2, B2M
7. **Drug-specific** — recommend specific ICI agents with evidence
8. **English-first** — always use English terms in tool calls

---

## When to Use

- "Will this patient respond to immunotherapy?"
- "Should I give pembrolizumab to this melanoma patient?"
- "Patient has NSCLC with TMB 25, PD-L1 80% — predict ICI response"
- "MSI-high colorectal cancer — which checkpoint inhibitor?"
- "Low TMB NSCLC with STK11 mutation — should I try immunotherapy?"
- "Compare pembrolizumab vs nivolumab for this patient profile"

---

## Input Parsing

**Required**: Cancer type + at least one of: mutation list OR TMB value
**Optional**: PD-L1 expression, MSI status, immune infiltration data, HLA type, prior treatments, intended ICI

| Format | Example | Parse As |
|--------|---------|----------|
| Cancer + mutations | "Melanoma, BRAF V600E, TP53 R273H" | cancer=melanoma, mutations=[BRAF V600E, TP53 R273H] |
| Cancer + TMB | "NSCLC, TMB 25 mut/Mb" | cancer=NSCLC, tmb=25 |
| Cancer + full profile | "Melanoma, BRAF V600E, TMB 15, PD-L1 50%, MSS" | cancer=melanoma, mutations=[BRAF V600E], tmb=15, pdl1=50, msi=MSS |
| Cancer + MSI status | "Colorectal cancer, MSI-high" | cancer=CRC, msi=MSI-H |
| Resistance query | "NSCLC, TMB 2, STK11 loss, PD-L1 <1%" | cancer=NSCLC, tmb=2, mutations=[STK11 loss], pdl1=0 |

**Cancer type aliases**: NSCLC → non-small cell lung carcinoma, CRC → colorectal cancer, RCC → renal cell carcinoma, HNSCC → head and neck squamous cell carcinoma, UC/bladder → urothelial carcinoma, HCC → hepatocellular carcinoma, TNBC → triple-negative breast cancer, GEJ → gastroesophageal junction cancer

**Gene symbol aliases**: PD-L1 → CD274, PD-1 → PDCD1, CTLA-4 → CTLA4, HER2 → ERBB2, MSH2/MLH1/MSH6/PMS2 → MMR genes

---

## Abbreviated Tool Reference

Full parameter signatures and response shapes: `references/tools.md`

| Tool | Key Parameters | Purpose |
|------|---------------|---------|
| `OpenTargets_get_disease_id_description_by_name` | `diseaseName` | Cancer → EFO ID |
| `MyGene_query_genes` | `query` (NOT `q`) | Gene → Ensembl/Entrez IDs |
| `fda_pharmacogenomic_biomarkers` | `drug_name`, `biomarker`, `limit` | FDA biomarker approvals (TMB-H, MSI-H) |
| `HPA_get_cancer_prognostics_by_gene` | `gene_name` | Immune gene prognostic data |
| `HPA_get_rna_expression_by_source` | `gene_name`, `source_type`, `source_name` (ALL 3) | Baseline expression |
| `OpenTargets_get_associated_drugs_by_disease_efoId` | `efoId`, `size` | ICI drugs for cancer type |
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | `chemblId` | Drug MOA confirmation |
| `FDA_get_indications_by_drug_name` | `drug_name`, `limit` | FDA-approved indications |
| `clinical_trials_search` | `action='search_studies'`, `condition`, `intervention`, `limit` | Active ICI trials |
| `PubMed_search_articles` | `query`, `max_results` | Literature evidence |
| `civic_search_evidence_items` | `therapy_name`, `disease_name` | CIViC predictive evidence |
| `enrichr_gene_enrichment_analysis` | `gene_list` (array), `libs` (array) | Immune pathway enrichment |
| `UniProt_get_function_by_accession` | `accession` | Protein function / domain context |
| `iedb_search_epitopes` | `organism_name`, `source_antigen_name` | Known T-cell epitopes |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | `query`, `case_sensitive`, `exact_match`, `limit` (ALL 4) | DrugBank drug info |

---

## Known Gotchas

- `MyGene_query_genes` uses `query=`, NOT `q=`. Using `q=` silently returns no results.
- `EnsemblVEP_annotate_rsid` uses `variant_id=`, NOT `rsid=`.
- `cBioPortal_get_mutations`: `gene_list` must be a **string** (e.g. `"BRAF"`), not an array.
- All `drugbank_*` tools require exactly 4 params: `query`, `case_sensitive`, `exact_match`, `limit`. Omitting any causes failure.
- `ensembl_lookup_gene` requires `species='homo_sapiens'` alongside `gene_id`. Omitting species causes an error.
- `cBioPortal_get_cancer_studies` takes no keyword/filter parameters.
- `civic_get_variants_by_gene` requires the CIViC numeric gene ID, not Entrez ID.
- `civic_search_variants` and `civic_search_evidence_items` may return many unrelated entries — always filter results manually.
- `HPA_get_rna_expression_by_source` requires all three of `gene_name`, `source_type`, and `source_name`.
- `enrichr_gene_enrichment_analysis`: `libs` is required even though it may appear optional. Omitting it causes failure.
- RCC is ICI-responsive despite low TMB. Do not downgrade RCC solely on TMB.
- CRC (MSS) has <5% ORR with ICI monotherapy. Ensure MSI status is assessed before recommending ICI.
- MDM2/MDM4 amplification is associated with hyperprogression risk under ICI — flag explicitly.
- EGFR/ALK-positive NSCLC: targeted therapy is preferred over ICI; ICI may have worse outcomes.
- PD-L1 scoring method varies by cancer: TPS for NSCLC, CPS for HNSCC/Gastric/TNBC/Bladder.
- `FDA_get_boxed_warning_info_by_drug_name` may return `NOT_FOUND` for some drugs — handle gracefully.

---

## Workflow Overview

```
Phase 1  → Input Standardization & Cancer Context
Phase 2  → TMB Analysis
Phase 3  → Neoantigen Burden Estimation
Phase 4  → MSI/MMR Status Assessment
Phase 5  → PD-L1 Expression Analysis
Phase 6  → Immune Microenvironment Profiling
Phase 7  → Mutation-Based Predictors (resistance + sensitivity)
Phase 8  → Clinical Evidence & ICI Options
Phase 9  → Resistance Risk Assessment
Phase 10 → Multi-Biomarker Score Integration
Phase 11 → Clinical Recommendations & Report
```

---

## Phase 1: Input Standardization & Cancer Context

**Step 1.1 — Resolve cancer type.** Call `OpenTargets_get_disease_id_description_by_name` with the cancer name to obtain its EFO ID. Store this ID for use in later OpenTargets calls.

**Cancer-specific ICI context** (use as hardcoded baseline):

| Cancer | EFO ID | Baseline ORR | Key Biomarkers | FDA-Approved ICIs |
|--------|--------|-------------|----------------|-------------------|
| Melanoma | EFO_0000756 | 30–45% | TMB, PD-L1 | pembro, nivo, ipi, nivo+ipi |
| NSCLC | EFO_0003060 | 15–50% (PD-L1 dep.) | PD-L1, TMB, STK11 | pembro, nivo, atezo, durva, cemiplimab |
| Bladder/UC | EFO_0000292 | 15–25% | PD-L1, TMB | pembro, nivo, atezo, avelumab, durva |
| RCC | EFO_0000681 | 25–40% | PD-L1 | nivo, pembro, nivo+ipi |
| HNSCC | EFO_0000181 | 15–20% | PD-L1 CPS | pembro, nivo |
| MSI-H (any) | — | 30–50% | MSI, dMMR | pembro (tissue-agnostic) |
| TMB-H (any) | — | 20–30% | TMB >=10 | pembro (tissue-agnostic) |
| CRC (MSI-H) | EFO_0000365 | 30–50% | MSI, dMMR | pembro, nivo, nivo+ipi |
| CRC (MSS) | EFO_0000365 | <5% | Generally resistant | Not generally recommended |
| HCC | EFO_0000182 | 15–20% | PD-L1 | atezo+bev, durva+treme |
| TNBC | EFO_0005537 | 10–20% | PD-L1 CPS | pembro+chemo |
| Gastric/GEJ | EFO_0000178 | 10–20% | PD-L1 CPS, MSI | pembro, nivo |

**Step 1.2 — Parse mutations.** Structured format: gene, variant, type (missense / frameshift / nonsense / loss / amplification).

**Step 1.3 — Resolve gene IDs.** For each gene in the mutation list, call `MyGene_query_genes` with `query=<gene_symbol>` to obtain Ensembl and Entrez IDs.

---

## Phase 2: TMB Analysis

**Step 2.1 — Classify TMB.**

| TMB Range (mut/Mb) | Class | Score |
|--------------------|-------|-------|
| >= 20 | TMB-High | 30 pts |
| 10–19.9 | TMB-Intermediate | 20 pts |
| 5–9.9 | TMB-Low | 10 pts |
| < 5 | TMB-Very-Low | 5 pts |

If only a mutation list is provided (no numeric TMB), estimate from count, and flag: "estimated from provided mutations — clinical TMB testing recommended."

**Step 2.2 — Check FDA TMB-H approval.** Call `fda_pharmacogenomic_biomarkers` with `drug_name='pembrolizumab'` and scan for "Tumor Mutational Burden" in the Biomarker field. Pembrolizumab is approved tissue-agnostically for TMB-H (>=10 mut/Mb).

**Step 2.3 — Apply cancer-specific context.** RCC is ICI-responsive even with low TMB; do not apply a low-TMB penalty for RCC. Melanoma has high baseline UV-induced TMB — calibrate expectations accordingly.

| Cancer | Typical Range | High-TMB Threshold |
|--------|-------------|-------------------|
| Melanoma | 5–50+ | >20 |
| NSCLC | 2–30 | >10 |
| Bladder | 5–25 | >10 |
| CRC (MSI-H) | 20–100+ | >10 |
| CRC (MSS) | 2–10 | >10 |
| RCC | 1–8 | >10 (less predictive) |
| HNSCC | 2–15 | >10 |

---

## Phase 3: Neoantigen Burden Estimation

**Step 3.1 — Estimate neoantigen count from mutation types.**

- Missense mutations: ~30% chance of generating a neoantigen each
- Frameshift mutations: high potential (novel peptides); weight 1.5×
- Nonsense / splice-site: moderate potential

Formula: `estimated_neoantigens ≈ (missense_count × 0.3) + (frameshift_count × 1.5)`

| Estimated Count | Class | Score |
|----------------|-------|-------|
| >50 | High | 15 pts |
| 20–50 | Moderate | 10 pts |
| <20 | Low | 5 pts |

**Step 3.2 — Assess neoantigen quality.** Call `UniProt_get_function_by_accession` for the mutated protein. Mutations in kinase domains or surface-exposed regions have higher MHC-presentation potential. POLE/POLD1 mutations indicate ultramutated phenotype → ultra-high neoantigen load.

**Step 3.3 — Check known epitopes.** Call `iedb_search_epitopes` with `organism_name='homo sapiens'` and `source_antigen_name=<protein>` to find known T-cell epitopes for mutated proteins.

---

## Phase 4: MSI/MMR Status Assessment

**Step 4.1 — Classify MSI status.**

| Status | Score |
|--------|-------|
| MSI-H / dMMR | 25 pts |
| MSS / pMMR | 5 pts |
| Unknown | 10 pts (neutral) |

**Step 4.2 — Check for MMR gene mutations.** If mutations include MLH1, MSH2, MSH6, PMS2, or EPCAM but no MSI status is given, flag: "possible MSI-H — recommend testing."

**Step 4.3 — Confirm FDA MSI-H approvals.** Call `fda_pharmacogenomic_biomarkers` with `biomarker='Microsatellite Instability'` to retrieve approved drugs. Key approvals: pembrolizumab (tissue-agnostic), nivolumab (CRC), dostarlimab (dMMR solid tumors).

---

## Phase 5: PD-L1 Expression Analysis

**Step 5.1 — Classify PD-L1.**

| PD-L1 Level | Score |
|-------------|-------|
| >= 50% TPS | 20 pts |
| 1–49% TPS | 12 pts |
| < 1% TPS | 5 pts |
| Unknown | 10 pts (neutral) |

**Step 5.2 — Apply cancer-specific scoring method.**

| Cancer | Method | Monotherapy Threshold |
|--------|--------|----------------------|
| NSCLC | TPS | >=50% first-line mono; >=1% post-chemo |
| Melanoma | Not required | ICI recommended regardless |
| Bladder | CPS or IC | CPS>=10 preferred |
| HNSCC | CPS | CPS>=20 monotherapy; CPS>=1 combo |
| Gastric | CPS | CPS>=1 |
| TNBC | CPS | CPS>=10 |

**Step 5.3 — Get baseline expression.** Call `HPA_get_cancer_prognostics_by_gene` with `gene_name='CD274'` for PD-L1 prognostic context by cancer type.

---

## Phase 6: Immune Microenvironment Profiling

**Step 6.1 — Query immune gene expression.** Call `HPA_get_cancer_prognostics_by_gene` for each key immune marker: CD274, PDCD1, CTLA4, LAG3, HAVCR2, TIGIT, CD8A, CD8B, GZMA, GZMB, PRF1, IFNG.

**Step 6.2 — Classify tumor immune phenotype.**

| Phenotype | Characteristics | ICI Likelihood |
|-----------|-----------------|----------------|
| Hot (T cell inflamed) | High CD8+, IFN-g, PD-L1+ | High |
| Cold (immune desert) | Low immune infiltration | Low |
| Immune excluded | Immune cells at margin only | Moderate |
| Immune suppressed | High Tregs/MDSCs | Low–Moderate |

**Step 6.3 — Pathway enrichment (if mutation list available).** Call `enrichr_gene_enrichment_analysis` with the immune-related gene list and `libs=['KEGG_2021_Human', 'Reactome_2022']` to identify activated or suppressed immune pathways.

---

## Phase 7: Mutation-Based Predictors

**Step 7.1 — Resistance mutations (apply penalties).**

| Gene | Context | Mechanism | Penalty |
|------|---------|-----------|---------|
| STK11/LKB1 loss | NSCLC (esp. KRAS+) | Immune exclusion, cold TME | −10 pts |
| PTEN loss | Multiple | Reduced T cell infiltration | −5 pts |
| JAK1 loss-of-function | Multiple | IFN-g signaling loss | −10 pts |
| JAK2 loss-of-function | Multiple | IFN-g signaling loss | −10 pts |
| B2M loss/mutation | Multiple | MHC-I loss, immune escape | −15 pts |
| KEAP1 loss | NSCLC | Oxidative stress, cold TME | −5 pts |
| MDM2 amplification | Multiple | Hyperprogression risk | −5 pts |
| MDM4 amplification | Multiple | Hyperprogression risk | −5 pts |
| EGFR activating | NSCLC | Low TMB, cold TME | −5 pts |

**Step 7.2 — Sensitivity mutations (apply bonuses).**

| Gene | Context | Mechanism | Bonus |
|------|---------|-----------|-------|
| POLE exonuclease domain | Any | Ultramutation, high neoantigens | +10 pts |
| POLD1 proofreading domain | Any | Ultramutation | +5 pts |
| BRCA1/2 loss-of-function | Multiple | Genomic instability | +3 pts |
| ARID1A loss-of-function | Multiple | Chromatin remodeling, TME | +3 pts |
| PBRM1 loss-of-function | RCC only | ICI response in RCC | +5 pts |

**Step 7.3 — DDR pathway check.** Mutations in ATM, ATR, CHEK1, CHEK2, BRCA1, BRCA2, PALB2, RAD50 are associated with elevated TMB and improved ICI response. Flag and add to sensitivity context.

**Step 7.4 — Driver mutation ICI context.** Call `OpenTargets_get_associated_drugs_by_disease_efoId` with the cancer EFO ID to retrieve known ICI associations. Filter results for checkpoint inhibitors.

---

## Phase 8: Clinical Evidence & ICI Options

**Step 8.1 — Retrieve FDA indications.** For each relevant ICI (pembrolizumab, nivolumab, atezolizumab, durvalumab, ipilimumab, avelumab, cemiplimab), call `FDA_get_indications_by_drug_name` and extract cancer-specific approved indications.

**Step 8.2 — ICI drug profiles.**

| Drug | Target | Key Indications |
|------|--------|-----------------|
| Pembrolizumab | PD-1 | Melanoma, NSCLC, HNSCC, Bladder, MSI-H, TMB-H, many others |
| Nivolumab | PD-1 | Melanoma, NSCLC, RCC, CRC (MSI-H), HCC, HNSCC |
| Atezolizumab | PD-L1 | NSCLC, Bladder, HCC, Melanoma |
| Durvalumab | PD-L1 | NSCLC (Stage III), Bladder, HCC, BTC |
| Ipilimumab | CTLA-4 | Melanoma, RCC (combo), CRC MSI-H (combo) |
| Avelumab | PD-L1 | Merkel cell, Bladder (maintenance) |
| Cemiplimab | PD-1 | CSCC, NSCLC, Basal cell |
| Dostarlimab | PD-1 | dMMR endometrial, dMMR solid tumors |
| Tremelimumab | CTLA-4 | HCC (combo with durvalumab) |

**Step 8.3 — Clinical trial evidence.** Call `clinical_trials_search` with `action='search_studies'`, the cancer type as `condition`, and the candidate ICI as `intervention` to find supporting trials and ORR data.

**Step 8.4 — Literature evidence.** Call `PubMed_search_articles` with a query combining the cancer type, ICI drug name, and relevant biomarker (e.g. "pembrolizumab melanoma TMB response biomarker") to retrieve supporting publications.

**Step 8.5 — Confirm drug mechanism.** Call `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` using the ChEMBL ID to confirm the molecular target. Key ICI ChEMBL IDs: pembrolizumab CHEMBL3137343, nivolumab CHEMBL2108738, atezolizumab CHEMBL3707227, ipilimumab CHEMBL1789844.

---

## Phase 9: Resistance Risk Assessment

**Step 9.1 — CIViC resistance evidence.** Call `civic_search_evidence_items` with `therapy_name=<ici_name>` and optionally `disease_name=<cancer>`. Filter results for resistance-type evidence. Note: CIViC filtering is imprecise — manually review returned nodes.

**Step 9.2 — Pathway-level resistance check.**

| Pathway | Mechanism | Genes to Check |
|---------|-----------|---------------|
| IFN-g signaling | Loss of IFN-g response | JAK1, JAK2, STAT1, IRF1 |
| Antigen presentation | MHC-I downregulation | B2M, TAP1, TAP2, HLA-A/B/C |
| WNT/beta-catenin | T cell exclusion | CTNNB1 activating mutations |
| MAPK | Immune suppression | MEK/ERK hyperactivation |
| PI3K/AKT/mTOR | Immune suppression | PTEN loss, PIK3CA |

**Step 9.3 — Summarize resistance risk.**

- **Low**: No resistance mutations, favorable TME
- **Moderate**: 1 resistance factor OR uncertain TME
- **High**: Multiple resistance mutations OR known resistant phenotype (e.g. CRC MSS, EGFR+ NSCLC)

---

## Phase 10: Multi-Biomarker Score Integration

**Score formula:**

```
ICI Response Score = TMB_score + MSI_score + PDL1_score + Neoantigen_score
                     + Mutation_bonus − Resistance_penalty

  TMB_score:          5–30 pts
  MSI_score:          5–25 pts
  PDL1_score:         5–20 pts
  Neoantigen_score:   5–15 pts
  Mutation_bonus:     0–10 pts  (POLE, PBRM1, DDR genes)
  Resistance_penalty: 0–20 pts  (STK11, PTEN, JAK1/2, B2M, etc.)

  Floor: 0  |  Ceiling: 100
```

**Response tiers:**

| Score | Tier | Expected ORR | Action |
|-------|------|-------------|--------|
| 70–100 | HIGH | 50–80% | Strong ICI candidate; monotherapy or combo |
| 40–69 | MODERATE | 20–50% | Consider ICI; combo preferred; monitor closely |
| 0–39 | LOW | <20% | ICI alone unlikely effective; consider alternatives |

**Confidence level:**

| Biomarkers Available | Confidence |
|----------------------|-----------|
| TMB + MSI + PD-L1 + mutations | HIGH |
| 3 of 4 | MODERATE-HIGH |
| 2 of 4 | MODERATE |
| 1 only | LOW |
| Cancer type only | VERY LOW |

---

## Phase 11: Clinical Recommendations

**Step 11.1 — ICI drug selection logic.**

- **MSI-H**: Pembrolizumab (tissue-agnostic). Also nivolumab (CRC-specific). Consider nivo+ipi combo.
- **TMB-H (>=10), not MSI-H**: Pembrolizumab (tissue-agnostic TMB-H approval).
- **Melanoma**: PD-L1 >=1% → pembrolizumab or nivolumab monotherapy. PD-L1 <1% → nivo+ipi. BRAF V600E → discuss targeted therapy first if rapid response needed.
- **NSCLC**: PD-L1 >=50% + no STK11/EGFR → pembrolizumab monotherapy (KEYNOTE-024). PD-L1 1–49% → pembrolizumab + chemo. PD-L1 <1% → ICI + chemo. STK11 loss → ICI less likely effective. EGFR/ALK+ → targeted therapy preferred.
- **RCC**: Nivo+ipi (IMDC intermediate/poor risk); pembrolizumab+axitinib (all risk).
- **Bladder**: Pembrolizumab or atezolizumab (2L); avelumab maintenance post-platinum.

**Step 11.2 — Monitoring plan.**

During ICI treatment, track:
- Tumor response (CT/MRI every 8–12 weeks)
- ctDNA (early response signal at 4–6 weeks)
- Immune-related adverse events (irAEs)
- Thyroid function (TSH every 6 weeks)
- Liver function (every 2–4 weeks initially)
- Cortisol if symptomatic adrenal insufficiency suspected

**Step 11.3 — Alternatives if ICI response predicted LOW.**
1. Targeted therapy (if actionable: BRAF, EGFR, ALK, ROS1)
2. Chemotherapy (standard of care)
3. ICI + chemotherapy combination
4. ICI + anti-angiogenic (may convert cold → hot tumor)
5. ICI + CTLA-4 doublet (nivo + ipi)
6. Clinical trial enrollment (novel combinations)

---

## Output Report Format

Save as `immunotherapy_response_prediction_{cancer_type}.md`. Required sections:

1. **Executive Summary** — 2–3 sentences: cancer, score, recommendation
2. **ICI Response Score: XX/100** — Tier (HIGH/MODERATE/LOW), Confidence, Expected ORR
3. **Score Breakdown table** — TMB (max 30) + MSI (max 25) + PD-L1 (max 20) + Neoantigen (max 15) + Bonus (max 10) − Penalty (max −20) = TOTAL
4. **Patient Profile** — cancer, mutations, TMB, MSI, PD-L1
5. **Biomarker Analysis** — TMB, MSI/MMR, PD-L1, Neoantigen subsections
6. **Mutation Analysis** — Driver / Resistance / Sensitivity subsections with score impact
7. **Immune Microenvironment** — hot/cold phenotype + immune gene data
8. **ICI Drug Recommendation** — primary drug, evidence tier, ORR, key trial/NCT#; alternatives; combinations
9. **Resistance Risk** — LOW/MODERATE/HIGH + factors + mitigation
10. **Monitoring Plan** — response schedule, ctDNA, irAE monitoring
11. **Alternative Strategies** — for low-score cases: targeted, chemo, trials
12. **Evidence Grading table** — Finding | Tier (T1–T4) | Source tool/DB
13. **Data Completeness table** — each biomarker: Provided/Estimated/Unknown + points used
14. **Missing Data Recommendations** — tests to improve prediction accuracy

*Footer*: Sources: OpenTargets, CIViC, FDA, DrugBank, PubMed, IEDB, HPA, cBioPortal

---

## Evidence Tiers

| Tier | Description | Source Examples |
|------|-------------|----------------|
| T1 | FDA-approved biomarker/indication | FDA labels, NCCN guidelines |
| T2 | Phase 2–3 clinical trial evidence | Published trial data, PubMed |
| T3 | Preclinical/computational evidence | Pathway analysis, in vitro data |
| T4 | Expert opinion/case reports | Case series, reviews |

---

## Use Case Examples

| Input | Expected Score | Tier | Primary Recommendation |
|-------|--------------|------|----------------------|
| NSCLC, TMB 25, PD-L1 80%, no STK11 | 70–85 | HIGH | Pembrolizumab monotherapy (KEYNOTE-024) |
| Melanoma, BRAF V600E, TMB 15, PD-L1 50% | 50–65 | MODERATE | Discuss ICI vs BRAF-targeted; ICI remains reasonable |
| CRC, MSI-high, TMB 40 | 80–95 | HIGH | Pembrolizumab first-line |
| NSCLC, TMB 2, PD-L1 <1%, STK11 loss | 5–20 | LOW | Chemotherapy preferred; ICI unlikely effective |
| Bladder, TMB 12, PD-L1 10%, no resistance | 45–55 | MODERATE | ICI+chemo or avelumab maintenance |
| NSCLC, PD-L1 90% (ICI selection query) | 65–80 | HIGH | Pembrolizumab monotherapy first-line |

---

## Completeness Checklist

Before finalizing, confirm:

- [ ] Cancer type resolved to EFO ID
- [ ] All mutations parsed; genes resolved to Ensembl/Entrez IDs
- [ ] TMB classified with cancer-specific context
- [ ] MSI/MMR status assessed (or flagged for testing)
- [ ] PD-L1 integrated (or marked unknown with neutral score)
- [ ] Neoantigen burden estimated
- [ ] Resistance mutations checked: STK11, PTEN, JAK1, JAK2, B2M, KEAP1, MDM2, MDM4
- [ ] Sensitivity mutations checked: POLE, POLD1, PBRM1, DDR genes
- [ ] FDA-approved ICIs identified for this cancer
- [ ] Clinical trial evidence retrieved
- [ ] ICI Response Score calculated with full component breakdown
- [ ] Drug recommendation provided with evidence tier
- [ ] Monitoring plan included
- [ ] Alternatives documented for low-score cases
- [ ] Evidence grading applied to all findings
- [ ] Data completeness table filled
- [ ] Missing data recommendations provided
- [ ] Report saved to file
