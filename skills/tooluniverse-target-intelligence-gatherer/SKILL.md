---
name: tooluniverse-target-intelligence-gatherer
description: Gather comprehensive biological target intelligence from 8 parallel research paths covering protein info, structure, interactions, pathways, expression, variants, drug interactions, and literature. Use when users ask about drug targets, proteins, genes, or need target validation, druggability assessment, or comprehensive target profiling. Triggers include "tell me about target X", "is gene Y druggable", "target profile for Z", or "what do we know about protein P".
---

# Comprehensive Target Intelligence Gatherer

Gather complete target intelligence by exploring 8 parallel research paths simultaneously. Supports targets identified by gene symbol, UniProt accession, Ensembl ID, or gene name.

## When to Use This Skill

Apply when users:
- Ask about a drug target, protein, or gene
- Need target validation or assessment
- Request druggability analysis
- Want comprehensive target profiling
- Ask "what do we know about [target]?"
- Need target-disease associations
- Request safety profile for a target

## Core Strategy

Execute 8 research paths in parallel:

```
Target Query (e.g., "EGFR" or "P00533")
├─ PATH 1: Core Identity (names, IDs, sequence, organism)
├─ PATH 2: Structure & Domains (3D structure, domains, binding sites)
├─ PATH 3: Function & Pathways (GO terms, pathways, biological role)
├─ PATH 4: Protein Interactions (PPI network, complexes)
├─ PATH 5: Expression Profile (tissue expression, single-cell)
├─ PATH 6: Variants & Disease (mutations, clinical significance)
├─ PATH 7: Drug Interactions (known drugs, druggability, safety)
└─ PATH 8: Literature & Research (publications, trends)
```

## Identifier Resolution

First, resolve the target to all needed IDs:

```python
def resolve_target_ids(tu, query):
    """
    Resolve target query to UniProt, Ensembl, and gene symbol.
    Input can be: gene symbol, UniProt accession, Ensembl ID, or name.
    """
    ids = {'query': query, 'uniprot': None, 'ensembl': None, 'symbol': None}
    
    # Detect input type
    if query.startswith('ENSG'):
        ids['ensembl'] = query
        # Map to UniProt
        mapping = tu.tools.UniProt_id_mapping(
            ids=[query], from_db="Ensembl", to_db="UniProtKB"
        )
        if mapping.get('results'):
            ids['uniprot'] = mapping['results'][0].get('to', {}).get('primaryAccession')
    
    elif len(query) == 6 and query[0].isalpha():  # Likely UniProt
        ids['uniprot'] = query
        # Get gene symbol
        entry = tu.tools.UniProt_get_entry_by_accession(accession=query)
        if entry:
            ids['symbol'] = entry.get('genes', [{}])[0].get('geneName', {}).get('value')
    
    else:  # Gene symbol or name
        ids['symbol'] = query.upper()
        # Search UniProt
        results = tu.tools.UniProt_search(query=f'gene:{query} AND organism_id:9606', limit=1)
        if results.get('results'):
            ids['uniprot'] = results['results'][0].get('primaryAccession')
    
    # Get Ensembl ID if missing
    if ids['uniprot'] and not ids['ensembl']:
        mapping = tu.tools.UniProt_id_mapping(
            ids=[ids['uniprot']], from_db="UniProtKB_AC-ID", to_db="Ensembl"
        )
        if mapping.get('results'):
            ids['ensembl'] = mapping['results'][0].get('to')
    
    return ids
```

## Tool Chains for Each Path

### PATH 1: Core Identity

**Objective**: Establish target identity and basic information

**Primary Tools**:
```
UniProt_get_entry_by_accession → Full protein entry
UniProt_get_recommended_name_by_accession → Official name
UniProt_get_alternative_names_by_accession → Aliases
UniProt_get_function_by_accession → Function description
UniProt_get_sequence_by_accession → Protein sequence
UniProt_get_organism_by_accession → Species
```

**Multi-Step Chain**:
```
1. UniProt_get_entry_by_accession(accession)
   └─ Extract: name, function, length, organism
   
2. MyGene_get_gene_annotation(gene_id)
   └─ Extract: gene summary, aliases, genomic location
   
3. ensembl_lookup_gene(gene_id, species)
   └─ Extract: biotype, chromosomal coordinates
```

**Output**: `{name, symbol, aliases, function, sequence_length, organism}`

### PATH 2: Structure & Domains

**Objective**: Understand 3D structure and domain architecture

**Primary Tools**:
```
alphafold_get_prediction → AlphaFold structure (any protein)
get_protein_metadata_by_pdb_id → Experimental structures
InterPro_get_protein_domains → Domain annotations
UniProt_get_ptm_processing_by_accession → PTMs, active sites
```

**Multi-Step Chain**:
```
1. UniProt_get_entry_by_accession(accession)
   └─ Extract: PDB cross-references
   
2. For each PDB ID → get_protein_metadata_by_pdb_id(pdb_id)
   └─ Extract: resolution, method, ligands
   
3. alphafold_get_prediction(uniprot_accession)
   └─ Extract: confidence scores, model URL
   
4. InterPro_get_protein_domains(uniprot_accession)
   └─ Extract: domains, families, sites
```

**Output**: `{pdb_structures[], alphafold_available, domains[], ptms[]}`

### PATH 3: Function & Pathways

**Objective**: Understand biological function and pathway involvement

**Primary Tools**:
```
GO_get_annotations_for_gene → GO terms (BP, MF, CC)
Reactome_map_uniprot_to_pathways → Reactome pathways
kegg_get_gene_info → KEGG pathways
WikiPathways_search → WikiPathways involvement
OpenTargets_get_target_gene_ontology_by_ensemblID → GO via Open Targets
```

**Multi-Step Chain**:
```
1. GO_get_annotations_for_gene(gene_id)
   └─ Extract: Top 5 each: BP, MF, CC terms

2. Reactome_map_uniprot_to_pathways(uniprot_accession)
   └─ Extract: Pathway names and IDs
   
3. kegg_get_gene_info(kegg_gene_id)
   └─ Extract: KEGG pathways
   
4. enrichr_gene_enrichment_analysis([gene_symbol], library="KEGG_2021")
   └─ Extract: Enriched pathways
```

**Output**: `{go_terms: {bp[], mf[], cc[]}, pathways[]}`

### PATH 4: Protein Interactions

**Objective**: Map protein interaction network

**Primary Tools**:
```
STRING_get_protein_interactions → STRING PPI network
intact_get_interactions → IntAct experimental interactions
OpenTargets_get_target_interactions_by_ensemblID → Open Targets PPI
HPA_get_protein_interactions_by_gene → HPA interactions
```

**Multi-Step Chain**:
```
1. STRING_get_protein_interactions(protein_ids=[symbol], species=9606, confidence_score=0.7)
   └─ Extract: Top 20 interactors with scores

2. intact_get_interactions(identifier=uniprot_accession)
   └─ Extract: Experimentally validated interactions
   
3. intact_get_complex_details(complex_id)  # If in complex
   └─ Extract: Complex members and stoichiometry
```

**Output**: `{interactors[], complexes[], interaction_count}`

### PATH 5: Expression Profile

**Objective**: Understand tissue and cell-type expression

**Primary Tools**:
```
GTEx_get_gene_expression → GTEx tissue expression
GTEx_get_median_gene_expression → Median by tissue
HPA_get_rna_expression_by_source → HPA RNA expression
HPA_get_comprehensive_gene_details_by_ensembl_id → Full HPA data
CELLxGENE_get_expression_data → Single-cell expression
```

**Multi-Step Chain**:
```
1. GTEx_get_median_gene_expression(gencode_id)
   └─ Extract: Expression by tissue (TPM)

2. HPA_get_rna_expression_by_source(ensembl_id)
   └─ Extract: Tissue specificity, expression level
   
3. HPA_get_subcellular_location(ensembl_id)
   └─ Extract: Subcellular localization
   
4. If cancer research → HPA_get_cancer_prognostics_by_gene(gene_symbol)
   └─ Extract: Cancer prognosis associations
```

**Output**: `{top_tissues[], tissue_specificity, subcellular_location}`

### PATH 6: Variants & Disease

**Objective**: Understand genetic variation and disease links

**Primary Tools**:
```
UniProt_get_disease_variants_by_accession → Disease variants
clinvar_search_variants → ClinVar variants
gnomad_get_gene → gnomAD population variants
gnomad_get_gene_constraints → Constraint scores (pLI, etc.)
OpenTargets_get_diseases_phenotypes_by_target_ensembl → Disease associations
```

**Multi-Step Chain**:
```
1. gnomad_get_gene_constraints(gene_symbol)
   └─ Extract: pLI, LOEUF, missense Z-score

2. UniProt_get_disease_variants_by_accession(accession)
   └─ Extract: Disease-associated mutations
   
3. clinvar_search_variants(gene=gene_symbol)
   └─ Extract: Pathogenic/likely pathogenic variants
   
4. OpenTargets_get_diseases_phenotypes_by_target_ensembl(ensemblId)
   └─ Extract: Top associated diseases with scores
```

**Output**: `{constraint_scores, disease_variants[], diseases_associated[]}`

### PATH 7: Drug Interactions

**Objective**: Assess druggability and known drugs

**Primary Tools**:
```
DGIdb_get_drug_gene_interactions → Drug-gene interactions
DGIdb_get_gene_druggability → Druggability categories
ChEMBL_search_targets → ChEMBL target info
ChEMBL_get_target_activities → Bioactivity data
OpenTargets_get_associated_drugs_by_target_ensemblID → Approved/trial drugs
OpenTargets_get_target_tractability_by_ensemblID → Tractability assessment
OpenTargets_get_target_safety_profile_by_ensemblID → Safety liabilities
OpenTargets_get_chemical_probes_by_target_ensemblID → Chemical probes
drugbank_get_drug_name_and_description_by_target_name → DrugBank drugs
```

**Multi-Step Chain**:
```
1. OpenTargets_get_target_tractability_by_ensemblID(ensemblID)
   └─ Extract: Small molecule, antibody, other modality tractability

2. DGIdb_get_gene_druggability(genes=[gene_symbol])
   └─ Extract: Druggability categories, drug count
   
3. OpenTargets_get_associated_drugs_by_target_ensemblID(ensemblID)
   └─ Extract: Approved drugs, clinical candidates
   
4. ChEMBL_get_target_activities(target_chembl_id)
   └─ Extract: IC50/Ki/Kd values, potent compounds
   
5. OpenTargets_get_target_safety_profile_by_ensemblID(ensemblID)
   └─ Extract: Safety liabilities, adverse events
```

**Output**: `{is_druggable, drugs[], tractability, safety_flags[]}`

### PATH 8: Literature & Research

**Objective**: Assess research activity and trends

**Primary Tools**:
```
PubMed_search_articles → PubMed publications
EuropePMC_search_articles → Europe PMC articles
OpenTargets_get_publications_by_target_ensemblID → Target publications
proteins_api_get_publications → Protein-specific papers
openalex_search_works → OpenAlex literature
```

**Multi-Step Chain**:
```
1. PubMed_search_articles(query=f'"{gene_symbol}"[Gene Name]', limit=100)
   └─ Extract: Total count, recent papers

2. PubMed_search_articles(query=f'"{gene_symbol}" AND drug', limit=20)
   └─ Extract: Drug-related publications
   
3. Compare 5-year vs 1-year counts
   └─ Calculate: Research trend (increasing/stable/declining)
```

**Output**: `{total_publications, recent_publications, trend}`

## Implementation Pattern

```python
from tooluniverse import ToolUniverse
from concurrent.futures import ThreadPoolExecutor

def gather_target_intelligence(target_query):
    """Main gathering function for target intelligence."""
    tu = ToolUniverse(use_cache=True)
    tu.load_tools()
    
    try:
        # Step 1: Resolve identifiers
        ids = resolve_target_ids(tu, target_query)
        if not ids['uniprot']:
            return {'error': f'Could not resolve target: {target_query}'}
        
        # Step 2: Execute 8 paths in parallel
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                'identity': executor.submit(path_identity, tu, ids),
                'structure': executor.submit(path_structure, tu, ids),
                'function': executor.submit(path_function, tu, ids),
                'interactions': executor.submit(path_interactions, tu, ids),
                'expression': executor.submit(path_expression, tu, ids),
                'variants': executor.submit(path_variants, tu, ids),
                'drugs': executor.submit(path_drugs, tu, ids),
                'literature': executor.submit(path_literature, tu, ids)
            }
            
            findings = {}
            for path_name, future in futures.items():
                try:
                    findings[path_name] = future.result(timeout=120)
                except Exception as e:
                    findings[path_name] = {'status': 'failed', 'error': str(e)}
        
        # Step 3: Synthesize
        return synthesize_target_report(ids, findings)
    finally:
        tu.close()
```

## Report Format Overview

Generate a **comprehensive 14-section report**. For full template and detailed requirements, see [REPORT_FORMAT.md](REPORT_FORMAT.md).

### Required Sections (All Mandatory)

| # | Section | Key Content | Minimum Data |
|---|---------|-------------|--------------|
| 1 | **Executive Summary** | 2-3 sentence overview + bottom line | Must answer: Is this druggable? |
| 2 | **Target Identifiers** | All IDs (UniProt, Ensembl, Entrez, ChEMBL) | All 6 identifier types |
| 3 | **Basic Information** | Name, function, localization | 3-4 sentence function description |
| 4 | **Structural Biology** | PDB structures, AlphaFold, domains | 5+ PDB entries, all domains |
| 5 | **Function & Pathways** | GO terms, pathways | 10 GO terms/category, 10 pathways |
| 6 | **Protein Interactions** | STRING, IntAct, complexes | 15-20 interactors |
| 7 | **Expression Profile** | GTEx, HPA, tissue specificity | Top 10 tissues |
| 8 | **Variants & Disease** | Constraints, ClinVar, disease links | All 4 constraint scores, top 10 diseases |
| 9 | **Druggability** | Tractability, drugs, pipeline, ChEMBL | All modalities, all approved drugs |
| 10 | **Safety Profile** | Liabilities, KO phenotypes, ADEs | All safety flags documented |
| 11 | **Literature** | Publication counts, trends | 5 metrics, 3-5 key papers |
| 12 | **Competitive Landscape** | Market status, differentiation | First-in-class status |
| 13 | **Summary & Recommendations** | Scorecard, strengths, risks | 6-criterion scorecard, 3+ recommendations |
| 14 | **Data Sources** | Tools used, limitations | All tools listed |

### Section Completeness Checklist

Before finalizing any report, verify:

- [ ] All 14 sections present with substantive content
- [ ] Executive summary is 2-3 sentences with clear bottom line
- [ ] All 6 identifier types included (UniProt, Ensembl, Entrez, ChEMBL, HGNC, Symbol)
- [ ] Function description is 3-4 sentences covering molecular function, biological process, cellular role
- [ ] At least 5 PDB structures listed (if available) with resolution and ligand info
- [ ] Complete domain architecture with positions and InterPro IDs
- [ ] Top 5-10 GO terms per category (MF, BP, CC) with evidence codes
- [ ] Top 10 pathways from Reactome/KEGG/WikiPathways
- [ ] Top 15-20 protein interactors with scores and evidence type
- [ ] Expression data for top 10 tissues with TPM values
- [ ] All 4 constraint scores (pLI, LOEUF, missense Z, pRec) with interpretations
- [ ] Top 10 disease associations with scores and EFO IDs
- [ ] All pathogenic/likely pathogenic ClinVar variants listed
- [ ] Tractability assessed for ALL modalities (small molecule, antibody, PROTAC, other)
- [ ] All approved drugs listed with mechanism, indication, approval year
- [ ] Clinical pipeline with phase, indication, trial count
- [ ] All safety liabilities documented with severity
- [ ] 5 publication metrics (total, 5y, 1y, drug-related, clinical)
- [ ] Research trend assessed (increasing/stable/declining)
- [ ] 3-5 notable recent publications with PMIDs
- [ ] Target validation scorecard with all 6 criteria scored 1-5
- [ ] At least 3 prioritized recommendations (HIGH/MEDIUM/LOW)
- [ ] Limitations and data gaps honestly noted

### Quick Reference: What Makes Each Section Comprehensive

**Section 1 (Executive Summary)**: Must answer in 2-3 sentences: What is it? What diseases? Is it druggable? + one-line bottom line recommendation.

**Section 4 (Structure)**: Total PDB count, best resolution, domain table with positions, AlphaFold status, binding sites for drug design.

**Section 8 (Variants)**: All gnomAD constraint scores with interpretations, disease associations with scores, pathogenic variant count, recurrent cancer mutations.

**Section 9 (Druggability)**: Tractability for SM/Ab/PROTAC/other, complete approved drug list, clinical pipeline by phase, ChEMBL activity summary, chemical probes.

**Section 13 (Recommendations)**: 6-criterion scorecard (genetic evidence, expression, function, druggability, safety, competition) each scored 1-5, 3 strengths, 3 challenges, prioritized action items.

## Quick Reference

Common tools by use case:

| Use Case | Primary Tool | Fallback |
|----------|--------------|----------|
| Get protein info | `UniProt_get_entry_by_accession` | `proteins_api_get_protein` |
| ID conversion | `UniProt_id_mapping` | `ensembl_get_xrefs` |
| Gene info | `MyGene_get_gene_annotation` | `ensembl_lookup_gene` |
| PDB structures | `get_protein_metadata_by_pdb_id` | `pdbe_get_entry_summary` |
| AlphaFold | `alphafold_get_prediction` | `alphafold_get_summary` |
| Domains | `InterPro_get_protein_domains` | UniProt entry features |
| GO terms | `GO_get_annotations_for_gene` | `OpenTargets_get_target_gene_ontology_by_ensemblID` |
| Pathways | `Reactome_map_uniprot_to_pathways` | `kegg_get_gene_info` |
| PPI | `STRING_get_protein_interactions` | `intact_get_interactions` |
| Expression | `GTEx_get_median_gene_expression` | `HPA_get_rna_expression_by_source` |
| Variants | `gnomad_get_gene` | `clinvar_search_variants` |
| Constraint | `gnomad_get_gene_constraints` | OpenTargets constraint |
| Druggability | `OpenTargets_get_target_tractability_by_ensemblID` | `DGIdb_get_gene_druggability` |
| Known drugs | `OpenTargets_get_associated_drugs_by_target_ensemblID` | `DGIdb_get_drug_gene_interactions` |
| Safety | `OpenTargets_get_target_safety_profile_by_ensemblID` | Literature search |
| Literature | `PubMed_search_articles` | `EuropePMC_search_articles` |

## Additional Resources

- **Report format template**: [REPORT_FORMAT.md](REPORT_FORMAT.md) - Full 14-section template with detailed requirements
- **Complete tool reference**: [REFERENCE.md](REFERENCE.md) - All 225+ tools organized by category
- **Detailed examples**: [EXAMPLES.md](EXAMPLES.md) - Multi-step workflow examples

## When NOT to Use This Skill

- Simple protein lookup → Use `UniProt_get_entry_by_accession` directly
- Drug information only → Use drug-focused tools
- Disease-centric query → Use disease-intelligence-gatherer skill
- Sequence retrieval → Use sequence-retrieval skill
- Structure download → Use protein-structure-retrieval skill

Use this skill for comprehensive, multi-angle target analysis.
