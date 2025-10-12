"""
HPA_get_protein_interactions_by_gene

Fetch known protein-protein interaction partners for a given gene from Human Protein Atlas database.
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


def HPA_get_protein_interactions_by_gene(
    gene_name: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Fetch known protein-protein interaction partners for a given gene from Human Protein Atlas database.

    Parameters
    ----------
    gene_name : str
        Official gene symbol, e.g., 'EGFR', 'TP53', 'BRCA1', etc.
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
            "name": "HPA_get_protein_interactions_by_gene",
            "arguments": {"gene_name": gene_name},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HPA_get_protein_interactions_by_gene"]
