---
name: tooluniverse
description: Router skill for ToolUniverse tasks. First checks if specialized tooluniverse skills (54 skills covering disease/drug/target research, clinical decision support, genomics, transcriptomics, single-cell analysis, variant analysis, phylogenetics, statistical modeling, image analysis, epigenomics, chemical safety, systems biology, multi-omics integration, proteomics, metabolomics, spatial omics, immune repertoire analysis, and more) can solve the problem, then falls back to general strategies for using 1400+ scientific tools. Covers tool discovery, multi-hop queries, comprehensive research workflows, disambiguation, evidence grading, and report generation. Use when users need to research any scientific topic, find biological data, or explore drug/target/disease relationships.
---

# ToolUniverse Router

## YOUR JOB: Route to the Right Skill, Then Act

When a user asks a question, **do not show this documentation**. Instead:

1. **Check for specialized skills** (routing table below) — if a match exists, invoke it immediately with the Skill tool
2. **If no skill matches**, fall back to general strategies at the bottom of this file
3. **Never describe what you would do** — actually do it

---

## STEP 0: Auto-Install Specialized Skills If Missing

Before doing anything else, check whether the specialized ToolUniverse skills are installed. If not, invoke `tooluniverse-install-skills`, then proceed to step 1.

---

## STEP 1: Route to a Specialized Skill

Scan the routing table. When you find a match, invoke the skill immediately using the Skill tool. Pass the user's full question as the argument.

**Tie-breaking rules:**
- Specificity wins over generality (e.g., "cancer treatment" → precision-oncology, not disease-research)
- "get/retrieve/fetch" queries go to retrieval skills
- If multiple skills match and it is genuinely ambiguous, ask the user to choose

### Data Retrieval

| Keywords | Skill to invoke |
|----------|----------------|
| chemical compound, PubChem, ChEMBL, SMILES, InChI, drug molecule | `tooluniverse-chemical-compound-retrieval` |
| expression data, RNA-seq dataset, ArrayExpress, BioStudies, microarray | `tooluniverse-expression-data-retrieval` |
| protein structure, PDB, AlphaFold, 3D model, crystal structure | `tooluniverse-protein-structure-retrieval` |
| DNA/RNA/protein sequence, NCBI, ENA, FASTA | `tooluniverse-sequence-retrieval` |

### Research & Profiling

| Keywords | Skill to invoke |
|----------|----------------|
| research / profile a disease, syndrome, disorder, illness | `tooluniverse-disease-research` |
| multiomic disease characterization, molecular profile of disease | `tooluniverse-multiomic-disease-characterization` |
| research / profile a drug, medication, therapeutic agent | `tooluniverse-drug-research` |
| literature review, papers about, publications on, synthesize research | `tooluniverse-literature-deep-research` |
| research / profile a target, protein target, gene target, tell me about [protein/gene] | `tooluniverse-target-research` |

### Clinical Decision Support

| Keywords | Skill to invoke |
|----------|----------------|
| drug safety, adverse events, side effects, pharmacovigilance, FAERS | `tooluniverse-pharmacovigilance` |
| adverse event detection, AE prediction, safety signal | `tooluniverse-adverse-event-detection` |
| chemical safety, toxicity prediction, ADMET, environmental toxicity | `tooluniverse-chemical-safety` |
| cancer treatment, precision oncology, tumor mutation, targeted therapy | `tooluniverse-precision-oncology` |
| cancer variant, somatic mutation interpretation, oncogenic variant | `tooluniverse-cancer-variant-interpretation` |
| clinical trial matching, trial eligibility, match patient to trial | `tooluniverse-clinical-trial-matching` |
| immunotherapy response, checkpoint inhibitor, PD-1/PD-L1 biomarkers | `tooluniverse-immunotherapy-response-prediction` |
| rare disease diagnosis, differential diagnosis, phenotype matching, HPO | `tooluniverse-rare-disease-diagnosis` |
| variant interpretation, VUS, pathogenicity, clinical significance | `tooluniverse-variant-interpretation` |
| precision medicine stratification, patient stratification, molecular subtyping | `tooluniverse-precision-medicine-stratification` |
| clinical guidelines, treatment guidelines, standard of care | `tooluniverse-clinical-guidelines` |

### Discovery & Design

| Keywords | Skill to invoke |
|----------|----------------|
| find binders, small molecule discovery, virtual screening, hit identification | `tooluniverse-binder-discovery` |
| drug repurposing, new indication, existing drugs for [disease], repurpose [drug] | `tooluniverse-drug-repurposing` |
| drug target validation, target druggability, target tractability, is [protein] druggable | `tooluniverse-drug-target-validation` |
| design protein, protein binder, de novo protein, RFdiffusion, ProteinMPNN | `tooluniverse-protein-therapeutic-design` |
| antibody engineering, antibody design, humanization, affinity maturation | `tooluniverse-antibody-engineering` |

### Genomics & Variant Analysis

| Keywords | Skill to invoke |
|----------|----------------|
| variant analysis, VCF, mutation annotation, VEP, missense, frameshift | `tooluniverse-variant-analysis` |
| GWAS study, genome-wide association, GWAS catalog, genetic associations | `tooluniverse-gwas-study-explorer` |
| GWAS trait to gene, trait-associated genes, causal genes | `tooluniverse-gwas-trait-to-gene` |
| fine-mapping, finemapping, credible sets, causal variants | `tooluniverse-gwas-finemapping` |
| SNP interpretation, SNP function, rsID, rs[number] annotation | `tooluniverse-gwas-snp-interpretation` |
| polygenic risk, PRS, genetic risk score | `tooluniverse-polygenic-risk-score` |
| structural variant, SV, CNV, deletion, duplication, chromosomal rearrangement | `tooluniverse-structural-variant-analysis` |
| GWAS drug discovery, genetic target validation, GWAS to drug | `tooluniverse-gwas-drug-discovery` |

### Systems & Network Analysis

| Keywords | Skill to invoke |
|----------|----------------|
| protein interactions, PPI, interactome, binding partners | `tooluniverse-protein-interactions` |
| systems biology, pathway analysis, network analysis, gene set enrichment | `tooluniverse-systems-biology` |
| gene enrichment, pathway enrichment, GO, KEGG, Reactome, GSEA, ORA | `tooluniverse-gene-enrichment` |
| metabolomics, metabolite identification, metabolic pathway | `tooluniverse-metabolomics` |
| epigenomics, transcription factor binding, enhancers, chromatin, ATAC-seq, ChIP-seq | `tooluniverse-epigenomics` |
| network pharmacology, drug-target network, polypharmacology, systems pharmacology | `tooluniverse-network-pharmacology` |

### Omics Analysis

| Keywords | Skill to invoke |
|----------|----------------|
| RNA-seq, differential expression, DESeq2, DEG, count matrix, bulk RNA-seq | `tooluniverse-rnaseq-deseq2` |
| single-cell, scRNA-seq, cell clustering, UMAP, scanpy, Seurat, marker genes | `tooluniverse-single-cell` |
| proteomics, protein quantification, mass spec, peptide identification | `tooluniverse-proteomics-analysis` |
| metabolomics analysis, untargeted metabolomics, metabolite profiling, peak annotation | `tooluniverse-metabolomics-analysis` |
| spatial transcriptomics, Visium, spatially resolved expression, spot-level | `tooluniverse-spatial-transcriptomics` |
| spatial omics, imaging mass cytometry, CODEX, multiplexed imaging | `tooluniverse-spatial-omics-analysis` |
| multi-omics integration, integrate omics, cross-omics, combine RNA-seq and proteomics | `tooluniverse-multi-omics-integration` |
| immune repertoire, TCR-seq, BCR-seq, V(D)J, CDR3, clonotype analysis | `tooluniverse-immune-repertoire-analysis` |

### Functional Genomics & Screening

| Keywords | Skill to invoke |
|----------|----------------|
| CRISPR screen, genetic screen, MAGeCK, essential genes, screen hits | `tooluniverse-crispr-screen-analysis` |
| drug-drug interaction, DDI, drug combination, polypharmacy | `tooluniverse-drug-drug-interaction` |

### Specialized Analysis

| Keywords | Skill to invoke |
|----------|----------------|
| phylogenetics, phylogenetic tree, treeness, RCV, PhyKIT, Newick, alignment | `tooluniverse-phylogenetics` |
| statistical modeling, regression, logistic regression, Cox PH, survival analysis, Kaplan-Meier | `tooluniverse-statistical-modeling` |
| image analysis, microscopy, cell counting, colony morphometry, fluorescence quantification | `tooluniverse-image-analysis` |
| infectious disease, pathogen, outbreak, emerging infection, novel virus | `tooluniverse-infectious-disease` |
| clinical trial design, trial protocol, study design, endpoint selection | `tooluniverse-clinical-trial-design` |

### Infrastructure & Development

| Keywords | Skill to invoke |
|----------|----------------|
| setup, install ToolUniverse, configure MCP, API keys, how to install | `setup-tooluniverse` |
| Python SDK, programmatic access, use ToolUniverse in Python, build AI scientist | `tooluniverse-sdk` |
| create skill, new skill, build skill, add skill, write a skill | `create-tooluniverse-skill` |
| create tool, new tool, add tool, wrap API, register tool, local tool | `tooluniverse-custom-tool` |

---

## STEP 2: If No Skill Matches — General Strategies

Use the following strategies only when no specialized skill from the routing table applies.

### Access Modes

| Mode | When | Command |
|------|------|---------|
| MCP server | AI assistants (Claude Desktop, Cursor, Windsurf) | `tu serve` |
| `tu` CLI | Terminal / shell | `tu list`, `tu find "query"`, `tu run ToolName key=val`, `tu grep pattern`, `tu info ToolName` |
| Python SDK | Scripts, notebooks | `from tooluniverse import ToolUniverse; tu = ToolUniverse()` |

### Fallback Workflow When No Skill Exists

1. Acknowledge that no specialized skill covers the topic
2. Run `Tool_Finder` / `Tool_Finder_Keyword` queries to discover relevant tools — actually execute them
3. If tools exist, build a multi-hop workflow and execute it
4. If no tools exist, offer to build one: `create-tooluniverse-skill` (workflow) or `tooluniverse-custom-tool` (single API wrapper)

Known gaps with suggested fallbacks:

| Topic | Fallback |
|-------|----------|
| Methylation analysis, DMR | Use `tooluniverse-epigenomics` for regulatory context; search for methylation tools (RnBeads, DSS) |
| Microbiome, 16S, metagenomics | Search Tool_Finder for "microbiome", "16S" |
| Lipidomics | Use `tooluniverse-metabolomics-analysis` as closest match |
| Glycomics, glycosylation | Search Tool_Finder for "glycan" |
| Flow cytometry / FACS | Use `tooluniverse-image-analysis` or search Tool_Finder |

### Core Operating Principles

1. **Search widely** — run multiple Tool_Finder queries with synonyms; don't assume you know all tools
2. **Query multiple databases** — cross-reference data across sources (e.g., UniProt + Proteins API + NCBI for proteins)
3. **Multi-hop persistence** — chain 5–10 tool calls for comprehensive answers; a single call is rarely enough
4. **Never give up** — if a tool fails, try alternatives; document what was unavailable rather than omitting it
5. **Comprehensive reports** — cite every data point with its source; use evidence grading (T1 mechanistic → T4 review mention)
6. **English-first queries** — translate all tool calls to English; respond back in the user's language
7. **Parallelize when possible** — run independent queries simultaneously for speed
8. **Clarify before acting** — if the entity or scope is ambiguous, ask one focused question covering all ambiguities

### Multi-Hop Patterns

**ID resolution chain**: Name → canonical ID → data → related data (e.g., gene symbol → Ensembl → UniProt → structure)

**Cross-database enrichment**: Primary data → cross-reference → enriched view (e.g., drug name → PubChem CID → ChEMBL ID → bioactivity → ADMET)

**Network expansion**: Seed entity → connected entities → entity details (e.g., gene → PPI network → disease associations for each interactor)

**Literature integration**: Database annotations → literature evidence → synthesized findings

### Cross-Skill Workflow Templates

When a request spans multiple domains, chain specialized skills sequentially, passing outputs forward:

| Workflow | Skills to chain |
|----------|----------------|
| GWAS to therapeutics | gwas-trait-to-gene → target-research → gene-enrichment → drug-repurposing |
| Variant to clinical action | variant-analysis → variant-interpretation → precision-oncology → pharmacovigilance |
| Multi-omics disease profile | disease-research → rnaseq-deseq2 → epigenomics → variant-analysis → multi-omics-integration → gene-enrichment → drug-repurposing |
| Protein to drug | target-research → protein-structure-retrieval → binder-discovery → chemical-safety → literature-deep-research |
| Single-cell to therapeutics | single-cell → target-research → drug-repurposing |
| SV clinical report | variant-analysis → target-research → literature-deep-research |

Trigger words for workflow mode: "from X to Y", "comprehensive analysis", "integrate X and Y", "end-to-end pipeline".

---

## Summary: What You Must Do

| Situation | Your action |
|-----------|-------------|
| User question arrives | Immediately scan routing table for keyword matches |
| 1 clear skill match | Invoke that skill with the Skill tool — do not describe it |
| Multiple skill matches, ambiguous | Ask user to choose with AskUserQuestion |
| No skill match | Execute general strategies — run actual tool queries |
| Ambiguous entity or scope | Ask one clarifying question covering all ambiguities |
| Tool fails | Try fallback alternatives; document what was unavailable |
| Non-English query | Translate to English for tool calls; respond in user's language |

See CHECKLIST.md for a completion checklist applicable to all research tasks.

**THE KEY**: Whatever the outcome, take action. Do not show documentation or describe strategies — execute them.
