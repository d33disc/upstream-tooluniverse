"""
MetMuseum_search_objects

Search the Metropolitan Museum of Art (New York) collection for artworks and artifacts. Returns o...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MetMuseum_search_objects(
    q: str,
    hasImages: Optional[bool | Any] = None,
    departmentId: Optional[int | Any] = None,
    isOnView: Optional[bool | Any] = None,
    artistOrCulture: Optional[bool | Any] = None,
    medium: Optional[str | Any] = None,
    dateBegin: Optional[int | Any] = None,
    dateEnd: Optional[int | Any] = None,
    isHighlight: Optional[bool | Any] = None,
    isPublicDomain: Optional[bool | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the Metropolitan Museum of Art (New York) collection for artworks and artifacts. Returns o...

    Parameters
    ----------
    q : str
        Search query. Examples: 'impressionism', 'ancient egypt', 'japanese armor', '...
    hasImages : bool | Any
        Filter to only return objects with available images (true/false)
    departmentId : int | Any
        Department ID filter. 1=American Decorative Arts, 3=Ancient Near East, 4=Arms...
    isOnView : bool | Any
        Filter to objects currently on view at the museum
    artistOrCulture : bool | Any
        If true, searches artist name and culture fields too
    medium : str | Any
        Filter by medium/material. Examples: 'oil on canvas', 'marble', 'bronze', 'wa...
    dateBegin : int | Any
        Start of date range (year, BCE as negative). Example: -3000 for 3000 BCE
    dateEnd : int | Any
        End of date range (year). Example: 1900
    isHighlight : bool | Any
        Filter to only museum highlights (iconic objects)
    isPublicDomain : bool | Any
        Filter to public domain objects only (free to use)
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
            "name": "MetMuseum_search_objects",
            "arguments": {
                "q": q,
                "hasImages": hasImages,
                "departmentId": departmentId,
                "isOnView": isOnView,
                "artistOrCulture": artistOrCulture,
                "medium": medium,
                "dateBegin": dateBegin,
                "dateEnd": dateEnd,
                "isHighlight": isHighlight,
                "isPublicDomain": isPublicDomain,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MetMuseum_search_objects"]
