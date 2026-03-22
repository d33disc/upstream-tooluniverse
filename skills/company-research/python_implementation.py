#!/usr/bin/env python3
"""Company Research -- biotech/pharma intelligence briefs via ToolUniverse SDK."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path

from tooluniverse import ToolUniverse


def company_research(
    company_name: str,
    output_file: str | None = None,
) -> str:
    """Generate a dated intelligence brief for a biotech/pharma company.

    Args:
        company_name: Company name (e.g., "Moderna", "Recursion Pharmaceuticals").
        output_file: Output markdown path. Auto-generated if None.

    Returns:
        Path to the generated report file.
    """
    tu = ToolUniverse()
    tu.load_tools()

    if output_file is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = company_name.lower().replace(" ", "_")[:30]
        output_file = f"company_brief_{slug}_{ts}.md"

    report: list[str] = []
    sources: list[dict[str, str]] = []
    today = datetime.now().strftime("%Y-%m-%d")

    # ------------------------------------------------------------------
    # Phase 0: Disambiguation
    # ------------------------------------------------------------------
    identity = _disambiguate(tu, company_name, report, sources)

    # ------------------------------------------------------------------
    # Report header
    # ------------------------------------------------------------------
    ticker = identity.get("ticker", "N/A")
    cik = identity.get("cik", "N/A")
    sector = identity.get("sector", "Biotechnology / Pharmaceuticals")
    report.insert(
        0,
        (
            f"# Company Brief: {identity.get('name', company_name)}\n\n"
            f"Generated: {today} | Ticker: {ticker} | CIK: {cik} | Sector: {sector}\n\n"
            "---\n"
        ),
    )

    # ------------------------------------------------------------------
    # Phase 1: Fresh Signals (0-30 days)
    # ------------------------------------------------------------------
    _fresh_signals(tu, company_name, identity, report, sources)

    # ------------------------------------------------------------------
    # Phase 2: Pipeline & Science (1-12 months)
    # ------------------------------------------------------------------
    _pipeline_science(tu, company_name, identity, report, sources)

    # ------------------------------------------------------------------
    # Phase 3: Foundation (1+ years)
    # ------------------------------------------------------------------
    _foundation(tu, company_name, identity, report, sources)

    # ------------------------------------------------------------------
    # Phase 4: Synthesis
    # ------------------------------------------------------------------
    _append_sources(report, sources)

    content = "\n".join(report)
    Path(output_file).write_text(content)
    print(f"Report generated: {output_file} ({len(content)} chars)")
    return output_file


# ======================================================================
# Phase 0: Disambiguation
# ======================================================================


def _disambiguate(
    tu: ToolUniverse,
    name: str,
    report: list[str],
    sources: list[dict[str, str]],
) -> dict[str, str]:
    """Resolve company identity: name, ticker, CIK, sector."""
    identity: dict[str, str] = {"name": name}

    # Wikipedia
    try:
        result = tu.tools.Wikipedia_search(
            query=f"{name} company biotechnology", limit=3
        )
        if isinstance(result, dict):
            results = result.get("results", [])
            if results:
                identity["name"] = results[0].get("title", name)
                sources.append(
                    {
                        "tool": "Wikipedia_search",
                        "query": name,
                        "items": str(len(results)),
                    }
                )
    except Exception:
        pass

    # SEC EDGAR -- find CIK
    try:
        result = tu.tools.SEC_EDGAR_search_filings(query=name, forms="10-K")
        data = _extract_data(result)
        if isinstance(data, list) and data:
            identity["cik"] = data[0].get("cik", "")
            company_str = data[0].get("company", "")
            if "(" in company_str:
                identity["ticker"] = company_str.split("(")[1].split(")")[0]
            sources.append(
                {
                    "tool": "SEC_EDGAR_search_filings",
                    "query": name,
                    "items": str(len(data)),
                }
            )
    except Exception:
        pass

    # Wikidata for structured facts
    try:
        result = tu.tools.Wikidata_search_entities(search=name, limit=3)
        if isinstance(result, dict):
            entities = result.get("results", result.get("search", []))
            if isinstance(entities, list) and entities:
                desc = entities[0].get("description", "")
                if desc:
                    identity.setdefault("sector", desc)
                sources.append(
                    {
                        "tool": "Wikidata_search_entities",
                        "query": name,
                        "items": str(len(entities)),
                    }
                )
    except Exception:
        pass

    return identity


# ======================================================================
# Phase 1: Fresh Signals
# ======================================================================


def _fresh_signals(
    tu: ToolUniverse,
    name: str,
    identity: dict[str, str],
    report: list[str],
    sources: list[dict[str, str]],
) -> None:
    report.append("\n## What They're Doing NOW (0-30 days)\n")

    # News via web search
    report.append("\n### Recent News\n")
    try:
        result = tu.tools.web_search(query=f"{name} biotech news 2026", max_results=10)
        data = _extract_data(result)
        items = _as_list(data)
        if items:
            for item in items[:7]:
                title = _strip_html(item.get("title", "Untitled"))
                href = item.get("href", item.get("url", item.get("link", "")))
                body = _strip_html(item.get("body", item.get("snippet", ""))[:200])
                report.append(f"- **{title}** {f'[link]({href})' if href else ''}\n")
                if body:
                    report.append(f"  {body}\n")
            sources.append(
                {
                    "tool": "web_search",
                    "query": f"{name} news",
                    "items": str(len(items)),
                }
            )
        else:
            report.append("*No recent news found.*\n")
    except Exception:
        report.append("*News search unavailable.*\n")

    # SEC filings (recent)
    cik = identity.get("cik")
    if cik:
        report.append("\n### Recent SEC Filings [T1]\n")
        try:
            ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            result = tu.tools.SEC_EDGAR_search_filings(
                query=name, startdt=ninety_days_ago
            )
            data = _extract_data(result)
            filings = data if isinstance(data, list) else []
            if filings:
                report.append(
                    "| Form | Date | Accession |\n|------|------|-----------|\n"
                )
                seen: set[str] = set()
                for f in filings[:15]:
                    key = f"{f.get('form')}-{f.get('accession')}"
                    if key in seen:
                        continue
                    seen.add(key)
                    report.append(
                        f"| {f.get('form', '')} | {f.get('file_date', '')} "
                        f"| {f.get('accession', '')} |\n"
                    )
                sources.append(
                    {
                        "tool": "SEC_EDGAR_search_filings",
                        "query": f"{name} recent",
                        "items": str(len(filings)),
                    }
                )
            else:
                report.append("*No recent filings found.*\n")
        except Exception:
            report.append("*SEC filing search unavailable.*\n")
    else:
        report.append(
            "\n### SEC Filings\n\n*Company appears to be private -- no SEC filings.*\n"
        )

    # Job postings
    report.append("\n### Job Postings & Hiring Signals\n")
    try:
        result = tu.tools.web_search(
            query=f"{name} careers hiring biotech jobs", max_results=5
        )
        data = _extract_data(result)
        items = _as_list(data)
        if items:
            for item in items[:5]:
                title = _strip_html(item.get("title", "Untitled"))
                href = item.get("href", item.get("url", item.get("link", "")))
                report.append(f"- {title} {f'[link]({href})' if href else ''}\n")
            sources.append(
                {
                    "tool": "web_search",
                    "query": f"{name} careers",
                    "items": str(len(items)),
                }
            )
        else:
            report.append("*No job postings found.*\n")
    except Exception:
        report.append("*Job search unavailable.*\n")


# ======================================================================
# Phase 2: Pipeline & Science
# ======================================================================


def _pipeline_science(
    tu: ToolUniverse,
    name: str,
    identity: dict[str, str],
    report: list[str],
    sources: list[dict[str, str]],
) -> None:
    report.append("\n## Pipeline & Science (1-12 months)\n")

    # Clinical trials
    report.append("\n### Clinical Trials\n")
    try:
        result = tu.tools.ClinicalTrials_search_studies(query_term=name, page_size=10)
        data = _extract_data(result)
        studies = _as_list(data)
        if studies:
            report.append("| NCT ID | Title | Phase | Status |\n")
            report.append("|--------|-------|-------|--------|\n")
            for s in studies[:10]:
                nct = s.get("nct_id", s.get("nctId", ""))
                title = s.get("brief_title", s.get("briefTitle", s.get("title", "")))[
                    :80
                ]
                phases = s.get("phases", s.get("phase", []))
                phase = ", ".join(phases) if isinstance(phases, list) else str(phases)
                status = s.get("status", s.get("overallStatus", ""))
                report.append(f"| {nct} | {title} | {phase} | {status} |\n")
            sources.append(
                {
                    "tool": "ClinicalTrials_search_studies",
                    "query": name,
                    "items": str(len(studies)),
                }
            )
        else:
            report.append("*No clinical trials found.*\n")
    except Exception:
        report.append("*Clinical trials search unavailable.*\n")

    # Preprints via EuropePMC (SRC:PPR)
    report.append("\n### Preprints [T3]\n")
    try:
        result = tu.tools.EuropePMC_search_articles(query=f"{name} SRC:PPR", limit=5)
        data = _extract_data(result)
        articles = _as_list(data)
        if articles:
            for a in articles[:5]:
                title = _strip_html(a.get("title", "Untitled"))
                doi = a.get("doi", "")
                date = a.get("firstPublicationDate", a.get("pubYear", ""))
                link = f"https://doi.org/{doi}" if doi else ""
                report.append(
                    f"- {title} ({date}) {f'[doi]({link})' if link else ''} [T3]\n"
                )
            sources.append(
                {
                    "tool": "EuropePMC_search_articles",
                    "query": f"{name} SRC:PPR",
                    "items": str(len(articles)),
                }
            )
        else:
            report.append("*No preprints found.*\n")
    except Exception:
        report.append("*Preprint search unavailable.*\n")

    # Peer-reviewed publications
    report.append("\n### Publications [T2]\n")
    try:
        result = tu.tools.PubMed_search_articles(query=name, limit=5, sort="pub_date")
        data = _extract_data(result)
        articles = _as_list(data)
        if articles:
            for a in articles[:5]:
                title = _strip_html(a.get("title", "Untitled"))
                pub_date = a.get("pub_date", a.get("pubdate", a.get("pub_year", "")))
                journal = a.get(
                    "journal", a.get("fulljournalname", a.get("source", ""))
                )
                report.append(f"- {title} *{journal}* ({pub_date}) [T2]\n")
            sources.append(
                {
                    "tool": "PubMed_search_articles",
                    "query": name,
                    "items": str(len(articles)),
                }
            )
        else:
            report.append("*No publications found.*\n")
    except Exception:
        report.append("*PubMed search unavailable.*\n")

    # FDA Orange Book
    report.append("\n### FDA Approved Products [T1]\n")
    try:
        result = tu.tools.FDA_OrangeBook_search_drug(brand_name=name, limit=5)
        data = _extract_data(result)
        products = _as_list(data)
        if products:
            for p in products[:5]:
                brand = p.get("brand_name", p.get("trade_name", ""))
                ingredient = p.get("active_ingredient", p.get("ingredient", ""))
                app_no = p.get("application_number", p.get("appl_no", ""))
                report.append(f"- **{brand}** ({ingredient}) -- {app_no} [T1]\n")
            sources.append(
                {
                    "tool": "FDA_OrangeBook_search_drug",
                    "query": name,
                    "items": str(len(products)),
                }
            )
        else:
            report.append("*No FDA-approved products found under this name.*\n")
    except Exception:
        report.append("*FDA search unavailable.*\n")


# ======================================================================
# Phase 3: Foundation
# ======================================================================


def _foundation(
    tu: ToolUniverse,
    name: str,
    identity: dict[str, str],
    report: list[str],
    sources: list[dict[str, str]],
) -> None:
    report.append("\n## Foundation (1+ years)\n")

    # Wikipedia company profile
    wiki_title = identity.get("name", name)
    report.append("\n### Company Profile\n")
    try:
        result = tu.tools.Wikipedia_get_content(
            title=wiki_title, extract_type="summary", max_chars=3000
        )
        if isinstance(result, dict) and result.get("content"):
            report.append(f"{result['content']}\n")
            sources.append(
                {"tool": "Wikipedia_get_content", "query": wiki_title, "items": "1"}
            )
        elif isinstance(result, str) and len(result) > 50:
            report.append(f"{result[:3000]}\n")
        else:
            report.append("*No Wikipedia article found.*\n")
    except Exception:
        report.append("*Wikipedia content unavailable.*\n")

    # Research output via OpenAlex
    report.append("\n### Research Output [T2]\n")
    try:
        result = tu.tools.openalex_literature_search(
            search_keywords=name, max_results=5
        )
        data = _extract_data(result)
        papers = _as_list(data)
        if papers:
            for p in papers[:5]:
                title = p.get("title", "Untitled")
                year = p.get("publication_year", p.get("year", ""))
                cited = p.get("cited_by_count", p.get("citations", ""))
                report.append(f"- {title} ({year}, cited: {cited}) [T2]\n")
            sources.append(
                {
                    "tool": "openalex_literature_search",
                    "query": name,
                    "items": str(len(papers)),
                }
            )
        else:
            report.append("*No research output found in OpenAlex.*\n")
    except Exception:
        report.append("*OpenAlex search unavailable.*\n")


# ======================================================================
# Helpers
# ======================================================================


def _extract_data(result: object) -> object:
    """Unwrap ToolUniverse response -- handles up to 3 levels of nesting."""
    cur = result
    for _ in range(3):
        if not isinstance(cur, dict):
            break
        if cur.get("status") == "success" and "data" in cur:
            cur = cur["data"]
        elif "data" in cur and isinstance(cur["data"], (dict, list)):
            cur = cur["data"]
        else:
            break
    return cur


def _as_list(data: object) -> list:
    """Coerce response data to a list."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("studies", "results", "items", "articles", "data"):
            if isinstance(data.get(key), list):
                return data[key]
        return [data] if data else []
    return []


def _strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text)


def _append_sources(report: list[str], sources: list[dict[str, str]]) -> None:
    """Append sources table to report."""
    report.append("\n## Data Gaps\n")
    report.append("*Review sections marked 'unavailable' or 'No ... found' above.*\n")

    report.append("\n## Sources\n")
    report.append("| Tool | Query | Items |\n|------|-------|-------|\n")
    for s in sources:
        report.append(
            f"| {s['tool']} | {s.get('query', '')} | {s.get('items', '')} |\n"
        )


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "Moderna"
    company_research(target)
