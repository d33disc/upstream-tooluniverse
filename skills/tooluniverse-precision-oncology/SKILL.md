---
name: tooluniverse-precision-oncology
description: Provide actionable treatment recommendations for cancer patients based on molecular profile. Interprets tumor mutations, identifies FDA-approved therapies, finds resistance mechanisms, matches clinical trials. Use when oncologist asks about treatment options for specific mutations (EGFR, KRAS, BRAF, etc.), therapy resistance, or clinical trial eligibility.
---

# Precision Oncology Treatment Advisor

Provide actionable treatment recommendations for cancer patients based on their molecular profile using CIViC, ClinVar, OpenTargets, ClinicalTrials.gov, and structure-based analysis.

**KEY PRINCIPLES**:
1. **Report-first** - Create report file FIRST, update progressively
2. **Evidence-graded** - Every recommendation has evidence level
3. **Actionable output** - Prioritized treatment options, not data dumps
4. **Clinical focus** - Answer "what should we do?" not "what exists?"
5. **English-first queries** - Always use English terms in tool calls (mutations, drug names, cancer types), even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## When to Use

Apply when user asks:
- "Patient has [cancer] with [mutation] - what treatments?"
- "What are options for EGFR-mutant lung cancer?"
- "Patient failed [drug], what's next?"
- "Clinical trials for KRAS G12C?"
- "Why isn't [drug] working anymore?"

---

## Phase 0: Tool Verification

**CRITICAL**: Verify tool parameters before first use.

| Tool | WRONG | CORRECT |
|------|-------|---------|
| `civic_get_variant` | `variant_name` | `id` (numeric) |
| `civic_get_evidence_item` | `variant_id` | `id` |
| `OpenTargets_*` | `ensemblID` | `ensemblId` (camelCase) |
| `search_clinical_trials` | `disease` | `condition` |

---

## Workflow Overview

```
Input: Cancer type + Molecular profile (mutations, fusions, amplifications)

Phase 1: Profile Validation
├── Validate variant nomenclature
├── Resolve gene identifiers
└── Confirm cancer type (EFO/ICD)

Phase 2: Variant Interpretation
├── CIViC → Evidence for each variant
├── ClinVar → Pathogenicity
├── COSMIC → Somatic mutation frequency
├── GDC/TCGA → Real tumor data
├── DepMap → Target essentiality
├── OncoKB → FDA actionability levels
├── cBioPortal → Cross-study mutation data
├── Human Protein Atlas → Expression validation
├── OpenTargets → Target-disease evidence
└── OUTPUT: Variant significance table + target validation + expression

Phase 2.5: Tumor Expression Context
├── CELLxGENE → Cell-type specific expression in tumor
├── ChIPAtlas → Regulatory context
└── OUTPUT: Expression validation

Phase 3: Treatment Options
├── Approved therapies (FDA label)
├── NCCN-recommended (literature)
├── Off-label with evidence
└── OUTPUT: Prioritized treatment list

Phase 3.5: Pathway & Network Analysis
├── KEGG/Reactome → Pathway context
├── IntAct → Protein interactions
├── Drug combination rationale
└── OUTPUT: Biological context for combinations

Phase 4: Resistance Analysis (if prior therapy)
├── Known resistance mechanisms
├── Structure-based analysis (NvidiaNIM)
├── Network-based bypass pathways (IntAct)
└── OUTPUT: Resistance explanation + strategies

Phase 5: Clinical Trial Matching
├── Active trials for indication + biomarker
├── Eligibility filtering
└── OUTPUT: Matched trials

Phase 5.5: Literature Evidence
├── PubMed → Published evidence
├── BioRxiv/MedRxiv → Recent preprints
├── OpenAlex → Citation analysis
└── OUTPUT: Supporting literature

Phase 6: Report Synthesis
├── Executive summary
├── Treatment recommendations (prioritized)
└── Next steps
```

---

## Phase 1: Profile Validation

### 1.1 Resolve Gene Identifiers

For each gene in the molecular profile, collect all identifiers needed downstream:
- Call `MyGene_query_genes` with `q=<gene_symbol>` and `species="human"` to get the Ensembl ID (required by OpenTargets tools).
- Call `UniProt_search` with `query=<gene_symbol>` and `organism="human"` to get the UniProt primary accession (required for structure prediction).
- Call `ChEMBL_search_targets` with `query=<gene_symbol>` and `organism="Homo sapiens"` to get the ChEMBL target ID (required for bioactivity queries).

Store all three IDs before proceeding to Phase 2.

### 1.2 Validate Variant Nomenclature

Accept any of these formats; normalize to HGVS protein notation internally:
- HGVS protein: `p.L858R`, `p.V600E`
- cDNA: `c.2573T>G`
- Common shorthand: `T790M`, `G12C`

---

## Phase 2: Variant Interpretation

### 2.1 CIViC Evidence

Call `civic_search_variants` with `query="<GENE> <VARIANT>"` to find variant records. For each result, call `civic_get_variant` with the numeric `id` to retrieve evidence items. Categorize evidence by `evidence_type`: Predictive (drug response), Prognostic, or Diagnostic.

### 2.2 COSMIC Somatic Mutation Analysis

Call `COSMIC_search_mutations` with `operation="search"` and `terms="<GENE> <VARIANT>"` to find frequency and cancer type distribution. For hotspot analysis, call `COSMIC_get_mutations_by_gene` with `operation="get_by_gene"` and `gene=<GENE>`. Use `genome_build=38` (GRCh38) unless the patient report specifies GRCh37.

COSMIC provides: cancer type distribution, recurrence count, FATHMM pathogenicity prediction.

### 2.3 GDC/TCGA Pan-Cancer Analysis

Call `GDC_get_mutation_frequency` with `gene_symbol=<GENE>` for pan-cancer mutation statistics. For cancer-specific data, call `GDC_get_ssm_by_gene` with `gene_symbol=<GENE>` and `project_id="TCGA-<TYPE>"` (e.g., `TCGA-LUAD`). Use `GDC_list_projects` with `program="TCGA"` to find valid project IDs. For copy number status, call `GDC_get_cnv_data` with `project_id` and `gene_symbol`.

Common TCGA project IDs: `TCGA-LUAD` (lung adeno), `TCGA-BRCA` (breast), `TCGA-COAD` (colorectal), `TCGA-SKCM` (melanoma), `TCGA-GBM` (glioblastoma), `TCGA-PAAD` (pancreatic).

### 2.4 DepMap Target Essentiality

Call `DepMap_get_gene_dependencies` with `gene_symbol=<GENE>` to retrieve CRISPR knockout effect scores. Scores below -0.5 indicate the gene is essential for cell survival; below -1.0 is strongly essential. For cancer-type context, call `DepMap_get_cell_lines` with `tissue=<TISSUE>` or `cancer_type=<TYPE>` to identify relevant cell lines.

Essential in cancer but not normal cells = selective target. Pan-essential genes (e.g., MYC) are harder to target safely.

### 2.5 OncoKB Actionability

Call `OncoKB_annotate_variant` with `gene=<GENE>`, `variant=<VARIANT>` (e.g., `"V600E"`), and `tumor_type=<ONCOTREE_CODE>` (e.g., `"MEL"`, `"LUAD"`). Returns `oncogenic` status, `mutationEffect`, `highestSensitiveLevel`, and applicable treatments. Also call `OncoKB_get_gene_info` with `gene=<GENE>` to confirm oncogene vs. tumor suppressor status.

For copy number alterations, use `OncoKB_annotate_copy_number` with `copy_number_type="AMPLIFICATION"` or `"DELETION"`.

OncoKB level mapping: Level 1/2 = FDA-approved or standard care (★★★); Level 3A/3B = clinical evidence (★★☆); Level 4 = biological (★☆☆); R1/R2 = resistance markers.

### 2.6 cBioPortal Cross-Study Analysis

Call `cBioPortal_get_mutations` with `study_id=<STUDY>` and `gene_list="<GENE1>,<GENE2>"` to retrieve mutation types and co-mutation patterns. Use `cBioPortal_get_cancer_studies` to find study IDs. For multi-omic context, call `cBioPortal_get_molecular_profiles` with `study_id`.

Common study IDs: `luad_tcga`, `brca_tcga`, `coadread_tcga`, `skcm_tcga`, `genie_public`.

### 2.7 Human Protein Atlas Expression Validation

Call `HPA_search_genes_by_query` with `search_query=<GENE>` to find the gene entry, then call `HPA_get_comparative_expression_by_gene_and_cellline` with `gene_name=<GENE>` and `cell_line=<LINE>` to compare tumor vs. normal expression.

Cancer-to-cell-line mapping: lung → `a549`, breast → `mcf7`, liver → `hepg2`, cervical → `hela`, prostate → `pc3`.

### 2.8 Evidence Level Mapping

| CIViC Level | Our Tier | Meaning |
|-------------|----------|---------|
| A | ★★★ | FDA-approved, guideline |
| B | ★★☆ | Clinical evidence |
| C | ★★☆ | Case study |
| D | ★☆☆ | Preclinical |
| E | ☆☆☆ | Inferential |

### 2.9 Output Table

```markdown
## Variant Interpretation

| Variant | Gene | Significance | Evidence Level | Clinical Implication |
|---------|------|--------------|----------------|---------------------|
| L858R | EGFR | Oncogenic driver | ★★★ (Level A) | Sensitive to EGFR TKIs |
| T790M | EGFR | Resistance | ★★★ (Level A) | Resistant to 1st/2nd gen TKIs |

### COSMIC Mutation Frequency
| Gene | Mutation | COSMIC Count | Primary Cancer Types | FATHMM |
|------|----------|--------------|---------------------|--------|
| EGFR | L858R | 15,234 | Lung (85%), CRC (5%) | Pathogenic |

### TCGA/GDC Patient Tumor Data
| Gene | TCGA Project | SSM Cases | CNV Amp | % Samples |
|------|-------------|-----------|---------|-----------|
| EGFR | TCGA-LUAD | 156 | 89 | 28% |

### DepMap Target Essentiality
| Gene | Mean Effect (All) | Mean Effect (Cancer Type) | Interpretation |
|------|-------------------|---------------------------|----------------|
| EGFR | -0.15 | -0.45 (lung) | Cancer-selective target |
```

---

## Phase 2.5: Tumor Expression Context

Call `CELLxGENE_get_expression_data` with `gene=<GENE>` and `tissue=<TISSUE>` to get cell-type-specific expression in the tumor microenvironment. Compare tumor epithelial, CAF, and immune compartments. High tumor/normal expression ratio confirms the target is expressed where therapy needs to act and supports selectivity.

---

## Phase 3: Treatment Options

### 3.1 Approved Therapies

Query in this order:
1. `OpenTargets_get_associated_drugs_by_target_ensemblId` with `ensemblId=<ID>` — approved drugs for the target
2. `DailyMed_search_spls` with `drug_name=<DRUG>` — FDA label details and approved indications
3. `ChEMBL_get_drug_mechanisms_of_action_by_chemblId` with `chemblId=<ID>` — mechanism of action

### 3.2 Treatment Prioritization

| Priority | Criteria |
|----------|----------|
| **1st Line** | FDA-approved for indication + biomarker (★★★) |
| **2nd Line** | Clinical trial evidence, guideline-recommended (★★☆) |
| **3rd Line** | Off-label with mechanistic rationale (★☆☆) |

### 3.3 Output Format

```markdown
## Treatment Recommendations

### First-Line Options
**1. Osimertinib (Tagrisso)** ★★★
- FDA-approved for EGFR T790M+ NSCLC
- Evidence: AURA3 trial (ORR 71%, mPFS 10.1 mo)
- Source: FDA label, PMID:27959700

### Second-Line Options
**2. Combination: Osimertinib + [Agent]** ★★☆
- Evidence: Phase 2 data
- Source: NCT04487080
```

---

## Phase 3.5: Pathway & Network Analysis

### 3.5.1 Pathway Context

Call `kegg_search_pathway` with `query=<GENE>` or `kegg_get_gene_info` with the KEGG gene ID (format: `hsa:<ENTREZ_ID>`) to identify relevant signaling pathways. Call `reactome_disease_target_score` with `disease=<CANCER_TYPE>` and `target=<GENE>` for Reactome disease relevance scores.

Identify: primary activated pathway, downstream effectors, and potential bypass pathways that may mediate resistance.

### 3.5.2 Protein Interaction Network

Call `intact_get_interaction_network` with `gene=<GENE>` and `depth=1` for direct interactors (use `depth=2` for second-degree bypass candidates). Known EGFR bypass pathways to check: MET, ERBB2, ERBB3, AXL, IGF1R.

Document direct interactions with MI-score as biological rationale for combination therapies.

### 3.5.3 Output

```markdown
## Pathway & Network Analysis

| Pathway | Genes | Relevance | Drug Targets |
|---------|-------|-----------|--------------|
| EGFR signaling (hsa04012) | EGFR, MET, ERBB3 | Primary | Osimertinib, Capmatinib |
| PI3K-AKT (hsa04151) | PIK3CA, AKT1 | Downstream | Alpelisib |
| RAS-MAPK (hsa04010) | KRAS, BRAF, MEK | Bypass | Sotorasib, Trametinib |

**Combination rationale**: EGFR inhibition → compensatory MET activation (60% of cases).
Network confirms direct EGFR-MET interaction (IntAct MI-score 0.75).
```

---

## Phase 4: Resistance Analysis

### 4.1 Known Mechanisms

Call `civic_search_evidence_items` with `drug=<DRUG>`, `evidence_type="Predictive"`, and `clinical_significance="Resistance"` to retrieve CIViC resistance evidence. Then call `PubMed_search_articles` with `query='"<DRUG>" AND "<GENE>" AND resistance'` for published mechanisms.

Key resistance patterns to check:
- **EGFR TKIs**: T790M (1st/2nd gen), C797S (osimertinib), MET amplification, SCLC transformation
- **BRAF inhibitors**: NRAS mutation, MEK bypass, BRAF splice variants
- **ALK inhibitors**: ALK secondary mutations (L1196M, G1269A), bypass via EGFR, KRAS

### 4.2 Structure-Based Analysis

When the resistance mutation affects the drug binding site, use `NvidiaNIM_alphafold2` with `sequence=<WT_SEQUENCE>` to predict the wild-type structure, then `NvidiaNIM_diffdock` with `protein=<STRUCTURE>` and `ligand=<DRUG_SMILES>` and `num_poses=5` to model drug binding. Repeat with mutant sequence to compare binding site geometry.

Report the structural basis: e.g., "T790M introduces a bulky methionine that creates steric clash with erlotinib's aniline group."

Retrieve protein sequences via `UniProt_get_protein_sequence` with `accession=<UNIPROT_ID>`.

---

## Phase 5: Clinical Trial Matching

### 5.1 Search Strategy

Call `search_clinical_trials` with `condition=<CANCER_TYPE>`, `intervention=<BIOMARKER_OR_DRUG>`, `status="Recruiting"`, and `pageSize=50`. For the top 20 results, call `get_clinical_trial_eligibility_criteria` with `nct_ids=[<LIST>]` to retrieve inclusion/exclusion criteria.

Filter for biomarker-required trials that match the patient's molecular profile.

### 5.2 Output Format

```markdown
## Clinical Trial Options

| NCT ID | Phase | Agent | Biomarker Required | Status | Location |
|--------|-------|-------|-------------------|--------|----------|
| NCT04487080 | 2 | Amivantamab + lazertinib | EGFR T790M | Recruiting | US, EU |
| NCT05388669 | 3 | Patritumab deruxtecan | Prior osimertinib | Recruiting | US |

*Source: ClinicalTrials.gov*
```

---

## Phase 5.5: Literature Evidence

### 5.5.1 Published Literature

Call `PubMed_search_articles` with `query='"<DRUG>" AND "<BIOMARKER>" AND "<CANCER_TYPE>"'` (limit 20) for treatment efficacy evidence. For resistance, search `'"<DRUG>" AND resistance AND mechanism'`.

### 5.5.2 Preprints

Use `EuropePMC_search_articles` with `source="PPR"` to search preprints across bioRxiv and medRxiv (these servers lack their own search APIs). Mark all preprint findings as NOT peer-reviewed in the report.

### 5.5.3 Citation Context

Call `openalex_search_works` with `query=<PAPER_TITLE>` to retrieve citation counts for key evidence papers. High citation count (>100) from a Phase 3 trial strengthens evidence tier.

### 5.5.4 Output

```markdown
## Literature Evidence

| PMID | Title | Year | Citations | Type |
|------|-------|------|-----------|------|
| 27959700 | AURA3: Osimertinib vs chemotherapy... | 2017 | 2,450 | Phase 3 |
| 30867819 | Mechanisms of osimertinib resistance... | 2019 | 680 | Review |

**Note**: Preprints have NOT undergone peer review — interpret with caution.
```

---

## Report Template

**File**: `[PATIENT_ID]_oncology_report.md`

```markdown
# Precision Oncology Report

**Patient ID**: [ID] | **Date**: [Date]

## Patient Profile
- **Diagnosis**: [Cancer type, stage]
- **Molecular Profile**: [Mutations, fusions]
- **Prior Therapy**: [Previous treatments]

---

## Executive Summary
[2-3 sentence summary of key findings and recommendation]

---

## 1. Variant Interpretation
[Table with variants, significance, evidence levels]

## 2. Treatment Recommendations
### First-Line Options
[Prioritized list with evidence]

### Second-Line Options
[Alternative approaches]

## 3. Resistance Analysis (if applicable)
[Mechanism explanation, strategies to overcome]

## 4. Clinical Trial Options
[Matched trials with eligibility]

## 5. Next Steps
1. [Specific actionable recommendation]
2. [Follow-up testing if needed]
3. [Referral if appropriate]

---

## Data Sources
| Source | Query | Data Retrieved |
|--------|-------|----------------|
| CIViC | [gene] [variant] | Evidence items |
| ClinicalTrials.gov | [condition] | Active trials |
```

---

## Completeness Checklist

See [CHECKLIST.md](CHECKLIST.md) for the full pre-delivery checklist.

Quick summary before finalizing:
- [ ] All variants interpreted with evidence levels
- [ ] ≥1 first-line recommendation with ★★★ evidence (or explain why none)
- [ ] Resistance mechanism addressed (if prior therapy failed)
- [ ] ≥3 clinical trials listed (or "no matching trials")
- [ ] Executive summary is actionable (says what to DO)
- [ ] All recommendations have source citations

---

## Known Gotchas

**Parameter naming traps**:
- `OpenTargets_*` tools require `ensemblId` (camelCase i, lowercase d). `ensemblID` (capital D) will silently fail.
- `civic_get_variant` takes a numeric `id`, not `variant_name` or gene symbol. Always search first to get the numeric ID.
- `search_clinical_trials` uses `condition` not `disease`. Using `disease` returns no results without error.
- `OncoKB_annotate_variant` requires the `operation="annotate_variant"` parameter even though it is the only operation; omitting it causes failure.
- `COSMIC_*` tools require the `operation` parameter (`"search"` or `"get_by_gene"`).

**Data interpretation traps**:
- CIViC evidence items use `evidence_type="Predictive"` for drug sensitivity/resistance — do NOT filter for `"Therapeutic"` (that field does not exist).
- DepMap effect scores are negative for essential genes. A score of 0 means NOT essential. Do not misread -0.8 as "80% expressed."
- cBioPortal study IDs are lowercase with underscores (e.g., `luad_tcga`), not the TCGA-format used by GDC (e.g., `TCGA-LUAD`). Use the correct format per tool.
- OncoKB `tumor_type` takes OncoTree codes (e.g., `"LUAD"`, `"MEL"`), not free-text cancer names.
- EuropePMC preprint search uses `source="PPR"`, not `source="preprint"` or `source="biorxiv"`.

**Workflow traps**:
- If CIViC returns no results for a variant, it does NOT mean the variant is benign — fall back to OncoKB and COSMIC before concluding.
- GDC expression tools (`GDC_get_gene_expression`) return file metadata, not expression values directly. Use TCGA data for mutation/CNV; use Human Protein Atlas or CELLxGENE for expression levels.
- NvidiaNIM structure prediction requires the full amino acid sequence, not just the gene name. Retrieve the sequence first via `UniProt_get_protein_sequence`.
- TMB (tumor mutational burden) and MSI status are biomarkers for immunotherapy eligibility (pembrolizumab). If the patient profile includes TMB-High (≥10 mut/Mb) or MSI-High, always check pembrolizumab FDA approval regardless of the primary driver mutation.

---

## Fallback Chains

| Primary | Fallback | Use When |
|---------|----------|----------|
| CIViC variant | OncoKB, then COSMIC | Variant not in CIViC |
| OpenTargets drugs | ChEMBL activities | No approved drugs found |
| ClinicalTrials.gov | WHO ICTRP | US trials insufficient |
| NvidiaNIM_alphafold2 | AlphaFold DB precomputed | API unavailable |
| GDC expression | Human Protein Atlas | RNA-seq data absent |

---

## Evidence Grading

| Tier | Symbol | Criteria | Example |
|------|--------|----------|---------|
| T1 | ★★★ | FDA-approved, Level A evidence | Osimertinib for T790M |
| T2 | ★★☆ | Phase 2/3 data, Level B | Combination trials |
| T3 | ★☆☆ | Preclinical, Level D | Novel mechanisms |
| T4 | ☆☆☆ | Computational only | Docking predictions |

---

## Abbreviated Tool Reference

| Phase | Tool | Purpose |
|-------|------|---------|
| 1 | `MyGene_query_genes` | Resolve gene → Ensembl/Entrez IDs |
| 1 | `UniProt_search` | Resolve gene → UniProt accession |
| 2 | `civic_search_variants` | Find CIViC variant records |
| 2 | `civic_get_variant` | Get evidence items (requires numeric id) |
| 2 | `COSMIC_search_mutations` | Mutation frequency + cancer types |
| 2 | `GDC_get_mutation_frequency` | Pan-cancer TCGA mutation stats |
| 2 | `GDC_get_ssm_by_gene` | Per-project somatic mutations |
| 2 | `DepMap_get_gene_dependencies` | CRISPR essentiality scores |
| 2 | `OncoKB_annotate_variant` | FDA actionability level |
| 2 | `cBioPortal_get_mutations` | Cross-study mutation data |
| 2 | `HPA_get_comparative_expression_by_gene_and_cellline` | Tumor vs normal expression |
| 2.5 | `CELLxGENE_get_expression_data` | Cell-type expression in tumor |
| 3 | `OpenTargets_get_associated_drugs_by_target_ensemblId` | Approved drugs |
| 3 | `DailyMed_search_spls` | FDA label details |
| 3.5 | `kegg_get_gene_info` | Pathway membership |
| 3.5 | `intact_get_interaction_network` | Protein interaction partners |
| 4 | `civic_search_evidence_items` | Resistance evidence |
| 4 | `NvidiaNIM_alphafold2` | Protein structure prediction |
| 4 | `NvidiaNIM_diffdock` | Drug-protein docking |
| 5 | `search_clinical_trials` | Find active trials |
| 5 | `get_clinical_trial_eligibility_criteria` | Eligibility criteria |
| 5.5 | `PubMed_search_articles` | Published evidence |
| 5.5 | `EuropePMC_search_articles` | Preprints (source="PPR") |
| 5.5 | `openalex_search_works` | Citation counts |

For complete parameter tables and usage examples, see [references/tools.md](references/tools.md).
