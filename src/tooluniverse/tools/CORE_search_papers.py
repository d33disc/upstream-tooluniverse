"""
CORE_search_papers

Search for open access academic papers using CORE API. CORE is the world's largest collection of open access research papers, providing access to over 200 million papers from repositories and journals worldwide.
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


def CORE_search_papers(
    query: str,
    limit: Optional[int] = 10,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    language: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search for open access academic papers using CORE API. CORE is the world's largest collection of open access research papers, providing access to over 200 million papers from repositories and journals worldwide.

    Parameters
    ----------
    query : str
        Search query for CORE papers. Use keywords separated by spaces to refine your search.
    limit : int
        Maximum number of papers to return. This sets the maximum number of papers retrieved from CORE.
    year_from : int
        Start year for publication date filter (e.g., 2020). Optional parameter to limit search to papers published from this year onwards.
    year_to : int
        End year for publication date filter (e.g., 2024). Optional parameter to limit search to papers published up to this year.
    language : str
        Language filter for papers (e.g., 'en', 'es', 'fr'). Optional parameter to limit search to papers in specific language.
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
            "name": "CORE_search_papers",
            "arguments": {
                "query": query,
                "limit": limit,
                "year_from": year_from,
                "year_to": year_to,
                "language": language,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CORE_search_papers"]
