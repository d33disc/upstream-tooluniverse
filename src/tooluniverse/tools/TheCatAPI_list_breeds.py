"""
TheCatAPI_list_breeds

List all available cat breeds from TheCatAPI with pagination support. Returns breed names, IDs, d...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheCatAPI_list_breeds(
    limit: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List all available cat breeds from TheCatAPI with pagination support. Returns breed names, IDs, d...

    Parameters
    ----------
    limit : int | Any
        Number of breeds to return per page (default returns all ~67 breeds)
    page : int | Any
        Page number for pagination (0-indexed, default: 0). Use with limit parameter.
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
        {"name": "TheCatAPI_list_breeds", "arguments": {"limit": limit, "page": page}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheCatAPI_list_breeds"]
