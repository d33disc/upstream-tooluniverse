# Metabolomics Analysis - Tool Reference

Detailed parameter tables for all ToolUniverse tools used in the metabolomics analysis workflow.
For workflow steps and decision logic, see `../SKILL.md`.

All tool calls use: `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`

---

## Phase 1: Metabolite Identification

### MetaboAnalyst_name_to_id

Map metabolite common names to KEGG, HMDB, PubChem, and ChEBI identifiers.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `metabolites` | array of strings | Yes | List of metabolite common names, e.g. `["glucose", "pyruvate", "lactate"]` |

**Returns**: For each metabolite — matched name, KEGG compound ID, HMDB ID, PubChem CID, ChEBI ID, molecular formula, exact mass.

**Notes**:
- Use this before `MetaboAnalyst_pathway_enrichment` to validate which names resolve
- Unresolved names are returned with null IDs — exclude these from enrichment input
- Accepts common names, synonyms, and abbreviations; tries multiple aliases internally

---

### MetabolomicsWorkbench_search_by_mz

Identify metabolites by m/z value from mass spectrometry data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input_value` | string | Yes | m/z value as string, e.g. `"180.0634"` |
| `ion_type` | string | No | Ion mode: `"[M+H]+"`, `"[M-H]-"`, `"[M+Na]+"`, `"[M+NH4]+"`. Default: `"[M+H]+"` |
| `mass_tolerance` | string | No | Tolerance in Da or ppm. Default: `"0.5"` (Da). For high-res: `"5ppm"` |
| `output_item` | string | No | `"all"` (default), or specific fields |

**Returns**: List of matching RefMet compounds with name, formula, exact mass, KEGG ID, PubChem CID.

**Notes**:
- Searches the RefMet database — optimized for biologically relevant small molecules
- For high-resolution instruments (Orbitrap, Q-TOF): use `mass_tolerance="5ppm"`
- For low-resolution (triple quad): use `mass_tolerance="0.5"` (Da)
- Convert observed m/z to neutral mass before searching: subtract adduct mass (H=1.00728, Na=22.98922, etc.)

---

### MetabolomicsWorkbench_search_by_exact_mass

Search metabolites by neutral exact molecular mass.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input_value` | string | Yes | Exact neutral mass as string, e.g. `"180.0634"` |
| `mass_tolerance` | string | No | Tolerance in Da. Default: `"0.5"` |
| `output_item` | string | No | `"all"` (default) |

**Notes**: Use when you already have the neutral monoisotopic mass (not m/z). Preferred over `search_by_mz` when adduct form is uncertain.

---

### MetabolomicsWorkbench_search_compound_by_name

Search for a compound by name using RefMet nomenclature.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input_value` | string | Yes | Metabolite name, e.g. `"citric acid"` |
| `output_item` | string | No | `"all"` (default), `"formula"`, `"exactmass"`, `"inchi_key"`, `"smiles"` |

**Returns**: RefMet ID, standardized name, formula, exact mass, classification (super-class, main-class, sub-class).

---

### MetabolomicsWorkbench_get_refmet_info

Get RefMet standardized nomenclature for a metabolite.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input_value` | string | Yes | Metabolite name or synonym |
| `output_item` | string | No | `"all"` (default), `"refmet_name"`, `"formula"`, `"exactmass"`, `"super_class"`, `"main_class"`, `"sub_class"` |

**Notes**: Use to harmonize metabolite names across studies and databases. RefMet is the controlled vocabulary for Metabolomics Workbench.

---

### MetabolomicsWorkbench_get_comp_by_pubc_cid

Get metabolite information using PubChem compound ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input_value` | string | Yes | PubChem CID as string, e.g. `"311"` for citric acid |
| `output_item` | string | No | `"all"` (default), `"regno"`, `"formula"`, `"exactmass"`, `"inchi_key"`, `"name"`, `"smiles"` |

---

### HMDB_search

Search HMDB by metabolite name, formula, or mass.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `operation` | string | Yes | Must be `"search"` |
| `query` | string | Yes | Metabolite name, formula, or HMDB ID prefix |
| `limit` | integer | No | Maximum results to return (default: 10) |

**Returns**: List of matching metabolites with HMDB IDs and basic properties.

---

### HMDB_get_metabolite

Get full metabolite information from HMDB by HMDB ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `operation` | string | Yes | Must be `"get_metabolite"` |
| `hmdb_id` | string | Yes | HMDB accession ID, e.g. `"HMDB0000122"` for glucose |

**Returns**: Name, formula, SMILES, InChIKey, classification, biological roles, pathways, normal concentration ranges, biospecimen presence (blood, urine, CSF, etc.).

---

### HMDB_get_diseases

Get disease and pathway associations for a metabolite.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `operation` | string | Yes | Must be `"get_diseases"` |
| `hmdb_id` | string | Yes | HMDB accession ID |

**Returns**: Diseases linked to abnormal levels of this metabolite (elevated or decreased), metabolic pathways, and literature references. Useful for biomarker context.

---

### metabolights_search_studies

Search MetaboLights studies by keyword.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search term (disease, metabolite, technology) |

**Returns**: List of matching study IDs (MTBLS*).

---

### metabolights_get_study

Get metadata for a specific MetaboLights study.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `study_id` | string | Yes | MetaboLights study ID, e.g. `"MTBLS1"` |

**Returns**: Title, description, organism, metabolite list, assay types, protocols, publication info.

---

### metabolights_get_study_assays

Get assay metadata for a MetaboLights study.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `study_id` | string | Yes | MetaboLights study ID |

**Returns**: Assay types (LC-MS, GC-MS, NMR), protocols, measurement technology details.

---

### metabolights_get_study_protocols

Get experimental protocols for a MetaboLights study.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `study_id` | string | Yes | MetaboLights study ID |

**Returns**: Detailed protocol descriptions for sample collection, extraction, chromatography, and data acquisition. Use to assess study quality and comparability.

---

### MetabolomicsWorkbench_get_study

Get metadata for a Metabolomics Workbench study.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `study_id` | string | Yes | Study ID, e.g. `"ST000001"` |
| `context` | string | No | `"study"` (default) |
| `output_item` | string | No | `"summary"` (default), `"analysis"`, `"metabolites"`, `"factors"`, `"mwtab"` |

---

## Phase 6: Pathway Enrichment

### MetaboAnalyst_pathway_enrichment

Perform pathway over-representation analysis (ORA) using KEGG metabolic pathways.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `metabolites` | array of strings | Yes | List of differential metabolite names. Use KEGG-compatible names from `MetaboAnalyst_name_to_id`. |
| `organism` | string | No | KEGG organism code. Default: `"hsa"` (human). Common: `"mmu"` (mouse), `"rno"` (rat), `"sce"` (yeast), `"eco"` (E. coli) |

**Returns**: Pathways sorted by p-value with:
- Pathway name, KEGG ID
- p-value (hypergeometric test), FDR-corrected p-value
- Fold enrichment
- Number of hits / total in pathway
- Hit metabolite names

**Critical notes**:
- Only metabolites with valid KEGG IDs are included in the test; unresolved names are silently ignored
- Run `MetaboAnalyst_name_to_id` first and log how many metabolites resolved
- Minimum ~10 input metabolites for reliable results
- Background is all KEGG compounds for the organism by default

---

### MetaboAnalyst_biomarker_enrichment

Test metabolite list against curated metabolite set libraries (SMPDB, HMDB).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `metabolites` | array of strings | Yes | List of metabolite names to test |

**Returns**: Enriched metabolite sets including:
- Glycolysis, TCA cycle, urea cycle
- Amino acid metabolism pathways (individual)
- Fatty acid beta-oxidation
- Purine and pyrimidine metabolism
- Glutathione metabolism
- Bile acid biosynthesis
- Sphingolipid metabolism
- Ketone body metabolism
- Pentose phosphate pathway

**Notes**: Complementary to `MetaboAnalyst_pathway_enrichment`. Uses different underlying library (SMPDB/HMDB) vs KEGG. Run both for comprehensive coverage.

---

### MetaboAnalyst_get_pathway_library

List available KEGG metabolic pathways for a species.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `organism` | string | No | KEGG organism code. Default: `"hsa"` |

**Returns**: All pathways with KEGG ID, name, category (metabolic/non-metabolic), and number of compounds per pathway.

**Use case**: Run before enrichment to verify pathway coverage for non-human organisms, or to browse relevant pathways.

---

### kegg_search_pathway

Search KEGG pathways by keyword.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search term, e.g. `"glycolysis"`, `"TCA"`, `"fatty acid"` |
| `organism` | string | No | Organism code, e.g. `"hsa"` |

**Returns**: Matching pathway IDs and descriptions.

---

### kegg_get_pathway_info

Get detailed KEGG pathway information including genes, compounds, and reactions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pathway_id` | string | Yes | KEGG pathway ID, e.g. `"hsa00010"` (Glycolysis/Gluconeogenesis) |

**Returns**: Pathway name, organism, compounds (metabolites), genes (enzymes), reactions, cross-references to other databases.

**Common pathway IDs**:

| Pathway | KEGG ID (human) |
|---------|----------------|
| Glycolysis/Gluconeogenesis | `hsa00010` |
| TCA cycle | `hsa00020` |
| Oxidative phosphorylation | `hsa00190` |
| Fatty acid biosynthesis | `hsa00061` |
| Fatty acid degradation (beta-ox) | `hsa00071` |
| Glutathione metabolism | `hsa00480` |
| Amino acid biosynthesis | `hsa00250` |
| Purine metabolism | `hsa00230` |
| Pyrimidine metabolism | `hsa00240` |
| Pentose phosphate pathway | `hsa00030` |

---

### KEGG_get_compound

Get KEGG compound/metabolite details.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `compound_id` | string | Yes | KEGG compound ID, e.g. `"C00002"` (ATP), `"C00022"` (pyruvate) |

**Returns**: Names (all synonyms), formula, molecular weight, associated pathways (all pathways containing this compound), associated enzymes (EC numbers), reactions, cross-references (HMDB, PubChem, ChEBI).

**Use case**: After identifying key differential metabolites, retrieve their linked enzymes and pathways for Phase 7 integration.

---

### KEGG_get_pathway_genes

Get all genes/enzymes in a KEGG pathway.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pathway_id` | string | Yes | KEGG pathway ID with organism prefix, e.g. `"hsa00010"` |

**Returns**: All gene IDs (KEGG format, e.g. `hsa:2023`) in the pathway. Cross-reference with transcriptomics DE results for multi-omics integration.

---

### ReactomeContent_search

Search Reactome knowledge base by keyword.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search term |
| `species` | string | No | Species name, e.g. `"Homo sapiens"` |
| `types` | array | No | Entity types to include: `["Pathway", "Reaction", "Protein", "Chemical Compound"]` |

**Returns**: Matching pathways, reactions, and entities with Reactome stable IDs (R-HSA-*).

---

### Reactome_get_pathway

Get detailed Reactome pathway information.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `stId` | string | Yes | Reactome stable pathway ID, e.g. `"R-HSA-70171"` (Glycolysis) |

**Returns**: Pathway name, species, description, sub-events (reactions and sub-pathways), compartments, GO annotations, literature references.

---

### ReactomeContent_get_contained_events

Get all sub-events in a Reactome pathway.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `stId` | string | Yes | Reactome pathway stable ID |

**Returns**: Full hierarchy of sub-pathways and reactions within the pathway. Useful for identifying which specific reactions are affected.

---

## Common Metabolite KEGG IDs (Quick Reference)

| Metabolite | KEGG ID | Pathway Context |
|------------|---------|-----------------|
| Glucose | C00031 | Glycolysis, pentose phosphate |
| Glucose-6-phosphate | C00092 | Glycolysis, pentose phosphate |
| Pyruvate | C00022 | Glycolysis, TCA entry |
| Lactate | C00186 | Glycolysis (anaerobic) |
| Acetyl-CoA | C00024 | TCA cycle, fatty acid synthesis |
| Citrate | C00158 | TCA cycle |
| alpha-Ketoglutarate | C00026 | TCA cycle, amino acid catabolism |
| Succinate | C00042 | TCA cycle |
| Fumarate | C00122 | TCA cycle, urea cycle |
| Malate | C00149 | TCA cycle |
| Oxaloacetate | C00036 | TCA cycle, gluconeogenesis |
| NADH | C00004 | Electron transport chain |
| NAD+ | C00003 | Redox metabolism |
| ATP | C00002 | Energy metabolism |
| ADP | C00008 | Energy metabolism |
| Glutamate | C00025 | Amino acid, TCA anaplerosis |
| Glutamine | C00064 | Amino acid, nitrogen metabolism |
| Aspartate | C00049 | Amino acid, urea cycle |
| Alanine | C00041 | Amino acid, gluconeogenesis |
| Serine | C00065 | Amino acid, one-carbon metabolism |
| Glycine | C00037 | Amino acid, one-carbon metabolism |
| Leucine | C00123 | Branched-chain amino acid |
| Isoleucine | C00407 | Branched-chain amino acid |
| Valine | C00183 | Branched-chain amino acid |
| Palmitate | C00249 | Fatty acid synthesis |
| Stearate | C01530 | Fatty acid |
| Cholesterol | C00187 | Steroid biosynthesis |
| Sphingosine | C00319 | Sphingolipid metabolism |
| Carnitine | C00318 | Fatty acid transport |
| Taurine | C00245 | Bile acid conjugation |
| Uric acid | C00366 | Purine degradation |
| Creatinine | C00791 | Muscle energy metabolism |

---

## Ion Adduct Mass Corrections (LC-MS)

To convert observed m/z to neutral mass:

| Ion Form | Mode | Correction | Example |
|----------|------|-----------|---------|
| `[M+H]+` | Positive | m/z - 1.00728 | glucose m/z 181.0712 → mass 180.0634 |
| `[M+Na]+` | Positive | m/z - 22.98922 | |
| `[M+NH4]+` | Positive | m/z - 18.03437 | |
| `[M+K]+` | Positive | m/z - 38.96316 | |
| `[M-H]-` | Negative | m/z + 1.00728 | |
| `[M+Cl]-` | Negative | m/z - 34.96940 | |
| `[M+HCOO]-` | Negative | m/z - 44.99820 | |

---

## Organism Codes (KEGG)

| Organism | Code |
|----------|------|
| Human | `hsa` |
| Mouse | `mmu` |
| Rat | `rno` |
| Zebrafish | `dre` |
| Drosophila | `dme` |
| C. elegans | `cel` |
| Yeast (S. cerevisiae) | `sce` |
| E. coli K-12 | `eco` |
| A. thaliana | `ath` |
