"""
OpenTargets_get_disease_synonyms_by_efoId

Retrieve disease synonyms by its EFO ID.
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


def OpenTargets_get_disease_synonyms_by_efoId(
    efoId: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve disease synonyms by its EFO ID.

    Parameters
    ----------
    efoId : str
        The EFO ID of the disease.
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
            "name": "OpenTargets_get_disease_synonyms_by_efoId",
            "arguments": {"efoId": efoId},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_disease_synonyms_by_efoId"]
