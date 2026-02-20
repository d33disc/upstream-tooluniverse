"""
OpenVerse_search_images

Search Creative Commons licensed images from the Openverse API (formerly Creative Commons Search)...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenVerse_search_images(
    q: str,
    license: Optional[str | Any] = None,
    license_type: Optional[str | Any] = None,
    source: Optional[str | Any] = None,
    extension: Optional[str | Any] = None,
    page_size: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Creative Commons licensed images from the Openverse API (formerly Creative Commons Search)...

    Parameters
    ----------
    q : str
        Search query. Examples: 'DNA structure', 'coral reef', 'microscopy cells', 'C...
    license : str | Any
        License type filter. Values: 'cc0' (public domain), 'by' (CC BY), 'by-sa' (CC...
    license_type : str | Any
        License type category. Values: 'commercial' (can be used commercially), 'modi...
    source : str | Any
        Filter by image source. Examples: 'flickr', 'wikimedia', 'met', 'europeana', ...
    extension : str | Any
        File format filter. Values: 'jpg', 'png', 'gif', 'svg'
    page_size : int | Any
        Number of results (default 20, max 500)
    page : int | Any
        Page number for pagination
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
            "name": "OpenVerse_search_images",
            "arguments": {
                "q": q,
                "license": license,
                "license_type": license_type,
                "source": source,
                "extension": extension,
                "page_size": page_size,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenVerse_search_images"]
