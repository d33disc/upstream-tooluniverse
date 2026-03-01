---
name: devtu-optimize-skills
description: Optimize ToolUniverse skills for better report quality, evidence handling, and user experience. Apply patterns like tool verification, foundation data layers, disambiguation-first, evidence grading, quantified completeness, and report-only output. Use when reviewing skills, improving existing skills, or creating new ToolUniverse research skills.
---

# Optimizing ToolUniverse Skills

Best practices for creating high-quality ToolUniverse research skills. These 10 principles come from real failures: skills with excellent documentation but 0-20% functionality because tools were never tested.

---

## Principle 1: Verify Tool Contracts Before Documenting

**Problem**: Tool parameter names differ from function names; skills fail silently.

**Solution**: Before documenting any tool in a skill, verify its actual parameters:
```
mcp__tooluniverse__get_tool_info(tool_names=["TOOL_NAME"], detail_level="full")
```

**Known corrections table** (maintain this in skills using many tools):

| Tool | WRONG (assumed) | CORRECT (tested) |
|------|-----------------|------------------|
| `Reactome_map_uniprot_to_pathways` | `uniprot_id` | `id` |
| `ensembl_get_xrefs` | `gene_id` | `id` |
| `OpenTargets_*` | `ensemblID` | `ensemblId` (camelCase) |
| `gwas_get_associations_for_trait` | `disease_trait="Alzheimer's"` | `efo_id="MONDO_0004975"` |
| `OpenTargets_get_variant_credible_sets` | `variant_id="rs429358"` | `variantId="19_44908684_G_C"` |

**Also check tool existence** — do NOT trust memory for tool names:
```
mcp__tooluniverse__grep_tools(pattern="[suspected_tool_name]")
```

**API quirks to document in skill's "Known Gotchas" section:**
- `p_value=0.0` in GWAS APIs = floating-point underflow (treat as significant, p < 5e-8)
- EFO/MONDO namespace: `EFO_0000249` (Alzheimer's) → 0 results; `MONDO_0004975` → 6,200+
- Co-localized genes: APOE/TOMM40/NECTIN2 share the same GWAS lead SNPs → report as "APOE locus"
- Some tools return direct `[...]` instead of `{status, data}` — check with `isinstance(result, list)`

---

## Principle 2: Foundation Data Layer (Query Aggregators First)

**Problem**: Skills query specialized tools per section, missing data already in comprehensive aggregators.

**Solution**: Add a **Phase 0** that queries domain aggregators FIRST:

| Domain | Foundation Source | What It Provides |
|--------|-------------------|------------------|
| Drug targets | Open Targets | Diseases, drugs, GO, safety, publications, mouse models |
| Chemicals | PubChem | Properties, bioactivity, patents, literature |
| Diseases | Open Targets / OMIM | Genes, drugs, phenotypes, literature |
| Genes | MyGene / Ensembl | Annotations, cross-refs, GO, pathways |

```
Phase 0: Foundation Data (aggregator)
Phase 1: Disambiguation (ID resolution, collision detection)
Phase 2: Specialized Queries (fill gaps)
Phase 3: Report
```

---

## Principle 3: Versioned Identifier Handling

Some APIs require `ENSG00000123456.12` (versioned); others reject it. During disambiguation:
- Capture both versioned and unversioned Ensembl IDs
- Try unversioned first (more portable); if empty, try versioned
- Note which format worked in the skill's documentation

**Common versioned ID APIs**: GTEx, GENCODE, some Ensembl endpoints.

---

## Principle 4: Disambiguation Before Research

Add a disambiguation phase before any literature or data search:

1. Resolve official IDs (UniProt, Ensembl, NCBI Gene, ChEMBL target)
2. Gather synonyms/aliases (all known gene symbols, historical names)
3. Detect naming collisions: search `"[SYMBOL]"[Title]` — if >20% off-topic, build negative filter
4. Get baseline profile from annotation DBs (not literature): domains (InterPro), localization (HPA), expression (GTEx), GO terms

**Why**: Annotation databases provide reliable baseline data even when literature is sparse or noisy.

---

## Principle 5: Report-Only Output (Hide Search Process)

Users want findings, not methodology logs.

**Output files:**
| File | Content | When |
|------|---------|------|
| `[topic]_report.md` | Narrative findings only | Always |
| `[topic]_bibliography.json` | Full deduplicated papers | Always |
| `methods_appendix.md` | Search methodology | Only if requested |

✅ DO: "The literature reveals three main therapeutic approaches..."
❌ DON'T: "I searched PubMed, OpenAlex, and EuropePMC, finding 342 papers..."

---

## Principle 6: Evidence Grading

Apply tiers to every claim in research reports:

| Tier | Symbol | Criteria |
|------|--------|----------|
| T1 | ★★★ | Mechanistic study with direct experimental evidence |
| T2 | ★★☆ | Functional study (knockdown, overexpression, rescue) |
| T3 | ★☆☆ | Association (screen hit, GWAS, expression correlation) |
| T4 | ☆☆☆ | Mention (review, text-mined, peripheral reference) |

Per-section summary:
```markdown
### Theme: Lysosomal Function (47 papers)
**Evidence Quality**: Strong (32 mechanistic, 11 functional, 4 association)

ATP6V1A drives lysosomal acidification [★★★: PMID:12345678].
```

---

## Principle 7: Quantified Completeness

Replace aspirational "include PPIs" with **numeric minimums**:

| Section | Minimum | If Not Met |
|---------|---------|------------|
| PPIs | ≥20 interactors | Explain gaps + which tools failed |
| Expression | Top 10 tissues with TPM values | Note "limited data" |
| Disease links | Top 10 associations with scores | Note if fewer available |
| Constraint scores | All 4 (pLI, LOEUF, missense Z, pRec) | Note which unavailable |
| Literature | Total + 5-year trend + ≥3 key papers | Note if sparse (<50) |

---

## Principle 8: Mandatory Completeness Checklist

Every report section MUST exist, even if populated with "Limited evidence" or "Unknown":

**Identity & Context**: identifiers, synonyms, collisions handled
**Biology**: protein architecture, localization, expression (≥10 tissues), pathways
**Mechanism**: core function with grades, model organism data, key assays
**Disease & Clinical**: variants, constraint scores (all 4), disease links with grades
**Druggability**: tractability for all modalities, known drugs, chemical probes, clinical pipeline
**Synthesis**: research themes (≥3 papers each), open questions, biological model, ≥3 testable hypotheses

---

## Principle 9: Data Gaps Section

Consolidate all failures/gaps in one place at report end:

```markdown
## Data Gaps & Limitations

| Section | Expected | Actual | Reason | Alternative |
|---------|----------|--------|--------|-------------|
| PPIs | ≥20 | 8 | Novel target | Literature review |
| Expression | GTEx TPM | None | Versioned ID failed | See HPA data |
```

**Rule**: NEVER silently skip failed tools. Document in this section.

---

## Principle 10: Collision-Aware Query Strategy

Three-step pattern for literature searches:

1. **High-precision seeds** (15-30 papers): `"[SYMBOL]"[Title] AND mechanism`, `"[UNIPROT_ID]"`
2. **Citation expansion**: forward (cited-by), backward (references), related
3. **Collision-filtered broad**: `"[SYMBOL]" AND [function] NOT [collision_term1]`

**Citation-first for sparse targets**: when keyword search returns <30 papers, prioritize citation expansion from seeds.

**Fallback chains** for flaky tools:

| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `PubMed_get_cited_by` | `EuropePMC_get_citations` | OpenAlex citations |
| `GTEx_*` | `HPA_*` | Note as unavailable |
| `intact_get_interactions` | `STRING_get_protein_interactions` | OpenTargets interactions |

---

## Skill Review Checklist

When reviewing an existing skill for quality:

**Interface & Context**
- [ ] Interface matches execution context:
  - LLM agent / MCP client → `mcp__tooluniverse__execute_tool` calls
  - Python scripts / notebooks → Python SDK (`tu.tools.X()`)
  - Shell / one-off → `tu` CLI
- [ ] Frontmatter description states which interface is expected
- [ ] Code examples in SKILL.md use the correct interface (not a mismatch)

**Tool Contract**
- [ ] Tool names verified to exist (not assumed from memory)
- [ ] Parameters verified via `get_tool_info` or corrections table in skill
- [ ] Known API quirks documented (namespaces, p_value=0.0, co-localization, etc.)
- [ ] Foundation aggregator identified for domain

**Report Quality**
- [ ] Content-focused output (not process logs)
- [ ] Evidence grades applied (T1-T4)
- [ ] Source attribution on every fact
- [ ] All sections present even if "Limited evidence"
- [ ] Data Gaps section exists

**Query & Disambiguation**
- [ ] Disambiguation phase before any search
- [ ] Collision detection for ambiguous names
- [ ] Fallback chains defined for critical tools
- [ ] Failed tools documented, not silently skipped

**Synthesis**
- [ ] Research themes (≥3 papers each, or "limited evidence")
- [ ] Biological model synthesized
- [ ] ≥3 testable hypotheses with experiments
- [ ] Open questions/gaps articulated
