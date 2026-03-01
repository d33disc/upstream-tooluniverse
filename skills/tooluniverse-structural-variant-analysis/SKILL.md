---
name: tooluniverse-structural-variant-analysis
description: Comprehensive structural variant (SV) analysis skill for clinical genomics. Classifies SVs (deletions, duplications, inversions, translocations), assesses pathogenicity using ACMG-adapted criteria, evaluates gene disruption and dosage sensitivity, and provides clinical interpretation with evidence grading. Use when analyzing CNVs, large deletions/duplications, chromosomal rearrangements, or any structural variants requiring clinical interpretation.
---

# Structural Variant Analysis Workflow

Systematic analysis of structural variants (deletions, duplications, inversions, translocations, complex rearrangements) for clinical genomics interpretation using ACMG-adapted criteria.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create SV_analysis_report.md FIRST, then populate progressively
2. **ACMG-style classification** - Pathogenic/Likely Pathogenic/VUS/Likely Benign/Benign with explicit evidence
3. **Evidence grading** - Grade all findings by confidence level (★★★/★★☆/★☆☆)
4. **Dosage sensitivity critical** - Gene dosage effects drive SV pathogenicity
5. **Breakpoint precision matters** - Exact gene disruption vs dosage-only effects
6. **Population context essential** - gnomAD SVs for frequency assessment
7. **English-first queries** - Always use English terms in tool calls (gene names, disease names), even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## When to Use / When Not to Use

**Use this skill for**: SVs ≥50 bp — deletions, duplications, inversions, translocations, complex rearrangements.

**Do NOT use for**: SNVs, small indels (<50 bp), somatic cancer variants, mitochondrial variants, repeat expansions. Use `tooluniverse-variant-interpretation` for those.

---

## Workflow Overview

```
Phase 1: SV IDENTITY & CLASSIFICATION
  Normalize coordinates, determine type (DEL/DUP/INV/TRA/CPX), calculate size

Phase 2: GENE CONTENT ANALYSIS
  Identify fully contained, partially disrupted, and flanking genes; annotate function

Phase 3: DOSAGE SENSITIVITY ASSESSMENT
  ClinGen HI/TS scores, pLI (gnomAD), ClinGen gene validity, OMIM inheritance

Phase 4: POPULATION FREQUENCY CONTEXT
  ClinVar overlapping SVs, DECIPHER patient cases, gnomAD SV frequency

Phase 5: PATHOGENICITY SCORING
  Weighted 0-10 score: gene content (40%) + dosage sensitivity (30%)
                       + population frequency (20%) + clinical evidence (10%)

Phase 6: LITERATURE & CLINICAL EVIDENCE
  PubMed searches, DECIPHER cohort phenotypes, functional study evidence

Phase 7: ACMG-ADAPTED CLASSIFICATION
  Apply SV-specific evidence codes; derive final Pathogenic/LP/VUS/LB/Benign
```

---

## Phase 1: SV Identity & Classification

**Goal**: Standardize SV notation and classify type before any database queries.

**Capture**:
- Chromosome(s), start/end coordinates (note genome build: hg19/hg38)
- SV type: DEL / DUP / INV / TRA / CPX
- Size in bp or Mb
- Breakpoint precision (e.g., ±5 kb for array, ±50 bp for WGS)
- Inheritance: de novo / inherited / unknown

**SV Types and Molecular Effects**:
| Type | Effect |
|------|--------|
| DEL | Haploinsufficiency, gene disruption |
| DUP | Triplosensitivity, gene dosage imbalance |
| INV | Disruption at breakpoints, position effects |
| TRA | Gene fusions, disruption, position effects |
| CPX | Variable; break into components |

**Example notation**: `arr[GRCh38] 17q21.31(44039927-44352659)x1` → 313 kb heterozygous deletion, genes MAPT and KANSL1 fully contained.

---

## Phase 2: Gene Content Analysis

**Goal**: Annotate all genes affected by the SV.

**Gene categories**:
1. **Fully contained** — entire gene within SV boundaries (deletion = haploinsufficiency; duplication = extra copy)
2. **Partially disrupted** — breakpoint within gene (likely LOF; check critical domains)
3. **Flanking** — within 1 Mb of breakpoints (possible position/regulatory effects)

**Tools to call**:
- `Ensembl_lookup_gene` — gene boundaries, exon structure, coordinates
- `NCBI_gene_search` — official symbol, aliases, description
- `OMIM_search` then `OMIM_get_entry` — disease associations, inheritance mode
- `DisGeNET_search_gene` — additional gene-disease evidence with scores
- `Gene_Ontology_get_term_info` — biological process / molecular function

**Report section format**:
```markdown
### 2.1 Fully Contained Genes
| Gene | Function | Disease | Inheritance | Evidence |
| KANSL1 | Histone acetyltransferase | Koolen-De Vries (OMIM 610443) | AD | ★★★ |

### 2.2 Partially Disrupted Genes
| Gene | Breakpoint Location | Domains Lost | Effect |

### 2.3 Flanking Genes (Potential Position Effects)
| Gene | Distance | Regulatory Risk |
```

---

## Phase 3: Dosage Sensitivity Assessment

**Goal**: Determine whether affected genes are dosage-sensitive (haploinsufficient or triplosensitive).

**Tools to call**:
- `ClinGen_search_dosage_sensitivity` — gold-standard HI/TS scores (0–3)
- `ClinGen_search_gene_validity` — gene-disease classification level (Definitive/Strong/Moderate)
- `gnomad_search` — pLI score for LoF intolerance
- `OMIM_get_entry` — confirm AD/AR inheritance (AD strongly suggests HI)

**Score interpretation**:

ClinGen HI/TS Scores:
- 3 = Sufficient evidence for dosage sensitivity → treat as dosage-sensitive
- 2 = Emerging evidence → likely dosage-sensitive
- 1 = Little evidence → uncertain
- 0 = No evidence → not established

pLI (gnomAD):
- ≥0.9 → extremely LoF-intolerant (likely HI)
- 0.5–0.9 → moderately intolerant
- <0.5 → tolerant (probably NOT HI)

**Report section format**:
```markdown
### 3.1 Haploinsufficient Genes
| Gene | ClinGen HI | pLI | Validity | Disease | Evidence |
| KANSL1 | 3 (Sufficient) | 0.99 | Definitive | Koolen-De Vries | ★★★ |

### 3.2 Triplosensitive Genes (for duplications)
| Gene | ClinGen TS | Disease Mechanism | Evidence |

### 3.3 Non-Dosage-Sensitive Genes
| Gene | HI | TS | Interpretation |
```

---

## Phase 4: Population Frequency Context

**Goal**: Determine if the SV is seen in the general population (supports benign) or is absent (supports pathogenic).

**Tools to call**:
- `ClinVar_search_variants` — known pathogenic/benign SVs at same locus
- `DECIPHER_search` — patient SVs with phenotypes (developmental disorder focus)

**Frequency thresholds** (ACMG-adapted):
| Frequency | ACMG Code | Interpretation |
|-----------|-----------|----------------|
| >1% in gnomAD SVs | BA1 (Stand-alone Benign) | Too common for rare disease |
| 0.1–1% | BS1 (Strong Benign) | Likely common benign variant |
| <0.01% | PM2 (Moderate Path.) | Rare, supports pathogenicity |
| Absent | PM2 (Moderate Path.) | Very rare |

**Reciprocal overlap rule**: Two SVs are considered "the same" when reciprocal overlap ≥70%:
```
Reciprocal Overlap = min(overlap/SV_A_length, overlap/SV_B_length)
```

**Note on gnomAD SVs**: Direct API access is not available via ToolUniverse. Query gnomAD SV via browser or note absence in report. ClinVar and DECIPHER are the primary queryable sources.

**Report section format**:
```markdown
### 4.1 ClinVar Matches
| VCV ID | Classification | Size | Reciprocal Overlap | Review Status |

### 4.2 DECIPHER Patient Cases
| Case ID | Phenotype Summary | Size | Overlap | Phenotype Match |

### 4.3 Frequency Interpretation
Absent from population databases → PM2 (Moderate)
```

---

## Phase 5: Pathogenicity Scoring

**Goal**: Quantitative 0–10 score to guide ACMG classification.

**Scoring weights**:
| Component | Max Points | Scale Factor |
|-----------|-----------|-------------|
| Gene content (HI/TS genes, disease genes) | 40 pts | → 0–4 |
| Dosage sensitivity (ClinGen definitive/emerging) | 30 pts | → 0–3 |
| Population frequency (absent=20, rare=10, common=−20) | ±20 pts | → ±2 |
| Clinical evidence (ClinVar match, DECIPHER, literature) | 10 pts | → 0–1 |

**Gene content rules**: +10 pts per HI/TS score-3 gene; +5 pts per score-2 gene; +2 pts per disease-associated gene; cap at 40.

**Dosage sensitivity rules**: ≥2 definitive genes = 30 pts; 1 definitive = 20 pts; emerging only = up to 10 pts.

**Score → Classification**:
| Score | Classification | Confidence |
|-------|---------------|------------|
| 9–10 | Pathogenic | ★★★ |
| 7–8 | Likely Pathogenic | ★★☆ |
| 4–6 | VUS | ★☆☆ |
| 2–3 | Likely Benign | ★★☆ |
| 0–1 | Benign | ★★★ |

---

## Phase 6: Literature & Clinical Evidence

**Goal**: Corroborate classification with published case reports, functional studies, and DECIPHER cohort data.

**Tools to call**:
- `PubMed_search` — use queries such as `"GENE" AND (haploinsufficiency OR "deletion syndrome")` and `"GENE" AND deletion AND [phenotype]`
- `EuropePMC_search` — additional coverage for European literature
- `DECIPHER_search` — cases matching the gene or region; report phenotype frequencies

**Key evidence to capture**:
- Functional studies confirming gene dosage sensitivity (mouse/zebrafish knockouts, patient cells)
- Cohort studies characterizing phenotype spectrum
- Penetrance and expressivity data for known syndromes

**ACMG codes from this phase**:
- **PS3** — well-established functional studies showing dosage sensitivity
- **PP4** — patient phenotype consistent with gene-disease association

---

## Phase 7: ACMG-Adapted Classification

**Goal**: Apply SV-specific evidence codes and derive final classification.

**Pathogenic codes**:
| Code | Strength | SV Application |
|------|----------|----------------|
| PVS1 | Very Strong | Complete deletion of established HI gene (ClinGen score 3) |
| PS1 | Strong | ≥70% reciprocal overlap with ClinVar pathogenic SV |
| PS2 | Strong | Confirmed de novo with consistent phenotype |
| PS3 | Strong | Functional studies demonstrate dosage sensitivity |
| PS4 | Strong | SV enriched in cases vs. controls |
| PM1 | Moderate | Breakpoint within critical exon of HI gene |
| PM2 | Moderate | Absent from gnomAD SVs and DGV |
| PM5 | Moderate | Nearby SVs in ClinVar classified pathogenic |
| PM6 | Moderate | De novo (parentage not confirmed) |
| PP1 | Supporting | Segregation with phenotype in family |
| PP2 | Supporting | Genes in SV match patient phenotype pathway |
| PP3 | Supporting | Computational predictors support HI |
| PP4 | Supporting | Patient phenotype matches gene-disease |

**Benign codes**:
| Code | Strength | SV Application |
|------|----------|----------------|
| BA1 | Stand-Alone | Frequency >5% in gnomAD SVs |
| BS1 | Strong | Frequency >1% |
| BS2 | Strong | SV in healthy adults without phenotype (caution: incomplete penetrance) |
| BS3 | Strong | Functional studies show no dosage effect |
| BS4 | Strong | Non-segregation with phenotype |
| BP2 | Supporting | Seen in trans with pathogenic variant; unaffected patient |
| BP4 | Supporting | Predictors suggest no HI |
| BP5 | Supporting | Phenotype explained by another variant |

**Classification rules**:
| Classification | Evidence Required |
|---------------|------------------|
| Pathogenic | PVS1 + PS1; OR ≥2 Strong; OR 1 Strong + 3 Moderate |
| Likely Pathogenic | 1 VS + 1 Mod; OR 1 Strong + 2 Mod; OR 3 Mod |
| VUS | Criteria not met or conflicting evidence |
| Likely Benign | 1 Strong Benign + 1 Supporting; OR ≥2 Supporting Benign |
| Benign | BA1; OR BS1 + BS2; OR ≥2 Strong Benign |

---

## Known Gotchas

1. **gnomAD SV has no direct API** — ToolUniverse has no tool for gnomAD structural variant frequencies. Use ClinVar and DECIPHER as proxies. Note the limitation explicitly in the report.

2. **ClinGen score 1 ≠ dosage-sensitive** — Score 1 means "little evidence," not "likely sensitive." Many labs incorrectly treat score 1 as supporting pathogenicity. Only scores 2–3 support dosage sensitivity.

3. **BA1 threshold for SVs is debated** — The 5% gnomAD threshold from SNV guidelines is often too high for SVs. Some ClinGen groups use 1% for SVs. Note which threshold you apply.

4. **BS2 requires caution** — "Healthy adult with SV" can be misleading if penetrance is incomplete (e.g., 22q11.2 deletion has ~5% healthy carriers). Do not apply BS2 for known reduced-penetrance syndromes.

5. **Reciprocal overlap matters** — A 95%-contained ClinVar pathogenic SV does not qualify as PS1 if the query SV is 3x larger (reciprocal overlap would be ~32%). Always compute both directions.

6. **DECIPHER access** — DECIPHER data may not be publicly queryable via API for all cases. If `DECIPHER_search` returns empty, note this limitation rather than asserting absence.

7. **Position effects are rare** — Flanking gene position effects are real but uncommon. Do not over-interpret; apply PP2/PP3 at Supporting strength only when phenotype is unexplained by contained genes.

8. **Balanced translocations** — If no genes are disrupted, classification is usually VUS or Likely Benign. The primary clinical concern is reproductive risk (unbalanced offspring), not the carrier phenotype.

9. **pLI vs. LOEUF** — Newer gnomAD versions report LOEUF (loss-of-function observed/expected upper bound) rather than pLI. LOEUF <0.35 is the equivalent of pLI ≥0.9. Prefer LOEUF for gnomAD v4+.

10. **OMIM gene vs. phenotype entries** — OMIM has both gene entries (e.g., 605543 for KANSL1) and phenotype entries (e.g., 610443 for Koolen-De Vries syndrome). Search for both; gene entries list inheritance mode most reliably.

---

## Output: Report File

**Filename convention**: `SV_analysis_[TYPE]_chr[CHR]_[START]_[END]_[GENES].md`

Example: `SV_analysis_DEL_chr17_44039927_44352659_KANSL1_MAPT.md`

**Report structure**:
```markdown
# SV Analysis Report: [SV_IDENTIFIER]

## Executive Summary
| Field | Value |
| SV Type | DEL / DUP / INV / TRA / CPX |
| Coordinates | chrN:start-end (GRCh38) |
| Size | X kb / X Mb |
| Gene Content | N fully contained, N partially disrupted |
| Classification | Pathogenic / LP / VUS / LB / Benign |
| Pathogenicity Score | X.X / 10 |
| Confidence | ★★★ / ★★☆ / ★☆☆ |
| Key Finding | [one sentence] |

Clinical Action: Required / Recommended / None

## 1. SV Identity & Classification
## 2. Gene Content Analysis (2.1 Contained / 2.2 Disrupted / 2.3 Flanking)
## 3. Dosage Sensitivity (3.1 HI / 3.2 TS / 3.3 Non-dosage-sensitive)
## 4. Population Frequency (4.1 ClinVar / 4.2 DECIPHER / 4.3 Interpretation)
## 5. Pathogenicity Scoring (score table + key drivers)
## 6. Literature & Clinical Evidence (papers, DECIPHER cohort, functional)
## 7. ACMG-Adapted Classification (evidence codes, final class, strengths/limitations)
## 8. Clinical Recommendations
   8.1 For affected individual (testing, surveillance)
   8.2 For family members (cascade testing, counseling)
   8.3 Reproductive considerations (recurrence risk, prenatal options)
## 9. Limitations & Uncertainties
## Data Sources
```

---

## Special Scenarios

**Recurrent microdeletion syndrome** (e.g., 22q11.2, 17q21.31):
- Verify recurrence mechanism (LCRs / NAHR); look for founder effects; note incomplete penetrance and variable expressivity.

**Balanced translocation, no gene disruption**:
- Classification: usually VUS or Likely Benign. Primary concern is reproductive risk for unbalanced offspring.

**Complex rearrangement (chromothripsis)**:
- Break into component SVs; assess each breakpoint independently; consider cumulative gene dosage effects and DNA repair pathway involvement.

**Small in-frame deletion/duplication**:
- May not cause haploinsufficiency. Check critical domain involvement, ClinVar for similar variants; may need functional studies.

---

## Quantified Minimums

| Section | Minimum Requirement |
|---------|---------------------|
| Gene content | All genes in SV region annotated |
| Dosage sensitivity | ClinGen scores queried for all disease-relevant genes |
| Population frequency | ClinVar + DECIPHER queried (gnomAD SV noted if inaccessible) |
| Literature | ≥2 search strategies (gene-specific + SV/syndrome-specific) |
| ACMG codes | All applicable codes listed with explicit rationale |

---

## Evidence Grading System

| Symbol | Confidence | Criteria |
|--------|------------|----------|
| ★★★ | High | ClinGen Definitive, ClinVar expert-reviewed, multiple independent studies |
| ★★☆ | Moderate | ClinGen Strong/Moderate, single well-designed study, DECIPHER cohort support |
| ★☆☆ | Limited | Computational predictions only, case reports, emerging evidence |

---

## Clinical Recommendations Framework

**Pathogenic / Likely Pathogenic**:
- Genetic counseling; phenotype-specific surveillance; cascade testing for family members
- Balanced translocation carriers: reproductive counseling re: unbalanced offspring risk

**VUS**:
- Base clinical management on phenotype, not genotype
- Reinterpret in 1–2 years or when phenotype evolves
- Segregation analysis in family may reclassify

**Likely Benign / Benign**:
- Not expected to cause rare disease
- Cascade testing generally not indicated (exception: balanced translocation reproductive risk)

---

## Tool Reference

| Tool | Purpose |
|------|---------|
| `ClinGen_search_dosage_sensitivity` | HI/TS scores (0–3) for genes |
| `ClinGen_search_gene_validity` | Gene-disease classification (Definitive/Strong/Moderate) |
| `ClinVar_search_variants` | Overlapping known pathogenic/benign SVs |
| `DECIPHER_search` | Patient SVs with phenotypes (developmental disorders) |
| `Ensembl_lookup_gene` | Gene coordinates, exon structure |
| `OMIM_search` | Disease entries by gene symbol |
| `OMIM_get_entry` | Entry details including inheritance mode |
| `DisGeNET_search_gene` | Gene-disease associations with evidence scores |
| `gnomad_search` | pLI / LOEUF scores for LoF intolerance |
| `PubMed_search` | Peer-reviewed literature for genes and SVs |
| `EuropePMC_search` | Additional literature coverage |
| `Gene_Ontology_get_term_info` | Gene biological process / molecular function |

Full parameter details: see `references/tools.md`

---

## See Also

- `EXAMPLES.md` — Sample SV interpretations
- `README.md` — Quick start guide
- `references/tools.md` — Full tool parameter reference
- `tooluniverse-variant-interpretation` — For SNVs and small indels
- ClinGen Dosage Sensitivity Map: https://www.ncbi.nlm.nih.gov/projects/dbvar/clingen/
- ACMG SV Guidelines: Riggs et al., Genet Med 2020 (PMID: 31690835)
