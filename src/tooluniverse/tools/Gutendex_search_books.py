"""
Gutendex_search_books

Search Project Gutenberg's catalog of over 70,000 free ebooks using the Gutendex API. Supports te...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Gutendex_search_books(
    search: Optional[str | Any] = None,
    topic: Optional[str | Any] = None,
    languages: Optional[str | Any] = None,
    author_year_start: Optional[int | Any] = None,
    author_year_end: Optional[int | Any] = None,
    sort: Optional[str | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Project Gutenberg's catalog of over 70,000 free ebooks using the Gutendex API. Supports te...

    Parameters
    ----------
    search : str | Any
        Search terms for book titles and authors (e.g., 'shakespeare', 'pride prejudi...
    topic : str | Any
        Filter by subject or bookshelf topic (e.g., 'science fiction', 'children', 'p...
    languages : str | Any
        Comma-separated language codes to filter by (e.g., 'en', 'fr', 'de', 'en,fr')
    author_year_start : int | Any
        Filter by author birth year range start (e.g., 1800)
    author_year_end : int | Any
        Filter by author birth year range end (e.g., 1900)
    sort : str | Any
        Sort by: 'popular' (most downloaded first, default), 'ascending' (oldest firs...
    page : int | Any
        Page number for pagination (default: 1, 32 results per page)
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
            "name": "Gutendex_search_books",
            "arguments": {
                "search": search,
                "topic": topic,
                "languages": languages,
                "author_year_start": author_year_start,
                "author_year_end": author_year_end,
                "sort": sort,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Gutendex_search_books"]
