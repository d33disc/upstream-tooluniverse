"""
PokemonTCG_search_cards

Search for Pokemon Trading Card Game cards using the Pokemon TCG API. Supports querying by name, ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PokemonTCG_search_cards(
    q: str,
    page: Optional[int | Any] = None,
    pageSize: Optional[int | Any] = None,
    orderBy: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for Pokemon Trading Card Game cards using the Pokemon TCG API. Supports querying by name, ...

    Parameters
    ----------
    q : str
        Search query using Lucene syntax. Examples: 'name:charizard', 'name:pikachu t...
    page : int | Any
        Page number for pagination. Default: 1
    pageSize : int | Any
        Number of results per page (max 250). Default: 10
    orderBy : str | Any
        Field to order by. Examples: 'name', '-name' (descending), 'set.releaseDate',...
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
            "name": "PokemonTCG_search_cards",
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


__all__ = ["PokemonTCG_search_cards"]
