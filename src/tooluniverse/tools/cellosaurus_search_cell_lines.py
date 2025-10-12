"""
cellosaurus_search_cell_lines

Search Cellosaurus cell lines using the /search/cell-line endpoint. Supports Solr query syntax for precise field-based searches.
"""

from typing import Any, Optional, Callable
from tooluniverse import ToolUniverse

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = ToolUniverse()
        _client.load_tools()
    return _client


def cellosaurus_search_cell_lines(
    q: str,
    offset: Optional[int] = 0,
    size: Optional[int] = 20,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Search Cellosaurus cell lines using the /search/cell-line endpoint. Supports Solr query syntax for precise field-based searches.

    Parameters
    ----------
    q : str
        Search query. Supports Solr syntax for field-specific searches (e.g., 'id:HeLa', 'ox:9606', 'char:cancer'). See https://api.cellosaurus.org/api-fields for available fields.
    offset : int
        Number of results to skip (for pagination)
    size : int
        Maximum number of results to return
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
    return _get_client().run_one_function(
        {
            "name": "cellosaurus_search_cell_lines",
            "arguments": {"q": q, "offset": offset, "size": size},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["cellosaurus_search_cell_lines"]
