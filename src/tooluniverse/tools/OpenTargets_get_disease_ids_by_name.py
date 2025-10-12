"""
OpenTargets_get_disease_ids_by_name

Given a disease or phenotype name, find all cross-referenced external IDs (e.g., OMIM, MONDO, MeSH, ICD10, UMLS, MedDRA, NCIt, Orphanet) using Open Targets GraphQL API.
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


def OpenTargets_get_disease_ids_by_name(
    name: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Given a disease or phenotype name, find all cross-referenced external IDs (e.g., OMIM, MONDO, MeSH, ICD10, UMLS, MedDRA, NCIt, Orphanet) using Open Targets GraphQL API.

    Parameters
    ----------
    name : str
        The name of the disease or phenotype (e.g. 'rheumatoid arthritis').
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
        {"name": "OpenTargets_get_disease_ids_by_name", "arguments": {"name": name}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_disease_ids_by_name"]
