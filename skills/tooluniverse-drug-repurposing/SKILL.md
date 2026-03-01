---
name: tooluniverse-drug-repurposing
description: Identify drug repurposing candidates using ToolUniverse for target-based, compound-based, and disease-driven strategies. Searches existing drugs for new therapeutic indications by analyzing targets, bioactivity, safety profiles, and literature evidence. Use when exploring drug repurposing opportunities, finding new indications for approved drugs, or when users mention drug repositioning, off-label uses, or therapeutic alternatives.
---

# Drug Repurposing with ToolUniverse

Systematically identify and evaluate drug repurposing candidates using multiple computational strategies.

**IMPORTANT**: Always use English terms in tool calls (drug names, disease names, target names), even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

## Core Strategies

| Strategy | Starting Point | Direction |
|----------|---------------|-----------|
| Target-based | Disease targets | Find drugs that modulate those targets |
| Compound-based | Approved drugs | Find new disease indications |
| Disease-driven | Disease phenotype | Find targets, then match to existing drugs |
| Mechanism-based | Known MoA | Find drugs with similar mechanism |
| Network-based | Pathway membership | Find drugs affecting shared pathways |
| Phenotype-based | Indication similarity | Find drugs approved for related conditions |

---

## Workflow Overview

```
Phase 1: Disease & Target Analysis
├── Get disease EFO ID (OpenTargets)
├── Retrieve associated targets with scores
└── Assess target druggability (DGIdb)
    ↓
Phase 2: Drug Discovery
├── Search DrugBank by target name
├── Search DGIdb drug-gene interactions
├── Search ChEMBL drugs
├── Search OpenTargets approved drugs for disease
└── Deduplicate across sources
    ↓
Phase 3: Drug Detail Enrichment
├── Basic drug info + approval status (DrugBank)
├── Current indications (DrugBank / OpenTargets)
├── Pharmacology + mechanism of action (DrugBank / FDA)
└── Drug-target profile (DrugBank)
    ↓
Phase 4: Safety Assessment
├── Boxed warnings + contraindications (FDA)
├── Adverse event profile (FAERS)
├── Drug-drug interaction risk (DrugBank / FDA)
└── ADMET predictions for novel structures
    ↓
Phase 5: Literature Evidence
├── PubMed search: "[drug] AND [disease]"
├── Europe PMC search (includes preprints)
└── ClinicalTrials.gov: existing/completed trials
    ↓
Phase 6: Scoring & Ranking
└── Score on target association, safety, evidence, properties
```

---

## Phase 1: Disease & Target Analysis

Call `OpenTargets_get_dise_id_desc_by_name` with `diseaseName` to retrieve the EFO ID and description for the target disease.

Call `OpenTargets_get_asso_targ_by_dise_efoI` with `efoId` and `limit` (20–50 recommended) to get associated targets ranked by association score. Each target has `gene_symbol`, `ensembl_id`, `uniprot_id`, and `score`.

For each top target (top 10), call `DGIdb_get_gene_druggability` with `gene_name` (HUGO symbol) to check if it is a known druggable class (kinase, GPCR, ion channel, etc.). Skip non-druggable targets before spending API calls on drug searches.

Optionally call `UniProt_get_function_by_accession` for a concise functional summary of each target protein.

---

## Phase 2: Drug Discovery

For each druggable target, search three sources in parallel:

1. Call `drugbank_get_drug_name_and_desc_by_targ_name` with `target_name` (gene symbol).
2. Call `DGIdb_get_drug_gene_interactions` with `gene_name`. Returns interaction types and evidence sources.
3. Call `ChEMBL_search_drugs` with `query` set to the gene symbol, `limit` 10–20.

Also call `OpenTargets_get_asso_drug_by_dise_efoI` with `efoId` to get drugs directly linked to the disease in OpenTargets (clinical evidence).

Deduplicate results by normalized generic drug name. For compound-based repurposing (starting from a known drug), call `drugbank_get_targ_by_drug_name_or_drug_id` to enumerate all targets, then reverse-map each target to diseases using `OpenTargets_get_dise_phen_by_targ_ense` with the `ensemblId`.

For mechanism-based repurposing, call `drugbank_get_drug_desc_pharmacology_by_moa` with `mechanism_of_action` as a keyword phrase to find drugs sharing the same MoA.

For pathway-based repurposing, call `drugbank_get_pathways_reactions_by_drug_or_id` to get affected pathways, then `drugbank_get_drug_name_and_desc_by_path_name` to find other drugs in those pathways.

---

## Phase 3: Drug Detail Enrichment

For each candidate drug (prioritize FDA-approved or clinical-stage), gather:

- **Basic info + approval status**: `drugbank_get_dru_bas_inf_by_dru_nam_or_id` with `drug_name_or_drugbank_id`
- **Current indications**: `drugbank_get_indi_by_drug_name_or_drug_id` with `drug_name_or_drugbank_id`
- **Pharmacology + MoA**: `drugbank_get_phar_by_drug_name_or_drug_id` with `drug_name_or_drugbank_id`
- **All known targets**: `drugbank_get_targ_by_drug_name_or_drug_id` (useful for polypharmacology analysis)

For structure-based repurposing, call `PubChem_get_CID_by_compound_name` first to get the CID, then `PubChem_get_compound_properties_by_CID` for MW, LogP, TPSA, and drug-likeness metrics.

---

## Phase 4: Safety Assessment

For each shortlisted candidate:

1. **Boxed warnings**: Call `FDA_get_boxed_warning_info_by_drug_name` with `drug_name`. A black-box warning does not disqualify but must be disclosed.
2. **Contraindications**: Call `FDA_get_contraindications_by_drug_name`.
3. **Adverse event profile**: Call `FAERS_count_reactions_by_drug_event` with `medicinalproduct` (UPPERCASE). Returns top MedDRA PTs with counts.
4. **Serious events**: Call `FAERS_filter_serious_events` or `FAERS_count_death_related_by_drug`.
5. **Drug interactions**: Call `drugbank_get_drug_inte_by_drug_name_or_id` — important if the new indication has a different co-medication landscape.

For novel structures or compounds not yet approved, call ADMET-AI tools using SMILES:
- `ADMETAI_predict_toxicity` (hERG, DILI, AMES, ClinTox, LD50)
- `ADMETAI_predict_bioavailability` (HIA, Caco2, Pgp)
- `ADMETAI_predict_BBB_penetrance` (for CNS indications)

All ADMET-AI tools accept `smiles` as a **list** of SMILES strings, not a single string.

---

## Phase 5: Literature Evidence

For each top candidate, search:

1. `PubMed_search_articles` with `query` = `"[drug_name] AND [disease_name]"`, `max_results` 50–100.
2. `EuropePMC_search_articles` with `query` = same string, `limit` 50. Captures preprints.
3. `ClinicalTrials_search_by_intervention` with `intervention` = drug name to find all trials. Then scan for the target disease in returned conditions.

Score evidence: clinical trials > RCTs > systematic reviews > preclinical studies > case reports.

---

## Phase 6: Scoring & Ranking

Score each candidate 0–100 across four dimensions:

| Dimension | Max Points | Criteria |
|-----------|-----------|---------|
| Target association | 40 | OpenTargets score × 40; pathway-only evidence = 15 |
| Safety profile | 30 | FDA approved = +20; Phase III = +15; no black-box warning = +10; serious AE signal = −10 |
| Literature evidence | 20 | Clinical trial = 10 pts each (cap 15); RCT = 5; review = 3; paper = 1 (cap 10) |
| Drug properties | 10 | High bioavailability = +5; BBB penetration for CNS = +5 |

Present the ranked list with top 10 candidates. For each, include: current indications, proposed indication, repurposing rationale, evidence summary, key papers, and suggested next steps.

---

## Alternative Strategies

### Adverse-Effect-as-Therapeutic

Search FAERS for drugs with unexpected beneficial adverse effects. Call `FAERS_count_reactions_by_drug_event` and look for AEs that are therapeutic in the target indication context (e.g., weight loss, hair growth, immunosuppression). Historical example: minoxidil (hypertension) → hair loss treatment.

### Polypharmacology

For each candidate, call `drugbank_get_targ_by_drug_name_or_drug_id` and count how many disease targets from Phase 1 the drug hits. A drug hitting 3+ disease targets is a stronger polypharmacology candidate. Use `BindingDB_get_ligands_by_uniprot` to find quantitative binding data (Ki, IC50) for target proteins.

### Structure-Based Analog Search

Call `PubChem_get_CID_by_compound_name` to get CID, then `PubChem_search_compounds_by_similarity` with SMILES and `threshold` (0–100). Cross-reference returned CIDs against DrugBank to identify which analogs are already approved drugs.

---

## Known Gotchas

**Tool name truncation**: Many tool names are shortened in the registry. Do not invent or guess names. Use the exact names in the Tool Reference table below.

**`ADMETAI_predict_admet` does not exist**: Use specific sub-tools: `ADMETAI_predict_toxicity`, `ADMETAI_predict_bioavailability`, `ADMETAI_predict_BBB_penetrance`, etc. All accept `smiles` as a list.

**`FDA_get_warnings_and_cautions_by_drug_name` does not exist**: Use `FDA_get_boxed_warning_info_by_drug_name`, `FDA_get_contraindications_by_drug_name`, or `FDA_get_general_precautions_by_drug_name` separately.

**`ClinicalTrials_search` does not exist**: Use `ClinicalTrials_search_studies` (broad) or `ClinicalTrials_search_by_intervention` (drug-centric).

**`OpenTargets_get_associated_targets_by_disease_efoId` does not exist**: Use `OpenTargets_get_asso_targ_by_dise_efoI`.

**FAERS drug names must be UPPERCASE**: `medicinalproduct="METFORMIN"`, not `"metformin"`. Mixed-case often returns zero results.

**DrugBank `drug_name` parameter is case-insensitive but prefers generic names**: Use `"metformin"` not `"Glucophage"`. If no result, try the DrugBank ID from `drugbank_vocab_search`.

**`UniProt_get_entry_by_accession` returns huge payloads**: Use `UniProt_get_function_by_accession` or `UniProt_get_recommended_name_by_accession` instead.

**OpenTargets EFO IDs**: If `OpenTargets_get_dise_id_desc_by_name` returns no match, try disease synonyms or broader categories. EFO IDs use underscore format: `EFO_0000249`.

**DGIdb gene names**: Use HUGO approved symbol (e.g., `APP`, `BACE1`, `PSEN1`). Full protein names are not accepted.

**ChEMBL `pref_name__contains` filter often returns zero results**: Use `ChEMBL_search_drugs` with `query` instead, or look up the ChEMBL ID first then use `ChEMBL_get_drug`.

**PubChem similarity search returns max 10 CIDs**: `PubChem_search_compounds_by_similarity` is capped at `MaxRecords=10`.

---

## Abbreviated Tool Reference

For full parameter details, see [references/tools.md](references/tools.md).

### Disease & Target

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `OpenTargets_get_dise_id_desc_by_name` | `diseaseName` | Returns EFO ID |
| `OpenTargets_get_asso_targ_by_dise_efoI` | `efoId`, `limit` | Returns targets with association scores |
| `OpenTargets_get_dise_phen_by_targ_ense` | `ensemblId` | Reverse: target → diseases |
| `OpenTargets_get_asso_drug_by_dise_efoI` | `efoId` | Drugs with clinical evidence for disease |
| `DGIdb_get_gene_druggability` | `gene_name` | HUGO symbol; returns druggability tier |

### Drug Discovery

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `drugbank_get_drug_name_and_desc_by_targ_name` | `target_name` | Gene symbol |
| `drugbank_get_drug_name_and_desc_by_indi` | `indication` | Indication keyword |
| `DGIdb_get_drug_gene_interactions` | `gene_name` | Returns interaction types |
| `ChEMBL_search_drugs` | `query`, `limit` | Broad drug search |
| `ChEMBL_get_drug_mechanisms` | `chembl_id` | Mechanism of action |

### Drug Information

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `drugbank_get_dru_bas_inf_by_dru_nam_or_id` | `drug_name_or_drugbank_id` | Approval status, groups |
| `drugbank_get_indi_by_drug_name_or_drug_id` | `drug_name_or_drugbank_id` | Current indications |
| `drugbank_get_phar_by_drug_name_or_drug_id` | `drug_name_or_drugbank_id` | MoA, pharmacodynamics, PK |
| `drugbank_get_targ_by_drug_name_or_drug_id` | `drug_name_or_drugbank_id` | All targets |
| `drugbank_get_drug_inte_by_drug_name_or_id` | `drug_name_or_id` | Drug-drug interactions |
| `drugbank_get_pathways_reactions_by_drug_or_id` | `drug_name_or_drugbank_id` | Affected pathways |
| `drugbank_get_drug_name_and_desc_by_path_name` | `pathway_name` | Drugs in pathway |
| `drugbank_get_drug_desc_pharmacology_by_moa` | `mechanism_of_action` | MoA-based search |

### Safety

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `FDA_get_boxed_warning_info_by_drug_name` | `drug_name` | Black-box warnings |
| `FDA_get_contraindications_by_drug_name` | `drug_name` | Contraindications |
| `FDA_get_adverse_reactions_by_drug_name` | `drug_name` | Labeled AEs |
| `FAERS_count_reactions_by_drug_event` | `medicinalproduct` (UPPERCASE) | All AE counts |
| `FAERS_count_death_related_by_drug` | `medicinalproduct` (UPPERCASE) | Fatal outcomes |
| `FAERS_filter_serious_events` | `medicinalproduct` | Serious/fatal events |
| `FAERS_calculate_disproportionality` | `medicinalproduct`, `reaction` | ROR, PRR, IC |

### ADMET (requires SMILES list)

| Tool | Key Output |
|------|-----------|
| `ADMETAI_predict_toxicity` | hERG, DILI, AMES, ClinTox, LD50 |
| `ADMETAI_predict_bioavailability` | HIA, Caco2, Pgp, PAMPA |
| `ADMETAI_predict_BBB_penetrance` | BBB_Martins probability |
| `ADMETAI_predict_physicochemical_properties` | MW, LogP, TPSA, Lipinski, QED |

### Literature

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `PubMed_search_articles` | `query`, `max_results` | Primary literature |
| `EuropePMC_search_articles` | `query`, `limit` | Includes preprints |
| `ClinicalTrials_search_by_intervention` | `intervention` | All trials for drug |
| `ClinicalTrials_search_studies` | `condition`, `intervention` | Combined filter |

---

## Output Format

Present a ranked candidate report:

```
## Drug Repurposing Analysis: [Disease Name]

### Top Candidates

#### 1. [Drug Name] — Score: [X]/100
- Current indications: [list]
- Proposed indication: [disease/condition]
- Repurposing rationale: targets [gene] with association score [X]
- Approval status: FDA approved / Phase [X]
- Safety flags: [boxed warning yes/no; major AEs]
- Literature: [N papers, N clinical trials]
- Mechanism fit: [brief]
- Next steps: [Phase II feasibility / dosing optimization / etc.]
```

---

## Resources

For comprehensive disease analysis, see [disease-intelligence-gatherer skill](../disease-intelligence-gatherer/SKILL.md).

For compound property analysis, see [chemical-compound-retrieval skill](../chemical-compound-retrieval/SKILL.md).

For detailed parameter tables and data structure patterns, see [references/tools.md](references/tools.md).
