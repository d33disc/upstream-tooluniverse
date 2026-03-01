---
name: tooluniverse-drug-target-validation
description: Comprehensive computational validation of drug targets for early-stage drug discovery. Evaluates targets across 10 dimensions (disambiguation, disease association, druggability, chemical matter, clinical precedent, safety, pathway context, validation evidence, structural insights, validation roadmap) using 60+ ToolUniverse tools. Produces a quantitative Target Validation Score (0-100) with GO/NO-GO recommendation. Use when users ask about target validation, druggability assessment, target prioritization, or "is X a good drug target for Y?"
---

# Drug Target Validation Pipeline

Validate drug target hypotheses using multi-dimensional computational evidence before committing to wet-lab work. Produces a quantitative Target Validation Score (0-100) with priority tier classification and GO/NO-GO recommendation.

**KEY PRINCIPLES**:
1. **Report-first** - Create report file first, then populate progressively
2. **Target disambiguation FIRST** - Resolve all identifiers before any analysis
3. **Evidence grading** - Grade all evidence as T1 (experimental) to T4 (computational)
4. **Disease-specific** - Tailor analysis to disease context when provided
5. **Modality-aware** - Consider small molecule vs biologics tractability
6. **Safety-first** - Prominently flag safety concerns early
7. **Quantitative scoring** - Every dimension scored numerically (0-100 composite)
8. **Negative results documented** - "No data" is data; empty sections are failures
9. **Source references** - Every statement must cite tool/database
10. **English-first queries** - Always use English terms in tool calls; respond in user's language

---

## When to Use This Skill

Apply when users ask:
- "Is [target] a good drug target for [disease]?"
- Need target validation, druggability assessment, or target prioritization
- Want safety risk analysis of modulating a target
- Need chemical starting points for target validation
- Need a GO/NO-GO recommendation or comprehensive target dossier

**NOT for**: general target biology (use `tooluniverse-target-research`), drug profiling (use `tooluniverse-drug-research`), variant interpretation, or disease research.

---

## Scoring System

### Score Components (Total: 0-100)

| Dimension | Max | Sub-components |
|-----------|-----|----------------|
| Disease Association | 30 | Genetic (10) + Literature (10) + Pathway (10) |
| Druggability | 25 | Structural tractability (10) + Chemical matter (10) + Target class (5) |
| Safety Profile | 20 | Expression selectivity (5) + Genetic validation (10) + Known ADRs (5) |
| Clinical Precedent | 15 | Approved=15, Ph3=10, Ph2=7, Ph1=5, Preclinical=3, None=0 |
| Validation Evidence | 10 | Functional studies (5) + Disease models (5) |

### Priority Tiers

| Score | Tier | Recommendation |
|-------|------|----------------|
| 80-100 | Tier 1 | Highly validated - proceed with confidence |
| 60-79 | Tier 2 | Good target - needs focused validation |
| 40-59 | Tier 3 | Moderate risk - significant validation needed |
| 0-39 | Tier 4 | High risk - consider alternatives |

### Evidence Grades

| Grade | Symbol | Criteria |
|-------|--------|----------|
| T1 | [T1] | Direct mechanistic, human clinical proof (approved drug, patient mutation, crystal structure with mechanism) |
| T2 | [T2] | Functional studies, model organism (siRNA phenotype, mouse KO, biochemical assay) |
| T3 | [T3] | Association, screen hits, computational (GWAS hit, DepMap essentiality) |
| T4 | [T4] | Mention, review, text-mined, predicted (review article, AlphaFold prediction) |

---

## Phase 0: Target Disambiguation (ALWAYS FIRST)

**Objective**: Resolve the target to all needed identifiers before any analysis.

**Steps**:
1. Call `MyGene_query_genes` with the gene symbol to get Ensembl, UniProt, and Entrez IDs
2. Call `UniProt_get_entry_by_accession` to get protein function and PDB cross-references
3. Call `ensembl_lookup_gene` to get the versioned Ensembl ID needed for GTEx (e.g., ENSG00000146648.18)
4. Call `ensembl_get_xrefs` to confirm cross-database ID mappings
5. Call `OpenTargets_get_target_id_description_by_name` to get the verified OpenTargets Ensembl ID
6. Call `ChEMBL_search_targets` to get the ChEMBL target ID
7. Call `UniProt_get_function_by_accession` and `UniProt_get_alternative_names_by_accession` for context and collision detection

**Output**: A verified ID table with Gene Symbol, Full Name, Ensembl (plain + versioned), UniProt, Entrez, ChEMBL, and HGNC.

---

## Phase 1: Disease Association Evidence (0-30 pts)

**Objective**: Quantify the strength of target-disease association from genetic, literature, and pathway evidence.

**Steps**:
1. Call `OpenTargets_get_diseases_phenotypes_by_target_ensembl` to get all disease associations for the target
2. If a specific disease is provided, call `OpenTargets_get_disease_id_description_by_name` to get the EFO ID, then call `OpenTargets_target_disease_evidence` with both IDs
3. Call `OpenTargets_get_evidence_by_datasource` for genetic datasources (ot_genetics_portal, eva, gene2phenotype, genomics_england)
4. Call `gwas_get_snps_for_gene` to get GWAS associations; if disease-specific, also call `gwas_search_studies`
5. Call `gnomad_get_gene_constraints` to get pLI and LOEUF scores (pLI > 0.9 = essential gene)
6. Call `PubMed_search_articles` with target + disease query; call `OpenTargets_get_publications_by_target_ensemblID`

**Scoring**:
- Genetic (0-10): GWAS hits +3/locus (max 6), rare variant evidence +2, somatic mutations +2, pLI>0.9 +2
- Literature (0-10): >100 pubs=10, 50-100=7, 10-50=5, 1-10=3, none=0
- Pathway (0-10): OT overall score >0.8=10, 0.5-0.8=7, 0.2-0.5=4, <0.2=1

---

## Phase 2: Druggability Assessment (0-25 pts)

**Objective**: Assess whether the target is amenable to therapeutic intervention.

**Steps**:
1. Call `OpenTargets_get_target_tractability_by_ensemblID` for tractability across modalities (Small Molecule, Antibody, PROTAC)
2. Call `OpenTargets_get_target_classes_by_ensemblID` for target family classification (kinase, GPCR, nuclear receptor, etc.)
3. Call `Pharos_get_target` for the TDL classification: Tclin > Tchem > Tbio > Tdark
4. Call `DGIdb_get_gene_druggability` for druggability category annotations
5. Extract PDB cross-references from the UniProt entry (retrieved in Phase 0)
6. Call `alphafold_get_prediction` and `alphafold_get_summary` for structural coverage
7. Call `ProteinsPlus_predict_binding_sites` on the best available PDB structure for pocket detection
8. Call `OpenTargets_get_chemical_probes_by_target_ensemblID` and `OpenTargets_get_target_enabling_packages_by_ensemblID`

**Scoring**:
- Structural (0-10): co-crystal with ligand=10, PDB+pockets=7, AlphaFold confident pocket=5, AlphaFold low confidence=2, none=0
- Chemical matter (0-10): drug-like compounds IC50<100nM=10, tool compounds <1uM=7, HTS hits only=4, none=0
- Target class (0-5): kinase/GPCR/nuclear receptor=5, enzyme/ion channel=4, PPI/transporter=2, unknown=0

---

## Phase 3: Known Modulators & Chemical Matter

**Objective**: Identify existing chemical starting points.

**Steps**:
1. Call `ChEMBL_search_targets` to confirm the ChEMBL target ID, then call `ChEMBL_get_target_activities` with `target_chembl_id__exact` to retrieve bioactivity data (filter for pChEMBL >= 6.0)
2. Call `BindingDB_get_ligands_by_uniprot` with the UniProt ID and an affinity cutoff (e.g., 10000 nM)
3. Call `PubChem_search_assays_by_target_gene` to find HTS screening data; follow up with `PubChem_get_assay_summary` and `PubChem_get_assay_active_compounds` for top assays
4. Call `OpenTargets_get_associated_drugs_by_target_ensemblID` (size parameter is required) for known drugs
5. Call `ChEMBL_search_mechanisms` and `DGIdb_get_gene_info` for drug-target mechanism annotations

**Report**: Summarize approved drugs, best pChEMBL value, number of chemical series, BindingDB ligand count and affinity distribution, and available chemical probes.

---

## Phase 4: Clinical Precedent (0-15 pts)

**Objective**: Assess clinical validation from approved drugs and clinical trials.

**Steps**:
1. For known drugs targeting this protein, call `FDA_get_mechanism_of_action_by_drug_name` and `FDA_get_indications_by_drug_name`
2. Call `drugbank_get_targets_by_drug_name_or_drugbank_id` and `drugbank_get_safety_by_drug_name_or_drugbank_id` (all four parameters required: query, case_sensitive, exact_match, limit)
3. Call `search_clinical_trials` with the target gene symbol (query_term is required); repeat with disease condition if applicable
4. For known drug ChEMBL IDs, call `OpenTargets_get_drug_warnings_by_chemblId` and `OpenTargets_get_drug_adverse_events_by_chemblId` to learn from failed programs

**Scoring adjustments**: Failed clinical program for safety: -3; drug withdrawal: -5; multiple approved drugs: +2

---

## Phase 5: Safety & Toxicity (0-20 pts)

**Objective**: Identify safety risks from expression, genetics, and known adverse events.

**Steps**:
1. Call `OpenTargets_get_target_safety_profile_by_ensemblID` for consolidated safety liabilities
2. Call `GTEx_get_median_gene_expression` with operation="median" and the versioned gencode_id; fall back to unversioned ID if empty
3. Call `HPA_search_genes_by_query` and `HPA_get_comprehensive_gene_details_by_ensembl_id` for expression in critical tissues (heart, liver, kidney, brain, bone marrow = high risk)
4. Reuse mouse model data from `OpenTargets_get_biological_mouse_models_by_ensemblID`; reuse gnomAD constraints from Phase 1
5. For each known drug targeting this protein, call `FDA_get_adverse_reactions_by_drug_name`, `FDA_get_warnings_and_cautions_by_drug_name`, `FDA_get_boxed_warning_info_by_drug_name`, and `FDA_get_contraindications_by_drug_name`
6. Call `OpenTargets_get_target_homologues_by_ensemblID` to identify paralogs that could cause selectivity-driven off-target effects

**Scoring**:
- Expression selectivity (0-5): disease tissue restricted=5, low in critical organs=4, moderate in 1-2=2, high in many=0
- Genetic validation (0-10): mouse KO viable no phenotype=10, mild phenotype=7, concerning=3, lethal=0; no KO data: low pLI=5, high pLI=2
- Known ADRs (0-5): none=5, mild manageable=3, serious=1, black box/withdrawal=0

---

## Phase 6: Pathway Context & Network Analysis

**Objective**: Understand the target's role in biological networks and disease pathways.

**Steps**:
1. Call `Reactome_map_uniprot_to_pathways` (parameter is `id`, not `uniprot_id`), then call `Reactome_get_pathway` and `Reactome_get_pathway_reactions` for top 5 pathways
2. Call `STRING_get_protein_interactions` with protein_ids as an array and species=9606 and confidence_score=0.7
3. Call `intact_get_interactions` for experimental PPI data
4. Call `OpenTargets_get_target_interactions_by_ensemblID` for additional interaction data
5. Call `OpenTargets_get_target_gene_ontology_by_ensemblID` and `GO_get_annotations_for_gene` for functional annotations
6. Call `STRING_functional_enrichment` on the interaction partners for enrichment context

**Report**: List top pathways with Reactome IDs and disease relevance; summarize key interactors and assess pathway redundancy/compensation risk.

---

## Phase 7: Validation Evidence (0-10 pts)

**Objective**: Assess existing functional validation data.

**Steps**:
1. Call `DepMap_get_gene_dependencies` to get CRISPR/RNAi essentiality scores (score < -0.5 = moderately essential, < -1.0 = strongly essential)
2. Call `PubMed_search_articles` searching for CRISPR/siRNA/knockdown/knockout studies in the disease context
3. Call `PubMed_search_articles` searching for biomarker and target engagement studies
4. Call `CTD_get_gene_diseases` for complementary gene-disease associations including animal model data

**Scoring**:
- Functional studies (0-5): CRISPR phenotype=5, siRNA phenotype=4, biochemical assay=3, overexpression only=2, none=0
- Disease models (0-5): PDX response=5, GEMM=4, cell line model=3, in silico only=1, none=0

---

## Phase 8: Structural Insights

**Objective**: Leverage structural biology for druggability and mechanism understanding.

**Steps**:
1. Parse PDB cross-references from the UniProt entry (retrieved in Phase 0); call `pdbe_get_entry_summary`, `pdbe_get_entry_quality`, `pdbe_get_entry_experiment`, and `pdbe_get_entry_molecules` for the top 10 PDB entries
2. Call `get_protein_metadata_by_pdb_id` for additional PDB metadata
3. Call `alphafold_get_prediction` (parameter is `qualifier`, not `uniprot_accession`) and `alphafold_get_summary`
4. Call `ProteinsPlus_predict_binding_sites` on the best PDB structure for pocket druggability scores, volume, and surface area; call `ProteinsPlus_generate_interaction_diagram` for co-crystal structures with ligands
5. Call `InterPro_get_protein_domains` and `InterPro_get_domain_details` for domain architecture

---

## Phase 9: Literature Deep Dive

**Objective**: Comprehensive literature analysis with collision-aware search.

**Steps**:
1. **Collision detection**: Call `PubMed_search_articles` with the gene symbol in title only and check if >20% of results are off-topic; if so, add biology context filters (AND protein OR gene OR receptor OR kinase)
2. Call `PubMed_search_articles` for total publication count (check total_count field), recent publications (2021-2026 date filter), and drug-focused publications
3. Call `EuropePMC_search_articles` for broader database coverage
4. Call `PubMed_search_articles` filtering for review articles to get key landmark papers
5. Call `openalex_search_works` for citation metrics and research trend data

---

## Phase 10: Validation Roadmap (Synthesis)

**Objective**: Generate actionable recommendations based on all evidence.

**Steps**:
1. Calculate the Target Validation Score by summing all 12 sub-component scores from Phases 1-7
2. Assign a Priority Tier (1-4) and GO/NO-GO recommendation based on the total score
3. List 3-5 highest-priority validation experiments, prioritized by unresolved evidence gaps
4. Identify the best available tool compounds for in vitro/in vivo testing
5. Propose a biomarker strategy: predictive biomarkers (patient selection), pharmacodynamic biomarkers (target engagement), and safety biomarkers
6. Enumerate key risks and mitigations, and assess the competitive landscape

---

## Known Gotchas

These are confirmed API quirks that will cause silent errors if ignored:

| Issue | Detail |
|-------|--------|
| `ensembl_lookup_gene` requires `species` | Must pass `species="homo_sapiens"`; response is wrapped in `{status, data, url, content_type}` — access via `result['data']` |
| `OpenTargets_*` parameter casing | Use `ensemblId` (camelCase), NOT `ensemblID` (uppercase D) |
| `OpenTargets_get_publications_*` | Parameter is `entityId`, NOT `ensemblId` |
| `OpenTargets_get_associated_drugs_*` | `size` parameter is REQUIRED — call will fail without it |
| `GTEx_get_median_gene_expression` | `operation="median"` is REQUIRED in addition to `gencode_id`; use versioned ID (e.g., ENSG00000146648.18) first |
| `HPA_get_rna_expression_by_source` | All three parameters required: `gene_name`, `source_type`, `source_name` |
| `PubMed_search_articles` return format | Returns a **plain list** of dicts, NOT `{articles: [...]}` — do not unwrap |
| `UniProt_get_function_by_accession` return format | Returns a **list of strings**, NOT a dict |
| `alphafold_get_prediction` parameter | Use `qualifier`, NOT `uniprot_accession` |
| `drugbank_get_safety_*` | All four parameters required: `query`, `case_sensitive`, `exact_match`, `limit` |
| `Reactome_map_uniprot_to_pathways` | Parameter is `id`, NOT `uniprot_id` |
| `ensembl_get_xrefs` | Parameter is `id`, NOT `gene_id` |
| `MyGene_query_genes` | Parameter is `query`, NOT `q` |
| `ChEMBL_get_target_activities` filter | Use `target_chembl_id__exact` (double underscore) |
| `search_clinical_trials` | `query_term` is REQUIRED |
| `STRING_get_protein_interactions` | `protein_ids` must be an **array**; use `species=9606` |

---

## Fallback Chains

| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `OpenTargets_get_diseases_phenotypes_*` | `CTD_get_gene_diseases` | PubMed search |
| `GTEx_get_median_gene_expression` (versioned) | GTEx (unversioned) | `HPA_search_genes_by_query` |
| `ChEMBL_get_target_activities` | `BindingDB_get_ligands_by_uniprot` | `DGIdb_get_gene_info` |
| `gnomad_get_gene_constraints` | `OpenTargets_get_target_constraint_info_*` | Note as unavailable |
| `Reactome_map_uniprot_to_pathways` | `OpenTargets_get_target_gene_ontology_*` | Use GO only |
| `STRING_get_protein_interactions` | `intact_get_interactions` | `OpenTargets_get_target_interactions_*` |
| `ProteinsPlus_predict_binding_sites` | `alphafold_get_prediction` | Literature pockets |

---

## Modality-Specific Emphasis

- **Small molecule**: Binding pockets, ChEMBL compounds, Lipinski compliance, co-crystal structures, IC50/Ki/Kd data, OpenTargets SM tractability bucket
- **Antibody**: Extracellular domains, cell surface expression, glycosylation, ectodomain structures, surface expression in disease vs normal, OpenTargets AB tractability bucket
- **PROTAC**: Intracellular targets, surface lysines, E3 ligase proximity, full-length structures for linker design, known binders + E3 ligase binders, OpenTargets PROTAC tractability

---

## Report Structure

Create `[TARGET]_[DISEASE]_validation_report.md` immediately, populate sections progressively:

1. Executive Summary (Score, Tier, GO/NO-GO, Key Findings, Critical Risks)
2. Validation Scorecard (table of all 12 sub-components)
3. Target Identity (ID table from Phase 0)
4. Disease Association Evidence (OT, GWAS, gnomAD, literature)
5. Druggability Assessment (tractability, class, structure, probes)
6. Known Modulators & Chemical Matter (approved drugs, ChEMBL, BindingDB, PubChem)
7. Clinical Precedent (FDA, trials, failed programs)
8. Safety & Toxicity Profile (OT safety, expression, KO, ADRs, paralogs)
9. Pathway Context & Network Analysis (Reactome, STRING, GO, redundancy)
10. Validation Evidence (DepMap, functional studies, animal models)
11. Structural Insights (PDB, AlphaFold, pockets, domains)
12. Literature Landscape (metrics, key papers, research trend)
13. Validation Roadmap (experiments, tool compounds, biomarkers, risks)
14. Completeness Checklist (mandatory — all phases, scoring, evidence grades)
15. Data Sources & Methodology

---

## Completeness Checklist (MANDATORY before finalizing)

- [ ] Phase 0: All IDs resolved (Ensembl, UniProt, Entrez, ChEMBL, HGNC)
- [ ] Phase 1: OT + GWAS + gnomAD + literature evidence collected
- [ ] Phase 2: Tractability + class + structure + probes assessed
- [ ] Phase 3: ChEMBL + BindingDB + PubChem + drugs collected
- [ ] Phase 4: FDA + trials + failed programs reviewed
- [ ] Phase 5: OT safety + expression + KO + ADRs + paralogs assessed
- [ ] Phase 6: Reactome + STRING + GO analyzed
- [ ] Phase 7: DepMap + functional literature + animal models reviewed
- [ ] Phase 8: PDB + AlphaFold + pockets + domains analyzed
- [ ] Phase 9: Collision-aware literature search with metrics
- [ ] Phase 10: Score calculated, tier assigned, roadmap generated
- [ ] All 12 score components justified with specific data
- [ ] Evidence grades (T1-T4) assigned to key claims
- [ ] Negative results documented (not left blank)

---

## Tool Quick Reference

For full parameter details see `references/tools.md`.

| Tool | Purpose |
|------|---------|
| `MyGene_query_genes` | Gene symbol to Ensembl/UniProt/Entrez IDs |
| `UniProt_get_entry_by_accession` | Full UniProt entry with PDB cross-references |
| `UniProt_get_function_by_accession` | Protein function (returns list of strings) |
| `ensembl_lookup_gene` | Versioned Ensembl ID (species required) |
| `ensembl_get_xrefs` | Cross-database ID mappings from Ensembl |
| `OpenTargets_get_target_id_description_by_name` | OpenTargets target lookup by name |
| `ChEMBL_search_targets` | Find ChEMBL target ID |
| `OpenTargets_get_diseases_phenotypes_by_target_ensembl` | All disease associations for target |
| `OpenTargets_get_disease_id_description_by_name` | Disease EFO ID lookup |
| `OpenTargets_target_disease_evidence` | Target-disease evidence summary |
| `OpenTargets_get_evidence_by_datasource` | Evidence by data source (GWAS, EVA, etc.) |
| `gwas_get_snps_for_gene` | GWAS SNPs mapped to gene |
| `gwas_search_studies` | GWAS studies for disease trait |
| `gnomad_get_gene_constraints` | pLI, LOEUF, missense z-score |
| `PubMed_search_articles` | PubMed literature search (returns plain list) |
| `OpenTargets_get_publications_by_target_ensemblID` | OT-linked publications (entityId param) |
| `OpenTargets_get_target_tractability_by_ensemblID` | Tractability across modalities |
| `OpenTargets_get_target_classes_by_ensemblID` | Target family classification |
| `Pharos_get_target` | TDL classification (Tclin/Tchem/Tbio/Tdark) |
| `DGIdb_get_gene_druggability` | Druggability category annotations |
| `alphafold_get_prediction` | AlphaFold structure (qualifier param) |
| `alphafold_get_summary` | AlphaFold summary metadata |
| `ProteinsPlus_predict_binding_sites` | Binding pocket prediction and druggability |
| `ProteinsPlus_generate_interaction_diagram` | Ligand-protein interaction diagram |
| `OpenTargets_get_chemical_probes_by_target_ensemblID` | Validated chemical probes |
| `OpenTargets_get_target_enabling_packages_by_ensemblID` | TEPs available for target |
| `ChEMBL_get_target_activities` | Bioactivity data (double-underscore filter) |
| `BindingDB_get_ligands_by_uniprot` | Experimental binding affinities |
| `PubChem_search_assays_by_target_gene` | HTS assay data |
| `PubChem_get_assay_active_compounds` | Active compounds from HTS assay |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | Known drugs (size required) |
| `ChEMBL_search_mechanisms` | Drug-target mechanism annotations |
| `DGIdb_get_gene_info` | Drug-gene interaction database |
| `FDA_get_mechanism_of_action_by_drug_name` | FDA label MoA |
| `FDA_get_indications_by_drug_name` | FDA approved indications |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | DrugBank target annotations |
| `drugbank_get_safety_by_drug_name_or_drugbank_id` | DrugBank safety information |
| `search_clinical_trials` | ClinicalTrials.gov query |
| `OpenTargets_get_drug_warnings_by_chemblId` | Drug safety warnings |
| `OpenTargets_get_drug_adverse_events_by_chemblId` | Drug adverse events |
| `OpenTargets_get_target_safety_profile_by_ensemblID` | Consolidated target safety liabilities |
| `GTEx_get_median_gene_expression` | Tissue expression (operation+gencode_id required) |
| `HPA_search_genes_by_query` | Human Protein Atlas gene search |
| `HPA_get_comprehensive_gene_details_by_ensembl_id` | HPA full gene details |
| `OpenTargets_get_biological_mouse_models_by_ensemblID` | Mouse KO phenotypes |
| `FDA_get_adverse_reactions_by_drug_name` | FDA adverse reaction data |
| `FDA_get_warnings_and_cautions_by_drug_name` | FDA warnings |
| `FDA_get_boxed_warning_info_by_drug_name` | Black box warnings |
| `FDA_get_contraindications_by_drug_name` | Contraindication data |
| `OpenTargets_get_target_homologues_by_ensemblID` | Paralogs for selectivity risk |
| `Reactome_map_uniprot_to_pathways` | Map protein to Reactome pathways (id param) |
| `Reactome_get_pathway` | Pathway details |
| `Reactome_get_pathway_reactions` | Pathway reaction list |
| `STRING_get_protein_interactions` | PPI network (protein_ids array, species=9606) |
| `intact_get_interactions` | Experimental PPI data |
| `OpenTargets_get_target_interactions_by_ensemblID` | OT interaction data |
| `OpenTargets_get_target_gene_ontology_by_ensemblID` | GO annotations from OT |
| `GO_get_annotations_for_gene` | GO term annotations |
| `STRING_functional_enrichment` | Functional enrichment of interaction network |
| `DepMap_get_gene_dependencies` | CRISPR/RNAi essentiality scores |
| `CTD_get_gene_diseases` | Comparative Toxicogenomics Database |
| `pdbe_get_entry_summary` | PDB entry summary |
| `pdbe_get_entry_quality` | PDB structure quality metrics |
| `pdbe_get_entry_experiment` | PDB experimental method details |
| `pdbe_get_entry_molecules` | PDB chain/molecule information |
| `get_protein_metadata_by_pdb_id` | PDB structure metadata |
| `InterPro_get_protein_domains` | Domain architecture from InterPro |
| `InterPro_get_domain_details` | Detailed domain information |
| `EuropePMC_search_articles` | Europe PMC literature search |
| `openalex_search_works` | Citation metrics and research trends |
