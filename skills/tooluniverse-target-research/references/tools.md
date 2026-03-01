# Tool Detail Reference for Target Research

Detailed parameter tables and output templates moved here from SKILL.md.
For the full 225+ tool catalog see `../REFERENCE.md`.

---

## Parameter Corrections (Known Gotchas)

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `Reactome_map_uniprot_to_pathways` | `uniprot_id` | `id` |
| `ensembl_get_xrefs` | `gene_id` | `id` |
| `GTEx_get_median_gene_expression` | `gencode_id` alone | `gencode_id` + `operation="median"` |
| `OpenTargets_*` | `ensemblID` | `ensemblId` (camelCase, lowercase d) |
| `DisGeNET_search_gene` | any positional | `operation="search_gene"`, `gene=symbol` |
| `GPCRdb_get_protein` | gene symbol direct | `operation="get_protein"`, `protein="{symbol_lower}_human"` |

---

## Path 0: Open Targets Endpoints (All Required)

Call ALL nine endpoints with the Ensembl ID:

| Endpoint | Fills Report Section |
|----------|---------------------|
| `OpenTargets_get_diseases_phenotypes_by_target_ensemblId` | §8 Disease Associations |
| `OpenTargets_get_target_tractability_by_ensemblId` | §9 Tractability |
| `OpenTargets_get_target_safety_profile_by_ensemblId` | §10 Safety |
| `OpenTargets_get_target_interactions_by_ensemblId` | §6 PPIs |
| `OpenTargets_get_target_gene_ontology_by_ensemblId` | §5 GO |
| `OpenTargets_get_publications_by_target_ensemblId` | §11 Literature |
| `OpenTargets_get_biological_mouse_models_by_ensemblId` | §8/§10 Mouse KO |
| `OpenTargets_get_chemical_probes_by_target_ensemblId` | §9 Probes |
| `OpenTargets_get_associated_drugs_by_target_ensemblId` | §9 Drugs |

---

## Structure Search — 3-Step Chain

1. **UniProt cross-references** — Extract `uniProtKBCrossReferences` where `database=="PDB"` from `UniProt_get_entry_by_accession`. Fetch each PDB ID with `get_protein_metadata_by_pdb_id`.
2. **Sequence similarity** — If fewer than 5 structures found, call `PDB_search_similar_structures` with the first 500 aa of the sequence at `identity_cutoff=0.7`.
3. **Domain keyword** — If still sparse, call `PDB_search_by_keyword` for each InterPro domain name returned by `InterPro_get_protein_domains`.
4. **AlphaFold** — Always call `alphafold_get_prediction(qualifier=uniprot_accession)` regardless of PDB coverage.

---

## GTEx Versioned ID Fallback

GTEx often rejects bare Ensembl IDs. If the first call returns empty data:
1. Call `ensembl_lookup_gene(id=ensembl_id, species="human")` and read the `version` field.
2. Retry GTEx with `gencode_id=f"{ensembl_id}.{version}"`, e.g., `ENSG00000146648.18`.

---

## Pharos TDL Interpretation

| TDL | Meaning | Drug Development Signal |
|-----|---------|------------------------|
| Tclin | Approved drug target | Validated, highest confidence |
| Tchem | IC50 < 30 nM small molecule data | Chemically tractable |
| Tbio | Biological annotations, no chemical data | May need new modalities |
| Tdark | Understudied, limited data | High novelty; proceed with caution |

---

## DepMap Effect Score Interpretation

| Score | Label |
|-------|-------|
| < −1.0 | Strongly essential |
| −0.5 to −1.0 | Essential |
| −0.5 to 0 | Weakly essential |
| > 0 | Non-essential |

---

## BindingDB Affinity Ranges

| Affinity (nM) | Level | Clinical Relevance |
|---------------|-------|--------------------|
| < 1 | Ultra-potent | Clinical candidate likely exists |
| 1 – 30 | Tchem threshold | Drug-like |
| 30 – 100 | Potent | Good starting point |
| 100 – 1000 | Moderate | Needs optimization |
| > 1000 | Weak | Early hit only |

---

## DisGeNET Score Mapping to Evidence Tiers

| DisGeNET Score | Evidence Tier |
|----------------|---------------|
| ≥ 0.7 | T2 — multiple validated sources |
| 0.4 – 0.7 | T3 — association level |
| < 0.4 | T4 — mention/predicted |

---

## GPCR Detection: Entry Name Format

GPCRdb requires the receptor entry name, not the gene symbol:
- Format: `{gene_symbol_lowercase}_human`
- Examples: `adrb2_human`, `drd2_human`, `htr1a_human`
- Call `GPCRdb_get_protein(operation="get_protein", protein=entry_name)`
- If status is `"success"`, target is a confirmed GPCR.

For confirmed GPCRs, additionally call:
- `GPCRdb_get_structures(operation="get_structures", protein=entry_name)` — active/inactive state structures with Ballesteros-Weinstein numbering
- `GPCRdb_get_ligands(operation="get_ligands", protein=entry_name)` — curated agonists/antagonists
- `GPCRdb_get_mutations(operation="get_mutations", protein=entry_name)` — experimental mutation effects

---

## Collision-Aware Literature Query Construction

1. Search `"{symbol}"[Title]` with limit 20 and scan for off-topic results (no bio terms like protein/gene/expression/kinase/receptor in title).
2. If collision detected, append ` NOT {collision_term}` to all subsequent queries.
3. Seed query priority order:
   - `"{symbol}"[Title] AND (protein OR gene OR expression)`
   - `"{full_name}"[Title]`
   - `"UniProt:{accession}"`
   - Top 3 synonyms in title
4. If seed count < 30, expand via `PubMed_get_related` and `EuropePMC_get_citations` for top 10 seeds.

---

## Fallback Chain Reference

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `ChEMBL_get_target_activities` | `GtoPdb_get_target_ligands` | Open Targets drugs endpoint |
| `intact_get_interactions` | `STRING_get_protein_interactions` | Open Targets interactions endpoint |
| `GO_get_annotations_for_gene` | Open Targets GO endpoint | `MyGene_get_gene_annotation` fields="go" |
| `GTEx_get_median_gene_expression` | `HPA_get_rna_expression_by_source` | Note as unavailable, document in §15 |
| `gnomad_get_gene_constraints` | Open Targets constraint endpoint | Note as unavailable |
| `DGIdb_get_drug_gene_interactions` | Open Targets drugs endpoint | `GtoPdb_get_target_interactions` |

---

## HPA Cell Lines Supported

`HPA_get_comparative_expression_by_gene_and_cellline` accepts: `a549`, `mcf7`, `hela`, `hepg2`, `pc3`, `jurkat`, `rh30`, `siha`, `u251`, `ishikawa`

---

## Evidence Tier Criteria

| Tier | Symbol | Criteria |
|------|--------|----------|
| T1 | ★★★ | Direct mechanistic evidence, human genetic proof (CRISPR KO, patient mutations, crystal structure with mechanism) |
| T2 | ★★☆ | Functional studies, model organism (siRNA phenotype, mouse KO, biochemical assay) |
| T3 | ★☆☆ | Association/screen (GWAS hit, DepMap essentiality, expression correlation) |
| T4 | ☆☆☆ | Mention, review, text-mined, computational prediction |

---

## Report Section Minimum Data Requirements

| Section | Minimum | If Not Met |
|---------|---------|------------|
| §6 PPIs | ≥ 20 interactors | Document which tools failed + why |
| §7 Expression | Top 10 tissues with TPM + HPA RNA summary | Note "limited data" with gaps |
| §8 Disease | Top 10 OT diseases + gnomAD constraints + ClinVar summary | Separate SNV/CNV; note missing data |
| §9 Druggability | OT tractability + probes + drugs + DGIdb + GtoPdb fallback | "No drugs/probes" is valid data |
| §11 Literature | Total count + 5-year trend + 3–5 key papers with evidence tiers | Note if sparse (< 50 papers) |
