"""
HackerNews_get_item

Get details of a Hacker News story, comment, job, poll, or poll option by its item ID using the o...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HackerNews_get_item(
    id: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get details of a Hacker News story, comment, job, poll, or poll option by its item ID using the o...

    Parameters
    ----------
    id : int
        Hacker News item ID. Examples: 47082496, 37570568 (can be story, comment, job...
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
        {"name": "HackerNews_get_item", "arguments": {"id": id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HackerNews_get_item"]
