---
name: tooluniverse-sequence-retrieval
description: Retrieves biological sequences (DNA, RNA, protein) from NCBI and ENA with gene disambiguation, accession type handling, and comprehensive sequence profiles. Creates detailed reports with sequence metadata, cross-database references, and download options. Use when users need nucleotide sequences, protein sequences, genome data, or mention GenBank, RefSeq, EMBL accessions.
---

# Biological Sequence Retrieval

Retrieve DNA, RNA, and protein sequences with proper disambiguation and cross-database handling.

**IMPORTANT**: Always use English terms in tool calls (gene names, organism names), even if the user writes in another language. Respond in the user's language.

## Workflow

```
Phase 0: Clarify (if needed)
Phase 1: Disambiguate gene/organism → determine accession type
Phase 2: Search & retrieve (silent)
Phase 3: Report sequence profile
```

---

## Phase 0: Clarify Only When Needed

Ask the user ONLY if:
- Gene name exists in multiple organisms (e.g., "BRCA1" → human or mouse?)
- Sequence type unclear (mRNA, genomic, protein?)
- Strain matters (e.g., "E. coli" → which strain?)

Skip clarification if the user provides a specific accession number or clear organism+gene.

---

## Phase 1: Accession Type Decision

**CRITICAL**: Accession prefix determines which tools to use.

| Prefix | Type | Tools |
|--------|------|-------|
| `NC_`, `NM_`, `NR_`, `NP_`, `XM_`, `XR_` | RefSeq | NCBI only |
| `U*`, `M*`, `K*`, `X*`, `CP*`, `NZ_*` | GenBank | NCBI or ENA |
| EMBL format | EMBL | ENA preferred |

**Rule**: Never use ENA tools with RefSeq accessions (NC_, NM_, etc.) — they return 404 errors.

If no accession provided, search NCBI Nucleotide:
- Use `NCBI_search_nucleotide` with: organism (scientific name), gene symbol, strain (if relevant), seq_type (`complete_genome`, `mrna`, `refseq`)
- Convert UIDs to accessions with `NCBI_fetch_accessions`

---

## Phase 2: Retrieve Sequence Data (Internal — Do Not Narrate)

**For any accession**: `NCBI_get_sequence` with format `fasta` or `genbank`
- FASTA: sequence only (use for BLAST, alignment)
- GenBank: sequence + annotations (use for gene analysis)

**For GenBank/EMBL accessions**: also try ENA for richer metadata:
- `ena_get_entry` — entry metadata
- `ena_get_sequence_fasta` — FASTA from ENA
- `ena_get_entry_summary` — summary information

**Fallback chain**:
1. NCBI_get_sequence → if fails → ENA (only for non-RefSeq)
2. NCBI_search_nucleotide finds nothing → broaden search (remove strain, try synonyms)

---

## Phase 3: Report Sequence Profile

Present results as a **Sequence Profile Report**. Do not narrate the search process.

```markdown
# Sequence Profile: [Gene/Organism]

**Search**: [gene] in [organism] | Database: NCBI Nucleotide | Found: [N] sequences

---

## Primary Sequence

### [Accession] — [Definition/Title]

| Attribute | Value |
|-----------|-------|
| Accession | [accession] |
| Type | RefSeq / GenBank |
| Organism | [scientific name] |
| Strain | [strain if applicable] |
| Length | [X,XXX] bp / aa |
| Molecule | DNA / mRNA / Protein |
| Topology | Linear / Circular |
| Curation | ●●● RefSeq (curated) / ●●○ GenBank (submitted) |

### Sequence Preview
```fasta
>[accession] [definition]
ATGCGATCGATCG... [first 100 bp shown; full sequence available via download]
```

### Annotation Summary (from GenBank)
| Feature | Count |
|---------|-------|
| CDS | [N] |
| tRNA | [N] |
| rRNA | [N] |

---

## Alternative Sequences

| Accession | Type | Length | Description | ENA Available |
|-----------|------|--------|-------------|---------------|
| [acc] | RefSeq | [N] bp | [desc] | ✗ |
| [acc] | GenBank | [N] bp | [desc] | ✓ |

---

## Cross-Database References

| Database | Accession |
|----------|-----------|
| RefSeq | [NC_*] |
| GenBank | [U*/CP*] |
| ENA/EMBL | [same as GenBank] |
| BioProject | [PRJNA*] |

---

## Download Options

- **FASTA**: `NCBI_get_sequence(accession="[acc]", format="fasta")`
- **GenBank**: `NCBI_get_sequence(accession="[acc]", format="genbank")`
- **ENA FASTA** (non-RefSeq): `ena_get_sequence_fasta(accession="[acc]")`
```

---

## Curation Tiers

| Symbol | Prefix | Description |
|--------|--------|-------------|
| ●●●● | NC_, NM_, NP_ | NCBI-curated RefSeq — use as reference |
| ●●●○ | XM_, XP_, XR_ | Computationally predicted RefSeq |
| ●●○○ | Various | GenBank validated |
| ●○○○ | Various | GenBank direct submission |

---

## Error Handling

| Error | Action |
|-------|--------|
| "No search criteria provided" | Add organism, gene, or keywords |
| "ENA 404 error" | Accession is RefSeq → use NCBI only |
| "No results found" | Broaden search: remove strain, try gene aliases |
| Sequence too large to display | Show metadata only; provide download instructions |

---

## Tools

| Tool | Purpose |
|------|---------|
| `NCBI_search_nucleotide` | Search by gene/organism/keywords |
| `NCBI_fetch_accessions` | Convert UIDs to accession numbers |
| `NCBI_get_sequence` | Retrieve FASTA or GenBank sequence |
| `ena_get_entry` | ENA entry metadata |
| `ena_get_sequence_fasta` | ENA FASTA retrieval |
| `ena_get_entry_summary` | ENA summary info |
