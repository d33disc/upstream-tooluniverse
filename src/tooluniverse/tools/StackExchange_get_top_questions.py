"""
StackExchange_get_top_questions

Get top-voted questions on Stack Exchange sites by tag or general site using the Stack Exchange A...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def StackExchange_get_top_questions(
    tagged: Optional[str | Any] = None,
    site: Optional[str | Any] = None,
    pagesize: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get top-voted questions on Stack Exchange sites by tag or general site using the Stack Exchange A...

    Parameters
    ----------
    tagged : str | Any
        Semicolon-separated tags to filter. Examples: 'python', 'javascript', 'sql', ...
    site : str | Any
        Stack Exchange site. Default: stackoverflow. Values: 'stackoverflow', 'superu...
    pagesize : int | Any
        Number of results (1-100). Default: 10
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
            "name": "StackExchange_get_top_questions",
            "arguments": {"tagged": tagged, "site": site, "pagesize": pagesize},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["StackExchange_get_top_questions"]
