"""
ChuckNorris_get_categories

Get the list of all available Chuck Norris joke categories from chucknorris.io. Returns category ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ChuckNorris_get_categories(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the list of all available Chuck Norris joke categories from chucknorris.io. Returns category ...

    Parameters
    ----------
    No parameters
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
        {"name": "ChuckNorris_get_categories", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ChuckNorris_get_categories"]
