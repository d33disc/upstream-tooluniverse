---
name: tooluniverse-target-research
description: Gather comprehensive biological target intelligence from 9 parallel research paths covering protein info, structure, interactions, pathways, expression, variants, drug interactions, and literature. Features collision-aware searches, evidence grading (T1-T4), explicit Open Targets coverage, and mandatory completeness auditing. Use when users ask about drug targets, proteins, genes, or need target validation, druggability assessment, or comprehensive target profiling.
---

# Comprehensive Target Intelligence Gatherer

Gather complete target intelligence by exploring 9 parallel research paths. Supports targets identified by gene symbol, UniProt accession, Ensembl ID, or gene name.

**KEY PRINCIPLES**:
1. **Report-first** — Create the report file FIRST with all section headers, then populate progressively.
2. **Verify before calling** — Call `mcp__tooluniverse__get_tool_info` before any unfamiliar tool to check exact parameter names.
3. **Evidence grading** — Grade every factual claim T1–T4 (see `references/tools.md`).
4. **Cite everything** — Every data point needs its source database and tool name.
5. **Negative results are data** — "No drugs found" must appear explicitly; empty sections are failures.
6. **Disambiguation first** — Resolve all IDs before starting any research path.
7. **Collision-aware literature** — Detect and filter gene symbol naming collisions.
8. **English-first queries** — Translate all gene/disease names to English before calling tools. Respond to the user in their language.

---

## When to Use This Skill

- User asks about a drug target, protein, or gene
- Target validation or druggability assessment needed
- Comprehensive multi-angle target profiling requested
- "What do we know about [target]?" type questions

**When NOT to use**: Simple protein lookup → call `UniProt_get_entry_by_accession` directly. Drug-only, disease-centric, structure-download, or sequence-retrieval queries → use the dedicated skill for that task.

---

## Phase 0: Pre-Flight Tool Verification

**Before calling any tool for the first time in a session**, call `mcp__tooluniverse__get_tool_info` with `tool_names=["ToolName"]` to confirm exact parameter names. This prevents silent failures.

Critical corrections to memorize (full table in `references/tools.md`):
- `Reactome_map_uniprot_to_pathways` takes `id`, not `uniprot_id`
- `OpenTargets_*` all take `ensemblId` (camelCase with lowercase d), not `ensemblID`
- `GTEx_get_median_gene_expression` requires both `gencode_id` AND `operation="median"`

---

## Phase 1: Create Report File (MANDATORY FIRST STEP)

Create `[TARGET]_target_report.md` with all 14 section headers filled with `[Researching...]` before collecting any data. Update sections progressively. See `REPORT_FORMAT.md` for the full template.

Never show raw tool outputs to the user — only the progressively updated report.

---

## Phase 2: Identifier Resolution

Resolve the query to ALL needed IDs before starting research paths. Collect:
- UniProt accession
- Ensembl ID (bare, e.g., `ENSG00000146648`)
- Ensembl versioned ID (e.g., `ENSG00000146648.18`) — required for GTEx
- Gene symbol
- Entrez ID
- ChEMBL target ID
- HGNC ID
- Full name and synonyms (for literature collision detection)

**Resolution strategy by input type**:
- Gene symbol → call `UniProt_search(query="gene:{SYMBOL} AND organism_id:9606")`, then `ensembl_get_xrefs(id=ensembl_id)`
- UniProt accession → call `UniProt_get_entry_by_accession` and extract cross-references
- Ensembl ID → call `ensembl_lookup_gene(id=ensembl_id, species="human")`; map to UniProt via `UniProt_id_mapping`

**GTEx versioned ID**: After getting the Ensembl ID, call `ensembl_lookup_gene` and read the `version` field. Store `{ensembl_id}.{version}` for use in Path 5. See `references/tools.md` for the fallback procedure.

**GPCR check**: After resolving the symbol, call `GPCRdb_get_protein(operation="get_protein", protein="{symbol_lower}_human")`. If it returns success, the target is a GPCR — activate the GPCR-specific data collection (see Path 2 and Path 7 below).

---

## Phase 3: Execute 9 Research Paths

```
PATH 0: Open Targets Foundation  ← ALWAYS RUN FIRST
PATH 1: Core Identity
PATH 2: Structure & Domains
PATH 3: Function & Pathways
PATH 4: Protein-Protein Interactions
PATH 5: Expression Profile
PATH 6: Variants & Disease
PATH 7: Druggability & Pharmacology
PATH 8: Literature & Research
```

Paths 1–8 can run in parallel after Path 0 completes.

---

### PATH 0: Open Targets Foundation (Always First)

Open Targets provides the most comprehensive aggregated data and fills baseline content for multiple sections before specialized queries. Call **all nine** endpoints with the Ensembl ID — see `references/tools.md` for the complete endpoint-to-section mapping.

If Ensembl ID is not available, document the skip and proceed directly to specialized tools.

---

### PATH 1: Core Identity (Report §2–§3)

Call these tools and populate the identifiers table and basic info sections:
- `UniProt_get_entry_by_accession` — full entry with cross-references
- `UniProt_get_recommended_name_by_accession` — official protein name
- `UniProt_get_alternative_names_by_accession` — synonyms (also needed for collision detection)
- `UniProt_get_subcellular_location_by_accession` — localization
- `UniProt_get_function_by_accession` — functional description
- `MyGene_get_gene_annotation(gene_id=ensembl_id, fields="symbol,name,entrezgene,HGNC,summary")` — gene-level info

---

### PATH 2: Structure & Domains (Report §4)

Use the 3-step chain (details in `references/tools.md`):
1. Extract PDB cross-references from UniProt entry; fetch each with `get_protein_metadata_by_pdb_id`
2. If fewer than 5 structures found, call `PDB_search_similar_structures` at 70% sequence identity
3. If still sparse, call `PDB_search_by_keyword` for each top InterPro domain name
4. Always call `alphafold_get_prediction` regardless of PDB coverage
5. Call `InterPro_get_protein_domains` for domain architecture

**If target is a GPCR**: Also call `GPCRdb_get_structures` to get active/inactive state structures with Ballesteros-Weinstein residue numbering.

**If Tdark or uncharacterized**: Call `InterProScan_scan_sequence` with the protein sequence to predict domains de novo. The job may be asynchronous — check with `InterProScan_get_job_status` and retrieve with `InterProScan_get_job_results`.

**Critical**: "No PDB hit" does NOT mean "no structure exists." Document the search method used, structures found, and note homolog/domain structures if no direct hit.

---

### PATH 3: Function & Pathways (Report §5)

- `GO_get_annotations_for_gene(gene_id=uniprot_accession)` — GO terms (fallback: Open Targets GO endpoint)
- `Reactome_map_uniprot_to_pathways(id=uniprot_accession)` — pathway membership
- `kegg_get_gene_info` — KEGG pathway links
- `enrichr_gene_enrichment_analysis` — optional enrichment if a gene set is needed

---

### PATH 4: Protein-Protein Interactions (Report §6)

Call both primary sources and merge, deduplicating by partner UniProt ID:
- `intact_get_interactions(identifier=uniprot_accession)` — curated interactions
- `STRING_get_protein_interactions(protein_ids=[uniprot_accession], species=9606, confidence_score=700)` — high-confidence network
- `BioGRID_get_interactions(gene_names=[symbol], organism="Homo sapiens")` — additional source

Fallback: If IntAct fails, use `OpenTargets_get_target_interactions_by_ensemblId` as the source.

**Minimum**: Report at least 20 interactors. If fewer returned, document which tools failed and note it explicitly.

---

### PATH 5: Expression Profile (Report §7)

- `GTEx_get_median_gene_expression(gencode_id=ensembl_id, operation="median")` — if empty, retry with versioned ID (see `references/tools.md`)
- `HPA_get_rna_expression_by_source(ensembl_id=ensembl_id)` — always query as backup/supplement
- `HPA_search_genes_by_query(search_query=symbol)` — get HPA gene page
- `HPA_get_comparative_expression_by_gene_and_cellline` — compare relevant cancer cell lines vs normal (supported lines: a549, mcf7, hela, hepg2, pc3)
- `CELLxGENE_get_expression_data` — single-cell expression if available

If GTEx fails for both bare and versioned IDs, document it explicitly and use HPA as the primary source.

---

### PATH 6: Variants & Disease (Report §8)

**Disease associations**:
- Open Targets (Path 0) already covers the primary disease data
- `DisGeNET_search_gene(operation="search_gene", gene=symbol)` — curated GDA scores (requires `DISGENET_API_KEY`; skip gracefully if not set)
- `gwas_get_snps_for_gene(gene_symbol=symbol)` — GWAS associations
- `OpenTargets_get_target_constraint_info_by_ensemblId` — pLI, LOEUF, missense Z-score

**Variants**:
- `clinvar_search_variants(gene=symbol)` — report SNVs and CNVs in separate tables
- `gnomad_get_gene_constraints(gene_symbol=symbol)` — population constraint
- `cBioPortal_get_mutations(gene_symbol=symbol, study_id="msk_impact_2017")` — somatic cancer mutations
- `civic_get_variants_by_gene(gene_symbol=symbol)` — clinically actionable variants

**Evidence tier for DisGeNET scores**: ≥0.7 → T2, 0.4–0.7 → T3, <0.4 → T4. Full mapping in `references/tools.md`.

---

### PATH 7: Druggability & Pharmacology (Report §9)

Call these tools to build a complete druggability picture:

1. **TDL classification**: `Pharos_get_target(gene=symbol)` — returns Tclin/Tchem/Tbio/Tdark plus novelty score. Tclin = approved drug target; Tchem = small molecule tractable; Tdark = understudied. See `references/tools.md` for full interpretation.

2. **Known drugs**: Open Targets already covered in Path 0. Also call `DGIdb_get_drug_gene_interactions(genes=[symbol])` and `ChEMBL_get_target_activities(target_chembl_id=chembl_id)`.

3. **Ligand binding data**: `BindingDB_get_ligands_by_uniprot(uniprot=uniprot_accession, affinity_cutoff=10000)` — sort by affinity; report top 20. Interpret ranges per `references/tools.md`.

4. **HTS screening data**: `PubChem_search_assays_by_target_gene(gene_symbol=symbol)` → for each AID call `PubChem_get_assay_summary` and `PubChem_get_assay_active_compounds`.

5. **Essentiality**: `DepMap_get_gene_dependencies(gene_symbol=symbol)` — negative scores indicate cell-essential genes. Score < −0.5 is strongly essential. See `references/tools.md` for score table.

6. **If GPCR**: `GPCRdb_get_ligands(operation="get_ligands", protein=entry_name)` — curated agonists, antagonists, allosteric modulators.

7. **Chemical probes**: Open Targets already covers this via Path 0. "No probes available" is valid data — state it explicitly with implications.

8. **Clinical pipeline**: `DGIdb_get_drug_gene_interactions`, `ChEMBL_search_mechanisms` for drugs in trial.

**Fallback chain**: If ChEMBL fails → `GtoPdb_get_target_ligands` → Open Targets drugs. Document which source was used.

---

### PATH 8: Literature & Research (Report §11)

**Collision-aware search** (details in `references/tools.md`):

1. Search `"{symbol}"[Title]` (limit 20) and check for off-topic hits — papers with no biology terms (protein/gene/expression/kinase/receptor) in the title.
2. If >20% off-topic, build a collision filter of NOT terms and apply to all queries.
3. Primary seed queries:
   - `"{symbol}"[Title] AND (protein OR gene OR expression)` via `PubMed_search_articles`
   - `"{full_name}"[Title]` via `PubMed_search_articles`
   - `"{symbol}" AND drug AND clinical` for clinical literature
4. If seed < 30 papers, expand via `PubMed_get_related` and `EuropePMC_get_citations` for top 10 seeds.
5. Classify papers into T1–T4 evidence tiers based on study type keywords.

Report: total count, 5-year trend, 3–5 key papers with PMID, title, year, and evidence tier.

---

## Phase 4: Completeness Audit (Before Finalizing)

Run this checklist before writing the Summary section:

- [ ] PPIs: ≥20 interactors OR explanation of why fewer
- [ ] Expression: Top 10 tissues with values OR explicit "unavailable"
- [ ] Diseases: Top 10 associations with scores OR "no associations found"
- [ ] Constraints: pLI, LOEUF, missense Z, pRec OR "unavailable with source noted"
- [ ] Druggability: All modalities assessed; probes and drugs listed OR "none"
- [ ] Every empty tool result noted (never left blank)
- [ ] Failed tools documented with the fallback source used
- [ ] T1–T4 grades present in Executive Summary disease claims
- [ ] T1–T4 grades in Disease Associations table
- [ ] Key papers table has evidence tiers
- [ ] Every data point has source database and tool name cited

If minimums not met, add a **§15 Data Gaps & Limitations** table with: Section | Expected | Actual | Reason | Alternative Source.

---

## Known Gotchas

**GTEx versioned IDs**: GTEx rejects most bare Ensembl IDs. Always get the versioned form (`ENSG....N`) from `ensembl_lookup_gene` before calling GTEx. If the versioned ID also fails, use HPA as primary expression source and document it.

**OpenTargets parameter name**: ALL OpenTargets tools use `ensemblId` (capital I, lowercase d). Using `ensemblID` (capital D) silently returns no data.

**Reactome wrong param**: `Reactome_map_uniprot_to_pathways` takes `id=`, not `uniprot_id=`. Verify with `get_tool_info` before calling.

**DisGeNET API key**: DisGeNET tools require `DISGENET_API_KEY` env var. If not set, skip gracefully and note it as a data gap — do not let it block the workflow.

**InterProScan is async**: `InterProScan_scan_sequence` returns a `job_id` if still running. Poll with `InterProScan_get_job_status` and retrieve with `InterProScan_get_job_results`. Do not proceed assuming immediate results.

**GPCRdb entry name**: GPCRdb uses `{gene_lower}_human` format (e.g., `adrb2_human`). Passing the gene symbol directly will fail silently.

**STRING protein IDs**: `STRING_get_protein_interactions` takes `protein_ids` as a list, not a string. Species must be the NCBI taxon ID integer (9606 for human).

**BindingDB empty results**: If `BindingDB_get_ligands_by_uniprot` returns nothing, this is meaningful data — the target has no measured binding data in BindingDB. State this explicitly and note the implication for tractability.

**Collision detection is mandatory for common words**: Symbols like "SET", "GAS", "CAT", "MAT" frequently appear in non-biological contexts. Always run the collision pre-check before building literature queries.

**NEVER silently skip failed tools**: Every failed tool call must appear in the report either as a documented fallback or as a data gap entry in §15.

---

## Report Structure Summary

Full template in `REPORT_FORMAT.md`. Required sections:

| § | Title | Key Requirement |
|---|-------|-----------------|
| 1 | Executive Summary | Disease claims graded T1–T4 |
| 2 | Target Identifiers | All 7 ID types |
| 3 | Basic Information | Function, location, description |
| 4 | Structural Biology | 3-step PDB chain + AlphaFold |
| 5 | Function & Pathways | GO terms + Reactome/KEGG |
| 6 | Protein-Protein Interactions | ≥20 interactors |
| 7 | Expression Profile | Top 10 tissues with values |
| 8 | Genetic Variation & Disease | SNV/CNV separate; top 10 diseases |
| 9 | Druggability & Pharmacology | All modalities + drugs + probes |
| 10 | Safety Profile | OT safety + mouse KO |
| 11 | Literature | Count + trend + key papers with tiers |
| 12 | Competitive Landscape | Competing targets/drugs |
| 13 | Summary & Recommendations | Scorecard + ≥3 prioritized recs |
| 14 | Data Sources & Methodology | All tools and databases used |
| 15 | Data Gaps & Limitations | Required if any minimums unmet |

---

## Quick Tool Reference

| Tool | Purpose |
|------|---------|
| `mcp__tooluniverse__get_tool_info` | Verify exact parameter names before first call |
| `UniProt_search` | Gene symbol → UniProt accession |
| `UniProt_get_entry_by_accession` | Full protein entry with PDB/Ensembl xrefs |
| `UniProt_id_mapping` | Cross-database ID conversion |
| `ensembl_lookup_gene` | Ensembl gene info + version number for GTEx |
| `ensembl_get_xrefs` | Ensembl → external DB IDs (param: `id`) |
| `MyGene_get_gene_annotation` | Gene summary, Entrez, HGNC |
| `OpenTargets_get_diseases_phenotypes_by_target_ensemblId` | Disease associations |
| `OpenTargets_get_target_tractability_by_ensemblId` | Druggability modalities |
| `OpenTargets_get_target_safety_profile_by_ensemblId` | Safety liabilities |
| `OpenTargets_get_chemical_probes_by_target_ensemblId` | Validated chemical probes |
| `OpenTargets_get_associated_drugs_by_target_ensemblId` | Approved/trial drugs |
| `get_protein_metadata_by_pdb_id` | PDB structure details |
| `alphafold_get_prediction` | AlphaFold3 structure prediction |
| `InterPro_get_protein_domains` | Domain annotations |
| `InterProScan_scan_sequence` | De novo domain prediction (async) |
| `GPCRdb_get_protein` | GPCR family/class check |
| `GPCRdb_get_structures` | GPCR active/inactive structures |
| `GPCRdb_get_ligands` | Curated GPCR ligands |
| `GO_get_annotations_for_gene` | Gene Ontology annotations |
| `Reactome_map_uniprot_to_pathways` | Reactome pathways (param: `id`) |
| `intact_get_interactions` | Curated PPIs |
| `STRING_get_protein_interactions` | High-confidence PPI network |
| `BioGRID_get_interactions` | Additional PPI source |
| `GTEx_get_median_gene_expression` | Tissue expression (needs `operation="median"`) |
| `HPA_get_rna_expression_by_source` | Human Protein Atlas RNA expression |
| `HPA_get_comparative_expression_by_gene_and_cellline` | Cancer vs normal expression |
| `clinvar_search_variants` | Clinical variant significance |
| `gnomad_get_gene_constraints` | Population constraint scores |
| `cBioPortal_get_mutations` | Somatic cancer mutations |
| `civic_get_variants_by_gene` | Clinically actionable variants |
| `DisGeNET_search_gene` | Curated gene-disease associations (needs API key) |
| `Pharos_get_target` | TDL classification (Tclin/Tchem/Tbio/Tdark) |
| `DepMap_get_gene_dependencies` | Cancer cell CRISPR essentiality |
| `BindingDB_get_ligands_by_uniprot` | Measured binding affinities |
| `PubChem_search_assays_by_target_gene` | HTS screening assays |
| `ChEMBL_get_target_activities` | Bioactivity data |
| `DGIdb_get_drug_gene_interactions` | Drug-gene interaction database |
| `PubMed_search_articles` | Literature search |
| `PubMed_get_related` | Expand literature via related articles |
| `EuropePMC_get_citations` | Expand literature via citations |
