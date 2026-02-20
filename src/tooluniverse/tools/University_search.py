"""
University_search

Search for universities worldwide by name and/or country. Returns university name, country, web p...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def University_search(
    name: Optional[str | Any] = None,
    country: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for universities worldwide by name and/or country. Returns university name, country, web p...

    Parameters
    ----------
    name : str | Any
        University name to search for (e.g., 'Harvard', 'Oxford', 'MIT')
    country : str | Any
        Country name to filter by (e.g., 'United States', 'United Kingdom', 'Germany')
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
        {"name": "University_search", "arguments": {"name": name, "country": country}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["University_search"]
