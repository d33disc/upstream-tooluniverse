# Antibody Engineering — Detailed Tool Parameters & Sample Output

This file is a reference supplement to `SKILL.md`. It contains verbose parameter tables,
sample report output blocks, and scoring rubrics that would bloat the main workflow guide.

---

## IMGT Tools

### `IMGT_search_genes`
Search germline genes in the IMGT database.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `gene_type` | string | Yes | `"IGHV"`, `"IGKV"`, `"IGLV"`, `"IGHJ"`, `"IGKJ"` |
| `species` | string | Yes | `"Homo sapiens"`, `"Mus musculus"` |

### `IMGT_get_sequence`
Retrieve a germline sequence by accession.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `accession` | string | Yes | IMGT accession from `IMGT_search_genes` |
| `format` | string | No | `"fasta"` (default) or `"raw"` |

---

## SAbDab / TheraSAbDab Tools

### `SAbDab_search_structures`
Search PDB structures of antibodies.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `query` | string | Yes | Protein name, antigen, or PDB ID |
| `limit` | int | No | Default 20 |

### `TheraSAbDab_search_by_target`
Find clinical/approved antibodies against a target.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `target` | string | Yes | Antigen name (e.g., `"PD-L1"`, `"HER2"`) |

Response fields: `name`, `target`, `phase` (`"Approved"`, `"Phase 1"`, etc.), `format`, `isotype`.

---

## IEDB Tools

### `iedb_search_epitopes`
Search IEDB for known T-cell/B-cell epitopes.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `sequence_contains` | string | Yes | Peptide sequence (partial match allowed) |
| `structure_type` | string | No | `"Linear peptide"` or `"Discontinuous"` |
| `limit` | int | No | Default 20 |

### `iedb_search_bcell`
Search B-cell epitope data.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `sequence_contains` | string | Yes | Peptide or protein sequence fragment |
| `limit` | int | No | Default 20 |

### `iedb_search_mhc`
Search MHC-binding epitopes.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `sequence_contains` | string | Yes | 9-mer peptide for sliding window scan |
| `mhc_allele` | string | No | e.g., `"HLA-DR1"` |

---

## Structure & Target Tools

### `AlphaFold_get_prediction`
Retrieve or compute a structure prediction.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `sequence` | string | Yes | Use `":"` as chain separator for VH:VL |
| `return_format` | string | No | `"pdb"` (default) or `"mmcif"` |

Response includes `plddt` scores per residue. Mean pLDDT >85 = high confidence; CDR-H3 often 75-85 due to loop flexibility.

### `UniProt_get_protein_by_accession`
Get target antigen information.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `accession` | string | Yes | UniProt accession (e.g., `"Q9NZQ7"` for PD-L1) |

---

## Systems Biology Tools (Bispecifics)

### `STRING_get_interactions`
Get protein-protein interactions for co-target identification.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `protein` | string | Yes | Gene name or UniProt ID |
| `species` | int | No | NCBI Taxonomy ID; `9606` = human |
| `limit` | int | No | Default 10 |

### `STRING_get_enrichment`
Pathway enrichment for a set of proteins.

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `proteins` | list | Yes | List of gene names or UniProt IDs |
| `species` | int | No | Default `9606` |

---

## Developability Scoring Rubric

**Overall score: 0–100 (higher is better), Tiers: T1 (>75), T2 (60–75), T3 (<60)**

| Component | Weight | What 100 means |
|-----------|--------|----------------|
| Aggregation | 30% | No APRs, TANGO score <20 |
| PTM liability | 25% | No NG/DG deamidation/isomerization in CDRs |
| Thermal stability | 20% | Predicted Tm >70°C |
| Expression | 15% | Predicted titer >1 g/L CHO fed-batch |
| Solubility | 10% | >100 mg/mL formulation achievable |

**PTM motif cheat sheet**:
- Deamidation: Asn-Gly (NG) = High risk; Asn-Ser (NS) = Medium risk
- Isomerization: Asp-Gly (DG) or Asp-Ser (DS) = High risk
- Oxidation: Met (M), Trp (W) = Medium risk (surface-exposed worst)
- N-glycosylation: N-X-S/T where X ≠ Pro

---

## Immunogenicity Risk Scoring

**Total risk 0–100 (lower is better)**:
- Low: <30 (clinical candidate ready)
- Medium: 30–60 (acceptable with monitoring)
- High: >60 (requires deimmunization)

Components: T-cell epitope count × 10 + non-human framework residues × 5 + aggregation risk × 20.

---

## Humanization Evidence Tiers

| Tier | Symbol | Criteria |
|------|--------|----------|
| T1 | ★★★ | Humanness >85%, KD <2 nM, Developability >75, Low immunogenicity |
| T2 | ★★☆ | Humanness 70–85%, KD 2–10 nM, Developability 60–75, Medium immunogenicity |
| T3 | ★☆☆ | Humanness <70%, KD >10 nM, Developability <60, or High immunogenicity |
| T4 | ☆☆☆ | Failed validation or major liabilities |

---

## Sample Report Output Format

See `EXAMPLES.md` for complete worked examples (PD-L1 humanization case study).

Each phase section in the report should follow this template:

```markdown
### Optimized Variant: VH_Humanized_v1

**Original Sequence**: EVQLVESGGGLVQPGG... (mouse)
**Humanized Sequence**: EVQLVQSGAEVKKPGA... (human framework)
**Humanization Score**: 87% human framework
**CDR Preservation**: 100% (all CDR residues retained)

**Metrics**:
| Metric | Original | Optimized | Change |
|--------|----------|-----------|--------|
| Humanness | 62% | 87% | +25% |
| Aggregation risk | 0.58 | 0.32 | -45% |
| Predicted KD | 5.2 nM | 3.8 nM | +27% affinity |
| Immunogenicity | High | Low | -65% |

*Source: IMGT germline analysis, IEDB predictions*
```

---

## IMGT CDR Numbering Reference

| Region | Heavy Chain (VH) | Light Chain (VL) |
|--------|-----------------|-----------------|
| FR1 | 1–26 | 1–26 |
| CDR1 | 27–38 | 27–38 |
| FR2 | 39–55 | 39–55 |
| CDR2 | 56–65 | 56–65 |
| FR3 | 66–104 | 66–104 |
| CDR3 | 105–117 | 105–117 |
| FR4 | 118–128 | 118–127 |

**Vernier zone residues** (affect CDR conformation; candidates for backmutation):
Positions 2, 27, 28, 29, 30, 47, 48, 67, 69, 71, 78, 93, 94 (IMGT numbering)
High-priority positions: 27, 29, 30, 48

---

## Manufacturing Reference Data

**3-step purification strategy (standard IgG)**:
1. Protein A affinity capture — yield >95%, purity >90%
2. Cation exchange polishing (SP, pH 5.0–5.5) — aggregate/variant removal, purity >98%
3. Nanofiltration (20 nm) — viral clearance, purity >99%

**Formulation baseline**:
- Buffer: 20 mM Histidine-HCl, pH 6.0
- Stabilizer: 0.02% Polysorbate 80 + 240 mM Sucrose
- Target: ≤15 cP viscosity for subcutaneous delivery

**Analytical release assays (ICH)**:
SEC-MALS (monomer >95%), CEX (main peak >70%), CE-SDS (purity >95%), SPR/ELISA (KD <5 nM), DSF (Tm >65°C), cell-based bioactivity (EC50 <10 nM)
