"""
OpenAIRE_search_publications

Search OpenAIRE Explore for research products including publications, datasets, and software. OpenAIRE is the European open science platform that provides access to research outputs from EU-funded projects.
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


def OpenAIRE_search_publications(
    query: str,
    max_results: Optional[int] = 10,
    type: Optional[str] = "publications",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search OpenAIRE Explore for research products including publications, datasets, and software. OpenAIRE is the European open science platform that provides access to research outputs from EU-funded projects.

    Parameters
    ----------
    query : str
        Search query for OpenAIRE research products. Use keywords to search across titles, abstracts, and metadata.
    max_results : int
        Maximum number of results to return. Default is 10, maximum is 100.
    type : str
        Type of research product to search: 'publications', 'datasets', or 'software'. Default is 'publications'.
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
            "name": "OpenAIRE_search_publications",
            "arguments": {"query": query, "max_results": max_results, "type": type},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenAIRE_search_publications"]
