---
name: tooluniverse-infectious-disease
description: Rapid pathogen characterization and drug repurposing analysis for infectious disease outbreaks. Identifies pathogen taxonomy, essential proteins, predicts structures, and screens existing drugs via docking. Use when facing novel pathogens, emerging infections, or needing rapid therapeutic options during outbreaks.
---

# Infectious Disease Outbreak Intelligence

Rapid response system for emerging pathogens using taxonomy analysis, target identification, structure prediction, and computational drug repurposing.

**KEY PRINCIPLES**:
1. **Speed is critical** - Optimize for rapid actionable intelligence
2. **Target essential proteins** - Focus on conserved, essential viral/bacterial proteins
3. **Leverage existing drugs** - Prioritize FDA-approved compounds for repurposing
4. **Structure-guided** - Use NvidiaNIM for rapid structure prediction and docking
5. **Evidence-graded** - Grade repurposing candidates by evidence strength
6. **Actionable output** - Prioritized drug candidates with rationale
7. **English-first queries** - Always use English terms in tool calls (pathogen names, protein names, drug names), even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## When to Use

Apply when user asks:
- "New pathogen detected - what drugs might work?"
- "Emerging virus [X] - therapeutic options?"
- "Drug repurposing candidates for [pathogen]"
- "What do we know about [novel coronavirus/bacteria]?"
- "Essential targets in [pathogen] for drug development"
- "Can we repurpose [drug] against [pathogen]?"

---

## Critical Workflow Requirements

### 1. Report-First Approach (MANDATORY)

1. **Create the report file FIRST**:
   - File name: `[PATHOGEN]_outbreak_intelligence.md`
   - Initialize with section headers
   - Add placeholder: `[Analyzing...]`

2. **Progressively update** as you gather data

3. **Output separate files**:
   - `[PATHOGEN]_drug_candidates.csv` - Ranked repurposing candidates
   - `[PATHOGEN]_target_proteins.csv` - Druggable targets

### 2. Citation Requirements (MANDATORY)

Every data point must cite the source tool and identifier. Example:

```
### Target: RNA-dependent RNA polymerase (RdRp)
- **UniProt**: P0DTD1 (NSP12)
- **Essentiality**: Required for replication
- **Conservation**: >95% across variants
- **Drug precedent**: Remdesivir targets RdRp

*Source: UniProt via `UniProt_search`, literature review*
```

---

## Phase 0: Tool Verification

### Known Parameter Corrections

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `NCBI_Taxonomy_search` | `name` | `query` |
| `UniProt_search` | `name` | `query` |
| `ChEMBL_search_targets` | `target` | `query` |
| `NvidiaNIM_diffdock` | `protein_file` | `protein` (content, not path) |
| `NvidiaNIM_alphafold2` | `seq` | `sequence` |

---

## Workflow Overview

```
Phase 1: Pathogen Identification
├── Taxonomic classification
├── Closest relatives (for knowledge transfer)
├── Genome/proteome availability
└── OUTPUT: Pathogen profile
    ↓
Phase 2: Target Identification
├── Essential genes/proteins
├── Conserved across strains
├── Druggability assessment
└── OUTPUT: Prioritized target list
    ↓
Phase 3: Structure Prediction (NvidiaNIM)
├── AlphaFold2/ESMFold for targets
├── Binding site identification
├── Quality assessment (pLDDT)
└── OUTPUT: Target structures
    ↓
Phase 4: Drug Repurposing Screen
├── Approved drugs for related pathogens
├── Broad-spectrum antivirals/antibiotics
├── Docking screen (NvidiaNIM_diffdock)
└── OUTPUT: Candidate drugs
    ↓
Phase 4.5: Pathway Analysis
├── KEGG: Pathogen metabolism pathways
├── Essential metabolic targets
├── Host-pathogen interaction pathways
└── OUTPUT: Pathway-based drug targets
    ↓
Phase 5: Literature Intelligence
├── PubMed: Published outbreak reports
├── EuropePMC (source=PPR): Preprints (CRITICAL for outbreaks)
├── ArXiv: Computational/ML preprints
├── OpenAlex: Citation tracking
└── OUTPUT: Evidence synthesis
    ↓
Phase 6: Report Synthesis
├── Top drug candidates
├── Clinical trial opportunities
├── Recommended immediate actions
└── OUTPUT: Final report
```

---

## Phase 1: Pathogen Identification

### 1.1 Taxonomic Classification

Call `NCBI_Taxonomy_search` with `query=<pathogen_name>`. Extract `taxid`, `scientific_name`, `rank`, and `lineage`. Determine pathogen type: virus, bacteria, fungus, or parasite.

### 1.2 Related Pathogens (Knowledge Transfer)

Use the TaxID to find family/genus-level relatives. For each relative, call `ChEMBL_search_targets` with the relative's scientific name to detect existing drug precedent. Relatives with approved drugs are high-value knowledge transfer sources.

### 1.3 Output Section

```markdown
## 1. Pathogen Profile

### 1.1 Taxonomic Classification

| Property | Value |
|----------|-------|
| **Organism** | SARS-CoV-2 |
| **Taxonomy ID** | 2697049 |
| **Type** | RNA virus (positive-sense, single-stranded) |
| **Family** | Coronaviridae |
| **Genus** | Betacoronavirus |
| **Lineage** | Riboviria > Orthornavirae > Pisuviricota > Pisoniviricetes > Nidovirales |

### 1.2 Related Pathogens with Drug Precedent

| Relative | Similarity | Approved Drugs | Relevance |
|----------|------------|----------------|-----------|
| SARS-CoV | 79% genome | Remdesivir (EUA) | High |
| MERS-CoV | 50% genome | None approved | Medium |
| HCoV-229E | 45% genome | None specific | Low |

*Source: NCBI Taxonomy, ChEMBL*
```

---

## Phase 2: Target Identification

### 2.1 Essential Protein Identification

Call `UniProt_search` with `query="organism:<taxid>"` and `reviewed=True`. For each protein, check `ChEMBL_search_targets` with the gene name to find drug precedent. Rank targets by the criteria below.

### 2.2 Target Prioritization Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Essentiality** | 30% | Required for replication/survival |
| **Conservation** | 25% | Conserved across strains/variants |
| **Druggability** | 25% | Structural features amenable to binding |
| **Drug precedent** | 20% | Existing drugs for homologous targets |

### 2.3 Pathogen-Specific Essential Targets

**Viruses** — Always check: RNA/DNA polymerase (replication), main protease (polyprotein cleavage), entry proteins (cell attachment/fusion), helicase (RNA unwinding).

**Bacteria** — Always check: cell wall synthesis (penicillin-binding proteins), DNA gyrase/topoisomerase, ribosomal proteins (23S/16S rRNA targets), essential metabolic enzymes.

**Drug-resistant pathogens** — Document resistance genes (e.g., beta-lactamases, efflux pumps). Prioritize drugs with novel mechanisms unaffected by known resistance.

### 2.4 Output Section

```markdown
## 2. Druggable Targets

| Rank | Target | UniProt | Function | Score | Drug Precedent |
|------|--------|---------|----------|-------|----------------|
| 1 | RdRp (NSP12) | P0DTD1 | RNA replication | 92 | Remdesivir |
| 2 | Main protease (Mpro) | P0DTD1 | Polyprotein cleavage | 88 | Nirmatrelvir |
| 3 | Papain-like protease | P0DTD1 | Polyprotein cleavage | 75 | GRL0617 |

*Source: UniProt via `UniProt_search`, ChEMBL via `ChEMBL_search_targets`*
```

---

## Phase 3: Structure Prediction

### 3.1 Choosing a Predictor

For urgent outbreaks, start with `NvidiaNIM_esmfold` (synchronous, ~30 seconds). Switch to `NvidiaNIM_alphafold2` for production-quality structures needed for reliable docking (asynchronous, 5-15 min, may return HTTP 202 requiring polling).

Pass the protein sequence as the `sequence` parameter. The response contains PDB-format structure content and a `plddt` array.

### 3.2 Structure Quality Assessment

| pLDDT Range | Confidence | Use for Docking |
|-------------|------------|-----------------|
| >90 | Very High | Excellent |
| 70-90 | High | Good |
| 50-70 | Medium | Use with caution |
| <50 | Low | Not recommended |

Require mean pLDDT >70 and active site pLDDT >80 before docking.

### 3.3 Output Section

```markdown
## 3. Target Structures

| Target | Method | Length | Mean pLDDT | Docking Ready |
|--------|--------|--------|------------|---------------|
| RdRp (NSP12) | AlphaFold2 | 932 aa | 91.2 | Yes |
| Mpro | AlphaFold2 | 306 aa | 93.5 | Yes |

*Source: NVIDIA NIM via `NvidiaNIM_alphafold2`*
```

---

## Phase 4: Drug Repurposing Screen

### 4.1 Identify Repurposing Candidates

Three parallel search strategies:

1. **Related-pathogen drugs** — Call `ChEMBL_search_drugs` with `query=<pathogen_family>` and `max_phase=4` (approved only).
2. **Broad-spectrum agents** — Call `ChEMBL_search_drugs` with `query="broad spectrum antiviral"` (or antibiotic for bacteria), `max_phase=4`.
3. **Target-class drugs** — Call `DGIdb_get_drug_gene_interactions` with the gene names of top targets.

Deduplicate results across all three sources. Aim for at least 20 candidates.

### 4.2 Docking Screen

For each candidate drug SMILES, call `NvidiaNIM_diffdock` with:
- `protein` = PDB content of predicted structure (not a file path)
- `ligand` = SMILES string
- `num_poses` = 5 to 10

Always dock a known reference drug first to calibrate scores. Rank candidates by top pose confidence score.

### 4.3 Output Section

```markdown
## 4. Drug Repurposing Screen

| Rank | Drug | Indication | Docking Score | Evidence |
|------|------|------------|---------------|----------|
| 1 | Remdesivir | COVID-19 | 0.92 | ★★★ FDA approved |
| 2 | Favipiravir | Influenza | 0.87 | ★★☆ Phase 3 COVID |
| 3 | Sofosbuvir | HCV | 0.84 | ★★☆ In vitro active |

*Source: NVIDIA NIM via `NvidiaNIM_diffdock`, ChEMBL via `ChEMBL_search_drugs`*
```

---

## Phase 4.5: Pathway Analysis

### 4.5.1 Pathogen Metabolism Pathways

Call `kegg_search_pathway` with `query="<pathogen_name> metabolism"` to find druggable metabolic pathways. Then call `kegg_get_pathway_genes` with the relevant pathway ID to enumerate essential gene targets. For host-pathogen interactions, search `kegg_search_pathway` with `query="<pathogen_name> host interaction"` and cross-reference using `Reactome_search_pathway` with `species="Homo sapiens"`.

### 4.5.2 Output Section

```markdown
## 4.5 Pathway Analysis

| Pathway | Essentiality | Drug Targets |
|---------|--------------|--------------|
| Viral replication (ko03030) | Essential | RdRp, Helicase |
| Viral protein processing | Essential | Mpro, PLpro |
| Host membrane interaction | Essential | Spike, ACE2 |

*Source: KEGG via `kegg_search_pathway`, Reactome*
```

---

## Phase 5: Literature Intelligence

### 5.1 Search Strategy

Run these in parallel:

- **Peer-reviewed**: `PubMed_search_articles` with `query="<pathogen> AND (outbreak OR treatment OR drug)"`, sort by date.
- **Preprints** (critical for emerging outbreaks): `EuropePMC_search_articles` with `source="PPR"`. Note: bioRxiv and medRxiv do not have direct search APIs — use EuropePMC as the gateway.
- **Computational/ML**: `ArXiv_search_papers` with `category="q-bio"`.
- **Citation ranking**: `openalex_search_works` or `SemanticScholar_search` for high-impact papers.
- **Clinical trials**: `search_clinical_trials` with `condition=<pathogen>` and `status="Recruiting"`.

Mark preprints clearly as NOT peer-reviewed.

### 5.2 Output Section

```markdown
## 5. Literature Intelligence

### Recent Findings

| Source | Title | Posted | Key Finding |
|--------|-------|--------|-------------|
| BioRxiv | Novel RdRp inhibitor shows activity... | 2024-02-01 | New candidate |
| MedRxiv | Real-world effectiveness of... | 2024-01-28 | Paxlovid 85% effective |

**Note**: Preprints are NOT peer-reviewed. Critical for rapid intelligence.

### Active Clinical Trials

| NCT ID | Phase | Drug | Status |
|--------|-------|------|--------|
| NCT05012345 | 3 | Ensitrelvir | Recruiting |

*Source: PubMed, EuropePMC (PPR), ArXiv, OpenAlex, ClinicalTrials.gov*
```

---

## Phase 6: Report Synthesis

Once all phases complete, update the report:

1. **Executive Summary** — Top 3 drug candidates with evidence tier, key discovery, recommended immediate action.
2. **Recommendations** — At least 3 immediate actions (e.g., stockpile specific drug, prepare supply chain, initiate surveillance).
3. **Clinical Trial Opportunities** — Drugs in Phase 2-3 with open slots.
4. **Research Priorities** — Targets lacking structural data, resistance surveillance needs.
5. **Data Gaps** — List what could not be determined and why.
6. **Data Sources** — Enumerate all tools and identifiers used.

Replace all `[Analyzing...]` placeholders before delivering the report.

---

## Report Template

File: `[PATHOGEN]_outbreak_intelligence.md`. Sections: Executive Summary, Pathogen Profile (1.1 Classification, 1.2 Related Pathogens), Druggable Targets (2.1 Prioritized, 2.2 Details), Target Structures (3.1 Predictions, 3.2 Binding Sites), Drug Repurposing Screen (4.1 Candidates, 4.2 Docking), Literature Intelligence (5.1 Findings, 5.2 Trials), Recommendations (6.1 Immediate Actions, 6.2 Trial Opportunities, 6.3 Research Priorities), Data Gaps, Data Sources.

Initialize each section with `[Analyzing...]` and replace before delivery. See [`references/tools.md`](references/tools.md) for the full skeleton template.

---

## Evidence Grading

| Tier | Symbol | Criteria | Example |
|------|--------|----------|---------|
| **T1** | ★★★ | FDA approved for this pathogen | Remdesivir for COVID |
| **T2** | ★★☆ | Clinical trial evidence OR approved for related pathogen | Favipiravir |
| **T3** | ★☆☆ | In vitro activity OR strong docking + mechanism | Sofosbuvir |
| **T4** | ☆☆☆ | Computational prediction only | Novel docking hits |

---

## Known Gotchas

### Tool Parameters
- `NCBI_Taxonomy_search`, `UniProt_search`, `ChEMBL_search_targets` all use `query=`, not `name=`.
- `NvidiaNIM_diffdock` expects `protein=<PDB content string>`, not a file path.
- `NvidiaNIM_alphafold2` uses `sequence=`, not `seq=`.
- bioRxiv and medRxiv have no direct search APIs — use `EuropePMC_search_articles` with `source="PPR"`.

### NVIDIA NIM
- Requires `NVIDIA_API_KEY` environment variable. If absent, fall back to `alphafold_get_prediction` or `NvidiaNIM_esmfold`.
- AlphaFold2 is asynchronous and may return HTTP 202. Poll until complete. ESMFold is synchronous and faster for triage.
- Respect rate limits (~40 RPM); allow ~1.5 seconds between calls.

### Drug Search
- `ChEMBL_search_drugs` with `max_phase=4` returns approved drugs only. Use `max_phase=3` to include late-stage candidates.
- SMILES strings for docking must come from a validated source (ChEMBL, PubChem). Malformed SMILES will fail silently.

### Preprints
- Preprints are not peer-reviewed. Always flag them explicitly in the report.
- EuropePMC returns preprints under `source="PPR"`. If a result has a `10.1101/` DOI, you can retrieve full metadata via `BioRxiv_get_preprint` or `MedRxiv_get_preprint`.

### Structure Quality
- Do not dock against structures with mean pLDDT <70. Use a fallback predictor or locate an existing PDB entry instead.
- Always dock a known reference drug first to establish a score baseline.

### Novel Pathogens
- For pathogens with no UniProt reviewed entries, also search with `reviewed=False` and filter manually.
- For fully novel pathogens with no relatives, broaden the drug search to "broad spectrum antiviral" or mechanism class (e.g., "nucleoside analog").

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `NvidiaNIM_alphafold2` | `alphafold_get_prediction` | `NvidiaNIM_esmfold` |
| `NvidiaNIM_diffdock` | `NvidiaNIM_boltz2` | Literature docking data |
| `NCBI_Taxonomy_search` | `UniProt_taxonomy` | Manual classification |
| `ChEMBL_search_drugs` | `DrugBank_search` | PubChem bioassays |
| `kegg_search_pathway` | `Reactome_search_pathway` | WikiPathways |
| `PubMed_search_articles` | `openalex_search_works` | `SemanticScholar_search` |
| `EuropePMC_search_articles` (PPR) | `web_search` (site:biorxiv.org) | ArXiv q-bio |

---

## Tool Reference

See [`references/tools.md`](references/tools.md) for the full tool table organized by phase (taxonomy, protein annotation, structure prediction, drug search, docking, pathway analysis, literature, clinical trials).

---

## Completeness Checklist

See [CHECKLIST.md](CHECKLIST.md) for the pre-delivery verification checklist.

Quick summary of minimums:

| Section | Minimum |
|---------|---------|
| Related pathogens | ≥3 with drug precedent |
| Druggable targets | ≥5 ranked targets |
| Structure predictions | ≥3 targets |
| Drug candidates screened | ≥20 |
| Docking results | Top 10 docked |
| Recommendations | ≥3 immediate actions |
