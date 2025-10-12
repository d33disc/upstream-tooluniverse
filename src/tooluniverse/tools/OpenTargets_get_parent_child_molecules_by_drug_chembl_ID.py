"""
OpenTargets_get_parent_child_molecules_by_drug_chembl_ID

Get parent and child molecules of specified drug chemblId.
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


def OpenTargets_get_parent_child_molecules_by_drug_chembl_ID(
    chemblId: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get parent and child molecules of specified drug chemblId.

    Parameters
    ----------
    chemblId : str
        The ChEMBL ID of the drug.
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
            "name": "OpenTargets_get_parent_child_molecules_by_drug_chembl_ID",
            "arguments": {"chemblId": chemblId},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_parent_child_molecules_by_drug_chembl_ID"]
