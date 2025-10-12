"""
OpenTargets_get_drug_chembId_by_generic_name

Fetch the drug chemblId and description based on the drug generic name.
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


def OpenTargets_get_drug_chembId_by_generic_name(
    drugName: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Fetch the drug chemblId and description based on the drug generic name.

    Parameters
    ----------
    drugName : str
        The generic name of the drug for which the ID is required.
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
            "name": "OpenTargets_get_drug_chembId_by_generic_name",
            "arguments": {"drugName": drugName},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_drug_chembId_by_generic_name"]
