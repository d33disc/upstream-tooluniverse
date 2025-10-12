"""
OSF_search_preprints

Search OSF (Open Science Framework) Preprints for research preprints and working papers. OSF Preprints aggregates preprints from multiple providers including OSF, PsyArXiv, and others.
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


def OSF_search_preprints(
    query: str,
    max_results: Optional[int] = 10,
    provider: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search OSF (Open Science Framework) Preprints for research preprints and working papers. OSF Preprints aggregates preprints from multiple providers including OSF, PsyArXiv, and others.

    Parameters
    ----------
    query : str
        Search query for OSF preprints. Use keywords to search across titles and abstracts.
    max_results : int
        Maximum number of results to return. Default is 10, maximum is 100.
    provider : str
        Optional preprint provider filter (e.g., 'osf', 'psyarxiv', 'socarxiv'). If not specified, searches all providers.
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
            "name": "OSF_search_preprints",
            "arguments": {
                "query": query,
                "max_results": max_results,
                "provider": provider,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OSF_search_preprints"]
