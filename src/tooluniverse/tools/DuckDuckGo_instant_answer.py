"""
DuckDuckGo_instant_answer

Get an instant answer summary for a search query using the DuckDuckGo Instant Answer API. Returns...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DuckDuckGo_instant_answer(
    q: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get an instant answer summary for a search query using the DuckDuckGo Instant Answer API. Returns...

    Parameters
    ----------
    q : str
        Search query string. Works best with specific entity names, topics, or well-d...
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
        {"name": "DuckDuckGo_instant_answer", "arguments": {"q": q}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DuckDuckGo_instant_answer"]
