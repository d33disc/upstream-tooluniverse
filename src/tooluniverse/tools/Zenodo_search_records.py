"""
Zenodo_search_records

Search Zenodo for research data, publications, and datasets. Zenodo is an open-access repository that hosts research outputs from all fields of science, including papers, datasets, software, and more.
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


def Zenodo_search_records(
    query: str,
    max_results: Optional[int] = 10,
    community: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search Zenodo for research data, publications, and datasets. Zenodo is an open-access repository that hosts research outputs from all fields of science, including papers, datasets, software, and more.

    Parameters
    ----------
    query : str
        Free text search query for Zenodo records. Use keywords to search across titles, descriptions, authors, and other metadata.
    max_results : int
        Maximum number of results to return. Must be between 1 and 200.
    community : str
        Optional community slug to filter results by specific research community (e.g., 'zenodo', 'ecfunded').
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
            "name": "Zenodo_search_records",
            "arguments": {
                "query": query,
                "max_results": max_results,
                "community": community,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Zenodo_search_records"]
