"""
Gutendex_get_book

Get detailed information about a specific Project Gutenberg book by its ID using the Gutendex API...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Gutendex_get_book(
    book_id: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific Project Gutenberg book by its ID using the Gutendex API...

    Parameters
    ----------
    book_id : int
        Project Gutenberg book ID (e.g., 1 for Declaration of Independence, 84 for Fr...
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
        {"name": "Gutendex_get_book", "arguments": {"book_id": book_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Gutendex_get_book"]
