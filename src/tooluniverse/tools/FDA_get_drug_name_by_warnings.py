"""
FDA_get_drug_name_by_warnings

Retrieve the drug names based on specific warning information.
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


def FDA_get_drug_name_by_warnings(
    warning_text: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the drug names based on specific warning information.

    Parameters
    ----------
    warning_text : str
        The warning text to search for in the drug labeling.
    limit : int
        The number of records to return.
    skip : int
        The number of records to skip.
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
            "name": "FDA_get_drug_name_by_warnings",
            "arguments": {"warning_text": warning_text, "limit": limit, "skip": skip},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_name_by_warnings"]
