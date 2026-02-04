---
name: devtu-optimize-skills
description: Optimize ToolUniverse skills for better report quality, evidence handling, and user experience. Apply patterns like disambiguation-first, evidence grading, mandatory completeness, and report-only output. Use when reviewing skills, improving existing skills, or creating new ToolUniverse research skills.
---

# Optimizing ToolUniverse Skills

Best practices for creating high-quality ToolUniverse research skills that produce detailed, evidence-graded reports with proper source attribution.

## When to Use This Skill

Apply when:
- Creating new ToolUniverse research skills
- Reviewing/improving existing skills
- User complains about missing details, noisy results, or unclear reports
- Skill produces process-heavy instead of content-heavy output

## Core Optimization Principles

### 1. Disambiguation Before Research

**Problem**: Skills that jump straight to literature search often miss target details or retrieve irrelevant papers due to naming collisions.

**Solution**: Add a disambiguation phase before any literature search:

```markdown
## Phase 1: Target Disambiguation (Default ON)

### 1.1 Resolve Official Identifiers
- UniProt accession (canonical protein)
- Ensembl gene ID (for expression data)
- NCBI Gene ID (for literature)
- ChEMBL target ID (for drug data)

### 1.2 Gather Synonyms and Aliases
- All known gene symbols
- Protein name variants
- Historical names

### 1.3 Detect Naming Collisions
- Search "[SYMBOL]"[Title] - review top 20 results
- If >20% off-topic → identify collision terms
- Build negative filter: NOT [collision1] NOT [collision2]

### 1.4 Get Baseline Profile (from annotation DBs, not literature)
- Protein domains (InterPro)
- Subcellular location (HPA)
- Tissue expression (GTEx)
- GO terms and pathways
```

**Why this works**: Annotation databases provide reliable baseline data even when literature is sparse or noisy.

### 2. Report-Only Output (Hide Search Process)

**Problem**: Users don't want to see "searched 8 databases, found 1,247 papers, deduplicated to 892..."

**Solution**: Output structure:

| File | Content | When |
|------|---------|------|
| `[topic]_report.md` | Narrative findings only | Always (default) |
| `[topic]_bibliography.json` | Full deduplicated papers | Always |
| `methods_appendix.md` | Search methodology | Only if requested |

**In the report**:
- ✅ DO: "The literature reveals three main therapeutic approaches..."
- ❌ DON'T: "I searched PubMed, OpenAlex, and EuropePMC, finding 342 papers..."

### 3. Evidence Grading

**Problem**: A review article mention is treated the same as a mechanistic study with direct evidence.

**Solution**: Apply evidence tiers to every claim:

| Tier | Symbol | Criteria |
|------|--------|----------|
| T1 | ★★★ | Mechanistic study with direct evidence |
| T2 | ★★☆ | Functional study (knockdown, overexpression) |
| T3 | ★☆☆ | Association (screen hit, GWAS, correlation) |
| T4 | ☆☆☆ | Mention (review, text-mined, peripheral) |

**In report**:
```markdown
ATP6V1A drives lysosomal acidification [★★★: PMID:12345678] and has been 
implicated in cancer progression [★☆☆: PMID:23456789, TCGA expression data].
```

**Per-section summary**:
```markdown
### Theme: Lysosomal Function (47 papers)
**Evidence Quality**: Strong (32 mechanistic, 11 functional, 4 association)
```

### 4. Mandatory Completeness Checklist

**Problem**: Reports have inconsistent sections; some topics get skipped entirely.

**Solution**: Define mandatory sections that MUST exist, even if populated with "Limited evidence" or "Unknown":

```markdown
## Completeness Checklist (ALL Required)

### Identity & Context
- [ ] Official identifiers resolved
- [ ] Synonyms/aliases documented
- [ ] Naming collisions handled (or "none detected")

### Biology
- [ ] Protein architecture (or "N/A for non-protein")
- [ ] Subcellular localization
- [ ] Expression profile
- [ ] Pathway involvement

### Mechanism
- [ ] Core function with evidence grades
- [ ] Model organism data (or "none found")
- [ ] Key assays described

### Disease & Clinical
- [ ] Genetic variants
- [ ] Disease links with evidence grades
- [ ] Pathogen involvement (or "none identified")

### Synthesis (CRITICAL)
- [ ] Research themes (≥3 papers each, or "limited")
- [ ] Open questions/gaps
- [ ] Biological model synthesized
- [ ] Testable hypotheses (≥3)
```

### 5. Query Strategy Optimization

**Problem**: Simple keyword searches retrieve too much noise or miss relevant papers.

**Solution**: Three-step collision-aware query strategy:

```markdown
## Query Strategy

### Step 1: High-Precision Seeds
Build a mechanistic core set (15-30 papers):
- "[GENE_SYMBOL]"[Title] AND mechanism
- "[FULL_PROTEIN_NAME]"[Title]
- "UniProt:ACCESSION"

### Step 2: Citation Network Expansion
From seeds, expand via citations:
- Forward: PubMed_get_cited_by, EuropePMC_get_citations
- Related: PubMed_get_related
- Backward: EuropePMC_get_references

### Step 3: Collision-Filtered Broad
Apply negative filters for known collisions:
- "TRAG" AND immune NOT plasmid NOT conjugation
- "JAK" AND kinase NOT "just another"
```

**Citation-first for sparse targets**: When keyword search returns <30 papers, prioritize citation expansion from the few good seeds.

### 6. Tool Failure Handling

**Problem**: NCBI elink and other APIs can be flaky; skills fail silently.

**Solution**: Automatic retry with fallback chains:

```markdown
## Failure Handling

### Retry Protocol
Attempt 1 → fails → wait 2s → Attempt 2 → fails → wait 5s → Fallback

### Fallback Chains
| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| PubMed_get_cited_by | EuropePMC_get_citations | OpenAlex citations |
| PubMed_get_related | SemanticScholar | Keyword search |
| GTEx_* | HPA_* | Note as unavailable |
| Unpaywall | EuropePMC OA flag | OpenAlex is_oa |

### Document Failures
In report: "Expression data unavailable (GTEx API timeout)"
```

### 7. Scalable Output Structure

**Problem**: Reports with 500+ papers become unreadable; users can't find what they need.

**Solution**: Separate narrative from data:

**Narrative report** (~20-50 pages max):
- Executive summary
- Key findings by theme
- Top 20-50 papers highlighted
- Conclusions and hypotheses

**Bibliography files** (unlimited):
- `[topic]_bibliography.json` - Full structured data
- `[topic]_bibliography.csv` - Tabular for filtering

**JSON structure**:
```json
{
  "pmid": "12345678",
  "doi": "10.1038/xxx",
  "title": "...",
  "evidence_tier": "T1",
  "themes": ["lysosomal_function", "autophagy"],
  "is_core_seed": true,
  "oa_status": "gold"
}
```

### 8. Synthesis Sections

**Problem**: Reports describe what was found but don't synthesize into actionable insights.

**Solution**: Require synthesis sections:

```markdown
## Required Synthesis Sections

### Biological Model (3-5 paragraphs)
Integrate all evidence into a coherent model:
- What does the target do?
- How does it connect to disease?
- What's the key uncertainty?

### Testable Hypotheses (≥3)
| # | Hypothesis | Perturbation | Readout | Expected |
|---|------------|--------------|---------|----------|
| 1 | [Hypothesis] | [Experiment] | [Measure] | [Prediction] |

### Suggested Experiments
Brief description of how to test each hypothesis.
```

---

## Skill Review Checklist

When reviewing a ToolUniverse skill, check:

### Report Quality
- [ ] Report focuses on content, not search process
- [ ] Methodology in separate appendix (optional)
- [ ] Evidence grades applied to claims
- [ ] Source attribution on every fact
- [ ] Sections exist even if "limited evidence"

### Query Strategy
- [ ] Disambiguation phase before search
- [ ] Collision detection for ambiguous names
- [ ] High-precision seeds before broad search
- [ ] Citation expansion option for sparse topics
- [ ] Negative filters documented

### Tool Usage
- [ ] Annotation tools used (not just literature)
- [ ] Fallback chains defined
- [ ] Failure handling with retry
- [ ] OA handling (full or best-effort)

### Output Structure
- [ ] Main report is narrative-focused
- [ ] Bibliography in separate JSON/CSV
- [ ] Completeness checklist defined
- [ ] Synthesis sections required

### User Experience
- [ ] Progress updates are brief
- [ ] No raw tool outputs shown
- [ ] Final report is the deliverable

---

## Common Anti-Patterns to Fix

### 1. "Search Log" Reports
**Bad**: "Round 1: Searched PubMed (234 papers), OpenAlex (456 papers)..."
**Fix**: Keep methodology internal; report findings only

### 2. Missing Disambiguation
**Bad**: Search "JAK" and get kinase + "just another kinase" papers mixed
**Fix**: Add collision detection; build negative filters

### 3. No Evidence Grading
**Bad**: "Multiple studies show..." (which studies? what quality?)
**Fix**: Apply T1-T4 grades; label each claim

### 4. Empty Sections Omitted
**Bad**: Skip "Pathogen Involvement" because nothing found
**Fix**: Include section with "None identified in literature search"

### 5. No Synthesis
**Bad**: Long list of papers organized by theme
**Fix**: Add biological model + testable hypotheses

### 6. Monolithic Bibliography
**Bad**: 200 papers embedded in report narrative
**Fix**: Top 20-50 in report; full list in JSON/CSV

### 7. Silent Failures
**Bad**: "Expression data: [blank]" (tool failed, user doesn't know)
**Fix**: "Expression data unavailable (API timeout); see HPA directly"

---

## Template: Optimized Skill Structure

```markdown
---
name: [domain]-research
description: [What it does]. Creates detailed report with evidence grading 
and mandatory completeness. [When to use triggers].
---

# [Domain] Research Strategy

## When to Use
[Trigger scenarios]

## Workflow
Phase 0: Clarify → Phase 1: Disambiguate → Phase 2: Search → Phase 3: Report

## Phase 1: Disambiguation (Default ON)
[ID resolution, collision detection, baseline profile from annotation DBs]

## Phase 2: Literature Search (Internal)
[Query strategy with collision filters, citation expansion, tool fallbacks]

## Phase 3: Report Synthesis
[Progressive writing, evidence grading, mandatory sections]

## Output Files
- `[topic]_report.md` (narrative, always)
- `[topic]_bibliography.json` (data, always)
- `methods_appendix.md` (only if requested)

## Completeness Checklist
[ALL required sections listed]

## Evidence Grading
[T1-T4 definitions]

## Tool Reference
[Tools by category with fallback chains]
```

---

## Quick Fixes for Common Complaints

| User Complaint | Root Cause | Fix |
|----------------|------------|-----|
| "Report is too short" | Missing annotation data | Add Phase 1 disambiguation |
| "Too much noise" | No collision filtering | Add negative query filters |
| "Can't tell what's important" | No evidence grading | Add T1-T4 tiers |
| "Missing sections" | No completeness checklist | Add mandatory sections |
| "Too long/unreadable" | Monolithic output | Separate narrative from JSON |
| "Just a list of papers" | No synthesis | Add biological model + hypotheses |
| "Shows search process" | Wrong output focus | Report-only; methodology in appendix |
| "Tool failed, no data" | No fallback handling | Add retry + fallback chains |

---

## Summary

**Five pillars of optimized ToolUniverse skills**:

1. **Disambiguate first** - Resolve IDs, detect collisions, get baseline from annotation DBs
2. **Grade evidence** - T1-T4 tiers on all claims; summarize quality per section
3. **Require completeness** - Mandatory sections, even if "unknown"
4. **Report content, not process** - Methodology in appendix only if asked
5. **Synthesize** - Biological models and testable hypotheses, not just paper lists

Apply these principles to any ToolUniverse research skill for better user experience and actionable output.
