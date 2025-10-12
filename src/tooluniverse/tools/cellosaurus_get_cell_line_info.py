"""
cellosaurus_get_cell_line_info

Get detailed information about a specific cell line using its Cellosaurus accession number (CVCL_ format).
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


def cellosaurus_get_cell_line_info(
    accession: str,
    format: Optional[str] = "json",
    fields: Optional[list[Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get detailed information about a specific cell line using its Cellosaurus accession number (CVCL_ format).

    Parameters
    ----------
    accession : str
        Cellosaurus accession number (must start with 'CVCL_')
    format : str
        Response format
    fields : list[Any]
        Specific fields to retrieve (e.g., ['id', 'ox', 'char']). If not specified, all fields are returned.
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
            "name": "cellosaurus_get_cell_line_info",
            "arguments": {"accession": accession, "format": format, "fields": fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["cellosaurus_get_cell_line_info"]
