---
name: company-research
description: >-
  Generate dated intelligence briefs on biotech/pharma
  companies for job applications. Covers fresh signals
  (news, SEC filings, hiring), pipeline (clinical trials,
  preprints, publications), and foundation (history,
  research output). Every fact dated, evidence graded
  T1-T3. Use when users ask about a company before an
  interview, need competitive intelligence, or want a
  quick company overview.
---

# Company Research

Generate a structured intelligence brief on a biotech
or pharma company. Fresh signals first, science depth
second, foundation third.

## When to Use This Skill

- "Tell me about [company] before my interview"
- "What is [company] working on right now?"
- "Give me a company brief on [company]"
- Biotech/pharma competitive intelligence
- Job application preparation

## Core Databases Integrated

| Database           | Coverage                       | Tier |
| ------------------ | ------------------------------ | ---- |
| SEC EDGAR          | Public US filings              | T1   |
| ClinicalTrials.gov | 500k+ clinical studies         | T1   |
| FDA Orange Book    | FDA-approved drug products     | T1   |
| PubMed             | 37M+ biomedical citations      | T2   |
| OpenAlex           | 250M+ academic works           | T2   |
| Europe PMC         | 45M+ articles incl. preprints  | T3   |
| Wikipedia          | Company profiles               | T3   |
| Wikidata           | Structured entity data         | T3   |
| Web search         | Real-time news, job postings   | T3   |

## Workflow Overview

```text
Company Name
  -> Phase 0: Disambiguation
  -> Phase 1: Fresh Signals (0-30 days)
  -> Phase 2: Pipeline & Science (1-12 months)
  -> Phase 3: Foundation (1+ years)
  -> Report with evidence grading and sources
```

## Phase 0: Disambiguation

- **Objective**: Resolve name, ticker, CIK, sector
- **Tools Used**:
  - `Wikipedia_search` -- confirm canonical name
  - `SEC_EDGAR_search_filings` -- find CIK/ticker
  - `Wikidata_search_entities` -- sector/description
- **Decision Logic**: No CIK = private company,
  skip SEC phases gracefully

## Phase 1: Fresh Signals (0-30 days)

- **Objective**: What the company is doing right now
- **Tools Used**:
  - `web_search` -- recent news
  - `SEC_EDGAR_search_filings` -- recent filings
  - `web_search` -- hiring signals

## Phase 2: Pipeline & Science (1-12 months)

- **Objective**: Active pipeline and scientific output
- **Tools Used**:
  - `ClinicalTrials_search_studies` -- active trials
  - `EuropePMC_search_articles` -- preprints
  - `PubMed_search_articles` -- publications
  - `FDA_OrangeBook_search_drug` -- approved products

## Phase 3: Foundation (1+ years)

- **Objective**: History, mission, research record
- **Tools Used**:
  - `Wikipedia_get_content` -- company profile
  - `openalex_literature_search` -- research output

## Output Structure

```markdown
# Company Brief: {Name}
Generated: {date} | Ticker | CIK | Sector

## What They're Doing NOW (0-30 days)
### Recent News
### Recent SEC Filings [T1]
### Job Postings & Hiring Signals

## Pipeline & Science (1-12 months)
### Clinical Trials
### Preprints [T3]
### Publications [T2]
### FDA Approved Products [T1]

## Foundation (1+ years)
### Company Profile
### Research Output [T2]

## Data Gaps
## Sources
```

## Evidence Grading

| Tier | Sources                            | Meaning              |
| ---- | ---------------------------------- | -------------------- |
| T1   | SEC, FDA, ClinicalTrials.gov       | Regulatory/official  |
| T2   | Peer-reviewed (PubMed, OpenAlex)   | Validated            |
| T3   | Preprints, news, web, Wikipedia    | Unvalidated/realtime |

## Tool Parameter Reference

| Tool | Key Params | Gotchas |
| ---- | ---------- | ------- |
| `SEC_EDGAR_search_filings` | `query`, `forms`, `startdt` | Returns ALL entity matches |
| `SEC_EDGAR_get_company_submissions` | `cik` (10-digit) | Up to 1000 filings |
| `ClinicalTrials_search_studies` | `query_term`, `page_size` | Fields: `nct_id`, `brief_title` |
| `openalex_literature_search` | `search_keywords` (NOT `query`) | Name collisions |
| `EuropePMC_search_articles` | `query`, `limit` | `SRC:PPR` for preprints |
| `PubMed_search_articles` | `query`, `limit`, `sort` | Fields: `title`, `journal` |
| `Wikipedia_get_content` | `title`, `extract_type` | Exact title match |
| `Wikidata_search_entities` | `search` (NOT `query`) | Returns Q-numbers |
| `web_search` | `query`, `max_results` | Nested response |
| `FDA_OrangeBook_search_drug` | `brand_name`, `limit` | Drug name, not company |

## Fallback Strategies

| Data             | Primary          | Fallback       | Default        |
| ---------------- | ---------------- | -------------- | -------------- |
| Company identity | Wikipedia + SEC  | web_search     | Input name     |
| News             | web_search       | --             | No news found  |
| SEC filings      | SEC_EDGAR        | --             | Skip (private) |
| Clinical trials  | ClinicalTrials   | web_search     | None found     |
| Preprints        | EuropePMC        | --             | None found     |
| Publications     | PubMed           | EuropePMC      | None found     |
| Company profile  | Wikipedia        | web_search     | None found     |
| Research output  | OpenAlex         | Crossref       | None found     |

## Limitations

- SEC EDGAR full-text search returns filings from ANY
  entity mentioning the company, not just filings BY
  the company.
- FDA Orange Book searches by drug brand name, not
  company name. No results for pre-commercial companies.
- OpenAlex keyword search produces false positives for
  common-word names (e.g., "Moderna" matches "modern"
  in Portuguese/Italian).
- Web search depends on DuckDuckGo availability.
- Date filtering depends on upstream API indexing delays.
