# Tool Reference: Infectious Disease Outbreak Intelligence

Full tool tables and report template for the `tooluniverse-infectious-disease` skill.

---

## Report File Template

Initialize `[PATHOGEN]_outbreak_intelligence.md` with this skeleton. All `[Analyzing...]` placeholders must be replaced before delivery.

```markdown
# Outbreak Intelligence Report: [PATHOGEN]

**Generated**: [Date] | **Query**: [Original query] | **Status**: In Progress

---

## Executive Summary
[Analyzing...]

---

## 1. Pathogen Profile
### 1.1 Classification
[Analyzing...]
### 1.2 Related Pathogens
[Analyzing...]

---

## 2. Druggable Targets
### 2.1 Prioritized Targets
[Analyzing...]
### 2.2 Target Details
[Analyzing...]

---

## 3. Target Structures
### 3.1 Prediction Results
[Analyzing...]
### 3.2 Binding Sites
[Analyzing...]

---

## 4. Drug Repurposing Screen
### 4.1 Candidate Drugs
[Analyzing...]
### 4.2 Docking Results
[Analyzing...]

---

## 5. Literature Intelligence
### 5.1 Recent Findings
[Analyzing...]
### 5.2 Clinical Trials
[Analyzing...]

---

## 6. Recommendations
### 6.1 Immediate Actions
[Analyzing...]
### 6.2 Clinical Trial Opportunities
[Analyzing...]
### 6.3 Research Priorities
[Analyzing...]

---

## 7. Data Gaps & Limitations
[Analyzing...]

---

## 8. Data Sources
[Will be populated...]
```

---

## Tool Reference by Phase

| Phase | Tool | Purpose |
|-------|------|---------|
| 1 | `NCBI_Taxonomy_search` | Classify pathogen, get TaxID |
| 1 | `UniProt_search` | List pathogen proteins |
| 1 | `UniProt_get_protein_by_accession` | Get protein details |
| 1 | `UniProt_get_protein_sequence` | Get amino acid sequence |
| 2 | `ChEMBL_search_targets` | Find drug targets |
| 2 | `ChEMBL_get_target_activities` | Get bioactivity data |
| 2 | `DGIdb_get_drug_gene_interactions` | Drug-gene interactions |
| 2 | `DGIdb_get_gene_druggability` | Druggability score |
| 3 | `NvidiaNIM_alphafold2` | High-accuracy structure prediction (async, 5-15 min) |
| 3 | `NvidiaNIM_esmfold` | Fast structure prediction (sync, ~30 sec) |
| 4 | `ChEMBL_search_drugs` | Find approved drug candidates |
| 4 | `NvidiaNIM_diffdock` | Blind docking screen |
| 4 | `NvidiaNIM_boltz2` | Biomolecular complex prediction |
| 4.5 | `kegg_search_pathway` | Pathogen metabolic pathways |
| 4.5 | `kegg_get_pathway_genes` | Genes in a KEGG pathway |
| 4.5 | `Reactome_search_pathway` | Host-pathogen pathways |
| 5 | `PubMed_search_articles` | Peer-reviewed literature |
| 5 | `EuropePMC_search_articles` | Preprints (source=PPR) |
| 5 | `ArXiv_search_papers` | Computational preprints |
| 5 | `openalex_search_works` | Citation-ranked search |
| 5 | `SemanticScholar_search` | AI-ranked literature |
| 5 | `search_clinical_trials` | Active trials |
| 5 | `BioRxiv_get_preprint` | Full preprint by DOI |
| 5 | `MedRxiv_get_preprint` | Full clinical preprint by DOI |
