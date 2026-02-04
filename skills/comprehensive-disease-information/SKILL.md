---
name: comprehensive-disease-information
description: Gather comprehensive disease information using 100+ ToolUniverse tools across 10 research dimensions. Includes direct disease queries and multi-step tool chains for phenotypes, genetics, treatments, pathways, epidemiology, and literature. Use when users ask about diseases, syndromes, medical conditions, or need systematic disease analysis.
---

# Comprehensive Disease Information Retrieval

Systematically gather disease information across 10 research dimensions using direct queries and multi-step tool chains.

## When to Use

Apply when the user:
- Asks about any disease, syndrome, or medical condition
- Needs disease mechanisms, symptoms, or genetics
- Wants treatment options or clinical trial information
- Requires comprehensive disease intelligence
- Asks "what do we know about [disease]?"

## Quick Start: Disease Name to Full Profile

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

# Step 1: Get disease identifier (EFO ID)
disease_id = tu.tools.OSL_get_efo_id_by_disease_name(disease="Parkinson disease")
# Returns: {"efo_id": "EFO_0002508", "name": "Parkinson disease"}

# Step 2: Use EFO ID for detailed queries
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId="EFO_0002508")
phenotypes = tu.tools.OpenTargets_get_associated_phenotypes_by_disease_efoId(efoId="EFO_0002508")
drugs = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId="EFO_0002508", size=50)
```

## 10 Research Dimensions

### DIM 1: Disease Identification & Ontology

**Objective**: Map disease name to standardized IDs and understand disease hierarchy.

**Direct Tools**:
| Tool | Input | Output |
|------|-------|--------|
| `OSL_get_efo_id_by_disease_name` | disease name | EFO ID |
| `ols_search_efo_terms` | query text | EFO term list |
| `ols_get_efo_term` | iri or obo_id | term details, synonyms |
| `ols_get_efo_term_children` | iri or obo_id | disease subtypes |
| `OpenTargets_get_disease_id_description_by_name` | diseaseName | EFO ID, description |
| `umls_search_concepts` | query | UMLS CUI, terms |
| `umls_get_concept_details` | cui | definitions, relations |
| `icd_search_codes` | query, version | ICD-10/11 codes |
| `snomed_search_concepts` | query | SNOMED CT concepts |

**Tool Chain - Disease Hierarchy**:
```
Disease Name
  → OSL_get_efo_id_by_disease_name (get EFO ID)
  → ols_get_efo_term (get synonyms, description)
  → ols_get_efo_term_children (get subtypes)
```

**Example**:
```python
# Get disease ID and hierarchy
efo = tu.tools.OSL_get_efo_id_by_disease_name(disease="type 2 diabetes")
term = tu.tools.ols_get_efo_term(obo_id="EFO:0001360")
children = tu.tools.ols_get_efo_term_children(obo_id="EFO:0001360", size=20)
```

---

### DIM 2: Clinical Manifestations & Phenotypes

**Objective**: Understand symptoms, signs, and clinical presentation.

**Direct Tools**:
| Tool | Input | Output |
|------|-------|--------|
| `OpenTargets_get_associated_phenotypes_by_disease_efoId` | efoId | HPO phenotypes |
| `get_HPO_ID_by_phenotype` | query (symptom name) | HPO ID |
| `get_phenotype_by_HPO_ID` | id | phenotype details |
| `MedlinePlus_search_topics_by_keyword` | term, db | health topics |
| `MedlinePlus_get_genetics_condition_by_name` | condition | genetic condition info |
| `MedlinePlus_connect_lookup_by_code` | cs, c | clinical info by ICD code |

**Multi-Step Chain - Phenotype to Disease**:
```
Symptom/Phenotype
  → get_HPO_ID_by_phenotype (symptom → HPO ID)
  → get_joint_associated_diseases_by_HPO_ID_list (HPO IDs → diseases)
```

**Example**:
```python
# Get phenotypes for disease
phenotypes = tu.tools.OpenTargets_get_associated_phenotypes_by_disease_efoId(efoId="EFO_0000384")

# Reverse: Find diseases from symptoms
hpo = tu.tools.get_HPO_ID_by_phenotype(query="seizure", limit=5)
# Extract HPO ID (e.g., HP:0001250)
diseases = tu.tools.get_joint_associated_diseases_by_HPO_ID_list(
    HPO_ID_list=["HP:0001250"], limit=20
)
```

---

### DIM 3: Genetic & Molecular Basis

**Objective**: Identify genes, variants, and molecular mechanisms.

**Direct Tools**:
| Tool | Input | Output |
|------|-------|--------|
| `OpenTargets_get_associated_targets_by_disease_efoId` | efoId | genes with scores |
| `OpenTargets_target_disease_evidence` | efoId, ensemblId | evidence details |
| `clinvar_search_variants` | condition or gene | variant IDs |
| `clinvar_get_variant_details` | variant_id | variant info |
| `clinvar_get_clinical_significance` | variant_id | pathogenicity |
| `gwas_search_associations` | disease_trait | GWAS hits |
| `gwas_get_variants_for_trait` | disease_trait | associated SNPs |
| `gwas_get_associations_for_trait` | disease_trait | associations ranked by p-value |
| `gwas_get_studies_for_trait` | disease_trait | GWAS studies |
| `GWAS_search_associations_by_gene` | gene_name | gene-trait associations |
| `gnomad_get_variant_frequency` | variant | population frequency data |

**Multi-Step Chain - Gene to Disease**:
```
Gene Symbol
  → OpenTargets_get_diseases_phenotypes_by_target_ensembl (gene → diseases)
  # OR via variants:
  → clinvar_search_variants (gene → variants)
  → clinvar_get_clinical_significance (variant → disease association)
```

**Multi-Step Chain - Variant to Disease**:
```
rs ID (SNP)
  → gwas_get_associations_for_snp (rs ID → disease associations)
  → gwas_get_study_by_id (study details)
```

**Example**:
```python
# Get disease-associated genes
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId="EFO_0000249")

# Get GWAS associations
gwas = tu.tools.gwas_get_associations_for_trait(disease_trait="Alzheimer disease", size=20)

# Reverse: Gene to diseases
gene_diseases = tu.tools.OpenTargets_get_diseases_phenotypes_by_target_ensembl(
    ensemblId="ENSG00000142192"  # APP gene
)

# Variant analysis
variants = tu.tools.clinvar_search_variants(condition="breast cancer", max_results=20)
```

---

### DIM 4: Treatment Landscape

**Objective**: Map approved drugs, clinical trials, and therapeutic pipeline.

**Direct Tools**:
| Tool | Input | Output |
|------|-------|--------|
| `OpenTargets_get_associated_drugs_by_disease_efoId` | efoId, size | drugs with phases |
| `search_clinical_trials` | condition, intervention | trial list |
| `get_clinical_trial_descriptions` | nct_ids | trial descriptions |
| `get_clinical_trial_conditions_and_interventions` | nct_ids | conditions, arms |
| `get_clinical_trial_eligibility_criteria` | nct_ids | eligibility |
| `get_clinical_trial_outcome_measures` | nct_ids | endpoints |
| `extract_clinical_trial_outcomes` | nct_ids | efficacy results |
| `extract_clinical_trial_adverse_events` | nct_ids | safety data |
| `GtoPdb_list_diseases` | name | diseases with targets |
| `GtoPdb_get_disease` | disease_id | targets, drugs |

**Multi-Step Chain - Drug Mechanism**:
```
Drug Name
  → OpenTargets_get_drug_chembId_by_generic_name (name → ChEMBL ID)
  → OpenTargets_get_drug_mechanisms_of_action_by_chemblId (mechanism)
  → OpenTargets_get_drug_warnings_by_chemblId (safety)
```

**Example**:
```python
# Get approved and pipeline drugs
drugs = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(
    efoId="EFO_0000311",  # cancer
    size=100
)

# Search clinical trials
trials = tu.tools.search_clinical_trials(
    condition="non-small cell lung cancer",
    intervention="pembrolizumab",
    query_term="Phase III"
)

# Get trial outcomes (if NCT IDs known)
outcomes = tu.tools.extract_clinical_trial_outcomes(
    nct_ids=["NCT02220894"],
    outcome_measure="overall survival"
)
```

---

### DIM 5: Biological Pathways & Mechanisms

**Objective**: Understand disease mechanisms at pathway level.

**Direct Tools**:
| Tool | Input | Output |
|------|-------|--------|
| `Reactome_get_diseases` | (none) | all disease pathways |
| `Reactome_get_pathway` | stId | pathway details |
| `Reactome_get_pathway_reactions` | stId | reactions |
| `Reactome_map_uniprot_to_pathways` | UniProt ID | protein's pathways |
| `humanbase_ppi_analysis` | gene_list, tissue | tissue-specific PPI |
| `gtex_get_expression_by_gene` | gene | tissue-specific expression |
| `HPA_get_protein_expression` | gene | protein expression atlas |
| `geo_search_datasets` | query | gene expression datasets |

**Multi-Step Chain - Disease Gene to Pathways**:
```
Disease
  → OpenTargets_get_associated_targets_by_disease_efoId (top genes)
  → UniProt_get_entry_by_accession (get UniProt ID)
  → Reactome_map_uniprot_to_pathways (pathways)
```

**Example**:
```python
# Get disease pathways via Reactome
pathways = tu.tools.Reactome_get_diseases()

# Get pathways for disease-associated protein
protein_pathways = tu.tools.Reactome_map_uniprot_to_pathways(id="P04637")  # TP53

# Tissue-specific analysis
ppi = tu.tools.humanbase_ppi_analysis(
    gene_list=["SNCA", "PARK2", "PINK1"],
    tissue="brain",
    max_node=15,
    interaction="co-expression",
    string_mode=True
)
```

---

### DIM 6: Literature & Research Activity

**Objective**: Find publications, assess research momentum.

**Direct Tools**:
| Tool | Input | Output |
|------|-------|--------|
| `PubMed_search_articles` | query | PMIDs |
| `PubMed_get_article` | pmid | article metadata |
| `PubMed_get_related` | pmid | related articles |
| `PubMed_get_cited_by` | pmid | citations |
| `OpenTargets_get_publications_by_disease_efoId` | efoId | disease publications |
| `OpenTargets_get_publications_by_target_ensemblID` | ensemblId | target publications |
| `openalex_search_works` | query | works with institutions, citations |
| `europe_pmc_search_abstracts` | query | Europe PMC abstracts |
| `semantic_scholar_search_papers` | query | papers with citation networks |

**Example**:
```python
# Search literature
pmids = tu.tools.PubMed_search_articles(
    query='"Alzheimer disease" AND (biomarker OR diagnosis)',
    limit=50
)

# Get article details
article = tu.tools.PubMed_get_article(pmid="37654321")

# Find citing articles
citations = tu.tools.PubMed_get_cited_by(pmid="19880848", limit=20)
```

---

### DIM 7: Similar Diseases & Comorbidities

**Objective**: Find related diseases and comorbidities.

**Direct Tools**:
| Tool | Input | Output |
|------|-------|--------|
| `OpenTargets_get_similar_entities_by_disease_efoId` | efoId, threshold, size | similar diseases/targets/drugs |

**Example**:
```python
similar = tu.tools.OpenTargets_get_similar_entities_by_disease_efoId(
    efoId="EFO_0000249",  # Alzheimer
    threshold=0.5,
    size=20
)
```

---

### DIM 8: Cancer-Specific Information (CIViC)

**Objective**: Get curated clinical interpretations for cancer variants.

**Direct Tools**:
| Tool | Input | Output |
|------|-------|--------|
| `civic_search_diseases` | limit | cancer diseases |
| `civic_search_genes` | query, limit | cancer genes |
| `civic_get_variants_by_gene` | gene_id | gene variants |
| `civic_get_evidence_item` | evidence_id | clinical evidence |
| `civic_search_therapies` | limit | cancer therapies |
| `civic_search_molecular_profiles` | limit | biomarker profiles |

**Example**:
```python
# Browse cancer diseases
diseases = tu.tools.civic_search_diseases(limit=50)

# Get variants for cancer gene
genes = tu.tools.civic_search_genes(query="BRAF", limit=10)
variants = tu.tools.civic_get_variants_by_gene(gene_id=5, limit=20)  # BRAF
```

---

### DIM 9: Pharmacological Targets (GtoPdb)

**Objective**: Find druggable targets for disease.

**Direct Tools**:
| Tool | Input | Output |
|------|-------|--------|
| `GtoPdb_list_diseases` | name | disease list |
| `GtoPdb_get_disease` | disease_id | disease details |
| `GtoPdb_get_targets` | target_type | pharmacological targets |
| `GtoPdb_get_target` | target_id | target details |
| `GtoPdb_get_target_interactions` | target_id | ligand interactions |
| `GtoPdb_search_interactions` | various filters | drug-target pairs |

**Example**:
```python
# Find diseases
diseases = tu.tools.GtoPdb_list_diseases(name="diabetes", limit=10)

# Get disease details with targets
disease = tu.tools.GtoPdb_get_disease(disease_id=652)

# Get drug interactions for target
interactions = tu.tools.GtoPdb_get_target_interactions(
    target_id=290,
    action_type="Agonist"
)
```

---

### DIM 10: Adverse Events & Drug Safety

**Objective**: Understand treatment-related adverse events.

**Direct Tools**:
| Tool | Input | Output |
|------|-------|--------|
| `OpenTargets_get_drug_warnings_by_chemblId` | chemblId | drug warnings |
| `OpenTargets_get_drug_blackbox_status_by_chembl_ID` | chemblId | withdrawal/blackbox |
| `extract_clinical_trial_adverse_events` | nct_ids | trial adverse events |
| `AdverseEventPredictionQuestionGenerator` | disease_name, drug_name | safety questions |
| `FAERS_count_reactions_by_drug_event` | drug, event | FDA adverse event counts |

**Example**:
```python
# Get drug warnings
warnings = tu.tools.OpenTargets_get_drug_warnings_by_chemblId(chemblId="CHEMBL25")

# Get adverse events from trials
ae = tu.tools.extract_clinical_trial_adverse_events(
    nct_ids=["NCT01158625"],
    organ_systems=["Cardiac Disorders"],
    adverse_event_type="serious"
)
```

---

## Complete Multi-Step Tool Chains

### Chain A: Symptom-Based Disease Identification
```
Patient Symptoms
  1. get_HPO_ID_by_phenotype (for each symptom)
  2. get_joint_associated_diseases_by_HPO_ID_list (HPO IDs → candidate diseases)
  3. OSL_get_efo_id_by_disease_name (get EFO IDs)
  4. OpenTargets_get_associated_phenotypes_by_disease_efoId (validate)
```

### Chain B: Gene-Centric Disease Discovery
```
Gene of Interest
  1. OpenTargets_get_diseases_phenotypes_by_target_ensembl (diseases)
  2. clinvar_search_variants (gene → pathogenic variants)
  3. gwas_get_snps_for_gene (GWAS hits)
  4. Reactome_map_uniprot_to_pathways (pathways)
```

### Chain C: Drug-to-Disease Mechanism
```
Drug Name
  1. OpenTargets_get_drug_chembId_by_generic_name (get ChEMBL ID)
  2. OpenTargets_get_drug_mechanisms_of_action_by_chemblId (targets)
  3. OpenTargets_get_diseases_phenotypes_by_target_ensembl (diseases per target)
  4. OpenTargets_get_drug_warnings_by_chemblId (safety)
```

### Chain D: Variant-to-Clinical Impact
```
rs ID or Variant
  1. gwas_get_snp_by_id OR clinvar_search_variants (variant info)
  2. gwas_get_associations_for_snp (disease associations)
  3. clinvar_get_clinical_significance (pathogenicity)
  4. PubMed_search_articles (literature)
```

### Chain E: Pathway-Centric Analysis
```
Disease Name
  1. OSL_get_efo_id_by_disease_name (EFO ID)
  2. OpenTargets_get_associated_targets_by_disease_efoId (top genes)
  3. Reactome_map_uniprot_to_pathways (per gene → pathways)
  4. Reactome_get_pathway (pathway details)
  5. humanbase_ppi_analysis (tissue-specific interactions)
```

---

## Parallel Execution Strategy

Execute dimensions in parallel for speed:

```python
from concurrent.futures import ThreadPoolExecutor

def gather_disease_info(disease_name):
    tu = ToolUniverse()
    tu.load_tools()
    
    # Get EFO ID first
    efo = tu.tools.OSL_get_efo_id_by_disease_name(disease=disease_name)
    efo_id = efo.get('efo_id')
    
    if not efo_id:
        return {"error": "Disease not found"}
    
    # Parallel execution
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            'phenotypes': executor.submit(
                tu.tools.OpenTargets_get_associated_phenotypes_by_disease_efoId,
                efoId=efo_id
            ),
            'targets': executor.submit(
                tu.tools.OpenTargets_get_associated_targets_by_disease_efoId,
                efoId=efo_id
            ),
            'drugs': executor.submit(
                tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId,
                efoId=efo_id, size=50
            ),
            'similar': executor.submit(
                tu.tools.OpenTargets_get_similar_entities_by_disease_efoId,
                efoId=efo_id, threshold=0.5, size=10
            ),
            'gwas': executor.submit(
                tu.tools.gwas_search_studies,
                disease_trait=disease_name, size=20
            ),
            'trials': executor.submit(
                tu.tools.search_clinical_trials,
                condition=disease_name, query_term="Phase III", pageSize=10
            ),
            'literature': executor.submit(
                tu.tools.PubMed_search_articles,
                query=f'"{disease_name}"', limit=20
            ),
        }
        
        results = {k: f.result() for k, f in futures.items()}
    
    return {'efo_id': efo_id, 'name': disease_name, **results}
```

---

## Complete Implementation

Full implementation with 5 parallel research paths and synthesis:

```python
from tooluniverse import ToolUniverse
from concurrent.futures import ThreadPoolExecutor

def gather_disease_intelligence(disease_id, disease_name=None):
    """
    Main function: gather comprehensive disease intelligence
    """
    tu = ToolUniverse()
    tu.load_tools()
    
    # Execute 5 paths in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            'biological': executor.submit(path_biological, tu, disease_id),
            'clinical': executor.submit(path_clinical, tu, disease_id),
            'epidemiology': executor.submit(path_epidemiology, tu, disease_name),
            'treatment': executor.submit(path_treatment, tu, disease_id, disease_name),
            'research': executor.submit(path_research, tu, disease_name)
        }
        
        # Collect results with error handling
        findings = {}
        for path_name, future in futures.items():
            try:
                findings[path_name] = future.result(timeout=120)
            except Exception as e:
                findings[path_name] = {'status': 'failed', 'error': str(e)}
    
    # Synthesize findings
    return synthesize_findings(disease_id, findings)


def path_biological(tu, disease_id):
    """PATH 1: Biological Understanding"""
    bio_data = {}
    
    # Get disease-gene associations
    targets = tu.run({
        'name': 'OpenTargets_get_associated_targets_by_disease_efoId',
        'arguments': {'efoId': disease_id}
    })
    
    if targets.get('data'):
        top_targets = targets['data'][:10]
        bio_data['key_genes'] = [
            {
                'gene': t.get('gene_symbol'),
                'score': t.get('score'),
                'ensembl_id': t.get('target_id')
            }
            for t in top_targets
        ]
        
        # Get pathways for top gene
        if top_targets:
            gene_symbol = top_targets[0].get('gene_symbol')
            pathways = tu.run({
                'name': 'Reactome_map_uniprot_to_pathways',
                'arguments': {'id': gene_symbol}
            })
            bio_data['pathways'] = pathways.get('data', [])[:5]
    
    return bio_data


def path_clinical(tu, disease_id):
    """PATH 2: Clinical Manifestations"""
    clinical_data = {}
    
    # Get phenotypes
    phenotypes = tu.run({
        'name': 'OpenTargets_get_associated_phenotypes_by_disease_efoId',
        'arguments': {'efoId': disease_id}
    })
    clinical_data['phenotypes'] = phenotypes.get('data', [])[:10]
    
    # Get variants count
    variants = tu.run({
        'name': 'clinvar_search_variants',
        'arguments': {'condition': disease_id}
    })
    clinical_data['variants'] = len(variants.get('data', []))
    
    return clinical_data


def path_epidemiology(tu, disease_name):
    """PATH 3: Epidemiology"""
    epi_data = {}
    
    # GWAS studies
    gwas = tu.run({
        'name': 'gwas_get_studies_for_trait',
        'arguments': {'disease_trait': disease_name}
    })
    epi_data['gwas_studies'] = len(gwas.get('data', []))
    
    # Epidemiology literature
    lit = tu.run({
        'name': 'PubMed_search_articles',
        'arguments': {'query': f'"{disease_name}" AND epidemiology'}
    })
    epi_data['epidemiology_papers'] = lit.get('count', 0)
    
    return epi_data


def path_treatment(tu, disease_id, disease_name):
    """PATH 4: Treatment Landscape"""
    treatment_data = {}
    
    # Approved drugs
    drugs = tu.run({
        'name': 'OpenTargets_get_associated_drugs_by_disease_efoId',
        'arguments': {'efoId': disease_id, 'size': 50}
    })
    treatment_data['approved_drugs'] = [
        d.get('name') for d in drugs.get('data', [])[:5]
    ]
    
    # Clinical trials
    trials = tu.run({
        'name': 'search_clinical_trials',
        'arguments': {'condition': disease_name}
    })
    treatment_data['total_trials'] = trials.get('total_count', 0)
    treatment_data['active_trials'] = len([
        t for t in trials.get('data', [])
        if t.get('status') in ['Recruiting', 'Active']
    ])
    
    return treatment_data


def path_research(tu, disease_name):
    """PATH 5: Research Activity"""
    research_data = {}
    
    # Recent publications
    recent = tu.run({
        'name': 'PubMed_search_articles',
        'arguments': {'query': f'"{disease_name}"', 'years': 5}
    })
    research_data['recent_publications'] = recent.get('count', 0)
    
    # Current year
    current = tu.run({
        'name': 'PubMed_search_articles',
        'arguments': {'query': f'"{disease_name}"', 'years': 1}
    })
    research_data['current_year'] = current.get('count', 0)
    
    # Calculate trend
    if research_data['recent_publications'] > 0:
        annual_avg = research_data['recent_publications'] / 5
        if research_data['current_year'] > annual_avg * 1.2:
            research_data['trend'] = 'increasing'
        elif research_data['current_year'] < annual_avg * 0.8:
            research_data['trend'] = 'declining'
        else:
            research_data['trend'] = 'stable'
    
    return research_data


def synthesize_findings(disease_id, findings):
    """
    Synthesize all path findings into comprehensive report
    """
    # Generate executive summary
    summary = []
    
    bio = findings.get('biological', {})
    if bio.get('key_genes'):
        summary.append(f"Identified {len(bio['key_genes'])} key genes")
    
    treatment = findings.get('treatment', {})
    if treatment.get('approved_drugs'):
        summary.append(f"{len(treatment['approved_drugs'])} approved drugs")
    if treatment.get('active_trials'):
        summary.append(f"{treatment['active_trials']} active trials")
    
    research = findings.get('research', {})
    if research.get('recent_publications'):
        summary.append(f"{research['recent_publications']} publications (5y)")
    
    # Generate recommendations
    recommendations = []
    
    if bio.get('key_genes') and len(bio['key_genes']) > 5:
        recommendations.append({
            'category': 'Research',
            'priority': 'HIGH',
            'text': 'Multiple genetic targets - consider network-based approach'
        })
    
    if len(treatment.get('approved_drugs', [])) < 3:
        recommendations.append({
            'category': 'Clinical',
            'priority': 'HIGH',
            'text': 'Limited treatments - explore clinical trial opportunities'
        })
    
    # Compile report
    return {
        'disease_id': disease_id,
        'completeness': calculate_completeness(findings),
        'summary': summary,
        'findings': findings,
        'recommendations': recommendations
    }


def calculate_completeness(findings):
    """Calculate what % of paths succeeded"""
    completeness = {}
    for path, data in findings.items():
        if data.get('status') != 'failed':
            completeness[path] = 'COMPLETE'
        else:
            completeness[path] = 'FAILED'
    return completeness
```

### Error Handling Pattern

Always handle path failures gracefully:

```python
# If a path fails, continue with others
try:
    result = path_function(...)
except Exception as e:
    result = {'status': 'failed', 'error': str(e)}
    # Log but don't stop - other paths may succeed

# In synthesis, note which paths failed
if findings['biological'].get('status') == 'failed':
    summary.append("⚠️ Biological data unavailable")
```

---

## Output Template

Present disease information in this structure:

```markdown
# Disease Profile: [Disease Name]

## Identity
- **EFO ID**: [EFO_XXXXXXX]
- **Synonyms**: [list]
- **ICD-10**: [code]
- **UMLS CUI**: [CUI]

## Clinical Presentation
- **Key Phenotypes**: [HPO terms]
- **Symptoms**: [list]

## Genetic Basis
- **Top Associated Genes**: [gene list with scores]
- **GWAS Hits**: [count]
- **Pathogenic Variants**: [count in ClinVar]

## Treatment Landscape
- **Approved Drugs**: [count and top drugs]
- **Clinical Trials**: [active count]
- **Pipeline**: [phase distribution]

## Biological Mechanisms
- **Key Pathways**: [pathway names]
- **Affected Tissues**: [list]

## Research Activity
- **Publications (5yr)**: [count]
- **Trend**: [increasing/stable/declining]

## Similar Diseases
- [disease1, score]
- [disease2, score]
```

---

## Tool Name Quick Reference

**Identification**: `OSL_get_efo_id_by_disease_name`, `ols_search_efo_terms`, `umls_search_concepts`, `icd_search_codes`

**Phenotypes**: `OpenTargets_get_associated_phenotypes_by_disease_efoId`, `get_HPO_ID_by_phenotype`, `MedlinePlus_search_topics_by_keyword`

**Genetics**: `OpenTargets_get_associated_targets_by_disease_efoId`, `clinvar_search_variants`, `gwas_get_associations_for_trait`

**Treatments**: `OpenTargets_get_associated_drugs_by_disease_efoId`, `search_clinical_trials`, `extract_clinical_trial_outcomes`

**Pathways**: `Reactome_get_diseases`, `Reactome_map_uniprot_to_pathways`, `humanbase_ppi_analysis`

**Literature**: `PubMed_search_articles`, `PubMed_get_article`, `OpenTargets_get_publications_by_disease_efoId`

**Cancer**: `civic_search_diseases`, `civic_get_variants_by_gene`, `civic_get_evidence_item`

**Pharmacology**: `GtoPdb_list_diseases`, `GtoPdb_get_disease`, `GtoPdb_get_target_interactions`

For detailed tool reference, see [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md).
