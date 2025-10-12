"""
OpenTargets_map_any_disease_id_to_all_other_ids

Given any known disease or phenotype ID (EFO, OMIM, MONDO, UMLS, ICD10, MedDRA, etc.), return all known cross-referenced IDs including the EFO ID.
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


def OpenTargets_map_any_disease_id_to_all_other_ids(
    inputId: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Given any known disease or phenotype ID (EFO, OMIM, MONDO, UMLS, ICD10, MedDRA, etc.), return all known cross-referenced IDs including the EFO ID.

    Parameters
    ----------
    inputId : str
        Any known disease ID (e.g. OMIM:604302, UMLS:C0003873, ICD10:M05, EFO_0000685, etc.)
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
            "name": "OpenTargets_map_any_disease_id_to_all_other_ids",
            "arguments": {"inputId": inputId},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_map_any_disease_id_to_all_other_ids"]
