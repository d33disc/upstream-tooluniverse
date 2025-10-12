"""
OpenTargets_target_disease_evidence

Explore evidence that supports a specific target-disease association. Input is disease efoId and target ensemblID.
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


def OpenTargets_target_disease_evidence(
    efoId: Optional[str] = None,
    ensemblId: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Explore evidence that supports a specific target-disease association. Input is disease efoId and target ensemblID.

    Parameters
    ----------
    efoId : str
        The efoId of a disease or phenotype.
    ensemblId : str
        The ensemblId of a target.
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
            "name": "OpenTargets_target_disease_evidence",
            "arguments": {"efoId": efoId, "ensemblId": ensemblId},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_target_disease_evidence"]
