---
name: tooluniverse-clinical-trial-design
description: Strategic clinical trial design feasibility assessment using ToolUniverse. Evaluates patient population sizing, biomarker prevalence, endpoint selection, comparator analysis, safety monitoring, and regulatory pathways. Creates comprehensive feasibility reports with evidence grading, enrollment projections, and trial design recommendations. Use when planning Phase 1/2 trials, assessing trial feasibility, or designing biomarker-driven studies.
---

# Clinical Trial Design Feasibility Assessment

Systematically assess clinical trial feasibility by analyzing 6 research dimensions. Produces comprehensive feasibility reports with quantitative enrollment projections, endpoint recommendations, and regulatory pathway analysis.

**IMPORTANT**: Always use English terms in tool calls (drug names, disease names, biomarker names), even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

---

## Core Principles

### 1. Report-First Approach (MANDATORY)
**DO NOT** show raw tool outputs to the user. Instead:
1. Create `[INDICATION]_trial_feasibility_report.md` FIRST, with all 14 section headers initialized to `[Researching...]`
2. Progressively fill in each section as tool data arrives
3. Present only the final compiled report

### 2. Evidence Grading

| Grade | Symbol | Criteria |
|-------|--------|----------|
| A | ★★★ | Regulatory acceptance, multiple precedents |
| B | ★★☆ | Clinical validation, single precedent |
| C | ★☆☆ | Preclinical or exploratory |
| D | ☆☆☆ | Proposed, no validation |

### 3. Feasibility Score (0-100)
Weighted composite:
- **Patient Availability** (30%): Population × biomarker prevalence × geography
- **Endpoint Precedent** (25%): Historical use, regulatory acceptance
- **Regulatory Clarity** (20%): Pathway defined, precedents exist
- **Comparator Feasibility** (15%): Standard of care availability
- **Safety Monitoring** (10%): Known risks, monitoring plan established

Interpretation: ≥75 = HIGH (proceed), 50-74 = MODERATE (additional validation), <50 = LOW (de-risk first)

---

## 6-Path Research Workflow

Execute all 6 paths; most can run in parallel.

### PATH 1: Patient Population Sizing
1. Look up the disease EFO ID using `OpenTargets_get_disease_id_description_by_name`
2. Retrieve phenotype/prevalence data with `OpenTargets_get_diseases_phenotypes`
3. Supplement with `PubMed_search_articles` for epidemiology if OpenTargets prevalence is sparse
4. Search `ClinVar_search_variants` (gene + significance) and `gnomAD_search_gene_variants` for biomarker allele frequency
5. Calculate the enrollment funnel explicitly (see below)

**Enrollment funnel math (always show):**
```
US disease incidence/year
× biomarker prevalence %  = biomarker-positive pool
× eligibility factor %    = eligible pool
÷ competing trial dilution = available for enrollment/year
→ Target N / available/year = capture rate needed
```
Example: 200K NSCLC × 15% EGFR+ × 45% L858R × 60% eligible ÷ 3 competing trials = 2,700/year. N=43 requires 1.6% capture — achievable.

### PATH 2: Biomarker Prevalence & Testing
1. Search `COSMIC_search_mutations` for somatic frequency in the specific cancer type
2. Search `ClinVar_search_variants` for clinical significance and pathogenicity
3. Search `PubMed_search_articles` for CDx test performance, FDA approval status, and testing guidelines (turnaround time, cost)
4. Note geographic variation — report US/EU vs. Asian prevalence separately where it differs (e.g., EGFR: 15% Caucasian vs. 50% Asian)
5. Assess tissue biopsy vs. liquid biopsy (ctDNA) feasibility for screening

### PATH 3: Comparator Selection
1. Identify SOC drug(s) from `drugbank_get_indications_by_drug_name_or_drugbank_id`
2. Get pharmacology/mechanism from `drugbank_get_pharmacology_by_drug_name_or_drugbank_id`
3. Check generic availability and patent status via `FDA_OrangeBook_search_drugs`
4. Get approval history and efficacy benchmarks from `FDA_get_drug_approval_history`
5. Evaluate three design options: single-arm vs. historical control, randomized vs. SOC, non-inferiority

### PATH 4: Endpoint Selection
1. Search `search_clinical_trials` (condition + phase=2/3 + status=completed) for precedent endpoints
2. Tally how many completed trials used ORR, PFS, OS, DOR as primary endpoint
3. Use `FDA_get_drug_approval_history` to confirm which endpoints supported approval in this indication
4. Search `PubMed_search_articles` for FDA guidance documents, accelerated approval precedents
5. Document measurement method (RECIST 1.1, irRECIST), imaging modality, assessment frequency, and whether independent review is required

**Sample size guidance:**
- Phase 2 single-arm ORR: Simon 2-stage (N≈43 for H0=10%, H1=30%, α=0.05, β=0.20)
  - Stage 1: N=13; proceed if ≥2 responses
  - Stage 2: N=30 additional
- Phase 1 dose escalation: 3+3 or BOIN design, N=12-18, Cycle 1 DLT window (28 days)

### PATH 5: Safety Endpoints & Monitoring
1. Get mechanism-based toxicity from `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` (use a reference drug from the same class)
2. Pull FDA label warnings with `FDA_get_warnings_and_cautions_by_drug_name`
3. Get real-world AE frequency with `FAERS_count_reactions_by_drug_event` (use UPPERCASE drug name)
4. For more detail: `FAERS_search_reports_by_drug_and_reaction` (limit up to 500)
5. Define DLT criteria, organ-specific monitoring schedule, and Safety Monitoring Committee (SMC) stopping rules

### PATH 6: Regulatory Pathway
1. Use `FDA_get_drug_approval_history` to find ≥3 similar approvals (same indication + endpoint)
2. Search `PubMed_search_articles` for breakthrough therapy designation precedents and FDA guidance documents
3. Evaluate Orphan Drug eligibility: US prevalence <200,000 total. Note: biomarker-defined subsets of common cancers may qualify even if the parent indication does not
4. Assess Breakthrough Therapy criteria: substantial improvement on serious outcome vs. available therapy
5. Outline Pre-IND meeting agenda and IND timeline (Pre-IND request at -4 months, IND at 0, FDA 30-day review, first patient at +1-2 months)

---

## Report Structure (14 Sections)

Create `[INDICATION]_trial_feasibility_report.md` containing all sections below.

**1. Executive Summary** — Date, trial type, primary endpoint, Feasibility Score (0-100), key findings (patient availability, enrollment timeline, endpoint precedent, regulatory pathway, top 3 risks), Go/No-Go recommendation with 2-3 sentence rationale.

**2. Disease Background** — Indication definition, prevalence/incidence with sources, current SOC, unmet need, relevant disease biology.

**3. Patient Population Analysis** — Base population, biomarker selection impact, eligibility criteria funnel table (each criterion with N remaining and % retained), geographic distribution, enrollment projections (assumptions + timeline table).

**4. Biomarker Strategy** — Primary biomarker (prevalence ★★★, assay type, FDA-approved CDx tests, turnaround, cost), alternative biomarkers table, testing logistics (pre-screen vs. screen, central vs. local, tissue vs. ctDNA).

**5. Endpoint Selection & Justification** — Primary endpoint with regulatory precedent count, measurement feasibility (RECIST version, imaging, frequency, independent review), statistical considerations (expected vs. null ORR, sample size, α/β). Secondary endpoints table with evidence grade and rationale. Exploratory endpoints. Endpoint risks and mitigation.

**6. Comparator Analysis** — SOC with approval year ★★★, efficacy benchmarks, limitations. Three design options (single-arm, randomized, non-inferiority) each with pros, cons, feasibility score. Comparator drug sourcing (commercial availability, patent status, cost).

**7. Safety Endpoints & Monitoring Plan** — DLT definition and assessment window (Phase 1). Mechanism-based toxicity table (toxicity, incidence, Grade 3+ rate, monitoring plan) ★★★ from FAERS/label. Organ-specific monitoring (hepatic, cardiac, renal) with baseline, frequency, stopping rules. SMC composition, review frequency, stopping rules.

**8. Study Design Recommendations** — Phase and design type, schema diagram (dose escalation → expansion), eligibility criteria (inclusion/exclusion), treatment plan (dose, modifications, duration, drug interactions), assessment schedule table.

**9. Enrollment & Site Strategy** — Site selection criteria, geographic distribution, enrollment projections with milestone table (first patient, 25%/50%/75%/last patient enrolled, primary analysis), minimum sites required, recruitment strategies.

**10. Regulatory Pathway** — Recommended FDA pathway (505(b)(1), 505(b)(2), Breakthrough, Orphan) with rationale. ≥3 regulatory precedents with drug, indication, year, endpoint, N, and outcome. Relevant FDA guidance documents. Pre-IND meeting recommended topics. IND milestone timeline.

**11. Budget & Resource Considerations** — Cost driver table (protocol, IND prep, site activation, recruitment, biomarker testing, imaging, CRO, data management, statistics) with estimates. Duration and FTE requirements by role.

**12. Risk Assessment** — Feasibility risks table (risk, likelihood, impact, mitigation) covering: slow enrollment, low response rate, unexpected toxicity, comparator supply, regulatory pushback. Scientific risks (unvalidated biomarker hypothesis, patient heterogeneity, resistance mechanisms).

**13. Success Criteria & Go/No-Go Decision** — Phase 1 go criteria (DLT rate, PD biomarker, safety, PK). Simon Stage 1 decision rule. Phase 2 final success criteria (ORR threshold, DoR, PFS, safety, biomarker correlation). Feasibility scorecard table (dimension, weight, raw score, weighted, evidence grade, source).

**14. Recommendations & Next Steps** — Final GO/CONDITIONAL GO/NO-GO with 2-3 paragraph rationale citing specific scores. Critical path to IND (months 0-3, 3-6, 6-9 checklist). Alternative designs (Plan B for slow enrollment, Plan C if single-arm rejected). Long-term development strategy (Phase 3 design, CDx submission, commercial readiness).

---

## Known Gotchas

**OpenTargets prevalence data is often sparse.** `OpenTargets_get_diseases_phenotypes` may return no numeric prevalence. Always cross-check with `PubMed_search_articles` using epidemiology queries (e.g., "NSCLC incidence United States SEER").

**gnomAD is germline only.** For somatic cancer mutations, use `COSMIC_search_mutations` instead of gnomAD allele frequencies. gnomAD is appropriate for germline biomarkers (e.g., BRCA1/2 in hereditary cancers).

**ClinVar variant filtering must be done client-side.** `ClinVar_search_variants` returns all variants for a gene; filter results for the specific mutation of interest (e.g., L858R) after retrieval.

**FAERS requires UPPERCASE drug names.** `FAERS_count_reactions_by_drug_event` and `FAERS_count_death_related_by_drug` require the `medicinalproduct` parameter in all-caps (e.g., "ERLOTINIB" not "erlotinib").

**Orphan Drug math for biomarker-defined subsets.** The orphan threshold is <200,000 US patients total (prevalence, not incidence). A biomarker-selected subset of a common cancer may qualify even if the parent indication does not — calculate this explicitly (e.g., EGFR L858R NSCLC: ~13,500/year new cases, prevalence pool ~40-50K, likely does NOT qualify; but NTRK fusion rare histologies often do).

**Geographic biomarker variation affects enrollment projections.** Always report US/EU vs. Asian prevalence separately. EGFR+ prevalence is ~15% in Caucasian vs. ~50% in Asian NSCLC — including Asian sites can double enrollment speed.

**Screen failure rate compounds with biomarker testing turnaround.** A 7-14 day biomarker test turnaround delays enrollment; model this in the timeline. Liquid biopsy (ctDNA) can enable pre-screening before formal eligibility, reducing delays.

**Single-arm designs require FDA alignment.** Plan a Pre-IND meeting specifically to confirm whether single-arm with historical control is acceptable. Without this, FDA may require randomization before Phase 2 is complete, forcing redesign.

**Simon 2-stage stopping at Stage 1 is binding.** If <2 responses in 13 patients (for H0=10%, H1=30%), the trial must stop for futility — do not allow sponsors to override without statistical justification and protocol amendment.

**Competing trials reduce available patient pool.** Divide the eligible patient pool by an estimated number of competing trials (typically 2-5 for common oncology indications) to get the realistic capture rate. Failure to account for this leads to optimistic enrollment timelines.

---

## Output Requirements

- File name: `[INDICATION]_trial_feasibility_report.md` (e.g., `EGFR_L858R_NSCLC_trial_feasibility_report.md`)
- All 14 sections must be present and populated
- Evidence grade (★★★/★★☆/★☆☆/☆☆☆) on every key claim in sections 1, 4, 5, 6, 7, 10, 13
- Enrollment funnel math shown explicitly in Section 3
- Feasibility scorecard table with calculation shown in Section 13
- Go/No-Go recommendation appears in both Section 1 (summary) and Section 14 (rationale)

---

## Example Use Cases (Quick Reference)

| Scenario | Key Challenge | Typical Feasibility | Design |
|----------|--------------|-------------------|--------|
| EGFR+ NSCLC Phase 2, ORR endpoint | Geographic biomarker variation | HIGH (80+) | Single-arm, Simon 2-stage, N=43 |
| Rare disease (prevalence <3,000 US) | No validated endpoint, tiny pool | MODERATE (55-65) | Single-arm, orphan designation, multi-year enrollment |
| PD-L1 high NSCLC vs. pembrolizumab | Large N for randomized comparison | HIGH (75+) | Randomized 1:1, N=120 for 20% ORR improvement |
| Non-inferiority vs. warfarin | Very large N required | MODERATE (60-70) | N=5,000+, stroke/SE endpoint |
| NTRK basket trial (15 histologies) | <1% fusion rate, broad screening needed | MODERATE (60-65) | Single-arm, 15-20/cohort, tissue-agnostic |

---

## Integration with Other Skills

- **tooluniverse-drug-research**: Investigate mechanism, preclinical data for the investigational drug
- **tooluniverse-disease-research**: Deep dive on disease biology and unmet need
- **tooluniverse-target-research**: Validate drug target and essentiality
- **tooluniverse-pharmacovigilance**: Post-market safety data for the comparator drug
- **tooluniverse-precision-oncology**: Biomarker biology, co-mutations, resistance mechanisms

---

## Tool Quick Reference

Detailed parameter tables: see `references/tools.md`

| Tool | Purpose | Path |
|------|---------|------|
| `OpenTargets_get_disease_id_description_by_name` | Disease EFO ID lookup | 1 |
| `OpenTargets_get_diseases_phenotypes` | Prevalence/phenotype data | 1 |
| `ClinVar_search_variants` | Biomarker pathogenicity, variant list | 1, 2 |
| `ClinVar_get_variant_details` | Single variant details | 2 |
| `gnomAD_search_gene_variants` | Germline allele frequencies | 1 |
| `gnomAD_get_variant_details` | Single variant population frequency | 2 |
| `COSMIC_search_mutations` | Somatic mutation frequency in cancer | 2 |
| `search_clinical_trials` | Precedent trials, endpoints, enrollment data | 1, 3, 4 |
| `PubMed_search_articles` | Epidemiology, CDx guidelines, FDA guidance | 1, 2, 4, 6 |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | Drug identification | 3 |
| `drugbank_get_indications_by_drug_name_or_drugbank_id` | Approved indications, SOC identification | 3 |
| `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` | Mechanism, toxicity profile | 3, 5 |
| `FDA_OrangeBook_search_drugs` | Generic availability, patent status | 3 |
| `FDA_get_drug_approval_history` | Approval precedents, endpoints used | 3, 4, 6 |
| `FDA_get_warnings_and_cautions_by_drug_name` | Boxed warnings, label safety | 5 |
| `FAERS_search_reports_by_drug_and_reaction` | Real-world AE reports (detailed) | 5 |
| `FAERS_count_reactions_by_drug_event` | AE frequency ranking (UPPERCASE name) | 5 |
| `FAERS_count_death_related_by_drug` | Serious/fatal AE summary (UPPERCASE name) | 5 |
