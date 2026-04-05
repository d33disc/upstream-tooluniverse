# Bibliography Guide

Build `references.bib` from tool call returns. Never hallucinate a reference.

## BibTeX from Tool Results

Extract DOIs from PubMed, OpenAlex, Crossref, Semantic Scholar results.
Write one `@article` entry per source.

```bibtex
@article{Smith2023,
  author  = {Smith, John A. and Doe, Jane B.},
  title   = {Title from the database result},
  journal = {Journal name from the result},
  year    = {2023},
  volume  = {45},
  pages   = {123--130},
  doi     = {10.1234/example.2023.001},
}
```

## Field Mapping by Database

| Database | author | title | journal | year | doi |
| ---------- | -------- | ------- | --------- | ------ | ----- |
| PubMed | `authors` list | `title` | `journal` / `source` | `pub_date` | `doi` or `elocationid` |
| OpenAlex | `authorships[].author.display_name` | `title` | `host_venue.display_name` | `publication_year` | `doi` |
| Crossref | `author[].family, given` | `title[0]` | `container-title[0]` | `published.date-parts[0][0]` | `DOI` |
| Semantic Scholar | `authors[].name` | `title` | `venue` | `year` | `externalIds.DOI` |
| EuropePMC | `authorString` | `title` | `journalTitle` | `pubYear` | `doi` |

## Citation Key Convention

`LastnameYear` -- first author's surname + publication year. If duplicate,
append a/b/c: `Smith2023a`, `Smith2023b`.

## LaTeX Setup

```latex
\usepackage[numbers,super,sort&compress]{natbib}
\bibliographystyle{naturemag}
% ...
\bibliography{references}
```

## Database Citations

Cite databases and tools as `@misc`:

```bibtex
@misc{GeneOntology2024,
  author = {{Gene Ontology Consortium}},
  title  = {Gene Ontology Resource},
  year   = {2024},
  url    = {http://geneontology.org},
  note   = {Accessed 2024-01-15},
}

@misc{UniProt2024,
  author = {{UniProt Consortium}},
  title  = {UniProt: the Universal Protein Knowledgebase},
  year   = {2024},
  url    = {https://www.uniprot.org},
  note   = {Accessed 2024-01-15},
}

@misc{STRING2024,
  author = {Szklarczyk, Damian and others},
  title  = {STRING: functional protein association networks},
  year   = {2024},
  url    = {https://string-db.org},
  note   = {Accessed 2024-01-15},
}

@misc{ClinicalTrials2024,
  title  = {ClinicalTrials.gov},
  author = {{U.S. National Library of Medicine}},
  year   = {2024},
  url    = {https://clinicaltrials.gov},
  note   = {Accessed 2024-01-15},
}
```

## Rules

1. Every `\cite{}` in the paper must have a matching `.bib` entry.
2. Every `.bib` entry must trace to a specific tool call in the SI log.
3. Never invent a reference. If a claim lacks a citable source, flag it.
4. Prefer DOIs over URLs. Use URLs only for databases and grey literature.
5. Include `note = {Accessed YYYY-MM-DD}` for all `@misc` entries.
6. Run `bibtex` after first `lualatex` pass; two more `lualatex` passes
   to resolve all cross-references.
