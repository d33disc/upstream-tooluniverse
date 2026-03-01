---
name: tooluniverse-expression-data-retrieval
description: Retrieves gene expression and omics datasets from ArrayExpress and BioStudies with gene disambiguation, experiment quality assessment, and structured reports. Creates comprehensive dataset profiles with metadata, sample information, and download links. Use when users need expression data, omics datasets, or mention ArrayExpress (E-MTAB, E-GEOD) or BioStudies (S-BSST) accessions.
---

# Gene Expression & Omics Data Retrieval

Retrieve gene expression experiments and multi-omics datasets with proper disambiguation and quality assessment.

**IMPORTANT**: Always use English terms in tool calls (gene names, tissue names, condition descriptions), even if the user writes in another language. Respond in the user's language.

## Workflow

```
Phase 0: Clarify query (if ambiguous)
Phase 1: Resolve gene/condition identifiers
Phase 2: Search & retrieve (silent)
Phase 3: Report dataset profile
```

---

## Phase 0: Clarify Only When Needed

Ask only if:
- Gene name is ambiguous (e.g., "p53" → TP53 expression studies, or MDM2?)
- Tissue/condition unclear for comparative studies
- Organism not specified for non-human research

Skip for: specific accession numbers (E-MTAB-*, E-GEOD-*, S-BSST*), clear disease+organism queries, explicit platform requests.

---

## Phase 1: Query Disambiguation

If searching by gene: resolve official symbol first (HGNC for human, MGI for mouse). Include common aliases in the search keywords (e.g., search "TP53 p53" not just "TP53").

| User Query Type | Search Strategy |
|-----------------|-----------------|
| Specific accession | Direct retrieval |
| Gene + condition | "[gene alias1 alias2] [condition]" + species filter |
| Disease only | "[disease]" + species filter |
| Technology-specific | Add platform keywords (RNA-seq, microarray) |

---

## Phase 2: Search & Retrieve (Silent — Do Not Narrate)

**Primary search**:
- `arrayexpress_search_experiments(keywords=<query>, species=<organism>, limit=20)` — gene expression experiments
- `biostudies_search_studies(query=<keywords>, limit=10)` — multi-omics datasets

**Get experiment details** for top results (top 5-10):
- `arrayexpress_get_experiment_details(accession=<E-MTAB-*>)` — full metadata
- `arrayexpress_get_experiment_samples(accession=<acc>)` — sample annotations
- `arrayexpress_get_experiment_files(accession=<acc>)` — download links

**BioStudies details**:
- `biostudies_get_study_details(accession=<S-BSST*>)` — study metadata
- `biostudies_get_study_files(accession=<acc>)` — data files
- `biostudies_get_study_sections(accession=<acc>)` — study structure

**Fallback chain**:
1. ArrayExpress finds nothing → try BioStudies search
2. `arrayexpress_get_experiment_details` fails → try `biostudies_get_study_details` (E-GEOD often mirrors)
3. Files unavailable → note "Data files restricted by submitter"

---

## Phase 3: Report Dataset Profile

Present as **Dataset Search Report**. Do not show search process.

```markdown
# Expression Data: [Query Topic]

**Search**: [gene/disease] in [species] | Databases: ArrayExpress, BioStudies | Found: [N] experiments

---

## Top Experiments

### 1. [E-MTAB-XXXX] — [Title]

| Attribute | Value |
|-----------|-------|
| Accession | [accession] |
| Organism | [species] |
| Type | RNA-seq / Microarray |
| Platform | [platform name] |
| Samples | [N] |
| Release Date | [date] |

**Description**: [Brief description]

**Experimental Design**:
- Conditions: [treatment vs control]
- Replicates: [N biological, M technical]
- Tissue/Cell type: [if specified]

**Sample Groups**:
| Group | N | Description |
|-------|---|-------------|
| Control | [N] | [desc] |
| Treatment | [N] | [desc] |

**Data Files**:
| File | Type |
|------|------|
| [filename] | Processed data |
| [filename] | Raw data |

**Quality**: ●●● High / ●●○ Medium / ●○○ Low
- [Rationale: replicate count, metadata completeness, platform recency]

---

### 2. [E-GEOD-XXXXX] — [Title]
[Same structure]

---

## Multi-Omics Studies (BioStudies)

### [S-BSST-XXXXX] — [Title]
| Attribute | Value |
|-----------|-------|
| Accession | [accession] |
| Study Type | proteomics / metabolomics / integrated |
| Organism | [species] |
| Samples | [N] |

Data types: Transcriptomics ☐ / Proteomics ☐ / Metabolomics ☐

---

## Summary & Recommendations

| Accession | Type | Samples | Quality |
|-----------|------|---------|---------|
| [E-MTAB-X] | RNA-seq | [N] | ●●● |

**Best for [user's purpose]**: [accession] — [reason]

**Data access**:
- [E-MTAB-XXXX]: https://www.ebi.ac.uk/arrayexpress/experiments/[acc]
- [S-BSST-XXXX]: https://www.ebi.ac.uk/biostudies/studies/[acc]
```

---

## Quality Tiers

| Symbol | Criteria |
|--------|----------|
| ●●● High | ≥3 biological replicates, complete metadata, processed data available |
| ●●○ Medium | 2-3 replicates OR some metadata gaps, data accessible |
| ●○○ Low | No replicates, sparse metadata, or data access issues |
| ○○○ Caution | Single sample, no replication, outdated platform |

---

## Error Handling

| Error | Action |
|-------|--------|
| No experiments found | Broaden keywords, remove species filter, try synonyms |
| Accession not found | Verify format (E-MTAB-*, E-GEOD-*, S-BSST*); check if withdrawn |
| Files not available | Note: "Data files restricted by submitter" |
| API timeout | Retry once; then note "(metadata retrieval incomplete)" |

---

## Tools

| Tool | Purpose |
|------|---------|
| `arrayexpress_search_experiments` | Keyword + species search |
| `arrayexpress_get_experiment_details` | Full experiment metadata |
| `arrayexpress_get_experiment_files` | Download links and file sizes |
| `arrayexpress_get_experiment_samples` | Sample annotations |
| `biostudies_search_studies` | Multi-omics keyword search |
| `biostudies_get_study_details` | Study metadata |
| `biostudies_get_study_files` | Data files |
| `biostudies_get_study_sections` | Study structure |
