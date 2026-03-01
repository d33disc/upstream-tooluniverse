# Tool Parameter Reference — Disease Research

Full parameter reference for all tools used in the disease research workflow.
For workflow instructions see [../SKILL.md](../SKILL.md).

All tool calls use `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

---

## 1. Disease Identity & Ontology

### `OSL_get_efo_id_by_disease_name`
Map a disease name to its EFO ID. Primary entry point for the research workflow.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `disease` | string | yes | English disease name (e.g. `"diabetes mellitus"`) |

Returns `efo_id` in underscore format (e.g. `EFO_0000400`) and `name`.

---

### `ols_search_efo_terms`
Search the EFO ontology by keyword. Use as fallback if `OSL_get_efo_id_by_disease_name` returns nothing.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search term |
| `rows` | integer | no | Max results (default 10) |

Returns terms with `iri`, `obo_id`, `label`, and `description`.

---

### `ols_get_efo_term`
Get full details for a single EFO term including synonyms and hierarchy.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `obo_id` | string | yes | OBO colon format (e.g. `"EFO:0000400"`) — NOT underscore format |

Returns `synonyms`, `description`, `has_children`, `is_obsolete`.

---

### `ols_get_efo_term_children`
Get disease subtypes (child nodes in the ontology tree).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `obo_id` | string | yes | OBO colon format |
| `size` | integer | no | Max children to return (default 10) |

Returns list of child terms with `obo_id` and `label`.

---

### `OpenTargets_get_disease_id_description_by_name`
Search OpenTargets for a disease by name.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `diseaseName` | string | yes | Disease name (e.g. `"Diabetes Mellitus"`) |

Returns `id` (underscore EFO format), `name`, `description`.

---

### `umls_search_concepts`
Search UMLS for medical concepts. Requires `UMLS_API_KEY` environment variable.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search term |
| `sabs` | string | no | Source vocabulary filter (e.g. `"SNOMEDCT_US"`, `"ICD10CM"`) |
| `pageSize` | integer | no | Results per page (default 25) |

Returns `CUI`, `name`, `source`. Fails silently if API key missing — note as Data Gap.

---

### `umls_get_concept_details`
Get UMLS concept definitions and semantic types by CUI.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cui` | string | yes | UMLS CUI (e.g. `"C0011849"`) |

Returns definitions and semantic types.

---

### `icd_search_codes`
Search ICD-10 or ICD-11 codes.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search term |
| `version` | string | no | `"ICD10CM"` (default) or `"ICD11"` |

Returns ICD codes with descriptions.

---

### `snomed_search_concepts`
Search SNOMED CT concepts.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search term |

Returns SNOMED concepts with codes.

---

## 2. Clinical Manifestations & Phenotypes

### `OpenTargets_get_associated_phenotypes_by_disease_efoId`
Get HPO phenotypes associated with a disease.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `efoId` | string | yes | EFO ID in underscore format (e.g. `"EFO_0000384"`) |

Returns `phenotypeHPO` list (id, name, description) and `phenotypeEFO`.

---

### `get_HPO_ID_by_phenotype`
Convert a symptom name to HPO ID (Monarch Initiative).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Phenotype description (e.g. `"seizure"`) |
| `limit` | integer | no | Max results (default 5) |

Returns list of matching HPO IDs.

---

### `get_phenotype_by_HPO_ID`
Get phenotype details from an HPO ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | yes | HPO ID with colon format (e.g. `"HP:0001250"`) |

Returns phenotype details including description and synonyms.

---

### `get_joint_associated_diseases_by_HPO_ID_list`
Find diseases sharing a set of phenotypes (differential diagnosis support).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `HPO_ID_list` | array of strings | yes | List of HPO IDs |
| `limit` | integer | no | Max results (default 20) |

Returns diseases associated with all provided phenotypes.

---

### `MedlinePlus_search_topics_by_keyword`
Search MedlinePlus consumer health topics.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `term` | string | yes | Search keyword |
| `db` | string | no | `"healthTopics"` (default) |
| `rettype` | string | no | `"topic"` |

Returns topics with `title`, `summary`, `url`.

---

### `MedlinePlus_get_genetics_condition_by_name`
Get genetics condition information from MedlinePlus Genetics.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `condition` | string | yes | URL slug form — use hyphens, not spaces (e.g. `"alzheimer-disease"`) |

Returns description, associated genes, and synonyms. Convert "Alzheimer disease" to `alzheimer-disease` before calling.

---

### `MedlinePlus_connect_lookup_by_code`
Look up MedlinePlus information by clinical code (ICD-10, LOINC, etc.).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cs` | string | yes | Code system OID. For ICD-10-CM use `"2.16.840.1.113883.6.90"` |
| `c` | string | yes | The code value (e.g. `"E11.9"` for type 2 diabetes) |

Returns relevant MedlinePlus health information. Note: `cs` and `c` are separate parameters.

---

## 3. Genetic & Molecular Basis

### `OpenTargets_get_associated_targets_by_disease_efoId`
Get gene-disease associations with evidence scores.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `efoId` | string | yes | EFO ID in underscore format |

Returns `target.id` (Ensembl), `target.approvedSymbol`, overall `score`.

---

### `OpenTargets_get_diseases_phenotypes_by_target_ensembl`
Reverse lookup: find all diseases associated with a gene.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ensemblId` | string | yes | Ensembl gene ID (e.g. `"ENSG00000141510"`) |

Returns diseases associated with the gene.

---

### `OpenTargets_target_disease_evidence`
Get detailed evidence for a specific gene-disease association pair.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `efoId` | string | yes | EFO ID in underscore format |
| `ensemblId` | string | yes | Ensembl gene ID |

Returns evidence breakdown by data type and mutation data.

---

### `clinvar_search_variants`
Search ClinVar for variants by disease name or gene.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `condition` | string | no | Disease name (use when searching by disease) |
| `gene` | string | no | Gene symbol (use instead of condition for gene-based search) |
| `max_results` | integer | no | Max results (default 20) |

Returns variant IDs and total count.

---

### `clinvar_get_variant_details`
Get full ClinVar variant details by variant ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `variant_id` | string | yes | ClinVar variant ID |

Returns full variant information including genomic coordinates.

---

### `clinvar_get_clinical_significance`
Get pathogenicity classification for a ClinVar variant.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `variant_id` | string | yes | ClinVar variant ID |

Returns clinical significance (Pathogenic / Likely pathogenic / VUS / Benign).

---

### `gwas_search_associations`
Search GWAS Catalog associations by disease trait label.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `disease_trait` | string | yes | Trait label — must match GWAS Catalog label closely; try synonyms if sparse |
| `size` | integer | no | Max results (default 20) |

Returns associations with `p_value`, `snp_allele`, `mapped_genes`.

---

### `gwas_get_variants_for_trait`
Get variants associated with a GWAS Catalog trait.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `disease_trait` | string | yes | Trait label |
| `size` | integer | no | Max results |

Returns variants with `rs_id`, chromosome location, `mapped_genes`.

---

### `gwas_get_associations_for_trait`
Get GWAS associations sorted by statistical significance.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `disease_trait` | string | yes | Trait label |
| `size` | integer | no | Max results |

Returns associations sorted by p-value ascending.

---

### `gwas_get_studies_for_trait`
Get GWAS study metadata for a trait.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `disease_trait` | string | yes | Trait label |
| `size` | integer | no | Max results |

Returns study accession, sample sizes, populations.

---

### `gwas_get_snp_by_id`
Get SNP details from GWAS Catalog by rs ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `rs_id` | string | yes | rs ID (e.g. `"rs1234"`) |

Returns SNP details, chromosome location, alleles.

---

### `gwas_get_associations_for_snp`
Get all trait associations for a SNP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `rs_id` | string | yes | rs ID |
| `size` | integer | no | Max results |

Returns traits associated with the SNP.

---

### `gwas_get_snps_for_gene`
Get SNPs mapped to a gene in GWAS Catalog.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mapped_gene` | string | yes | Gene symbol (e.g. `"BRCA1"`) |
| `size` | integer | no | Max results |

Returns SNPs in or near the gene.

---

### `GWAS_search_associations_by_gene`
Search GWAS associations by gene name.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene_name` | string | yes | Gene symbol |
| `size` | integer | no | Max results |

Returns GWAS associations mapped to the gene.

---

### `gnomad_get_variant_frequency`
Get population allele frequencies from gnomAD.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `variant` | string | yes | Variant in `chr-pos-ref-alt` format (e.g. `"1-55505647-G-T"`) |

Returns allele frequencies across gnomAD population groups. rsID is not accepted — convert from ClinVar or GWAS data first.

---

## 4. Treatment Landscape

### `OpenTargets_get_associated_drugs_by_disease_efoId`
Get drugs associated with a disease in OpenTargets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `efoId` | string | yes | EFO ID in underscore format |
| `size` | integer | no | Max results (default 100) |

Returns drug name, ChEMBL ID, phase, status, mechanism, and molecular target.

---

### `OpenTargets_get_drug_chembId_by_generic_name`
Get ChEMBL ID from a drug's generic name.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drugName` | string | yes | Generic drug name (e.g. `"Aspirin"`) |

Returns `chemblId`, `name`, `description`.

---

### `OpenTargets_get_drug_mechanisms_of_action_by_chemblId`
Get mechanism of action for a drug.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chemblId` | string | yes | ChEMBL ID (e.g. `"CHEMBL25"`) |

Returns `mechanism`, `actionType`, list of target IDs.

---

### `search_clinical_trials`
Search ClinicalTrials.gov.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `condition` | string | no | Disease or condition name |
| `intervention` | string | no | Drug or intervention name |
| `query_term` | string | no | Free-text query (e.g. `"Phase 3"`) |
| `status` | string | no | Trial status (e.g. `"Recruiting"`, `"Completed"`) |
| `pageSize` | integer | no | Results per page (default 20) |

Returns NCT ID, `brief_title`, `status`, `phase`.

---

### `get_clinical_trial_descriptions`
Get full or brief trial descriptions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nct_ids` | array of strings | yes | List of NCT IDs (always an array, even for one trial) |
| `description_type` | string | no | `"full"` or `"brief"` |

---

### `get_clinical_trial_conditions_and_interventions`
Get conditions and intervention arms for trials.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nct_ids` | array of strings | yes | List of NCT IDs |
| `condition_and_intervention` | string | no | Filter string (leave empty for all) |

Returns `conditions`, `arm_groups`, `interventions`.

---

### `get_clinical_trial_eligibility_criteria`
Get eligibility criteria (inclusion/exclusion).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nct_ids` | array of strings | yes | List of NCT IDs |
| `eligibility_criteria` | string | no | Filter string |

Returns `eligibility_criteria`, `sex`, age range.

---

### `get_clinical_trial_outcome_measures`
Get primary and secondary outcome measures.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nct_ids` | array of strings | yes | List of NCT IDs |
| `outcome_measures` | string | no | `"primary"`, `"secondary"`, or empty for all |

---

### `extract_clinical_trial_outcomes`
Extract efficacy results from completed trials.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nct_ids` | array of strings | yes | List of NCT IDs |
| `outcome_measure` | string | no | Specific measure (e.g. `"overall survival"`) |

Returns detailed outcome results including statistical data.

---

### `extract_clinical_trial_adverse_events`
Extract safety data from trial results reports.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nct_ids` | array of strings | yes | List of NCT IDs |
| `organ_systems` | array of strings | no | MedDRA organ system filter (e.g. `["Cardiac Disorders"]`) |
| `adverse_event_type` | string | no | `"serious"` or `"other"` |

---

### `GtoPdb_list_diseases`
Search IUPHAR/BPS Guide to Pharmacology diseases.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | no | Disease name filter |
| `limit` | integer | no | Max results |

Returns diseases with internal IDs, OMIM references, and DOID.

---

### `GtoPdb_get_disease`
Get GtoPdb disease details including pharmacological targets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `disease_id` | integer | yes | GtoPdb internal disease ID (from `GtoPdb_list_diseases`) |

Returns associated pharmacological targets, ligands, and description.

---

## 5. Biological Pathways & Mechanisms

### `Reactome_get_diseases`
Get all disease-associated pathway entries in Reactome.

No parameters. Returns all disease pathways with DOID annotations. Filter the response locally by disease name or DOID.

---

### `Reactome_get_pathway`
Get pathway details.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `stId` | string | yes | Reactome stable ID (e.g. `"R-HSA-73817"`) |

Returns pathway metadata, events, and literature references.

---

### `Reactome_get_pathway_reactions`
Get reactions within a pathway.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `stId` | string | yes | Reactome stable ID |

Returns list of reactions and subpathways.

---

### `Reactome_map_uniprot_to_pathways`
Get pathways containing a specific protein.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | yes | UniProt accession (e.g. `"P04637"`) |

Returns pathways that contain the protein.

---

### `Reactome_map_uniprot_to_reactions`
Get reactions involving a specific protein.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | yes | UniProt accession |

Returns reactions involving the protein.

---

### `Reactome_list_top_pathways`
List the top-level pathway hierarchy.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `species` | string | no | Species name (default `"Homo sapiens"`) |

---

### `humanbase_ppi_analysis`
Tissue-specific protein-protein interaction analysis.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene_list` | array of strings | yes | Gene symbols. Keep to 10 or fewer for reasonable performance. |
| `tissue` | string | yes | Tissue name (e.g. `"brain"`, `"liver"`, `"kidney"`) |
| `max_node` | integer | no | Max nodes in the returned network (default 10) |
| `interaction` | string | no | Interaction type filter (e.g. `"co-expression"`) |
| `string_mode` | boolean | no | Include STRING database data |

Returns PPI network graph and GO biological process annotations.

---

### `gtex_get_expression_by_gene`
Get tissue-specific gene expression from GTEx.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene` | string | yes | Gene symbol or Ensembl ID |

Returns expression levels (TPM) across tissues.

---

### `HPA_get_protein_expression`
Get protein expression from the Human Protein Atlas.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene` | string | yes | Gene symbol (e.g. `"TP53"`) |

Returns protein expression by tissue and subcellular localization.

---

### `geo_search_datasets`
Search NCBI GEO for gene expression datasets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Disease or condition term |
| `max_results` | integer | no | Max results (default 20) |

Returns GEO dataset accessions (GSE IDs) and descriptions.

---

## 6. Literature & Research

### `PubMed_search_articles`
Search PubMed biomedical literature.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | PubMed query string. Wrap multi-word terms in double quotes (e.g. `'"Alzheimer disease" AND biomarker'`). Supports MeSH terms and field tags. |
| `limit` | integer | no | Max PMIDs returned |
| `years` | integer | no | Restrict to last N years |

Returns list of PMIDs. Useful query patterns:
- `'"Disease Name"[MeSH] AND "Drug Therapy"[MeSH]'`
- `'Disease[Title] AND biomarker[Title]'`
- `'"disease" NOT "related disease" AND treatment'`

---

### `PubMed_get_article`
Get article metadata by PMID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pmid` | string | yes | PubMed ID |

Returns `title`, `abstract`, `authors`, `journal`, `year`.

---

### `PubMed_get_related`
Get articles related to a given paper.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pmid` | string | yes | PubMed ID |
| `limit` | integer | no | Max results |

Returns related PMIDs.

---

### `PubMed_get_cited_by`
Get articles citing a given paper.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pmid` | string | yes | PubMed ID |
| `limit` | integer | no | Max results |

Returns PMIDs of citing articles.

---

### `OpenTargets_get_publications_by_disease_efoId`
Get publications linked to a disease in OpenTargets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `efoId` | string | yes | EFO ID in underscore format |

Returns disease-related publications with metadata.

---

### `OpenTargets_get_publications_by_target_ensemblID`
Get publications linked to a gene target in OpenTargets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ensemblId` | string | yes | Ensembl gene ID |

Returns target-related publications.

---

### `openalex_search_works`
Search OpenAlex for scholarly works with institutional metadata.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search query |
| `limit` | integer | no | Max results (default 50) |

Returns works with `authors`, `institutions`, `citation_count`, `topics`.

---

### `europe_pmc_search_abstracts`
Search Europe PMC literature database.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search query |
| `limit` | integer | no | Max results |

Returns abstracts and metadata from Europe PMC.

---

### `semantic_scholar_search_papers`
Search Semantic Scholar with citation network data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search query |
| `limit` | integer | no | Max results |

Returns papers with `citation_count` and influential citation data.

---

## 7. Similar Diseases

### `OpenTargets_get_similar_entities_by_disease_efoId`
Find diseases, targets, and drugs similar to a given disease.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `efoId` | string | yes | EFO ID in underscore format |
| `threshold` | float | no | Minimum similarity score 0–1. Default 0.5; use 0.3 for broader results. |
| `size` | integer | no | Max results |

Returns similar entities with similarity scores and shared gene counts.

---

## 8. Cancer-Specific (CIViC)

All CIViC tools use internal numeric IDs. Always resolve IDs via search tools before calling detail endpoints.

### `civic_search_diseases`
List all diseases represented in the CIViC clinical interpretation knowledgebase.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | no | Max results |

---

### `civic_search_genes`
Search CIViC for cancer genes.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Gene symbol (e.g. `"BRAF"`) |
| `limit` | integer | no | Max results |

Returns CIViC internal `id`, `name`, `description` for each gene.

---

### `civic_get_variants_by_gene`
Get clinical variants for a CIViC gene.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gene_id` | integer | yes | CIViC internal gene ID (from `civic_search_genes`) |
| `limit` | integer | no | Max results |

---

### `civic_get_variant`
Get detailed information for a CIViC variant.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `variant_id` | integer | yes | CIViC internal variant ID |

---

### `civic_get_evidence_item`
Get clinical evidence for a variant-disease-therapy association.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `evidence_id` | integer | yes | CIViC internal evidence ID |

Returns evidence description, level (A–E), and type (Predictive/Prognostic/Diagnostic).

---

### `civic_search_therapies`
List therapies in the CIViC knowledgebase.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | no | Max results |

---

### `civic_search_molecular_profiles`
Search biomarker molecular profiles in CIViC.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | no | Max results |

---

## 9. Pharmacology (GtoPdb)

### `GtoPdb_get_targets`
Get pharmacological targets filtered by type.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target_type` | string | no | E.g. `"GPCR"`, `"ion channel"`, `"nuclear receptor"`, `"kinase"` |
| `limit` | integer | no | Max results |

Returns targets with associated drugs and ligands.

---

### `GtoPdb_get_target`
Get detailed information for a pharmacological target.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target_id` | integer | yes | GtoPdb internal target ID |

Returns detailed target information including approved drugs.

---

### `GtoPdb_get_target_interactions`
Get ligand-target interactions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target_id` | integer | yes | GtoPdb internal target ID |
| `action_type` | string | no | E.g. `"Agonist"`, `"Antagonist"`, `"Inhibitor"` |

Returns interactions with affinity values (Ki, IC50, etc.).

---

### `GtoPdb_search_interactions`
Search drug-target interactions across GtoPdb.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `approved_only` | boolean | no | Restrict to approved drugs only |
| `limit` | integer | no | Max results |

---

### `GtoPdb_list_ligands`
List ligands/drugs in GtoPdb.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ligand_type` | string | no | E.g. `"Approved"`, `"Synthetic organic"`, `"Peptide"` |
| `limit` | integer | no | Max results |

---

### `GtoPdb_get_ligand`
Get full details for a ligand including structure and targets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ligand_id` | integer | yes | GtoPdb internal ligand ID |

Returns SMILES string, molecular properties, and known targets.

---

## 10. Protein Information (UniProt)

### `UniProt_get_disease_variants_by_accession`
Get disease-associated variants for a protein.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `accession` | string | yes | UniProt accession (e.g. `"P05067"` for APP) |

Returns disease variants annotated on the protein.

---

### `UniProt_get_function_by_accession`
Get protein function description from UniProt.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `accession` | string | yes | UniProt accession |

Returns protein function description and catalytic activity.

---

### `UniProt_get_subcellular_location_by_accession`
Get protein subcellular localization from UniProt.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `accession` | string | yes | UniProt accession |

Returns cellular compartment and topology data.

---

## 11. Adverse Events & Safety

### `OpenTargets_get_drug_warnings_by_chemblId`
Get drug safety warnings from OpenTargets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chemblId` | string | yes | ChEMBL ID |

Returns `warningType`, `description`, `toxicityClass`, `references`.

---

### `OpenTargets_get_drug_blackbox_status_by_chembl_ID`
Check if a drug has been withdrawn or carries a black-box warning.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chemblId` | string | yes | ChEMBL ID |

Returns `hasBeenWithdrawn` (boolean) and `blackBoxWarning` (boolean).

---

### `FAERS_count_reactions_by_drug_event`
Count FDA adverse event reports for a drug-event pair from FAERS.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drug` | string | yes | Drug name as reported in FAERS (may differ from generic name) |
| `event` | string | yes | Adverse event MedDRA term |

Returns count of matching FAERS report records.

---

### `AdverseEventPredictionQuestionGenerator`
Generate structured safety prediction questions for a drug-disease pair.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `disease_name` | string | yes | Disease name |
| `drug_name` | string | yes | Drug name |

Returns structured safety questions for downstream clinical analysis.

---

### `AdverseEventICDMapper`
Map free-text adverse event descriptions to ICD-10 codes.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source_text` | string | yes | Free-text description of adverse event(s) |

Returns ICD-10 codes matching the described events.

---

## ID Mapping Quick Reference

| Goal | Tool |
|------|------|
| Disease name → EFO ID | `OSL_get_efo_id_by_disease_name` |
| Disease name → EFO ID (alt) | `OpenTargets_get_disease_id_description_by_name` |
| Drug name → ChEMBL ID | `OpenTargets_get_drug_chembId_by_generic_name` |
| Symptom text → HPO ID | `get_HPO_ID_by_phenotype` |
| HPO ID list → disease list | `get_joint_associated_diseases_by_HPO_ID_list` |
| Gene symbol → disease list | `OpenTargets_get_diseases_phenotypes_by_target_ensembl` |
| UniProt ID → pathways | `Reactome_map_uniprot_to_pathways` |
| SNP rs ID → trait list | `gwas_get_associations_for_snp` |
| Gene symbol → GWAS SNPs | `gwas_get_snps_for_gene` |
| CIViC gene name → CIViC ID | `civic_search_genes` |
| GtoPdb disease name → ID | `GtoPdb_list_diseases` |
