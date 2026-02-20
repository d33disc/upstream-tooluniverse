"""
OpenLibrary_search_books

Search Open Library for books by title, author, subject, or ISBN. Open Library is an open, editab...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenLibrary_search_books(
    q: str,
    author: Optional[str | Any] = None,
    subject: Optional[str | Any] = None,
    isbn: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Open Library for books by title, author, subject, or ISBN. Open Library is an open, editab...

    Parameters
    ----------
    q : str
        Search query for title or general search (e.g., 'The Double Helix', 'CRISPR r...
    author : str | Any
        Filter by author name (e.g., 'Richard Dawkins', 'Francis Crick')
    subject : str | Any
        Filter by subject/topic (e.g., 'genetics', 'climate change', 'quantum physics')
    isbn : str | Any
        Search by ISBN-10 or ISBN-13 (e.g., '9780141975108')
    limit : int | Any
        Number of results to return (default 10, max 1000)
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
            "name": "OpenLibrary_search_books",
            "arguments": {
                "q": q,
                "author": author,
                "subject": subject,
                "isbn": isbn,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenLibrary_search_books"]
