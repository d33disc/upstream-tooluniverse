"""
DailyMed_get_spl_by_setid

Get complete label corresponding to SPL Set ID, returns content in XML or JSON format.
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


def DailyMed_get_spl_by_setid(
    setid: str,
    format: Optional[str] = "xml",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get complete label corresponding to SPL Set ID, returns content in XML or JSON format.

    Parameters
    ----------
    setid : str
        SPL Set ID to query.
    format : str
        Return format, only supports 'xml'.
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
    return _get_client().run_one_function(
        {
            "name": "DailyMed_get_spl_by_setid",
            "arguments": {"setid": setid, "format": format},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DailyMed_get_spl_by_setid"]
