# Tool Parameter Reference

Detailed parameter notes for tools used in binder discovery.
Agents: check these when a tool call returns an unexpected error — parameter names are the most common cause.

---

## Known Parameter Corrections

| Tool | WRONG Parameter | CORRECT Parameter | Notes |
|------|-----------------|-------------------|-------|
| `OpenTargets_get_target_tractability_by_ensemblID` | `ensembl_id` | `ensemblId` | camelCase |
| `ChEMBL_get_target_activities` | `chembl_target_id` | `target_chembl_id` | underscored form |
| `ChEMBL_search_similar_molecules` | `smiles` | `molecule` | accepts SMILES, ChEMBL ID, or name |
| `alphafold_get_prediction` | `uniprot` | `accession` | AlphaFold DB wrapper |

---

## Phase 0: Tool Verification Pattern

Before calling an unfamiliar tool, call `get_tool_info(tool_name="...")` to check parameter names.
This is especially important for OpenTargets and ChEMBL tools, which frequently use non-obvious param names.

---

## NvidiaNIM Tool Details

All `NvidiaNIM_*` tools require the `NVIDIA_API_KEY` environment variable. Check availability before planning
any NIM-dependent step — if unavailable, fall back to non-NIM alternatives.

### NvidiaNIM_alphafold2
- `sequence`: protein sequence string
- `algorithm`: `"mmseqs2"` (recommended) or `"jackhmmer"`
- `relax_prediction`: boolean (default False; set True for final structures)
- Returns: PDB text + per-residue pLDDT scores
- Runtime: 5–15 minutes (async)
- Use when: accuracy is critical

### NvidiaNIM_esmfold
- `sequence`: protein sequence string (max 1024 AA)
- Returns: PDB text
- Runtime: ~30 seconds (synchronous)
- Use when: quick structural assessment is enough

### NvidiaNIM_diffdock
- `protein`: PDB text content (not file path)
- `ligand`: SDF or MOL2 text content
- `num_poses`: integer (default 10)
- Returns: docking poses with confidence scores
- Use when: you have a PDB structure and want to dock a specific ligand

### NvidiaNIM_boltz2
- `polymers`: list of `{"molecule_type": "protein", "sequence": "..."}`
- `ligands`: list of `{"smiles": "..."}`
- `sampling_steps`: integer (default 50)
- `diffusion_samples`: integer (default 1)
- Returns: protein-ligand complex structure
- Use when: starting from SMILES with no SDF file

### NvidiaNIM_genmol
- `smiles`: SMILES with masked positions written as `[*{min-max}]`
  - Example: `COc1cc2ncnc(Nc3ccc([*{1-3}])cc3)c2cc1[*{5-12}]`
  - `[*{1-3}]` = generate 1–3 atoms at that position
- `num_molecules`: integer
- `temperature`: float (2.0 = more diverse; 1.0 = closer to input)
- `scoring`: `"QED"` or `"LogP"`
- Use when: you want scaffold hopping at specific positions

### NvidiaNIM_molmim
- `smi`: reference SMILES (known active)
- `num_molecules`: integer
- `algorithm`: `"CMA-ES"` (recommended)
- Use when: generating close analogs of a top active

---

## ADMET Tool Details

All `ADMETAI_predict_*` tools accept a `smiles` parameter that takes a list of SMILES strings.

### Filter thresholds (recommended defaults)
| Filter | Tool | Threshold |
|--------|------|-----------|
| Lipinski | `ADMETAI_predict_physicochemical_properties` | violations ≤ 1 |
| QED | `ADMETAI_predict_physicochemical_properties` | > 0.3 |
| MW | `ADMETAI_predict_physicochemical_properties` | 200–600 Da |
| Oral bioavailability | `ADMETAI_predict_bioavailability` | > 0.3 |
| AMES mutagenicity | `ADMETAI_predict_toxicity` | < 0.5 |
| hERG cardiotoxicity | `ADMETAI_predict_toxicity` | < 0.5 |
| DILI (liver) | `ADMETAI_predict_toxicity` | < 0.5 |

---

## BindingDB Tool Details

- `BindingDB_get_ligands_by_uniprot(uniprot, affinity_cutoff)`: `affinity_cutoff` is in nM
- `BindingDB_get_targets_by_compound(smiles, similarity_cutoff)`: `similarity_cutoff` is 0–1 Tanimoto
- BindingDB returns `affinity_type` (Ki, IC50, Kd), `affinity` (nM), `pmid`, `monomerid`

---

## GPCRdb Tool Details

- Entry name format: `"{gene_symbol_lower}_human"` — e.g., `"adrb2_human"` for ADRB2
- Operations: `get_protein`, `get_structures`, `get_ligands`, `get_mutations`
- GPCRdb provides Ballesteros-Weinstein generic numbering — use when comparing binding residues across GPCR subtypes

---

## Docking Score Interpretation

| Compound score vs reference | Evidence tier | Priority |
|-----------------------------|---------------|----------|
| Higher than reference | T0 (upgrade) | Top |
| Within 5% of reference | T2 | High |
| Within 20% of reference | Maintain tier | Moderate |
| More than 20% lower | Downgrade one tier | Low |

---

## Source Comparison (ChEMBL vs BindingDB vs PubChem BioAssay)

| Source | Strengths | Best For |
|--------|-----------|----------|
| ChEMBL | Curated, standardized, SAR-ready | Primary ligand source |
| BindingDB | Direct Ki/Kd/IC50 + PMIDs | Affinity verification, unique scaffolds |
| PubChem BioAssay | HTS data, NIH MLPCN screens | Novel scaffolds, broad coverage |

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 | When |
|---|---|---|---|
| `ChEMBL_get_target_activities` | `GtoPdb_get_target_interactions` | `PubChem_search_assays` | No ChEMBL data |
| `ChEMBL_search_similar_molecules` | `PubChem_search_compounds_by_similarity` | `STITCH_get_chemical_protein_interactions` | ChEMBL exhausted |
| `PDB_search_similar_structures` | `NvidiaNIM_alphafold2` | `alphafold_get_prediction` | No PDB structure |
| `alphafold_get_prediction` | `NvidiaNIM_alphafold2` | `NvidiaNIM_esmfold` | AlphaFold DB unavailable |
| `NvidiaNIM_alphafold2` | `NvidiaNIM_esmfold` | `alphafold_get_prediction` | NIM AlphaFold error |
| `NvidiaNIM_diffdock` | `NvidiaNIM_boltz2` | Skip docking, use similarity | Docking error |
| `NvidiaNIM_genmol` | `NvidiaNIM_molmim` | Skip de novo generation | Generation error |
| `OpenTargets_get_target_tractability` | `DGIdb_get_gene_druggability` | Document "Unknown" | Open Targets error |
| `ADMETAI_*` | SwissADME tools | Basic Lipinski only | Invalid SMILES |
| `PDB_search_similar_structures` | `emdb_search` + PDB | `NvidiaNIM_alphafold2` | Membrane proteins |
| `PubMed_search_articles` | `openalex_search_works` | `SemanticScholar_search` | Literature search |

---

## Tool Reference by Phase

### Phase 0 (Verification)
| Tool | Purpose |
|------|---------|
| `get_tool_info` | Check parameter names before calling unfamiliar tools |

### Phase 1 (Target Validation)
| Tool | Purpose |
|------|---------|
| `UniProt_search` | Resolve UniProt accession |
| `MyGene_query_genes` | Get Ensembl / NCBI IDs |
| `ChEMBL_search_targets` | Get ChEMBL target ID |
| `OpenTargets_get_target_tractability_by_ensemblID` | Tractability bucket and score |
| `OpenTargets_get_target_classes_by_ensemblID` | Target class (kinase, GPCR, etc.) |
| `DGIdb_get_gene_druggability` | Druggability categories |
| `GPCRdb_get_protein / _structures / _ligands / _mutations` | GPCR-specific data (if GPCR) |
| `TheraSAbDab_search_by_target` | Therapeutic antibody landscape |
| `ChEMBL_search_binding_sites` | Binding site names and types |
| `InterPro_get_protein_domains` | Domain architecture and active sites |
| `get_binding_affinity_by_pdb_id` | Kd/Ki/IC50 for co-crystallized ligands |
| `NvidiaNIM_alphafold2` | High-accuracy structure prediction (async, needs NVIDIA key) |
| `NvidiaNIM_esmfold` | Fast structure prediction, max 1024 AA (needs NVIDIA key) |
| `alphafold_get_prediction` | Fetch structure from AlphaFold DB (use `accession=`) |

### Phase 2 (Known Ligand Mining)
| Tool | Purpose |
|------|---------|
| `ChEMBL_get_target_activities` | Bioactivity data (use `target_chembl_id=`) |
| `ChEMBL_get_molecule` | Full molecule data including max_phase |
| `GtoPdb_get_target_interactions` | Pharmacology ligands with pKi/pIC50 |
| `OpenTargets_get_chemical_probes_by_target_ensemblID` | Validated chemical probes |
| `BindingDB_get_ligands_by_uniprot` | Affinity data with direct PMIDs |
| `BindingDB_get_targets_by_compound` | Polypharmacology / off-target check |
| `PubChem_search_assays_by_target_gene` | HTS assay IDs (returns AIDs, not compounds) |
| `PubChem_get_assay_active_compounds` | Compound CIDs per assay |

### Phase 3 (Structure Analysis)
| Tool | Purpose |
|------|---------|
| `PDB_search_similar_structures` | Find PDB entries by sequence |
| `get_protein_metadata_by_pdb_id` | Resolution, method, ligand codes |
| `get_ligand_smiles_by_chem_comp_id` | Ligand SMILES from PDB component code |
| `emdb_search` / `emdb_get_entry` | Cryo-EM structures; extract PDB model ID for docking |
| `NvidiaNIM_diffdock` | Blind docking given PDB text + SDF text (needs NVIDIA key) |
| `NvidiaNIM_boltz2` | Protein-ligand complex from sequence + SMILES (needs NVIDIA key) |

### Phase 4 (Compound Expansion)
| Tool | Purpose |
|------|---------|
| `ChEMBL_search_similar_molecules` | Similarity search (use `molecule=`, not `smiles=`) |
| `PubChem_search_compounds_by_similarity` | PubChem Tanimoto similarity search |
| `ChEMBL_search_substructure` | Scaffold-containing compounds |
| `PubChem_search_compounds_by_substructure` | PubChem substructure search |
| `STITCH_get_chemical_protein_interactions` | Cross-database chemical-protein links |
| `DGIdb_get_drug_gene_interactions` | Approved/investigational drugs |
| `NvidiaNIM_genmol` | Scaffold hopping via masked SMILES (needs NVIDIA key) |
| `NvidiaNIM_molmim` | Analog generation from reference SMILES (needs NVIDIA key) |

### Phase 5 (ADMET)
| Tool | Purpose |
|------|---------|
| `ADMETAI_predict_physicochemical_properties` | Lipinski, QED, MW |
| `ADMETAI_predict_bioavailability` | Oral absorption |
| `ADMETAI_predict_toxicity` | AMES, hERG, DILI |
| `ADMETAI_predict_CYP_interactions` | CYP3A4 liability flags |
| `ChEMBL_search_compound_structural_alerts` | PAINS and reactive groups |

### Phase 6.5 (Literature)
| Tool | Purpose |
|------|---------|
| `PubMed_search_articles` | Published SAR studies |
| `BioRxiv_search_preprints` / `MedRxiv_search_preprints` | Preprints (flag as not peer-reviewed) |
| `openalex_search_works` | Citation counts for key papers |
| `SemanticScholar_search` | AI-ranked paper search |
