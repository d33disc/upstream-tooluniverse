# Chemical Safety: Detailed Tool Reference

Full parameter details and response format notes for all tools used in the Chemical Safety & Toxicology Assessment skill. For the workflow guide, see [SKILL.md](../SKILL.md).

---

## Phase 0: Compound Disambiguation

### PubChem

| Tool | Parameter | Type | Notes |
|------|-----------|------|-------|
| `PubChem_get_CID_by_compound_name` | `name` | str | Common name, IUPAC name, or synonym |
| `PubChem_get_compound_properties_by_CID` | `cid` | int | Numeric CID |

**PubChem CID lookup response structure:**
```json
{"IdentifierList": {"CID": [1983]}}
```
Extract CID as `response["IdentifierList"]["CID"][0]`.

**PubChem compound properties response fields:**
- `CID` — PubChem compound ID
- `MolecularWeight` — molecular weight in g/mol
- `ConnectivitySMILES` or `CanonicalSMILES` or `IsomericSMILES` — check all three; field name varies by query
- `IUPACName` — systematic name
- `MolecularFormula` — e.g., `C8H9NO2`
- `InChI`, `InChIKey` — standard identifiers

### ChEMBL

| Tool | Parameter | Type | Notes |
|------|-----------|------|-------|
| `ChEMBL_get_molecule` | `molecule_chembl_id` | str | e.g., `"CHEMBL112"` — always a string, never int |
| `ChEMBL_search_compounds` | `query` | str | Name or synonym search |

**ChEMBL molecule response fields:**
- `molecule_chembl_id` — ChEMBL identifier
- `pref_name` — preferred name
- `molecule_structures.canonical_smiles` — canonical SMILES
- `molecule_properties` — MW, AlogP, HBD, HBA, PSA, num_ro5_violations

---

## Phase 1: Predictive Toxicology (ADMET-AI)

All ADMET-AI tools share the same parameter signature.

**Universal parameter:**

| Parameter | Type | Notes |
|-----------|------|-------|
| `smiles` | list[str] | Always a list, even for a single compound. Up to ~10 SMILES per call. |

**Response envelope:**
```json
{"status": "success", "data": {"SMILES_0": {"endpoint_name": value, ...}}}
```

### `ADMETAI_predict_toxicity`

| Output Field | Type | Interpretation |
|-------------|------|----------------|
| `AMES` | int (0/1) | 1 = mutagenic signal (Ames test prediction) |
| `Carcinogens_Lagunin` | int (0/1) | 1 = carcinogenic signal |
| `ClinTox` | int (0/1) | 1 = clinical toxicity concern |
| `DILI` | int (0/1) | 1 = drug-induced liver injury risk |
| `LD50_Zhu` | float | Acute oral toxicity in log(mg/kg); convert to mg/kg as 10^value |
| `Skin_Reaction` | int (0/1) | 1 = skin sensitization signal |
| `hERG` | int (0/1) | 1 = hERG channel inhibition (cardiac arrhythmia risk) |

### `ADMETAI_predict_stress_response`

| Output Field | Interpretation |
|-------------|----------------|
| `ARE` | Antioxidant response element activation |
| `ATAD5` | DNA damage / genotoxicity stress |
| `HSE` | Heat shock / protein stress |
| `MMP` | Mitochondrial membrane potential disruption |
| `p53` | p53 pathway activation (DNA damage, apoptosis) |

### `ADMETAI_predict_nuclear_receptor_activity`

| Output Field | Interpretation |
|-------------|----------------|
| `AhR` | Aryl hydrocarbon receptor activation (dioxin-like toxicity) |
| `AR` | Androgen receptor activity (endocrine disruption) |
| `ER` | Estrogen receptor activity (endocrine disruption) |
| `PPARg` | Peroxisome proliferator-activated receptor gamma activity |
| `Aromatase` | Aromatase inhibition (sex hormone disruption) |

---

## Phase 2: ADMET Properties (ADMET-AI)

Same `smiles: list[str]` parameter and `{"status", "data"}` response envelope as Phase 1.

### `ADMETAI_predict_BBB_penetrance`

| Output Field | Type | Interpretation |
|-------------|------|----------------|
| `BBB_Martins` | float (0-1) | Probability of crossing blood-brain barrier; >0.5 = penetrant |

### `ADMETAI_predict_bioavailability`

| Output Field | Type | Interpretation |
|-------------|------|----------------|
| `Bioavailability_Ma` | int (0/1) | 1 = >20% oral bioavailability predicted |
| `HIA_Hou` | int (0/1) | Human intestinal absorption |
| `PAMPA_NCATS` | float | Passive permeability (parallel artificial membrane) |
| `Caco2_Wang` | float | Caco-2 permeability |
| `Pgp_Broccatelli` | int (0/1) | P-glycoprotein substrate (efflux risk) |

### `ADMETAI_predict_clearance_distribution`

| Output Field | Type | Interpretation |
|-------------|------|----------------|
| `Clearance_Hepatocyte_AZ` | float | Hepatocyte clearance (mL/min/10^6 cells) |
| `Half_Life_Obach` | float | Plasma half-life (hours) |
| `VDss_Lombardo` | float | Volume of distribution at steady state (L/kg) |
| `PPBR_AZ` | float | Plasma protein binding ratio (%) |

### `ADMETAI_predict_CYP_interactions`

| Output Field | Type | Interpretation |
|-------------|------|----------------|
| `CYP1A2_Inhibitor` | int (0/1) | 1 = inhibits CYP1A2 |
| `CYP1A2_Substrate` | int (0/1) | 1 = metabolized by CYP1A2 |
| `CYP2C9_Inhibitor` | int (0/1) | |
| `CYP2C9_Substrate` | int (0/1) | |
| `CYP2C19_Inhibitor` | int (0/1) | |
| `CYP2C19_Substrate` | int (0/1) | |
| `CYP2D6_Inhibitor` | int (0/1) | |
| `CYP2D6_Substrate` | int (0/1) | |
| `CYP3A4_Inhibitor` | int (0/1) | 1 = high DDI risk |
| `CYP3A4_Substrate` | int (0/1) | |

### `ADMETAI_predict_physicochemical_properties`

| Output Field | Type | Interpretation |
|-------------|------|----------------|
| `MW` | float | Molecular weight (g/mol); Lipinski: <500 |
| `LogP` | float | Lipophilicity; Lipinski: <5 |
| `HBD` | int | H-bond donors; Lipinski: ≤5 |
| `HBA` | int | H-bond acceptors; Lipinski: ≤10 |
| `TPSA` | float | Topological polar surface area |
| `num_ro5_violations` | int | Lipinski Rule of 5 violations |
| `QED` | float | Drug-likeness score (0-1) |

### `ADMETAI_predict_solubility_lipophilicity_hydration`

| Output Field | Type | Interpretation |
|-------------|------|----------------|
| `Solubility_AqSolDB` | float | Aqueous solubility log(mol/L) |
| `Lipophilicity_AstraZeneca` | float | LogD at pH 7.4 |
| `HydrationFreeEnergy_FreeSolv` | float | Hydration free energy (kcal/mol) |

---

## Phase 3: Toxicogenomics (CTD)

| Tool | Parameter | Type | Notes |
|------|-----------|------|-------|
| `CTD_get_chemical_gene_interactions` | `input_terms` | str | Chemical name, MeSH name, CAS RN, or MeSH ID |
| `CTD_get_chemical_diseases` | `input_terms` | str | Same as above |

**Response format (gene interactions):** List of objects with fields:
- `GeneSymbol`, `GeneName` — target gene
- `InteractionActions` — e.g., `"increases^expression"`, `"decreases^activity"`, `"binds"`
- `InteractionTypes` — e.g., `"mRNA"`, `"protein"`
- `PubMedIDs` — supporting literature (curated entries have PubMed IDs; inferred do not)

**Response format (disease associations):** List of objects with fields:
- `DiseaseName`, `DiseaseID` — MeSH disease term and ID
- `DirectEvidence` — `"marker/mechanism"`, `"therapeutic"`, or empty (inferred)
- `InferenceScore` — numeric; higher = stronger inferred association
- `OmimIDs`, `PubMedIDs` — supporting evidence

**Evidence grading from CTD:**
- `DirectEvidence` is non-empty AND `PubMedIDs` present -> curated literature-backed [T2]
- `DirectEvidence` is empty -> computationally inferred [T3]
- `DirectEvidence = "therapeutic"` -> drug treats disease (positive relationship, not a hazard signal)

---

## Phase 4: Regulatory Safety (FDA Labels)

| Tool | Parameter | Type | Notes |
|------|-----------|------|-------|
| `FDA_get_boxed_warning_info_by_drug_name` | `drug_name` | str | Brand or generic name |
| `FDA_get_contraindications_by_drug_name` | `drug_name` | str | |
| `FDA_get_adverse_reactions_by_drug_name` | `drug_name` | str | |
| `FDA_get_warnings_by_drug_name` | `drug_name` | str | |
| `FDA_get_nonclinical_toxicology_info_by_drug_name` | `drug_name` | str | |
| `FDA_get_carcinogenic_mutagenic_fertility_by_drug_name` | `drug_name` | str | |

**Response envelope:** `{"status": "success"/"error", "data": "...label text..."}` or `{"status": "error", "message": "..."}`.

If status is "error" or data is empty, the drug is likely not in the FDA database. Try alternative names before concluding "not an FDA-approved drug."

Rate notes: FDA endpoints may throttle under rapid parallel queries; brief retry is acceptable.

---

## Phase 5: Drug Safety Profile (DrugBank)

| Tool | Parameter | Type | Required | Notes |
|------|-----------|------|----------|-------|
| `drugbank_get_safety_by_drug_name_or_drugbank_id` | `query` | str | Yes | Drug name or DrugBank ID (e.g., `"DB00316"`) |
| | `case_sensitive` | bool | Yes | Use `false` for name searches |
| | `exact_match` | bool | Yes | Use `false` to allow partial matches |
| | `limit` | int | Yes | Typically `5`; increase if first match is wrong compound |

**Response:** `{"data": [...drug records...]}` — each record contains:
- `name` — drug name
- `drugbank_id` — DrugBank identifier
- `toxicity` — free text with LD50 values, overdose symptoms, organ toxicity
- `contraindications` — structured list
- `drug_interactions` — list of interacting drugs with descriptions

---

## Phase 6: Chemical-Protein Interactions (STITCH)

| Tool | Parameter | Type | Notes |
|------|-----------|------|-------|
| `STITCH_resolve_identifier` | `identifier` | str | Chemical name or CID |
| | `species` | int | `9606` for human |
| `STITCH_get_chemical_protein_interactions` | `identifiers` | list[str] | STITCH IDs from resolve step |
| | `species` | int | `9606` for human |
| | `required_score` | int | Minimum confidence (400=low, 700=medium, 900=high); default `400`; recommended `700` |
| `STITCH_get_interaction_partners` | `identifiers` | list[str] | STITCH IDs |
| | `species` | int | `9606` |
| | `limit` | int | Max partners to return |

**Response (interactions):** List of objects with fields:
- `stringId_A`, `stringId_B` — interaction partner identifiers
- `score` — combined confidence score (0-1000)
- `nscore`, `fscore`, `pscore`, `ascore`, `escore`, `dscore` — channel-specific scores (neighborhood, fusion, co-occurrence, co-expression, experimental, database)

**STITCH ID format:** Internal CID prefixed with species, e.g., `9606.CIDs00001983`. Do not construct manually; always use `STITCH_resolve_identifier` first.

---

## Phase 7: Structural Alerts (ChEMBL)

| Tool | Parameter | Type | Notes |
|------|-----------|------|-------|
| `ChEMBL_search_compound_structural_alerts` | `molecule_chembl_id` | str | e.g., `"CHEMBL112"` |
| | `limit` | int | Typically `20`; increase for thorough scan |

**Response:** List of alert objects with fields:
- `alert_set` — `"PAINS"`, `"Brenk"`, `"Glaxo"`, `"SureChEMBL"`, or other alert set name
- `alert_name` — specific alert (e.g., `"Aniline"`, `"Michael_acceptor"`)
- `smarts` — SMARTS pattern that matched
- `alert_id` — ChEMBL internal ID

**Alert set severity guide:**
- **Brenk** — Most actionable; flags reactive or metabolically labile substructures
- **PAINS** — Pan-assay interference; informational for screening context
- **Glaxo** — Additional medicinal chemistry filters
- **SureChEMBL** — Patent-based; less direct toxicity relevance

---

## Response Format Summary

| Source | Top-level Structure |
|--------|-------------------|
| ADMET-AI (all) | `{"status": "success", "data": {"SMILES_0": {field: value, ...}}}` |
| CTD | Direct list of interaction/association objects |
| FDA (all) | `{"status": "success"/"error", "data": "label text"}` |
| DrugBank safety | `{"data": [...drug records...]}` |
| STITCH interactions | List of interaction objects with score fields |
| PubChem CID lookup | `{"IdentifierList": {"CID": [int, ...]}}` |
| PubChem properties | Dict with `CID`, `MolecularWeight`, `ConnectivitySMILES`, `IUPACName`, etc. |
| ChEMBL molecule | Nested dict with `molecule_chembl_id`, `pref_name`, `molecule_structures`, `molecule_properties` |
| ChEMBL alerts | List of alert objects with `alert_set`, `alert_name`, `smarts` |
