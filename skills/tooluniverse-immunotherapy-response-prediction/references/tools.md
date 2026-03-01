# Immunotherapy Response Prediction - Detailed Tool Reference

Complete parameter signatures and response shapes for every tool used in this skill.
Agents should consult this file when the abbreviated table in SKILL.md is not enough.

---

## Tool Parameters by Phase

### Phase 1: Input Standardization & Cancer Context

| Tool | Parameters | Response Shape | Purpose |
|------|-----------|----------------|---------|
| `OpenTargets_get_disease_id_description_by_name` | `diseaseName` (string) | `{data: {search: {hits: [{id, name, description}]}}}` | Resolve cancer name to EFO ID |
| `MyGene_query_genes` | `query` (NOT `q`) | `{hits: [{_id, symbol, name, ensembl: {gene}}]}` | Resolve gene symbol to Ensembl/Entrez IDs |
| `ensembl_lookup_gene` | `gene_id`, `species='homo_sapiens'` (BOTH required) | `{data: {id, display_name, description, biotype}}` | Gene metadata lookup |

### Phase 2: TMB Analysis

| Tool | Parameters | Response Shape | Purpose |
|------|-----------|----------------|---------|
| `fda_pharmacogenomic_biomarkers` | `drug_name` (string), `biomarker` (string, optional), `limit` (int) | `{count, shown, results: [{Drug, Biomarker, TherapeuticArea, LabelingSection}]}` | Check FDA TMB-H / biomarker approvals |

### Phase 3: Neoantigen Analysis

| Tool | Parameters | Response Shape | Purpose |
|------|-----------|----------------|---------|
| `UniProt_get_function_by_accession` | `accession` (UniProt ID) | List of strings | Protein function — assess neoantigen domain importance |
| `UniProt_get_disease_variants_by_accession` | `accession` (UniProt ID) | Disease-associated variant list | Known pathogenic variants |
| `iedb_search_epitopes` | `organism_name` (e.g. `'homo sapiens'`), `source_antigen_name` (protein name) | `{status, data, count}` | Known T-cell epitopes for antigen |
| `EnsemblVEP_annotate_rsid` | `variant_id` (NOT `rsid`) | VEP annotation object with SIFT/PolyPhen scores | Predict functional impact of variant |

### Phase 4: MSI/MMR Status Assessment

| Tool | Parameters | Response Shape | Purpose |
|------|-----------|----------------|---------|
| `fda_pharmacogenomic_biomarkers` | `biomarker='Microsatellite Instability'`, `limit` | Same as Phase 2 above | FDA MSI-H drug approvals |

### Phase 5: PD-L1 Expression Analysis

| Tool | Parameters | Response Shape | Purpose |
|------|-----------|----------------|---------|
| `HPA_get_cancer_prognostics_by_gene` | `gene_name` (e.g. `'CD274'`) | Cancer-type prognostic associations | PD-L1 baseline prognostic context |
| `HPA_get_rna_expression_by_source` | `gene_name`, `source_type`, `source_name` (ALL 3 required) | RNA expression level per tissue/cancer | Baseline expression reference |

### Phase 6: Immune Microenvironment Profiling

| Tool | Parameters | Response Shape | Purpose |
|------|-----------|----------------|---------|
| `HPA_get_cancer_prognostics_by_gene` | `gene_name` (e.g. `'CD8A'`, `'IFNG'`) | Prognostic data by cancer | Immune infiltration proxies |
| `enrichr_gene_enrichment_analysis` | `gene_list` (array of strings, REQUIRED), `libs` (array of strings, REQUIRED) | Enrichment result per library | Immune pathway enrichment. Key libs: `KEGG_2021_Human`, `Reactome_2022` |

### Phase 7: Mutation-Based Predictors

| Tool | Parameters | Response Shape | Purpose |
|------|-----------|----------------|---------|
| `cBioPortal_get_mutations` | `study_id` (string), `gene_list` (STRING not array) | `{data: [{proteinChange, mutationType, studyId, ...}]}` | Mutation frequency in cancer cohort |
| `OpenTargets_get_associated_drugs_by_disease_efoId` | `efoId` (string), `size` (int) | `{data: {disease: {knownDrugs: {count, rows}}}}` | ICI drugs associated with cancer EFO |

### Phase 8: Clinical Evidence & ICI Options

| Tool | Parameters | Response Shape | Purpose |
|------|-----------|----------------|---------|
| `FDA_get_indications_by_drug_name` | `drug_name` (string), `limit` (int) | `{meta, results}` | Cancer-specific FDA-approved indications |
| `FDA_get_mechanism_of_action_by_drug_name` | `drug_name`, `limit` | `{meta, results}` | Drug mechanism of action |
| `FDA_get_clinical_studies_info_by_drug_name` | `drug_name`, `limit` | `{meta, results}` | Clinical study summary |
| `FDA_get_adverse_reactions_by_drug_name` | `drug_name`, `limit` | `{meta, results}` | Adverse reaction profile |
| `FDA_get_boxed_warning_info_by_drug_name` | `drug_name`, `limit` | `{meta, results}` or NOT_FOUND | Black-box warnings |
| `FDA_get_warnings_by_drug_name` | `drug_name`, `limit` | `{meta, results}` | General warnings |
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | `chemblId` (string) | `{data: {drug: {mechanismsOfAction: {rows}}}}` | Molecular target confirmation |
| `OpenTargets_get_approved_indications_by_drug_chemblId` | `chemblId` | Approved indications list | Cross-reference approvals |
| `OpenTargets_get_drug_description_by_chemblId` | `chemblId` | Drug description text | Drug summary |
| `OpenTargets_get_associated_targets_by_drug_chemblId` | `chemblId` | Drug target list | Drug targets |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | `query`, `case_sensitive` (bool), `exact_match` (bool), `limit` (ALL 4 required) | Drug info dict | DrugBank drug details |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` (ALL 4 required) | Target list | DrugBank targets |
| `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` (ALL 4 required) | Pharmacology dict | PK/PD data |
| `drugbank_get_indications_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` (ALL 4 required) | Indication list | DrugBank indications |
| `clinical_trials_search` | `action='search_studies'`, `condition` (string), `intervention` (string), `limit` (int) | `{total_count, studies: [{nctId, title, status, conditions}]}` | Active ICI trials for cancer |
| `PubMed_search_articles` | `query` (string), `max_results` (int) | Plain list of dicts with pmid, title, etc. | Literature evidence |

### Phase 9: Resistance Risk Assessment

| Tool | Parameters | Response Shape | Purpose |
|------|-----------|----------------|---------|
| `civic_search_evidence_items` | `therapy_name` (string), `disease_name` (string, optional) | `{data: {evidenceItems: {nodes}}}` | CIViC resistance/predictive evidence. Note: filtering may be imprecise |
| `civic_search_variants` | `name` (variant name), `gene_name` | `{data: {variants: {nodes}}}` | CIViC variant records. Returns many unrelated variants |
| `civic_get_variants_by_gene` | `gene_id` (CIViC numeric ID — NOT Entrez) | Variant list for gene | CIViC gene-level variants |
| `civic_search_assertions` | `therapy_name`, `disease_name` | `{data: {assertions: {nodes}}}` | CIViC clinical assertions |
| `civic_search_therapies` | `name` (string) | Therapy search results | Confirm therapy name in CIViC |
| `gnomad_get_gene_constraints` | `gene_symbol` (string) | Gene constraint metrics (pLI, LOEUF) | Gene essentiality assessment |

---

## Key ICI Drug Reference

| Drug | ChEMBL ID | DrugBank ID | Target | Type |
|------|-----------|-------------|--------|------|
| Pembrolizumab (Keytruda) | CHEMBL3137343 | DB09037 | PD-1 (PDCD1) | IgG4 mAb |
| Nivolumab (Opdivo) | CHEMBL2108738 | DB09035 | PD-1 (PDCD1) | IgG4 mAb |
| Atezolizumab (Tecentriq) | CHEMBL3707227 | DB11595 | PD-L1 (CD274) | IgG1 mAb |
| Durvalumab (Imfinzi) | CHEMBL3301587 | DB11714 | PD-L1 (CD274) | IgG1 mAb |
| Ipilimumab (Yervoy) | CHEMBL1789844 | DB06186 | CTLA-4 | IgG1 mAb |
| Avelumab (Bavencio) | CHEMBL3833373 | DB11945 | PD-L1 (CD274) | IgG1 mAb |
| Cemiplimab (Libtayo) | CHEMBL4297723 | DB14716 | PD-1 (PDCD1) | IgG4 mAb |
| Dostarlimab (Jemperli) | — | — | PD-1 (PDCD1) | IgG4 mAb |
| Tremelimumab (Imjudo) | — | — | CTLA-4 | IgG2 mAb |

---

## Key Gene IDs

| Gene | Ensembl ID | Entrez ID | UniProt | Role |
|------|-----------|-----------|---------|------|
| PDCD1 (PD-1) | ENSG00000188389 | 5133 | Q15116 | ICI target |
| CD274 (PD-L1) | ENSG00000120217 | 29126 | Q9NZQ7 | ICI target |
| CTLA4 | ENSG00000163599 | 1493 | P16410 | ICI target |
| LAG3 | ENSG00000089692 | 3902 | P18627 | Immune checkpoint |
| HAVCR2 (TIM-3) | ENSG00000135077 | 84868 | Q8TDQ0 | Immune checkpoint |
| TIGIT | ENSG00000181847 | 201633 | Q495A1 | Immune checkpoint |
| BRAF | ENSG00000157764 | 673 | P15056 | Driver mutation |
| STK11 | ENSG00000118046 | 6794 | Q15831 | Resistance |
| PTEN | ENSG00000284792 | 5728 | P60484 | Resistance |
| JAK1 | ENSG00000162434 | 3716 | P23458 | Resistance |
| JAK2 | ENSG00000096968 | 3717 | O60674 | Resistance |
| B2M | ENSG00000166710 | 567 | P61769 | Resistance |
| KEAP1 | ENSG00000079999 | 9817 | Q14145 | Resistance |
| MDM2 | ENSG00000135679 | 4193 | Q00987 | Hyperprogression |
| POLE | ENSG00000177084 | 5426 | Q07864 | Sensitivity / ultramutation |
| POLD1 | ENSG00000062822 | 5424 | P28340 | Sensitivity |
| PBRM1 | ENSG00000163932 | 55193 | Q86U86 | Sensitivity (RCC) |
| MLH1 | ENSG00000076242 | 4292 | P40692 | MMR |
| MSH2 | ENSG00000095002 | 4436 | P43246 | MMR |
| MSH6 | ENSG00000116062 | 2956 | P52701 | MMR |
| PMS2 | ENSG00000122512 | 5395 | P54278 | MMR |
| EPCAM | ENSG00000119888 | 4072 | P16422 | MMR (silences MSH2) |

---

## Common Parameter Mistakes

| Wrong | Correct | Tool |
|-------|---------|------|
| `q='BRAF'` | `query='BRAF'` | `MyGene_query_genes` |
| `rsid='rs...'` | `variant_id='rs...'` | `EnsemblVEP_annotate_rsid` |
| `gene_list=['BRAF']` (array) | `gene_list='BRAF'` (string) | `cBioPortal_get_mutations` |
| 3 params | ALL 4 params: `query`, `case_sensitive`, `exact_match`, `limit` | All `drugbank_*` tools |
| `ensembl_lookup_gene(gene_id=...)` no species | Add `species='homo_sapiens'` | `ensembl_lookup_gene` |
| `drugName` | `diseaseName` | `OpenTargets_get_disease_id_description_by_name` |
| Entrez gene ID | CIViC numeric gene ID | `civic_get_variants_by_gene` |
| `cBioPortal_get_cancer_studies(keyword=...)` | Call with no params | `cBioPortal_get_cancer_studies` |
