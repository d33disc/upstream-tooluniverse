"""
DBnomics_search_datasets

Search DBnomics for economic and statistical datasets from 90+ providers including IMF, World Ban...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DBnomics_search_datasets(
    q: str,
    limit: Optional[int | Any] = None,
    offset: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search DBnomics for economic and statistical datasets from 90+ providers including IMF, World Ban...

    Parameters
    ----------
    q : str
        Search query for datasets. Examples: 'GDP growth', 'inflation USA', 'unemploy...
    limit : int | Any
        Maximum number of results to return (default: 10, max: 1000)
    offset : int | Any
        Number of results to skip for pagination (default: 0)
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
            "name": "DBnomics_search_datasets",
            "arguments": {"q": q, "limit": limit, "offset": offset},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DBnomics_search_datasets"]
