"""
OpenTargets_get_similar_entities_by_target_ensemblID

Retrieve similar entities for a given target ensemblID using a model trained with PubMed.
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


def OpenTargets_get_similar_entities_by_target_ensemblID(
    ensemblId: Optional[str] = None,
    threshold: Optional[float] = None,
    size: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve similar entities for a given target ensemblID using a model trained with PubMed.

    Parameters
    ----------
    ensemblId : str
        The ensemblID of the disease.
    threshold : float
        Threshold similarity between 0 and 1. Only results above threshold are returned.
    size : int
        Number of similar entities to fetch.
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
            "name": "OpenTargets_get_similar_entities_by_target_ensemblID",
            "arguments": {"ensemblId": ensemblId, "threshold": threshold, "size": size},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_similar_entities_by_target_ensemblID"]
