---
name: tooluniverse-gwas-drug-discovery
description: Transform GWAS signals into actionable drug targets and repurposing opportunities. Performs locus-to-gene mapping, target druggability assessment, existing drug identification, safety profile evaluation, and clinical trial matching. Use when discovering drug targets from GWAS data, finding drug repurposing opportunities from genetic associations, or translating GWAS findings into therapeutic leads.
---

# GWAS-to-Drug Target Discovery

Transform genome-wide association studies (GWAS) into actionable drug targets and repurposing opportunities.

## Overview

This skill bridges genetic discoveries from GWAS with drug development by:

1. Identifying genes associated with a disease through GWAS signal analysis
2. Mapping credible-set signals to likely causal genes via Locus-to-Gene (L2G) scores
3. Assessing druggability and safety for candidate targets
4. Finding existing drugs and repurposing opportunities
5. Evaluating clinical and safety evidence

**Why genetic evidence matters**: Targets with human genetic support have approximately 2x higher probability of clinical approval (Nelson et al., Nature Genetics 2015).

---

## Known Gotchas

**EFO/MONDO namespace for Open Targets**
Open Targets tools that take a disease ID require an EFO or MONDO-formatted ID (e.g., `EFO_0000249`, `MONDO_0005148`). Raw OMIM, ICD-10, or UMLS IDs will not work directly. Use `OpenTargets_get_dise_id_desc_by_name` to resolve a disease name to its EFO ID, or use `OpenTargets_map_any_dise_id_to_all_othe_ids` to convert any known disease ID (OMIM, UMLS, ICD-10, etc.) to EFO.

**`p_value = 0.0` in GWAS Catalog results**
The GWAS Catalog REST API returns `p_value: 0.0` for highly significant hits (typically p < 10^-300) where the value underflows to zero. This is a data representation artifact, not an error. Treat `p_value = 0.0` as "extremely significant" and do not filter these records out.

**`variantId` format for Open Targets**
`OpenTargets_get_variant_credible_sets` requires the Open Targets variant ID format: `chr_position_ref_alt` (e.g., `10_112998590_C_T`). Standard dbSNP rs IDs (e.g., `rs7903146`) are not accepted directly. Obtain the correct `variantId` from a credible set row's `variant.id` field returned by `OpenTargets_get_study_credible_sets`, or look up the variant's genomic coordinates and construct the ID manually.

**`studyLocusId` is a hash, not a GCST accession**
`OpenTargets_get_credible_set_detail` takes a `studyLocusId` which is a 32-character hex hash (e.g., `b758d8fb10924f5338cbad8d27c7dee8`), not a GWAS Catalog accession. Obtain it from the `rows[].studyLocusId` field returned by `OpenTargets_get_study_credible_sets` or `OpenTargets_get_variant_credible_sets`.

**Open Targets uses abbreviated tool names**
Several Open Targets tools have abbreviated names in this system (e.g., `OpenTargets_get_targ_trac_by_ense` for tractability, `OpenTargets_get_targ_safe_prof_by_ense` for safety). See the Tool Reference table below for the full mapping.

---

## Workflow

### Phase 1 — Identify disease EFO ID

Open Targets tools require an EFO or MONDO disease ID. Always resolve the disease name first.

Call `OpenTargets_get_dise_id_desc_by_name` with the disease name (e.g., `"type 2 diabetes"`). Take the top hit's `id` field — this is the EFO ID (e.g., `EFO_0003777`) or MONDO ID (e.g., `MONDO_0005148`).

If you have an OMIM, UMLS, or ICD-10 ID instead, call `OpenTargets_map_any_dise_id_to_all_othe_ids` with that ID to retrieve the EFO equivalent.

### Phase 2 — Find GWAS studies and significant loci

With the EFO ID, search for GWAS studies in Open Targets:

Call `OpenTargets_search_gwas_studies_by_disease` with `diseaseIds` set to the EFO/MONDO ID array and `enableIndirect=true` to include child disease terms. This returns GCST accession IDs (e.g., `GCST000392`), sample sizes, and whether summary statistics are available.

Alternatively (or in addition), call `gwas_get_associations_for_trait` with `efo_id` to pull associations directly from the GWAS Catalog REST API. Results are sorted by p-value (most significant first). Prefer `efo_id` over `disease_trait` for reliable filtering.

For a known SNP of interest, call `gwas_get_associations_for_snp` with `rs_id` to retrieve all associated traits.

### Phase 3 — Locus-to-Gene (L2G) mapping

L2G scores predict which gene at a fine-mapped locus is the most likely causal target.

Call `OpenTargets_get_study_credible_sets` with `studyIds` set to the GCST accession(s) from Phase 2. Each row in the response includes:
- `studyLocusId` — identifier for the credible set (needed for Phase 3b)
- `variant.id` — Open Targets format variant ID (`chr_pos_ref_alt`)
- `l2GPredictions.rows` — list of genes with L2G scores (0 to 1, higher = more likely causal)
- `pValueMantissa` / `pValueExponent` — p-value as mantissa × 10^exponent
- `finemappingMethod` — fine-mapping method used (e.g., SuSiE, FINEMAP)

For deeper detail on a specific locus, call `OpenTargets_get_credible_set_detail` with the `studyLocusId`. This also returns colocalization evidence with QTLs.

For a specific variant rather than a study, call `OpenTargets_get_variant_credible_sets` with `variantId` in `chr_pos_ref_alt` format.

Collect genes with L2G score > 0.5 as high-confidence candidates. Include genes with score > 0.1 if coverage is sparse.

### Phase 4 — Druggability and safety assessment

For each candidate gene, retrieve its Ensembl ID. If you only have the gene symbol, call `OpenTargets_get_target_id_description_by_name` (pass the gene symbol as the name) to get the Ensembl ID.

**Target class**: Call `OpenTargets_get_target_classes_by_ensemblID` with `ensemblId`. The response lists target class labels (e.g., `GPCR`, `Kinase`, `Ion channel`, `Nuclear receptor`) and hierarchy levels. Target class strongly predicts druggability tier.

**Tractability**: Call `OpenTargets_get_targ_trac_by_ense` with `ensemblId`. The response lists tractability assessments by modality (`Small molecule`, `Antibody`, `PROTAC`, `Oligonucleotide`) with boolean `value` fields indicating evidence for that modality. A target with `Small molecule: true` and prior clinical candidates is highly tractable.

**Genetic constraint**: Call `OpenTargets_get_targ_cons_info_by_ense` with `ensemblId`. The `pLI` score (probability of loss-of-function intolerance) indicates essential gene risk. A high pLI (> 0.9) means strong selection against loss of function, flagging potential on-target toxicity.

**Safety liabilities**: Call `OpenTargets_get_targ_safe_prof_by_ense` with `ensemblId`. Returns safety events with tissue context, dosing direction (activation vs inhibition), and data source. Flag any events in cardiac, hepatic, or CNS tissues.

### Phase 5 — Existing drugs and repurposing

**Drugs for the disease**: Call `OpenTargets_get_asso_drug_by_dise_efoI` with `efoId` and a reasonable `size` (e.g., 50). Returns known drugs with their targets, mechanisms of action, clinical phase, approval status, and withdrawal status. This identifies existing approved drugs and repurposing candidates directly tied to the disease.

**Drugs for a specific target**: Call `OpenTargets_get_asso_drug_by_targ_ense` with `ensemblId` and `size`. Returns drugs that modulate this target across all indications — critical for repurposing: a drug approved for indication A may be repurposable for indication B if the same target is implicated in B by GWAS.

**ChEMBL bioactivity**: Call `ChEMBL_search_targets` with the gene symbol to get a ChEMBL target ID. Then call `ChEMBL_get_target_activities` with that target ID to retrieve quantitative bioactivity data (IC50, Ki, EC50) across compounds. This reveals the depth of the chemical matter landscape.

**Drug mechanisms**: Call `ChEMBL_get_drug_mechanisms` with a ChEMBL drug ID to confirm mechanism of action and directionality (agonist, antagonist, inhibitor, activator).

### Phase 6 — Clinical and safety evidence

**Drug warnings**: Call `OpenTargets_get_drug_warnings_by_chemblId` with the drug's ChEMBL ID (format: `CHEMBL25`). Returns black-box warnings, withdrawals, and toxicity class by country and year.

**FDA adverse events**: Call `FDA_get_adverse_reactions_by_drug_name` with `drug_name`. Returns adverse reactions text and warnings from FDA drug labels. Use `limit` to control result count.

**Repurposing decision logic**:
- Approved drug + target implicated by GWAS in new disease = strong repurposing candidate
- Check mechanism directionality: does the drug's action (inhibition/activation) match the genetic direction of effect (risk allele increases/decreases expression or function)?
- Approved drugs skip Phase I; repurposing timelines are 3-5 years vs 10-15 years for novel drugs

---

## Worked Example: Type 2 Diabetes

1. `OpenTargets_get_dise_id_desc_by_name(diseaseName="type 2 diabetes")` → `MONDO_0005148`
2. `OpenTargets_search_gwas_studies_by_disease(diseaseIds=["MONDO_0005148"], enableIndirect=true, size=10)` → e.g., GCST000392
3. `OpenTargets_get_study_credible_sets(studyIds=["GCST000392"], size=20)` → credible sets with L2G predictions
4. Top L2G gene: `TCF7L2` (ENSG00000148737, score 0.9)
5. `OpenTargets_get_target_classes_by_ensemblID(ensemblId="ENSG00000148737")` → Transcription factor
6. `OpenTargets_get_targ_trac_by_ense(ensemblId="ENSG00000148737")` → limited small molecule tractability
7. `OpenTargets_get_asso_drug_by_dise_efoI(efoId="MONDO_0005148", size=50)` → GLP1R agonists, DPP4 inhibitors
8. `OpenTargets_get_targ_safe_prof_by_ense(ensemblId="ENSG00000006634")` (GLP1R) → safety review
9. Outcome: GLP1R is a validated tractable target; TCF7L2 is high-confidence GWAS hit but transcription factor — prioritize GLP1R for drug search

---

## Target Prioritization Framework

When multiple GWAS genes emerge, rank by combining:

- **L2G score** (0-1) — genetic evidence for causality at this locus
- **Target class** — GPCR/kinase/ion channel score higher than transcription factors/scaffold proteins
- **Tractability modality** — small molecule or antibody evidence present
- **Genetic constraint** — pLI < 0.5 preferred (fewer essential gene risks)
- **Safety liabilities** — flag cardiac, hepatic events

Approximate composite priority:
```
Priority = (L2G × 0.4) + (Druggability tier × 0.3) + (Existing chemical matter × 0.2) + (Constraint safety × 0.1)
```

---

## Drug Repurposing Decision Tree

```
GWAS gene implicated in disease?
  └─ Yes → Drug approved for any indication targeting that gene?
               └─ Yes → Check mechanism directionality
                           └─ Matches? → Strong repurposing candidate
                           └─ Opposite? → Contraindicated
               └─ No  → Clinical-stage compound for that gene?
                           └─ Yes → Phase II repurposing
                           └─ No  → Novel target program
```

---

## Tool Reference

Agents call tools via `mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`.

| Tool | Key Arguments | Purpose |
|------|--------------|---------|
| `OpenTargets_get_dise_id_desc_by_name` | `diseaseName` | Resolve disease name to EFO ID |
| `OpenTargets_map_any_dise_id_to_all_othe_ids` | `inputId` (any ID format) | Convert OMIM/UMLS/ICD10 to EFO |
| `gwas_get_associations_for_trait` | `efo_id` or `disease_trait` | GWAS Catalog associations for trait |
| `gwas_get_associations_for_snp` | `rs_id` | All traits associated with a SNP |
| `gwas_search_associations` | `disease_trait`, `efo_id`, `rs_id` | Flexible GWAS Catalog search |
| `OpenTargets_search_gwas_studies_by_disease` | `diseaseIds[]`, `enableIndirect` | GWAS studies by disease (EFO/MONDO IDs) |
| `OpenTargets_get_study_credible_sets` | `studyIds[]`, `size` | Fine-mapped loci + L2G for a study |
| `OpenTargets_get_variant_credible_sets` | `variantId` (chr_pos_ref_alt) | Credible sets containing a variant |
| `OpenTargets_get_credible_set_detail` | `studyLocusId` (32-char hash) | Full detail on one credible set |
| `OpenTargets_get_target_id_description_by_name` | `name` (gene symbol) | Gene symbol to Ensembl ID |
| `OpenTargets_get_target_classes_by_ensemblID` | `ensemblId` | Target class (GPCR, kinase, etc.) |
| `OpenTargets_get_targ_trac_by_ense` | `ensemblId` | Tractability by modality |
| `OpenTargets_get_targ_cons_info_by_ense` | `ensemblId` | Genetic constraint / pLI score |
| `OpenTargets_get_targ_safe_prof_by_ense` | `ensemblId` | Safety liabilities |
| `OpenTargets_get_asso_drug_by_dise_efoI` | `efoId`, `size` | Known drugs for a disease |
| `OpenTargets_get_asso_drug_by_targ_ense` | `ensemblId`, `size` | Known drugs for a target |
| `OpenTargets_get_asso_targ_by_dise_efoI` | `efoId` | Targets associated with disease |
| `ChEMBL_search_targets` | target name or gene symbol | Find ChEMBL target ID |
| `ChEMBL_get_target_activities` | ChEMBL target ID | Bioactivity data (IC50, Ki, EC50) |
| `ChEMBL_search_drugs` | drug name | Search drugs by name |
| `ChEMBL_get_drug_mechanisms` | ChEMBL drug ID | Drug mechanism of action |
| `OpenTargets_get_drug_warnings_by_chemblId` | `chemblId` | Drug black-box warnings, withdrawals |
| `FDA_get_adverse_reactions_by_drug_name` | `drug_name`, `limit` | FDA adverse event data |

Full parameter schemas: `references/tools.md`

---

## Limitations

- GWAS association does not imply causation. Linkage disequilibrium means the causal variant may differ from the lead SNP.
- L2G scores are predictions, not ground truth. Experimental validation is required.
- Most GWAS cohorts are of European ancestry; findings may not generalize across populations.
- Druggable does not mean effective: the right direction of modulation (agonism vs inhibition) must be verified against disease biology.
- This skill is for research hypothesis generation only, not clinical decision-making or regulatory submission.

---

## References

- Nelson et al. (2015) *Nature Genetics* — Genetic support doubles clinical success rate
- King et al. (2019) *PLOS Genetics* — Systematic analysis of genetic evidence and trial success
- Claussnitzer et al. (2020) *Nature Reviews Genetics* — From GWAS to biology

Databases: [GWAS Catalog](https://www.ebi.ac.uk/gwas/), [Open Targets Genetics](https://genetics.opentargets.org/), [ChEMBL](https://www.ebi.ac.uk/chembl/), [Open Targets Platform](https://platform.opentargets.org/)
