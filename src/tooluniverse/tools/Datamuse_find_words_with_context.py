"""
Datamuse_find_words_with_context

Find words that fit naturally after or before a given word (word adjacency) using the Datamuse AP...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Datamuse_find_words_with_context(
    lc: Optional[str | Any] = None,
    rc: Optional[str | Any] = None,
    sp: Optional[str | Any] = None,
    topics: Optional[str | Any] = None,
    max: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Find words that fit naturally after or before a given word (word adjacency) using the Datamuse AP...

    Parameters
    ----------
    lc : str | Any
        Words that typically follow this word (left context). Examples: 'drink', 'swi...
    rc : str | Any
        Words that typically precede this word (right context). Examples: 'pool', 'cr...
    sp : str | Any
        Words spelled like this pattern. Use * for wildcard. Examples: 'b*k', 'tre*'
    topics : str | Any
        Constrain to words related to this topic. Examples: 'medicine', 'music,jazz'
    max : int | Any
        Maximum number of results (1-1000). Default: 100
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
            "name": "Datamuse_find_words_with_context",
            "arguments": {"lc": lc, "rc": rc, "sp": sp, "topics": topics, "max": max},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Datamuse_find_words_with_context"]
