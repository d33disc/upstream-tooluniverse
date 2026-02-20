"""
PoetryDB_search_by_title

Search for poems by title in PoetryDB. Returns matching poems with full text and metadata. Suppor...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PoetryDB_search_by_title(
    title: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for poems by title in PoetryDB. Returns matching poems with full text and metadata. Suppor...

    Parameters
    ----------
    title : str
        Poem title (full or partial). Examples: 'The Raven', 'Sonnet 18', 'Ode to a N...
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
        {"name": "PoetryDB_search_by_title", "arguments": {"title": title}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PoetryDB_search_by_title"]
