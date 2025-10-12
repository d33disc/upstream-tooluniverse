"""
OpenTargets_get_target_interactions_by_ensemblID

Retrieve interaction data for a specific target ensemblID, including interaction partners and evidence.
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


def OpenTargets_get_target_interactions_by_ensemblID(
    ensemblId: Optional[str] = None,
    page: Optional[dict[str, Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve interaction data for a specific target ensemblID, including interaction partners and evidence.

    Parameters
    ----------
    ensemblId : str
        The Ensembl ID of the target.
    page : dict[str, Any]
        Pagination parameters.
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
            "name": "OpenTargets_get_target_interactions_by_ensemblID",
            "arguments": {"ensemblId": ensemblId, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_target_interactions_by_ensemblID"]
