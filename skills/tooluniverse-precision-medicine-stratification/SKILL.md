---
name: tooluniverse-precision-medicine-stratification
description: Comprehensive patient stratification for precision medicine by integrating genomic, clinical, and therapeutic data. Given a disease/condition, genomic data (germline variants, somatic mutations, expression), and optional clinical parameters, performs multi-phase analysis across 9 phases covering disease disambiguation, genetic risk assessment, disease-specific molecular stratification, pharmacogenomic profiling, comorbidity/DDI risk, pathway analysis, clinical evidence and guideline mapping, clinical trial matching, and integrated outcome prediction. Generates a quantitative Precision Medicine Risk Score (0-100) with risk tier assignment (Low/Intermediate/High/Very High), treatment algorithm (1st/2nd/3rd line), pharmacogenomic guidance, clinical trial matches, and monitoring plan. Use when clinicians ask about patient risk stratification, treatment selection, prognosis prediction, or personalized therapeutic strategy across cancer, metabolic, cardiovascular, neurological, or rare diseases.
---

# Precision Medicine Patient Stratification

Transform patient genomic and clinical profiles into actionable risk stratification, treatment recommendations, and personalized therapeutic strategies. Integrates germline genetics, somatic alterations, pharmacogenomics, pathway biology, and clinical evidence to produce a quantitative risk score with tiered management recommendations.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Disease-specific logic** - Cancer vs metabolic vs rare disease pipelines diverge at Phase 3
3. **Multi-level integration** - Germline + somatic + expression + clinical data layers
4. **Evidence-graded** - Every finding has an evidence tier (T1-T4)
5. **Quantitative output** - Precision Medicine Risk Score (0-100) with transparent components
6. **Pharmacogenomic guidance** - Drug selection AND dosing recommendations
7. **Guideline-concordant** - Reference NCCN, ACC/AHA, ADA, and other guidelines
8. **Source-referenced** - Every statement cites the tool/database source
9. **Completeness checklist** - Mandatory section showing data availability and analysis coverage
10. **English-first queries** - Always use English terms in tool calls. Respond in user's language

---

## When to Use

Apply when user asks about risk stratification, treatment selection, prognosis, or personalized therapeutic strategy for:
- Cancer patients with genomic profiling (e.g., "NSCLC, EGFR L858R, stage IV")
- Metabolic disease with PGx concerns (e.g., "T2D, CYP2C19 poor metabolizer")
- CVD risk with genetic data (e.g., "LDL 190, SLCO1B1*5, family hx MI")
- Rare/monogenic disease (e.g., "Marfan, FBN1 c.4082G>A")
- Neurological risk (e.g., "Alzheimer risk, APOE e4/e4")

**NOT for** single-purpose tasks: use `tooluniverse-variant-interpretation`, `tooluniverse-immunotherapy-response-prediction`, `tooluniverse-adverse-event-detection`, `tooluniverse-drug-drug-interaction`, `tooluniverse-polygenic-risk-score`, or `tooluniverse-clinical-trial-matching` instead.

---

## Input Parsing

**Required**: Disease/condition name + at least one of: germline variants, somatic mutations, gene list, or clinical biomarkers.

**Strongly recommended**: Specific variants (e.g., "BRCA1 c.68_69delAG"), age/sex/stage, key biomarkers (HbA1c, PSA, LDL-C).

**Optional** (improves stratification): Comorbidities, prior treatments, family history, ethnicity, current medications.

### Disease Type Classification

| Category | Examples | Key Stratification Axes |
|----------|----------|------------------------|
| **CANCER** | Breast, lung, colorectal, melanoma, prostate | Stage, molecular subtype, TMB, driver mutations |
| **METABOLIC** | T2D, obesity, NAFLD | HbA1c, BMI, genetic risk, CYP genotypes |
| **CARDIOVASCULAR** | CAD, heart failure, AF, hypertension | ASCVD risk, LDL, statin/anticoagulant PGx |
| **NEUROLOGICAL** | Alzheimer, Parkinson, epilepsy | APOE status, genetic risk, anticonvulsant PGx |
| **RARE/MONOGENIC** | Marfan, CF, sickle cell, Huntington | Causal variant, penetrance, genotype-phenotype |
| **AUTOIMMUNE** | RA, lupus, Crohn's | HLA associations, biologic PGx |

### Gene Symbol Normalization

HER2 = ERBB2, PD-L1 = CD274. Always use official HGNC symbols in tool calls. CYP genes, VKORC1, SLCO1B1, DPYD, UGT1A1, TPMT are already official. APOE, LDLR, PCSK9, FBN1, CFTR require no aliasing.

---

## Workflow Overview

```
Phase 1: Disease Disambiguation & Profile Standardization
Phase 2: Genetic Risk Assessment
Phase 3: Disease-Specific Molecular Stratification  <-- routes by disease type
Phase 4: Pharmacogenomic Profiling
Phase 5: Comorbidity & Drug Interaction Risk
Phase 6: Molecular Pathway Analysis
Phase 7: Clinical Evidence & Guidelines
Phase 8: Clinical Trial Matching
Phase 9: Integrated Scoring & Recommendations
```

Detailed tool parameters are in `TOOLS_REFERENCE.md`. For API quirks, see **Known Gotchas** below.

---

## Phase 1: Disease Disambiguation & Profile Standardization

**Goal**: Resolve disease to a standard ontology ID, classify its type, parse all genomic inputs, and resolve gene IDs.

**Steps**:

1. **Resolve disease to EFO ID** - Call `OpenTargets_get_disease_id_description_by_name` with the disease name. Extract the EFO/MONDO/Orphanet ID from `data.search.hits[0].id`.

2. **Classify disease type** - Based on disease name and EFO ID, assign: CANCER / METABOLIC / CVD / NEUROLOGICAL / RARE / AUTOIMMUNE. This determines Phase 3 routing.

3. **Parse genomic data** - Structure each variant as `{gene, variant, type}`. Examples:
   - `"BRCA1 c.68_69delAG"` → frameshift in BRCA1
   - `"CYP2C19 *2/*2"` → poor metabolizer genotype
   - `"APOE e4/e4"` → highest AD risk genotype

4. **Resolve gene IDs** - Call `MyGene_query_genes` for each gene. Extract Ensembl ID from `hits[0].ensembl.gene` and Entrez ID from `hits[0]._id`. Filter results by `symbol` match — first hit may be a LOC gene, not the target.

**Common EFO IDs** (avoid redundant lookup): breast cancer = EFO_0000305, NSCLC = EFO_0003060, CRC = EFO_0000365, melanoma = EFO_0000756, T2D = EFO_0001360, CAD = EFO_0001645, Alzheimer = MONDO_0004975, Marfan = Orphanet_558.

---

## Phase 2: Genetic Risk Assessment

**Goal**: Assess pathogenicity of provided variants and overall genetic risk load.

**Steps**:

1. **Germline pathogenicity** - For each germline variant: call `clinvar_search_variants` (gene + significance) and/or `EnsemblVEP_annotate_rsid` (for rsIDs) or `EnsemblVEP_annotate_hgvs` (for HGVS notation, requires `species='homo_sapiens'`). VEP returns SIFT/PolyPhen predictions and consequence type.

2. **Gene-disease association strength** - Call `OpenTargets_target_disease_evidence` with Ensembl ID + EFO ID to get evidence items and scores for the specific gene-disease pair.

3. **GWAS-based polygenic risk** - Call `gwas_get_associations_for_trait` with disease name, or `GWAS_search_associations_by_gene` per gene. If GWAS data is sparse, use `OpenTargets_search_gwas_studies_by_disease` with `diseaseIds` as an array.

4. **Population frequency** - Call `gnomad_get_variant` with variant ID for allele frequency across populations. High frequency (>1%) suggests benign.

5. **Gene constraint** - Call `gnomad_get_gene_constraints` for pLI and LOEUF scores. High pLI (>0.9) or low LOEUF indicates haploinsufficiency.

**Pathogenicity → score points**: Pathogenic = 25, Likely pathogenic = 20, VUS = 10, Likely benign = 2, Benign = 0.

**Genetic Risk Score Component (0-35 pts)**: Pathogenic variant in high-penetrance gene = 30-35 pts; high PRS (>90th percentile) = 25-30 pts; single moderate-risk variant = 12-18 pts; VUS = 8-12 pts; low genetic risk = 0-5 pts.

---

## Phase 3: Disease-Specific Molecular Stratification

Routes by disease type classified in Phase 1.

### CANCER PATH (3C)

1. **Molecular subtyping** - Identify driver mutations, receptor status (ER/PR/HER2 for breast), and key biomarkers. Use `cBioPortal_get_mutations` (pass `gene_list` as a space-separated STRING, not array) to assess somatic mutation landscape in the relevant TCGA study. Use `HPA_get_cancer_prognostics_by_gene` for prognostic data.

2. **TMB/MSI/HRD assessment** - If TMB >= 10 mut/Mb: pembrolizumab-eligible (tissue-agnostic). If MSI-H/dMMR: pembrolizumab/nivolumab-eligible. If HRD-positive: PARP inhibitor-eligible. Verify with `fda_pharmacogenomic_biomarkers`.

3. **Prognostic stratification** - Combine clinical stage with molecular features. Stage IV = 25-30 clinical points regardless of molecular. Stage I-II with favorable subtype = 5-18 points.

**Cancer subtype-to-treatment mapping**:
- Breast: Luminal A/B (ER/PR+, HER2-) → endocrine therapy; HER2+ → anti-HER2 therapy; TNBC → chemotherapy ± immunotherapy; BRCA+ → PARP inhibitor eligible
- NSCLC: EGFR mutation → EGFR TKI (osimertinib first-line); ALK/ROS1 → ALK/ROS1 inhibitor; KRAS G12C → sotorasib/adagrasib; high PD-L1 (≥50%) without driver → pembrolizumab
- CRC: RAS/BRAF wild-type → anti-EGFR eligible; BRAF V600E → BRAF+MEK inhibitor; MSI-H → pembrolizumab first-line
- Melanoma: BRAF V600E/K → BRAF+MEK inhibitor; no BRAF → immunotherapy

### METABOLIC PATH (3M)

1. **Clinical risk integration** - Map HbA1c to risk: <7% low, 7-9% moderate, >9% high. Check for monogenic forms (MODY genes: HNF1A, HNF4A, GCK; lipodystrophy genes) via ClinVar.

2. **Complication risk** - Assess presence of nephropathy, neuropathy, retinopathy, CVD. Each complication adds score points.

3. **GWAS hits** - Call `GWAS_search_associations_by_gene` for TCF7L2 (strongest T2D risk gene) and `OpenTargets_target_disease_evidence` for key metabolic genes.

### CVD PATH (3V)

1. **FH gene check** - Call `clinvar_search_variants` for LDLR, APOB, PCSK9 to detect familial hypercholesterolemia. FH gene mutation = 20 pts; LDL > 190 = 15 pts; ASCVD > 20% 10-yr risk = 30 pts.

2. **Statin/anticoagulant PGx** - Check SLCO1B1 (*5 = statin myopathy risk), CYP2C9/VKORC1 (warfarin dosing), CYP2C19 (clopidogrel efficacy) via `PharmGKB_get_clinical_annotations`.

### RARE DISEASE PATH (3R)

1. **Causal variant** - Call `clinvar_search_variants` for the disease gene (e.g., FBN1 for Marfan, CFTR for CF). Check `UniProt_get_disease_variants_by_accession` for genotype-phenotype correlations.

2. **Penetrance** - Pathogenic variant in causal gene = definitive (30 pts); likely pathogenic = strong (25 pts); VUS = moderate (15 pts).

---

## Phase 4: Pharmacogenomic Profiling

**Goal**: Identify drug metabolism, transport, and target variants that affect drug selection and dosing.

**Steps**:

1. **Drug-metabolizing enzymes** - For each clinically relevant CYP gene (CYP2D6, CYP2C19, CYP2C9, CYP3A4): call `PharmGKB_get_clinical_annotations` and `PharmGKB_get_dosing_guidelines`. Cross-reference with `fda_pharmacogenomic_biomarkers` for FDA-labeled PGx interactions.

2. **Treatment-specific PGx** - Identify the primary drugs for the disease, then check each drug's PGx profile via `PharmGKB_get_drug_details` and `FDA_get_pharmacogenomics_info_by_drug_name`.

3. **Drug target variants** - Check VKORC1 (warfarin), DPYD (fluoropyrimidines), UGT1A1 (irinotecan), TPMT (thiopurines), HLA-B*5701 (abacavir), HLA-B*1502 (carbamazepine) via `PharmGKB_search_variants`.

**Key PGx impacts**:
- CYP2D6 PM: avoid codeine; tamoxifen → switch to aromatase inhibitor; many antidepressants require dose adjustment
- CYP2C19 PM: clopidogrel ineffective → switch to ticagrelor/prasugrel; voriconazole dose reduction needed
- SLCO1B1 *5: high simvastatin myopathy risk → use rosuvastatin or low-dose alternative
- DPYD deficient: avoid fluoropyrimidines (5-FU, capecitabine) or reduce dose 50%
- UGT1A1 *28/*28: reduce irinotecan starting dose

**PGx score (0-10 pts)**: Poor metabolizer for treatment-critical CYP + high-risk HLA = 10 pts; PM alone = 7-8 pts; IM = 4-5 pts; drug target variant = 3-5 pts; no actionable PGx = 0-2 pts.

---

## Phase 5: Comorbidity & Drug Interaction Risk

**Goal**: Assess how comorbidities and concurrent medications affect treatment safety.

**Steps**:

1. **Comorbidity analysis** - Call `OpenTargets_get_associated_targets_by_disease_efoId` for the primary disease and each comorbidity. Compare shared genetic targets. Search PubMed for comorbidity interactions.

2. **DDI analysis** - For each current medication: call `drugbank_get_drug_interactions_by_drug_name_or_id` (requires all 4 params: `query`, `case_sensitive=False`, `exact_match=False`, `limit`) and `FDA_get_drug_interactions_by_drug_name`.

3. **PGx-amplified DDI** - If patient is a CYP PM AND taking a CYP inhibitor for that same enzyme: flag as "compounded risk — very high priority for alternative drug or dose reduction."

---

## Phase 6: Molecular Pathway Analysis

**Goal**: Identify dysregulated pathways in the patient's gene set and find druggable pathway nodes.

**Steps**:

1. **Pathway enrichment** - Call `enrichr_gene_enrichment_analysis` with the patient's gene list (array) and `libs=['KEGG_2021_Human', 'Reactome_2022', 'GO_Biological_Process_2023']` (libs is REQUIRED). Alternatively call `ReactomeAnalysis_pathway_enrichment` with identifiers as a space-separated string.

2. **Protein network** - Call `STRING_get_interaction_partners` with `protein_ids` (array), `species=9606`, and `limit`. Follow with `STRING_functional_enrichment` for the expanded gene set.

3. **Druggability** - For key pathway nodes: call `OpenTargets_get_target_tractability_by_ensemblID` to assess small molecule, antibody, and PROTAC tractability.

**Key druggable pathways**: PI3K/AKT/mTOR (PI3K/mTOR inhibitors), RAS/MAPK (KRAS G12C/BRAF inhibitors), DNA damage repair (PARP inhibitors), Cell cycle CDK4/6 (palbociclib etc.), Immunocheckpoint (ICIs).

---

## Phase 7: Clinical Evidence & Guidelines

**Goal**: Map findings to established clinical guidelines, FDA approvals, and published evidence.

**Steps**:

1. **Guideline search** - Call `PubMed_Guidelines_Search` with a focused query (requires `limit` parameter, NOT `max_results`). Fall back to `PubMed_search_articles` if PubMed_Guidelines_Search fails.

2. **FDA-approved drugs for disease** - Call `OpenTargets_get_associated_drugs_by_disease_efoId` (efoId, size). For specific drugs of interest: `FDA_get_indications_by_drug_name` and `FDA_get_warnings_by_drug_name`.

3. **Biomarker-drug evidence** - Call `civic_search_evidence_items` (therapy_name, disease_name) for clinical evidence. Call `civic_search_assertions` for regulatory-level assertions.

**Guideline references**: Breast cancer = NCCN + St. Gallen; NSCLC = NCCN + ESMO; CRC = NCCN; T2D = ADA Standards; CVD = ACC/AHA; AF = ACC/AHA/HRS (CHA2DS2-VASc); Rare disease = ACMG/AMP variant classification.

---

## Phase 8: Clinical Trial Matching

**Goal**: Identify open trials matching the patient's molecular profile and disease stage.

**Steps**:

1. **Biomarker-driven trials** - Call `clinical_trials_search` with `action='search_studies'`, `condition`, `intervention`, `limit`. For broader search: `search_clinical_trials` with `query_term` (REQUIRED), `condition`, `intervention`, `pageSize`.

2. **Precision medicine trials** - Search for basket/umbrella trials using the patient's driver mutation as the query term. Also search risk-adapted trials for the patient's risk tier.

3. **Trial details** - For promising trials: call `clinical_trials_get_details` with `action='get_study_details'` and `nct_id`. Optionally call `get_clinical_trial_eligibility_criteria` with `nct_ids` (array) to verify biomarker eligibility.

---

## Phase 9: Integrated Scoring & Recommendations

### Precision Medicine Risk Score (0-100)

| Component | Max Points | Key Determinants |
|-----------|-----------|-----------------|
| Genetic Risk | 35 | Pathogenic variants, PRS, gene constraint |
| Clinical Risk | 30 | Stage, biomarker values, disease severity |
| Molecular Features | 25 | Driver mutations, subtype markers, TMB/MSI |
| Pharmacogenomic Risk | 10 | Metabolizer status, HLA alleles |

**Risk Tier Assignment**:

| Total Score | Tier | Management |
|------------|------|------------|
| 75-100 | VERY HIGH | Intensive treatment, subspecialty referral, clinical trial enrollment |
| 50-74 | HIGH | Aggressive treatment, close monitoring, molecular tumor board |
| 25-49 | INTERMEDIATE | Standard guideline-based care, PGx-guided dosing |
| 0-24 | LOW | Surveillance, prevention, risk factor modification |

### Treatment Algorithm

**Cancer**:
- Actionable driver mutation present → 1st line targeted therapy → 2nd line ICI or chemo → 3rd line alternate target or trial
- No driver, TMB-H or MSI-H → 1st line immunotherapy → 2nd line chemo
- No driver, no TMB-H → standard histology-based chemotherapy → clinical trial
- PGx mandatory adjustments: DPYD deficient → avoid fluoropyrimidines; UGT1A1 *28/*28 → reduce irinotecan; CYP2D6 PM + tamoxifen → switch to aromatase inhibitor

**Metabolic/CVD**:
- Monogenic form (MODY, FH) → disease-specific therapy (sulfonylureas for HNF1A-MODY; PCSK9i for FH)
- Polygenic → ADA/ACC-AHA guidelines with PGx adjustment: CYP2C19 PM → ticagrelor over clopidogrel; SLCO1B1 *5 → rosuvastatin or low-dose statin; VKORC1 variant → warfarin dose reduction or DOAC preference

---

## Known Gotchas

These API-specific quirks cause silent failures — check before calling:

- **DrugBank tools**: ALL 4 parameters are required for every DrugBank call: `query`, `case_sensitive` (bool), `exact_match` (bool), `limit` (int). Omitting any one causes failure.
- **MyGene CYP2D6**: First hit may be LOC110740340 (a pseudogene). Always filter hits by `symbol` match, not just position.
- **EnsemblVEP**: Parameter is `variant_id` (NOT `rsid`). Response may be a list `[{...}]` or `{data, metadata}` — handle both shapes.
- **ensembl_lookup_gene**: `species='homo_sapiens'` is REQUIRED, not optional.
- **OpenTargets_search_gwas_studies_by_disease**: `diseaseIds` must be an array (e.g., `["EFO_0000305"]`), not a string.
- **PubMed_Guidelines_Search**: Requires `limit` parameter (NOT `max_results`). May require API key — use `PubMed_search_articles` as fallback.
- **cBioPortal_get_mutations**: `gene_list` is a space-separated STRING (e.g., `"BRCA1 TP53 EGFR"`), not an array.
- **ClinVar**: Response shape varies — may return a plain list or `{status, data: {esearchresult}}`. Handle both.
- **gnomAD**: May return "Service overloaded" — treat as transient, retry once or skip and note in report.
- **fda_pharmacogenomic_biomarkers**: Default `limit=10` returns partial results. Use `limit=1000` to get all entries.
- **gwas_get_associations_for_trait**: Prone to errors; prefer `gwas_search_associations` as alternative.
- **FDA label tools**: Results nested as `result['results'][0]['field_name']`. Always index into `results` list.
- **enrichr_gene_enrichment_analysis**: `libs` parameter is REQUIRED. Omitting it causes failure. Key values: `KEGG_2021_Human`, `Reactome_2022`, `GO_Biological_Process_2023`.
- **ReactomeAnalysis_pathway_enrichment**: `identifiers` must be space-separated string, not an array.
- **clinical_trials_search**: Requires `action='search_studies'` explicitly set.
- **search_clinical_trials**: `query_term` is REQUIRED even if you specify `condition` and `intervention`.

---

## Output Report Structure

Save to `[PATIENT_ID]_precision_medicine_report.md`. Sections:

1. **Executive Summary** — Risk Score X/100, Risk Tier, key finding, primary recommendation
2. **Patient Profile** — Disease classification, genomic data summary, clinical parameters
3. **Genetic Risk Assessment** — Germline variants, gene-disease evidence, PRS, population frequency
4. **Disease-Specific Stratification** — Subtype, prognostic markers, risk group
5. **Pharmacogenomic Profile** — CYP status, drug target variants, PGx recommendations
6. **Comorbidity & DDI Risk** — Disease overlap, DDI list, PGx-amplified risks
7. **Dysregulated Pathways** — Key pathways, druggable targets, network findings
8. **Clinical Evidence & Guidelines** — Guideline tier, FDA-approved therapies, biomarker-drug evidence
9. **Clinical Trial Matches** — Biomarker-driven, precision medicine, risk-adapted trials
10. **Integrated Risk Score** — Component breakdown table (Genetic/Clinical/Molecular/PGx)
11. **Treatment Algorithm** — 1st/2nd/3rd line + PGx dose adjustments
12. **Monitoring Plan** — Biomarker surveillance, imaging, reassessment timeline
13. **Completeness Checklist** — Table: data layer | available | analyzed | key finding
14. **Evidence Sources** — All databases and tools cited

---

## Evidence Grading

| Tier | Level | Sources |
|------|-------|---------|
| **T1** | Clinical/regulatory | FDA labels, NCCN, PharmGKB Level 1A/1B, ClinVar pathogenic |
| **T2** | Strong experimental | CIViC Level A/B, OpenTargets high-score, GWAS p<5e-8, clinical trials |
| **T3** | Moderate evidence | PharmGKB Level 2, CIViC Level C, GWAS suggestive, preclinical |
| **T4** | Computational | VEP predictions, pathway inference, network analysis, PRS estimates |

---

## Common Use Patterns

| Pattern | Key Phases | Expected Score |
|---------|-----------|---------------|
| Cancer + actionable mutation (e.g., BRCA1 breast, EGFR NSCLC) | 1→2→3C→4→7→8→9 | HIGH-VERY HIGH (50-80) |
| Metabolic + PGx concern (e.g., T2D + CYP2C19 PM on clopidogrel) | 1→2→3M→4→5→9 | HIGH (50-60), urgent PGx switch |
| CVD risk (e.g., LDL 190 + SLCO1B1*5 + family hx MI) | 1→2→3V→4→7→9 | INTERMEDIATE-HIGH (45-55) |
| Rare disease (e.g., Marfan + FBN1 variant) | 1→2→3R→7→9 | Depends on aortic involvement |
| Neurological risk (e.g., APOE e4/e4 AD risk) | 1→2→3→4→7→9 | HIGH (60-75) |
| Comprehensive cancer (e.g., NSCLC + EGFR + TMB-H + PD-L1 80%) | All phases critical | VERY HIGH (70-80, stage IV) |

---

## Abbreviated Tool Reference

Full parameter details and response schemas are in `TOOLS_REFERENCE.md`.

| Tool | Purpose |
|------|---------|
| `OpenTargets_get_disease_id_description_by_name` | Resolve disease name to EFO/MONDO ID |
| `MyGene_query_genes` | Resolve gene symbol to Ensembl/Entrez IDs |
| `ensembl_lookup_gene` | Get gene details (requires `species='homo_sapiens'`) |
| `EnsemblVEP_annotate_rsid` | Variant impact for rsID |
| `EnsemblVEP_annotate_hgvs` | Variant impact for HGVS notation |
| `clinvar_search_variants` | Search pathogenic variants by gene |
| `clinvar_get_variant_details` | Full ClinVar record for a variant |
| `OpenTargets_target_disease_evidence` | Gene-disease evidence strength |
| `OpenTargets_search_gwas_studies_by_disease` | GWAS studies for a disease |
| `GWAS_search_associations_by_gene` | GWAS associations for a gene |
| `gwas_get_associations_for_trait` | Trait-SNP GWAS associations |
| `gnomad_get_variant` | Population allele frequency |
| `gnomad_get_gene_constraints` | Gene constraint (pLI, LOEUF) |
| `cBioPortal_get_mutations` | Somatic mutation landscape (gene_list = STRING) |
| `HPA_get_cancer_prognostics_by_gene` | Cancer prognostic data |
| `PharmGKB_get_clinical_annotations` | Drug-gene PGx clinical annotations |
| `PharmGKB_get_dosing_guidelines` | CPIC dosing guidelines |
| `PharmGKB_get_drug_details` | Drug PGx profile |
| `fda_pharmacogenomic_biomarkers` | FDA PGx biomarker labels |
| `FDA_get_pharmacogenomics_info_by_drug_name` | FDA PGx label text for drug |
| `FDA_get_indications_by_drug_name` | FDA-approved indications |
| `FDA_get_warnings_by_drug_name` | Drug warnings |
| `FDA_get_drug_interactions_by_drug_name` | FDA DDI info |
| `drugbank_get_drug_interactions_by_drug_name_or_id` | DrugBank DDI data (all 4 params required) |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | Drug basic info (all 4 params required) |
| `enrichr_gene_enrichment_analysis` | Pathway enrichment (libs param required) |
| `ReactomeAnalysis_pathway_enrichment` | Reactome pathway enrichment |
| `STRING_get_interaction_partners` | Protein-protein interactions |
| `STRING_functional_enrichment` | Network functional enrichment |
| `OpenTargets_get_target_tractability_by_ensemblID` | Druggability assessment |
| `OpenTargets_get_associated_drugs_by_disease_efoId` | Approved drugs for a disease |
| `civic_search_evidence_items` | CIViC biomarker-drug clinical evidence |
| `civic_search_assertions` | CIViC regulatory-level assertions |
| `PubMed_Guidelines_Search` | Clinical guideline articles (limit required) |
| `PubMed_search_articles` | General literature search |
| `UniProt_get_disease_variants_by_accession` | Known disease variants for protein |
| `UniProt_get_function_by_accession` | Protein function |
| `clinical_trials_search` | ClinicalTrials.gov search (action required) |
| `search_clinical_trials` | Alternative trial search (query_term required) |
| `clinical_trials_get_details` | Full trial protocol |
