# Comprehensive Disease Information Skill

Systematically gather disease information across 10 research dimensions using 100+ ToolUniverse tools.

## Overview

This skill provides comprehensive coverage of disease information retrieval using both:
- **Direct queries**: Tools that directly return disease information
- **Multi-step chains**: Tool sequences that derive disease info indirectly

## 10 Research Dimensions

| # | Dimension | Key Tools | Use Case |
|---|-----------|-----------|----------|
| 1 | **Identification & Ontology** | OSL_get_efo_id_by_disease_name, ols_*, umls_*, icd_search_codes | Map disease names to IDs, get synonyms |
| 2 | **Clinical Manifestations** | OpenTargets_get_associated_phenotypes_*, get_HPO_ID_by_*, MedlinePlus_* | Symptoms, phenotypes, clinical signs |
| 3 | **Genetic Basis** | OpenTargets_get_associated_targets_*, clinvar_*, gwas_* | Genes, variants, GWAS associations |
| 4 | **Treatment Landscape** | OpenTargets_get_associated_drugs_*, search_clinical_trials, extract_* | Drugs, trials, outcomes |
| 5 | **Pathways & Mechanisms** | Reactome_*, humanbase_ppi_analysis | Disease pathways, PPI networks |
| 6 | **Literature** | PubMed_*, OpenTargets_get_publications_* | Research papers, trends |
| 7 | **Similar Diseases** | OpenTargets_get_similar_entities_* | Comorbidities, related conditions |
| 8 | **Cancer-Specific** | civic_* | CIViC variants, clinical evidence |
| 9 | **Pharmacology** | GtoPdb_* | Druggable targets, interactions |
| 10 | **Adverse Events** | OpenTargets_get_drug_warnings_*, extract_clinical_trial_adverse_events | Safety data |

## Quick Start

```python
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()

# Step 1: Get disease ID
disease = tu.tools.OSL_get_efo_id_by_disease_name(disease="Parkinson disease")
efo_id = disease['efo_id']  # EFO_0002508

# Step 2: Get comprehensive data
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId=efo_id)
phenotypes = tu.tools.OpenTargets_get_associated_phenotypes_by_disease_efoId(efoId=efo_id)
drugs = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId=efo_id, size=50)
trials = tu.tools.search_clinical_trials(condition="Parkinson disease", pageSize=10)
```

## Multi-Step Tool Chains

### Symptom → Disease (Differential Diagnosis)
```
Symptom → get_HPO_ID_by_phenotype → get_joint_associated_diseases_by_HPO_ID_list
```

### Gene → Disease
```
Gene → OpenTargets_get_diseases_phenotypes_by_target_ensembl
```

### Drug → Disease (via targets)
```
Drug → OpenTargets_get_drug_mechanisms_of_action_by_chemblId → OpenTargets_get_diseases_phenotypes_by_target_ensembl
```

### Variant → Disease
```
SNP → gwas_get_associations_for_snp → Disease associations
```

## Files in This Skill

| File | Description |
|------|-------------|
| `SKILL.md` | Main skill with all 10 dimensions, tool chains, code examples |
| `TOOLS_REFERENCE.md` | Complete tool reference with signatures and examples |
| `EXAMPLES.md` | Concrete examples for different disease types |
| `README.md` | This overview |

## When to Use

Apply when:
- User asks about any disease, syndrome, or medical condition
- Need comprehensive disease intelligence
- Want to understand disease mechanisms, genetics, or treatments
- Performing systematic disease analysis

## Tool Categories

**100+ tools across categories:**
- OpenTargets (20+ tools)
- GWAS Catalog (13 tools)
- ClinVar (3 tools)
- ClinicalTrials.gov (10 tools)
- PubMed (5 tools)
- Reactome (16 tools)
- Monarch/HPO (3 tools)
- MedlinePlus (5 tools)
- UMLS (5 tools)
- CIViC (12 tools)
- GtoPdb (8 tools)
- UniProt (disease variants)
- HumanBase (tissue-specific PPI)
