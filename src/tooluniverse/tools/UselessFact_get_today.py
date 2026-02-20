"""
UselessFact_get_today

Get today's useless fact from the Useless Facts API. Returns the fact of the day, which is the sa...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def UselessFact_get_today(
    language: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get today's useless fact from the Useless Facts API. Returns the fact of the day, which is the sa...

    Parameters
    ----------
    language : str | Any
        Language for the fact. Options: 'en' (English), 'de' (German). Default: 'en'
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
        {"name": "UselessFact_get_today", "arguments": {"language": language}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["UselessFact_get_today"]
