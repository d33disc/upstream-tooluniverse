---
name: tooluniverse-protein-therapeutic-design
description: Design novel protein therapeutics (binders, enzymes, scaffolds) using AI-guided de novo design. Uses RFdiffusion for backbone generation, ProteinMPNN for sequence design, ESMFold/AlphaFold2 for validation. Use when asked to design protein binders, therapeutic proteins, or engineer protein function.
---

# Therapeutic Protein Designer

AI-guided de novo protein design using RFdiffusion backbone generation, ProteinMPNN sequence optimization, and structure validation for therapeutic protein development.

**KEY PRINCIPLES**:
1. **Structure-first design** - Generate backbone geometry before sequence
2. **Target-guided** - Design binders with target structure in mind
3. **Iterative validation** - Predict structure to validate designs
4. **Developability-aware** - Consider aggregation, immunogenicity, expression
5. **Evidence-graded** - Grade designs by confidence metrics
6. **Actionable output** - Provide sequences ready for experimental testing
7. **English-first queries** - Always use English terms in tool calls (protein names, target names), even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## When to Use

Apply when user asks:
- "Design a protein binder for [target]"
- "Create a therapeutic protein against [protein/epitope]"
- "Design a protein scaffold with [property]"
- "Optimize this protein sequence for [function]"
- "Design a de novo enzyme for [reaction]"
- "Generate protein variants for [target binding]"

---

## Critical Workflow Requirements

### 1. Report-First Approach (MANDATORY)

1. **Create the report file FIRST**:
   - File name: `[TARGET]_protein_design_report.md`
   - Initialize with all section headers
   - Add placeholder: `[Designing...]`

2. **Progressively update** as designs are generated

3. **Output separate files**:
   - `[TARGET]_designed_sequences.fasta` - All designed sequences
   - `[TARGET]_top_candidates.csv` - Ranked candidates with metrics

### 2. Design Documentation (MANDATORY)

Every design MUST include:

```markdown
### Design: Binder_001

**Sequence**: MVLSPADKTN...
**Length**: 85 amino acids
**Target**: PD-L1 (UniProt: Q9NZQ7)
**Method**: RFdiffusion -> ProteinMPNN -> ESMFold validation

**Quality Metrics**:
| Metric | Value | Interpretation |
|--------|-------|----------------|
| pLDDT | 88.5 | High confidence |
| pTM | 0.82 | Good fold |
| ProteinMPNN score | -2.3 | Favorable |
| Predicted binding | Strong | Based on interface pLDDT |

*Source: NVIDIA NIM via `NvidiaNIM_rfdiffusion`, `NvidiaNIM_proteinmpnn`, `NvidiaNIM_esmfold`*
```

---

## Phase 0: Tool Verification

Confirm NVIDIA NIM tools are available before starting. All five tools require `NVIDIA_API_KEY`.

| Tool | Purpose |
|------|---------|
| `NvidiaNIM_rfdiffusion` | Backbone generation |
| `NvidiaNIM_proteinmpnn` | Sequence design |
| `NvidiaNIM_esmfold` | Fast structure validation |
| `NvidiaNIM_alphafold2` | High-accuracy validation |
| `NvidiaNIM_esm2_650m` | Sequence embeddings |

If `NVIDIA_API_KEY` is absent, stop and inform the user that NVIDIA NIM access is required.

---

## Workflow Overview

```
Phase 1: Target Characterization
├── Get target structure (PDB, EMDB cryo-EM, or AlphaFold)
├── Identify binding epitope
├── Analyze existing binders
└── OUTPUT: Target profile
    |
Phase 2: Backbone Generation (RFdiffusion)
├── Define design constraints
├── Generate >=5 backbones (diffusion_steps=50)
├── Filter by geometry quality
└── OUTPUT: Candidate backbones
    |
Phase 3: Sequence Design (ProteinMPNN)
├── Design >=8 sequences per backbone (temperature=0.1)
├── Score by ProteinMPNN likelihood
└── OUTPUT: Designed sequences
    |
Phase 4: Structure Validation
├── Predict structure (ESMFold fast; AlphaFold2 for top hits)
├── Check pLDDT >70 and pTM >0.7
└── OUTPUT: Validated designs
    |
Phase 5: Developability Assessment
├── Aggregation propensity, pI, cysteine count, MW
└── OUTPUT: Developability scores
    |
Phase 6: Report Synthesis
├── Ranked candidate list
├── Experimental recommendations
└── OUTPUT: Final report + FASTA + CSV
```

---

## Phase 1: Target Characterization

### 1.1 Get Target Structure

Try sources in priority order:

1. **PDB (X-ray/NMR)** - Call `PDB_search_by_uniprot` with the UniProt accession. If results are returned, retrieve the highest-resolution entry with `PDB_get_structure`.

2. **EMDB cryo-EM** - Preferred for membrane proteins, GPCRs, ion channels, and large complexes. Call `emdb_search` with the target name. For each result call `emdb_get_entry` to find associated PDB model IDs, then fetch the atomic model with `PDB_get_structure`. Prioritize entries with resolution <3 Å; accept up to 5 Å with caution.

3. **AlphaFold2 prediction (fallback)** - Retrieve the sequence via `UniProt_get_protein_sequence`, then call `NvidiaNIM_alphafold2` with `algorithm="mmseqs2"`. Label the result clearly as a predicted structure.

### 1.2 Identify Binding Epitope

- If the user specifies hotspot residues, use them directly.
- Otherwise, identify surface-exposed loops and known functional sites using `InterPro_get_protein_domains` and literature context.
- Document the selected epitope residue range in the report.

### 1.3 Report Output for Phase 1

```markdown
## 1. Target Characterization

| Property | Value |
|----------|-------|
| **Target** | PD-L1 (Programmed death-ligand 1) |
| **UniProt** | Q9NZQ7 |
| **Structure source** | PDB: 4ZQK (2.0 A resolution) |
| **Binding epitope** | IgV domain, residues 54-68 |
| **Known binders** | Atezolizumab, durvalumab, avelumab |

*Source: PDB via `PDB_search_by_uniprot`, `PDB_get_structure`*
```

---

## Phase 2: Backbone Generation

### 2.1 RFdiffusion Design

Call `NvidiaNIM_rfdiffusion` to generate de novo backbones. Generate at least 5 backbones; select 3-5 for sequence design based on topology diversity and geometric quality.

Key parameter: `diffusion_steps` (default 50; use 75-100 for higher quality at the cost of speed).

Design modes:
| Mode | Use Case |
|------|----------|
| Unconditional | De novo scaffold, no target constraint |
| Binder design | Provide `target_structure` and `hotspot_residues` |
| Motif scaffolding | Provide `motif_sequence` and `motif_structure` |

See [references/tools.md](references/tools.md) for full parameter details.

### 2.2 Report Output for Phase 2

```markdown
## 2. Backbone Generation

| Parameter | Value |
|-----------|-------|
| Method | RFdiffusion via NVIDIA NIM |
| Diffusion steps | 50 |
| Backbones generated | 10 |
| Selected for design | BB_001, BB_002, BB_003, BB_005 |

| Backbone | Length | Topology | Quality |
|----------|--------|----------|---------|
| BB_001 | 85 aa | 3-helix bundle | Good |
| BB_002 | 92 aa | Beta sandwich | Good |

*Source: NVIDIA NIM via `NvidiaNIM_rfdiffusion`*
```

---

## Phase 3: Sequence Design

### 3.1 ProteinMPNN Design

For each selected backbone, call `NvidiaNIM_proteinmpnn` with:
- `pdb_string`: the backbone PDB content (not a file path)
- `num_sequences`: 8 per backbone (minimum)
- `temperature`: 0.1 for conservative design; increase to 0.2-0.5 for more diversity

Rank all sequences by MPNN score (more negative = better). Report the top 10.

### 3.2 Report Output for Phase 3

```markdown
## 3. Sequence Design

| Rank | Backbone | Sequence ID | Length | MPNN Score |
|------|----------|-------------|--------|------------|
| 1 | BB_001 | Seq_001_A | 85 | -1.89 |
| 2 | BB_002 | Seq_002_C | 92 | -1.95 |

*Source: NVIDIA NIM via `NvidiaNIM_proteinmpnn`*
```

---

## Phase 4: Structure Validation

### 4.1 ESMFold Fast Validation

Call `NvidiaNIM_esmfold` with `sequence` for each designed sequence. Extract mean pLDDT and pTM from the response.

Pass criteria: mean pLDDT >70 AND pTM >0.7.

Sequences that fail are excluded from further analysis. At least 3 designs must pass; if fewer pass, return to Phase 2 and regenerate backbones with more diffusion steps.

### 4.2 AlphaFold2 High-Accuracy Validation

For the top 3-5 designs by pLDDT, run `NvidiaNIM_alphafold2` with `algorithm="mmseqs2"` for higher-confidence structure assessment. Note that AlphaFold2 may return HTTP 202 (accepted) and require polling.

### 4.3 Report Output for Phase 4

```markdown
## 4. Structure Validation

| Sequence | pLDDT | pTM | Status |
|----------|-------|-----|--------|
| Seq_001_A | 88.5 | 0.85 | PASS |
| Seq_002_C | 82.3 | 0.79 | PASS |
| Seq_005_B | 68.2 | 0.65 | FAIL |

*Source: NVIDIA NIM via `NvidiaNIM_esmfold`*
```

---

## Phase 5: Developability Assessment

Evaluate each passing design on the following criteria without requiring external tool calls (compute from sequence):

| Metric | Favorable | Marginal | Unfavorable |
|--------|-----------|----------|-------------|
| Aggregation score | <0.5 | 0.5-0.7 | >0.7 |
| Isoelectric point | 5-9 | 4-5 or 9-10 | <4 or >10 |
| Molecular weight | <50 kDa | 50-100 kDa | >100 kDa |
| Cysteine count | 0 or even (paired) | Odd | Multiple unpaired |

Assign each design a tier (see Evidence Grading below) and recommend an expression system.

### 5.1 Report Output for Phase 5

```markdown
## 5. Developability Assessment

| Design | Aggregation | pI | Cysteines | Expression | Tier |
|--------|-------------|-----|-----------|------------|------|
| Seq_001_A | 0.32 (Low) | 6.2 | 0 | High (E. coli) | T1 |
| Seq_002_C | 0.45 (Low) | 5.8 | 2 (paired) | Medium | T2 |

*Source: Sequence analysis*
```

---

## Report Template

```markdown
# Therapeutic Protein Design Report: [TARGET]

**Generated**: [Date] | **Query**: [Original query] | **Status**: In Progress

---

## Executive Summary
[Designing...]

---

## 1. Target Characterization
### 1.1 Target Information
[Designing...]
### 1.2 Binding Epitope
[Designing...]

---

## 2. Backbone Generation
### 2.1 Design Parameters
[Designing...]
### 2.2 Generated Backbones
[Designing...]

---

## 3. Sequence Design
### 3.1 ProteinMPNN Results
[Designing...]
### 3.2 Top Sequences
[Designing...]

---

## 4. Structure Validation
### 4.1 ESMFold Validation
[Designing...]
### 4.2 Quality Metrics
[Designing...]

---

## 5. Developability Assessment
### 5.1 Scores
[Designing...]
### 5.2 Recommendations
[Designing...]

---

## 6. Final Candidates
### 6.1 Ranked List
[Designing...]
### 6.2 Sequences for Testing
[Designing...]

---

## 7. Experimental Recommendations
[Designing...]

---

## 8. Data Sources
[Will be populated...]
```

---

## Evidence Grading

| Tier | Symbol | Criteria |
|------|--------|----------|
| **T1** | 3 stars | pLDDT >85, pTM >0.8, aggregation <0.5, neutral pI |
| **T2** | 2 stars | pLDDT >75, pTM >0.7, acceptable developability |
| **T3** | 1 star | pLDDT >70, pTM >0.65, developability concerns |
| **T4** | 0 stars | Failed validation or major developability issues |

---

## Known Gotchas

### Parameter Name Traps

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `NvidiaNIM_rfdiffusion` | `num_steps` | `diffusion_steps` |
| `NvidiaNIM_proteinmpnn` | `pdb` | `pdb_string` |
| `NvidiaNIM_esmfold` | `seq` | `sequence` |
| `NvidiaNIM_alphafold2` | `seq` | `sequence` |

### NVIDIA NIM Operational Issues

- **Rate limit**: 40 RPM maximum. Wait at least 1.5 seconds between consecutive NIM calls. If validating many sequences, pause 5 seconds between batches of 5.
- **AlphaFold2 async**: The tool may return HTTP 202 (accepted, not done). Poll until a 200 response is received before reading results.
- **ESMFold length cap**: Maximum 1024 amino acids. For longer sequences use `NvidiaNIM_alphafold2`.
- **RFdiffusion output**: Returns a backbone with only Gly residues. This PDB is the input to `NvidiaNIM_proteinmpnn`, not a final design.
- **pdb_string vs file path**: `NvidiaNIM_proteinmpnn` expects the full PDB file *content* as a string, not a filesystem path.

### Structural Data Gotchas

- **EMDB vs PDB**: EMDB entries describe density maps; the atomic model (needed for design) is a separate PDB entry referenced in `emdb_get_entry` response under `pdb_ids`. Always fetch that linked PDB.
- **AlphaFold predictions for design**: Label predicted structures clearly in the report. Design quality depends on target structure accuracy; a low-confidence AlphaFold model (pLDDT <70 in binding region) undermines binder design.
- **Resolution cutoff**: Cryo-EM structures >5 Å are unsuitable as direct design templates; prefer `NvidiaNIM_alphafold2` fallback.

### Validation Gotchas

- **Minimum passing designs**: If fewer than 3 designs pass (pLDDT >70, pTM >0.7), do not deliver the report. Increase `diffusion_steps` to 75-100, regenerate backbones, and repeat.
- **Self-consistency check**: After ESMFold validation, the predicted structure should resemble the RFdiffusion backbone (RMSD <2 Å for core regions). Large deviations indicate sequence-structure mismatch; discard that design.
- **MPNN score alone is insufficient**: A good MPNN score does not guarantee foldability. Always validate by structure prediction.

### Developability Gotchas

- **Odd cysteine count**: An odd number of cysteines almost always leads to misfolding due to an unpaired disulfide. Flag these designs explicitly.
- **Extreme pI**: Proteins with pI <4 or >10 are difficult to purify and prone to aggregation at physiological pH.
- **Membrane expression**: Designs with high hydrophobicity (GRAVY > 0.5) may require detergent or specialized expression systems; flag explicitly.

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `NvidiaNIM_rfdiffusion` | Increase diffusion steps and retry | Scaffold from PDB |
| `NvidiaNIM_proteinmpnn` | Lower temperature and retry | Manual sequence analysis |
| `NvidiaNIM_esmfold` | `NvidiaNIM_alphafold2` | AlphaFold DB lookup |
| `NvidiaNIM_alphafold2` | `alphafold_get_prediction` | AlphaFold DB homolog |
| PDB experimental structure | EMDB cryo-EM + PDB model | `NvidiaNIM_alphafold2` |
| EMDB cryo-EM | `PDB_search_by_uniprot` | `NvidiaNIM_alphafold2` |

---

## Tool Reference (Abbreviated)

| Tool | Call | Key Arguments |
|------|------|---------------|
| `NvidiaNIM_rfdiffusion` | Backbone generation | `diffusion_steps` (int, default 50) |
| `NvidiaNIM_proteinmpnn` | Sequence design | `pdb_string` (str), `num_sequences` (int), `temperature` (float) |
| `NvidiaNIM_esmfold` | Fast structure prediction | `sequence` (str, max 1024 aa) |
| `NvidiaNIM_alphafold2` | High-accuracy prediction | `sequence` (str), `algorithm` ("mmseqs2") |
| `NvidiaNIM_esm2_650m` | Sequence embeddings | `sequences` (list), `format` ("npz") |
| `PDB_search_by_uniprot` | Find PDB entries | `uniprot_id` (str) |
| `PDB_get_structure` | Download PDB file | `pdb_id` (str) |
| `alphafold_get_prediction` | AlphaFold DB lookup | `accession` (str) |
| `emdb_search` | Search cryo-EM maps | `query` (str) |
| `emdb_get_entry` | Get EMDB entry details | `entry_id` (str) |
| `UniProt_get_protein_sequence` | Get amino acid sequence | `accession` (str) |
| `InterPro_get_protein_domains` | Domain annotation | `accession` (str) |

Full parameter tables and quality thresholds: [references/tools.md](references/tools.md)

Pre-delivery verification: [CHECKLIST.md](CHECKLIST.md)
