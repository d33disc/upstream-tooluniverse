"""
PoetryDB_search_by_lines

Search for poems containing specific text lines in PoetryDB. Returns poems where the specified te...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PoetryDB_search_by_lines(
    lines: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for poems containing specific text lines in PoetryDB. Returns poems where the specified te...

    Parameters
    ----------
    lines : str
        Text to search for in poem lines. Examples: 'shall I compare', 'two roads div...
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
        {"name": "PoetryDB_search_by_lines", "arguments": {"lines": lines}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PoetryDB_search_by_lines"]
