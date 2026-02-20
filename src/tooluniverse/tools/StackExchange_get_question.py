"""
StackExchange_get_question

Get details of a specific StackOverflow question by its ID, including the question body, comments...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def StackExchange_get_question(
    question_id: int,
    site: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get details of a specific StackOverflow question by its ID, including the question body, comments...

    Parameters
    ----------
    question_id : int
        The StackOverflow question ID (e.g., 16476924)
    site : str | Any
        StackExchange site (default: 'stackoverflow')
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
            "name": "StackExchange_get_question",
            "arguments": {"question_id": question_id, "site": site},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["StackExchange_get_question"]
