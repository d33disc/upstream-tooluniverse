"""
StackExchange_get_answers

Get answers for a specific StackOverflow question, sorted by votes. Returns the answer body, vote...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def StackExchange_get_answers(
    question_id: int,
    site: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    pagesize: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get answers for a specific StackOverflow question, sorted by votes. Returns the answer body, vote...

    Parameters
    ----------
    question_id : int
        The StackOverflow question ID
    site : str | Any
        StackExchange site (default: 'stackoverflow')
    sort : str | Any
        Sort order: 'votes', 'activity', 'creation' (default: 'votes')
    pagesize : int | Any
        Number of answers to return (default: 5)
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
            "name": "StackExchange_get_answers",
            "arguments": {
                "question_id": question_id,
                "site": site,
                "sort": sort,
                "pagesize": pagesize,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["StackExchange_get_answers"]
