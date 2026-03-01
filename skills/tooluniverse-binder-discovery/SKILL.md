---
name: tooluniverse-binder-discovery
description: Discover novel small molecule binders for protein targets using structure-based and ligand-based approaches. Creates actionable reports with candidate compounds, ADMET profiles, and synthesis feasibility. Use when users ask to find small molecules for a target, identify novel binders, perform virtual screening, or need hit-to-lead compound identification.
---

# Small Molecule Binder Discovery Strategy

Systematic discovery of novel small molecule binders using 60+ ToolUniverse tools across druggability assessment, known ligand mining, similarity expansion, ADMET filtering, and synthesis feasibility.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Target validation FIRST** - Confirm druggability before compound searching
3. **Multi-strategy approach** - Combine structure-based and ligand-based methods
4. **ADMET-aware filtering** - Eliminate poor compounds early
5. **Evidence grading** - Grade candidates by supporting evidence
6. **Actionable output** - Provide prioritized candidates with rationale
7. **English-first queries** - Always use English terms in tool calls, even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## Critical Workflow Requirements

### 1. Report-First Approach (MANDATORY)

Do not show search process or raw tool outputs to the user. Instead:

1. **Create the report file FIRST** before any data collection:
   - File name: `[TARGET]_binder_discovery_report.md`
   - Initialize with all section headers from the Report Template below
   - Add placeholder text `[Researching...]` in each section

2. **Progressively update the report** as you gather data — the user sees the report growing, not the search process.

3. **Output separate data files**:
   - `[TARGET]_candidate_compounds.csv` — prioritized compounds with SMILES, scores
   - `[TARGET]_bibliography.json` — literature references (optional)

### 2. Citation Requirements (MANDATORY)

Every piece of information must include its source. Example:

```
### 3.2 Known Inhibitors
| Compound | ChEMBL ID | IC50 (nM) | Source |
|----------|-----------|-----------|--------|
| Imatinib | CHEMBL941 | 38 | ChEMBL |

*Source: ChEMBL via `ChEMBL_get_target_activities` (CHEMBL1862)*
```

---

## Workflow Overview

```
Phase 0: Tool Verification
    ↓
Phase 1: Target Validation
    ├─ 1.1 Resolve identifiers (UniProt, Ensembl, ChEMBL target ID)
    ├─ 1.2 Assess druggability/tractability
    │   └─ 1.2a GPCRdb enrichment (if GPCR target)
    │   └─ 1.2.5 Check therapeutic antibodies (Thera-SAbDab)
    ├─ 1.3 Identify binding sites
    └─ 1.4 Predict structure if no experimental (NvidiaNIM_alphafold2 / esmfold)
    ↓
Phase 2: Known Ligand Mining
    ├─ 2.1 ChEMBL bioactivity data
    ├─ 2.2 GtoPdb interactions
    ├─ 2.3 Chemical probes (Open Targets)
    ├─ 2.4 SAR analysis from known actives
    ├─ 2.5 BindingDB affinity data
    └─ 2.6 PubChem BioAssay HTS data
    ↓
Phase 3: Structure Analysis
    ├─ 3.1 PDB structures with ligands
    ├─ 3.1b EMDB cryo-EM (for membrane targets)
    └─ 3.2 Binding pocket characterization
    ↓
Phase 3.5: Docking Validation (NvidiaNIM_diffdock / boltz2)
    └─ Dock reference inhibitor to validate binding pocket geometry
    ↓
Phase 4: Compound Expansion
    ├─ 4.1–4.3 Similarity / substructure / cross-database search
    └─ 4.4 De novo generation (NvidiaNIM_genmol / molmim)
    ↓
Phase 5: ADMET Filtering
    ├─ Physicochemical properties
    ├─ ADMET endpoints (bioavailability, toxicity, CYP)
    └─ Structural alerts (PAINS)
    ↓
Phase 6: Candidate Docking & Prioritization
    ├─ Dock all ADMET-passing candidates
    ├─ Score by docking + ADMET + novelty
    ├─ Synthesis feasibility
    └─ Final ranked list
    ↓
Phase 6.5: Literature Evidence
    └─ PubMed / BioRxiv / MedRxiv / OpenAlex
    ↓
Phase 7: Report Synthesis
```

---

## Phase 0: Tool Verification

**Before calling an unfamiliar tool**, call `get_tool_info` with the tool name to confirm parameter names.
This prevents silent failures caused by wrong argument names.

See [references/tools.md](references/tools.md) for a full list of known parameter corrections and
detailed per-tool argument schemas.

**Quick reference — most common corrections**:

| Tool | Wrong | Correct |
|------|-------|---------|
| `OpenTargets_get_target_tractability_by_ensemblID` | `ensembl_id` | `ensemblId` |
| `ChEMBL_get_target_activities` | `chembl_target_id` | `target_chembl_id` |
| `ChEMBL_search_similar_molecules` | `smiles` | `molecule` |
| `alphafold_get_prediction` | `uniprot` | `accession` |

---

## Phase 1: Target Validation

### 1.1 Identifier Resolution Chain

Run these queries in order; store all IDs for downstream use:

1. Call `UniProt_search` with the target name and `organism="human"` → get UniProt accession, gene name
2. Call `MyGene_query_genes` with the gene symbol → get Ensembl gene ID, NCBI gene ID
3. Call `ChEMBL_search_targets` with the target name → get ChEMBL target ID, target type
4. Call `GtoPdb_get_targets` with the target name → get GtoPdb target ID (if GPCR/ion channel/enzyme)

Store: `uniprot`, `ensembl`, `chembl_target`, `gene_symbol`, `gtopdb` (if available).

### 1.2 Druggability Assessment

Triangulate from at least two sources:

1. Call `OpenTargets_get_target_tractability_by_ensemblID(ensemblId)` → small molecule tractability score and bucket
2. Call `DGIdb_get_gene_druggability(genes=[gene_symbol])` → druggability categories, known drug count
3. Call `OpenTargets_get_target_classes_by_ensemblID(ensemblId)` → target class (kinase, GPCR, etc.)

**Decision point**: if tractability bucket > 3 and no known drugs, warn user about challenges.

Scorecard: known drugs (★★★), tractability bucket 1–3 (★★–★★★), enzyme/GPCR/ion channel class (★★★), X-ray binding site (★★★), GPCRdb ligands ≥10 (★★★, GPCR only).

### 1.2a GPCRdb Enrichment (GPCR Targets Only)

~35% of approved drugs target GPCRs. Build entry name as `"{gene_lower}_human"` (e.g., `"adrb2_human"`).
Call `GPCRdb_get_protein` (confirm GPCR), `GPCRdb_get_structures` (active/inactive states), `GPCRdb_get_ligands` (curated data), `GPCRdb_get_mutations` (binding effects — important for SAR).
GPCRdb provides Ballesteros-Weinstein generic residue numbering — critical for comparing binding pockets across subtypes.

### 1.2.5 Therapeutic Antibody Landscape

Approved antibodies validate target tractability; understanding the antibody landscape identifies gaps (no oral, no CNS-penetrant small molecule).
Call `TheraSAbDab_search_by_target(target=target_name)` and `TheraSAbDab_search_therapeutics(query=synonym)` for major synonyms.
Report by phase: Approved / Phase 3 / Phase 2 / Phase 1 / Preclinical.

### 1.3 Binding Site Analysis

1. Call `ChEMBL_search_binding_sites(target_chembl_id)` → binding site names and types
2. Call `get_binding_affinity_by_pdb_id(pdb_id)` for each PDB with a ligand → Kd/Ki/IC50 for co-crystallized ligands
3. Call `InterPro_get_protein_domains(uniprot_accession)` → domain architecture, active site annotations

### 1.4 Structure Prediction (NVIDIA NIM)

Use only when no experimental structure is available, or for custom domain predictions.
Requires `NVIDIA_API_KEY`.

- **AlphaFold2** (`NvidiaNIM_alphafold2`): high accuracy, async, 5–15 min. Use when accuracy is critical.
- **ESMFold** (`NvidiaNIM_esmfold`): fast (~30 s), max 1024 AA. Use for quick assessment.

Report mean pLDDT and confidence per region. Confidence thresholds:
- ≥90: very high (reliable)
- 70–90: confident (reliable)
- 50–70: low (use with caution)
- <50: very low (unreliable — do not base docking on these regions)

---

## Phase 2: Known Ligand Mining

### 2.1 ChEMBL Bioactivity

Call `ChEMBL_get_target_activities(target_chembl_id, limit=500)`.
Filter to standard_type in [IC50, Ki, Kd, EC50] and standard_value < 10,000 nM.
Call `ChEMBL_get_molecule(molecule_chembl_id)` for top actives to get full molecular data and max_phase.

### 2.2 GtoPdb Interactions

Call `GtoPdb_get_target_interactions(target_id)` → ligands with pKi/pIC50 and selectivity data.

### 2.3 Chemical Probes

Call `OpenTargets_get_chemical_probes_by_target_ensemblID(ensemblId)` → validated probes with ratings.
Identify the recommended probe for target validation (highest rating, validated in vivo preferred).

### 2.4 SAR Analysis

From ChEMBL actives, summarize: core scaffolds with compound counts and potency ranges; key structural features driving potency (e.g., halogen at meta position, H-bond acceptor at hinge).

### 2.5 BindingDB Affinity Data

Call `BindingDB_get_ligands_by_uniprot(uniprot, affinity_cutoff=10000)` (cutoff in nM). BindingDB may have compounds not in ChEMBL, with direct PMIDs. Sort by potency; take top 50.
For polypharmacology, call `BindingDB_get_targets_by_compound(smiles, similarity_cutoff=0.85)`.

### 2.6 PubChem BioAssay HTS Data

Call `PubChem_search_assays_by_target_gene(gene_symbol)` → assay IDs (AIDs). Then call `PubChem_get_assay_active_compounds(aid)` for each. Covers NIH MLPCN HTS data not in ChEMBL.
Source comparison: ChEMBL (curated, SAR-ready), BindingDB (Ki/Kd/IC50 + PMIDs), PubChem (HTS breadth).

---

## Phase 3: Structure Analysis

### 3.1 PDB Structure Retrieval

1. Call `PDB_search_similar_structures(query=uniprot_accession, type="sequence")` → PDB IDs with ligands
2. Call `get_protein_metadata_by_pdb_id(pdb_id)` → resolution, method, ligand codes
3. If no experimental structure, call `alphafold_get_prediction(accession=uniprot_accession)` from AlphaFold DB

### 3.1b EMDB Cryo-EM Structures (Membrane Targets)

For GPCRs, ion channels, and large complexes, prefer cryo-EM (native conformation, multiple functional states). Call `emdb_search` then `emdb_get_entry(entry_id)` to get resolution, state, and associated PDB model IDs. The PDB model ID is required for docking — EMDB entries are not directly dockable. For kinases, X-ray typically gives better resolution.

### 3.2 Binding Pocket Characterization

Call `get_binding_affinity_by_pdb_id(pdb_id)` for each structure with a co-crystallized ligand.
Note key interaction residues (hinge region, gatekeeper, DFG motif, selectivity pocket).
Identify the best structure for docking (highest resolution, most relevant ligand).

---

## Phase 3.5: Docking Validation (NVIDIA NIM)

Validate that the structure captures the binding pocket correctly by docking a known reference inhibitor.
Requires `NVIDIA_API_KEY`.

**DiffDock** (`NvidiaNIM_diffdock`): blind docking given PDB text + SDF/MOL2 text. Use when you have a PDB and ligand SDF.

**Boltz2** (`NvidiaNIM_boltz2`): protein-ligand structure prediction from sequence + SMILES. Use when starting from SMILES only (no SDF file needed).

Validation passes if: the docked pose is consistent with known binding residues and there are no steric clashes.
See [references/tools.md](references/tools.md) for docking score interpretation thresholds and NIM tool parameter schemas.

---

## Phase 4: Compound Expansion

### 4.1 Similarity Search

Use 3–5 diverse actives (IC50 < 100 nM) as seeds. Similarity threshold 70–85% balances novelty vs. predicted activity.

- Call `ChEMBL_search_similar_molecules(molecule=seed_smiles, similarity=70)`
- Call `PubChem_search_compounds_by_similarity(smiles, threshold=0.7)`

Prioritize compounds not yet tested on this target.

### 4.2 Substructure Search

- Call `ChEMBL_search_substructure(smiles=core_scaffold)`
- Call `PubChem_search_compounds_by_substructure(smiles=core_scaffold)`

### 4.3 Cross-Database Mining

- Call `STITCH_get_chemical_protein_interactions(identifier=target_gene)` → additional chemical-protein links
- Call `DGIdb_get_drug_gene_interactions(genes=[gene_symbol])` → approved/investigational drugs

Deduplicate across all sources and report: total unique candidates, novel vs. already-tested breakdown.

### 4.4 De Novo Generation (NVIDIA NIM)

Use when database mining yields insufficient diversity. Requires `NVIDIA_API_KEY`.

**GenMol** (`NvidiaNIM_genmol`): scaffold hopping with masked regions. Provide a SMILES with `[*{min-max}]` at positions to vary (e.g., `[*{1-3}]` = generate 1–3 atoms). Use `temperature=2.0` for diversity. Good for: exploring specific substitution positions while keeping the scaffold.

**MolMIM** (`NvidiaNIM_molmim`): controlled generation from a reference SMILES using CMA-ES optimization. Good for: generating close analogs of a top active.

Generation workflow: identify top 3–5 actives → design masked SMILES or use reference → generate 50–100 molecules per seed → feed survivors to Phase 5.

---

## Phase 5: ADMET Filtering

Apply in sequence; document the filter funnel (input count → passed count at each stage).

**Physicochemical** — call `ADMETAI_predict_physicochemical_properties(smiles=[...])`:
- Keep: Lipinski violations ≤ 1, QED > 0.3, MW 200–600

**Bioavailability** — call `ADMETAI_predict_bioavailability(smiles=[...])`:
- Keep: oral bioavailability > 0.3

**Toxicity** — call `ADMETAI_predict_toxicity(smiles=[...])`:
- Eliminate: AMES ≥ 0.5, hERG ≥ 0.5, DILI ≥ 0.5

**CYP liabilities** — call `ADMETAI_predict_CYP_interactions(smiles=[...])`:
- Flag (do not eliminate): CYP3A4 inhibitors (drug interaction risk)

**Structural alerts** — call `ChEMBL_search_compound_structural_alerts(smiles=...)`:
- Eliminate: PAINS, reactive groups, toxicophores

---

## Phase 6: Candidate Prioritization

### 6.1 Scoring Framework

Score each candidate across five dimensions (weights are guidelines, adjust to context):

| Dimension | Weight | Scoring Notes |
|-----------|--------|---------------|
| Structural similarity to actives | 25% | Tanimoto to known actives (0.7–1.0) |
| Novelty | 20% | Not in ChEMBL bioactivity for target = +2; novel scaffold = +3 |
| ADMET score | 25% | Composite of Phase 5 predictions |
| Synthesis feasibility | 15% | SA score 1–3 easy, 3–5 moderate, 5–10 challenging |
| Scaffold diversity | 15% | Cluster representative bonus |

### 6.2 Docking-Enhanced Scoring

Dock all ADMET-passing candidates using `NvidiaNIM_diffdock` or `NvidiaNIM_boltz2`.
Update evidence tiers based on docking result vs. reference compound score:
- Score better than reference → upgrade to T0 (★★★★)
- Within 5% → T2 (★★☆)
- Within 20% → maintain tier
- More than 20% worse → downgrade one tier

### 6.3 Synthesis Feasibility

For top 20 candidates, report SA score and commercial availability (Enamine, Sigma, etc.).

### 6.4 Final Ranked List

Produce a ranked table of ≥ 20 candidates (or all if fewer) with SMILES, scores, and rationale.
Note scaffold diversity in the top 20 and the fraction commercially available.

---

## Phase 6.5: Literature Evidence

After candidates are ranked, call `PubMed_search_articles` (SAR studies), `BioRxiv_search_preprints` (latest findings), `MedRxiv_search_preprints` (clinical data), and `openalex_search_works` (citation counts for key papers). Mark all preprint findings as not peer-reviewed.

---

## Evidence Grading

Apply to all candidate compounds in the final report:

| Tier | Symbol | Criteria |
|------|--------|----------|
| T0 | ★★★★ | Docking score beats reference inhibitor |
| T1 | ★★★ | Experimental IC50/Ki < 100 nM (ChEMBL/BindingDB) |
| T2 | ★★☆ | Docking within 5% of reference OR IC50 100–1000 nM |
| T3 | ★☆☆ | Structural similarity > 80% to a T1 compound |
| T4 | ☆☆☆ | Similarity 70–80% to active, scaffold match |
| T5 | ○○○ | Generated molecule, ADMET-passed, no docking |

---

## Known Gotchas

**Parameter names**: ChEMBL and OpenTargets tools use inconsistent naming conventions (camelCase vs underscore). Always verify with `get_tool_info` before calling. See [references/tools.md](references/tools.md) for the full correction table.

**NVIDIA API key**: All `NvidiaNIM_*` tools fail silently or with unclear errors if `NVIDIA_API_KEY` is absent. Confirm availability at the start of the workflow; plan fallbacks for every NIM step.

**ChEMBL similarity search**: The `molecule` parameter in `ChEMBL_search_similar_molecules` accepts SMILES, ChEMBL ID, or a name — not just SMILES. Do not pass it as `smiles=`.

**AlphaFold DB wrapper**: `alphafold_get_prediction` uses `accession=`, not `uniprot=`.

**GPCRdb entry names**: Must be `"{gene_lower}_human"` format (e.g., `"adrb2_human"`). The tool will return an error for other formats; do not guess — build the name programmatically.

**EMDB → PDB link**: EMDB entries include associated PDB model IDs. You must extract these to use the structure for docking — the EMDB entry itself is not directly dockable.

**BindingDB affinity units**: `affinity_cutoff` is in nM. `affinity` field in results is also in nM. Do not confuse with pKi/pIC50 returned by GtoPdb (those are -log10 scale).

**PubChem BioAssay**: `PubChem_search_assays_by_target_gene` returns assay IDs (AIDs), not compounds. You must call `PubChem_get_assay_active_compounds(aid)` separately for each assay to get compound CIDs.

**GenMol masked SMILES**: The `[*{min-max}]` syntax is specific to NvidiaNIM_genmol — it is not standard SMILES. Regular SMILES parsers will reject it. Only pass masked SMILES to this tool.

---

## Report Template

**File**: `[TARGET]_binder_discovery_report.md`

Initialize immediately with all headers and `[Researching...]` placeholders. Required top-level sections:

```
# Small Molecule Binder Discovery: [TARGET]
**Generated**: [Date] | **Query**: [query] | **Status**: In Progress

## Executive Summary          ← [Researching...]
## 1. Target Validation       ← 1.1 Identifiers / 1.2 Druggability / 1.3 Binding Sites
## 2. Known Ligand Landscape  ← 2.1 ChEMBL / 2.2 Approved Drugs / 2.3 Probes / 2.4 SAR
## 3. Structural Information  ← 3.1 Structures / 3.2 Pocket / 3.3 Key Interactions
## 4. Compound Expansion      ← 4.1 Similarity / 4.2 Substructure / 4.3 Cross-DB
## 5. ADMET Filtering         ← 5.1 Physicochemical / 5.2 ADMET / 5.3 Alerts / 5.4 Funnel
## 6. Candidate Prioritization ← 6.1 Scoring / 6.2 Synthesis / 6.3 Top 20
## 7. Recommendations         ← 7.1 Immediate Actions / 7.2 Validation Plan / 7.3 Backups
## 8. Data Gaps & Limitations
## 9. Data Sources            ← populated progressively
```

---

## Common Use Cases

| Scenario | Key Focus |
|----------|-----------|
| Well-characterized target (e.g., EGFR) | Novel scaffolds, selectivity, ADMET optimization |
| Novel target (no known ligands) | Structure-based assessment, similar-target ligands, de novo generation |
| Lead optimization (analog of compound X) | Deep similarity search around specific compound; SAR focus |
| Selectivity challenge (kinase X vs. kinase Y) | Include off-target docking/BindingDB polypharmacology analysis |

---

## When NOT to Use This Skill

- **Drug research** → use `tooluniverse-drug-research` (existing drug profiling)
- **Target research only** → use `tooluniverse-target-research`
- **Single compound ADMET** → call ADMET tools directly
- **Literature search** → use `tooluniverse-literature-deep-research`
- **Protein structure only** → use `tooluniverse-protein-structure-retrieval`

Use this skill for **discovering new compounds** for a protein target.

---

## Tool Reference (Abbreviated)

For full parameter schemas and fallback chains, see [references/tools.md](references/tools.md).

**Phase 0 (Verification)**: `get_tool_info` — check parameter names before calling unfamiliar tools

| Tool | Phase | Purpose |
|------|-------|---------|
| `UniProt_search` | 1 | Resolve UniProt accession |
| `MyGene_query_genes` | 1 | Get Ensembl / NCBI IDs |
| `ChEMBL_search_targets` | 1 | Get ChEMBL target ID |
| `OpenTargets_get_target_tractability_by_ensemblID` | 1 | Tractability bucket and score |
| `OpenTargets_get_target_classes_by_ensemblID` | 1 | Target class (kinase, GPCR, etc.) |
| `DGIdb_get_gene_druggability` | 1 | Druggability categories |
| `GPCRdb_get_protein / _structures / _ligands / _mutations` | 1 | GPCR-specific data (if GPCR) |
| `TheraSAbDab_search_by_target` | 1 | Therapeutic antibody landscape |
| `ChEMBL_search_binding_sites` | 1 | Binding site names and types |
| `InterPro_get_protein_domains` | 1 | Domain architecture and active sites |
| `get_binding_affinity_by_pdb_id` | 1/3 | Kd/Ki/IC50 for co-crystallized ligands |
| `NvidiaNIM_alphafold2` | 1 | High-accuracy structure prediction (async, NVIDIA key) |
| `NvidiaNIM_esmfold` | 1 | Fast structure prediction, max 1024 AA (NVIDIA key) |
| `alphafold_get_prediction` | 1/3 | Fetch structure from AlphaFold DB (use `accession=`) |
| `ChEMBL_get_target_activities` | 2 | Bioactivity data (use `target_chembl_id=`) |
| `ChEMBL_get_molecule` | 2 | Full molecule data including max_phase |
| `GtoPdb_get_target_interactions` | 2 | Pharmacology ligands with pKi/pIC50 |
| `OpenTargets_get_chemical_probes_by_target_ensemblID` | 2 | Validated chemical probes |
| `BindingDB_get_ligands_by_uniprot` | 2 | Affinity data with direct PMIDs |
| `BindingDB_get_targets_by_compound` | 2 | Polypharmacology / off-target check |
| `PubChem_search_assays_by_target_gene` | 2 | HTS assay IDs (returns AIDs, not compounds) |
| `PubChem_get_assay_active_compounds` | 2 | Compound CIDs per assay |
| `PDB_search_similar_structures` | 3 | Find PDB entries by sequence |
| `get_protein_metadata_by_pdb_id` | 3 | Resolution, method, ligand codes |
| `get_ligand_smiles_by_chem_comp_id` | 3 | Ligand SMILES from PDB component code |
| `emdb_search` / `emdb_get_entry` | 3 | Cryo-EM structures; extract PDB model ID for docking |
| `NvidiaNIM_diffdock` | 3.5/6 | Blind docking: PDB text + SDF text (NVIDIA key) |
| `NvidiaNIM_boltz2` | 3.5/6 | Protein-ligand complex from sequence + SMILES (NVIDIA key) |
| `ChEMBL_search_similar_molecules` | 4 | Similarity search (use `molecule=`, not `smiles=`) |
| `PubChem_search_compounds_by_similarity` | 4 | PubChem Tanimoto similarity |
| `ChEMBL_search_substructure` | 4 | Scaffold-containing compounds |
| `PubChem_search_compounds_by_substructure` | 4 | PubChem substructure search |
| `STITCH_get_chemical_protein_interactions` | 4 | Cross-database chemical-protein links |
| `DGIdb_get_drug_gene_interactions` | 4 | Approved/investigational drugs |
| `NvidiaNIM_genmol` | 4 | Scaffold hopping via masked SMILES (NVIDIA key) |
| `NvidiaNIM_molmim` | 4 | Analog generation from reference SMILES (NVIDIA key) |
| `ADMETAI_predict_physicochemical_properties` | 5 | Lipinski, QED, MW |
| `ADMETAI_predict_bioavailability` | 5 | Oral absorption |
| `ADMETAI_predict_toxicity` | 5 | AMES, hERG, DILI |
| `ADMETAI_predict_CYP_interactions` | 5 | CYP3A4 liability flags |
| `ChEMBL_search_compound_structural_alerts` | 5 | PAINS and reactive groups |
| `PubMed_search_articles` | 6.5 | Published SAR studies |
| `BioRxiv_search_preprints` / `MedRxiv_search_preprints` | 6.5 | Preprints (flag as not peer-reviewed) |
| `openalex_search_works` | 6.5 | Citation counts for key papers |
| `SemanticScholar_search` | 6.5 | AI-ranked paper search |

---

## Additional Resources

- **Checklist**: [CHECKLIST.md](CHECKLIST.md) — pre-delivery verification
- **Examples**: [EXAMPLES.md](EXAMPLES.md) — detailed workflow examples
- **Tool parameter details**: [references/tools.md](references/tools.md) — full parameter schemas, fallback chains, NIM tool arguments
