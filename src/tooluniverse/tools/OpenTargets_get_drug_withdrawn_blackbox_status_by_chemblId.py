"""
OpenTargets_get_drug_withdrawn_blackbox_status_by_chemblId

Find withdrawn and black-box warning statuses for a specific drug by chemblId.
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


def OpenTargets_get_drug_withdrawn_blackbox_status_by_chemblId(
    chemblId: Optional[list[Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Find withdrawn and black-box warning statuses for a specific drug by chemblId.

    Parameters
    ----------
    chemblId : list[Any]
        The chemblId of a drug.
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
            "name": "OpenTargets_get_drug_withdrawn_blackbox_status_by_chemblId",
            "arguments": {"chemblId": chemblId},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_drug_withdrawn_blackbox_status_by_chemblId"]
