"""
ChuckNorris_search_jokes

Search for Chuck Norris jokes by keyword from the Chuck Norris API (chucknorris.io). Returns all ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ChuckNorris_search_jokes(
    query: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for Chuck Norris jokes by keyword from the Chuck Norris API (chucknorris.io). Returns all ...

    Parameters
    ----------
    query : str
        Search query (minimum 3 characters). Examples: 'internet', 'computer', 'karat...
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
        {"name": "ChuckNorris_search_jokes", "arguments": {"query": query}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ChuckNorris_search_jokes"]
