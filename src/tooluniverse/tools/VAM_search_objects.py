"""
VAM_search_objects

Search the Victoria and Albert Museum (V&A, London) collection - one of the world's greatest muse...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def VAM_search_objects(
    q: Optional[str | Any] = None,
    q_object_type: Optional[str | Any] = None,
    q_material_tech: Optional[str | Any] = None,
    q_place_name: Optional[str | Any] = None,
    q_actor_name: Optional[str | Any] = None,
    year_made_from: Optional[int | Any] = None,
    year_made_to: Optional[int | Any] = None,
    images_exist: Optional[int | Any] = None,
    on_display: Optional[int | Any] = None,
    page_size: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the Victoria and Albert Museum (V&A, London) collection - one of the world's greatest muse...

    Parameters
    ----------
    q : str | Any
        Search query. Examples: 'silk dress', 'Chinese porcelain', 'William Morris', ...
    q_object_type : str | Any
        Filter by object type. Examples: 'dress', 'vase', 'painting', 'sculpture', 'c...
    q_material_tech : str | Any
        Filter by material or technique. Examples: 'silk', 'ceramic', 'oil paint', 'w...
    q_place_name : str | Any
        Filter by place of origin. Examples: 'Japan', 'England', 'India', 'France'
    q_actor_name : str | Any
        Filter by maker/artist name. Examples: 'Wedgwood', 'Chanel', 'William Morris'
    year_made_from : int | Any
        Filter objects made from this year (e.g. 1800)
    year_made_to : int | Any
        Filter objects made up to this year (e.g. 1900)
    images_exist : int | Any
        Filter to objects with images: 1 = has images, 0 = no images
    on_display : int | Any
        Filter to objects currently on display: 1 = on display
    page_size : int | Any
        Number of results per page (default 15, max 100)
    page : int | Any
        Page number (1-indexed)
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
            "name": "VAM_search_objects",
            "arguments": {
                "q": q,
                "q_object_type": q_object_type,
                "q_material_tech": q_material_tech,
                "q_place_name": q_place_name,
                "q_actor_name": q_actor_name,
                "year_made_from": year_made_from,
                "year_made_to": year_made_to,
                "images_exist": images_exist,
                "on_display": on_display,
                "page_size": page_size,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["VAM_search_objects"]
