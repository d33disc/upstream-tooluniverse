"""
BioGRID_get_interactions

Query protein and genetic interactions from the BioGRID database. BioGRID is a comprehensive data...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BioGRID_get_interactions(
    gene_names: list[str],
    organism: Optional[str] = "Homo sapiens",
    interaction_type: Optional[str] = "both",
    evidence_types: Optional[list[str]] = None,
    limit: Optional[int] = 100,
    format: Optional[str] = "json",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Query protein and genetic interactions from the BioGRID database. BioGRID is a comprehensive data...

    Parameters
    ----------
    gene_names : list[str]
        List of gene names or protein identifiers
    organism : str
        Organism name (e.g., 'Homo sapiens', 'Mus musculus')
    interaction_type : str
        Type of interaction ('physical', 'genetic', 'both')
    evidence_types : list[str]
        List of evidence types to include
    limit : int
        Maximum number of interactions to return (default: 100)
    format : str
        Output format ('json' or 'tab', default: 'json')
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
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "BioGRID_get_interactions",
            "arguments": {
                "gene_names": gene_names,
                "organism": organism,
                "interaction_type": interaction_type,
                "evidence_types": evidence_types,
                "limit": limit,
                "format": format,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BioGRID_get_interactions"]
