"""
drugbank_filter_drugs_by_name

Filter DrugBank records based on conditions applied to drug names. For example, find drugs whose names end with 'cillin' (penicillin antibiotics), contain 'mab', or are exactly 'Insulin'.
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


def drugbank_filter_drugs_by_name(
    condition: str,
    value: Optional[str] = None,
    limit: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Filter DrugBank records based on conditions applied to drug names. For example, find drugs whose names end with 'cillin' (penicillin antibiotics), contain 'mab', or are exactly 'Insulin'.

    Parameters
    ----------
    condition : str
        The condition to apply for filtering.
    value : str
        The value to use with the condition (e.g., 'Aspirin' for 'starts_with'). Required for 'contains', 'starts_with', 'ends_with', and 'exact' conditions.
    limit : int
        Maximum number of results to return.
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
            "name": "drugbank_filter_drugs_by_name",
            "arguments": {"condition": condition, "value": value, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["drugbank_filter_drugs_by_name"]
