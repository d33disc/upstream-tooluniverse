# Drug Repurposing: Detailed Tool Reference

Full parameter details for tools used in the drug repurposing skill.
For the workflow guide, see [SKILL.md](../SKILL.md).

---

## Disease & Target Tools

### OpenTargets_get_dise_id_desc_by_name
- **Parameter**: `diseaseName` (str) — disease or phenotype name in plain English
- **Returns**: `{"data": {"id": "EFO_0000249", "name": "...", "description": "..."}}`
- **Use**: First step; get the EFO ID required by all other OpenTargets disease tools
- **Gotcha**: If not found, try broader terms or synonyms ("Alzheimer's disease" vs "Alzheimer disease")

### OpenTargets_get_asso_targ_by_dise_efoI
- **Parameters**: `efoId` (str, e.g. `"EFO_0000249"`), `limit` (int, default 10; recommended 20–50)
- **Returns**: List of targets with `gene_symbol`, `ensembl_id`, `uniprot_id`, association `score` (0–1)
- **Use**: Core target discovery; rank by score and focus on top 10–20

### OpenTargets_get_dise_phen_by_targ_ense
- **Parameter**: `ensemblId` (str, e.g. `"ENSG00000142192"`)
- **Returns**: Diseases/phenotypes associated with the target
- **Use**: Compound-based repurposing — for a drug's known target, what diseases does it associate with?

### OpenTargets_get_asso_drug_by_dise_efoI
- **Parameter**: `efoId` (str)
- **Returns**: Drugs with clinical trial or post-market evidence for the disease
- **Use**: Direct drug-disease link with highest clinical confidence

### OpenTargets_target_disease_evidence
- **Parameters**: `efoId` (str), `ensemblId` (str)
- **Returns**: Evidence rows (intogen by default) supporting the target-disease association
- **Use**: Validate strength of a specific target-disease pair before investing in drug search

### DGIdb_get_gene_druggability
- **Parameter**: `gene_name` (str, HUGO symbol)
- **Returns**: Druggability tier and categories (kinase, GPCR, ion channel, etc.)
- **Use**: Screen targets before drug search — skip non-druggable tier 3/4 targets

### DGIdb_get_drug_gene_interactions
- **Parameter**: `gene_name` (str, HUGO symbol)
- **Returns**: Drug-gene pairs with `interaction_type` (inhibitor, activator, etc.) and evidence sources
- **Use**: Comprehensive drug-target interaction coverage; alternative to DrugBank target search

### UniProt_get_function_by_accession
- **Parameter**: `accession` (str, UniProt accession e.g. `"P05067"`)
- **Returns**: Functional annotation text
- **Use**: Understand target biology without triggering the large full-entry response
- **Gotcha**: `UniProt_get_entry_by_accession` returns 40,000+ lines; avoid it — use specific extractors

---

## Drug Discovery Tools

### drugbank_get_drug_name_and_desc_by_targ_name
- **Parameter**: `target_name` (str) — gene symbol or protein name
- **Returns**: List of drug names and descriptions targeting the protein
- **Use**: Primary tool for target-based repurposing drug discovery

### drugbank_get_drug_name_and_desc_by_indi
- **Parameter**: `indication` (str) — indication keyword (e.g. `"hypertension"`)
- **Returns**: Drugs approved for the specified indication
- **Use**: Indication-based repurposing; find drugs for related diseases

### drugbank_get_drug_desc_pharmacology_by_moa
- **Parameter**: `mechanism_of_action` (str) — MoA keyword (e.g. `"receptor antagonist"`)
- **Returns**: Drug names, descriptions, and pharmacology matching the MoA
- **Use**: Mechanism-based repurposing

### drugbank_get_drug_name_and_desc_by_path_name
- **Parameter**: `pathway_name` (str) — pathway name (e.g. `"cholesterol biosynthesis"`)
- **Returns**: Drugs affecting the specified pathway
- **Use**: Network/pathway-based repurposing

### ChEMBL_search_drugs
- **Parameters**: `query` (str), `limit` (int)
- **Returns**: Drug molecules with ChEMBL IDs, pref_name, approval status
- **Use**: Alternative/supplementary drug search; use gene symbol as query for target-centric search
- **Gotcha**: `pref_name__contains` filter returns zero results for many common names; use `query` parameter instead

### ChEMBL_get_drug_mechanisms
- **Parameter**: `chembl_id` (str, e.g. `"CHEMBL941"`) — must be ChEMBL drug ID, not molecule ID
- **Returns**: Mechanism of action with target info
- **Use**: Verify MoA of a candidate drug; find ChEMBL ID first via `ChEMBL_search_drugs`

### ChEMBL_search_similar_molecules
- **Parameters**: `smiles` or `chembl_id` or compound name (str), optionally `similarity` threshold
- **Returns**: Similar molecules by Tanimoto similarity
- **Use**: Structure-based repurposing to find approved analogs of an active compound

---

## Drug Information Tools

### drugbank_get_dru_bas_inf_by_dru_nam_or_id
- **Parameter**: `drug_name_or_drugbank_id` (str)
- **Returns**: Name, description, CAS number, approval status, drug groups (approved/investigational/etc.)
- **Use**: First drug lookup; confirm it is actually approved and not just investigational

### drugbank_get_indi_by_drug_name_or_drug_id
- **Parameter**: `drug_name_or_drugbank_id` (str)
- **Returns**: Approved indications and therapeutic uses
- **Use**: Check current uses; if the new disease is already listed, this is not a novel repurposing

### drugbank_get_phar_by_drug_name_or_drug_id
- **Parameter**: `drug_name_or_drugbank_id` (str)
- **Returns**: Mechanism of action, pharmacodynamics, pharmacokinetics
- **Use**: Understand the drug's biological mechanism for repurposing rationale

### drugbank_get_targ_by_drug_name_or_drug_id
- **Parameter**: `drug_name_or_drugbank_id` (str)
- **Returns**: Targets, enzymes, carriers, and transporters with UniProt accessions
- **Use**: Enumerate all molecular targets — essential for polypharmacology analysis

### drugbank_get_drug_inte_by_drug_name_or_id
- **Parameter**: `drug_name_or_id` (str)
- **Returns**: Drug-drug interactions and contraindications
- **Use**: Assess interaction risk for the new patient population (different co-medications than original indication)

### drugbank_get_pathways_reactions_by_drug_or_id
- **Parameter**: `drug_name_or_drugbank_id` (str)
- **Returns**: Affected metabolic/biological pathways and reactions
- **Use**: Network-based repurposing — find disease-pathway overlap

### drugbank_vocab_search
- **Parameter**: `query` (str) — name, synonym, or ID fragment
- **Returns**: DrugBank IDs, common names, CAS, synonyms
- **Use**: Disambiguation when drug name is ambiguous or results are empty; retrieve DrugBank ID for precise lookups

---

## Safety Assessment Tools

### FDA_get_boxed_warning_info_by_drug_name
- **Parameter**: `drug_name` (str)
- **Returns**: Boxed (black-box) warning text
- **Use**: Critical first safety check; boxed warning does not disqualify but must be documented

### FDA_get_contraindications_by_drug_name
- **Parameter**: `drug_name` (str)
- **Returns**: Contraindication text from FDA label
- **Use**: Identify patient populations that must be excluded from the new indication

### FDA_get_general_precautions_by_drug_name
- **Parameter**: `drug_name` (str)
- **Returns**: General precautions and warnings text
- **Use**: Broader safety context beyond boxed warnings

### FDA_get_adverse_reactions_by_drug_name
- **Parameter**: `drug_name` (str)
- **Returns**: Labeled adverse reactions section from FDA SPL
- **Use**: Official documented AE list; complements real-world FAERS data

### FDA_get_drug_interactions_by_drug_name
- **Parameter**: `drug_name` (str)
- **Returns**: Drug interaction text from FDA label
- **Use**: Formal interaction warnings; also see DrugBank for structured data

### FAERS_count_reactions_by_drug_event
- **Parameter**: `medicinalproduct` (str, UPPERCASE required)
- **Optional**: `reactionmeddraverse` to filter to one specific reaction
- **Returns**: MedDRA Preferred Terms with report counts, ranked by frequency
- **Use**: Real-world adverse event profile; compare with labeled AEs
- **Gotcha**: Use UPPERCASE — `"ASPIRIN"` not `"aspirin"`. Mixed case returns zero results.

### FAERS_count_death_related_by_drug
- **Parameter**: `medicinalproduct` (str, UPPERCASE)
- **Returns**: Fatal adverse event count
- **Use**: Most serious safety metric; high death count is a red flag for new indications

### FAERS_filter_serious_events
- **Parameter**: `medicinalproduct` (str, UPPERCASE)
- **Returns**: Deaths, hospitalizations, life-threatening events only
- **Use**: Prioritize safety assessment for high-severity signals

### FAERS_calculate_disproportionality
- **Parameters**: `medicinalproduct` (str, UPPERCASE), `reaction` (str)
- **Returns**: ROR, PRR, IC with 95% CI and signal classification
- **Use**: Statistical signal detection; PRR > 2 with N > 3 is a conventional signal threshold

### FAERS_search_reports_by_drug_and_reaction
- **Parameters**: `medicinalproduct` (str, UPPERCASE), `reactionmeddrapt` (str)
- **Returns**: Individual case reports for a specific drug+reaction combination
- **Use**: Deep dive into specific adverse event type of concern

---

## ADMET Prediction Tools

All ADMET-AI tools accept `smiles` as a **list of SMILES strings** (not a single string).

| Tool | Key Output Fields |
|------|-------------------|
| `ADMETAI_predict_physicochemical_properties` | MW, logP, HBD, HBA, Lipinski, QED, TPSA |
| `ADMETAI_predict_toxicity` | AMES, hERG, DILI, ClinTox, LD50_Zhu, Carcinogens |
| `ADMETAI_predict_bioavailability` | Bioavailability_Ma, HIA_Hou, PAMPA_NCATS, Caco2_Wang, Pgp_Broccatelli |
| `ADMETAI_predict_BBB_penetrance` | BBB_Martins (0–1 probability) |
| `ADMETAI_predict_CYP_interactions` | CYP1A2, CYP2C9, CYP2C19, CYP2D6, CYP3A4 (inhibitor/substrate) |
| `ADMETAI_predict_clearance_distribution` | Half_Life_Obach, VDss_Lombardo, PPBR_AZ |
| `ADMETAI_pred_solu_lipo_hydr` | Solubility_AqSolDB, Lipophilicity_AstraZeneca |

---

## Literature & Clinical Trial Tools

### PubMed_search_articles
- **Parameters**: `query` (str), `max_results` (int, 50–100 for repurposing)
- **Returns**: PMIDs, titles, authors, journal, year, DOI, article type
- **Use**: Primary literature evidence; use Boolean queries: `"metformin AND Alzheimer's disease"`

### EuropePMC_search_articles
- **Parameters**: `query` (str), `limit` (int)
- **Returns**: Article metadata including preprints
- **Use**: Broader coverage than PubMed; captures BioRxiv/MedRxiv preprints
- **Gotcha**: `BODY:` field search only works for records where full text is indexed (`HAS_FT:Y`)

### ClinicalTrials_search_by_intervention
- **Parameter**: `intervention` (str) — drug name
- **Returns**: All trials testing the drug, with conditions, phases, and status
- **Use**: Find all disease contexts the drug has been tested in; identifies completed trials

### ClinicalTrials_search_studies
- **Parameters**: `condition` (str), `intervention` (str), optional `pageSize`, `study_type`
- **Returns**: NCT IDs, phases, status, enrollment, metadata
- **Use**: Combined disease+drug search; filter by phase and status for most relevant results

---

## Chemical Structure Tools

### PubChem_get_CID_by_compound_name
- **Parameter**: `compound_name` (str) — drug or compound name (not disease names)
- **Returns**: PubChem Compound ID (CID)
- **Use**: First step for any PubChem workflow; required for similarity and property queries

### PubChem_get_compound_properties_by_CID
- **Parameter**: `cid` (str or int)
- **Returns**: MW, molecular formula, canonical SMILES, XLogP, TPSA, HBD, HBA, rotatable bonds
- **Use**: Drug-likeness assessment (Lipinski Ro5, ADME estimation)

### PubChem_search_compounds_by_similarity
- **Parameters**: `smiles` (str), `threshold` (int 0–100)
- **Returns**: Up to 10 similar CIDs (hard cap at MaxRecords=10)
- **Use**: Structure-based repurposing; find approved drugs structurally similar to an active compound
- **Gotcha**: Returns at most 10 results regardless of threshold setting

### BindingDB_get_ligands_by_uniprot
- **Parameter**: `uniprot_id` (str)
- **Returns**: SMILES, Ki, IC50, Kd values for all tested ligands
- **Use**: Quantitative binding data for target proteins; find high-affinity ligands for repurposing targets

---

## Query Parameter Guidelines

### Drug Name Conventions

| Database | Convention | Example |
|----------|-----------|---------|
| DrugBank | Generic, case-insensitive | `"metformin"` |
| FAERS | UPPERCASE | `"METFORMIN"` |
| FDA label | Generic preferred | `"metformin"` |
| ChEMBL | Generic, lowercase preferred | `"metformin"` |
| PubMed | Any form | `"metformin OR Glucophage"` |

### Gene/Target Name Conventions
- Use HUGO approved symbol: `"APP"`, `"BACE1"`, `"PSEN1"`
- For UniProt: use accession number (e.g. `"P05067"`) not gene name
- For OpenTargets: use Ensembl ID (e.g. `"ENSG00000142192"`) for target-level queries

### Disease Name Conventions
- OpenTargets: plain English full name — `"Alzheimer's disease"` not `"AD"`
- If name not found: try synonyms, broader categories, or check `OpenTargets_get_disease_synonyms_by_efoId`

---

## Response Data Patterns

### OpenTargets Target Object
```json
{
  "gene_symbol": "APP",
  "ensembl_id": "ENSG00000142192",
  "uniprot_id": "P05067",
  "score": 0.95,
  "data_sources": ["genetics_portal", "europepmc"]
}
```

### DrugBank Drug Object (basic info)
```json
{
  "drugbank_id": "DB00945",
  "name": "Aspirin",
  "description": "...",
  "groups": ["approved", "vet_approved"],
  "indication": "...",
  "mechanism_of_action": "..."
}
```

### FAERS Reaction Count Result
```json
{
  "results": [
    {"term": "NAUSEA", "count": 12345},
    {"term": "HEADACHE", "count": 8901}
  ],
  "meta": {"total": 50000, "disclaimer": "..."}
}
```

---

## Additional Resources

- ToolUniverse Documentation: https://zitniklab.hms.harvard.edu/ToolUniverse/
- DrugBank: https://go.drugbank.com/
- OpenTargets: https://platform.opentargets.org/
- ChEMBL: https://www.ebi.ac.uk/chembl/
- OpenFDA (FAERS): https://open.fda.gov/drug/event/
- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- ClinicalTrials.gov: https://clinicaltrials.gov/
