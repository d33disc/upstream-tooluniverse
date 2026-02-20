"""
Lemmy_list_communities

List communities on Lemmy (lemmy.world), an open-source federated social platform. Returns commun...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Lemmy_list_communities(
    sort: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    type_: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List communities on Lemmy (lemmy.world), an open-source federated social platform. Returns commun...

    Parameters
    ----------
    sort : str | Any
        Sort order. Values: 'TopAll' (most subscribers), 'Hot', 'New', 'Active', 'Top...
    limit : int | Any
        Number of communities (1-50). Default: 10
    page : int | Any
        Page number for pagination. Default: 1
    type_ : str | Any
        Filter type. Values: 'All', 'Local', 'Subscribed'. Default: 'All'
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
            "name": "Lemmy_list_communities",
            "arguments": {"sort": sort, "limit": limit, "page": page, "type_": type_},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Lemmy_list_communities"]
