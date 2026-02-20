"""
InternetArchive_wayback_search

Search the Wayback Machine CDX (Capture inDeX) for archived snapshots of a URL over time. Returns...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def InternetArchive_wayback_search(
    url: str,
    limit: Optional[int | Any] = None,
    from_: Optional[str | Any] = None,
    to: Optional[str | Any] = None,
    matchType: Optional[str | Any] = None,
    filter: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the Wayback Machine CDX (Capture inDeX) for archived snapshots of a URL over time. Returns...

    Parameters
    ----------
    url : str
        URL to look up in the Wayback Machine (e.g., 'example.com', 'https://www.pyth...
    limit : int | Any
        Maximum number of capture records to return (default 10)
    from_ : str | Any
        Start date filter (YYYYMMDD format, e.g., '20200101')
    to : str | Any
        End date filter (YYYYMMDD format, e.g., '20231231')
    matchType : str | Any
        URL matching: 'exact' (default), 'prefix', 'host', 'domain'
    filter : str | Any
        Field filter (e.g., 'statuscode:200' for successful captures only, 'mimetype:...
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
            "name": "InternetArchive_wayback_search",
            "arguments": {
                "url": url,
                "limit": limit,
                "from": from_,
                "to": to,
                "matchType": matchType,
                "filter": filter,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["InternetArchive_wayback_search"]
