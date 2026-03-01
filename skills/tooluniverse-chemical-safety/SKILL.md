---
name: tooluniverse-chemical-safety
description: Comprehensive chemical safety and toxicology assessment integrating ADMET-AI predictions, CTD toxicogenomics, FDA label safety data, DrugBank safety profiles, and STITCH chemical-protein interactions. Performs predictive toxicology (AMES, DILI, LD50, carcinogenicity), organ/system toxicity profiling, chemical-gene-disease relationship mapping, regulatory safety extraction, and environmental hazard assessment. Use when asked about chemical toxicity, drug safety profiling, ADMET properties, environmental health risks, chemical hazard assessment, or toxicogenomic analysis.
---

# Chemical Safety & Toxicology Assessment

Comprehensive chemical safety and toxicology analysis integrating predictive AI models, curated toxicogenomics databases, regulatory safety data, and chemical-biological interaction networks. Generates structured risk assessment reports with evidence grading.

## When to Use This Skill

**Triggers**:
- "Is this chemical toxic?" / "What are the toxicity endpoints for [compound]?"
- "Assess the safety profile of [drug/chemical]"
- "What are the ADMET properties of [SMILES]?"
- "What genes does [chemical] interact with?" / "What diseases are linked to [chemical] exposure?"
- "Predict toxicity for these molecules" / "Batch toxicity screening"
- "Drug safety assessment for [drug name]" / "Environmental health risk of [chemical]"
- "Chemical hazard profiling" / "Toxicogenomic analysis of [compound]"

**Use Cases**:
1. **Predictive Toxicology**: AI-predicted endpoints (AMES, DILI, LD50, carcinogenicity, skin reactions) for novel compounds via SMILES
2. **ADMET Profiling**: Full absorption, distribution, metabolism, excretion, toxicity characterization
3. **Toxicogenomics**: Chemical-gene interaction mapping, gene-disease associations from CTD
4. **Regulatory Safety**: FDA label warnings, boxed warnings, contraindications, adverse reactions
5. **Drug Safety Assessment**: Combined DrugBank safety + FDA labels + adverse event data
6. **Chemical-Protein Interactions**: STITCH-based chemical-protein binding and interaction networks
7. **Environmental Toxicology**: Chemical-disease associations for environmental contaminants

---

## Key Principles

1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Disambiguation first** - Resolve compound identity (name -> SMILES, CID, ChEMBL ID) before analysis
3. **Evidence grading** - Grade all safety claims by evidence strength (T1-T4)
4. **Citation requirements** - Every toxicity finding must have inline source attribution
5. **Mandatory completeness** - All sections must exist with data minimums or explicit "No data" notes
6. **Negative results documented** - "No toxicity signals found" is valid data; empty sections are failures
7. **Conservative risk assessment** - When evidence is ambiguous, flag as "requires further investigation"
8. **English-first queries** - Always use English chemical/drug names in tool calls

---

## Evidence Grading System (MANDATORY)

Grade every toxicity claim with one of these tiers:

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|---------|
| T1 | [T1] | Direct human evidence, regulatory finding | FDA boxed warning, clinical trial toxicity |
| T2 | [T2] | Animal studies, validated in vitro | Nonclinical toxicology, AMES positive, animal LD50 |
| T3 | [T3] | Computational prediction, association data | ADMET-AI prediction, CTD inferred association |
| T4 | [T4] | Database annotation, text-mined | Literature mention without validation |

Evidence grades MUST appear in: Executive Summary, Toxicity Predictions, Regulatory Safety section, CTD results, and the final Risk Assessment.

---

## Research Workflow: 8 Phases

```
Chemical/Drug Query
|
+-- PHASE 0: Compound Disambiguation (ALWAYS FIRST)
|   +-- Resolve name -> SMILES, PubChem CID, ChEMBL ID
|   +-- Get molecular formula, weight, canonical structure
|
+-- PHASE 1: Predictive Toxicology (ADMET-AI)
|   +-- Mutagenicity (AMES), Hepatotoxicity (DILI, ClinTox)
|   +-- Carcinogenicity, Acute toxicity (LD50), Skin reactions
|   +-- Stress response pathways, Nuclear receptor activity
|
+-- PHASE 2: ADMET Properties
|   +-- Absorption: BBB penetrance, bioavailability
|   +-- Distribution: clearance, volume of distribution
|   +-- Metabolism: CYP interactions (1A2, 2C9, 2C19, 2D6, 3A4)
|   +-- Physicochemical: solubility, lipophilicity, pKa
|
+-- PHASE 3: Toxicogenomics (CTD)
|   +-- Chemical-gene interactions
|   +-- Chemical-disease associations
|   +-- Affected biological pathways
|
+-- PHASE 4: Regulatory Safety (FDA Labels)
|   +-- Boxed warnings, Contraindications, Adverse reactions
|   +-- Warnings and precautions, Nonclinical toxicology
|
+-- PHASE 5: Drug Safety Profile (DrugBank)
|   +-- Toxicity data, Contraindications
|   +-- Drug interactions affecting safety
|
+-- PHASE 6: Chemical-Protein Interactions (STITCH)
|   +-- Direct chemical-protein binding
|   +-- Interaction confidence scores, Off-target effects
|
+-- PHASE 7: Structural Alerts (ChEMBL)
|   +-- Known toxic substructures (PAINS, Brenk)
|
+-- SYNTHESIS: Integrated Risk Assessment
    +-- Aggregate all evidence tiers
    +-- Risk classification (Low/Medium/High/Critical)
    +-- Data gaps and recommendations
```

---

## Phase 0: Compound Disambiguation (ALWAYS FIRST)

Resolve compound identity before any analysis. Determine input type then apply the appropriate strategy:

| Input Format | Detection | Resolution Strategy |
|-------------|-----------|---------------------|
| Drug/chemical name | Default if not SMILES/CID/ChEMBL | `PubChem_get_CID_by_compound_name` -> `PubChem_get_compound_properties_by_CID` |
| SMILES string | Contains `=`, `#`, `[`, `]`, `(`, `)` or lowercase `c`, `n`, `o` | Use directly for ADMET-AI; resolve to CID via PubChem |
| PubChem CID | Numeric only | `PubChem_get_compound_properties_by_CID` directly |
| ChEMBL ID | Starts with "CHEMBL" | `ChEMBL_get_molecule` -> get SMILES + properties |

After resolution, store: `name`, `smiles`, `cid`, `formula`, `weight`, `inchi`. Extract SMILES from PubChem response field `ConnectivitySMILES`, `CanonicalSMILES`, or `IsomericSMILES`.

**Output template:**
```markdown
## Compound Identity
| Property | Value |
|----------|-------|
| Name | Acetaminophen |
| PubChem CID | 1983 |
| SMILES | CC(=O)Nc1ccc(O)cc1 |
| Formula | C8H9NO2 |
| Molecular Weight | 151.16 |
```

---

## Phase 1: Predictive Toxicology (ADMET-AI)

Run when SMILES is available. Call all three tools; they are independent and can run in parallel.

| Tool | Endpoints Predicted |
|------|---------------------|
| `ADMETAI_predict_toxicity` | AMES mutagenicity, Carcinogens_Lagunin, ClinTox, DILI, LD50_Zhu, Skin_Reaction, hERG |
| `ADMETAI_predict_stress_response` | ARE, ATAD5, HSE, MMP, p53 pathway activation |
| `ADMETAI_predict_nuclear_receptor_activity` | AhR, AR, ER, PPARg, Aromatase activity |

All three tools accept `smiles` as a list of strings. Batch up to ~10 SMILES in a single call. All predictions are graded [T3] (computational).

**Interpretation rules:**
- Classification endpoints: Active (1) = toxic signal; Inactive (0) = no signal
- Regression endpoint (LD50): Report the numerical value with context (log mg/kg)
- If ADMET-AI fails for a compound, note "prediction unavailable" and continue
- **hERG Active** -> flag prominently as cardiac safety risk
- **AMES Active** -> flag prominently as mutagenicity concern
- **DILI Active** -> flag prominently as liver toxicity concern

**Output template:**
```markdown
### Toxicity Predictions [T3]
| Endpoint | Prediction | Concern Level |
|----------|-----------|---------------|
| AMES Mutagenicity | Inactive | Low |
| DILI | Active | HIGH |
| LD50 (Zhu) | 2.45 log(mg/kg) (~282 mg/kg) | Medium |
| hERG Inhibition | Active | HIGH |
| Skin Reaction | Inactive | Low |
*Evidence tier: [T3] (ADMET-AI computational prediction)*
```

---

## Phase 2: ADMET Properties

Run when SMILES is available. All six tools are independent; call in parallel.

| Tool | Properties |
|------|-----------|
| `ADMETAI_predict_BBB_penetrance` | Blood-brain barrier crossing probability |
| `ADMETAI_predict_bioavailability` | Oral bioavailability (F20%, F30%) |
| `ADMETAI_predict_clearance_distribution` | Clearance, VDss, half-life, PPB |
| `ADMETAI_predict_CYP_interactions` | CYP1A2/2C9/2C19/2D6/3A4 inhibition and substrate status |
| `ADMETAI_predict_physicochemical_properties` | LogP, LogD, LogS, MW, pKa, Lipinski compliance |
| `ADMETAI_predict_solubility_lipophilicity_hydration` | Aqueous solubility, lipophilicity, hydration free energy |

**Decision logic:**
- BBB penetrant + any CNS toxicity endpoint active -> flag as neurotoxicity risk
- F20% = Low -> note oral absorption concern
- CYP3A4 inhibitor = Yes -> flag high drug-drug interaction (DDI) risk
- Count Lipinski violations and report drug-likeness assessment

**Output template:**
```markdown
### ADMET Profile [T3]
#### Absorption
| Property | Value | Interpretation |
|----------|-------|----------------|
| BBB Penetrance | Yes | Crosses blood-brain barrier |
| Bioavailability (F20%) | 85% | Good oral absorption |

#### Metabolism (CYP Interactions)
| CYP Enzyme | Substrate | Inhibitor |
|------------|-----------|-----------|
| CYP3A4 | Yes | Yes (DDI risk) |
| CYP2D6 | No | No |
```

---

## Phase 3: Toxicogenomics (CTD)

Run when compound name is resolved. Requires the chemical name (not SMILES or CID).

Call `CTD_get_chemical_gene_interactions(input_terms=compound_name)` and `CTD_get_chemical_diseases(input_terms=compound_name)`. Both accept a string: common chemical name, MeSH name, CAS RN, or MeSH ID. If the common name returns no results, try the MeSH name.

**Grading:**
- Direct curated CTD evidence from literature -> [T2]
- Computationally inferred associations -> [T3]

**Interpretation rules:**
- Distinguish therapeutic disease associations (drug treats disease) from adverse (chemical causes disease)
- Prioritize "marker/mechanism" evidence over simple "association" — stronger causal signal
- Gene interaction types: expression changes, binding, and activity modulation carry different weight
- Report top 20 gene interactions and top 10 disease associations; note total count

**Output template:**
```markdown
### Toxicogenomics (CTD) [T2/T3]
#### Chemical-Gene Interactions (Top 20 of N total)
| Gene | Interaction | Evidence |
|------|------------|---------|
| CYP1A2 | increases expression | [T2] curated |
| TP53 | affects activity | [T2] curated |

#### Chemical-Disease Associations (Top 10)
| Disease | Association Type | Evidence |
|---------|-----------------|---------|
| Liver Neoplasms | marker/mechanism | [T2] curated |

**Top affected pathways**: Xenobiotic metabolism, Apoptosis, DNA damage response
```

---

## Phase 4: Regulatory Safety (FDA Labels)

Run when the compound has an approved drug name. All six tools are independent; call in parallel.

| Tool | Information Retrieved |
|------|----------------------|
| `FDA_get_boxed_warning_info_by_drug_name` | Black box warnings (most serious) |
| `FDA_get_contraindications_by_drug_name` | Absolute contraindications |
| `FDA_get_adverse_reactions_by_drug_name` | Known adverse reactions |
| `FDA_get_warnings_by_drug_name` | Warnings and precautions |
| `FDA_get_nonclinical_toxicology_info_by_drug_name` | Animal toxicology data [T2] |
| `FDA_get_carcinogenic_mutagenic_fertility_by_drug_name` | Carcinogenicity/mutagenicity/fertility data [T2] |

All tools accept `drug_name` as a string (brand or generic name).

**Decision logic:**
- Boxed warning present -> flag as CRITICAL in executive summary [T1]
- No FDA data returned -> note "Not an FDA-approved drug" and continue with other phases
- If first name fails, retry with alternative name (brand vs. generic)
- Nonclinical toxicology data is [T2]; all other FDA label data is [T1]
- Categorize warnings by organ system (hepatic, cardiac, renal, CNS, etc.)

**Output template:**
```markdown
### Regulatory Safety (FDA) [T1]
#### Boxed Warning
**PRESENT** — Hepatotoxicity risk with doses >4g/day. Liver failure reported. [T1]

#### Contraindications
- Severe hepatic impairment [T1]

#### Nonclinical Toxicology [T2]
- Carcinogenicity: No carcinogenic potential in 2-year rat/mouse studies
- Mutagenicity: Negative in Ames assay and in vivo micronucleus test
```

---

## Phase 5: Drug Safety Profile (DrugBank)

Run when compound is a known drug.

Call `drugbank_get_safety_by_drug_name_or_drugbank_id` with `query=drug_name`, `case_sensitive=False`, `exact_match=False`, `limit=5`.

Parse toxicity (LD50 values, overdose symptoms, organ toxicity), contraindications, and any DrugBank ID for cross-referencing. If DrugBank and FDA disagree on a finding, note the discrepancy and defer to FDA [T1]. If not found, note "not found in DrugBank" and continue.

---

## Phase 6: Chemical-Protein Interactions (STITCH)

Run when the compound can be identified by name or SMILES.

1. Resolve compound: call `STITCH_resolve_identifier` with `identifier=compound_name` and `species=9606` (human)
2. Get interactions: call `STITCH_get_chemical_protein_interactions` with the resolved STITCH ID, `species=9606`, `required_score=700`
3. Identify off-target proteins not intended as the drug target
4. Flag safety-relevant targets: hERG (cardiac), CYP enzymes (metabolism), nuclear receptors (endocrine)

**Confidence grading:**
- Score > 900 -> well-established interaction [T2]
- Score 700-900 -> probable interaction [T3]
- Score 400-700 -> possible interaction, needs validation [T4]

If STITCH returns no data, note "no STITCH data available" and continue.

---

## Phase 7: Structural Alerts (ChEMBL)

Run when a ChEMBL ID was obtained in Phase 0. If no ChEMBL ID is available, skip and note "structural alert analysis not available."

Call `ChEMBL_search_compound_structural_alerts` with `molecule_chembl_id=chembl_id` and `limit=20`.

Parse alert types:
- **PAINS** (pan-assay interference) — may cause false positives in screening; informational for medicinal chemistry
- **Brenk** — known problematic substructures; flag if present as [T3] concern
- **Glaxo/GSK** — additional structural alert set

No alerts does not definitively confirm safety; absence of ChEMBL ID is not a failure.

---

## Synthesis: Integrated Risk Assessment (MANDATORY)

Always the final section. Aggregate all phase results into a risk classification.

### Risk Classification Matrix

| Risk Level | Criteria |
|-----------|---------|
| CRITICAL | FDA boxed warning present OR multiple [T1] toxicity findings OR active DILI + active hERG |
| HIGH | FDA warnings present OR [T2] animal toxicity OR multiple active ADMET endpoints |
| MEDIUM | Some [T3] predictions positive OR CTD disease associations OR structural alerts |
| LOW | All ADMET endpoints negative AND no FDA/DrugBank safety flags AND no CTD concerns |
| INSUFFICIENT DATA | Fewer than 3 phases returned data; cannot make confident assessment |

**Output template:**
```markdown
## Integrated Risk Assessment

### Overall Risk Classification: [HIGH]

### Evidence Summary
| Dimension | Finding | Evidence Tier | Concern |
|-----------|---------|--------------|---------|
| ADMET Toxicity | DILI active, hERG active | [T3] | HIGH |
| FDA Label | Boxed warning for hepatotoxicity | [T1] | CRITICAL |
| CTD Toxicogenomics | 156 gene interactions, liver neoplasms | [T2] | HIGH |
| DrugBank | Known hepatotoxicity at high doses | [T2] | HIGH |
| STITCH | Binds CYP3A4, hERG | [T3] | MEDIUM |
| Structural Alerts | 2 Brenk alerts | [T3] | MEDIUM |

### Key Safety Concerns
1. **Hepatotoxicity** [T1]: FDA boxed warning + ADMET-AI DILI + CTD liver disease associations
2. **Cardiac Risk** [T3]: ADMET-AI hERG prediction + STITCH hERG interaction
3. **Drug Interactions** [T3]: CYP3A4 substrate/inhibitor — DDI risk

### Data Gaps
- [ ] No in vivo genotoxicity data available
- [ ] STITCH interaction scores moderate (700-900)

### Recommendations
1. Avoid doses >4g/day (hepatotoxicity threshold) [T1]
2. Monitor liver function in chronic use [T1]
3. Screen for CYP3A4 interactions before co-administration [T3]
```

---

## Mandatory Completeness Checklist

Before finalizing any report, verify all phases are accounted for:

- [ ] **Phase 0**: Compound fully disambiguated (SMILES + CID at minimum)
- [ ] **Phase 1**: At least 5 toxicity endpoints reported or "prediction unavailable" noted
- [ ] **Phase 2**: ADMET profile with A/D/M/E sections or "not available" noted
- [ ] **Phase 3**: CTD queried; gene interactions and disease associations reported or "no data in CTD"
- [ ] **Phase 4**: FDA labels queried; results or "not an FDA-approved drug" noted
- [ ] **Phase 5**: DrugBank queried; results or "not found in DrugBank" noted
- [ ] **Phase 6**: STITCH queried; results or "no STITCH data available" noted
- [ ] **Phase 7**: Structural alerts checked or "ChEMBL ID not available" noted
- [ ] **Synthesis**: Risk classification provided with evidence summary and data gaps
- [ ] **Evidence Grading**: All findings annotated with [T1]-[T4]

---

## Common Use Patterns

**Pattern 1 — Novel compound (SMILES input):**
Phase 0 (SMILES -> CID) -> Phase 1 -> Phase 2 -> Phase 7 (structural alerts) -> Synthesis. FDA/DrugBank phases will be empty for novel compounds; note this explicitly.

**Pattern 2 — Approved drug safety review:**
All phases 0-7 + Synthesis. Most complete dossier; combines regulatory [T1], experimental [T2], and predictive [T3] evidence.

**Pattern 3 — Environmental chemical risk:**
Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 (CTD is central for environmental chemicals) -> Phase 6 -> Synthesis. FDA/DrugBank will typically be empty.

**Pattern 4 — Batch toxicity screening:**
Phase 0 -> Phase 1 (batch all SMILES) -> Phase 2 (batch) -> Comparative ranking table -> Synthesis. ADMET-AI accepts up to ~10 SMILES per call.

**Pattern 5 — Toxicogenomic deep-dive:**
Phase 0 -> Phase 3 (CTD expanded, top 50 interactions) -> targeted literature follow-up -> Synthesis focused on gene-disease mechanisms.

---

## Output Report Structure

```markdown
# Chemical Safety & Toxicology Report: [Compound Name]
**Generated**: YYYY-MM-DD | **Compound**: [Name] | SMILES: [...] | CID: [...]

## Executive Summary
[2-3 sentence overview with overall risk classification and key findings graded by tier]

## 1. Compound Identity            [Phase 0]
## 2. Predictive Toxicology        [Phase 1 — ADMET-AI toxicity endpoints]
## 3. ADMET Profile                [Phase 2 — Absorption/Distribution/Metabolism/Excretion]
## 4. Toxicogenomics               [Phase 3 — CTD chemical-gene-disease]
## 5. Regulatory Safety            [Phase 4 — FDA label information]
## 6. Drug Safety Profile          [Phase 5 — DrugBank]
## 7. Chemical-Protein Interactions [Phase 6 — STITCH network]
## 8. Structural Alerts            [Phase 7 — ChEMBL alerts]
## 9. Integrated Risk Assessment   [Synthesis]
## Appendix: Methods and Data Sources
```

---

## Known Gotchas

**Compound disambiguation:**
- PubChem CID lookup returns `{IdentifierList: {CID: [...]}}` — the CID is inside a list; extract `[0]`
- PubChem properties response fields are `ConnectivitySMILES`, `CanonicalSMILES`, or `IsomericSMILES` depending on the query; check all three
- SMILES strings passed to ADMET-AI must always be wrapped in a list even for a single compound: `smiles=["CC(=O)Nc1ccc(O)cc1"]`

**FDA tools:**
- FDA returns no data for non-approved drugs, supplements, and environmental chemicals — this is expected, not an error
- Try both brand name and generic name if first query fails
- Nonclinical toxicology data is [T2], not [T1], even though it comes from an FDA label

**CTD tools:**
- `input_terms` accepts common name, MeSH name, CAS RN, or MeSH ID — try MeSH name as fallback if common name returns nothing
- CTD separates curated direct evidence (literature-backed, [T2]) from inferred associations (computational, [T3]) — do not flatten these into the same tier
- Novel or industrial chemicals may have zero CTD entries; this is data, not a failure

**DrugBank:**
- `drugbank_get_safety_by_drug_name_or_drugbank_id` requires all four params: `query`, `case_sensitive`, `exact_match`, `limit`
- When DrugBank and FDA disagree, document the discrepancy and defer to FDA [T1]

**STITCH:**
- `STITCH_resolve_identifier` must precede `STITCH_get_chemical_protein_interactions` — do not guess STITCH IDs
- `required_score=700` is recommended as baseline; lower scores significantly increase false positives
- `species=9606` for human interactions throughout

**ADMET-AI batch:**
- Very large or unusual SMILES (e.g., macrocycles, polymers) may cause prediction failures; handle per-compound, not as batch failures
- LD50 is reported as log(mg/kg); convert to mg/kg for the report (10^value)

**Risk classification:**
- "INSUFFICIENT DATA" is a valid classification when fewer than 3 phases return results; do not inflate to LOW
- Active hERG alone does not trigger CRITICAL — it triggers HIGH; CRITICAL requires FDA boxed warning or [T1] evidence

---

## Abbreviated Tool Reference

For full parameter details, see [`references/tools.md`](references/tools.md).

| Phase | Tool | Key Parameter(s) |
|-------|------|-----------------|
| 0 | `PubChem_get_CID_by_compound_name` | `name`: str |
| 0 | `PubChem_get_compound_properties_by_CID` | `cid`: int |
| 0 | `ChEMBL_get_molecule` | `molecule_chembl_id`: str |
| 1-2 | All `ADMETAI_predict_*` tools | `smiles`: list[str] |
| 3 | `CTD_get_chemical_gene_interactions` | `input_terms`: str |
| 3 | `CTD_get_chemical_diseases` | `input_terms`: str |
| 4 | All `FDA_get_*_by_drug_name` tools | `drug_name`: str |
| 5 | `drugbank_get_safety_by_drug_name_or_drugbank_id` | `query`: str, `case_sensitive`: bool, `exact_match`: bool, `limit`: int |
| 6 | `STITCH_resolve_identifier` | `identifier`: str, `species`: int (9606) |
| 6 | `STITCH_get_chemical_protein_interactions` | `identifiers`: list[str], `species`: int, `required_score`: int |
| 7 | `ChEMBL_search_compound_structural_alerts` | `molecule_chembl_id`: str, `limit`: int |

---

## Limitations

- **ADMET-AI**: Predictions are [T3]; should not replace experimental testing
- **CTD**: Curated but may lag behind latest literature by 6-12 months
- **FDA**: Only covers FDA-approved drugs; not applicable to environmental chemicals or supplements
- **DrugBank**: Primarily drugs; limited coverage of industrial chemicals
- **STITCH**: Score thresholds affect sensitivity; lower scores increase false positives
- **Batch mode**: ADMET-AI supports batching; FDA, DrugBank, and CTD require individual queries
- **Novel compounds**: May only have ADMET-AI predictions; all database phases will be empty
- **SMILES validity**: Invalid SMILES will cause ADMET-AI failures — validate before calling
