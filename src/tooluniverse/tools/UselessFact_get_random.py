"""
UselessFact_get_random

Get a random useless fact from the Useless Facts API. Returns an interesting but trivial fact wit...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def UselessFact_get_random(
    language: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random useless fact from the Useless Facts API. Returns an interesting but trivial fact wit...

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
        {"name": "UselessFact_get_random", "arguments": {"language": language}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["UselessFact_get_random"]
