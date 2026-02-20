"""
JSONPlaceholder_list_todos

List todos from JSONPlaceholder fake REST API, optionally filtered by user ID or completion statu...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def JSONPlaceholder_list_todos(
    userId: Optional[int | Any] = None,
    completed: Optional[bool | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List todos from JSONPlaceholder fake REST API, optionally filtered by user ID or completion statu...

    Parameters
    ----------
    userId : int | Any
        Filter todos by user ID (1-10)
    completed : bool | Any
        Filter by completion status (true or false)
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
        {
            "name": "JSONPlaceholder_list_todos",
            "arguments": {"userId": userId, "completed": completed},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["JSONPlaceholder_list_todos"]
