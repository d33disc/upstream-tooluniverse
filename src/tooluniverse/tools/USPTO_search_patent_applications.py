"""
USPTO_search_patent_applications

Search USPTO patent applications with a JSON-body POST (Lucene query). Returns application record...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def USPTO_search_patent_applications(
    query: str,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Search USPTO patent applications with a JSON-body POST (Lucene query). Returns application record...

    Parameters
    ----------
    query : str
        Lucene query string, e.g. 'applicationNumberText:14412875'.
    offset : int
        Position in the dataset to start from (default 0).
    limit : int
        Maximum number of results to return (default 25).
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    # Handle mutable defaults to avoid B006 linting error

    # Strip None values so optional parameters don't trigger schema validation errors
    _args = {
        k: v
        for k, v in {"query": query, "offset": offset, "limit": limit}.items()
        if v is not None
    }
    return get_shared_client().run_one_function(
        {
            "name": "USPTO_search_patent_applications",
            "arguments": _args,
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["USPTO_search_patent_applications"]
