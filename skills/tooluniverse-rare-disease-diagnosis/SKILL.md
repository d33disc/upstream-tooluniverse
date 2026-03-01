---
name: tooluniverse-rare-disease-diagnosis
description: Provide differential diagnosis for patients with suspected rare diseases based on phenotype and genetic data. Matches symptoms to HPO terms, identifies candidate diseases from Orphanet/OMIM, prioritizes genes for testing, interprets variants of uncertain significance. Use when clinician asks about rare disease diagnosis, unexplained phenotypes, or genetic testing interpretation.
---

# Rare Disease Diagnosis Advisor

Systematic diagnosis support using phenotype matching, gene panel prioritization, and variant interpretation across Orphanet, OMIM, HPO, ClinVar, DisGeNET, ClinGen, and structure-based analysis.

**KEY PRINCIPLES**:
1. **Report-first** — Create the report file first, update it progressively as you gather data.
2. **Phenotype-driven** — Convert all symptoms to HPO terms before searching.
3. **Multi-database triangulation** — Cross-reference Orphanet, OMIM, DisGeNET, OpenTargets.
4. **Evidence grading** — Grade every diagnosis by supporting evidence strength.
5. **Actionable output** — Deliver a prioritized differential and concrete next steps.
6. **Genetic counseling aware** — Consider inheritance patterns and family history.
7. **English-first queries** — Always query tools in English even if the user writes in another language. Try original-language terms only as a fallback. Respond in the user's language.

---

## When to Use

- "Patient has [symptoms], what rare disease could this be?"
- "Unexplained developmental delay with [features]"
- "WES found VUS in [gene], is this pathogenic?"
- "What genes should we test for [phenotype]?"
- "Differential diagnosis for [rare symptom combination]"

---

## Workflow Overview

```
Phase 0  Verify tool parameters (known parameter corrections)
Phase 1  Phenotype standardization → HPO terms
Phase 2  Disease matching → ranked differential diagnosis
Phase 3  Gene panel → prioritized testing list
Phase 3.5 Expression & tissue context (CELLxGENE, ChIPAtlas)
Phase 3.6 Pathway & interaction analysis (KEGG, IntAct)
Phase 4  Variant interpretation → ACMG classification (if variants provided)
Phase 5  Structure analysis for VUS (NVIDIA NIM AlphaFold2)
Phase 6  Literature evidence (PubMed, EuropePMC, OpenAlex)
Phase 7  Report synthesis → final report + gene panel CSV
```

See [CHECKLIST.md](CHECKLIST.md) before delivery. For full tool parameter tables, see [references/tools.md](references/tools.md).

---

## Critical Workflow Requirements

### Report-First Approach (MANDATORY)

1. Create `[PATIENT_ID]_rare_disease_report.md` immediately with all section headers and `[Researching...]` placeholders.
2. Update it progressively as each phase completes.
3. Produce companion files if applicable:
   - `[PATIENT_ID]_gene_panel.csv` — prioritized genes
   - `[PATIENT_ID]_variant_interpretation.csv` — if variants provided

### Citation Requirements (MANDATORY)

Every finding must state its source, e.g.:

```
*Source: Orphanet via `Orphanet_get_disease` (ORPHA:558)*
*Source: OMIM via `OMIM_get_entry` (MIM:154700)*
*Source: ClinVar via `ClinVar_search_variants` (VCV000012345)*
```

---

## Phase 0: Parameter Verification

Before calling any tool, check these known parameter mistakes:

| Tool | Wrong Parameter | Correct Parameter |
|------|-----------------|-------------------|
| `OpenTargets_get_associated_diseases_by_target_ensemblId` | `ensemblID` | `ensemblId` |
| `ClinVar_get_variant_by_id` | `variant_id` | `id` |
| `MyGene_query_genes` | `gene` | `q` |
| `gnomAD_get_variant_frequencies` | `variant` | `variant_id` (format: `1-55505647-G-A`) |
| `GTEx_get_median_gene_expression` | `ensembl_id` | `gencode_id` (versioned, e.g. `ENSG00000166147.15`) |

---

## Phase 1: Phenotype Standardization

**Goal**: Convert every clinical symptom to a standardized HPO term before proceeding.

**Steps**:
1. For each symptom, call `HPO_search_terms` with the symptom as a text query.
2. Pick the best-matching term; record its HPO ID (e.g., `HP:0000098`) and name.
3. Classify each term as **core** (always present), **variable** (>50%), or **occasional** (<50%).
4. Note age of onset, family history, and suspected inheritance pattern.

**Minimum**: ≥5 standardized HPO terms.

**Report section output**:
```markdown
## 1. Phenotype Analysis

| Clinical Feature | HPO Term | HPO ID | Category |
|------------------|----------|--------|----------|
| Tall stature | Tall stature | HP:0000098 | Core |
| Long fingers | Arachnodactyly | HP:0001166 | Core |
| Heart murmur | Cardiac murmur | HP:0030148 | Variable |

Total HPO Terms: 8 | Onset: Childhood | Family history: Father affected (AD suspected)

*Source: HPO via `HPO_search_terms`*
```

---

## Phase 2: Disease Matching

**Goal**: Identify ≥5 ranked candidate diseases with ORPHA and OMIM identifiers.

**Steps**:

1. **Orphanet search** — call `Orphanet_search_diseases` for each key symptom keyword. Then call `Orphanet_get_genes` for each candidate to retrieve causative genes.

2. **OMIM cross-reference** — call `OMIM_search` for top genes, then `OMIM_get_entry` for full text and `OMIM_get_clinical_synopsis` for organ-system phenotype features.

3. **DisGeNET gene-disease associations** — call `DisGeNET_search_gene` for each candidate gene to get GDA scores. Use `source="CURATED"` and `min_score=0.3` for high-confidence results. Scores >0.7 = very strong; 0.4–0.7 = strong.

4. **Score phenotype overlap** — compare patient HPO terms against each disease's known features:

| Match Level | Score | Criteria |
|-------------|-------|----------|
| Excellent | >80% | Most core + variable features match |
| Good | 60–80% | Core features match, some variable |
| Possible | 40–60% | Some overlap |
| Unlikely | <40% | Poor phenotype fit |

5. **OpenTargets supplemental** — use `OpenTargets_get_disease_associated_targets` (EFO ID) or `OpenTargets_get_associated_diseases_by_target_ensemblId` (Ensembl ID, camelCase param) for additional gene-disease evidence.

**Report section output**:
```markdown
## 2. Differential Diagnosis

| Rank | Disease | ORPHA | OMIM | Match | Inheritance | Key Gene(s) |
|------|---------|-------|------|-------|-------------|-------------|
| 1 | Marfan syndrome | 558 | 154700 | 85% | AD | FBN1 |
| 2 | Loeys-Dietz syndrome | 60030 | 609192 | 72% | AD | TGFBR1/2 |
| 3 | Vascular EDS | 286 | 130050 | 65% | AD | COL3A1 |

For each top-3 disease: provide feature-by-feature comparison, OMIM clinical synopsis highlights,
diagnostic criteria if established (e.g. Ghent nosology for Marfan), and inheritance notes.
```

---

## Phase 3: Gene Panel Identification

**Goal**: Produce a prioritized gene list (≥5 genes) with evidence levels.

**Steps**:

1. **Collect genes** from top candidate diseases via Orphanet and OMIM results.

2. **ClinGen validity check** (critical) — for each gene, call:
   - `ClinGen_search_gene_validity` → get classification (Definitive/Strong/Moderate/Limited/Disputed/Refuted)
   - `ClinGen_search_dosage_sensitivity` → get Haploinsufficiency (HI) and Triplosensitivity (TS) scores
   - `ClinGen_search_actionability` → note if gene has adult/pediatric actionability
   - Only include Definitive, Strong, or Moderate genes in the primary panel. Flag Limited; exclude Disputed/Refuted.

3. **Expression validation** — for affected tissue relevance:
   - Get Ensembl ID via `MyGene_query_genes` (param: `q`)
   - Call `GTEx_get_median_gene_expression` (param: `gencode_id`, versioned). TPM >1 = expressed.

4. **Constraint scores** — call `gnomAD_get_gene_constraints` for pLI scores. pLI >0.9 = high constraint (intolerant to loss-of-function).

5. **Prioritize** using this scoring:

| Criteria | Points |
|----------|--------|
| Gene causes #1 ranked disease | +5 |
| Gene causes multiple candidate diseases | +3 |
| ClinGen Definitive | +3 |
| Expressed in affected tissue (TPM >1) | +2 |
| pLI >0.9 | +1 |
| HI score = 3 | +1 |
| Clinically actionable (ClinGen) | +1 |

**Report section output**:
```markdown
## 3. Recommended Gene Panel

| Priority | Gene | Evidence (ClinGen) | pLI | Expression | Associated Diseases |
|----------|------|--------------------|-----|------------|---------------------|
| ★★★ | FBN1 | Definitive | 1.00 | Heart, aorta | Marfan syndrome |
| ★★★ | TGFBR1 | Definitive | 0.98 | Ubiquitous | Loeys-Dietz 1 |

Minimum panel (high yield): [genes]
Extended panel (+differential): [genes]
Testing strategy: 1. Start with [gene] (highest probability). 2. If negative, proceed to full panel. 3. Consider WES if panel negative.
```

---

## Phase 3.5: Expression & Tissue Context

Perform when tissue specificity matters for candidate prioritization.

- **CELLxGENE** (`CELLxGENE_get_expression_data`, params: `gene`, `tissue`) — confirms expression in disease-relevant cell types (e.g., fibroblasts for connective tissue disorders). Mean expression >1.0 = relevant.
- **ChIPAtlas** (`ChIPAtlas_enrichment_analysis`, params: `gene`, `cell_type`) — identifies transcription factors regulating the gene; helps interpret regulatory variants near the gene.
- **ENCODE** (`ENCODE_search_experiments`) — use for ATAC-seq or ChIP-seq open chromatin data as supplemental regulatory evidence.

Add a brief "Expression & Regulatory Context" table to the report showing top expressing cell types and key TF regulators for the top 3 candidate genes.

---

## Phase 3.6: Pathway & Network Analysis

Perform when a shared biological mechanism is suspected across candidates.

- **KEGG** (`kegg_find_genes` then `kegg_get_gene_info`) — identifies pathway membership for each candidate gene (e.g., TGF-beta signaling hsa04350, ECM-receptor hsa04512).
- **Reactome** (`reactome_search_pathways`) — provides biological process context.
- **IntAct** (`intact_search_interactions`, params: `query`, `species="human"`) — retrieves direct protein-protein interaction partners. Note notable interactors and complex membership.

Look for convergent pathways (≥2 candidate genes sharing a pathway) and document in the report. This strengthens the biological plausibility of a shared etiology.

---

## Phase 4: Variant Interpretation

Perform when the clinician provides a specific variant (HGVS notation or genomic coordinates).

**Steps**:

1. **ClinVar lookup** — call `ClinVar_search_variants` with the HGVS string. Note classification, review status (expert panel = strongest), and associated conditions. If you have a ClinVar ID, use `ClinVar_get_variant_by_id` with param `id` (not `variant_id`).

2. **Population frequency** — call `gnomAD_get_variant_frequencies` (param: `variant_id` in format `chrom-pos-ref-alt`, e.g. `15-48942946-G-A`). Classify rarity:
   - AF <0.00001 → Ultra-rare (PM2 Moderate)
   - AF 0.00001–0.0001 → Rare
   - AF >0.01 → Likely benign (BA1 if >5%)

3. **Computational predictions** (for missense/splice VUS):
   - `CADD_get_variant_score` (params: `chrom`, `pos`, `ref`, `alt`, `version="GRCh38-v1.7"`) — PHRED ≥20 = top 1% deleterious.
   - `AlphaMissense_get_variant_score` (params: `uniprot_id`, `variant` e.g. `E1541K`) — score >0.564 = pathogenic. ~90% accuracy. Strongest single predictor for missense.
   - `EVE_get_variant_score` (params: `chrom`, `pos`, `ref`, `alt`) — score >0.5 = likely pathogenic.
   - `SpliceAI_predict_splice` (params: `variant` format `chr15-48942946-G-A`, `genome="38"`) — use for intronic, synonymous, or exon-proximal variants. Max delta ≥0.5 = splice impact.

   Strategy: run all applicable predictors. ≥2 concordant damaging → strong PP3. ≥2 concordant benign → BP4. Discordant → weight AlphaMissense for missense, SpliceAI for splice.

4. **ACMG criteria** — systematically evaluate and document:

| Criterion | Evidence | Strength |
|-----------|----------|----------|
| PVS1 | Null variant where LOF is disease mechanism | Very Strong |
| PS1 | Same amino acid change as known pathogenic | Strong |
| PM2 | Absent from population databases (gnomAD) | Moderate |
| PM1 | In critical functional domain | Moderate |
| PP3 | ≥2 concordant computational predictors | Supporting |
| BP4 | ≥2 concordant benign predictors | Supporting benign |
| BA1 | AF >5% in gnomAD | Benign standalone |

**Report section output**:
```markdown
## 4. Variant Interpretation

Variant: FBN1 c.4621G>A (p.Glu1541Lys)
ClinVar: VUS | gnomAD AF: 0.000004 (Ultra-rare, PM2)

| Predictor | Score | Result | ACMG |
|-----------|-------|--------|------|
| AlphaMissense | 0.78 | Pathogenic | PP3 (strong) |
| CADD PHRED | 28.5 | Top 0.1% deleterious | PP3 |
| EVE | 0.72 | Likely pathogenic | PP3 |

Consensus: 3/3 concordant damaging → Strong PP3 support
Preliminary classification: Likely Pathogenic (PM2 + strong PP3 + PP4)
```

---

## Phase 5: Structure Analysis for VUS

Perform when: variant is VUS, missense in a critical domain, novel variant, or conflicting interpretations.

**Steps**:

1. Retrieve protein sequence from UniProt (`UniProt_get_protein_by_accession`).
2. Call `NvidiaNIM_alphafold2` (params: `sequence`, `algorithm="mmseqs2"`, `relax_prediction=False`). Requires `NVIDIA_API_KEY`. Rate limit: 40 RPM. May return HTTP 202 (pending) — handled internally.
3. Extract pLDDT at the variant position. pLDDT >70 = high confidence region; variant in a structured region is more interpretable.
4. Call `InterPro_get_protein_domains` (param: `accession` = UniProt ID) to check whether the variant position falls within a functional domain.
5. Check for nearby known pathogenic variants at adjacent residues (same domain) — this supports PM1 and PS1.

**Structural evidence mapping to ACMG**:
- Variant in well-defined functional domain (pLDDT >70) + domain known to be disease mechanism → PM1
- Variant adjacent to known pathogenic position, same mechanism → PS1 candidate

**Report section output**:
```markdown
## 5. Structural Analysis

Method: AlphaFold2 via NVIDIA NIM | Protein: FBN1 (P35555)
Mean pLDDT: 85.3 | Variant position pLDDT: 92.1 (high confidence)
Domain: cbEGF-like domain 23 (calcium-binding; residues 1530–1570)

p.Glu1541Lys: charge reversal at Ca2+-coordinating residue.
Adjacent pathogenic variant: p.Glu1540Lys (Pathogenic in ClinVar).
Structural evidence: Strong PM1 support (critical domain).
```

---

## Phase 6: Literature Evidence

Gather supporting publications to contextualize the diagnosis and variants.

**Steps**:

1. **PubMed** — call `PubMed_search_articles` with disease name AND genetics/mutation/variant. Also search top gene names. Use quoted phrases for precision.

2. **Preprints** — bioRxiv and medRxiv have no public search API; use `EuropePMC_search_articles` with `source="PPR"`. If you have a DOI starting with `10.1101/`, call `BioRxiv_get_preprint` for full metadata. Always flag preprints as not peer-reviewed.

3. **Citation analysis** — use `openalex_search_works` to find citation counts and assess landmark papers. High-citation studies carry more evidential weight.

4. **AI-ranked search** — `SemanticScholar_search_papers` for broader discovery when primary searches return sparse results.

Include a literature summary table in the report (PMID, title, year, citation count, relevance) and a note on evidence type (case reports vs. functional studies vs. clinical trials).

---

## Phase 7: Report Synthesis

Complete the report file and deliver:

1. Fill the **Executive Summary** with the most likely diagnosis, supporting evidence strength, and urgency flags.
2. Fill **Clinical Recommendations**:
   - ≥3 specific next steps in priority order
   - Specialist referrals (clinical genetics, relevant subspecialty)
   - Family screening plan based on inheritance pattern
   - Follow-up timeline
3. Fill **Data Gaps & Limitations** — document any unavailable data (API keys missing, tool errors, absent ClinVar record) and suggest alternatives.
4. Remove all `[Researching...]` placeholders.
5. Finalize the gene panel CSV and variant interpretation CSV if applicable.

**Urgent findings protocol** — flag prominently if any of these are found:
- Pathogenic variant in an actionable gene
- Aortic pathology risk (immediate referral)
- Metabolic emergency risk
- Cancer predisposition syndrome

---

## Evidence Grading

| Tier | Symbol | Criteria |
|------|--------|----------|
| T1 | ★★★ | Phenotype match >80% AND pathogenic variant, OR clinical diagnostic criteria met |
| T2 | ★★☆ | Phenotype 60–80% OR likely pathogenic variant |
| T3 | ★☆☆ | Phenotype 40–60% OR VUS in candidate gene |
| T4 | ☆☆☆ | Phenotype <40% OR no supporting genetic evidence |

---

## Known Gotchas

| Issue | Detail |
|-------|--------|
| `MyGene_query_genes` param | Use `q`, not `gene` |
| `ClinVar_get_variant_by_id` param | Use `id`, not `variant_id` |
| `OpenTargets` Ensembl param | `ensemblId` (camelCase), not `ensemblID` |
| `gnomAD_get_variant_frequencies` format | `variant_id` must be `chrom-pos-ref-alt`, not HGVS |
| `GTEx_get_median_gene_expression` | `gencode_id` must be versioned (e.g. `ENSG00000166147.15`) |
| OMIM API | Requires `OMIM_API_KEY`; register at omim.org/api |
| DisGeNET API | Requires `DISGENET_API_KEY`; free registration at disgenet.org |
| NVIDIA NIM | Requires `NVIDIA_API_KEY`; 40 RPM rate limit; AlphaFold2 may return HTTP 202 (polling handled internally) |
| BioRxiv search | No public search API — use `EuropePMC_search_articles` with `source="PPR"` instead |
| AlphaMissense input | Variant format is amino acid change only (e.g. `E1541K`), not full HGVS |
| SpliceAI variant format | `chr{chrom}-{pos}-{ref}-{alt}` (with `chr` prefix), not bare coordinates |
| OMIM `mim_number` | Must be passed as a string, not integer |
| Preprints in reports | Always flag preprints as not peer-reviewed |
| DisGeNET `search_disease` | Disease name search can be noisy; use `min_score=0.3` to filter |

---

## Tool Reference

For full parameter tables and fallback chains, see [references/tools.md](references/tools.md).

| Tool | Purpose |
|------|---------|
| `HPO_search_terms` | Convert symptom text to HPO terms |
| `HPO_get_term_diseases` | Get diseases associated with an HPO term |
| `Orphanet_search_diseases` | Search rare diseases by keyword |
| `Orphanet_get_genes` | Get causative genes for an Orphanet disease |
| `OMIM_search` | Search OMIM by gene or disease name |
| `OMIM_get_entry` | Full OMIM entry text and inheritance |
| `OMIM_get_clinical_synopsis` | Organ-system phenotype features |
| `DisGeNET_search_gene` | Gene-to-disease associations with GDA scores |
| `DisGeNET_search_disease` | Disease-to-gene associations |
| `ClinGen_search_gene_validity` | Authoritative gene-disease validity classification |
| `ClinGen_search_dosage_sensitivity` | Haploinsufficiency/triplosensitivity scores |
| `ClinGen_search_actionability` | Clinical actionability for return of findings |
| `OpenTargets_get_disease_associated_targets` | Genes associated with a disease (EFO ID) |
| `MyGene_query_genes` | Gene search, returns Ensembl/Entrez IDs |
| `GTEx_get_median_gene_expression` | Bulk tissue expression (TPM) |
| `CELLxGENE_get_expression_data` | Single-cell expression by tissue/cell type |
| `ChIPAtlas_enrichment_analysis` | TF binding enrichment near a gene |
| `gnomAD_get_gene_constraints` | pLI, LOEUF constraint scores |
| `kegg_find_genes` | Find gene in KEGG for pathway lookup |
| `kegg_get_gene_info` | Gene pathway membership |
| `reactome_search_pathways` | Biological process pathways |
| `intact_search_interactions` | Protein-protein interactions |
| `ClinVar_search_variants` | Variant pathogenicity classification |
| `ClinVar_get_variant_by_id` | ClinVar record by ID (param: `id`) |
| `gnomAD_get_variant_frequencies` | Population allele frequencies |
| `AlphaMissense_get_variant_score` | DeepMind missense pathogenicity (~90% accuracy) |
| `CADD_get_variant_score` | CADD deleteriousness score |
| `EVE_get_variant_score` | Evolutionary variant effect prediction |
| `SpliceAI_predict_splice` | Splice-altering effect prediction |
| `NvidiaNIM_alphafold2` | Protein structure prediction (AlphaFold2) |
| `InterPro_get_protein_domains` | Functional domain annotation |
| `UniProt_get_protein_by_accession` | Protein sequence and features |
| `PubMed_search_articles` | Published literature search |
| `EuropePMC_search_articles` | Preprint search (use `source="PPR"`) |
| `openalex_search_works` | Citation analysis and publication metrics |
| `SemanticScholar_search_papers` | AI-ranked literature search |
