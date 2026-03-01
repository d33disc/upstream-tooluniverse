# Pharmacovigilance Tool Reference

Detailed parameter tables for all tools used in the pharmacovigilance skill. Tools are invoked via `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

For abbreviated reference, see the Tool Reference table in [SKILL.md](../SKILL.md).

---

## Phase 1: Drug Identification

### DailyMed Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `DailyMed_search_spls` | Search SPL drug labels | `drug_name` (str, required) | Returns list with `setid`, `generic_name`, `brand_name` |
| `DailyMed_get_spl_by_set_id` | Retrieve full SPL label | `setid` (str, required) | Returns full label with all safety sections |
| `DailyMed_get_drug_interactions` | Drug interaction section | `setid` (str, required) | Returns drug interaction text from the SPL |

**Common mistake**: Do NOT use `name` — the parameter is `drug_name`.

**Fields available in SPL response**:
- `boxed_warning`
- `contraindications`
- `warnings_and_precautions`
- `adverse_reactions`
- `drug_interactions`
- `use_in_specific_populations`
- `overdosage`
- `clinical_pharmacology`
- `mechanism_of_action`

### ChEMBL Drug Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `ChEMBL_search_drugs` | Search approved drugs | `query` (str, required) | Returns `molecule_chembl_id`, `max_phase`, `pref_name` |
| `ChEMBL_get_molecule` | Get molecule details | `molecule_chembl_id` (str, required) | Molecular properties, SMILES, InChI |
| `ChEMBL_get_drug_mechanisms_of_action` | Drug target and MOA | `molecule_chembl_id` (str, required) | Action type, target name, target ChEMBL ID |

---

## Phase 2: FAERS Adverse Events

### FAERS Query Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `FAERS_count_reactions_by_drug_event` | AE counts for a drug | `drug_name` (str, required), `limit` (int, default 20) | Returns list of `{reaction, count, prr}` |
| `FAERS_get_event_details` | Seriousness breakdown for one event | `drug_name` (str, required), `reaction` (str, required) | Returns `serious_count`, `death_count`, `hospitalization_count` |
| `FAERS_search_by_drug` | Raw report search | `drug_name` (str, required) | Returns individual case reports |
| `FAERS_get_demographics` | Patient demographics for a drug-event pair | `drug_name` (str, required), `reaction` (str, required) | Age, sex distribution of case reporters |

**Critical**: Use `drug_name`, NOT `drug`. The `drug` parameter silently fails or returns incorrect results.

### OpenFDA Tools (FAERS Fallback)

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `OpenFDA_get_drug_events` | AE reports via OpenFDA API | `search` (str, required) | Use OpenFDA query syntax: `"patient.drug.medicinalproduct:METFORMIN"` |
| `OpenFDA_get_drug_recalls` | Drug recall records | `search` (str, required) | Same OpenFDA query syntax |
| `OpenFDA_get_enforcement` | FDA enforcement actions | `search` (str, required) | Returns enforcement action records |

**OpenFDA search syntax examples**:
- By drug name: `"patient.drug.medicinalproduct:METFORMIN"`
- By reaction: `"patient.reaction.reactionmeddrapt:hepatitis"`
- Combined: `"patient.drug.medicinalproduct:WARFARIN+AND+patient.reaction.reactionmeddrapt:bleeding"`

---

## Phase 3: Label Warnings

All label tools use a `setid` obtained from `DailyMed_search_spls`.

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `DailyMed_get_spl_by_set_id` | Full SPL retrieval | `setid` (str, required) | Preferred for complete label extraction |
| `DailyMed_search_spls` | Search if setid unknown | `drug_name` (str, required) | Use to obtain setid first |
| `DailyMed_get_drug_interactions` | Drug interaction section | `setid` (str, required) | Returns structured interaction data |

---

## Phase 4: Pharmacogenomics

### PharmGKB Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `PharmGKB_search_drug` | Search drug annotations | `query` (str, required) | Returns drug list with PharmGKB ID |
| `PharmGKB_get_clinical_annotations` | Clinical PGx data | `drug_id` (str, required) | Gene, variant, phenotype, evidence level |
| `PharmGKB_get_drug_labels` | FDA/EMA PGx labeling | `drug_id` (str, required) | Returns PGx sections of labels |
| `PharmGKB_get_variants` | Relevant genetic variants | `drug_id` (str, required) | Variant IDs and annotations |

**Critical**: Use `query`, NOT `drug` or `name`.

**PharmGKB evidence levels**:
- **1A**: CPIC or DPWG guideline — actionable, implement at prescribing
- **1B**: CPIC or DPWG guideline annotation level only
- **2A**: VIP gene annotation, moderate supporting evidence
- **2B**: VIP gene annotation, weaker evidence
- **3**: Low-level or conflicting evidence — not clinically actionable

### CPIC Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `CPIC_get_guidelines` | CPIC/DPWG guidelines | `drug_name` (str) OR `gene` (str) | Returns guideline ID, genes, dosing recommendations |
| `CPIC_get_recommendations` | Specific dosing guidance | `guideline_id` (str, required) | Phenotype-specific recommendations |

---

## Phase 5: Clinical Trial Safety

### ClinicalTrials.gov Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `search_clinical_trials` | Search trials | `intervention` (str), `phase` (str), `status` (str), `pageSize` (int) | Phase values: "Phase 3", "Phase 4" |
| `get_clinical_trial_by_nct_id` | Retrieve trial details | `nct_id` (str, required) | Full protocol with eligibility, outcomes |
| `get_clinical_trial_results` | Posted results | `nct_id` (str, required) | AE tables, primary outcomes |

**Phase values**: `"Phase 1"`, `"Phase 2"`, `"Phase 3"`, `"Phase 4"`, `"Phase 1/Phase 2"`
**Status values**: `"Completed"`, `"Recruiting"`, `"Active, not recruiting"`, `"Terminated"`

**Note**: Always check `has_results` before calling `get_clinical_trial_results`. Trials without posted results will return empty data.

---

## Phase 5.5: Pathway & Mechanism Context

### KEGG Pathway Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `kegg_search_pathway` | Search pathways | `query` (str, required) | Returns pathway list with IDs |
| `kegg_get_gene_info` | Gene details and pathways | `gene_id` (str, required) | Format: `"hsa:GENE_SYMBOL"` (e.g., `"hsa:ATM"`) |
| `kegg_find_genes` | Find genes by keyword | `query` (str, required), `database` (str, optional) | Database: `"hsa"` for human |

**KEGG gene_id format**: Use KEGG organism code + gene symbol, e.g., `"hsa:PRKAA1"` for human AMPK.

### Reactome Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `Reactome_search_pathway` | Search pathways | `query` (str, required), `species` (str, optional) | Species: `"Homo sapiens"` |
| `Reactome_get_pathway_participants` | Entities in pathway | `pathway_id` (str, required) | Returns proteins, small molecules |

---

## Phase 5.6: Literature Intelligence

### PubMed Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `PubMed_search_articles` | Search peer-reviewed literature | `query` (str, required), `limit` (int, default 20) | Supports PubMed query syntax |
| `PubMed_get_article_details` | Retrieve article metadata | `pmid` (str or int, required) | Returns abstract, authors, journal, MeSH terms |

**Effective PubMed query patterns**:
- Safety focus: `'"metformin" AND (safety OR adverse OR toxicity) AND (systematic[pt] OR meta-analysis[pt])'`
- Specific AE: `'"metformin" AND "lactic acidosis" AND (case report OR cohort)'`
- Recent: `'"metformin" AND (safety OR adverse) AND ("2020"[dp]:"2025"[dp])'`

### Preprint Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `EuropePMC_search_articles` | Search preprints and literature | `query` (str, required), `source` (str, optional), `pageSize` (int, optional) | `source="PPR"` for preprints only |

**Do NOT** call `BioRxiv_search_preprints` or `MedRxiv_search_preprints` — these APIs do not exist. Use `EuropePMC_search_articles` with `source="PPR"` to search preprints from BioRxiv, MedRxiv, and other preprint servers.

**EuropePMC source values**:
- `"PPR"` — preprints only (BioRxiv, MedRxiv, ChemRxiv, etc.)
- `"MED"` — PubMed/MEDLINE
- Omit `source` — search all sources

### Citation Analysis Tools

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `openalex_search_works` | Search with citation counts | `query` (str, required), `limit` (int, optional) | Returns `cited_by_count` for ranking impact |
| `SemanticScholar_search` | AI-ranked literature search | `query` (str, required), `limit` (int, optional) | Good for mechanistic/topic searches |

---

## Utility Tools

### ICD-10 Mapping

| Tool | Purpose | Parameters | Notes |
|------|---------|------------|-------|
| `AdverseEventICDMapper` | Map AE text to ICD-10 codes | `text` (str, required) | Returns `[{adverse_event, icd10cm_code, icd10cm_name}]` |

**Example**: Calling with `text="Patient developed severe hepatotoxicity with jaundice"` returns ICD-10 codes for hepatotoxicity (K71.x range).

---

## Disproportionality Analysis Reference

### PRR Formula

```
PRR = (A / (A+B)) / (C / (C+D))

2x2 contingency table:
               Event Y   All other events
Drug X:           A            B
All other drugs:  C            D

95% Confidence Interval (Rothman formula):
  SE = sqrt(1/A - 1/(A+B) + 1/C - 1/(C+D))
  CI_lower = exp(ln(PRR) - 1.96 * SE)
  CI_upper = exp(ln(PRR) + 1.96 * SE)

Signal criteria: PRR ≥ 2.0 AND CI_lower > 1.0 AND A ≥ 3
```

### ROR Formula

```
ROR = (A/B) / (C/D) = (A*D) / (B*C)

95% CI:
  SE = sqrt(1/A + 1/B + 1/C + 1/D)
  CI_lower = exp(ln(ROR) - 1.96 * SE)
  CI_upper = exp(ln(ROR) + 1.96 * SE)

Signal criteria: CI_lower > 1.0 AND A ≥ 3
Note: ROR ≥ PRR; divergence increases for common events.
```

### Information Component (IC, Bayesian)

```
IC = log2( (A * N) / ((A+B) * (A+C)) )

N = total reports in database
(A+B) = total reports for drug X
(A+C) = total reports for event Y

Lower credible interval (approximate):
  IC025 = IC - 3.3 * sqrt(1/A + 1/N)

Signal criterion: IC025 > 0 (EMA preferred)
Strong signal: IC025 > 1.0
```

### Signal Tier Classification

| Tier | PRR Threshold | Additional Criteria | Action |
|------|---------------|---------------------|--------|
| T1 (Critical) | >10 | Fatal outcomes OR boxed warning | Highlight in executive summary |
| T2 (Moderate) | 3–10 | Serious outcomes | Monitor closely |
| T3 (Mild) | 2–3 | Moderate concern | Clinical management |
| T4 (Expected) | <2 | Known/expected | Document and manage |

### Signal Scoring

```
Signal Score = PRR × Severity_Weight × log10(Case_Count + 1)

Severity Weights:
  Fatal:              10
  Life-threatening:    8
  Hospitalization:     5
  Disability:          5
  Other serious:       3
  Non-serious:         1
```

---

## Fallback Chains

### FAERS Fallback

| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `FAERS_count_reactions_by_drug_event` | `OpenFDA_get_drug_events` (with search string) | PubMed meta-analysis search |
| `FAERS_get_event_details` | OpenFDA with count filter | Manual aggregation from case search |

### Label Fallback

| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `DailyMed_get_spl_by_set_id` | `OpenFDA_get_drug_labels` | FDA website via web search |
| `DailyMed_search_spls` | `ChEMBL_search_drugs` for identifiers | DrugBank lookup |

### PGx Fallback

| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `PharmGKB_search_drug` | `CPIC_get_guidelines` | PubMed PGx literature |
| `PharmGKB_get_clinical_annotations` | FDA Table of PGx Biomarkers (literature) | Label PGx section |

### Pathway Fallback

| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `kegg_search_pathway` | `Reactome_search_pathway` | PubMed mechanism search |
| `kegg_get_gene_info` | `ChEMBL_get_drug_mechanisms_of_action` | Reactome entity lookup |

### Literature Fallback

| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `PubMed_search_articles` | `openalex_search_works` | `SemanticScholar_search` |
| `EuropePMC_search_articles` (source='PPR') | `openalex_search_works` (filter by date) | Skip preprints section |

---

## Rate Limits and Best Practices

| API / Tool | Rate Limit | Best Practice |
|------------|------------|---------------|
| FAERS / OpenFDA | 240 req/min (no key); 120,000 req/day (with key) | Cache results; batch queries; request API key for intensive use |
| DailyMed | No strict limit | Cache SPL content (responses can be large) |
| PharmGKB | No strict limit | Use drug ID for all follow-up calls after initial search |
| ClinicalTrials.gov | ~3 req/sec | Use `pageSize` to minimize round trips |
| PubMed / NCBI | 3 req/sec (no key); 10 req/sec (with API key) | Add API key for intensive literature search |
| KEGG | 10 operations/sec | Avoid parallel bursts; batch gene lookups |

---

## Common Parameter Mistakes

| Tool | Wrong | Correct |
|------|-------|---------|
| `FAERS_count_reactions_by_drug_event` | `drug="metformin"` | `drug_name="metformin"` |
| `DailyMed_search_spls` | `name="aspirin"` | `drug_name="aspirin"` |
| `PharmGKB_search_drug` | `drug="warfarin"` | `query="warfarin"` |
| `OpenFDA_get_drug_events` | `drug_name="metformin"` | `search="patient.drug.medicinalproduct:METFORMIN"` |
| `kegg_get_gene_info` | `gene_id="ATM"` | `gene_id="hsa:ATM"` |
| `EuropePMC_search_articles` (preprints) | `source="BioRxiv"` | `source="PPR"` |
