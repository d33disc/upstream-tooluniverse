"""
GO_get_genes_for_term

Finds all genes/proteins associated with a specific Gene Ontology term using the Biolink API.
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


def GO_get_genes_for_term(
    id: str,
    taxon: Optional[str] = None,
    rows: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Finds all genes/proteins associated with a specific Gene Ontology term using the Biolink API.

    Parameters
    ----------
    id : str
        The standard GO term ID, e.g., 'GO:0006915'.
    taxon : str
        Optional species filter using a NCBI taxon ID. For example, Human is 'NCBITaxon:9606', and Mouse is 'NCBITaxon:10090'.
    rows : int
        The number of genes to return. Default is 100.
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
            "name": "GO_get_genes_for_term",
            "arguments": {"id": id, "taxon": taxon, "rows": rows},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GO_get_genes_for_term"]
