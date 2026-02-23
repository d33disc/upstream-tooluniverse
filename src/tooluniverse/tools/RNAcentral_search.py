"""
RNAcentral_search

Search RNA records via RNAcentral API
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RNAcentral_search(
    query: str,
    page_size: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search RNA records via RNAcentral API

    Parameters
    ----------
    query : str
        Keyword or accession
    page_size : int

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
            "name": "RNAcentral_search",
            "arguments": {"query": query, "page_size": page_size},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RNAcentral_search"]
