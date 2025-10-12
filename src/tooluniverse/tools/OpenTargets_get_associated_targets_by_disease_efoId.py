"""
OpenTargets_get_associated_targets_by_disease_efoId

Find targets associated with a specific disease or phenotype based on efoId.
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


def OpenTargets_get_associated_targets_by_disease_efoId(
    efoId: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Find targets associated with a specific disease or phenotype based on efoId.

    Parameters
    ----------
    efoId : str
        The efoId of a disease or phenotype.
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
            "name": "OpenTargets_get_associated_targets_by_disease_efoId",
            "arguments": {"efoId": efoId},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_associated_targets_by_disease_efoId"]
