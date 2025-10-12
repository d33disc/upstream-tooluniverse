"""
OpenTargets_get_target_gene_ontology_by_ensemblID

Retrieve Gene Ontology annotations for a specific target by Ensembl ID.
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


def OpenTargets_get_target_gene_ontology_by_ensemblID(
    ensemblId: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve Gene Ontology annotations for a specific target by Ensembl ID.

    Parameters
    ----------
    ensemblId : str
        The Ensembl ID of the target for which to retrieve Gene Ontology annotations.
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
            "name": "OpenTargets_get_target_gene_ontology_by_ensemblID",
            "arguments": {"ensemblId": ensemblId},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_target_gene_ontology_by_ensemblID"]
