"""
DataGov_search_datasets

Search the U.S. Government Open Data catalog (data.gov) for publicly available federal datasets a...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DataGov_search_datasets(
    q: str,
    rows: Optional[int | Any] = None,
    fq: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the U.S. Government Open Data catalog (data.gov) for publicly available federal datasets a...

    Parameters
    ----------
    q : str
        Search query for dataset discovery. Examples: 'climate change', 'covid-19', '...
    rows : int | Any
        Number of results to return (default 10, max 100)
    fq : str | Any
        Filter query. Examples: 'organization:usgs', 'res_format:CSV', 'res_format:JS...
    sort : str | Any
        Sort order. Examples: 'score desc', 'metadata_modified desc', 'name asc'
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
            "name": "DataGov_search_datasets",
            "arguments": {"q": q, "rows": rows, "fq": fq, "sort": sort},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DataGov_search_datasets"]
