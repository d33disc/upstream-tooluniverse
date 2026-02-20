"""
ArtIC_search_artworks

Search the Art Institute of Chicago's collection of 130,000+ artworks using their public API. Ret...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ArtIC_search_artworks(
    q: str,
    limit: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    is_public_domain: Optional[bool | Any] = None,
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the Art Institute of Chicago's collection of 130,000+ artworks using their public API. Ret...

    Parameters
    ----------
    q : str
        Search query. Examples: 'monet', 'impressionism', 'ancient egypt', 'self port...
    limit : int | Any
        Number of results to return (default 10, max 100)
    page : int | Any
        Page number for pagination
    is_public_domain : bool | Any
        Filter to public domain works (true/false)
    fields : str | Any
        Comma-separated fields to return. Default includes: id,title,artist_display,d...
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
            "name": "ArtIC_search_artworks",
            "arguments": {
                "q": q,
                "limit": limit,
                "page": page,
                "is_public_domain": is_public_domain,
                "fields": fields,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ArtIC_search_artworks"]
