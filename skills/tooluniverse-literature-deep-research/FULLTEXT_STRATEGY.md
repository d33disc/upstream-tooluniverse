# Full-Text Verification Strategy

Use when abstracts lack critical details (exact values, cell lines, concentrations, protocols, benchmark numbers, hyperparameters, dataset sizes).

**Policy default (2026-05).** Open-access full text + supplement is the default read, not a fallback. For any article cited inline as the anchor for a specific quantitative claim (T1 or T2 tier), the agent MUST attempt Tier 0 before treating the abstract as sufficient.

---

## Table of Contents

1. [Tier 0: Mandatory Full-Text for Load-Bearing Claims](#tier-0-mandatory-full-text-for-load-bearing-claims---default)
2. [Tier 1: Auto-Snippet (Europe PMC)](#tier-1-auto-snippet-europe-pmc---fastest)
3. [Tier 2: Manual Two-Step](#tier-2-manual-two-step---targeted)
4. [Tier 3: Manual Download](#tier-3-manual-download---fallback)
5. [Decision Matrix](#decision-matrix)
6. [Best Practices](#best-practices)

---

## Tier 0: Mandatory Full-Text for Load-Bearing Claims - DEFAULT

**Use for**: every T1 or T2 anchor — any article cited inline as the anchor for a specific quantitative, mechanistic, or structural claim. Default → full text. Fallback → abstract with explicit `abstract-only` tag and tier downgrade (see veracity escalation in `SKILL.md` Phase 3).

### Canonical retrieval sequence

Try in order; stop at first success. Record which source succeeded in the report's "Methods Verification" block.

1. **`EuropePMC_get_full_text`** — when `isOpenAccess=true` in EuropePMC metadata. Broadest OA coverage; returns XML including any `<sec sec-type="supplementary-material">` block.
2. **`PMC_get_full_text`** — when a PMC ID resolves (NIH open-access mandate articles). In practice this is reachable via EuropePMC for any PMC-indexed article; treat as equivalent to step 1 when the article has a PMC ID.
3. **`Unpaywall_check_oa_status`** — to discover the OA URL for articles not flagged OA by EuropePMC; then call `read_url` (Jina) on the returned `best_oa_location.url_for_pdf` or `url`.
4. **`Crossref_search_works`** → `read_url` (Jina) on the publisher landing page. Then scan returned text for a `Supplementary Materials` / `Supporting Information` section and follow the supplement link.
5. **Preprint fallback** — search BioRxiv / MedRxiv for a preprint version of the same paper (`BioRxiv_get_preprint` by DOI, or `EuropePMC_search_articles(query="...", source="PPR")`). Preprints often carry the same supplement as the final version and are reliably open.

### Supplement extraction is mandatory

Page-range notation in the citation tells you whether a supplement exists. **Parse it before deciding the abstract is enough.**

| Notation | Meaning | Action |
|---|---|---|
| `pages: 2918-2933` | No supplement signaled | Pull full text; check end of article for "Supporting Information" anyway |
| `pages: 2918-2933.e17` | 17 supplementary items (figures + tables) | MUST pull supplement; cite each used item by its e-number |
| `pages: 2918-2933.S1-S17` | Supplementary items S1 through S17 | MUST pull supplement; cite by S-number |
| `Article e1234567` | Open-access article-number style | Full text in HTML/XML; supplement usually a separate downloadable file |

When supplement is present, **surface specifically**:

- Structural biology figures (interface residues, binding-pocket views, cryo-EM maps)
- Mouse-model dose-response curves (in vivo PK/PD, tumor regression kinetics)
- Per-patient genotyping breakdowns (resistance allele frequency, co-mutations)
- Compound design schemes (SAR tables, second-generation TCI structures)
- Dose-escalation tables and timing distributions (time-to-resistance, time-to-progression)
- Full statistical tables (n per arm, hazard ratios, exact p-values, confidence intervals)

### Motivating example: Sang et al., Cell 2026 (PMID 42092352)

"Disrupted molecular glue complex drives RAS inhibitor resistance," published 2026-05-14, open access, pages **2918-2933.e17**. The `.e17` marks 17 supplementary items.

The abstract names "RAS Y64, Y71, kinase-dead BRAF" as resistance mechanisms but does NOT enumerate:

- Timing distribution of resistance emergence
- Whether Y64 / Y71 are binding-interface vs activity-modulating
- Whether CYPA-side (vs RAS-side) resistance occurred in the 40-patient cohort
- Time-to-resistance comparison vs Awad NEJM 2021 G12C-OFF

All four sit in the supplement. A page citing this paper as load-bearing for a public investor briefing cannot defensibly read only the abstract — the supplement materially changes the resistance-class classification on a heatmap. Retrieval path: `EuropePMC_get_full_text(article_id="PMC...")` → parse `<sec sec-type="supplementary-material">` → cite `[T1: PMID 42092352, Fig S4, Table S7]` rather than `[T1: PMID 42092352, abstract]`.

### Output discipline

In the report, cite full-text-verified claims with **figure/table/page** anchors, not paragraph-of-abstract anchors:

```markdown
- Resistance mutation Y64 is a CYPA-binding-interface residue [T1: PMID 42092352, Fig S4C, p. e9].
- Mouse-model dose-response: 30 mg/kg drives tumor regression in 6/8 animals [T1: PMID 42092352, Table S7].
```

Abstract-only reads get the explicit tag:

```markdown
- Resistance mutations include Y64, Y71, kinase-dead BRAF [T2: PMID 42092352, abstract-only].
```

---

## Tier 1: Auto-Snippet (Europe PMC) - FASTEST

**Use for**: Exploratory queries with 3-5 specific terms.

```
EuropePMC_search_articles(
    query="bacterial antibiotic resistance evolution",
    limit=10,
    extract_terms_from_fulltext=["ciprofloxacin", "meropenem", "A. baumannii", "MIC"]
)
→ Returns articles with fulltext_snippets[].term and fulltext_snippets[].snippet
```

- Single tool call (search + snippets)
- Bounded latency (max 3 OA articles, ~3-5 seconds)
- Terms processed in batches of 5 internally
- Only works for OA articles with fullTextXML (~30-40% coverage)

---

## Tier 2: Manual Two-Step - TARGETED

**Use for**: Specific high-value papers identified from search.

### Europe PMC Full-Text (broadest OA coverage)

```
EuropePMC_get_fulltext_snippets(
    article_id="PMC1234567",
    terms=["ADAR1", "MDA5", "interferon"],
    window_chars=300
)
→ Returns snippets from specific PMC article

EuropePMC_get_fulltext(article_id="PMC1234567")
→ Returns full-text XML
```

### Semantic Scholar PDF

```
SemanticScholar_get_pdf_snippets(
    open_access_pdf_url="<url from search results>",
    terms=["SHAP", "gradient attribution"],
    window_chars=300
)
→ First search with SemanticScholar_search_papers, then use open_access_pdf_url from results
```

### ArXiv (100% OA)

```
ArXiv_get_pdf_snippets(
    arxiv_id="2301.12345",
    terms=["attention mechanism", "self-attention", "layer normalization"],
    max_snippets_per_term=5
)
→ Works for any arXiv paper (100% coverage)
```

---

## Tier 3: Manual Download - FALLBACK

**Use for**: Paywalled content via institutional access (last resort).

```
get_webpage_text_from_url(url="https://doi.org/10.1016/...")
→ Returns full page text (quality varies by publisher)
```

- Requires institutional access
- No snippet extraction (full HTML)
- Quality varies by publisher

---

## Decision Matrix

| Scenario | Tier | Rationale |
|----------|------|-----------|
| **Load-bearing T1/T2 anchor (any open-access article)** | **0 (Mandatory full text + supplement)** | **Default policy — abstract not sufficient. Parse page-range for supplement.** |
| Open-access paper with `.e<N>` / `.S<N>` page range | 0 (Tier 0 + supplement extraction) | Supplement carries the data tables |
| Quick verification ("Which antibiotic?") | 1 (Auto-snippet) | Fast, single call |
| CS/ML paper on arXiv | 2 (ArXiv) | 100% coverage, use ArXiv_get_pdf_snippets |
| Preprint deep-dive (arXiv, bioRxiv) | 2 (Manual ArXiv) | 100% coverage |
| High-value paper analysis | 2 (Manual S2) | Precise control |
| Systematic review (50+ papers) | 0 + 1 + 2 | Tier 0 for anchors, auto-snippet for breadth, manual for key non-anchor papers |
| Paywalled critical paper | 3 (Manual download) | Only option |

---

## Best Practices

1. **Limit search terms to 3-5 specific keywords**:
   - Bio: `["ciprofloxacin 5 ug/mL", "HEK293 cells", "RNA-seq"]`
   - CS/ML: `["BLEU score", "F1 macro", "learning rate 3e-5"]`
   - Bad: `["drug", "method", "significant"]`

2. **Check OA status before extraction**: Use `isOpenAccess` field from EuropePMC or `open_access_pdf_url` from SemanticScholar.

3. **Adjust window size for context**:
   - Methods: 400-500 chars
   - Quick verification: 150-200 chars
   - Default: 220 chars

4. **Handle failures gracefully**: fall back to abstract or skip.

5. **Document full-text sources in report**:

   ```markdown
   ## Methods Verification

   **Key detail** (verified from full text):
   - Study A: Value X [PMC12345, Methods section]
   - Study B: Value Y [arXiv:2301.12345, Experimental Design]

   *Full-text verification performed on 8/15 OA papers (53% coverage)*
   ```
