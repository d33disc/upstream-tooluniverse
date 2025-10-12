"""
OpenTargets_get_associated_drugs_by_target_ensemblID

Get known drugs and information (e.g. id, name, MoA) associated with a specific target ensemblID, including clinical trial phase and mechanism of action of the drugs.
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


def OpenTargets_get_associated_drugs_by_target_ensemblID(
    ensemblId: Optional[str] = None,
    size: Optional[int] = None,
    cursor: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get known drugs and information (e.g. id, name, MoA) associated with a specific target ensemblID, including clinical trial phase and mechanism of action of the drugs.

    Parameters
    ----------
    ensemblId : str
        The Ensembl ID of the target.
    size : int
        Number of entries to fetch.
    cursor : str
        Cursor for pagination.
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
            "name": "OpenTargets_get_associated_drugs_by_target_ensemblID",
            "arguments": {"ensemblId": ensemblId, "size": size, "cursor": cursor},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_associated_drugs_by_target_ensemblID"]
