"""
FDA_get_drug_name_by_SPL_ID

Retrieve the drug name based on the FDA application number, NUI unique identifier, document ID of a specific version of the drug's Structured Product Label (SPL), or set ID of the drug's Structured Product Label that works across label versions.
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


def FDA_get_drug_name_by_SPL_ID(
    field_info: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the drug name based on the FDA application number, NUI unique identifier, document ID of a specific version of the drug's Structured Product Label (SPL), or set ID of the drug's Structured Product Label that works across label versions.

    Parameters
    ----------
    field_info : str
        The specific field information to search for.
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
            "name": "FDA_get_drug_name_by_SPL_ID",
            "arguments": {"field_info": field_info, "limit": limit, "skip": skip},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_name_by_SPL_ID"]
