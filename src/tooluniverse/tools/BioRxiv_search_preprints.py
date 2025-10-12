"""
BioRxiv_search_preprints

Search bioRxiv preprints using the public bioRxiv API. Returns preprints with title, authors, year, DOI, and URL.
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


def BioRxiv_search_preprints(
    query: str,
    max_results: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search bioRxiv preprints using the public bioRxiv API. Returns preprints with title, authors, year, DOI, and URL.

    Parameters
    ----------
    query : str
        Search query for bioRxiv preprints. Use keywords separated by spaces to refine your search.
    max_results : int
        Maximum number of preprints to return. Default is 10, maximum is 200.
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
            "name": "BioRxiv_search_preprints",
            "arguments": {"query": query, "max_results": max_results},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BioRxiv_search_preprints"]
