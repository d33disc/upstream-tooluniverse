"""
drugbank_get_drug_name_and_description_by_indication

Get drug name, Drugbank ID, and description by its indication.
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


def drugbank_get_drug_name_and_description_by_indication(
    query: str,
    case_sensitive: Optional[bool] = False,
    exact_match: Optional[bool] = False,
    limit: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get drug name, Drugbank ID, and description by its indication.

    Parameters
    ----------
    query : str
        Drug indication to search for
    case_sensitive : bool
        Select True to perform a case-sensitive search
    exact_match : bool
        Select True to require an exact match
    limit : int
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
            "name": "drugbank_get_drug_name_and_description_by_indication",
            "arguments": {
                "query": query,
                "case_sensitive": case_sensitive,
                "exact_match": exact_match,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["drugbank_get_drug_name_and_description_by_indication"]
