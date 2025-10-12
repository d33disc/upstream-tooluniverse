"""
openalex_literature_search

Search for academic literature using OpenAlex API. Retrieves papers with title, abstract, authors, publication year, and organizational affiliations based on search keywords.
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


def openalex_literature_search(
    search_keywords: str,
    max_results: Optional[int] = 10,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    open_access: Optional[bool] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search for academic literature using OpenAlex API. Retrieves papers with title, abstract, authors, publication year, and organizational affiliations based on search keywords.

    Parameters
    ----------
    search_keywords : str
        Keywords to search for in paper titles, abstracts, and content. Use relevant scientific terms or phrases.
    max_results : int
        Maximum number of papers to retrieve (default: 10, maximum: 200).
    year_from : int
        Start year for publication date filter (e.g., 2020). Optional parameter to limit search to papers published from this year onwards.
    year_to : int
        End year for publication date filter (e.g., 2023). Optional parameter to limit search to papers published up to this year.
    open_access : bool
        Filter for open access papers only. Set to true for open access papers, false for non-open access, or omit for all papers.
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
            "name": "openalex_literature_search",
            "arguments": {
                "search_keywords": search_keywords,
                "max_results": max_results,
                "year_from": year_from,
                "year_to": year_to,
                "open_access": open_access,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["openalex_literature_search"]
