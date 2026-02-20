"""
CatFact_get_breeds

List cat breeds from the CatFact Ninja API. Returns breed names, countries of origin, coats, and ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CatFact_get_breeds(
    limit: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List cat breeds from the CatFact Ninja API. Returns breed names, countries of origin, coats, and ...

    Parameters
    ----------
    limit : int | Any
        Number of breeds to return per page (1-100). Default: 25
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
        {"name": "CatFact_get_breeds", "arguments": {"limit": limit, "page": page}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CatFact_get_breeds"]
