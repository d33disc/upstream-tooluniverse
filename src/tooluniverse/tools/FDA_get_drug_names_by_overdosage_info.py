"""
FDA_get_drug_names_by_overdosage_info

Retrieve drug names based on information about signs, symptoms, and laboratory findings of acute overdosage.
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


def FDA_get_drug_names_by_overdosage_info(
    overdosage_info: Optional[str] = None,
    indication: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve drug names based on information about signs, symptoms, and laboratory findings of acute overdosage.

    Parameters
    ----------
    overdosage_info : str
        Information about signs, symptoms, and laboratory findings of acute overdosage.
    indication : str
        The indication or usage of the drug.
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
            "name": "FDA_get_drug_names_by_overdosage_info",
            "arguments": {
                "overdosage_info": overdosage_info,
                "indication": indication,
                "limit": limit,
                "skip": skip,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_names_by_overdosage_info"]
