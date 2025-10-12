"""
chembl_disease_target_score

Extract disease-target association scores specifically from ChEMBL database. ChEMBL provides bioactivity data for drug-target interactions.
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


def chembl_disease_target_score(
    efoId: str,
    pageSize: Optional[int] = 100,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Extract disease-target association scores specifically from ChEMBL database. ChEMBL provides bioactivity data for drug-target interactions.

    Parameters
    ----------
    efoId : str
        The EFO (Experimental Factor Ontology) ID of the disease, e.g., 'EFO_0000339' for chronic myelogenous leukemia
    pageSize : int
        Number of results per page (default: 100, max: 100)
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
            "name": "chembl_disease_target_score",
            "arguments": {"efoId": efoId, "pageSize": pageSize},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["chembl_disease_target_score"]
