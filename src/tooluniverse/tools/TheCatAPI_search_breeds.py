"""
TheCatAPI_search_breeds

Search for cat breeds by name using TheCatAPI. Returns breed information including temperament, o...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheCatAPI_search_breeds(
    q: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for cat breeds by name using TheCatAPI. Returns breed information including temperament, o...

    Parameters
    ----------
    q : str
        Search query for breed name (partial match supported). Examples: 'persian', '...
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
        {"name": "TheCatAPI_search_breeds", "arguments": {"q": q}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheCatAPI_search_breeds"]
