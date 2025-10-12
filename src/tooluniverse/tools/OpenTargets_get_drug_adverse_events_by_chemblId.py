"""
OpenTargets_get_drug_adverse_events_by_chemblId

Retrieve significant adverse events reported for a specific drug chemblId.
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


def OpenTargets_get_drug_adverse_events_by_chemblId(
    chemblId: Optional[str] = None,
    page: Optional[dict[str, Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve significant adverse events reported for a specific drug chemblId.

    Parameters
    ----------
    chemblId : str
        The ChEMBL ID of the drug.
    page : dict[str, Any]
        Pagination settings.
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
            "name": "OpenTargets_get_drug_adverse_events_by_chemblId",
            "arguments": {"chemblId": chemblId, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_drug_adverse_events_by_chemblId"]
