---
name: tooluniverse-literature-deep-research
description: Conduct comprehensive literature research with target disambiguation, evidence grading, and structured theme extraction. Creates a detailed report with mandatory completeness checklist, biological model synthesis, and testable hypotheses. For biological targets, resolves official IDs (Ensembl/UniProt), synonyms, naming collisions, and gathers expression/pathway context before literature search. Default deliverable is a report file; for single factoid questions, uses a fast verification mode and may include an inline answer. Use when users need thorough literature reviews, target profiles, or to verify specific claims from the literature.
---

# Literature Deep Research Strategy

A systematic approach to comprehensive literature research that **starts with target disambiguation** to prevent missing details, uses **evidence grading** to separate signal from noise, and produces a **content-focused report** with mandatory completeness sections.

**KEY PRINCIPLES**:
1. **Target disambiguation FIRST** - Resolve IDs, synonyms, naming collisions before literature search
2. **Right-size the deliverable** - Use *Factoid / Verification Mode* for single answerable questions; full report mode for deep research
3. **Report-first output** - Default deliverable is a report file; inline answer allowed only for Factoid Mode
4. **Evidence grading** - Grade every claim by evidence strength (T1-T4)
5. **Mandatory completeness** - All checklist sections must exist, even if "unknown / limited evidence"
6. **Source attribution** - Every piece of information traceable to a database or tool
7. **English-first queries** - Always use English terms for literature searches and tool calls, even if the user writes in another language. Try original-language terms as a fallback only if English returns no results. Respond in the user's language.

All tool calls in this skill follow the MCP pattern:
`mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})`

---

## Workflow Overview

```
User Query
  |
Phase 0: CLARIFY + MODE SELECT (factoid vs deep report)
  |
Phase 1: TARGET DISAMBIGUATION + PROFILE (default ON for biological targets)
  |- Resolve official IDs (Ensembl, UniProt, HGNC)
  |- Gather synonyms/aliases + known naming collisions
  |- Get protein domains, subcellular location, expression, GO terms, pathways
  `- Output: Target Profile section + Collision-aware search plan
  |
Phase 2: LITERATURE SEARCH
  |- High-precision seed queries (build mechanistic core)
  |- Citation network expansion from seeds
  |- Collision-filtered broader queries
  `- Theme clustering + evidence grading
  |
Phase 3: REPORT SYNTHESIS
  |- Progressive writing to [topic]_report.md
  |- Mandatory completeness checklist validation
  `- Biological model + testable hypotheses
  |
Optional: methods_appendix.md (only if user requests)
```

---

## Phase 0: Initial Clarification

### Mandatory Questions

1. **Target type**: Is this a biological target (gene/protein), a general topic, or a disease?
2. **Scope**: Single factoid to verify or a comprehensive/deep review?
3. **Known aliases**: Any specific gene symbols or protein names you use?
4. **Constraints**: Open access only? Include preprints? Specific organisms?
5. **Methods appendix**: Do you want methodology details in a separate file?

### Mode Selection (CRITICAL)

Pick exactly one mode based on the user's intent:

1. **Factoid / Verification Mode** - single concrete question; answer is a short phrase or sentence
2. **Mini-review Mode** - narrow topic; 1-3 pages of synthesis
3. **Full Deep-Research Mode** - full 15-section template + completeness checklist

**Heuristic**:
- "Which antibiotic was used?" or "Which year?" → **Factoid / Verification Mode**
- "What does the literature say about X?" → **Full Deep-Research Mode**

### Factoid / Verification Mode (Fast Path)

**Goal**: Correct, source-verified single answer with explicit evidence attribution.

**Deliverables**:
- `[topic]_factcheck_report.md` (1 page max)
- `[topic]_bibliography.json` (+ CSV) with the key paper(s)

**Fact-check report template**:
```markdown
# [TOPIC]: Fact-check Report

*Generated: [Date]*

## Question
[User question]

## Answer
**[One-sentence answer]** [Evidence: T1 ★★★ / T2 ★★☆ / T3 ★☆☆ / T4 ☆☆☆]

## Source(s)
- [Citation: journal / year / PMID / DOI as available]

## Verification Notes
- [1-3 bullets: where in the paper the statement appears and any key constraints]

## Limitations
- [If full text not available, or if only review evidence exists]
```

**Required verification behavior**:
- Prefer ToolUniverse literature tools (Europe PMC / PubMed / PMC / Semantic Scholar) over general web browsing.
- Use full-text snippet verification when possible (see Full-Text Verification Strategy, Phase 2.3).
- Do not add extra claims ("not X") unless the paper explicitly supports them.

**Evidence grading (factoid)**:
- Statement in a primary experimental paper (Results / Methods / Abstract): **T1 ★★★**
- Statement found only in a review: **T4 ☆☆☆** - try to locate the primary source before accepting it

### Detect Target Type

| Query Pattern | Type | Action |
|---------------|------|--------|
| Gene symbol (EGFR, TP53, ATP6V1A) | Biological target | Phase 1 required |
| Protein name ("V-ATPase", "kinase") | Biological target | Phase 1 required |
| UniProt ID (P00533, Q93050) | Biological target | Phase 1 required |
| Disease, pathway, method | General topic | Phase 1 optional |
| "Literature on X" | Depends on X | Assess X |

---

## Phase 1: Target Disambiguation + Profile (Default ON)

**CRITICAL**: This phase prevents missed literature when names are ambiguous or deprecated.

### 1.1 Resolve Official Identifiers

Call these tools to establish canonical identity before any literature search:

- **`UniProt_search`** - find the UniProt accession for the human protein
- **`UniProt_get_entry_by_accession`** - full entry with cross-references
- **`UniProt_id_mapping`** - map between ID types (e.g., UniProt AC to Ensembl)
- **`ensembl_lookup_gene`** - Ensembl gene ID and biotype
- **`MyGene_get_gene_annotation`** - NCBI Gene ID, aliases, summary

**Output for report** - a Target Identity table:

| Identifier | Value | Source |
|------------|-------|--------|
| Official Symbol | ATP6V1A | HGNC |
| UniProt | P38606 | UniProt |
| Ensembl Gene | ENSG00000114573 | Ensembl |
| NCBI Gene ID | 523 | NCBI |

Include Full Name and all Synonyms/Aliases gathered.

### 1.2 Identify Naming Collisions

**CRITICAL**: Many gene names have collisions. Examples:
- **TRAG**: T-cell regulatory gene vs bacterial TraG conjugation protein
- **CAT**: catalase vs chloramphenicol acetyltransferase
- **JAK**: Janus kinase vs "Just Another Kinase" (older literature)

**Detection strategy**:
1. Call `PubMed_search_articles` with `"[SYMBOL]"[Title]`, limit 20 results
2. If more than 20% of titles are off-topic, identify the collision terms
3. Build a negative filter: `NOT [collision_term1] NOT [collision_term2]`

Document collisions and the filter used in the report.

### 1.3 Protein Architecture and Domains

Call annotation tools (not literature search) to get:
- **`InterPro_get_protein_domains`** - domain architecture with InterPro IDs
- **`UniProt_get_ptm_processing_by_accession`** - PTMs and active sites
- **`alphafold_get_prediction`** - AlphaFold structure availability
- **`proteins_api_get_protein`** - additional protein features

Report a table of domains (name, position range, InterPro ID, function), isoforms, and key active/binding sites.

### 1.4 Subcellular Location

- **`HPA_get_subcellular_location`** - Human Protein Atlas localization data
- **`UniProt_get_subcellular_location_by_accession`** - UniProt annotation

Report a table of locations with confidence and source.

### 1.5 Baseline Expression

- **`GTEx_get_median_gene_expression`** - tissue expression in TPM
- **`HPA_get_rna_expression_by_source`** - HPA expression data

Report top tissues with TPM values and tissue specificity score.

### 1.6 GO Terms and Pathway Placement

- **`GO_get_annotations_for_gene`** - GO annotations (MF, BP, CC)
- **`Reactome_map_uniprot_to_pathways`** - Reactome pathways
- **`kegg_get_gene_info`** - KEGG pathways
- **`OpenTargets_get_target_gene_ontology_by_ensemblID`** - Open Targets GO

Report GO terms by category with evidence codes, and pathway memberships.

---

## Phase 2: Literature Search

**NOTE**: This methodology stays internal. The report shows findings, not process details.

### 2.1 Query Strategy: Three-Step Collision-Aware Plan

#### Step 1: High-Precision Seed Queries (Build Mechanistic Core)

Use these query patterns with `PubMed_search_articles` or `EuropePMC_search_articles`:
- `"[GENE_SYMBOL]"[Title] AND (mechanism OR function OR structure)`
- `"[FULL_PROTEIN_NAME]"[Title]`
- `"[UNIPROT_ID]"` (catches supplementary materials)

**Goal**: 15-30 high-confidence, mechanistic papers that are definitely on-target.

#### Step 2: Citation Network Expansion (Especially for Sparse Targets)

Once you have 5-15 core PMIDs, expand via:

- **`PubMed_get_cited_by`** - papers citing each seed (primary)
- **`EuropePMC_get_citations`** - fallback when PubMed citation lookup fails
- **`PubMed_get_related`** - computationally related papers
- **`EuropePMC_get_references`** - backward citations from seeds

**Citation-first strategy**: For older targets or deprecated terminology, citation network expansion often outperforms keyword searching. Prioritize this step when initial keyword results are sparse.

#### Step 3: Collision-Filtered Broader Queries

Expand coverage while filtering out collision noise:
- Query pattern: `"[GENE_SYMBOL]" AND ([pathway1] OR [pathway2]) NOT [collision_term]`
- Example for bacterial TraG collision: `"TRAG" AND (T-cell OR immune OR cancer) NOT plasmid NOT conjugation NOT bacterial`

Use multiple databases for broad coverage: `openalex_literature_search`, `Crossref_search_works`, `SemanticScholar_search_papers`, `BioRxiv_search_preprints`, `MedRxiv_search_preprints`.

### 2.2 Tool Failure Handling and Fallback Chains

**Retry strategy**: On timeout or error, wait 2 seconds and retry once. If still failing, wait 5 seconds and switch to fallback tool. If fallback also fails, document "Data unavailable" in report.

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `PubMed_get_cited_by` | `EuropePMC_get_citations` | OpenAlex citations |
| `PubMed_get_related` | `SemanticScholar_search_papers` | Keyword search |
| `GTEx_get_median_gene_expression` | `HPA_get_rna_expression_by_source` | Document unavailable |
| `InterPro_get_protein_domains` | UniProt features | Document unavailable |
| `Unpaywall_check_oa_status` | EuropePMC `isOpenAccess` flag | OpenAlex `is_oa` field |

### 2.3 Full-Text Verification Strategy

**When to use**: Abstract alone lacks critical experimental details (exact drug concentrations, cell lines, protocols).

#### Tier 1: Auto-Snippet Mode via Europe PMC (Fastest)

Call `EuropePMC_search_articles` with `extract_terms_from_fulltext` set to 3-5 specific terms. The tool automatically returns snippets from open-access full text for matching articles.

- Best for: quick verification of 1-2 papers, exploratory queries
- Limitations: OA articles only, capped at first 3 OA articles per call, max 5 terms
- Use specific terms: e.g., `["ciprofloxacin", "MIC", "A. baumannii"]` not `["drug", "method"]`

#### Tier 2: Manual Two-Step via Semantic Scholar or ArXiv (Targeted)

Search first with `SemanticScholar_search_papers`, then call `SemanticScholar_get_pdf_snippets` with the open-access PDF URL and specific terms. For ArXiv papers (100% OA), use `ArXiv_get_pdf_snippets` directly with the arXiv ID.

- Best for: thorough review of specific high-value papers, preprint analysis
- Adjust window size: 400-500 chars for Methods, 150-200 chars for quick verification

#### Tier 3: Manual Download (Last Resort)

Use `get_webpage_text_from_url` on the DOI URL only when the paper is both critical and accessible via institutional proxy. Quality varies by publisher.

Use Tier 1 for quick factoid verification or exploratory queries; Tier 2 for specific high-value or preprint papers; Tier 3 only as last resort for critical paywalled content. For systematic reviews, combine Tier 1 (OA papers) and Tier 2 (targeted key papers).

### 2.4 Open Access Handling

**With Unpaywall email configured**: Call `Unpaywall_check_oa_status` for all papers with DOIs.

**Without Unpaywall email**: Use best-effort OA signals:
- Europe PMC: `isOpenAccess` field
- PMC: all PMC papers are OA
- OpenAlex: `is_oa` field

Label in report: `*OA Status: Best-effort (Unpaywall not configured)*`

---

## Phase 3: Evidence Grading

**CRITICAL**: Grade every claim to prevent low-signal mentions from diluting the report.

### Evidence Tiers

| Tier | Label | Description | Example |
|------|-------|-------------|---------|
| **T1** | ★★★ Mechanistic | Direct experimental evidence on the target | CRISPR KO + rescue |
| **T2** | ★★☆ Functional | Functional study showing role (pathway context ok) | siRNA knockdown phenotype |
| **T3** | ★☆☆ Association | Screen hit, GWAS association, correlation | High-throughput screen |
| **T4** | ☆☆☆ Mention | Review mention, text-mined interaction, peripheral | Review article |

### How to Apply in Reports

Inline in narrative: `ATP6V1A is the catalytic subunit for ATP hydrolysis [★★★: PMID:12345678].`

Per theme section, summarize evidence quality: `**Evidence Quality**: Strong (8 mechanistic, 3 functional, 1 association)`

---

## Report Structure: Mandatory Completeness Checklist

**CRITICAL**: The checklist applies to **Full Deep-Research Mode** only. For **Factoid / Verification Mode**, use the short fact-check report from Phase 0.

### Output Files

1. **`[topic]_report.md`** - Main narrative report (Full Deep-Research Mode)
2. **`[topic]_factcheck_report.md`** - Short verification report (Factoid Mode)
3. **`[topic]_bibliography.json`** - Full deduplicated bibliography (always created)
4. **`[topic]_bibliography.csv`** - Same data in tabular format (always created)
5. **`methods_appendix.md`** - Methodology details (ONLY if user requests)

### Report Sections (All Mandatory)

| # | Section | Must Include |
|---|---------|--------------|
| 1 | Target Identity and Aliases | Official IDs, synonyms, collisions handled |
| 2 | Protein Architecture | Domains, isoforms, active sites (or "N/A") |
| 3 | Complexes and Interaction Partners | Interactors with evidence type |
| 4 | Subcellular Localization | Locations with confidence and source |
| 5 | Expression Profile | Top tissues with TPM, cell-type data if available |
| 6 | Core Mechanisms | Molecular function + biological role, evidence-graded |
| 7 | Model Organism Evidence | KO phenotypes, cross-species conservation (or "none found") |
| 8 | Human Genetics and Variants | Constraint scores (pLI/LOEUF), ClinVar, gnomAD, GWAS |
| 9 | Disease Links | Stratified by evidence strength: genetic+functional > association > correlation |
| 10 | Pathogen Involvement | Viral/bacterial interactions (or "none identified") |
| 11 | Key Assays and Readouts | Biochemical, cellular, in vivo |
| 12 | Research Themes | Cluster with >=3 papers/theme; note "limited evidence" otherwise |
| 13 | Open Questions and Research Gaps | Mechanistic unknowns, therapeutic gaps |
| 14 | Biological Model and Testable Hypotheses | 3-5 paragraph model + hypothesis table |
| 15 | Conclusions and Recommendations | Key takeaways, confidence assessment, next steps |

Sections 1-15 must all appear in the report. If data is absent, write the section heading and state "No evidence found" or "N/A - [reason]". Do not omit sections.

### Bibliography File Format

Each entry in `[topic]_bibliography.json` must contain: `pmid`, `doi`, `title`, `authors` (list), `year`, `journal`, `source_databases` (list of databases that returned it), `evidence_tier` (T1-T4), `themes` (list of theme labels), `oa_status` (`"gold"`, `"green"`, `"bronze"`, or `"closed"`), `oa_url` (if available), `citation_count`, `in_core_set` (boolean). A `metadata` block records the query, total papers found, and unique count after deduplication. Generate a matching `[topic]_bibliography.csv` with the same fields.

---

## Theme Extraction Protocol

1. Extract keywords from titles and abstracts of collected papers
2. Cluster into themes using semantic similarity
3. Require minimum 3 papers per theme (default)
4. Label themes with standardized names relevant to the target

**Theme quality thresholds**:
| Papers | Theme Status |
|--------|-------------|
| >=10 | Major theme (full section) |
| 3-9 | Minor theme (subsection) |
| <3 | Note as "limited evidence" or merge with adjacent theme |

---

## Completeness Checklist (Verify Before Delivery)

All items must be checked or explicitly marked "N/A" or "Limited evidence".

**Identity and Context**
- [ ] Official identifiers resolved (UniProt, Ensembl, NCBI, ChEMBL)
- [ ] All synonyms/aliases documented
- [ ] Naming collisions identified and handled
- [ ] Protein architecture described (or N/A stated)
- [ ] Subcellular localization documented
- [ ] Baseline expression profile included

**Mechanism and Function**
- [ ] Core mechanism section with evidence grades
- [ ] Pathway involvement documented
- [ ] Model organism evidence (or "none found")
- [ ] Complexes/interaction partners listed
- [ ] Key assays/readouts described

**Disease and Clinical**
- [ ] Human genetic variants documented
- [ ] Constraint scores with interpretation
- [ ] Disease links with evidence strength grades
- [ ] Pathogen involvement (or "none identified")

**Synthesis**
- [ ] Research themes clustered with >=3 papers each (or noted as limited)
- [ ] Open questions/gaps articulated
- [ ] Biological model synthesized
- [ ] >=3 testable hypotheses with experiments
- [ ] Conclusions with confidence assessment

**Technical**
- [ ] All claims have source attribution
- [ ] Evidence grades applied throughout
- [ ] Bibliography file (JSON + CSV) generated
- [ ] Data limitations documented

---

## Known Gotchas

**Naming collision false negatives**: A gene symbol with no obvious collision word (e.g., "MARCH") can still have off-topic hits (MARCH = month in non-biomedical corpora). Always scan the first 20 PubMed title hits before assuming a symbol is unambiguous.

**PubMed citation lookup flakiness**: `PubMed_get_cited_by` depends on NCBI elink, which returns empty results intermittently even for well-cited papers. Always fall back to `EuropePMC_get_citations` if the result count seems unexpectedly low.

**Europe PMC auto-snippet coverage**: Only ~30-40% of papers in Europe PMC have open-access full text XML. Do not assume silence means the term is absent - it may mean the paper is not OA. Use Tier 2 (Semantic Scholar) for targeted papers when OA snippet is missing.

**UniProt accession vs gene symbol mismatch**: `UniProt_id_mapping` maps IDs between databases but requires exact accessions. If the user provides a gene symbol, call `UniProt_search` first to get the accession, then map.

**GTEx gencode_id format**: GTEx tools require the versioned Ensembl ID in the format `ENSG00000114573.15`. The base Ensembl ID (no version) will return no results. Get the versioned ID from `ensembl_lookup_gene` or `UniProt_get_entry_by_accession`.

**Review vs primary source conflation**: Text-mining tools and some database annotations cite reviews as evidence. Always check whether a T1 or T2 grade is warranted by looking at the original paper type. A claim sourced only from a review is T4 until the primary source is located.

**Empty categories field in profile**: If a profile.yaml specifies `categories: []`, the system treats this as "load all categories" rather than "load nothing". Do not use an empty list as a way to restrict tools.

**Evidence tier inflation**: Screens, proteomics datasets, and DepMap scores are T3 (association) regardless of how large the dataset is. Only upgrade to T2 or T1 when there is a mechanistic follow-up experiment directly on the target.

**Citation network loops**: When expanding citations from a review paper, you will often recover the same seed papers. Deduplicate by PMID before each new round of expansion to avoid redundant calls.

---

## Quick Reference: Tool Categories

See [`references/tools.md`](references/tools.md) for full tool lists and parameter tables organized by category: Literature Search, Citation Tools, Full-Text Snippet Tools, Protein/Gene Annotation, Expression, Pathway and GO, Interaction, Variant and Disease, Open Access.

---

## Communication with User

**Brief progress updates during research**:
- "Resolving target identifiers and gathering baseline profile..."
- "Building core paper set with high-precision queries..."
- "Expanding via citation network..."
- "Clustering themes and grading evidence..."

**When the question looks like a factoid**: Ask once whether the user wants just the verified answer or a full deep-research report. If no preference stated, default to **Factoid / Verification Mode**.

**DO NOT expose**:
- Raw tool outputs
- Deduplication counts
- Search round details
- Database-by-database results

The report is the deliverable. Methodology stays internal.

---

## Summary

This skill produces comprehensive, evidence-graded research reports that:

1. **Start with disambiguation** to prevent naming collisions and missing details
2. **Use annotation tools** to fill gaps when literature is sparse
3. **Grade all evidence** to separate signal from noise
4. **Require completeness** even if stating "limited evidence"
5. **Synthesize into biological models** with testable hypotheses
6. **Separate narrative from bibliography** for scalability
7. **Keep methodology internal** unless explicitly requested

The result is a detailed, actionable research report that reads like an expert synthesis, not a search log.
