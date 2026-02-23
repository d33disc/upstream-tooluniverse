"""
WikiPathways_search

Search pathways by text via WikiPathways
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def WikiPathways_search(
    query: str,
    organism: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search pathways by text via WikiPathways

    Parameters
    ----------
    query : str
        Text to search, e.g., p53
    organism : str
        Optional organism
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    Any
    """
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "WikiPathways_search",
            "arguments": {"query": query, "organism": organism},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["WikiPathways_search"]
