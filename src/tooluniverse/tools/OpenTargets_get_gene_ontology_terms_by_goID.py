"""
OpenTargets_get_gene_ontology_terms_by_goID

Retrieve Gene Ontology terms based on a list of GO IDs.
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


def OpenTargets_get_gene_ontology_terms_by_goID(
    goIds: Optional[list[Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve Gene Ontology terms based on a list of GO IDs.

    Parameters
    ----------
    goIds : list[Any]
        A list of Gene Ontology (GO) IDs to fetch the corresponding terms.
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
            "name": "OpenTargets_get_gene_ontology_terms_by_goID",
            "arguments": {"goIds": goIds},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_gene_ontology_terms_by_goID"]
