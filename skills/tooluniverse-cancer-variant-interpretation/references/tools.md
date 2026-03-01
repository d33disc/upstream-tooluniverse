# Cancer Variant Interpretation — Full Tool Reference

Verified tool parameters and response structures for all tools used in this skill. See `SKILL.md` for the abbreviated quick-reference table and workflow instructions.

---

## Gene Resolution Tools

### MyGene_query_genes

**Purpose**: Resolve gene symbol to Ensembl, Entrez, and other IDs.

**Parameters**:
- `query` (string, REQUIRED): Gene symbol, name, or ID (e.g., `EGFR`)
- `species` (string, default=`human`): Species filter
- `fields` (string): Comma-separated fields to return

**Response**:
```
{
  took, total, max_score,
  hits: [{
    _id, _score,
    symbol,
    name,
    ensembl: { gene },   // Ensembl gene ID
    entrezgene,          // Entrez gene ID (string)
  }]
}
```

**Extraction**: Take the first hit where `symbol` exactly matches (case-insensitive). If none, take `hits[0]`.

---

### UniProt_search

**Purpose**: Find protein accession for a gene.

**Parameters**:
- `query` (string, REQUIRED): e.g., `gene:EGFR`
- `organism` (string): e.g., `human`
- `limit` (integer)

**Response**:
```
{
  total_results, returned,
  results: [{
    accession,          // e.g., P00533
    id, protein_name,
    gene_names, organism, length
  }]
}
```

---

### UniProt_get_function_by_accession

**Purpose**: Get protein function description.

**Parameters**:
- `accession` (string, REQUIRED): e.g., `P00533`

**Response**: A **plain list of strings** (NOT a dict). Each string is a function description paragraph.
```
["Receptor tyrosine kinase binding ligands of the EGF family...", ...]
```

**Warning**: Do NOT call `result.get("function")` — this will fail. Treat the result as a list directly.

---

### UniProt_get_disease_variants_by_accession

**Purpose**: Get known disease-associated variants in the same gene.

**Parameters**:
- `accession` (string, REQUIRED): UniProt accession

---

### OpenTargets_get_target_id_description_by_name

**Purpose**: Resolve gene name to Ensembl ID in OpenTargets.

**Parameters**:
- `targetName` (string, REQUIRED): Gene symbol (e.g., `EGFR`)

**Response**:
```
{
  data: {
    search: {
      hits: [{ id, name, description }]  // id = ensemblId
    }
  }
}
```

Match the hit where `name` equals the gene symbol (case-insensitive).

---

### OpenTargets_get_disease_id_description_by_name

**Purpose**: Resolve disease/cancer type to EFO ID for OpenTargets queries.

**Parameters**:
- `diseaseName` (string, REQUIRED): e.g., `lung adenocarcinoma`

**Response**:
```
{
  data: {
    search: {
      hits: [{ id, name, description }]  // id = efoId
    }
  }
}
```

---

### ensembl_lookup_gene

**Purpose**: Get gene details including version number (required for GTEx).

**Parameters**:
- `gene_id` (string, REQUIRED): Ensembl ID or gene symbol
- `species` (string, **REQUIRED** when using Ensembl IDs): `homo_sapiens` — call will error without this

**Response**:
```
{
  status: 'success',
  data: {
    id, version, display_name, species,
    biotype, start, end,
    seq_region_name, strand,
    canonical_transcript, assembly_name
  }
}
```

Use `data.version` to construct the versioned ID for GTEx: `{ensembl_id}.{version}`.

---

## CIViC Clinical Evidence Tools

### civic_search_genes

**Purpose**: List genes in the CIViC database.

**Parameters**:
- `query` (string): Search term — NOTE: does NOT filter server-side; returns genes alphabetically
- `limit` (integer, default=10, max=100): Number to return

**Response**:
```
{
  data: {
    genes: {
      nodes: [{ id, name, description, entrezId }]
    }
  }
}
```

**Critical limitation**: Returns genes alphabetically, no server-side filtering. Genes starting with letters D-Z may not appear in the first 100 results. Match client-side by `entrezId` against the Entrez ID from MyGene.

---

### civic_get_variants_by_gene

**Purpose**: Get all variants for a gene in CIViC.

**Parameters**:
- `gene_id` (integer, REQUIRED): CIViC gene ID — NOT Entrez ID
- `limit` (integer, default=50): Max variants to return

**Response**:
```
{
  data: {
    gene: {
      variants: {
        nodes: [{ id, name }]
      }
    }
  }
}
```

Match target variant by comparing `name` (case-insensitive, strip `p.` prefix). Try exact match first, then partial.

---

### civic_get_variant

**Purpose**: Get variant details.

**Parameters**:
- `variant_id` (integer, REQUIRED): CIViC variant ID

**Response**:
```
{ data: { variant: { id, name } } }
```

---

### civic_get_molecular_profile

**Purpose**: Get molecular profile details.

**Parameters**:
- `molecular_profile_id` (integer, REQUIRED)

**Response**:
```
{ data: { molecularProfile: { id, name } } }
```

---

### civic_search_evidence_items

**Purpose**: List evidence items (predictive, prognostic, diagnostic).

**Parameters**:
- `limit` (integer, default=20)

**Response**:
```
{
  data: {
    evidenceItems: {
      nodes: [{ id, description, evidenceLevel, evidenceType }]
    }
  }
}
```

---

### civic_search_assertions

**Purpose**: List CIViC assertions.

**Parameters**:
- `limit` (integer, default=20)

---

### civic_search_therapies

**Purpose**: List therapies in CIViC.

**Parameters**:
- `limit` (integer, default=20)

---

### Known CIViC Gene IDs (Pre-verified)

| Gene | CIViC Gene ID | Entrez ID |
|------|--------------|-----------|
| ABL1 | 4 | 25 |
| ALK | 1 | 238 |
| BRAF | 5 | 673 |

For genes not listed, call `civic_search_genes(limit=100)` and match `entrezId` client-side. If the gene starts with a letter beyond C, it likely will not appear in the first 100 alphabetical results.

---

## cBioPortal Mutation Prevalence Tools

### cBioPortal_get_mutations

**Purpose**: Get mutation data for genes in a specific study.

**Parameters**:
- `study_id` (string): Cancer study ID (e.g., `luad_tcga`)
- `gene_list` (string): Comma-separated gene symbols (e.g., `EGFR,KRAS`)

**Response**:
```
{
  status: 'success',
  data: [{
    proteinChange, mutationType, sampleId,
    entrezGeneId, studyId, mutationStatus,
    chr, startPosition, endPosition, ...
  }]
}
```

**Warning**: Always extract via `result.get("data", [])`. Do NOT treat the top-level result as a list.

---

### cBioPortal_get_cancer_studies

**Purpose**: List available cancer studies.

**Parameters**:
- `limit` (integer, default=20)

**Response**: Plain array:
```
[{ studyId, name, description, cancerTypeId, ... }]
```

**Key TCGA study IDs**:

| Cancer Type | Study ID |
|-------------|----------|
| Lung adenocarcinoma | luad_tcga |
| Breast cancer | brca_tcga |
| Colorectal cancer | coadread_tcga |
| Melanoma | skcm_tcga |
| Pancreatic cancer | paad_tcga |
| Glioblastoma | gbm_tcga |
| Prostate cancer | prad_tcga |
| Ovarian cancer | ov_tcga |

---

### cBioPortal_get_molecular_profiles

**Purpose**: Get molecular profiles (mutation, CNA, expression) for a study.

**Parameters**:
- `study_id` (string, REQUIRED)

**Response**: Array of `[{ molecularProfileId, molecularAlterationType, ... }]`

---

### cBioPortal_get_gene_info

**Purpose**: Get gene info by Entrez ID.

**Parameters**:
- `entrez_gene_id` (integer, REQUIRED)

---

### cBioPortal_get_samples

**Purpose**: Get samples from a study.

**Parameters**:
- `study_id` (string, REQUIRED)

---

## Drug Information Tools

### OpenTargets_get_associated_drugs_by_target_ensemblID

**Purpose**: Get ALL drugs targeting a gene (approved + clinical trials). Primary drug source.

**Parameters**:
- `ensemblId` (string, REQUIRED): Note camelCase — NOT `ensemblID`
- `size` (integer): Number of drug entries (default 10)

**Response**:
```
{
  data: {
    target: {
      id, approvedSymbol,
      knownDrugs: {
        count,
        rows: [{
          drug: {
            id,           // ChEMBL ID
            name,
            tradeNames,
            maximumClinicalTrialPhase,
            isApproved,
            hasBeenWithdrawn
          },
          phase,
          mechanismOfAction,
          disease: { id, name }
        }]
      }
    }
  }
}
```

Categorize: `drug.isApproved=true` → approved; `phase=3` without approval → Phase 3; `phase=2` → Phase 2.

---

### OpenTargets_get_drug_chembId_by_generic_name

**Purpose**: Resolve drug name to ChEMBL ID.

**Parameters**:
- `drugName` (string, REQUIRED): Note — NOT `genericName`

**Response**:
```
{
  data: {
    search: {
      hits: [{ id, name, description }]  // id = ChEMBL ID
    }
  }
}
```

---

### OpenTargets_get_drug_mechanisms_of_action_by_chemblId

**Purpose**: Drug mechanism of action from OpenTargets.

**Parameters**:
- `chemblId` (string, REQUIRED)

---

### OpenTargets_get_drug_indications_by_chemblId

**Purpose**: Drug indications from OpenTargets.

**Parameters**:
- `chemblId` (string, REQUIRED)

---

### OpenTargets_get_drug_adverse_events_by_chemblId

**Purpose**: Drug adverse events from OpenTargets.

**Parameters**:
- `chemblId` (string, REQUIRED)

---

### OpenTargets_get_associated_drugs_by_disease_efoId

**Purpose**: Get drugs associated with a specific disease/cancer type.

**Parameters**:
- `efoId` (string, REQUIRED)
- `size` (integer, REQUIRED)

---

### OpenTargets_target_disease_evidence

**Purpose**: Evidence for a specific target-disease association.

**Parameters**:
- `ensemblId` (string, REQUIRED): Note camelCase — NOT `ensemblID`
- `efoId` (string, REQUIRED): Both params are required

---

### OpenTargets_get_publications_by_target_ensemblID

**Purpose**: Publications mentioning the target.

**Parameters**:
- `ensemblId` (string, REQUIRED)

---

### FDA_get_indications_by_drug_name

**Purpose**: FDA-approved indications from drug label.

**Parameters**:
- `drug_name` (string)
- `limit` (integer)

**Response**:
```
{
  meta: { skip, limit, total },
  results: [{
    openfda: { brand_name, generic_name },
    indications_and_usage
  }]
}
```

---

### FDA_get_mechanism_of_action_by_drug_name

**Purpose**: Mechanism of action from FDA label.

**Parameters**:
- `drug_name` (string)
- `limit` (integer)

**Response**: `results[].mechanism_of_action`

---

### FDA_get_boxed_warning_info_by_drug_name

**Purpose**: FDA black box warnings.

**Parameters**:
- `drug_name` (string)
- `limit` (integer)

**Response**: `results[].boxed_warning`

---

### FDA_get_clinical_studies_info_by_drug_name

**Purpose**: Clinical study data from FDA label.

**Parameters**:
- `drug_name` (string)
- `limit` (integer)

---

### drugbank_get_drug_basic_info_by_drug_name_or_id

**Purpose**: Drug info from DrugBank. Fall back to this if FDA has no entry.

**Parameters** (ALL REQUIRED):
- `query` (string): Drug name or DrugBank ID
- `case_sensitive` (boolean): Use `false`
- `exact_match` (boolean): Use `false`
- `limit` (integer): e.g., 3

**Warning**: All four parameters are required. Omitting any one will cause a validation error.

**Response**:
```
{
  query, total_matches, total_returned_results,
  results: [{ drug_name, drugbank_id, description, ... }]
}
```

---

### drugbank_get_pharmacology_by_drug_name_or_drugbank_id

**Purpose**: Pharmacology details from DrugBank.

**Parameters** (ALL REQUIRED): `query`, `case_sensitive`, `exact_match`, `limit`

---

### drugbank_get_targets_by_drug_name_or_drugbank_id

**Purpose**: Drug targets from DrugBank.

**Parameters** (ALL REQUIRED): `query`, `case_sensitive`, `exact_match`, `limit`

---

### ChEMBL_get_drug_mechanisms

**Purpose**: Drug mechanisms from ChEMBL.

**Parameters**:
- `drug_chembl_id__exact` (string, REQUIRED): Note — NOT `chembl_id`
- `limit` (integer)
- `offset` (integer)

**Response**: `data.mechanisms[]`

---

### ChEMBL_search_drugs

**Purpose**: Search drugs in ChEMBL.

**Parameters**:
- `pref_name__contains` (string): Drug name fragment
- `max_phase` (integer): Filter by clinical phase
- `limit` (integer)

---

## Clinical Trial Tools

### search_clinical_trials

**Purpose**: Search ClinicalTrials.gov for active trials.

**Parameters**:
- `query_term` (string, REQUIRED): Search query — NOT `disease` or `biomarker`
- `condition` (string): Disease/condition — NOT `disease`
- `intervention` (string): Drug/intervention
- `pageSize` (integer): Max results (default 10, max 1000)

**Response**:
```
{
  studies: [{
    NCT ID,
    brief_title, brief_summary,
    overall_status,
    condition,
    phase
  }],
  nextPageToken,
  total_count
}
```

Prioritize: status `RECRUITING` or `NOT_YET_RECRUITING`, Phase 2 or 3.

---

## Literature & Pathway Tools

### PubMed_search_articles

**Purpose**: Search PubMed literature for evidence.

**Parameters**:
- `query` (string, REQUIRED): PubMed search query
- `limit` (integer, default=10, max=200)
- `include_abstract` (boolean, default=false)

**Response**: A **plain list** of article dicts — NOT wrapped in `{articles: [...]}`:
```
[{
  pmid, title, authors, journal,
  pub_date, pub_year, doi, pmcid,
  article_type, url, abstract, ...
}]
```

**Warning**: Do NOT call `result.get("articles")`. Treat the result as a list directly.

---

### Reactome_map_uniprot_to_pathways

**Purpose**: Map a protein to biological pathways (bypass resistance analysis, context).

**Parameters**:
- `id` (string, REQUIRED): UniProt accession (e.g., `P00533`)

---

### GTEx_get_median_gene_expression

**Purpose**: Tissue expression data from GTEx.

**Parameters**:
- `gencode_id` (string, REQUIRED): Versioned Ensembl ID — e.g., `ENSG00000146648.12`
- `operation` (string): Use `median`

**Warning**: GTEx requires a versioned ID. Call `ensembl_lookup_gene` first (with `species='homo_sapiens'`) to get the version, then construct `{ensembl_id}.{version}`.

---

## Parameter Corrections Quick-Reference

| Tool | Wrong Parameter | Correct Parameter |
|------|----------------|-------------------|
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblID` | `ensemblId` |
| `OpenTargets_get_drug_chembId_by_generic_name` | `genericName` | `drugName` |
| `OpenTargets_target_disease_evidence` | `ensemblID` | `ensemblId` (+ `efoId` both required) |
| `MyGene_query_genes` | `q` | `query` |
| `search_clinical_trials` | `disease`, `biomarker` | `condition`, `query_term` |
| `civic_get_variants_by_gene` | `gene_symbol` | `gene_id` (CIViC numeric ID) |
| `drugbank_*` | any 3 params | ALL 4: `query`, `case_sensitive`, `exact_match`, `limit` |
| `ChEMBL_get_drug_mechanisms` | `chembl_id` | `drug_chembl_id__exact` |
| `ensembl_lookup_gene` | (no species) | `species='homo_sapiens'` required for Ensembl IDs |
