import os
import threading
import time

import requests
from .base_tool import BaseTool
from .http_utils import request_with_retry
from .tool_registry import register_tool


@register_tool("SemanticScholarTool")
class SemanticScholarTool(BaseTool):
    """
    Tool to search for papers on Semantic Scholar including abstracts.

    API key is read from environment variable SEMANTIC_SCHOLAR_API_KEY.
    Request an API key at: https://www.semanticscholar.org/product/api

    Rate limits:
    - Without API key: 1 request/second
    - With API key: 100 requests/second
    """

    _last_request_time = 0.0
    _rate_limit_lock = threading.Lock()

    def __init__(
        self,
        tool_config,
        base_url="https://api.semanticscholar.org/graph/v1/paper/search",
    ):
        super().__init__(tool_config)
        self.base_url = base_url
        # Get API key from environment as fallback
        self.default_api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def run(self, arguments):
        query = arguments.get("query")
        limit = arguments.get("limit", 5)
        include_abstract = bool(arguments.get("include_abstract", False))
        if not query:
            return [
                {
                    "title": "Error",
                    "abstract": None,
                    "journal": None,
                    "year": None,
                    "url": None,
                    "error": "`query` parameter is required.",
                    "retryable": False,
                }
            ]
        return self._search(query, limit, include_abstract=include_abstract)

    def _enforce_rate_limit(self, has_api_key: bool) -> None:
        # Keep anonymous usage below 1 req/sec to reduce 429s.
        min_interval = 0.02 if has_api_key else 1.05
        with self._rate_limit_lock:
            now = time.time()
            elapsed = now - SemanticScholarTool._last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            SemanticScholarTool._last_request_time = time.time()

    def _fetch_missing_abstract(self, paper_id: str) -> dict | None:
        paper_id = (paper_id or "").strip()
        if not paper_id:
            return None

        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
        params = {"fields": "abstract,externalIds,openAccessPdf"}
        headers = {"x-api-key": self.default_api_key} if self.default_api_key else {}
        self._enforce_rate_limit(bool(self.default_api_key))
        resp = request_with_retry(
            self.session,
            "GET",
            url,
            params=params,
            headers=headers,
            timeout=20,
            max_attempts=3,
        )
        if resp.status_code != 200:
            return None
        try:
            payload = resp.json()
        except ValueError:
            return None
        return payload if isinstance(payload, dict) else None

    def _search(self, query, limit, *, include_abstract: bool = False):
        params = {
            "query": query,
            "limit": limit,
            # Include identifiers and lightweight impact signals for better downstream utility.
            "fields": ",".join(
                [
                    "paperId",
                    "externalIds",
                    "title",
                    "abstract",
                    "year",
                    "venue",
                    "url",
                    "authors",
                    "citationCount",
                    "referenceCount",
                    "isOpenAccess",
                    "openAccessPdf",
                ]
            ),
        }
        headers = {"x-api-key": self.default_api_key} if self.default_api_key else {}
        self._enforce_rate_limit(bool(self.default_api_key))
        response = request_with_retry(
            self.session,
            "GET",
            self.base_url,
            params=params,
            headers=headers,
            timeout=20,
            max_attempts=3,
        )
        if response.status_code != 200:
            return [
                {
                    "title": "Error",
                    "abstract": None,
                    "journal": None,
                    "year": None,
                    "url": None,
                    "error": f"Semantic Scholar API error {response.status_code}",
                    "reason": response.reason,
                    "retryable": response.status_code in (408, 429, 500, 502, 503, 504),
                    "suggestion": "Try again later or set SEMANTIC_SCHOLAR_API_KEY for higher limits.",
                }
            ]
        try:
            payload = response.json()
        except ValueError:
            return [
                {
                    "title": "Error",
                    "abstract": None,
                    "journal": None,
                    "year": None,
                    "url": None,
                    "error": "Semantic Scholar returned invalid JSON",
                    "retryable": True,
                }
            ]

        results = payload.get("data", []) if isinstance(payload, dict) else []
        papers = []
        for p in results:
            # Extract basic information
            external_ids = (
                p.get("externalIds") if isinstance(p.get("externalIds"), dict) else {}
            )
            doi = (
                external_ids.get("DOI")
                if isinstance(external_ids.get("DOI"), str)
                else None
            )
            doi_url = f"https://doi.org/{doi}" if doi else None
            title = p.get("title")
            abstract = p.get("abstract")
            journal = p.get("venue")
            year = p.get("year")
            url = p.get("url")
            paper_id = p.get("paperId") if isinstance(p.get("paperId"), str) else None

            # Handle missing abstract
            if not abstract:
                abstract = None

            # Handle missing journal information
            if not journal:
                journal = None

            authors = []
            raw_authors = p.get("authors", [])
            if isinstance(raw_authors, list):
                for a in raw_authors:
                    if (
                        isinstance(a, dict)
                        and isinstance(a.get("name"), str)
                        and a["name"].strip()
                    ):
                        authors.append(a["name"].strip())

            citation_count = p.get("citationCount")
            reference_count = p.get("referenceCount")
            is_open_access = p.get("isOpenAccess")
            open_access_pdf = (
                p.get("openAccessPdf")
                if isinstance(p.get("openAccessPdf"), dict)
                else None
            )
            open_access_pdf_url = (
                open_access_pdf.get("url")
                if open_access_pdf and isinstance(open_access_pdf.get("url"), str)
                else None
            )

            if include_abstract and not abstract and paper_id:
                details = self._fetch_missing_abstract(paper_id)
                if details:
                    details_external = (
                        details.get("externalIds")
                        if isinstance(details.get("externalIds"), dict)
                        else {}
                    )
                    details_doi = (
                        details_external.get("DOI")
                        if isinstance(details_external.get("DOI"), str)
                        else None
                    )
                    if not doi and details_doi:
                        doi = details_doi
                        doi_url = f"https://doi.org/{doi}"

                    details_abstract = details.get("abstract")
                    if isinstance(details_abstract, str) and details_abstract.strip():
                        abstract = details_abstract.strip()

                    details_open_access_pdf = (
                        details.get("openAccessPdf")
                        if isinstance(details.get("openAccessPdf"), dict)
                        else None
                    )
                    if (
                        not open_access_pdf_url
                        and details_open_access_pdf
                        and isinstance(details_open_access_pdf.get("url"), str)
                    ):
                        open_access_pdf_url = details_open_access_pdf.get("url")

            papers.append(
                {
                    "title": title or "Title not available",
                    "abstract": abstract,
                    "journal": journal,
                    "year": year,
                    "url": url,
                    "paper_id": paper_id,
                    "doi": doi,
                    "doi_url": doi_url,
                    "authors": authors,
                    "citation_count": citation_count,
                    "reference_count": reference_count,
                    "open_access": is_open_access
                    if isinstance(is_open_access, bool)
                    else None,
                    "open_access_pdf_url": open_access_pdf_url,
                    "data_quality": {
                        "has_abstract": bool(abstract),
                        "has_journal": bool(journal),
                        "has_year": bool(year),
                        "has_url": bool(url),
                        "has_doi": bool(doi),
                        "has_authors": bool(authors),
                    },
                }
            )
        return papers
