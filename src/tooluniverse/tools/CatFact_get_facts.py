"""
CatFact_get_facts

Get random cat facts from the CatFact Ninja API. Returns interesting and fun facts about cats. No...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CatFact_get_facts(
    limit: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get random cat facts from the CatFact Ninja API. Returns interesting and fun facts about cats. No...

    Parameters
    ----------
    limit : int | Any
        Number of facts to return per page (1-1000). Default: 10. Example: 5
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
        {"name": "CatFact_get_facts", "arguments": {"limit": limit, "page": page}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CatFact_get_facts"]
