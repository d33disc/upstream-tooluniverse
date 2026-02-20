"""
npm_search_packages

Search the npm (Node Package Manager) registry for JavaScript/TypeScript packages. Returns packag...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def npm_search_packages(
    text: str,
    size: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the npm (Node Package Manager) registry for JavaScript/TypeScript packages. Returns packag...

    Parameters
    ----------
    text : str
        Search query. Can include qualifiers: 'author:USERNAME', 'keywords:KEYWORD'. ...
    size : int | Any
        Number of results to return (default 20, max 250)
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
        {"name": "npm_search_packages", "arguments": {"text": text, "size": size}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["npm_search_packages"]
