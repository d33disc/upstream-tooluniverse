"""
PMC_search_papers

Search for full-text biomedical literature using PMC (PubMed Central) API. PMC is the free full-text archive of biomedical and life sciences journal literature at the U.S. National Institutes of Health's National Library of Medicine.
"""

from typing import Any, Optional, Callable
from tooluniverse import ToolUniverse

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = ToolUniverse()
        _client.load_tools()
    return _client


def PMC_search_papers(
    query: str,
    limit: Optional[int] = 10,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    article_type: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search for full-text biomedical literature using PMC (PubMed Central) API. PMC is the free full-text archive of biomedical and life sciences journal literature at the U.S. National Institutes of Health's National Library of Medicine.

    Parameters
    ----------
    query : str
        Search query for PMC papers. Use keywords separated by spaces to refine your search.
    limit : int
        Maximum number of papers to return. This sets the maximum number of papers retrieved from PMC.
    date_from : str
        Start date for publication date filter (YYYY/MM/DD format). Optional parameter to limit search to papers published from this date onwards.
    date_to : str
        End date for publication date filter (YYYY/MM/DD format). Optional parameter to limit search to papers published up to this date.
    article_type : str
        Article type filter (e.g., 'research-article', 'review', 'case-report'). Optional parameter to limit search to specific article types.
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    list[Any]
    """
    return _get_client().run_one_function(
        {
            "name": "PMC_search_papers",
            "arguments": {
                "query": query,
                "limit": limit,
                "date_from": date_from,
                "date_to": date_to,
                "article_type": article_type,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PMC_search_papers"]
