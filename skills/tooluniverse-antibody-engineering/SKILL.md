---
name: tooluniverse-antibody-engineering
description: Comprehensive antibody engineering and optimization for therapeutic development. Covers humanization, affinity maturation, developability assessment, and immunogenicity prediction. Use when asked to optimize antibodies, humanize sequences, or engineer therapeutic antibodies from lead to clinical candidate.
---

# Antibody Engineering & Optimization

AI-guided antibody optimization pipeline from preclinical lead to clinical candidate. Covers sequence humanization, structure modeling, affinity optimization, developability assessment, immunogenicity prediction, and manufacturing feasibility.

**KEY PRINCIPLES**:
1. **Report-first** — Create `antibody_optimization_report.md` before any analysis. Update it progressively.
2. **Evidence-graded humanization** — Score based on germline alignment and framework retention.
3. **Developability-focused** — Assess aggregation, stability, PTMs, immunogenicity in every variant.
4. **Structure-guided** — Use AlphaFold/SAbDab structures for CDR analysis.
5. **Clinical precedent** — Reference approved antibodies (TheraSAbDab) for validation.
6. **Quantitative scoring** — Developability score 0–100 combining multiple factors.
7. **English-first queries** — Always use English terms in tool calls, even if user writes in another language. Respond in user's language.

---

## When to Use

- "Humanize this mouse antibody sequence"
- "Optimize antibody affinity for [target]"
- "Assess developability of this antibody"
- "Predict immunogenicity risk for [sequence]"
- "Engineer bispecific antibody against [targets]"
- "Reduce aggregation in antibody formulation"
- "Design pH-dependent binding antibody"
- "Analyze CDR sequences and suggest mutations"

---

## Workflow Overview

```
Phase 1 → Input Analysis & Characterization
Phase 2 → Humanization Strategy
Phase 3 → Structure Modeling & Analysis
Phase 4 → Affinity Optimization
Phase 5 → Developability Assessment
Phase 6 → Immunogenicity Prediction
Phase 7 → Manufacturing Feasibility
Phase 8 → Final Report & Recommendations
```

---

## Phase 1: Input Analysis & Characterization

**Goal**: Annotate the input sequence and establish context before any optimization.

1. **Annotate CDRs and framework regions** using IMGT numbering (CDR1: 27–38, CDR2: 56–65, CDR3: 105–117 for both VH and VL). See `references/tools.md` for the full numbering table.

2. **Identify germline genes** — Call `IMGT_search_genes` for IGHV and IGKV/IGLV genes in *Homo sapiens*, then compute identity to the input sequence to find the closest human germline.

3. **Get target antigen information** — Call `UniProt_get_protein_by_accession` to characterize the target (function, disease context, isoforms).

4. **Search clinical precedents** — Call `TheraSAbDab_search_by_target` with the antigen name. Note approved antibodies, their isotypes, and humanization levels. These set the quality benchmark.

5. **Search literature** — Call `PubMed_search` for recent engineering studies on the same target.

**Output**: Write "1. Input Characterization" section to report. Include: sequence lengths, estimated humanness %, closest human germline + identity %, CDR sequences tabulated, target information, and list of approved antibodies targeting the same antigen.

---

## Phase 2: Humanization Strategy

**Goal**: Design CDR-grafted humanized variants with optimal human framework selection.

1. **Framework selection** — Call `IMGT_search_genes` for top human germlines, then `IMGT_get_sequence` for each candidate. Score each framework by: (a) sequence identity to mouse FR, (b) CDR canonical class compatibility, (c) clinical precedent usage count. IGHV1-69*01 and IGKV1-39*01 are most commonly used in approved antibodies.

2. **CDR grafting** — Graft mouse CDRs onto the top-scoring human framework. Always graft all 6 CDRs intact initially (CDR preservation = 100%).

3. **Backmutation analysis** — Check Vernier zone positions (2, 27, 29, 30, 47, 48, 67, 71, 78, 93, 94 in IMGT numbering). Where mouse and human differ, flag as backmutation candidates. Positions 27 and 48 are highest priority. Design at least two variants: one with no backmutations (maximum humanness), one with key backmutations (expected better affinity retention).

4. **Calculate humanization score** for each variant: % framework identity to human germline, T-cell epitope content (lower is better), aggregation motif count.

**Output**: Write "2. Humanization Strategy" section. Include: selected frameworks with rationale, Vernier zone table, humanized sequences in FASTA format for each variant, humanness % per variant. Also write to `optimized_sequences.fasta` and `humanization_comparison.csv`.

---

## Phase 3: Structure Modeling & Analysis

**Goal**: Assess 3D structure quality and identify binding epitope.

1. **AlphaFold prediction** — Call `AlphaFold_get_prediction` with the VH:VL sequence (use `":"` as chain separator). Check pLDDT: framework regions should be >88, CDR-H3 often 75–85 (acceptable — it is a flexible loop). If pLDDT <70 anywhere in framework regions, flag as structural concern.

2. **CDR conformation analysis** — Classify CDR loops by canonical class (e.g., H1-13-1, L3-9-cis7-1). Check that humanized variants maintain the same canonical classes as the parent — class switches indicate conformation change and potential affinity loss.

3. **Epitope mapping** — Call `iedb_search_epitopes` with the target protein name or known epitope sequences. Call `SAbDab_search_structures` to find PDB entries of antibody-antigen complexes for the same target. Use these to infer which CDRs dominate the binding interface.

4. **Structural benchmarking** — Compare predicted structure to clinical antibodies from Phase 1. Note VH RMSD, VL RMSD, CDR-H3 RMSD where SAbDab PDB entries are available.

**Output**: Write "3. Structure Modeling" section. Include: pLDDT values by region for each variant, CDR canonical classes, epitope residues, any structural red flags.

---

## Phase 4: Affinity Optimization

**Goal**: Design point mutations to improve binding affinity without sacrificing developability.

1. **Identify interface residues** — From the epitope analysis in Phase 3, determine which CDR residues contact the antigen.

2. **Propose affinity mutations** — For each CDR interface residue, consider:
   - Tyrosine (Y) enrichment: Tyr provides pi-stacking and H-bonds; highest impact per substitution.
   - Salt bridges: Add Asp/Glu near target Arg/Lys or vice versa for electrostatic gain.
   - CDR-H3 extension: Adding 1–2 residues (Gly-Tyr) can fill interface gaps.
   - Trp (W) for deep hydrophobic pockets.

3. **Design testing order**: single mutants first, then combinations of the best 2–3. Report predicted ΔΔG and estimated KD fold-improvement for each.

4. **Affinity ceiling warning** — Target KD of 1–5 nM for most therapeutics. KD <0.1 nM risks target-mediated drug disposition and accelerated clearance; avoid over-optimizing.

5. **pH-dependent binding** (optional) — If tumor-selective uptake or FcRn recycling improvement is desired: introduce His residues at the binding interface. His pKa ~6.0 enables binding at pH 7.4 and release at pH 6.0 (endosomal).

**Output**: Write "4. Affinity Optimization" section. Include: mutation table with predicted ΔΔG and rationale, recommended testing order (single → double → triple), expected KD range for each combination.

---

## Phase 5: Developability Assessment

**Goal**: Score each variant on aggregation, PTM liabilities, stability, expression, and solubility.

1. **Aggregation analysis** — Scan sequence for aggregation-prone regions (APRs). Flag hydrophobic patches and charge clusters. Estimate pI; pI 5.5–7.5 is favorable for purification. Formulation pH should be ≥0.5 units below pI to minimize aggregation.

2. **PTM liability scan** — Check for:
   - Deamidation: NG (high risk), NS (medium risk) — mutate Asn → Gln or Asp
   - Isomerization: DG, DS (high risk) — mutate Asp → Glu
   - Oxidation: exposed Met, Trp — mutate to Leu/Ile or Val/Phe
   - Glycosylation: N-X-S/T where X ≠ Pro — remove from CDRs if present
   PTM sites in CDRs are higher risk than framework because they directly affect binding.

3. **Stability prediction** — Target Tm >70°C, aggregation onset >65°C. Framework humanization typically improves Tm by +2–4°C vs. the mouse parent.

4. **Expression prediction** — Note unusual codon usage, free cysteines (misfolding risk), and extreme pI (purification difficulty). Standard IgG1 in CHO fed-batch should yield >1 g/L.

5. **Calculate overall developability score (0–100)** using weighted components: aggregation 30%, PTM 25%, stability 20%, expression 15%, solubility 10%. Tiers: T1 >75, T2 60–75, T3 <60. See `references/tools.md` for the full rubric.

**Output**: Write "5. Developability Assessment" section. Include: aggregation risk summary, PTM liability table with mitigation mutations, stability predictions, overall score per variant, tier classification. Write `developability_assessment.csv`.

---

## Phase 6: Immunogenicity Prediction

**Goal**: Estimate anti-drug antibody (ADA) risk and propose deimmunization if needed.

1. **T-cell epitope scan** — For each 9-mer window across VH and VL sequences, call `iedb_search_epitopes` with the core peptide. IEDB hits indicate regions with known immunogenic potential. Prioritize hits in non-CDR (framework) regions — these are candidates for deimmunization mutations.

2. **Non-human residue count** — Count framework positions that differ from the selected human germline. More non-human residues correlate with higher immunogenicity.

3. **Calculate immunogenicity risk score** — Combine T-cell epitope count, non-human residue count, and aggregation risk (aggregates are highly immunogenic). See `references/tools.md` for the formula. Target: Low risk (<30).

4. **Deimmunization strategy** — For high-risk framework positions: mutate to human consensus while preserving CDR contacts. Verify each deimmunization mutation does not introduce new PTM sites or reduce predicted Tm.

5. **Compare to clinical precedents** — Reference ADA rates for approved antibodies from TheraSAbDab (e.g., atezolizumab ~30% ADA, durvalumab ~6%, trastuzumab ~13%). Use these as calibration benchmarks.

**Output**: Write "6. Immunogenicity Prediction" section. Include: epitope table with positions and risk levels, risk scores per variant, deimmunization mutations proposed, comparison to clinical ADA rates.

---

## Phase 7: Manufacturing Feasibility

**Goal**: Confirm the lead candidate is manufacturable via standard IgG processes.

1. **Expression system** — Confirm suitability for CHO fed-batch (standard for IgG therapeutics). Note any unusual sequences (free Cys, rare codons, extreme pI >9 or <4) that would require non-standard process.

2. **Purification** — Standard IgG1/IgG4 uses Protein A capture. Confirm Protein A binding is intact (requires intact Fc — if engineering Fab or scFv, state alternative purification). Outline 3-step purification: Protein A → ion exchange polishing → nanofiltration. See `references/tools.md` for details.

3. **Formulation** — Recommend starting formulation: 20 mM Histidine-HCl pH 6.0, 0.02% PS80, 240 mM sucrose. If aggregation risk was flagged in Phase 5, add arginine-glutamate (20–50 mM). Target viscosity ≤15 cP for subcutaneous delivery.

4. **Analytical characterization** — List required ICH release assays: SEC-MALS, CEX, CE-SDS, SPR/BLI (affinity), DSF (Tm), cell-based bioactivity. See `references/tools.md` for specifications.

5. **CMC timeline** — Standard IgG to IND: ~18–24 months ($1.5–2.5M). Cell line development 4–6 months, process development 6–9 months, GMP manufacturing 9–12 months.

**Output**: Write "7. Manufacturing Feasibility" section. Flag any non-standard manufacturing requirements explicitly.

---

## Phase 8: Final Report & Recommendations

**Goal**: Rank all variants, recommend a lead candidate, and define next steps.

1. **Rank all variants** by overall score combining humanness, predicted affinity, developability score, immunogenicity risk, and stability.

2. **Recommend lead candidate** — The variant that best balances all factors for the target's clinical indication. State explicitly which variant is recommended and why.

3. **Identify 2–3 backup variants** — In case the lead fails experimental validation.

4. **Define experimental validation plan**:
   - Phase 1 (months 1–4): SPR/BLI affinity, SEC aggregation, DSF thermal stability, transient CHO expression
   - Phase 2 (months 4–6): stable cell line, scale-up to 500 mg, formulation development
   - Phase 3 (months 7–24): in vivo efficacy, PK/PD, GLP toxicology, IND filing

5. **Note IP considerations** — Flag novel CDR sequences, humanization combinations, and mutation clusters as potentially patentable. Recommend FTO analysis for the target antigen.

**Output**: Finalize `antibody_optimization_report.md` with Executive Summary. Ensure all output files are complete: `optimized_sequences.fasta`, `humanization_comparison.csv`, `developability_assessment.csv`.

---

## Known Gotchas

**IMGT gene searches return many results** — Limit comparison to the top 20 germlines by sequence identity. Do not attempt to score all genes; it is computationally impractical in this pipeline.

**AlphaFold for CDR-H3** — CDR-H3 pLDDT is routinely 75–85 even for well-behaved antibodies. Do not flag pLDDT <85 in CDR-H3 as a problem unless it is below 70.

**VH:VL chain separator for AlphaFold** — Use `":"` (colon) to separate VH and VL sequences. Without the separator, AlphaFold treats the input as a single chain and produces wrong domain assignment.

**IEDB sliding-window immunogenicity** — `iedb_search_epitopes` takes a sequence fragment, not a full antibody sequence. Use 5-residue core sequences from the 9-mer window. Searching with the full sequence will return no results or irrelevant matches.

**TheraSAbDab target names are case-sensitive and formal** — Use the official protein name (e.g., `"PD-L1"` not `"PDL1"` or `"programmed death ligand 1"`). If the first query returns empty, try the UniProt gene name.

**Backmutation vs. humanness trade-off** — Every backmutation reduces the humanness % score. Always present both the fully-humanized variant (max humanness) and the backmutated variant (expected better affinity). Let experimental data decide.

**PTM sites in CDRs are critical** — An NG deamidation motif in CDR-H2 is far more damaging than the same motif in FR3. The CDR residue directly contacts antigen; deamidation alters binding. Always prioritize PTM mitigation in CDR regions.

**Affinity ceiling** — Do not chase KD below 0.1 nM. Below 0.1 nM the binding is essentially irreversible and leads to target-mediated drug disposition, increasing clearance and reducing efficacy at low doses.

**Bispecific antibody aggregation** — Bispecifics have significantly higher aggregation risk than monospecifics. Run `STRING_get_interactions` to validate that the two targets are co-expressed in the relevant tissue before committing to a bispecific design.

**IMGT accessions can change** — If `IMGT_get_sequence` returns an error for a specific accession retrieved from `IMGT_search_genes`, retry with the gene name (e.g., `"IGHV1-69*01"`) directly as the accession parameter.

---

## Completeness Checklist

Before finalizing, confirm:
- [ ] Phase 1: CDRs annotated, germlines identified, clinical precedents found
- [ ] Phase 2: ≥2 humanized variants designed (one full humanization, one with backmutations)
- [ ] Phase 3: AlphaFold predicted, CDR canonical classes checked, epitope mapped
- [ ] Phase 4: Affinity mutations proposed with predicted ΔΔG and testing order
- [ ] Phase 5: Aggregation scored, all PTM sites flagged, developability score (0–100) calculated
- [ ] Phase 6: IEDB epitope scan done, immunogenicity risk score calculated, deimmunization proposed if needed
- [ ] Phase 7: Expression/purification/formulation assessed, any non-standard requirements flagged
- [ ] Phase 8: Lead candidate recommended, backup variants listed, validation plan defined
- [ ] Output files: `optimized_sequences.fasta`, `humanization_comparison.csv`, `developability_assessment.csv`

---

## Tool Reference

| Tool | Purpose |
|------|---------|
| `IMGT_search_genes` | List human germline genes (IGHV, IGKV, IGLV, IGHJ) |
| `IMGT_get_sequence` | Fetch germline sequence by accession |
| `TheraSAbDab_search_by_target` | Find clinical/approved antibodies by antigen name |
| `TheraSAbDab_search_therapeutics` | Find therapeutic antibody details by name |
| `SAbDab_search_structures` | Search PDB antibody structures by target or PDB ID |
| `SAbDab_get_structure` | Get structure details for a specific PDB entry |
| `AlphaFold_get_prediction` | Predict VH/VL structure (VH:VL with colon separator) |
| `iedb_search_epitopes` | Search known T-cell/linear epitopes in IEDB |
| `iedb_search_bcell` | Search B-cell epitopes in IEDB |
| `iedb_search_mhc` | Search MHC-II binding epitopes in IEDB |
| `iedb_get_epitope_references` | Get citations for an IEDB epitope |
| `UniProt_get_protein_by_accession` | Get target antigen details from UniProt |
| `PDB_get_structure` | Retrieve experimental PDB structure |
| `PubMed_search` | Search literature for engineering precedents |
| `STRING_get_interactions` | Protein interactions for bispecific target selection |
| `STRING_get_enrichment` | Pathway enrichment for co-target analysis |

Detailed parameter tables for all tools: `references/tools.md`

---

## Special Considerations

**Bispecific antibody engineering**: Use `STRING_get_interactions` to confirm targets are co-expressed in the disease tissue. Design separate binding arms for each target. Consider asymmetric formats (CrossMAb, DuoBody). Run aggregation assessment twice — once per arm individually, once for the full molecule.

**pH-dependent binding design**: Introduce His residues at the binding interface. His pKa ~6.0 means binding at physiological pH 7.4 and release in endosomes at pH 6.0. Useful for FcRn recycling (improved PK) and tumor targeting (acidic TME). Verify pH-dependent binding does not compromise affinity at pH 7.4 below the target KD threshold.

**Fc engineering (if requested)**: Note that Fc modifications (LALA for effector-null, YTE for extended half-life, GAALIE for enhanced effector) are outside this pipeline's primary scope but should be flagged as next steps when relevant.
