# Therapeutic Protein Designer - Tool Reference

Detailed parameter tables and quality thresholds for all tools used in the protein design pipeline. Agents call tools via `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

---

## NVIDIA NIM Design Tools

### NvidiaNIM_rfdiffusion - Backbone Generation

**Purpose**: Generate de novo protein backbones via diffusion. Output contains only Gly residues; feed the PDB content directly into `NvidiaNIM_proteinmpnn`.

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `diffusion_steps` | int | 50 | Number of denoising steps. Higher = better quality, slower. |

**Step guide**:
| Steps | Quality | Use case |
|-------|---------|----------|
| 50 | Standard | Initial exploration |
| 75 | Good | Production designs |
| 100 | High | Final refinement |

**Design modes** (controlled by additional parameters when available):
| Mode | Description |
|------|-------------|
| Unconditional | Pure de novo scaffold; no target constraint |
| Binder design | Provide target structure and hotspot residues |
| Motif scaffolding | Embed a functional motif into a new scaffold |

**Common mistake**: Using `num_steps` instead of `diffusion_steps`.

---

### NvidiaNIM_proteinmpnn - Sequence Design

**Purpose**: Design amino acid sequences that fold onto a given backbone. Accepts backbone PDB content (not a file path).

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pdb_string` | str | Required | Full PDB file content as a string |
| `num_sequences` | int | 8 | Number of sequences to generate per call |
| `temperature` | float | 0.1 | Sampling temperature |

**Temperature guide**:
| Temperature | Diversity | Use case |
|-------------|-----------|----------|
| 0.05-0.1 | Low (conservative) | Validated scaffolds, high-confidence designs |
| 0.1-0.2 | Moderate | Balanced exploration |
| 0.2-0.5 | High | Diversity sampling |
| 0.5-1.0 | Maximum | Novelty / fallback when earlier temperatures fail |

**Output**: List of sequences and corresponding MPNN scores (more negative = better fit to backbone).

**Common mistake**: Using `pdb` instead of `pdb_string`.

---

### NvidiaNIM_esmfold - Fast Structure Validation

**Purpose**: Rapid single-sequence structure prediction. Use for initial screening of all designed sequences.

**Parameters**:
| Parameter | Type | Limit | Description |
|-----------|------|-------|-------------|
| `sequence` | str | Max 1024 aa | Amino acid sequence (single-letter) |

**Output fields**:
| Field | Description |
|-------|-------------|
| `structure` | PDB-format structure string |
| `plddt` | Per-residue confidence scores (list of floats) |
| `ptm` | Global topology confidence (float) |

**Pass thresholds**:
| Metric | Fail | Marginal | Good | Excellent |
|--------|------|----------|------|-----------|
| Mean pLDDT | <50 | 50-70 | 70-85 | >85 |
| pTM | <0.5 | 0.5-0.7 | 0.7-0.85 | >0.85 |

**Common mistake**: Using `seq` instead of `sequence`.

---

### NvidiaNIM_alphafold2 - High-Accuracy Validation

**Purpose**: Higher-accuracy structure prediction. Use for final validation of top candidates or sequences >1024 aa.

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sequence` | str | Required | Amino acid sequence |
| `algorithm` | str | "mmseqs2" | MSA algorithm; "mmseqs2" recommended |
| `relax_prediction` | bool | False | Apply Amber relaxation |

**Async behavior**: May return HTTP 202 (accepted). Poll the result endpoint until HTTP 200 is received. Do not assume the result is ready immediately.

**When to use instead of ESMFold**:
- Sequences >1024 amino acids
- Final validation of top 3-5 candidates
- When highest accuracy is required

**Common mistake**: Using `seq` instead of `sequence`.

---

### NvidiaNIM_esm2_650m - Sequence Embeddings

**Purpose**: Compute sequence embeddings for similarity analysis, clustering, and quality assessment.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `sequences` | list[str] | List of amino acid sequences |
| `format` | str | Output format; "npz" recommended |

**Use cases**:
- Cluster designed sequences to select diverse candidates
- Compare designs to natural protein families
- Assess novelty relative to existing therapeutics

---

## Supporting Tools - Target Structure Retrieval

### PDB_search_by_uniprot

| Parameter | Type | Description |
|-----------|------|-------------|
| `uniprot_id` | str | UniProt accession (e.g., "Q9NZQ7") |

Returns a list of PDB entries with metadata including resolution. Sort by resolution ascending to select the best experimental structure.

---

### PDB_get_structure

| Parameter | Type | Description |
|-----------|------|-------------|
| `pdb_id` | str | 4-character PDB ID (e.g., "4ZQK") |

Returns PDB-format structure content as a string.

---

### alphafold_get_prediction

| Parameter | Type | Description |
|-----------|------|-------------|
| `accession` | str | UniProt accession |

Retrieves the precomputed AlphaFold DB structure. Use as fallback when no experimental structure is available and NIM tools are unavailable.

---

### emdb_search

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | str | Free-text search (protein name, keyword) |

Returns a list of EMDB entries. Sort by resolution ascending. Prioritize for membrane proteins, GPCRs, ion channels, and large complexes.

**Resolution suitability**:
| Resolution | Design Suitability |
|------------|-------------------|
| <3 Å | Excellent - use directly |
| 3-4 Å | Good - validate binding site carefully |
| 4-5 Å | Use with caution |
| >5 Å | Avoid; use AlphaFold2 instead |

---

### emdb_get_entry

| Parameter | Type | Description |
|-----------|------|-------------|
| `entry_id` | str | EMDB accession (e.g., "EMD-12345") |

Returns entry details including `pdb_ids` (associated atomic models). Always retrieve the linked PDB model for design work; the density map alone is not usable as a design template.

---

## Supporting Tools - Sequence and Domain Analysis

### UniProt_get_protein_sequence

| Parameter | Type | Description |
|-----------|------|-------------|
| `accession` | str | UniProt accession |

Returns the canonical amino acid sequence. Use as input to `NvidiaNIM_alphafold2` when no experimental structure exists.

---

### InterPro_get_protein_domains

| Parameter | Type | Description |
|-----------|------|-------------|
| `accession` | str | UniProt accession |

Returns domain annotations. Useful for identifying functional regions and potential binding epitopes.

---

## Quality Thresholds Reference

### ProteinMPNN Score Interpretation

| Score Range | Interpretation |
|-------------|----------------|
| < -2.5 | Exceptional (rare) |
| -2.5 to -2.0 | Very good |
| -2.0 to -1.5 | Good |
| -1.5 to -1.0 | Acceptable |
| > -1.0 | Consider redesign |

### Design Tier Criteria

| Tier | pLDDT | pTM | MPNN Score | Aggregation |
|------|-------|-----|------------|-------------|
| T1 (3 stars) | >85 | >0.8 | < -1.8 | <0.5 |
| T2 (2 stars) | >75 | >0.7 | < -1.5 | <0.6 |
| T3 (1 star) | >70 | >0.65 | < -1.2 | <0.7 |
| T4 (0 stars) | <70 | <0.65 | > -1.2 | >0.7 |

### Developability Criteria

| Factor | Favorable | Marginal | Unfavorable |
|--------|-----------|----------|-------------|
| Aggregation score | <0.5 | 0.5-0.7 | >0.7 |
| Isoelectric point | 5-9 | 4-5 or 9-10 | <4 or >10 |
| Molecular weight | <50 kDa | 50-100 kDa | >100 kDa |
| Cysteine count | 0 or even (paired) | Odd | Multiple unpaired |
| GRAVY score | <0 | 0-0.3 | >0.5 |

### Expression System Guide

| Design Type | Recommended | Alternative |
|-------------|-------------|-------------|
| Simple scaffold, no disulfides | E. coli | Yeast |
| Disulfide-containing | Mammalian (CHO/HEK) | Insect |
| Glycosylated | Mammalian | - |
| Toxic to cells | Cell-free | Insect |
| Membrane-anchored | Insect | Mammalian |

---

## NVIDIA NIM Operational Notes

- **API key**: `NVIDIA_API_KEY` environment variable must be set.
- **Rate limit**: Maximum 40 RPM. Wait at least 1.5 seconds between consecutive calls. Pause 5 seconds between batches of 5.
- **AlphaFold2 polling**: Returns HTTP 202 on acceptance; poll until HTTP 200. Do not pass results from a 202 response to downstream steps.
- **ESMFold length**: Hard cap at 1024 amino acids. Longer sequences must use `NvidiaNIM_alphafold2`.
- **RFdiffusion output**: Backbone-only PDB (all Gly). Pass the `structure` field content directly as `pdb_string` to `NvidiaNIM_proteinmpnn`.

---

## Common Parameter Mistakes

| Tool | Wrong Parameter | Correct Parameter |
|------|-----------------|-------------------|
| `NvidiaNIM_rfdiffusion` | `num_steps=50` | `diffusion_steps=50` |
| `NvidiaNIM_proteinmpnn` | `pdb=content` | `pdb_string=content` |
| `NvidiaNIM_esmfold` | `seq="MVLS..."` | `sequence="MVLS..."` |
| `NvidiaNIM_alphafold2` | `seq="MVLS..."` | `sequence="MVLS..."` |

---

## Fallback Chains

### Backbone Generation
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `NvidiaNIM_rfdiffusion` (steps=50) | Increase to 75-100 steps | Scaffold from known PDB fold |

### Sequence Design
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `NvidiaNIM_proteinmpnn` (T=0.1) | Lower T to 0.05 or raise to 0.2 | Manual sequence analysis |

### Structure Validation
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `NvidiaNIM_esmfold` | `NvidiaNIM_alphafold2` | AlphaFold DB homolog |
| `NvidiaNIM_alphafold2` | `alphafold_get_prediction` | Report as unvalidated |

### Target Structure
| Primary | Fallback 1 | Fallback 2 | Fallback 3 |
|---------|------------|------------|------------|
| PDB experimental | EMDB cryo-EM + linked PDB | `NvidiaNIM_alphafold2` | AlphaFold DB |
| EMDB cryo-EM | `PDB_search_by_uniprot` | `NvidiaNIM_alphafold2` | - |
