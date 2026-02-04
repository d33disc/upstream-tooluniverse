# Disease Information Retrieval Examples

Concrete examples for different disease types and use cases.

---

## Example 1: Neurological Disease (Alzheimer's Disease)

### Full Disease Profile

```python
from tooluniverse import ToolUniverse
from concurrent.futures import ThreadPoolExecutor

tu = ToolUniverse()
tu.load_tools()

# Step 1: Get disease identifier
disease = tu.tools.OSL_get_efo_id_by_disease_name(disease="Alzheimer disease")
efo_id = disease.get('efo_id')  # EFO_0000249

# Step 2: Parallel data collection
with ThreadPoolExecutor(max_workers=6) as executor:
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
        'gwas': executor.submit(
            tu.tools.gwas_get_associations_for_trait,
            disease_trait="Alzheimer disease", size=20
        ),
        'variants': executor.submit(
            tu.tools.clinvar_search_variants,
            condition="Alzheimer", max_results=30
        ),
        'similar': executor.submit(
            tu.tools.OpenTargets_get_similar_entities_by_disease_efoId,
            efoId=efo_id, threshold=0.5, size=10
        ),
    }
    results = {k: f.result() for k, f in futures.items()}

# Step 3: Get MedlinePlus consumer information
medline = tu.tools.MedlinePlus_get_genetics_condition_by_name(condition="alzheimer-disease")

# Step 4: Get clinical trials
trials = tu.tools.search_clinical_trials(
    condition="Alzheimer disease",
    query_term="Phase III",
    pageSize=10
)

# Step 5: Literature search
pmids = tu.tools.PubMed_search_articles(
    query='"Alzheimer disease" AND (biomarker OR treatment)',
    limit=20
)
```

### Key Gene Analysis (APP Gene)

```python
# Get diseases associated with APP gene
app_diseases = tu.tools.OpenTargets_get_diseases_phenotypes_by_target_ensembl(
    ensemblId="ENSG00000142192"  # APP
)

# Get pathways for APP protein
app_pathways = tu.tools.Reactome_map_uniprot_to_pathways(id="P05067")  # APP UniProt

# Brain-specific PPI analysis
ppi = tu.tools.humanbase_ppi_analysis(
    gene_list=["APP", "PSEN1", "PSEN2", "APOE"],
    tissue="brain",
    max_node=15,
    interaction="co-expression",
    string_mode=True
)
```

---

## Example 2: Cancer (Breast Cancer)

### Comprehensive Cancer Profile

```python
# Get disease ID
bc = tu.tools.OSL_get_efo_id_by_disease_name(disease="breast carcinoma")
efo_id = bc.get('efo_id')  # EFO_0000305

# Disease-gene associations
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId=efo_id)

# Get BRCA1/2 variants
brca1_variants = tu.tools.clinvar_search_variants(gene="BRCA1", max_results=50)
brca2_variants = tu.tools.clinvar_search_variants(gene="BRCA2", max_results=50)

# CIViC cancer-specific data
civic_genes = tu.tools.civic_search_genes(query="BRCA", limit=10)
# If gene_id found (e.g., BRCA1 = gene_id 5)
brca_variants = tu.tools.civic_get_variants_by_gene(gene_id=5, limit=50)

# Treatment landscape
drugs = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId=efo_id, size=100)

# Clinical trials for specific drug
trials = tu.tools.search_clinical_trials(
    condition="breast cancer",
    intervention="trastuzumab",
    query_term="Phase III",
    pageSize=15
)
```

### GWAS Analysis

```python
# GWAS associations
gwas_assoc = tu.tools.gwas_get_associations_for_trait(
    disease_trait="breast cancer",
    size=50
)

# GWAS studies
gwas_studies = tu.tools.gwas_get_studies_for_trait(
    disease_trait="breast cancer",
    size=20
)

# Variants
variants = tu.tools.gwas_get_variants_for_trait(
    disease_trait="breast cancer",
    size=100
)
```

---

## Example 3: Metabolic Disease (Type 2 Diabetes)

### Full Profile

```python
# Get disease ID
diabetes = tu.tools.OSL_get_efo_id_by_disease_name(disease="type 2 diabetes mellitus")
efo_id = diabetes.get('efo_id')  # EFO_0001360

# Get additional identifiers
icd_codes = tu.tools.icd_search_codes(query="type 2 diabetes", version="ICD10CM")
# Returns codes like E11.9

# Disease subtypes
subtypes = tu.tools.ols_get_efo_term_children(obo_id="EFO:0001360", size=20)

# Phenotypes
phenotypes = tu.tools.OpenTargets_get_associated_phenotypes_by_disease_efoId(efoId=efo_id)

# GWAS
gwas = tu.tools.gwas_get_associations_for_trait(
    disease_trait="type 2 diabetes",
    size=50
)

# Drugs
drugs = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId=efo_id, size=100)

# MedlinePlus info via ICD code
medline = tu.tools.MedlinePlus_connect_lookup_by_code(
    cs="2.16.840.1.113883.6.90",  # ICD-10 CM
    c="E11.9"
)
```

### Drug Mechanism Analysis (Metformin)

```python
# Get ChEMBL ID
metformin = tu.tools.OpenTargets_get_drug_chembId_by_generic_name(drugName="metformin")
chembl_id = metformin.get('data', {}).get('search', {}).get('hits', [{}])[0].get('id')

# Mechanism of action
moa = tu.tools.OpenTargets_get_drug_mechanisms_of_action_by_chemblId(chemblId=chembl_id)

# Warnings
warnings = tu.tools.OpenTargets_get_drug_warnings_by_chemblId(chemblId=chembl_id)
```

---

## Example 4: Rare Disease (Huntington Disease)

### Genetic Analysis Focus

```python
# Get disease ID
hd = tu.tools.OSL_get_efo_id_by_disease_name(disease="Huntington disease")
efo_id = hd.get('efo_id')

# Genetic information from MedlinePlus
genetics = tu.tools.MedlinePlus_get_genetics_condition_by_name(condition="huntington-disease")

# Gene information
gene_info = tu.tools.MedlinePlus_get_genetics_gene_by_name(gene="HTT")

# ClinVar variants
variants = tu.tools.clinvar_search_variants(gene="HTT", max_results=50)

# OpenTargets targets
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId=efo_id)

# Pathway analysis for HTT protein
htt_pathways = tu.tools.Reactome_map_uniprot_to_pathways(id="P42858")  # HTT
```

---

## Example 5: Infectious Disease (COVID-19)

### Research-Focused Profile

```python
# Literature search (primary source)
covid_papers = tu.tools.PubMed_search_articles(
    query='"COVID-19" AND (treatment OR vaccine)',
    limit=50
)

# Get article details for top hit
if covid_papers:
    article = tu.tools.PubMed_get_article(pmid=covid_papers[0])

# Clinical trials
trials = tu.tools.search_clinical_trials(
    condition="COVID-19",
    intervention="remdesivir",
    query_term="Phase III completed",
    pageSize=20
)

# Get trial outcomes
if trials.get('studies'):
    nct_ids = [s['NCT ID'] for s in trials['studies'][:3]]
    outcomes = tu.tools.extract_clinical_trial_outcomes(
        nct_ids=nct_ids,
        outcome_measure="primary"
    )
```

---

## Example 6: Symptom-Based Disease Finding (Differential Diagnosis)

### From Symptoms to Candidate Diseases

```python
# Patient has: seizures + developmental delay + hypotonia
symptoms = ["seizure", "developmental delay", "hypotonia"]

# Get HPO IDs for each symptom
hpo_ids = []
for symptom in symptoms:
    result = tu.tools.get_HPO_ID_by_phenotype(query=symptom, limit=1)
    # Parse to get HPO ID (e.g., HP:0001250 for seizure)
    # hpo_ids.append(hpo_id)

# Find diseases matching this phenotype combination
# Assuming HPO IDs: HP:0001250, HP:0001263, HP:0001252
candidate_diseases = tu.tools.get_joint_associated_diseases_by_HPO_ID_list(
    HPO_ID_list=["HP:0001250", "HP:0001263", "HP:0001252"],
    limit=20
)

# For each candidate, get more details
for disease_name in candidate_diseases[:3]:
    disease_info = tu.tools.OSL_get_efo_id_by_disease_name(disease=disease_name)
```

---

## Example 7: Drug-Centric Disease Discovery

### Find All Indications for a Drug

```python
# Get ChEMBL ID for drug
aspirin = tu.tools.OpenTargets_get_drug_chembId_by_generic_name(drugName="aspirin")
chembl_id = "CHEMBL25"  # Aspirin

# Get mechanism of action (includes targets)
moa = tu.tools.OpenTargets_get_drug_mechanisms_of_action_by_chemblId(chemblId=chembl_id)

# For each target, get associated diseases
targets = moa.get('data', {}).get('drug', {}).get('mechanismsOfAction', {}).get('rows', [])
for target_info in targets[:3]:
    target_id = target_info.get('targets', [{}])[0].get('id')
    if target_id:
        diseases = tu.tools.OpenTargets_get_diseases_phenotypes_by_target_ensembl(
            ensemblId=target_id
        )

# Drug warnings
warnings = tu.tools.OpenTargets_get_drug_warnings_by_chemblId(chemblId=chembl_id)
status = tu.tools.OpenTargets_get_drug_blackbox_status_by_chembl_ID(chemblId=chembl_id)
```

---

## Example 8: Variant-to-Disease Analysis

### Start from SNP

```python
# Known risk SNP
rs_id = "rs429358"  # APOE e4 allele

# Get SNP details
snp = tu.tools.gwas_get_snp_by_id(rs_id=rs_id)

# Get all disease associations
associations = tu.tools.gwas_get_associations_for_snp(
    rs_id=rs_id,
    size=50
)

# Literature for this variant
papers = tu.tools.PubMed_search_articles(
    query=f'"{rs_id}" AND disease',
    limit=20
)
```

---

## Example 9: Pharmacology-Focused Analysis (GtoPdb)

### Find Druggable Targets for Disease

```python
# Search disease in GtoPdb
diseases = tu.tools.GtoPdb_list_diseases(name="hypertension", limit=10)

# Get first disease details
if diseases:
    disease_id = diseases[0].get('diseaseId')
    disease_details = tu.tools.GtoPdb_get_disease(disease_id=disease_id)

# Find GPCR targets
gpcr_targets = tu.tools.GtoPdb_get_targets(target_type="GPCR", limit=50)

# Get interactions for specific target
# Example: Angiotensin II receptor (target_id may vary)
interactions = tu.tools.GtoPdb_get_target_interactions(
    target_id=34,  # AT1 receptor
    action_type="Antagonist"
)

# Search approved drug interactions
approved_interactions = tu.tools.GtoPdb_search_interactions(
    approved_only=True,
    action_type="Antagonist",
    limit=50
)
```

---

## Example 10: Pathway-Centric Disease Analysis

### Disease Pathways and Mechanisms

```python
# Get all disease pathways from Reactome
disease_pathways = tu.tools.Reactome_get_diseases()

# Get disease-associated genes
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId="EFO_0000384")
top_genes = targets.get('data', {}).get('disease', {}).get('associatedTargets', {}).get('rows', [])[:5]

# For each gene, get pathways
for gene in top_genes:
    ensembl_id = gene.get('target', {}).get('id')
    symbol = gene.get('target', {}).get('approvedSymbol')
    
    # Need to map to UniProt first (example: TP53 = P04637)
    # Then get pathways
    pathways = tu.tools.Reactome_map_uniprot_to_pathways(id="P04637")
    
    # Get pathway details
    for pathway in pathways[:3]:
        st_id = pathway.get('stId')
        pathway_detail = tu.tools.Reactome_get_pathway(stId=st_id)

# Tissue-specific analysis
ppi_result = tu.tools.humanbase_ppi_analysis(
    gene_list=["TP53", "BRCA1", "ATM", "CHEK2"],
    tissue="breast",
    max_node=20,
    interaction="co-expression",
    string_mode=True
)
```

---

## Example 11: Complete Multi-Step Chain

### Symptom → Disease → Gene → Pathway → Drug

```python
# START: Patient presents with memory loss
symptom = "memory loss"

# Step 1: Get HPO ID
hpo_result = tu.tools.get_HPO_ID_by_phenotype(query=symptom, limit=3)
# Get HPO:0002354

# Step 2: Find candidate diseases
diseases = tu.tools.get_joint_associated_diseases_by_HPO_ID_list(
    HPO_ID_list=["HP:0002354"],
    limit=20
)
# One candidate: Alzheimer disease

# Step 3: Get EFO ID
efo = tu.tools.OSL_get_efo_id_by_disease_name(disease="Alzheimer disease")
efo_id = efo.get('efo_id')  # EFO_0000249

# Step 4: Get associated genes
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId=efo_id)
top_gene = targets.get('data', {}).get('disease', {}).get('associatedTargets', {}).get('rows', [{}])[0]
# Top gene: APP

# Step 5: Get pathways for gene
# APP UniProt = P05067
pathways = tu.tools.Reactome_map_uniprot_to_pathways(id="P05067")

# Step 6: Get drugs for disease
drugs = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId=efo_id, size=20)

# Step 7: Get clinical trials
trials = tu.tools.search_clinical_trials(
    condition="Alzheimer disease",
    query_term="Phase III recruiting",
    pageSize=10
)

# END: Complete disease intelligence profile
```

---

## Example 12: Handling Path Failures (Graceful Degradation)

### Rare Disease with Limited Data

When some paths fail or return empty results, handle gracefully:

```python
def gather_with_error_handling(disease_id, disease_name):
    tu = ToolUniverse()
    tu.load_tools()
    
    results = {}
    
    # Path 1: Biological - may fail for rare diseases
    try:
        targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId=disease_id)
        results['biological'] = {
            'status': 'success',
            'key_genes': targets.get('data', [])[:10]
        }
    except Exception as e:
        results['biological'] = {'status': 'failed', 'error': str(e)}
    
    # Path 2: Clinical - phenotypes may be sparse
    try:
        phenotypes = tu.tools.OpenTargets_get_associated_phenotypes_by_disease_efoId(efoId=disease_id)
        results['clinical'] = {
            'status': 'success',
            'phenotypes': phenotypes.get('data', [])[:10]
        }
    except Exception as e:
        results['clinical'] = {'status': 'failed', 'error': str(e)}
    
    # Path 3: Treatment - no drugs for ultra-rare diseases
    try:
        drugs = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId=disease_id, size=20)
        results['treatment'] = {
            'status': 'success' if drugs.get('data') else 'empty',
            'drugs': drugs.get('data', [])
        }
    except Exception as e:
        results['treatment'] = {'status': 'failed', 'error': str(e)}
    
    return results

# Example output for rare disease with partial data:
"""
# Disease Intelligence Report: Rare Disease X

## Executive Summary
⚠️ Limited data available - 3/5 research paths completed
• 2 candidate genes identified
• No approved drugs (orphan disease)
• 5 case reports in literature

## Findings by Path

### Biological Understanding ✓
- Key genes: GENE1 (0.75), GENE2 (0.68)
- Pathways: Partially characterized

### Clinical Manifestations ✓
- Phenotypes: From case reports (n=5)
- Variants: 3 pathogenic in ClinVar

### Epidemiology ⚠️ PARTIAL
- GWAS studies: None found
- Prevalence: Unknown (ultra-rare)

### Treatment Landscape ✗ FAILED
- Approved drugs: None
- Clinical trials: Query timeout
- Note: Explore repurposing opportunities

### Research Activity ✓
- Publications: 12 (5 years)
- Trend: Emerging

## Data Gaps Identified
- No large-scale genetic studies
- No clinical trials
- Prevalence data needed

## Metadata
- Paths successful: 3/5 (60%)
- Data Quality: ⭐⭐⭐ (Limited but accurate)
"""
```

---

## Example 13: Multi-Disease Comparison

### Comparing Neurodegenerative Diseases

```python
from concurrent.futures import ThreadPoolExecutor

diseases = {
    "Alzheimer's": "EFO_0000249",
    "Parkinson's": "EFO_0002508",
    "ALS": "EFO_0000253"
}

def get_disease_summary(tu, name, efo_id):
    """Get key metrics for one disease"""
    summary = {'name': name, 'efo_id': efo_id}
    
    # Gene count
    targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId=efo_id)
    summary['gene_count'] = len(targets.get('data', []))
    
    # Drug count
    drugs = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId=efo_id, size=100)
    summary['drug_count'] = len(drugs.get('data', []))
    
    # Trial count
    trials = tu.tools.search_clinical_trials(condition=name, pageSize=100)
    summary['active_trials'] = len([t for t in trials.get('studies', []) 
                                    if t.get('status') in ['Recruiting', 'Active']])
    
    # Publication count
    pubs = tu.tools.PubMed_search_articles(query=f'"{name}"', limit=1000)
    summary['publications_5yr'] = pubs.get('count', 0)
    
    return summary

tu = ToolUniverse()
tu.load_tools()

# Parallel comparison
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {
        name: executor.submit(get_disease_summary, tu, name, efo_id)
        for name, efo_id in diseases.items()
    }
    comparisons = {name: f.result() for name, f in futures.items()}

# Format comparison table:
"""
# Neurodegenerative Disease Comparison

| Aspect | Alzheimer's | Parkinson's | ALS |
|--------|-------------|-------------|-----|
| Key genes | APOE, APP, PSEN1/2 | SNCA, LRRK2, PARK7 | SOD1, C9orf72, FUS |
| Gene associations | 245 | 180 | 95 |
| Approved drugs | 2 | 8+ | 3 |
| Active trials | 120 | 95 | 45 |
| Prevalence (US) | 6.5M | 1M | 30K |
| Papers (5yr) | 15,000 | 8,000 | 3,500 |

## Biological Commonalities
- Protein aggregation
- Neuroinflammation
- Mitochondrial dysfunction

## Treatment Landscape Comparison
| Disease | Drug Classes | Key Mechanisms |
|---------|--------------|----------------|
| Alzheimer's | Anti-amyloid, cholinesterase inhibitors | Amyloid clearance |
| Parkinson's | Dopamine agonists, MAO-B inhibitors | Dopamine replacement |
| ALS | Glutamate modulators, antioxidants | Neuroprotection |

## Research Investment
- Alzheimer's: Highest funding, most trials
- Parkinson's: Strong drug pipeline
- ALS: Orphan disease incentives, growing interest
"""
```

---

## Example 14: Follow-Up Drill-Down

### Initial Query → Detailed Follow-Up

**Initial Request**: "Tell me about Type 2 Diabetes"

```python
# Initial summary collection
tu = ToolUniverse()
tu.load_tools()

efo_id = "EFO_0001360"
summary = {
    'targets': tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId=efo_id),
    'drugs': tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId=efo_id, size=50),
    'trials': tu.tools.search_clinical_trials(condition="type 2 diabetes", pageSize=20),
    'gwas': tu.tools.gwas_get_associations_for_trait(disease_trait="type 2 diabetes", size=20),
}
# Present executive summary...
```

**Follow-Up Request**: "Tell me more about the treatment landscape"

```python
# Detailed treatment analysis
treatment_details = {}

# Get all drugs
drugs = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId=efo_id, size=200)

# Categorize by mechanism
drug_classes = {
    'GLP-1 Agonists': [],
    'SGLT2 Inhibitors': [],
    'DPP-4 Inhibitors': [],
    'Insulin': [],
    'Metformin': [],
    'Other': []
}

for drug in drugs.get('data', []):
    drug_name = drug.get('name', '').lower()
    if 'semaglutide' in drug_name or 'liraglutide' in drug_name or 'dulaglutide' in drug_name:
        drug_classes['GLP-1 Agonists'].append(drug)
    elif 'gliflozin' in drug_name or 'empagliflozin' in drug_name or 'dapagliflozin' in drug_name:
        drug_classes['SGLT2 Inhibitors'].append(drug)
    # ... categorize others

# Get detailed info for key drugs
key_drugs = ['semaglutide', 'empagliflozin', 'metformin']
for drug_name in key_drugs:
    chembl = tu.tools.OpenTargets_get_drug_chembId_by_generic_name(drugName=drug_name)
    chembl_id = chembl.get('data', {}).get('search', {}).get('hits', [{}])[0].get('id')
    
    if chembl_id:
        moa = tu.tools.OpenTargets_get_drug_mechanisms_of_action_by_chemblId(chemblId=chembl_id)
        warnings = tu.tools.OpenTargets_get_drug_warnings_by_chemblId(chemblId=chembl_id)
        treatment_details[drug_name] = {'moa': moa, 'warnings': warnings}

# Clinical trials by phase
trials_phase3 = tu.tools.search_clinical_trials(
    condition="type 2 diabetes",
    query_term="Phase 3",
    pageSize=50
)
trials_phase2 = tu.tools.search_clinical_trials(
    condition="type 2 diabetes", 
    query_term="Phase 2",
    pageSize=50
)

# Emerging therapies
trials_novel = tu.tools.search_clinical_trials(
    condition="type 2 diabetes",
    intervention="triple agonist",  # Novel mechanism
    pageSize=20
)

# Format detailed response:
"""
# Type 2 Diabetes - Treatment Landscape (Detailed)

## Approved Drug Classes

### GLP-1 Receptor Agonists
- **Drugs**: Semaglutide (Ozempic/Wegovy), Dulaglutide (Trulicity), Liraglutide (Victoza)
- **Mechanism**: Incretin mimetics, enhance insulin secretion
- **Efficacy**: HbA1c reduction 1.0-1.5%, weight loss 5-10%
- **Cardiovascular benefit**: Proven in outcomes trials
- **Active trials**: 120

### SGLT2 Inhibitors
- **Drugs**: Empagliflozin (Jardiance), Dapagliflozin (Farxiga), Canagliflozin (Invokana)
- **Mechanism**: Block glucose reabsorption in kidney
- **Efficacy**: HbA1c reduction 0.5-1.0%, weight loss
- **Cardiovascular benefit**: Heart failure reduction
- **Active trials**: 95

### DPP-4 Inhibitors
- **Drugs**: Sitagliptin, Linagliptin, Saxagliptin
- **Mechanism**: Enhance endogenous incretin
- **Efficacy**: HbA1c reduction 0.5-0.8%
- **Cardiovascular**: Neutral

### Metformin (First-line)
- **Mechanism**: Reduces hepatic glucose production
- **Efficacy**: HbA1c reduction ~1.5%
- **Safety**: GI side effects, contraindicated in renal impairment

## Clinical Trial Pipeline

| Phase | Count | Focus Areas |
|-------|-------|-------------|
| Phase IV | 180 | Post-marketing studies |
| Phase III | 85 | Novel combinations |
| Phase II | 120 | New mechanisms |
| Phase I | 40 | Early safety |

### Emerging Approaches
- Dual GLP-1/GIP agonists (Tirzepatide - approved 2022)
- Triple agonists (GLP-1/GIP/Glucagon) - Phase II
- Gene therapies - Preclinical

## Treatment Guidelines
1. **First-line**: Metformin + lifestyle
2. **Second-line**: Add GLP-1 RA or SGLT2i (especially if CV risk)
3. **Intensification**: Triple therapy or insulin
"""
```

---

## Output Formatting Template

After collecting data, format as:

```markdown
# Disease Intelligence Report: [Disease Name]

## Executive Summary
- Disease ID: [EFO_XXXXXXX]
- Also known as: [synonyms]
- Key genes: [top 5 genes with scores]
- Approved drugs: [count]
- Active trials: [count]

## Clinical Presentation
### Phenotypes (HPO)
| HPO ID | Phenotype | Description |
|--------|-----------|-------------|
| HP:XXXX | [name] | [description] |

## Genetic Basis
### Top Associated Genes
| Gene | Score | Evidence |
|------|-------|----------|
| [symbol] | [score] | [sources] |

### GWAS Findings
- Total associations: [count]
- Top SNPs: [list]

### ClinVar Variants
- Total variants: [count]
- Pathogenic: [count]

## Treatment Landscape
### Approved Drugs
| Drug | Phase | Mechanism | Target |
|------|-------|-----------|--------|
| [name] | [phase] | [moa] | [target] |

### Active Clinical Trials
| NCT ID | Title | Phase | Status |
|--------|-------|-------|--------|

## Biological Pathways
- Key pathways: [list]
- Tissue expression: [top tissues]

## Research Activity
- Publications (5yr): [count]
- Recent trend: [increasing/stable/declining]

## Related Conditions
| Disease | Similarity Score |
|---------|-----------------|
```
