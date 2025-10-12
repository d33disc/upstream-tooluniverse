"""
OpenTargets_get_approved_indications_by_drug_chemblId

Retrieve detailed information about multiple drugs using a list of ChEMBL IDs.
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


def OpenTargets_get_approved_indications_by_drug_chemblId(
    chemblId: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve detailed information about multiple drugs using a list of ChEMBL IDs.

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
            "name": "OpenTargets_get_approved_indications_by_drug_chemblId",
            "arguments": {"chemblId": chemblId},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_approved_indications_by_drug_chemblId"]
