"""
PokemonTCG_list_sets

List all Pokemon TCG card sets or search for specific sets. Returns set details including name, s...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PokemonTCG_list_sets(
    q: Optional[str | Any] = None,
    page: Optional[int | Any] = None,
    pageSize: Optional[int | Any] = None,
    orderBy: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List all Pokemon TCG card sets or search for specific sets. Returns set details including name, s...

    Parameters
    ----------
    q : str | Any
        Optional search query for filtering sets. Examples: 'name:base', 'series:swor...
    page : int | Any
        Page number. Default: 1
    pageSize : int | Any
        Results per page (max 250). Default: 10
    orderBy : str | Any
        Sort by field. Examples: 'releaseDate', '-releaseDate' (newest first), 'name'
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
            "name": "PokemonTCG_list_sets",
            "arguments": {
                "q": q,
                "page": page,
                "pageSize": pageSize,
                "orderBy": orderBy,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PokemonTCG_list_sets"]
