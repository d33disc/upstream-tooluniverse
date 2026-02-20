"""
iCanHazDadJoke_search_jokes

Search for dad jokes by keyword using the icanhazdadjoke.com API. Returns matching jokes with IDs...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def iCanHazDadJoke_search_jokes(
    term: str,
    limit: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for dad jokes by keyword using the icanhazdadjoke.com API. Returns matching jokes with IDs...

    Parameters
    ----------
    term : str
        Search term to find jokes. Examples: 'cat', 'dog', 'science', 'pizza', 'progr...
    limit : int | Any
        Number of results per page (1-30). Default: 20
    page : int | Any
        Page number for pagination. Default: 1
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
            "name": "iCanHazDadJoke_search_jokes",
            "arguments": {"term": term, "limit": limit, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["iCanHazDadJoke_search_jokes"]
