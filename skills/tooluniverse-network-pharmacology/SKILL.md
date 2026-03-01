---
name: tooluniverse-network-pharmacology
description: Construct and analyze compound-target-disease networks for drug repurposing, polypharmacology discovery, and systems pharmacology. Builds multi-layer networks from ChEMBL, OpenTargets, STRING, DrugBank, Reactome, FAERS, and 60+ other ToolUniverse tools. Calculates Network Pharmacology Scores (0-100), identifies repurposing candidates, predicts mechanisms, and analyzes polypharmacology. Use when users ask about drug repurposing via network analysis, multi-target drug effects, compound-target-disease networks, systems pharmacology, or polypharmacology.
---

# Network Pharmacology Pipeline

Construct and analyze compound-target-disease (C-T-D) networks to identify drug repurposing opportunities, understand polypharmacology, and predict drug mechanisms using systems pharmacology approaches.

**IMPORTANT**: Always use English terms in tool calls (drug names, disease names, target names), even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

---

## When to Use This Skill

Apply when users:
- Ask "Can [drug] be repurposed for [disease] based on network analysis?"
- Want to understand multi-target (polypharmacology) effects of a compound
- Need compound-target-disease network construction and analysis
- Ask about network proximity between drug targets and disease genes
- Want systems pharmacology analysis of a drug or target
- Ask about drug repurposing candidates ranked by network metrics
- Need mechanism prediction for a drug in a new indication
- Want to identify hub genes in disease networks as therapeutic targets
- Ask about disease module coverage by a compound's targets

**NOT for** (use other skills instead):
- Simple drug repurposing without network analysis -> Use `tooluniverse-drug-repurposing`
- Single target validation -> Use `tooluniverse-drug-target-validation`
- Adverse event detection only -> Use `tooluniverse-adverse-event-detection`
- General disease research -> Use `tooluniverse-disease-research`
- GWAS interpretation -> Use `tooluniverse-gwas-snp-interpretation`

---

## Network Pharmacology Score (0-100)

### Score Components

**Network Proximity** (0-35 points):
- Strong proximity (Z < -2, p < 0.01): 35 points
- Moderate proximity (Z < -1, p < 0.05): 20 points
- Weak proximity (Z < -0.5): 10 points
- No proximity: 0 points

**Clinical Evidence** (0-25 points):
- Approved for related indication: 25 points
- Active clinical trials: 15 points
- Completed trials with positive results: 10 points
- Preclinical only: 5 points

**Target-Disease Association** (0-20 points):
- Strong genetic evidence (GWAS, rare variants): 20 points
- Moderate evidence (pathways, literature): 12 points
- Weak evidence (computational only): 5 points

**Safety Profile** (0-10 points):
- FDA-approved, favorable safety: 10 points
- Known manageable adverse events: 7 points
- Significant safety concerns: 3 points
- Black box warning relevant to indication: 0 points

**Mechanism Plausibility** (0-10 points):
- Clear pathway mechanism with functional evidence: 10 points
- Indirect mechanism via network neighbors: 6 points
- Purely computational prediction: 2 points

### Priority Tiers

| Score | Tier | Recommendation |
|-------|------|----------------|
| 80-100 | Tier 1 | High repurposing potential - proceed with experimental validation |
| 60-79 | Tier 2 | Good potential - needs mechanistic validation |
| 40-59 | Tier 3 | Moderate potential - high-risk/high-reward, needs extensive validation |
| 0-39 | Tier 4 | Low potential - consider alternative approaches |

### Evidence Grading

| Tier | Criteria | Examples |
|------|----------|----------|
| T1 | Human clinical proof, regulatory evidence | FDA-approved indication, Phase III trial, patient genomics |
| T2 | Functional experimental evidence | Bioactivity (IC50 < 1 uM), CRISPR screen, animal model |
| T3 | Association/computational evidence | GWAS hit, network proximity, pathway enrichment, expression |
| T4 | Prediction, annotation, text-mining | AlphaFold prediction, database annotation, literature co-mention |

---

## KEY PRINCIPLES

1. **Report-first** - Create report file FIRST, then populate progressively
2. **Disambiguate first** - Resolve all identifiers before any analysis
3. **Bidirectional network** - Construct C-T-D from both directions comprehensively
4. **Quantify metrics** - Calculate proximity, centrality, module overlap numerically
5. **Rank candidates** - Prioritize by composite Network Pharmacology Score
6. **Predict mechanism** - Explain HOW drug could work for disease via network paths
7. **Clinical feasibility** - FDA-approved drugs ranked higher than preclinical
8. **Safety context** - Flag known adverse events and off-target liabilities
9. **Grade evidence** - Grade all evidence T1-T4
10. **Document negatives** - "No data" is data; empty sections are failures
11. **Cite sources** - Every finding must cite the source tool/database
12. **Completeness checklist** - Mandatory section at end showing analysis coverage

---

## Complete Workflow

### Phase 0: Entity Disambiguation and Report Setup

**Step 0.1**: Create the report file immediately before doing any tool calls. Write a header and placeholder sections so the report grows progressively.

**Step 0.2**: Resolve each input entity to all required identifiers.

For a **compound**: call `OpenTargets_get_drug_chembId_by_generic_name` to get the ChEMBL ID; call `drugbank_get_drug_basic_info_by_drug_name_or_id` (requires all 4 params: query, case_sensitive, exact_match, limit) to get the DrugBank ID; call `PubChem_get_CID_by_compound_name` to get the CID, then `PubChem_get_compound_properties_by_CID` for SMILES.

For a **target**: call `OpenTargets_get_target_id_description_by_name` to get the Ensembl ID; call `ensembl_lookup_gene` (species param required) for gene details; call `MyGene_query_genes` for cross-references.

For a **disease**: call `OpenTargets_get_disease_id_description_by_name` to get the MONDO/EFO ID; call `OpenTargets_get_disease_description_by_efoId` for description; call `OpenTargets_get_disease_ids_by_efoId` for cross-references.

---

### Phase 1: Network Node Identification

**Step 1.1**: Identify compound nodes.

Call `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` and `OpenTargets_get_associated_targets_by_drug_chemblId` to retrieve drug targets and mechanism of action. Supplement with `drugbank_get_targets_by_drug_name_or_drugbank_id` (all 4 DrugBank params required) and `DGIdb_get_drug_gene_interactions`. Also call `CTD_get_chemical_gene_interactions` for broader chemical-gene interactions and optionally `STITCH_get_chemical_protein_interactions`.

For drug-disease landscape: call `OpenTargets_get_drug_indications_by_chemblId`, `OpenTargets_get_drug_approval_status_by_chemblId`, and `OpenTargets_get_associated_diseases_by_drug_chemblId`.

**Step 1.2**: Identify target nodes (disease-associated targets).

Call `OpenTargets_get_associated_targets_by_disease_efoId` (limit 50) to get ranked targets. For the top 10, call `OpenTargets_target_disease_evidence` (both efoId and ensemblId required) for multi-datasource evidence. Call `OpenTargets_search_gwas_studies_by_disease` for GWAS context. For each key gene, call `CTD_get_gene_diseases` and `Pharos_get_target` to get druggability development levels (Tclin / Tchem / Tbio / Tdark).

**Step 1.3**: Identify disease nodes and related conditions.

Call `OpenTargets_get_similar_entities_by_disease_efoId` for related diseases, `OpenTargets_get_disease_descendants_children_by_efoId` and `OpenTargets_get_disease_ancestors_parents_by_efoId` for ontology context, `OpenTargets_get_associated_phenotypes_by_disease_efoId` for phenotypes, and `OpenTargets_get_disease_therapeutic_areas_by_efoId`.

---

### Phase 2: Network Edge Construction

**Step 2.1**: Compound-target edges (bioactivity data).

Call `ChEMBL_get_target_activities` using the target's ChEMBL ID to get IC50/Ki values. Call `ChEMBL_search_mechanisms` for all mechanisms. Supplement with `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` and optionally `BindingDB_get_ligands_by_uniprot` if a UniProt ID is available.

**Step 2.2**: Target-disease edges (genetic and functional associations).

For each top disease target, call `OpenTargets_target_disease_evidence`. Call `GWAS_search_associations_by_gene` for GWAS data. Supplement with `CTD_get_gene_diseases` and `PharmGKB_get_gene_details` for pharmacogenomics context.

**Step 2.3**: Compound-disease edges (clinical evidence).

Call `search_clinical_trials` (query_term required) and `clinical_trials_search` for trials. Call `CTD_get_chemical_diseases` for chemical-disease associations with DirectEvidence field ("therapeutic" or "marker/mechanism"). Call `PubMed_search_articles` and `EuropePMC_search_articles` for co-mention literature.

**Step 2.4**: Target-target edges (PPI network).

Call `STRING_get_interaction_partners` (protein_ids list, species=9606, limit) for PPI partners. Call `STRING_get_network` for the full network. Supplement with `intact_search_interactions` and `OpenTargets_get_target_interactions_by_ensemblID`. For tissue-specific PPI (e.g., brain), call `humanbase_ppi_analysis` (all 5 params required: gene_list, tissue, max_node, interaction, string_mode).

---

### Phase 3: Network Analysis

**Step 3.1**: Network topology (computed from Phase 2 data — no additional tool calls needed).

- **Node degree**: count connections from STRING + IntAct + OpenTargets interactions
- **Hub identification**: nodes with degree > mean + 2*SD are hubs; hub genes in the disease module are priority therapeutic targets
- **Betweenness centrality**: nodes on shortest paths between drug targets and disease genes; high betweenness = potential mediating targets
- **Network modules**: cluster disease-associated genes (disease module) and drug targets (drug module); module overlap = direct network relevance
- **Shortest paths**: length < 2 = direct interaction; 2-3 = close proximity; >4 = distant, weaker association

**Step 3.2**: Network proximity calculation (computed from collected data).

Practical approach using available data:
1. Collect drug target set T_d (Phase 1) and disease gene set G_d (Phase 1)
2. Count direct interactions between T_d and G_d in the PPI
3. Count shared PPI partners (second-degree connections)
4. Calculate overlap coefficient = shared_partners / min(degree_T, degree_D)
5. Count shared pathways as additional proximity metric
6. Estimate Z-score: strong overlap -> Z < -2 (35 pts); moderate -> Z < -1 (20 pts); weak -> Z < -0.5 (10 pts); none -> 0 pts

**Step 3.3**: Functional enrichment.

Call `STRING_functional_enrichment` and `STRING_ppi_enrichment` on the disease gene set. Call `enrichr_gene_enrichment_analysis` with libs `["KEGG_2021_Human", "Reactome_2022", "GO_Biological_Process_2023"]`. Call `ReactomeAnalysis_pathway_enrichment` with space-separated gene identifiers (NOT an array).

---

### Phase 4: Drug Repurposing Predictions

**Step 4.1**: Identify and rank repurposing candidates.

For **disease-to-compound mode**: for each top disease target, call `OpenTargets_get_associated_drugs_by_target_ensemblID`, `DGIdb_get_drug_gene_interactions`, and `drugbank_get_drug_name_and_description_by_target_name`. Collect candidates, deduplicate, and score each by: target_disease_score x drug_target_affinity x approval_bonus.

For **compound-to-disease mode**: for each drug target, call `OpenTargets_get_diseases_phenotypes_by_target_ensembl` to identify disease associations.

**Step 4.2**: Mechanism prediction for each repurposing candidate.

Trace the network path: Drug -> direct targets -> PPI neighbors -> disease genes. Call `ReactomeAnalysis_pathway_enrichment` on the combined set of drug target genes and disease genes to find shared pathways. Call `drugbank_get_pathways_reactions_by_drug_or_id` for drug-specific pathway data. Overlapping pathways explain the putative mechanism.

---

### Phase 5: Polypharmacology Analysis

**Step 5.1**: Multi-target profiling.

Call `OpenTargets_get_associated_targets_by_drug_chemblId` (size=100) for all targets. Supplement with `drugbank_get_targets_by_drug_name_or_drugbank_id` (includes enzymes, carriers, transporters) and `CTD_get_chemical_gene_interactions` for indirect interactions.

Compute disease module coverage: overlap between drug target set and top 50 disease genes. Coverage = |T_d ∩ G_d| / |G_d|.

For target family classification, call `OpenTargets_get_target_classes_by_ensemblID` for each target.

**Step 5.2**: Selectivity analysis.

For each drug target, call `DGIdb_get_gene_druggability`, `Pharos_get_target` (development level: Tclin = known drug targets, Tchem = has chemical tools, Tbio = has biology, Tdark = unexplored), and `OpenTargets_get_target_tractability_by_ensemblID`.

---

### Phase 6: Safety and Toxicity Context

**Step 6.1**: Adverse event profiling.

Call `FAERS_search_reports_by_drug_and_reaction` (limit 100). Call `FAERS_filter_serious_events` (operation param required). Call `FAERS_count_death_related_by_drug` (use `medicinalproduct` param, NOT `drug_name`). For specific AEs, call `FAERS_calculate_disproportionality` (operation param required) to get PRR and ROR with 95% CI and signal_detection flag.

Also call `OpenTargets_get_drug_adverse_events_by_chemblId`, `OpenTargets_get_drug_warnings_by_chemblId`, `OpenTargets_get_drug_blackbox_status_by_chembl_ID`, and `FDA_get_warnings_and_cautions_by_drug_name`.

**Step 6.2**: Target safety profiling.

For each drug target, call `OpenTargets_get_target_safety_profile_by_ensemblID`, `gnomad_get_gene_constraints` (pLI > 0.9 = loss-of-function intolerant = essential = safety concern), and `HPA_get_rna_expression_by_source` to assess tissue expression breadth.

---

### Phase 7: Validation Evidence

**Step 7.1**: Clinical precedent.

Call `search_clinical_trials` with drug + disease. For each matching trial (up to 5), call `clinical_trials_get_details`, `extract_clinical_trial_outcomes`, and `extract_clinical_trial_adverse_events`. Call `OpenTargets_get_approved_indications_by_drug_chemblId` for all approved uses.

**Step 7.2**: Literature evidence.

Call `PubMed_search_articles` with query "[drug] [disease] repurposing OR repositioning OR network pharmacology". Call `EuropePMC_search_articles` for broader coverage. Call `OpenTargets_get_publications_by_drug_chemblId` and `OpenTargets_get_publications_by_disease_efoId`.

**Step 7.3**: Experimental evidence.

Call `ChEMBL_search_drugs` for bioactivity data. If SMILES is available, call `ADMETAI_predict_toxicity`, `ADMETAI_predict_BBB_penetrance`, and `ADMETAI_predict_bioavailability`. Call `PharmGKB_get_drug_details` and `PharmGKB_get_clinical_annotations` for pharmacogenomics.

---

### Phase 8: Report Generation

**Step 8.1**: Compute Network Pharmacology Score from all collected data:
1. Network Proximity (0-35): count direct T_d <-> G_d PPI interactions, shared partners, shared pathways -> map to Z-score equivalent
2. Clinical Evidence (0-25): trials found + approved indications + max trial phase
3. Target-Disease Association (0-20): average OpenTargets score for drug targets in disease, weighted by evidence type
4. Safety (0-10): FDA approval (+5), black box warning (-3), death report proportion, off-target count penalty
5. Mechanism Plausibility (0-10): known mechanism for related indication (+5), pathway evidence (+3), network path length (+2)

**Step 8.2**: Generate the report with these sections:

```
# Network Pharmacology Analysis: [Entity]

## Executive Summary
[2-3 sentence summary]

## Network Pharmacology Score: [X]/100 - Tier [N]
| Component | Score | Max | Evidence |
Network Proximity | X | 35 | ...
Clinical Evidence  | X | 25 | ...
Target-Disease Assoc | X | 20 | ...
Safety Profile | X | 10 | ...
Mechanism Plausibility | X | 10 | ...
TOTAL | X | 100 |

## 1. Entity Profile
## 2. Network Topology Summary
   - Total nodes, edges, density
   - Hub nodes (degree > mean + 2*SD)
   - Drug target module vs disease gene module
   - Module overlap (shared genes, shared pathways)
## 3. Network Proximity
   - Z-score estimate, direct interactions, shared PPI partners, shared pathways
## 4. Top Repurposing Candidates (Ranked, up to 10)
   - Score, ChEMBL ID, status, current indications
   - Network path: Drug -> [targets] -> [PPI] -> [disease genes]
   - Mechanism prediction, clinical evidence, safety, evidence grade
## 5. Polypharmacology Profile
   - Disease module coverage percentage
   - Primary vs off-targets, synergistic/antagonistic effects
## 6. Pathway Analysis
   - Drug-affected pathways, disease-associated pathways, overlapping pathways
## 7. Safety Considerations
   - Top AEs with PRR/ROR, target safety flags, off-target risks
## 8. Clinical Precedent
   - Clinical trials (NCT IDs + status), literature summary, PGx data
## 9. Evidence Summary Table
   | Finding | Source | Evidence Grade | Confidence |
## 10. Recommendations
    - Immediate actions, further investigation, risk mitigation

## Completeness Checklist
| Phase | Status | Tools Used | Key Findings |
Entity Disambiguation | Done/Partial/Failed | ... | ...
[one row per phase]
```

---

## Known Gotchas

**DrugBank tools**: ALL require exactly 4 parameters: `query`, `case_sensitive`, `exact_match`, `limit`. Missing any one will fail. Use `case_sensitive=False`, `exact_match=True` for exact drug name matching.

**FAERS analytics tools** (`calculate_disproportionality`, `compare`, `filter_serious_events`, `stratify`, `rollup`, `trends`): ALL require an `operation` parameter as the first argument.

**FAERS count tools** (`count_death_related_by_drug`, `count_reactions`, etc.): Use `medicinalproduct` as the parameter name, NOT `drug_name`.

**ReactomeAnalysis_pathway_enrichment**: Takes `identifiers` as a space-separated string, NOT a Python list or array.

**ensembl_lookup_gene**: REQUIRES `species='homo_sapiens'` — the call will error or return wrong results without it.

**OpenTargets_target_disease_evidence**: BOTH `efoId` AND `ensemblId` are required — omitting either will fail.

**OpenTargets response structure**: Nested `{data: {entity: {field: ...}}}` — index carefully, do not assume a flat structure.

**PubMed_search_articles**: Returns a plain list of dicts, NOT `{articles: [...]}`.

**PubChem CID lookup**: Returns `{IdentifierList: {CID: [...]}}` — no `data` wrapper.

**STRING tools**: Return `{status: "success", data: [...]}`.

**CTD tools**: Return `{data: [...]}` — result sets can be very large; consider limiting queries.

**humanbase_ppi_analysis**: ALL 5 params required: `gene_list`, `tissue`, `max_node`, `interaction`, `string_mode`.

**Disease name synonyms**: Try "Alzheimer disease" not "Alzheimer's disease" for OpenTargets lookups. Use `OpenTargets_multi_entity_search_by_query_string` for fuzzy matching.

**Promiscuous compounds (>50 targets)**: Limit target retrieval to top 50 by confidence score; classify primary (mechanism) vs secondary (off-target) before network construction.

**Large networks (>100 nodes)**: Prioritize top-scored edges; analyze modules rather than full graph; summarize statistics instead of listing all nodes.

**Disconnected networks**: Report explicitly — disconnection is a meaningful result indicating low repurposing potential. Analyze drug module and disease module separately, then look for pathway-level bridges.

---

## Fallback Strategies

| Phase | Primary | Fallback 1 | Fallback 2 |
|-------|---------|-----------|-----------|
| Compound ID | OpenTargets drug lookup | ChEMBL search | PubChem CID lookup |
| Target ID | OpenTargets target lookup | ensembl_lookup_gene | MyGene_query_genes |
| Disease ID | OpenTargets disease lookup | ols_search_efo_terms | CTD_get_chemical_diseases |
| Drug targets | OpenTargets mechanisms | DrugBank targets | DGIdb interactions |
| Disease targets | OpenTargets disease targets | CTD gene-diseases | GWAS associations |
| PPI network | STRING interactions | OpenTargets interactions | IntAct interactions |
| Pathways | ReactomeAnalysis enrichment | enrichr enrichment | STRING functional enrichment |
| Clinical trials | search_clinical_trials | clinical_trials_search | PubMed clinical |
| Safety | FAERS + FDA | OpenTargets AEs | DrugBank safety |
| Literature | PubMed search | EuropePMC search | OpenTargets publications |

---

## Tool Reference

Full parameter tables are in [references/tools.md](references/tools.md).

| Tool | Purpose |
|------|---------|
| `OpenTargets_get_drug_chembId_by_generic_name` | Get ChEMBL ID from drug name |
| `OpenTargets_get_drug_id_description_by_name` | Get drug details from name |
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | Drug MOA and direct targets |
| `OpenTargets_get_associated_targets_by_drug_chemblId` | All targets linked to drug |
| `OpenTargets_get_drug_indications_by_chemblId` | Approved and trial indications |
| `OpenTargets_get_associated_diseases_by_drug_chemblId` | All diseases linked to drug |
| `OpenTargets_get_drug_approval_status_by_chemblId` | FDA approval status |
| `OpenTargets_get_drug_blackbox_status_by_chembl_ID` | Black box warning check |
| `OpenTargets_get_drug_adverse_events_by_chemblId` | Adverse events from OT |
| `OpenTargets_get_drug_warnings_by_chemblId` | Drug warnings from OT |
| `OpenTargets_get_approved_indications_by_drug_chemblId` | Approved indications list |
| `OpenTargets_get_publications_by_drug_chemblId` | Drug-associated publications |
| `OpenTargets_get_target_id_description_by_name` | Get Ensembl ID from gene symbol |
| `OpenTargets_get_associated_targets_by_disease_efoId` | Disease-associated targets ranked |
| `OpenTargets_target_disease_evidence` | Multi-datasource T-D evidence |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | Drugs linked to a target |
| `OpenTargets_get_diseases_phenotypes_by_target_ensembl` | Diseases associated with target |
| `OpenTargets_get_target_interactions_by_ensemblID` | Molecular interactions for target |
| `OpenTargets_get_target_tractability_by_ensemblID` | Target druggability/tractability |
| `OpenTargets_get_target_classes_by_ensemblID` | Target family classification |
| `OpenTargets_get_target_safety_profile_by_ensemblID` | Target safety liabilities |
| `OpenTargets_get_disease_id_description_by_name` | Get EFO/MONDO ID from name |
| `OpenTargets_get_disease_description_by_efoId` | Disease description |
| `OpenTargets_get_disease_ids_by_efoId` | Disease cross-references |
| `OpenTargets_get_disease_descendants_children_by_efoId` | Disease ontology children |
| `OpenTargets_get_disease_ancestors_parents_by_efoId` | Disease ontology parents |
| `OpenTargets_get_similar_entities_by_disease_efoId` | Related/similar diseases |
| `OpenTargets_get_associated_phenotypes_by_disease_efoId` | Disease phenotypes |
| `OpenTargets_get_disease_therapeutic_areas_by_efoId` | Therapeutic area classification |
| `OpenTargets_search_gwas_studies_by_disease` | GWAS studies for disease |
| `OpenTargets_get_publications_by_disease_efoId` | Disease-associated publications |
| `OpenTargets_multi_entity_search_by_query_string` | Broad entity search (fuzzy) |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | Basic drug info from DrugBank |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | Drug targets from DrugBank |
| `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` | Drug pharmacology from DrugBank |
| `drugbank_get_pathways_reactions_by_drug_or_id` | Drug pathway reactions |
| `drugbank_get_drug_name_and_description_by_target_name` | Drugs for a target (DrugBank) |
| `PubChem_get_CID_by_compound_name` | PubChem CID from name |
| `PubChem_get_compound_properties_by_CID` | SMILES, MW, IUPAC from CID |
| `ChEMBL_get_target_activities` | Bioactivity data for a target |
| `ChEMBL_search_drugs` | Search drugs in ChEMBL |
| `ChEMBL_search_mechanisms` | Drug mechanism data from ChEMBL |
| `DGIdb_get_drug_gene_interactions` | Drug-gene interactions (DGIdb) |
| `DGIdb_get_gene_druggability` | Gene druggability assessment |
| `CTD_get_chemical_gene_interactions` | Chemical-gene interactions |
| `CTD_get_gene_diseases` | Gene-disease associations |
| `CTD_get_chemical_diseases` | Chemical-disease associations |
| `GWAS_search_associations_by_gene` | GWAS associations for a gene |
| `STRING_get_interaction_partners` | PPI partners from STRING |
| `STRING_get_network` | Full STRING PPI network |
| `STRING_functional_enrichment` | Functional enrichment (STRING) |
| `STRING_ppi_enrichment` | PPI enrichment statistics |
| `intact_search_interactions` | Molecular interactions (IntAct) |
| `humanbase_ppi_analysis` | Tissue-specific PPI (HumanBase) |
| `ReactomeAnalysis_pathway_enrichment` | Pathway enrichment (Reactome) |
| `enrichr_gene_enrichment_analysis` | Multi-library gene enrichment |
| `ensembl_lookup_gene` | Gene details from Ensembl |
| `MyGene_query_genes` | Gene cross-references (MyGene) |
| `Pharos_get_target` | Target development level (Pharos) |
| `PharmGKB_get_gene_details` | Pharmacogenomics for gene |
| `PharmGKB_get_drug_details` | Pharmacogenomics for drug |
| `PharmGKB_get_clinical_annotations` | Clinical PGx annotations |
| `BindingDB_get_ligands_by_uniprot` | Binding affinity data |
| `STITCH_resolve_identifier` | Resolve chemical ID in STITCH |
| `STITCH_get_chemical_protein_interactions` | Chemical-protein interactions |
| `FAERS_search_reports_by_drug_and_reaction` | FAERS raw adverse event reports |
| `FAERS_filter_serious_events` | Filter serious FAERS events |
| `FAERS_count_death_related_by_drug` | Death count from FAERS |
| `FAERS_calculate_disproportionality` | PRR/ROR signal detection |
| `FDA_get_warnings_and_cautions_by_drug_name` | FDA label warnings |
| `gnomad_get_gene_constraints` | Gene essentiality (pLI, LOEUF) |
| `HPA_get_rna_expression_by_source` | Tissue RNA expression (HPA) |
| `search_clinical_trials` | Search ClinicalTrials.gov |
| `clinical_trials_search` | Alternative trial search |
| `clinical_trials_get_details` | Details for a specific trial |
| `extract_clinical_trial_outcomes` | Outcomes from a trial |
| `extract_clinical_trial_adverse_events` | AEs from a clinical trial |
| `PubMed_search_articles` | PubMed literature search |
| `PubMed_Guidelines_Search` | PubMed clinical guidelines |
| `EuropePMC_search_articles` | Europe PMC literature search |
| `ADMETAI_predict_toxicity` | ADMET toxicity prediction |
| `ADMETAI_predict_BBB_penetrance` | BBB penetrance prediction |
| `ADMETAI_predict_bioavailability` | Oral bioavailability prediction |

---

## Resources

For focused drug repurposing (without network analysis): [tooluniverse-drug-repurposing](../tooluniverse-drug-repurposing/SKILL.md)
For target validation: [tooluniverse-drug-target-validation](../tooluniverse-drug-target-validation/SKILL.md)
For adverse event detection: [tooluniverse-adverse-event-detection](../tooluniverse-adverse-event-detection/SKILL.md)
For systems biology: [tooluniverse-systems-biology](../tooluniverse-systems-biology/SKILL.md)
For protein interactions: [tooluniverse-protein-interactions](../tooluniverse-protein-interactions/SKILL.md)
