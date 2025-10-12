"""
OpenTargets_get_publications_by_target_ensemblID

Retrieve publications related to a target ensemblID, including PubMed IDs and publication dates.
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


def OpenTargets_get_publications_by_target_ensemblID(
    entityId: Optional[str] = None,
    additionalIds: Optional[list[Any]] = None,
    startYear: Optional[int] = None,
    startMonth: Optional[int] = None,
    endYear: Optional[int] = None,
    endMonth: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve publications related to a target ensemblID, including PubMed IDs and publication dates.

    Parameters
    ----------
    entityId : str
        The ID of the entity (ensemblID).
    additionalIds : list[Any]
        List of additional IDs to include in the search.
    startYear : int
        Year at the lower end of the filter.
    startMonth : int
        Month at the lower end of the filter.
    endYear : int
        Year at the higher end of the filter.
    endMonth : int
        Month at the higher end of the filter.
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
            "name": "OpenTargets_get_publications_by_target_ensemblID",
            "arguments": {
                "entityId": entityId,
                "additionalIds": additionalIds,
                "startYear": startYear,
                "startMonth": startMonth,
                "endYear": endYear,
                "endMonth": endMonth,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_publications_by_target_ensemblID"]
