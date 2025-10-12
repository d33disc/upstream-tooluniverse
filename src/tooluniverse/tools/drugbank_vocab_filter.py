"""
drugbank_vocab_filter

Filter the DrugBank vocabulary dataset based on specific field criteria. Use simple field-value pairs to filter drugs by properties like names, IDs, and chemical identifiers.
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


def drugbank_vocab_filter(
    field: Optional[str] = None,
    condition: Optional[str] = None,
    value: Optional[str] = None,
    limit: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Filter the DrugBank vocabulary dataset based on specific field criteria. Use simple field-value pairs to filter drugs by properties like names, IDs, and chemical identifiers.

    Parameters
    ----------
    field : str
        The field to filter on
    condition : str
        The type of filtering condition to apply. Filter is case-insensitive.
    value : str
        The value to filter by. Not required when condition is 'not_empty'. Examples: 'insulin' (for contains), 'DB00' (for starts_with), 'acid' (for ends_with), 'Aspirin' (for exact)
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
            "name": "drugbank_vocab_filter",
            "arguments": {
                "field": field,
                "condition": condition,
                "value": value,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["drugbank_vocab_filter"]
