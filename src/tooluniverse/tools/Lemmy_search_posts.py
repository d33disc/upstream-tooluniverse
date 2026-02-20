"""
Lemmy_search_posts

Search for posts across Lemmy (lemmy.world), an open-source Reddit alternative with thousands of ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Lemmy_search_posts(
    q: str,
    type_: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    community_name: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for posts across Lemmy (lemmy.world), an open-source Reddit alternative with thousands of ...

    Parameters
    ----------
    q : str
        Search query string. Examples: 'rust programming', 'machine learning', 'self-...
    type_ : str | Any
        Type of search results. Values: 'Posts' (default), 'Comments', 'Communities',...
    sort : str | Any
        Sort order. Values: 'TopAll', 'TopDay', 'TopWeek', 'TopMonth', 'TopYear', 'Ho...
    limit : int | Any
        Number of results (1-50). Default: 10
    page : int | Any
        Page number for pagination. Default: 1
    community_name : str | Any
        Filter to a specific community name. Examples: 'technology', 'programming', '...
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
            "name": "Lemmy_search_posts",
            "arguments": {
                "q": q,
                "type_": type_,
                "sort": sort,
                "limit": limit,
                "page": page,
                "community_name": community_name,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Lemmy_search_posts"]
